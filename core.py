import logging
import socket
from contextlib import suppress

from http_parser.http import HttpStream
from http_parser.reader import SocketReader
from python_socks.sync.v2 import Proxy as PySocksProxy
from yarl import URL


logging.basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger('proxy_checker')
logger.setLevel('INFO')

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
        with suppress(Exception):
            resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))

            resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))


def check_proxy(proxy, judge, timeout):
    url, expected, ip = judge
    request = (
        f"GET {url.path} HTTP/1.1\r\n"
        f"Host: {url.host}\r\n"
        f"User-Agent: curl/7.74.0\r\n"
        f"Accept: */*\r\n\r\n"
    ).encode()

    py_proxy = PySocksProxy.from_url(str(proxy))
    with suppress(Exception):
        with py_proxy.connect(ip, url.port, timeout=timeout).socket as sock:
            sock.sendall(request)
            parser = HttpStream(SocketReader(sock))
            status = parser.status_code()
            if status != 200:
                return False

            response = parser.body_file(binary=False).read(256)
            if expected in response:
                return True

    return False
