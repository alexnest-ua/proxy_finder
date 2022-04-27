import csv
import glob
import random
from ipaddress import IPv4Address


def load():
    for filename in glob.glob('networks/*.csv'):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    yield int(IPv4Address(row[0])), int(IPv4Address(row[1]))


_IP_RANGES = list(load())
_WEIGHTS = [r[1] - r[0] for r in _IP_RANGES]


def random_ip_range():
    return random.choices(_IP_RANGES, weights=_WEIGHTS, k=1)[0]
