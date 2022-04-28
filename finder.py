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
from report import report_proxy


CHECKED = 0
FOUND = 0

PORTS = [
    (8080, ProxyType.HTTP),
    (5678, ProxyType.SOCKS4),
]


def _report_proxy(proxy):
    result = report_proxy(proxy)
    if result:
        logger.info(f'Проксі {proxy} надіслано, дякуємо!')
    else:
        logger.warning(f'На жаль, проксі {proxy} не надіслане - зверніться до адміністратора')


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
    global CHECKED, FOUND
    try:
        for judge in random.sample(JUDGES, retries):
            for port, proto in PORTS:
                if not event.is_set():
                    return

                proxy = Proxy(host, port, proto)
                CHECKED += 1
                if proxy.check(judge, timeout):
                    FOUND += 1
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
    parser.add_argument('--threads', type=int, default=5000)
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
    threads_limit = 10000
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
        logger.info('Усі процеси запущено!')

        while event.is_set():
            time.sleep(period)
            logger.info(f'Перевірено: {CHECKED} | Знайдено: {FOUND}')
            file.flush()
            iterations += 1
            if period * iterations > restart_after:
                logger.info('Перезапускаємо процеси для стабільної роботи...')
                event.clear()
                time.sleep(args.timeout * args.retries)
                break


def main_wrapper():
    filename = f'proxy_{int(time.time())}.txt'
    logger.info(f'Проксі будуть автоматично відправлені на сервер, а також збережені у файл {filename}')
    file = open(filename, 'w')
    try:
        main(file)
    except:
        logger.info('Завершуємо роботу')
    finally:
        if FOUND:
            logger.info(f'Збережено {FOUND} у файл {filename}')
        else:
            logger.warning(f'Проксі не знайдено, видаляємо файл {filename}')
            os.remove(filename)
        file.close()


if __name__ == '__main__':
    main_wrapper()
