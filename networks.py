import csv
import glob
from ipaddress import IPv4Address


def load():
    for filename in glob.glob('networks/*.csv'):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    yield int(IPv4Address(row[0])), int(IPv4Address(row[1]))


IP_RANGES = list(load())
