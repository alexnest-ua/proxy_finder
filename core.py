import asyncio
import logging
import socket
from contextlib import suppress

import async_timeout
from python_socks.async_.asyncio import Proxy
from yarl import URL


try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

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
]

THREADS_LIMIT = 15000

JUDGES = [
    (URL('http://wfuchs.de/azenv.php'), 'AZ Environment', socket.gethostbyname('wfuchs.de')),
    (URL('http://www.meow.org.uk/cgi-bin/env.pl'), 'webmaster@meow.org.uk', socket.gethostbyname('www.meow.org.uk')),
    (URL('http://mojeip.net.pl/asdfa/azenv.php'), 'AZ Environment', socket.gethostbyname('mojeip.net.pl')),
    (URL('http://azenv.net/'), 'PHP Proxy Judge', socket.gethostbyname('azenv.net')),
    (URL('http://httpheader.net/azenv.php'), 'AZ Environment', socket.gethostbyname('httpheader.net')),
    (URL('http://www.proxyjudge.info/azenv.php'), 'AZ Environment', socket.gethostbyname('www.proxyjudge.info')),
]


def fix_ulimits():
    try:
        import resource
    except ImportError:
        return

    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    if soft < hard:
        resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))


async def _make_request(proxy, url, expected, ip, timeout):
    request = (
        f"GET {url.path} HTTP/1.1\r\n"
        f"Host: {url.host}\r\n"
        f"User-Agent: curl/7.74.0\r\n"
        f"Accept: */*\r\n\r\n"
    ).encode()

    parser = HttpParser()
    status, body = None, b""
    writer = None
    try:
        sock = await proxy.connect(dest_host=ip, dest_port=url.port, timeout=timeout)
        reader, writer = await asyncio.open_connection(host=None, port=None, sock=sock)

        # Separate timeout for connect and read-write
        async with async_timeout.timeout(timeout):
            writer.write(request)
            await writer.drain()
            while True:
                response = await reader.read(1024)
                recved = len(response)
                if recved == 0:
                    return False

                nparsed = parser.execute(response, recved)
                if nparsed != recved:
                    return False

                if status is None and parser.is_headers_complete():
                    status = parser.get_status_code()
                    if status != 200:
                        return False

                if parser.is_partial_body():
                    body += parser.recv_body()
                    if len(body) >= 256:
                        return expected in body.decode()

                if parser.is_message_complete():
                    return False
    finally:
        if writer:
            with suppress(Exception):
                writer.close()
                await writer.wait_closed()


async def check_proxy(proxy, judge, timeout):
    url, expected, ip = judge
    with suppress(Exception):
        return await _make_request(proxy, url, expected, ip, timeout)
    return False
