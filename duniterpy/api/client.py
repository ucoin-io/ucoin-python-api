# Authors:
# Caner Candan <caner@candan.fr>, http://caner.candan.fr
# Inso <insomniak.fr at gmail.com>
from typing import Callable
import json
import logging
import aiohttp
import jsonschema
from .errors import DuniterError
import duniterpy.api.endpoint as endpoint

logger = logging.getLogger("duniter")

# Response type constants
RESPONSE_JSON = 'json'
RESPONSE_TEXT = 'text'
RESPONSE_AIOHTTP = 'aiohttp'

# jsonschema validator
ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "ucode": {
            "type": "number"
        },
        "message": {
            "type": "string"
        }
    },
    "required": ["ucode", "message"]
}


def parse_text(text, schema):
    """
    Validate and parse the BMA answer from websocket

    :param str text: the bma answer
    :param dict schema: dict for jsonschema
    :return: the json data
    """
    try:
        data = json.loads(text)
        jsonschema.validate(data, schema)
        return data
    except (TypeError, json.decoder.JSONDecodeError):
        raise jsonschema.ValidationError("Could not parse json")


def parse_error(text):
    """
    Validate and parse the BMA answer from websocket

    :param str text: the bma error
    :return: the json data
    """
    try:
        data = json.loads(text)
        jsonschema.validate(data, ERROR_SCHEMA)
        return data
    except (TypeError, json.decoder.JSONDecodeError) as e:
        raise jsonschema.ValidationError("Could not parse json : {0}".format(str(e)))


async def parse_response(response, schema):
    """
    Validate and parse the BMA answer

    :param aiohttp.ClientResponse response: Response of aiohttp request
    :param dict schema: The expected response structure
    :return: the json data
    """
    try:
        data = await response.json()
        response.close()
        if schema is not None:
            jsonschema.validate(data, schema)
        return data
    except (TypeError, json.decoder.JSONDecodeError) as e:
        raise jsonschema.ValidationError("Could not parse json : {0}".format(str(e)))


class API(object):
    """APIRequest is a class used as an interface. The intermediate derivated classes are the modules and the leaf
    classes are the API requests. """

    schema = {}

    def __init__(self, connection_handler, module):
        """
        Asks a module in order to create the url used then by derivated classes.

        :param ConnectionHandler connection_handler: Connection handler
        :param str module: Module path
        """
        self.module = module
        self.connection_handler = connection_handler
        self.headers = {}

    def reverse_url(self, scheme, path):
        """
        Reverses the url using scheme and path given in parameter.

        :param str scheme: Scheme of the url
        :param str path: Path of the url
        :return: str
        """

        server, port = self.connection_handler.server, self.connection_handler.port
        if self.connection_handler.path:
            url = '{scheme}://{server}:{port}/{path}/{module}'.format(scheme=scheme,
                                                                      server=server,
                                                                      port=port,
                                                                      path=path,
                                                                      module=self.module)
        else:
            url = '{scheme}://{server}:{port}/{module}'.format(scheme=scheme,
                                                               server=server,
                                                               port=port,
                                                               module=self.module)

        return url + path

    async def requests_get(self, path, **kwargs):
        """
        Requests GET wrapper in order to use API parameters.

        :param str path: the request path
        :rtype: aiohttp.ClientResponse
        """
        logging.debug("Request : {0}".format(self.reverse_url(self.connection_handler.http_scheme, path)))
        url = self.reverse_url(self.connection_handler.http_scheme, path)
        response = await self.connection_handler.session.get(url, params=kwargs, headers=self.headers,
                                                             proxy=self.connection_handler.proxy,
                                                             timeout=15)
        if response.status != 200:
            try:
                error_data = parse_error(await response.text())
                raise DuniterError(error_data)
            except (TypeError, jsonschema.ValidationError):
                raise ValueError('status code != 200 => %d (%s)' % (response.status, (await response.text())))

        return response

    async def requests_post(self, path, **kwargs):
        """
        Requests POST wrapper in order to use API parameters.

        :param str path: the request path
        :rtype: aiohttp.ClientResponse
        """
        if 'self_' in kwargs:
            kwargs['self'] = kwargs.pop('self_')

        logging.debug("POST : {0}".format(kwargs))
        response = await self.connection_handler.session.post(
            self.reverse_url(self.connection_handler.http_scheme, path),
            data=kwargs,
            headers=self.headers,
            proxy=self.connection_handler.proxy,
            timeout=15
        )
        return response

    def connect_ws(self, path):
        """
        Connect to a websocket in order to use API parameters

        :param str path: the url path
        :rtype: aiohttp.ClientWebSocketResponse
        """
        url = self.reverse_url(self.connection_handler.ws_scheme, path)
        return self.connection_handler.session.ws_connect(url, proxy=self.connection_handler.proxy)


class Client:
    """
    Main class to create an API client
    """
    def __init__(self, _endpoint: str, session: aiohttp.ClientSession = None, proxy: str = None):
        """
        Init Client instance

        :param _endpoint: Endpoint string in duniter format
        :param session: Aiohttp client session (optional, default None)
        :param proxy: Proxy server as hostname:port
        """
        # Endpoint Protocol detection
        self.endpoint = endpoint.endpoint(_endpoint)

        # if no user session...
        if session is None:
            # open a session
            self.session = aiohttp.ClientSession()
        else:
            self.session = session
        self.proxy = proxy

    async def get(self, url_path: str, params: dict = None, rtype: str = RESPONSE_JSON, schema: dict = None)-> any:
        """
        Get request on self.endpoint + url_path

        :param url_path: Url encoded path following the endpoint
        :param params: Url query string parameters dictionary
        :param rtype: Response type
        :param schema: Json Schema to validate response (optional, default None)
        :return:
        """
        if params is None:
            params = dict()

        client = API(self.endpoint.conn_handler(self.session, self.proxy), '')

        # get aiohttp response
        response = await client.requests_get(url_path, **params)

        # if schema supplied...
        if schema is not None:
            # validate response
            await parse_response(response, schema)

        # return the chosen type
        if rtype == RESPONSE_AIOHTTP:
            return response
        elif rtype == RESPONSE_TEXT:
            return await response.text()
        elif rtype == RESPONSE_JSON:
            return await response.json()

    async def close(self):
        """
        Close aiohttp session

        :return:
        """
        await self.session.close()

    async def __call__(self, _function: Callable, *args: any, **kwargs: any) -> any:
        """
        Call the _function given with the args given
        So we can have use many packages wrapping a REST API

        :param _function: The function to call
        :param args: The parameters
        :param kwargs: The key/value parameters
        :return:
        """
        return await _function(self, *args, **kwargs)
