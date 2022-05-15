import argparse
import asyncio
import time

from src.core import JUDGES, Proxy, THREADS_LIMIT, check_proxy, fix_ulimits, logger, setup_event_loop


working_proxies = set()
CHECKED = 0


async def _check_proxy(proxy, judges, timeout):
    for judge in judges:
        if await check_proxy(proxy, judge, timeout):
            return True
    return False


async def checker(proxies, timeout, retries):
    global CHECKED
    for proxy in proxies:
        judges = [next(JUDGES) for _ in range(retries)]
        if await _check_proxy(proxy, judges, timeout):
            working_proxies.add(proxy)
        CHECKED += 1


async def progress(total):
    while True:
        logger.info(f'{CHECKED}/{total} | Found: {len(working_proxies)}')
        await asyncio.sleep(10)


async def check_proxies(proxies, threads, timeout, retries):
    start = time.time()
    asyncio.create_task(progress(len(proxies)))
    proxies_iter = iter(proxies)
    tasks = [
        asyncio.create_task(checker(proxies_iter, timeout, retries))
        for _ in range(threads)
    ]
    await asyncio.wait(tasks)
    logger.info(f'Found {len(working_proxies)} proxies in {round(time.time() - start)}s')
    return working_proxies


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('outfile')
    parser.add_argument('--threads', type=int, default=THREADS_LIMIT // 5)
    parser.add_argument('--timeout', type=int, default=5)
    parser.add_argument('--retries', type=int, default=2)

    args = parser.parse_args()

    threads = args.threads
    if threads > THREADS_LIMIT:
        logger.warning(f'Обмеження {THREADS_LIMIT} потоків!')
        threads = THREADS_LIMIT

    with open(args.infile, 'r') as f:
        proxies = {
            Proxy.from_url(line): line
            for line in f.read().splitlines()
            if line.split()
        }

    working = await check_proxies(proxies, threads, args.timeout, args.retries)
    with open(args.outfile, 'w') as f:
        for proxy in working:
            f.write(proxies[proxy] + '\n')


if __name__ == '__main__':
    fix_ulimits()
    loop = setup_event_loop()
    loop.run_until_complete(main())
