#!/usr/bin/env python3

import shutil
import time

from laser_prynter.colour.gradient import interp_xyz

def indexes(t, w):
    for i in range(max(t+1,w)):
        yield int(i*(max(w,t)/min(w,t)))

class PBar:
    def __init__(self, total):
        self.t = total
        self.w = shutil.get_terminal_size().columns
        self.curr, self.g = 0, interp_xyz((240,50,0),(10,220,0), max(self.t+1, self.w))
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
            print(f'\x1b[38;2;{int(r)};{int(g)};{int(b)}mN\x1b[0m', end='', flush=True)
            self.curr = i
