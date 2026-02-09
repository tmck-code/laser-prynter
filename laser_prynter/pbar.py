#!/usr/bin/env python3

from random import randint
import shutil
import time
from typing import NamedTuple

from laser_prynter.colour.gradient import interp_xyz

def indexes(t, w):
    for i in range(max(t+1,w)):
        yield int(i*(max(w,t)/min(w,t)))

class RGB(NamedTuple):
    r: int
    g: int
    b: int

DEFAULT_C1, DEFAULT_C2 = RGB(240,50,0), RGB(10,220,0)


class PBar:
    def __init__(self, total: int, c1: RGB=DEFAULT_C1, c2: RGB=DEFAULT_C2):
        self.t = total
        self.w = shutil.get_terminal_size().columns
        self.curr, self.g = 0, interp_xyz(c1, c2, max(self.t+1, self.w))
        self._iter_pbar = iter(self._pbar())


    def _pbar(self):
        for i, (r,g,b) in zip(indexes(self.t, self.w), self.g):
            yield ((i, (r,g,b)) for _ in range(self.curr, i))

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr >= max(self.t, self.w):
            raise StopIteration
        for i, (r,g,b) in next(self._iter_pbar):
            print(f'\x1b[38;2;{int(r)};{int(g)};{int(b)}m▉\x1b[0m', end='', flush=True)
            self.curr = i

    def update(self, n: int):
        for _ in range(n):
            next(self)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.curr = self.t


if __name__ == '__main__':
    import time
    c1, c2 = RGB(randint(0,255),randint(0,255),randint(0,255)), RGB(randint(0,255),randint(0,255),randint(0,255))
    # for i in PBar(100, c1, c2):
    #     time.sleep(0.05)
    with PBar(100, c1, c2) as pbar:
        for i in range(100):
            pbar.update(1)
            time.sleep(0.05)

