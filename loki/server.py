#!/usr/bin/env python3
import asyncio
import aiohttp
import aiohttp.server

API = "http://api.opencivicdata.org"


class HttpProxyHandler(aiohttp.server.ServerHttpProtocol):
    @asyncio.coroutine
    def handle_request(self, message, payload):
        path = message.path
        method = message.method

        remote = yield from aiohttp.request(method, "%s/%s" % (API, path))
        headers = remote.headers.items()
        headers = list(headers) + [("X-Loki-Version", "nil")]

        resp = aiohttp.Response(
            self.writer,
            remote.status,
            http_version=message.version
        )

        resp.add_headers(*headers)
        resp.send_headers()

        ## XXX: Insert manglers here.

        chunk = yield from remote.content.read()
        resp.write(chunk)
        resp.write_eof()


loop = asyncio.get_event_loop()
coro = loop.create_server(HttpProxyHandler, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)
print('serving on {}'.format(server.sockets[0].getsockname()))

try:
    loop.run_forever()
except KeyboardInterrupt:
    print("exit")
finally:
    server.close()
    loop.close()
