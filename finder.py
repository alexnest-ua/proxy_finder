# @formatter:off
try: import colorama; colorama.init()
except: pass
try:
    import gevent.monkey; gevent.monkey.patch_all()
    GEVENT = True
except ImportError:
    GEVENT = False
# @formatter:on
import argparse
import itertools
import json
import os
import random
import threading
import time
from collections import namedtuple
from ipaddress import IPv4Address
from threading import Event, Thread

import requests
from PyRoxy import Proxy, ProxyType, Tools
from colorama import Fore

from core import JUDGES, fix_ulimits, logger
from networks import random_ip_range
from report import report_proxy


CONFIG_URL = 'https://raw.githubusercontent.com/porthole-ascend-cinnamon/proxy_finder/main/config.json'
VERSION_URL = 'https://raw.githubusercontent.com/porthole-ascend-cinnamon/proxy_finder/main/version.txt'


def fetch(url):
    attempts = 3
    for attempt in range(attempts):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            pass
    return None


def is_latest_version():
    latest = int(fetch(VERSION_URL).strip())
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


class FastWriteCounter:
    def __init__(self):
        self._number_of_read = 0
        self._counter = itertools.count()
        self._read_lock = threading.Lock()

    def increment(self):
        next(self._counter)

    def value(self):
        with self._read_lock:
            value = next(self._counter) - self._number_of_read
            self._number_of_read += 1
        return value


CHECKED = FastWriteCounter()
FOUND = FastWriteCounter()

Config = namedtuple('Config', ('event', 'outfile', 'timeout', 'retries', 'targets', 'random_percents'))


def load_config(old_config, event, outfile, timeout, retries):
    response = fetch(CONFIG_URL)
    if response:
        data = json.loads(response)
        return Config(
            event,
            outfile,
            timeout or data['timeout'],
            retries or data['retries'],
            [
                (target['port'], ProxyType[target['proto'].upper()])
                for target in data['targets']
            ],
            data['random_percents']
        )
    elif old_config:
        return old_config
    else:
        logger.error(f'{cl.RED}Не вдалося завантажити налаштування - перевірте мережу!{cl.RESET}')
        raise RuntimeError


def _report_proxy(proxy):
    result = report_proxy(proxy)
    if result:
        logger.info(f'{cl.GREEN}Проксі {proxy} надіслано, дякуємо!{cl.RESET}')
    else:
        logger.warning(
            f'{cl.RED}На жаль, проксі {proxy} не надіслане - зверніться до адміністратора @ddosseparbot{cl.RESET}'
        )


def report_success(proxy):
    Thread(target=_report_proxy, args=[str(proxy)], daemon=True).start()


def generate_ip(random_percents) -> str:
    if random.random() < random_percents:
        return Tools.Random.rand_ipv4()

    ip_from, ip_to = random_ip_range()
    return IPv4Address._string_from_ip_int(
        random.randint(ip_from, ip_to)
    )


def _try_host(config, host):
    try:
        for judge in random.sample(JUDGES, config.retries):
            for port, proto in config.targets:
                if not config.event.is_set():
                    return

                proxy = Proxy(host, port, proto)
                CHECKED.increment()
                if proxy.check(judge, config.timeout):
                    FOUND.increment()
                    report_success(proxy)
                    config.outfile.write(str(proxy) + '\n')
                    return
    except KeyboardInterrupt:
        config.event.clear()


def worker(config):
    while config.event.is_set():
        host = generate_ip(config.random_percents)
        _try_host(config, host)


def start_workers(threads, config):
    for _ in range(100):
        for _ in range(max(threads // 100, 1)):
            Thread(target=worker, args=(config,), daemon=True).start()
        time.sleep(0.01)


def main(file):
    fix_ulimits()

    parser = argparse.ArgumentParser()
    parser.add_argument('--threads', type=int, default=5000 if GEVENT else 2000)
    parser.add_argument('--timeout', type=int, default=None)
    parser.add_argument('--retries', type=int, default=None)

    args = parser.parse_args()

    threads = args.threads
    threads_limit = 10000 if GEVENT else 3000
    if not GEVENT:
        logger.warning(f'{cl.MAGENTA}gevent не встановлено - підвищене використання системних ресурсів{cl.RESET}')

    if threads > threads_limit:
        logger.warning(f'{cl.MAGENTA}Обмеження {threads_limit} потоків!{cl.RESET}')
        threads = threads_limit

    period = 30
    restart_after = 900  # 15 minutes
    config = None
    while True:
        iterations = 0
        event = Event()
        event.set()
        config = load_config(config, event, file, args.timeout, args.retries)
        start_workers(threads, config)
        logger.info(f'{cl.GREEN}Усі процеси пошуку проксі запущено!{cl.RESET}')

        while event.is_set():
            logger.info(
                f'{cl.YELLOW}Перевірено: {cl.BLUE}{CHECKED.value()}{cl.YELLOW} | Знайдено: {cl.BLUE}{FOUND.value()}{cl.RESET}')
            file.flush()
            iterations += 1
            if period * iterations > restart_after:
                logger.info(f'{cl.MAGENTA}Перезапускаємо процеси пошуку проксі для стабільної роботи...{cl.RESET}')
                event.clear()
                time.sleep(args.timeout * args.retries)
                break
            time.sleep(period)


def main_wrapper():
    if not is_latest_version():
        logger.warning(f'{cl.RED}Запущена не остання версія - рекоменовано оновитися{cl.RESET}')

    filename = f'proxy_{int(time.time())}.txt'
    logger.info(
        f'{cl.YELLOW}Проксі будуть автоматично відправлені на сервер, а також збережені у файл {cl.BLUE}{filename}{cl.RESET}')
    file = open(filename, 'w')
    try:
        main(file)
    except:
        logger.info(f'{cl.MAGENTA}Завершуємо роботу{cl.RESET}')
    finally:
        found = FOUND.value()
        if found:
            logger.info(f'{cl.YELLOW}Збережено {cl.BLUE}{found}{cl.YELLOW} у файл {cl.BLUE}{filename}{cl.RESET}')
        else:
            logger.warning(f'{cl.YELLOW}Проксі не знайдено, видаляємо файл {cl.BLUE}{filename}{cl.RESET}')
            os.remove(filename)
        file.close()


if __name__ == '__main__':
    main_wrapper()
