'''
Created on 13 déc. 2014

@author: inso
'''
import unittest
from ucoinpy.documents.peer import Peer, BMAEndpoint, UnknownEndpoint


rawpeer = """Version: 1
Type: Peer
Currency: beta_brousouf
PublicKey: HsLShAtzXTVxeUtQd7yi5Z5Zh4zNvbu8sTEZ53nfKcqY
Block: 8-1922C324ABC4AF7EF7656734A31F5197888DDD52
Endpoints:
BASIC_MERKLED_API some.dns.name 88.77.66.55 2001:0db8:0000:85a3:0000:0000:ac1f 9001
BASIC_MERKLED_API some.dns.name 88.77.66.55 2001:0db8:0000:85a3:0000:0000:ac1f 9002
OTHER_PROTOCOL 88.77.66.55 9001
dkaXIiCYUJtCg8Feh/BKvPYf4uFH9CJ/zY6J4MlA9BsjmcMe4YAblvNt/gJy31b1aGq3ue3h14mLMCu84rraDg==
"""


class TestPeer(unittest.TestCase):
    def test_fromraw(self):
        peer = Peer.from_signed_raw(rawpeer)
        self.assertEquals(peer.currency, "beta_brousouf")
        self.assertEquals(peer.pubkey, "HsLShAtzXTVxeUtQd7yi5Z5Zh4zNvbu8sTEZ53nfKcqY")
        self.assertEquals(peer.blockid, "8-1922C324ABC4AF7EF7656734A31F5197888DDD52")
        self.assertEquals(len(peer.endpoints), 3)
        self.assertTrue(type(peer.endpoints[0]) is BMAEndpoint)
        self.assertTrue(type(peer.endpoints[1]) is BMAEndpoint)
        self.assertTrue(type(peer.endpoints[2]) is UnknownEndpoint)

        self.assertEquals(peer.endpoints[0].server, "some.dns.name")
        self.assertEquals(peer.endpoints[0].ipv4, "88.77.66.55")
        self.assertEquals(peer.endpoints[0].ipv6, "2001:0db8:0000:85a3:0000:0000:ac1f")
        self.assertEquals(peer.endpoints[0].port, 9001)

        self.assertEquals(peer.endpoints[1].server, "some.dns.name")
        self.assertEquals(peer.endpoints[1].ipv4, "88.77.66.55")
        self.assertEquals(peer.endpoints[1].ipv6, "2001:0db8:0000:85a3:0000:0000:ac1f")
        self.assertEquals(peer.endpoints[1].port, 9002)

        self.assertEquals(peer.signatures[0], "dkaXIiCYUJtCg8Feh/BKvPYf4uFH9CJ/zY6J4MlA9BsjmcMe4YAblvNt/gJy31b1aGq3ue3h14mLMCu84rraDg==")

    def test_fromraw_toraw(self):
        peer = Peer.from_signed_raw(rawpeer)
        rendered_peer = peer.signed_raw()
        from_rendered_peer = Peer.from_signed_raw(rendered_peer)

        self.assertEquals(from_rendered_peer.currency, "beta_brousouf")
        self.assertEquals(from_rendered_peer.pubkey, "HsLShAtzXTVxeUtQd7yi5Z5Zh4zNvbu8sTEZ53nfKcqY")
        self.assertEquals(from_rendered_peer.blockid, "8-1922C324ABC4AF7EF7656734A31F5197888DDD52")
        self.assertEquals(len(from_rendered_peer.endpoints), 3)
        self.assertTrue(type(from_rendered_peer.endpoints[0]) is BMAEndpoint)
        self.assertTrue(type(from_rendered_peer.endpoints[1]) is BMAEndpoint)
        self.assertTrue(type(from_rendered_peer.endpoints[2]) is UnknownEndpoint)

        self.assertEquals(from_rendered_peer.endpoints[0].server, "some.dns.name")
        self.assertEquals(from_rendered_peer.endpoints[0].ipv4, "88.77.66.55")
        self.assertEquals(from_rendered_peer.endpoints[0].ipv6, "2001:0db8:0000:85a3:0000:0000:ac1f")
        self.assertEquals(from_rendered_peer.endpoints[0].port, 9001)

        self.assertEquals(from_rendered_peer.endpoints[1].server, "some.dns.name")
        self.assertEquals(from_rendered_peer.endpoints[1].ipv4, "88.77.66.55")
        self.assertEquals(from_rendered_peer.endpoints[1].ipv6, "2001:0db8:0000:85a3:0000:0000:ac1f")
        self.assertEquals(from_rendered_peer.endpoints[1].port, 9002)

        self.assertEquals(from_rendered_peer.signatures[0], "dkaXIiCYUJtCg8Feh/BKvPYf4uFH9CJ/zY6J4MlA9BsjmcMe4YAblvNt/gJy31b1aGq3ue3h14mLMCu84rraDg==")

