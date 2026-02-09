#!/usr/bin/env python3

from __future__ import annotations
from random import randint
import shutil
import time
from typing import NamedTuple

from laser_prynter.colour.gradient import interp_xyz


def indexes(t, w):
    for i in range(max(t + 1, w)):
        yield int(i * (max(w, t) / min(w, t)))


class RGB(NamedTuple):
    r: int
    g: int
    b: int


DEFAULT_C1, DEFAULT_C2 = RGB(240, 50, 0), RGB(10, 220, 0)


class PBar:
    def __init__(self, total: int, c1: RGB = DEFAULT_C1, c2: RGB = DEFAULT_C2):
        self.t = total
        self.w = shutil.get_terminal_size().columns
        self.c1, self.c2 = c1, c2
        self.curr = 0
        self.g = interp_xyz(c1, c2, self.t + 1)
        self._iter_pbar = iter(self._pbar())
        self._initial_bar()

    def _initial_bar(self):
        "print initial bar in end color"
        print(
            f'\x1b[38;2;{self.c2.r};{self.c2.g};{self.c2.b}m' + '▉' * self.w + '\x1b[0m',
            end='',
            flush=True,
        )
        print('\r', end='', flush=True)

    def grad(self, c1: RGB, c2: RGB):
        self.g = interp_xyz(c1, c2, self.t + 1)
        self._iter_pbar = iter(self._pbar())
        return self

    @staticmethod
    def randgrad():
        return (
            RGB(randint(0, 255), randint(0, 255), randint(0, 255)),
            RGB(randint(0, 255), randint(0, 255), randint(0, 255)),
        )

    def _pbar(self):
        for i, (r, g, b) in zip(indexes(self.t, self.w), self.g):
            yield ((i, (r, g, b)) for _ in range(self.curr, i))

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr >= max(self.t, self.w):
            raise StopIteration
        for i, (r, g, b) in next(self._iter_pbar):
            print(f'\x1b[38;2;{int(r)};{int(g)};{int(b)}m▉\x1b[0m', end='', flush=True)
            self.curr = i

    def update(self, n: int):
        for _ in range(n):
            next(self)

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.curr = self.t


if __name__ == '__main__':
    import time

    c1, c2 = RGB(255, 0, 0), RGB(0, 255, 0)
    for i in PBar(200, c1, c2):
        time.sleep(0.01)
    print('\r' + ' ' * shutil.get_terminal_size().columns + '\r', end='', flush=True)

    # clear the bar
    for i in PBar(100, *PBar.randgrad()):
        time.sleep(0.05)
