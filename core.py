import logging
import socket
from contextlib import suppress

from yarl import URL


logging.basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger('proxy_checker')
logger.setLevel('INFO')

JUDGES = [
    URL(judge).with_host(
        socket.gethostbyname(
            URL(judge).host
        )
    )
    for judge in [
        'http://www.proxy-listen.de/azenv.php',
        'http://www.wfuchs.de/azenv.php',
        'http://users.ugent.be/~bfdwever/start/env.cgi',
        'http://mojeip.net.pl/asdfa/azenv.php',
        'http://www.meow.org.uk/cgi-bin/env.pl',
        'http://httpheader.net',
        'tcp://1.1.1.1:53',
        'tcp://8.8.8.8:53',
        'http://google.ru/',
    ]
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
