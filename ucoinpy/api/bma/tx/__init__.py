#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
# Caner Candan <caner@candan.fr>, http://caner.candan.fr
#

from .. import API, logging

logger = logging.getLogger("ucoin/tx")


class Tx(API):
    def __init__(self, connection_handler, module='tx'):
        super(Tx, self).__init__(connection_handler, module)


class History(Tx):
    """Get transaction sources."""
    def __init__(self, conn_handler, pubkey, module='tx'):
        super(Tx, self).__init__(conn_handler, module)
        self.pubkey = pubkey

    def __get__(self, **kwargs):
        assert self.pubkey is not None
        r = yield from self.requests_get('/history/%s' % self.pubkey, **kwargs)
        return (yield from r.json())


class Process(Tx):
    """POST a transaction."""

    def __post__(self, **kwargs):
        assert 'transaction' in kwargs

        r = yield from self.requests_post('/process', **kwargs)
        return (yield from r.text())


class Sources(Tx):
    """Get transaction sources."""
    def __init__(self, connection_handler, pubkey, module='tx'):
        super(Tx, self).__init__(connection_handler, module)
        self.pubkey = pubkey

    def __get__(self, **kwargs):
        assert self.pubkey is not None
        r = yield from self.requests_get('/sources/%s' % self.pubkey, **kwargs)
        return (yield from r.json())

from . import history