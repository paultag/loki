#!/usr/bin/env python3
import asyncio
import aiohttp
import aiohttp.server


def create_proxy(api):
    def _():
        p = HttpProxyHandler()
        p.api = api
        return p
    return _


class HttpProxyHandler(aiohttp.server.ServerHttpProtocol):
    @asyncio.coroutine
    def handle_request(self, message, payload):
        path = message.path
        method = message.method

        remote = yield from aiohttp.request(method, "%s/%s" % (self.api, path))
        headers = remote.headers.items()
        headers = list(headers) + [("X-Loki-Version", "nil")]
        resp = aiohttp.Response(
            self.writer,
            remote.status,
            http_version=message.version
        )
        resp.add_headers(*headers)
        resp.send_headers()
        while True:
            try:
                chunk = yield from remote.content.read()
                resp.write(chunk)
            except aiohttp.parsers.EofStream:
                break
        resp.write_eof()
