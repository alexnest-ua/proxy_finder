# @formatter:off
try:import gevent.monkey; gevent.monkey.patch_all()
except:raise
# @formatter:on
import argparse
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyRoxy import ProxyUtiles

from core import JUDGES, fix_ulimits, logger


def check_proxy(proxy, judges, timeout):
    for judge in judges:
        if proxy.check(judge, timeout):
            return True
    return False


def check_proxies(proxies, threads, timeout, retries):
    start = time.time()
    proxies = list(set(proxies))
    working_proxies = set()
    future_to_proxy = {}

    threads = min(threads, len(proxies))
    with ThreadPoolExecutor(threads) as executor:
        for proxy in proxies:
            judges = random.sample(JUDGES, retries)
            future = executor.submit(check_proxy, proxy, judges, timeout)
            future_to_proxy[future] = proxy

        percent = len(future_to_proxy) // 100
        for idx, future in enumerate(as_completed(future_to_proxy), start=1):
            if idx % percent == 0:
                logger.info(f'{int(idx * 100 / len(future_to_proxy))}% | Found: {len(working_proxies)}')

            if future.result():
                working_proxies.add(
                    future_to_proxy[future]
                )

    logger.info(f'Found {len(working_proxies)} proxies in {round(time.time() - start)}s')
    return working_proxies


def main():
    fix_ulimits()

    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('outfile')
    parser.add_argument('--threads', type=int, default=10000)
    parser.add_argument('--timeout', type=int, default=5)
    parser.add_argument('--retries', type=int, default=2)

    args = parser.parse_args()
    proxies = ProxyUtiles.readFromFile(args.infile)
    working = check_proxies(proxies, args.threads, args.timeout, args.retries)
    with open(args.outfile, 'w') as f:
        for proxy in working:
            f.write(str(proxy) + '\n')


if __name__ == '__main__':
    main()
