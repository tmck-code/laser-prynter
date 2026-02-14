#!/usr/bin/env python3

from __future__ import annotations

import shutil
import sys
import time
from random import randint
from typing import Iterator, NamedTuple

from laser_prynter.colour.gradient import interp_xyz


def indexes(t: int, w: int) -> Iterator[int]:
    if t > w:
        for i in range(t + 1):
            yield int(i * (w / t))
    else:
        for i in range(w + 1):
            yield int(i * (t / w))


def _print_to_terminal(s: str) -> None:
    'Helper function to perform ANSI escape sequences.'
    sys.stdout.write(s)
    sys.stdout.flush()


class RGB(NamedTuple):
    r: int
    g: int
    b: int


DEFAULT_C1, DEFAULT_C2 = RGB(240, 50, 0), RGB(10, 220, 0)


class PBar:
    def __init__(self, total: int, c1: RGB = DEFAULT_C1, c2: RGB = DEFAULT_C2):
        self.t = total
        self.w = shutil.get_terminal_size().columns
        self.h = shutil.get_terminal_size().lines
        self.c1, self.c2 = c1, c2
        self.curr = 0
        self.progress = 0  # Track logical progress out of total
        if self.t > self.w:
            self.g = list(interp_xyz(c1, c2, self.t + 1))
        else:
            self.g = list(interp_xyz(c1, c2, self.w + 1))

        self._iter_pbar = iter(self._pbar())

    @staticmethod
    def randgrad() -> tuple[RGB, RGB]:
        return (
            RGB(randint(0, 255), randint(0, 255), randint(0, 255)),
            RGB(randint(0, 255), randint(0, 255), randint(0, 255)),
        )

    def _pbar(self) -> Iterator[tuple[tuple[int, RGB]]]:
        for x in range(self.w + 1):  # TODO: i'm so dumb, why do I need a +1 here?
            if self.t > self.w:
                tpos = int((x / self.w) * self.t)
                color = self.g[tpos]
            else:
                color = self.g[x]

            yield ((x, RGB(*map(int, color))),)

    def __iter__(self) -> PBar:
        return self

    @staticmethod
    def _true_colour(rgb: RGB) -> str:
        return f'\x1b[48;2;{rgb.r};{rgb.g};{rgb.b}m'

    def _print_bar_chars(self, s: str) -> None:
        _print_to_terminal(
            '\x1b7'  # save cursor position
            f'\x1b[{self.h};{self.curr}H'  # move to bottom line
            f'{s}'  # the "bar" characters
            '\x1b[0m'  # reset color
            '\x1b8'  # restore cursor position
        )

    def _initial_bar(self) -> None:
        "print initial bar in end color"
        self._print_bar_chars(
            f'\x1b[48;2;{self.c2.r};{self.c2.g};{self.c2.b}m' + ' ' * self.w + '\x1b[0m'
        )

    def __next__(self) -> None:
        s = [f'{self._true_colour(rgb)} ' for _, rgb in next(self._iter_pbar)]
        self._print_bar_chars(''.join(s))

        self.curr += len(s)
        if self.curr > self.w:
            raise StopIteration

    def update(self, n: int) -> None:
        "update the progress bar by n steps"
        self.progress = min(self.progress + n, self.t)
        # Calculate target terminal position based on logical progress
        target_pos = int((self.progress / (self.t)) * self.w)
        # Update bar to target position
        while self.curr < target_pos:
            try:
                next(self)
            except StopIteration:
                break

    def __enter__(self) -> PBar:
        _print_to_terminal(
            '\n'  # ensure space for scrollbar
            '\x1b7'  # save cursor position
            f'\x1b[0;{self.h - 1}r'  # set top & bottom regions (margins)
            '\x1b8'  # restore cursor position
            '\x1b[1A'  # move cursor up
        )
        self._initial_bar()
        return self

    def __exit__(self, _exc_type: type, _exc_val: BaseException, _exc_tb: type) -> None:
        # TODO: this is to ensure that the bar draws the full width. it should have done this already?
        while True:
            try:
                next(self)
            except StopIteration:
                break
        _print_to_terminal(
            f'\x1b[0;{self.h}r'  # reset margins
            f'\x1b[{self.h};0H'  # move to bottom line
            '\n'
        )
        self.curr = self.t


if __name__ == '__main__':
    with PBar(100, *PBar.randgrad()) as pbar:
        for i in range(100):
            time.sleep(0.01)
            print(f'-> {i}')
            pbar.update(1)
