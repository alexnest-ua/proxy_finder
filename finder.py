# @formatter:off
try: import colorama; colorama.init()
except: pass
# @formatter:on
import argparse
import asyncio
import json
import os
import random
import time
from itertools import cycle
from threading import Thread

import requests
from python_socks import ProxyType

from src.core import JUDGES, Proxy, THREADS_LIMIT, check_proxy, cl, fix_ulimits, logger, setup_event_loop
from src.networks import get_random_ip
from src.report import sync_report_proxy


CONFIG_URL = 'https://raw.githubusercontent.com/porthole-ascend-cinnamon/proxy_finder/main/config.json'
VERSION_URL = 'https://raw.githubusercontent.com/porthole-ascend-cinnamon/proxy_finder/main/version.txt'


def sync_fetch(url: str):
    for _ in range(5):
        try:
            response = requests.get(url, verify=False, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            pass
    return None


async def fetch(url: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, sync_fetch, url)


async def is_latest_version():
    resp = await fetch(VERSION_URL)
    if not resp:
        logger.warning('New version check failed')
        return True

    latest = int(resp.strip())
    with open('version.txt', 'r') as f:
        current = int(f.read().strip())
    return current >= latest


async def load_config(timeout):
    response = await fetch(CONFIG_URL)
    if not response:
        logger.warning('Config was not updated')
        return

    data = json.loads(response)
    return {
        'timeout': timeout or data['timeout'],
        'report_url': data['report_url'],
        'targets': cycle([
            (target['port'], ProxyType[target['proto'].upper()])
            for target in data['targets']
        ])
    }


async def report_proxy(report_url, proxy):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, sync_report_proxy, report_url, proxy)


async def report_success(report_url, proxy):
    success, reason = await report_proxy(report_url, proxy)
    if success:
        logger.info(f'{cl.GREEN}Proxy {str(proxy)} sent, thanks!{cl.RESET}')
    else:
        logger.warning(
            f'{cl.RED}Proxy {proxy} could not be send - please contact admin @ddosseparbot ({reason}){cl.RESET}'
        )


CHECKED = FOUND = 0


async def try_host(config, host):
    global CHECKED, FOUND
    judge = next(JUDGES)
    port, proxy_type = next(config['targets'])
    proxy = Proxy.create(proxy_type, host, port)
    try:
        if await check_proxy(proxy, judge, config['timeout']):
            FOUND += 1
            proxy_str = f'{proxy_type.name.lower()}://{host}:{port}'
            asyncio.create_task(
                report_success(config['report_url'], proxy_str)
            )
            config['outfile'].write(proxy_str + '\n')
            return
    finally:
        CHECKED += 1


async def worker(config):
    while True:
        host = get_random_ip()
        await try_host(config, host)
        await asyncio.sleep(random.random())


async def start_workers(threads, config):
    for _ in range(100):
        for _ in range(threads // 100):
            yield asyncio.create_task(
                worker(config)
            )
        await asyncio.sleep(0.1)


async def statistic(file):
    while True:
        period = 30
        logger.info(
            f'{cl.YELLOW}Checked proxies: {cl.BLUE}{CHECKED:,}{cl.YELLOW} | '
            f'Found proxies: {cl.BLUE}{FOUND:,}{cl.RESET}'
        )
        file.flush()
        await asyncio.sleep(period)


async def reload_config(config, timeout):
    period = 300
    while True:
        await asyncio.sleep(period)
        try:
            new_config = await load_config(timeout)
            if new_config:
                config.update(new_config)
        except Exception as exc:
            logger.warning(f'Error while updating config: {repr(exc)}')


async def async_main(outfile, max_conns):
    parser = argparse.ArgumentParser()
    parser.add_argument('--threads', type=int, default=THREADS_LIMIT // 3)
    parser.add_argument('--timeout', type=int, default=None)
    args = parser.parse_args()

    threads = args.threads
    limit = THREADS_LIMIT
    if max_conns:
        limit = min(limit, max_conns - 50)
    if threads > limit:
        logger.warning(f'{cl.MAGENTA}Starting with {limit} threads available{cl.RESET}')
        threads = limit

    if not await is_latest_version():
        logger.warning(f'{cl.RED}New version available - please update (git pull){cl.RESET}')

    config = await load_config(args.timeout)
    if not config:
        logger.error(f'{cl.RED}Could not load config - check your connection!{cl.RESET}')
        exit()

    config['outfile'] = outfile
    tasks = [
        asyncio.create_task(
            reload_config(config, args.timeout)
        ),
        asyncio.create_task(
            statistic(outfile)
        )
    ]
    async for task in start_workers(threads, config):
        tasks.append(task)
    await asyncio.wait(tasks)


def main(outfile, max_conns):
    loop = setup_event_loop()
    loop.run_until_complete(async_main(outfile, max_conns))


def main_wrapper():
    max_conns = fix_ulimits()

    filename = f'proxy_{int(time.time())}.txt'
    logger.info(
        f'{cl.YELLOW}Proxy will be sent to the mhddos_proxy server '
        f'and saved into {cl.BLUE}{filename}{cl.RESET}'
    )
    outfile = open(filename, 'w')
    try:
        Thread(target=main, args=(outfile, max_conns), daemon=True).start()
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info(f'{cl.MAGENTA}Exiting...{cl.RESET}')
    finally:
        outfile.close()
        if FOUND:
            logger.info(f'{cl.YELLOW}Saved {cl.BLUE}{FOUND}{cl.YELLOW} proxies into {cl.BLUE}{filename}{cl.RESET}')
        else:
            logger.warning(f'{cl.YELLOW}No proxies found, deleting {cl.BLUE}{filename}{cl.RESET}')
            os.remove(filename)


if __name__ == '__main__':
    main_wrapper()
