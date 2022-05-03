# @formatter:off
from itertools import cycle
try: import colorama; colorama.init()
except: pass
# @formatter:on
import argparse
import asyncio
import json
import os
import random
import time
from threading import Thread
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from colorama import Fore
from python_socks import ProxyType

from core import JUDGES, Proxy, THREADS_LIMIT, check_proxy, fix_ulimits, logger
from networks import get_random_ip
from report import report_proxy


CONFIG_URL = 'https://raw.githubusercontent.com/porthole-ascend-cinnamon/proxy_finder/main/config.json'
VERSION_URL = 'https://raw.githubusercontent.com/porthole-ascend-cinnamon/proxy_finder/main/version.txt'


async def fetch(url: str):
    attempts = 3
    async with ClientSession(raise_for_status=True) as session:
        for _ in range(attempts):
            try:
                async with session.get(url, timeout=5) as response:
                    return await response.text()
            except ClientError:
                pass
    return None


async def is_latest_version():
    resp = await fetch(VERSION_URL)
    latest = int(resp.strip())
    with open('version.txt', 'r') as f:
        current = int(f.read().strip())
    return current >= latest


class cl:
    MAGENTA = Fore.LIGHTMAGENTA_EX
    BLUE = Fore.LIGHTBLUE_EX
    GREEN = Fore.LIGHTGREEN_EX
    YELLOW = Fore.LIGHTYELLOW_EX
    RED = Fore.LIGHTRED_EX
    RESET = Fore.RESET


async def load_config(timeout) -> dict:
    response = await fetch(CONFIG_URL)
    if response:
        data = json.loads(response)
        return {
            'timeout': timeout or data['timeout'],
            'targets': cycle([
                (target['port'], ProxyType[target['proto'].upper()])
                for target in data['targets']
            ])
        }


async def report_success(proxy):
    result = await report_proxy(proxy)
    if result:
        logger.info(f'{cl.GREEN}Проксі {str(proxy)} надіслано, дякуємо!{cl.RESET}')
    else:
        logger.warning(
            f'{cl.RED}На жаль, проксі {proxy} не надіслане - зверніться до адміністратора @ddosseparbot{cl.RESET}'
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
            asyncio.create_task(report_success(proxy_str))
            config['outfile'].write(proxy_str + '\n')
            return
    finally:
        CHECKED += 1


async def worker(config):
    while True:
        host = get_random_ip()
        await try_host(config, host)
        await asyncio.sleep(random.random())


def start_workers(threads, config):
    return [
        asyncio.create_task(worker(config))
        for _ in range(threads)
    ]


async def statistic(file):
    while True:
        period = 30
        logger.info(f'{cl.YELLOW}Перевірено: {cl.BLUE}{CHECKED}{cl.YELLOW} | Знайдено: {cl.BLUE}{FOUND}{cl.RESET}')
        file.flush()
        await asyncio.sleep(period)


async def reload_config(config, timeout):
    period = 300
    while True:
        await asyncio.sleep(period)
        new_config = await load_config(timeout)
        if new_config:
            logger.info(f'{cl.YELLOW}Перевірено: {cl.BLUE}{CHECKED}{cl.YELLOW} | Знайдено: {cl.BLUE}{FOUND}{cl.RESET}')
            config.update(new_config)


async def main(outfile):
    parser = argparse.ArgumentParser()
    parser.add_argument('--threads', type=int, default=THREADS_LIMIT // 2)
    parser.add_argument('--timeout', type=int, default=None)
    args = parser.parse_args()

    threads = args.threads
    if threads > THREADS_LIMIT:
        logger.warning(f'{cl.MAGENTA}Обмеження {THREADS_LIMIT} потоків!{cl.RESET}')
        threads = THREADS_LIMIT

    if not await is_latest_version():
        logger.warning(f'{cl.RED}Запущена не остання версія - рекоменовано оновитися{cl.RESET}')

    config = await load_config(args.timeout)
    if not config:
        logger.error(f'{cl.RED}Не вдалося завантажити налаштування - перевірте мережу!{cl.RESET}')
        exit()

    config['outfile'] = outfile
    tasks = [
        asyncio.create_task(reload_config(config, args.timeout)),
        asyncio.create_task(statistic(outfile)),
        *start_workers(threads, config)
    ]
    await asyncio.gather(*tasks)


def main_wrapper():
    fix_ulimits()
    filename = f'proxy_{int(time.time())}.txt'
    logger.info(
        f'{cl.YELLOW}Проксі будуть автоматично відправлені на сервер, '
        f'а також збережені у файл {cl.BLUE}{filename}{cl.RESET}'
    )
    outfile = open(filename, 'w')
    try:
        Thread(target=lambda: asyncio.run(main(outfile)), daemon=True).start()
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info(f'{cl.MAGENTA}Завершуємо роботу{cl.RESET}')
    finally:
        if FOUND:
            logger.info(f'{cl.YELLOW}Збережено {cl.BLUE}{FOUND}{cl.YELLOW} у файл {cl.BLUE}{filename}{cl.RESET}')
        else:
            logger.warning(f'{cl.YELLOW}Проксі не знайдено, видаляємо файл {cl.BLUE}{filename}{cl.RESET}')
            os.remove(filename)
        outfile.close()


if __name__ == '__main__':
    main_wrapper()
