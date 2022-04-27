# @formatter:off
try:import gevent.monkey; gevent.monkey.patch_all()
except:raise
# @formatter:on
import argparse
import logging
import random
import socket
import time
from contextlib import suppress
from ipaddress import IPv4Address
from threading import Event, Thread

from PyRoxy import Proxy, ProxyType
from yarl import URL

from networks import RU_NETWORK


logging.basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger('mhddos_proxy')
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

PROXIES = []
CHECKED = 0
event = Event()

PORTS = (
    (8080, ProxyType.HTTP),
    (999, ProxyType.HTTP),

    (5678, ProxyType.SOCKS4),
    (4153, ProxyType.SOCKS4),
    (4145, ProxyType.SOCKS4),
)


def generate_ip() -> str:
    ip_from, ip_to = random.choice(RU_NETWORK)
    return IPv4Address._string_from_ip_int(
        random.randint(ip_from, ip_to)
    )


def _try_host(host, timeout, retries):
    global CHECKED
    for judge in random.sample(JUDGES, retries):
        for port, proto in PORTS:
            proxy = Proxy(host, port, ProxyType.HTTP)
            CHECKED += 1
            if proxy.check(judge, timeout):
                PROXIES.append(proxy)
                logger.info(str(proxy))
                return


def worker(timeout, retries):
    while event.is_set():
        host = generate_ip()
        _try_host(host, timeout, retries)


def stats():
    while event.is_set():
        logger.info(f'Checked: {CHECKED} | Found: {len(PROXIES)}')
        time.sleep(10)


def fix_ulimits():
    try:
        import resource
    except ImportError:
        return

    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    if soft < hard:
        with suppress(Exception):
            resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))


def main():
    fix_ulimits()

    parser = argparse.ArgumentParser()
    parser.add_argument('--threads', type=int, default=5000)
    parser.add_argument('--timeout', type=int, default=3)
    parser.add_argument('--retries', type=int, default=1)

    args = parser.parse_args()
    event.set()

    Thread(target=stats, daemon=True).start()
    for _ in range(args.threads // 100):
        for _ in range(100):
            Thread(target=worker, args=(args.timeout, args.retries), daemon=True).start()
        time.sleep(0.1)
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info('Shutting down')
        event.clear()
        if PROXIES:
            filename = f'working_proxies{int(time.time())}.txt'
            logger.info(f'Saving {len(PROXIES)} into {filename}')
            with open(filename, 'w') as f:
                for proxy in PROXIES:
                    f.write(str(proxy) + '\n')


if __name__ == '__main__':
    main()
