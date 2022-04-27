# @formatter:off
try:import gevent.monkey; gevent.monkey.patch_all()
except:raise
# @formatter:on

import argparse
import random
import socket
import time
from ipaddress import IPv4Address
from threading import Thread

from PyRoxy import Proxy, ProxyType
from yarl import URL

from networks import RU_NETWORK


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
                print(str(proxy))
                return


def worker(timeout, retries):
    while True:
        host = generate_ip()
        _try_host(host, timeout, retries)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--threads', type=int, default=5000)
    parser.add_argument('--timeout', type=int, default=3)
    parser.add_argument('--retries', type=int, default=1)

    args = parser.parse_args()
    for _ in range(args.threads // 100):
        for _ in range(100):
            Thread(target=worker, args=(args.timeout, args.retries), daemon=True).start()
        time.sleep(0.1)

    try:
        while True:
            time.sleep(30)
            print(f'Checked: {CHECKED} | Found: {len(PROXIES)}')
    finally:
        if PROXIES:
            with open(f'working_proxies{int(time.time())}.txt', 'w') as f:
                for proxy in PROXIES:
                    f.write(str(proxy) + '\n')


if __name__ == '__main__':
    main()
