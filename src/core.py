import asyncio
import logging
import selectors
import socket
import sys
import warnings
from asyncio import events
from asyncio.log import logger as asyncio_logger
from contextlib import suppress
from itertools import cycle

import async_timeout
from colorama import Fore
from python_socks.async_.asyncio import Proxy, Socks5Proxy
from yarl import URL

from .httpparser import HttpParser


class RemoveUselessWarnings(logging.Filter):
    def filter(self, record):
        return all((
            "socket.send() raised exception." not in record.getMessage(),
            "SSL connection is closed" not in record.getMessage()
        ))


WINDOWS = sys.platform == "win32"
WINDOWS_WAKEUP_SECONDS = 0.5

warnings.filterwarnings("ignore")

logging.basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger('proxy_checker')
logger.setLevel('INFO')

# Make asyncio logger a little bit less noisy
asyncio_logger.addFilter(RemoveUselessWarnings())

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


class cl:
    MAGENTA = Fore.LIGHTMAGENTA_EX
    BLUE = Fore.LIGHTBLUE_EX
    GREEN = Fore.LIGHTGREEN_EX
    YELLOW = Fore.LIGHTYELLOW_EX
    RED = Fore.LIGHTRED_EX
    RESET = Fore.RESET


def fix_ulimits():
    try:
        import resource
    except ImportError:
        return None

    min_limit = 2 ** 15
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    # Try to raise hard limit if it's too low
    if hard < min_limit:
        with suppress(ValueError):
            resource.setrlimit(resource.RLIMIT_NOFILE, (min_limit, min_limit))
            soft = hard = min_limit

    # Try to raise soft limit to hard limit
    if soft < hard:
        with suppress(ValueError):
            resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
            soft = hard

    return soft


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


async def _windows_support_wakeup() -> None:
    """See more info here:
        https://bugs.python.org/issue23057#msg246316
    """
    while True:
        await asyncio.sleep(WINDOWS_WAKEUP_SECONDS)


def _handle_uncaught_exception(loop: asyncio.AbstractEventLoop, context) -> None:
    error_message = context.get("exception", context["message"])
    logger.debug(f"Uncaught event loop exception: {error_message}")


def setup_event_loop() -> asyncio.AbstractEventLoop:
    uvloop = False
    try:
        __import__("uvloop").install()
        uvloop = True
        logger.info(
            f"{cl.GREEN}'uvloop' успішно активований "
            f"(підвищенна ефективність роботи з мережею){cl.RESET}"
        )
    except:
        pass

    if uvloop:
        loop = events.new_event_loop()
    elif WINDOWS:
        _patch_proactor_connection_lost()
        loop = asyncio.ProactorEventLoop()
        # This is to allow CTRL-C to be detected in a timely fashion,
        # see: https://bugs.python.org/issue23057#msg246316
        loop.create_task(_windows_support_wakeup())
    elif hasattr(selectors, "DefaultSelector"):
        selector = selectors.DefaultSelector()
        loop = asyncio.SelectorEventLoop(selector)
    else:
        loop = events.new_event_loop()
    loop.set_exception_handler(_handle_uncaught_exception)
    asyncio.set_event_loop(loop)
    return loop
