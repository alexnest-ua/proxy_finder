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
import os
import random
import threading
import time
from ipaddress import IPv4Address
from threading import Event, Thread

from PyRoxy import Proxy, ProxyType, Tools
from colorama import Fore

from core import JUDGES, fix_ulimits, logger
from networks import random_ip_range
from report import report_proxy


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

PORTS = [
    (8080, ProxyType.HTTP),
    (5678, ProxyType.SOCKS4),
]


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


def generate_ip() -> str:
    if random.random() < 0.5:
        return Tools.Random.rand_ipv4()

    ip_from, ip_to = random_ip_range()
    return IPv4Address._string_from_ip_int(
        random.randint(ip_from, ip_to)
    )


def _try_host(event, out, host, timeout, retries):
    try:
        for judge in random.sample(JUDGES, retries):
            for port, proto in PORTS:
                if not event.is_set():
                    return

                proxy = Proxy(host, port, proto)
                CHECKED.increment()
                if proxy.check(judge, timeout):
                    FOUND.increment()
                    report_success(proxy)
                    out.write(str(proxy) + '\n')
                    return
    except KeyboardInterrupt:
        event.clear()


def worker(event, out, timeout, retries):
    while event.is_set():
        host = generate_ip()
        _try_host(event, out, host, timeout, retries)


def start_workers(threads, event, file, timeout, retries):
    for _ in range(100):
        for _ in range(max(threads // 100, 1)):
            Thread(target=worker, args=(event, file, timeout, retries), daemon=True).start()
        time.sleep(0.01)


def main(file):
    fix_ulimits()

    parser = argparse.ArgumentParser()
    parser.add_argument('--threads', type=int, default=5000 if GEVENT else 2000)
    parser.add_argument('--timeout', type=int, default=3)
    parser.add_argument('--retries', type=int, default=1)
    parser.add_argument('--socks5', default=False, action='store_true')

    args = parser.parse_args()

    if args.socks5:
        PORTS.extend((
            (5389, ProxyType.SOCKS5),
            (1080, ProxyType.SOCKS5),
        ))

    threads = args.threads
    threads_limit = 10000 if GEVENT else 5000
    if not GEVENT:
        logger.warning(f'{cl.MAGENTA}gevent не встановлено - потребується більше системних ресурсів{cl.RESET}')

    if threads > threads_limit:
        logger.warning(f'Обмеження {threads_limit} потоків!')
        threads = threads_limit

    period = 30
    restart_after = 900  # 15 minutes
    while True:
        iterations = 0
        event = Event()
        event.set()
        start_workers(threads, event, file, args.timeout, args.retries)
        logger.info(f'{cl.BLUE}Усі процеси запущено!{cl.RESET}')

        while event.is_set():
            time.sleep(period)
            logger.info(f'Перевірено: {CHECKED.value()} | Знайдено: {FOUND.value()}')
            file.flush()
            iterations += 1
            if period * iterations > restart_after:
                logger.info('Перезапускаємо процеси для стабільної роботи...')
                event.clear()
                time.sleep(args.timeout * args.retries)
                break


def main_wrapper():
    filename = f'proxy_{int(time.time())}.txt'
    logger.info(
        f'Проксі будуть автоматично відправлені на сервер, а також збережені у файл {cl.YELLOW}{filename}{cl.RESET}'
    )
    file = open(filename, 'w')
    try:
        main(file)
    except:
        logger.info(f'{Fore.LIGHTBLUE_EX}Завершуємо роботу{Fore.RESET}')
    finally:
        found = FOUND.value()
        if found:
            logger.info(f'Збережено {cl.BLUE}{found}{cl.RESET} у файл {cl.YELLOW}{filename}{cl.RESET}')
        else:
            logger.warning(f'Проксі не знайдено, видаляємо файл {cl.YELLOW}{filename}{cl.RESET}')
            os.remove(filename)
        file.close()


if __name__ == '__main__':
    main_wrapper()
