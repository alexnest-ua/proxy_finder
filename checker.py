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

from PyRoxy import Proxy, ProxyType, Tools
from yarl import URL

from networks import IP_RANGES


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
    if random.random() < 0.5:
        return Tools.Random.rand_ipv4()

    ip_from, ip_to = random.choice(IP_RANGES)
    return IPv4Address._string_from_ip_int(
        random.randint(ip_from, ip_to)
    )


def _try_host(out, host, timeout, retries):
    global CHECKED
    for judge in random.sample(JUDGES, retries):
        for port, proto in PORTS:
            try:
                proxy = Proxy(host, port, ProxyType.HTTP)
                CHECKED += 1
                if proxy.check(judge, timeout):
                    PROXIES.append(proxy)
                    logger.info(f'Found: {str(proxy)}')
                    out.write(str(proxy) + '\n')
                    return
            except KeyboardInterrupt:
                event.clear()
                return


def worker(out, timeout, retries):
    while event.is_set():
        host = generate_ip()
        _try_host(out, host, timeout, retries)


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

    filename = f'working_proxies{int(time.time()) % 10000}.txt'
    logger.info(f'Proxies will be saved into {filename}')
    file = open(filename, 'wa')

    for _ in range(args.threads // 100):
        for _ in range(100):
            Thread(target=worker, args=(file, args.timeout, args.retries), daemon=True).start()
        time.sleep(0.1)

    Thread(target=stats, daemon=True).start()
    try:
        while True:
            time.sleep(2)
            file.flush()
    except KeyboardInterrupt:
        logger.info('Shutting down')
        event.clear()
        logger.info(f'Saved {len(PROXIES)} into {filename}')
        file.close()


if __name__ == '__main__':
    main()
