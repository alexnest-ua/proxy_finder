import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from judges import JUDGES


def check_proxy(proxy, judges, timeout):
    for judge in judges:
        if proxy.check(judge, timeout):
            return True
    return False


def check_proxies(proxies, threads=5000, timeout=5, retries=2):
    start = time.time()
    proxies = list(set(proxies))
    working_proxies = set()
    future_to_proxy = {}

    with ThreadPoolExecutor(threads) as executor:
        for proxy in proxies:
            judges = random.sample(JUDGES, retries)
            future = executor.submit(check_proxy, proxy, judges, timeout)
            future_to_proxy[future] = proxy

        for future in as_completed(future_to_proxy):
            if future.result():
                working_proxies.add(
                    future_to_proxy[future]
                )

    print(f'Found {len(working_proxies)} proxies in {round(time.time() - start)}s')
    return working_proxies
