# @formatter:off
try:import gevent.monkey; gevent.monkey.patch_all()
except:raise
# @formatter:on
import argparse
import os
import random
import time
from ipaddress import IPv4Address
from threading import Event, Thread

from PyRoxy import Proxy, ProxyType, Tools

from core import JUDGES, fix_ulimits, logger
from networks import random_ip_range


PROXIES = []
CHECKED = 0
event = Event()

PORTS = (
    (8080, ProxyType.HTTP),
    (5678, ProxyType.SOCKS4),
)


def generate_ip() -> str:
    if random.random() < 0.5:
        return Tools.Random.rand_ipv4()

    ip_from, ip_to = random_ip_range()
    return IPv4Address._string_from_ip_int(
        random.randint(ip_from, ip_to)
    )


def _try_host(out, host, timeout, retries):
    global CHECKED
    for judge in random.sample(JUDGES, retries):
        for port, proto in PORTS:
            try:
                proxy = Proxy(host, port, proto)
                CHECKED += 1
                if proxy.check(judge, timeout):
                    PROXIES.append(proxy)
                    logger.info(f'Found: {str(proxy)}')
                    out.write(str(proxy) + '\n')
                    return
            except KeyboardInterrupt:
                event.clear()
                raise


def worker(out, timeout, retries):
    while event.is_set():
        host = generate_ip()
        _try_host(out, host, timeout, retries)


def main(file):
    fix_ulimits()

    parser = argparse.ArgumentParser()
    parser.add_argument('--threads', type=int, default=10000)
    parser.add_argument('--timeout', type=int, default=3)
    parser.add_argument('--retries', type=int, default=1)

    args = parser.parse_args()
    event.set()

    threads = args.threads
    threads_limit = 15000
    if threads > threads_limit:
        logger.warning(f'Max 15.000 threads')
        threads = threads_limit

    for _ in range(100):
        for _ in range(threads // 100):
            Thread(target=worker, args=(file, args.timeout, args.retries), daemon=True).start()
        time.sleep(0.01)

    logger.info('All threads started')

    while event.is_set():
        time.sleep(10)
        file.flush()
        logger.info(f'Checked: {CHECKED} | Found: {len(PROXIES)}')


def main_wrapper():
    filename = f'proxy_{int(time.time())}.txt'
    logger.info(f'Proxies will be saved into {filename}')
    file = open(filename, 'w')
    try:
        main(file)
    except:
        logger.info('Shutting down')
        event.clear()
        if PROXIES:
            logger.info(f'Saved {len(PROXIES)} into {filename}')
        else:
            logger.warning(f'No proxies found, deleting {filename}')
            os.remove(filename)
        file.close()


if __name__ == '__main__':
    main_wrapper()
