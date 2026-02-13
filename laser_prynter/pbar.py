#!/usr/bin/env python3

from __future__ import annotations
from random import randint
import shutil
import time
from typing import NamedTuple

from laser_prynter.colour.gradient import interp_xyz


def indexes(t: int, w: int):
    if t > w:
        for i in range(t + 1):
            yield int(i * (w / t))
    else:
        for i in range(w + 1):
            yield int(i * (t / w))


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
        self.progress = 0 # Track logical progress out of total
        if self.t > self.w:
            self.g = list(interp_xyz(c1, c2, self.t+1))
        else:
            self.g = list(interp_xyz(c1, c2, self.w+1))

        self._iter_pbar = iter(self._pbar())
        # self._initial_bar()

    def _initial_bar(self):
        "print initial bar in end color"
        print(
            f'\x1b[38;2;{self.c2.r};{self.c2.g};{self.c2.b}m' + '▉' * self.w + '\x1b[0m',
            end='',
            flush=True,
        )
        print('\r', end='', flush=True)

    @staticmethod
    def randgrad():
        return (
            RGB(randint(0, 255), randint(0, 255), randint(0, 255)),
            RGB(randint(0, 255), randint(0, 255), randint(0, 255)),
        )

    def _pbar(self):
        for x in range(self.curr, self.w):
            if self.t > self.w:
                tpos = int((x / self.w) * self.t)
                color = self.g[tpos]
            else:
                color = self.g[x]
            yield ((x, color),)

    def __iter__(self):
        return self

    def __next__(self):
        for i, (r, g, b) in next(self._iter_pbar):
            print(f'\x1b[38;2;{int(r)};{int(g)};{int(b)}m▉\x1b[0m', end='', flush=True)
            self.curr = i
        if self.curr >= self.w:
            raise StopIteration

    def update(self, n: int):
        "update the progress bar by n steps"
        self.progress = min(self.progress + n, self.t)
        # Calculate target terminal position based on logical progress
        target_pos = int((self.progress / self.t) * self.w)
        # Update bar to target position
        while self.curr < target_pos:
            try:
                next(self)
            except StopIteration:
                break

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.curr = self.t


if __name__ == '__main__':
    # for i in PBar(100, *PBar.randgrad()):
    #     time.sleep(0.01)

    with PBar(100) as pbar:
        for i in range(100):
            time.sleep(0.01)
            pbar.update(1)
