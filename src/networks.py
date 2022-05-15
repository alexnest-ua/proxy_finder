import random
from bisect import bisect
from ipaddress import IPv4Address, IPv4Network


def _get_excludes_from_file(file):
    for row in file.read().splitlines():
        if '-' in row:
            parts = row.split('.')
            part_ranges = [part.split('-') for part in parts]
            ip_from = '.'.join(part_range[0] for part_range in part_ranges)
            ip_to = '.'.join(
                part_range[1] if len(part_range) == 2 else part_range[0]
                for part_range in part_ranges
            )
            yield (
                (int(IPv4Address(ip_from)), int(IPv4Address(ip_to)))
            )
        else:
            net = IPv4Network(row)
            yield (
                (int(net.network_address), int(net.broadcast_address))
            )


def _reduce(ranges):
    ranges.sort()
    new_ranges = []
    left, right = ranges[0]
    for rng in ranges[1:]:
        next_left, next_right = rng
        if right + 1 < next_left:  # Is the next range to the right?
            new_ranges.append((left, right))  # Close the current range.
            left, right = rng  # Start a new range.
        else:
            right = max(right, next_right)  # Extend the current range.
    new_ranges.append((left, right))  # Close the last range.
    return new_ranges


with open('src/exclude.txt', 'r') as f:
    _EXCLUDES = _reduce(list(_get_excludes_from_file(f)))


# For binary search
_EXCLUDE_STARTS = [ex[0] for ex in _EXCLUDES]


def need_exclude(ip: int):
    range_idx = bisect(_EXCLUDE_STARTS, ip) - 1
    exclude_range = _EXCLUDES[range_idx]
    return exclude_range[0] <= ip <= exclude_range[1]


def get_random_ip() -> str:
    while True:
        ip = random.randint(1, 0xffffffff)
        if not need_exclude(ip):
            return IPv4Address._string_from_ip_int(ip)
