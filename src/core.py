import asyncio
import logging
import selectors
import socket
import sys
from asyncio import events
from contextlib import suppress
from itertools import cycle

import async_timeout
from python_socks.async_.asyncio import Proxy, Socks5Proxy
from yarl import URL

from .httpparser import HttpParser


logging.basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger('proxy_checker')
logger.setLevel('INFO')

__all__ = [
    'Proxy',
    'logger',
    'JUDGES',
    'fix_ulimits',
    'check_proxy',
    'THREADS_LIMIT',
    'setup_event_loop',
]

THREADS_LIMIT = 15000

# TODO: check whether judge is up and running
JUDGES = cycle([
    (URL('http://wfuchs.de/azenv.php'), b'<title>AZ Environment', socket.gethostbyname('wfuchs.de')),
    (
        URL('http://www.meow.org.uk/cgi-bin/env.pl'),
        b'<pre>CONTEXT_DOCUMENT_ROOT=/var/www/meow.org.uk/cgi-bin/',
        socket.gethostbyname('www.meow.org.uk')
    ),
    (URL('http://mojeip.net.pl/asdfa/azenv.php'), b'<title>AZ Environment', socket.gethostbyname('mojeip.net.pl')),
    (URL('http://azenv.net/'), b'<title>AZ Environment', socket.gethostbyname('azenv.net')),
    (URL('http://httpheader.net/azenv.php'), b'<title>AZ Environment', socket.gethostbyname('httpheader.net')),
])


def fix_ulimits():
    try:
        import resource
    except ImportError:
        return None

    min_hard = 2 ** 16
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    # Try to raise hard limit if it's too low
    if hard < min_hard:
        with suppress(Exception):
            resource.setrlimit(resource.RLIMIT_NOFILE, (min_hard, min_hard))
            return min_hard

    # At least raise soft limit to the hard limit
    resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
    return hard


async def _make_request(proxy, url, expected, ip, timeout):
    request = (
        f"GET {url.path} HTTP/1.1\r\n"
        f"Host: {url.host}\r\n"
        f"User-Agent: curl/7.74.0\r\n"
        f"Accept: */*\r\n\r\n"
    ).encode()

    status_line = b'HTTP/1.1 200'
    sock = await proxy.connect(dest_host=ip, dest_port=url.port, timeout=timeout)
    reader, writer = await asyncio.open_connection(host=None, port=None, sock=sock)
    # Separate timeout for connect and read-write
    async with async_timeout.timeout(timeout):
        try:
            writer.write(request)
            await writer.drain()

            parser = HttpParser()
            response, status, body = b'', None, b''
            while True:
                data = await reader.read(1024)
                if not data:
                    return False

                response += data

                # Issue with variable length bind address in socks5 protocol
                if isinstance(proxy, Socks5Proxy) and status is None and status_line in response:
                    idx = response.index(status_line)
                    if idx != 0 and idx <= 32:
                        parser = HttpParser()
                        response = response[idx:]
                        data = response

                # Fast-fail route
                if status is None and len(response) >= len(status_line) and not response.startswith(status_line):
                    return False

                recved = len(data)
                nparsed = parser.execute(data, recved)
                if nparsed != recved:
                    return False

                if status is None and parser.is_headers_complete():
                    status = parser.get_status_code()
                    if status != 200:
                        return False

                body += parser.recv_body()
                if len(response) >= 512 or len(body) >= 256 or parser.is_message_complete():
                    return expected in body

        finally:
            writer.close()
            await writer.wait_closed()


async def check_proxy(proxy, judge, timeout):
    url, expected, ip = judge
    with suppress(Exception):
        return await _make_request(proxy, url, expected, ip, timeout)
    return False


def _safe_connection_lost(transport, exc):
    try:
        transport._protocol.connection_lost(exc)
    finally:
        if hasattr(transport._sock, 'shutdown') and transport._sock.fileno() != -1:
            try:
                transport._sock.shutdown(socket.SHUT_RDWR)
            except ConnectionResetError:
                pass
        transport._sock.close()
        transport._sock = None
        server = transport._server
        if server is not None:
            server._detach()
            transport._server = None


def _patch_proactor_connection_lost():
    """
    The issue is described here:
      https://github.com/python/cpython/issues/87419

    The fix is going to be included into Python 3.11. This is merely
    a backport for already versions.
    """
    from asyncio.proactor_events import _ProactorBasePipeTransport
    setattr(_ProactorBasePipeTransport, "_call_connection_lost", _safe_connection_lost)


def setup_event_loop():
    WINDOWS = sys.platform == "win32"

    if WINDOWS:
        _patch_proactor_connection_lost()
        loop = asyncio.ProactorEventLoop()
    elif hasattr(selectors, "PollSelector"):
        selector = selectors.PollSelector()
        loop = asyncio.SelectorEventLoop(selector)
    else:
        loop = events.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop
