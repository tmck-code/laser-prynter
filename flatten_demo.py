#!/usr/bin/env python3

import json
from itertools import chain

from tabulate import tabulate

def flatten(d: dict, prefix: str = "") -> dict:
    def pairs(d, prefix):
        return chain.from_iterable(
            pairs(v, f'{prefix}{k}.') if isinstance(v, dict) else [(f'{prefix}{k}', v)] for k, v in d.items()
        )
    return dict(pairs(d, prefix))

lines = []
with open('test_logs.txt') as istream:
    for l in istream:
        lines.append(list(flatten(json.loads(l.strip())).values()))

print(tabulate(lines))
