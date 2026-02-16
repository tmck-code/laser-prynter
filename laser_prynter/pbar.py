#!/usr/bin/env python3

from __future__ import annotations

import os
import signal
import sys
import time
import types
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
    sys.stderr.write(s)
    sys.stderr.flush()


def _get_terminal_size() -> tuple[int, int]:
    'Get terminal size (width, height)'
    try:
        size = os.get_terminal_size(1)
    except OSError:
        try:
            size = os.get_terminal_size(2)
        except OSError:
            return (80, 24)
    return (size.columns, size.lines)


class RGB(NamedTuple):
    r: int
    g: int
    b: int


DEFAULT_C1, DEFAULT_C2 = RGB(240, 50, 0), RGB(10, 220, 0)


class PBar:
    def __init__(self, total: int, c1: RGB = DEFAULT_C1, c2: RGB = DEFAULT_C2):
        self.w, self.h = _get_terminal_size()
        self.c1, self.c2 = c1, c2

        self.t = total
        self.curr, self.progress = 0, 0

        self.start_time = time.time()

        if self.t > self.w:
            self.g = list(interp_xyz(self.c1, self.c2, self.t + 1))
        else:
            self.g = list(interp_xyz(self.c1, self.c2, self.w + 1))

        self._iter_pbar = iter(self._pbar())

        self.is_exiting = False
        signal.signal(signal.SIGINT, self.sigint_handler)
        signal.signal(signal.SIGWINCH, self.sigwinch_handler)

    def sigint_handler(self, _signum: int, _frame: types.FrameType | None) -> None:
        self.is_exiting = True
        self._reset_terminal()
        sys.exit(0)

    def sigwinch_handler(self, _signum: int, _frame: types.FrameType | None) -> None:
        self.w, self.h = _get_terminal_size()
        _print_to_terminal(
            '\x1b7'  # save cursor position
            f'\x1b[0;{self.h - 2}r'  # set top & bottom regions (margins) - reserve 2 lines
            f'\x1b[{self.h};1000H'  # move to bottom line
            '\r'
            '\x1b[2K'  # clear entire line
            f'\x1b[{self.h - 1};1000H'  # move to bottom line
            '\r'
            '\x1b[2K'  # clear entire line
            '\x1b8'  # restore cursor position
            '\x1b[2A'  # move cursor up 2 lines
        )

        curr, progress = self.curr, self.progress
        self.curr, self.progress = 0, 0
        if self.t > self.w:
            self.g = list(interp_xyz(self.c1, self.c2, self.t + 1))
        else:
            self.g = list(interp_xyz(self.c1, self.c2, self.w + 1))

        self._iter_pbar = iter(self._pbar())

        self._initial_bar()
        self.progress = progress
        for _ in range(curr):
            try:
                next(self)
            except StopIteration:
                break

        self._print_info()

    @staticmethod
    def randgrad() -> tuple[RGB, RGB]:
        rgb1 = RGB(randint(0, 255), randint(0, 255), randint(0, 255))
        rgb2 = RGB(
            (rgb1.r + (255 // 2)) % 255, (rgb1.g + (255 // 2)) % 255, (rgb1.b + (255 // 2)) % 255
        )
        return (rgb1, rgb2)

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

    @staticmethod
    def _format_time(seconds: float) -> str:
        'Format seconds into human-readable time string.'

        if seconds < 60:
            isec, fsec = divmod(seconds, 1)
            return f'{int(isec)}.{int(fsec * 100):02d}'
        elif seconds < 3600:
            isec, fsec = divmod(seconds, 60)
            return f'{int(isec)}:{fsec:05.2f}'
        else:
            hours, rem = divmod(seconds, 3600)
            mins, secs = divmod(rem, 60)
            return f'{int(hours)}:{int(mins)}:{secs:05.2f}'

    def _print_info(self) -> None:
        'Print progress info in the line above the bar.'

        elapsed = time.time() - self.start_time

        if self.progress == 0:
            eta_str = '??:??'
        else:
            eta_str = self._format_time((elapsed / self.progress) * (self.t - self.progress))

        pct = (self.progress / self.t) * 100
        item_info = f'[\x1b[1;32m{self.progress}\x1b[0m/{self.t}] \x1b[1;97m{pct:.1f}%\x1b[0m'
        time_info = f'\x1b[92m+{self._format_time(elapsed)}\x1b[0m \x1b[93m-{eta_str}\x1b[0m'

        # Clear the line and print info above the progress bar
        _print_to_terminal(
            '\x1b7'  # save cursor position
            f'\x1b[{self.h - 1};0H'  # move to line above bar
            '\x1b[2K'  # clear entire line
            f'{item_info} | {time_info}'
            '\x1b8'  # restore cursor position
        )

    def _print_bar_chars(self, s: str) -> None:
        _print_to_terminal(
            '\x1b7'  # save cursor position
            f'\x1b[{self.h};{self.curr}H'  # move to bottom line
            f'{s}'  # the 'bar' characters
            '\x1b[0m'  # reset color
            '\x1b8'  # restore cursor position
        )

    def _initial_bar(self) -> None:
        'print initial bar in end color'

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
        'update the progress bar by n steps'

        self.progress = min(self.progress + n, self.t)
        # Calculate target terminal position based on logical progress
        target_pos = int((self.progress / (self.t)) * self.w)
        # Update bar to target position
        while self.curr < target_pos:
            try:
                next(self)
            except StopIteration:
                break
        # Update progress info
        self._print_info()

    def __enter__(self) -> PBar:
        self.start_time = time.time()
        _print_to_terminal(
            '\x1b[?25l'  # hide cursor
            '\n\n'  # ensure space for info line and scrollbar
            '\x1b7'  # save cursor position
            f'\x1b[0;{self.h - 2}r'  # set top & bottom regions (margins) - reserve 2 lines
            '\x1b8'  # restore cursor position
            '\x1b[2A'  # move cursor up 2 lines
        )
        self._initial_bar()
        self._print_info()
        return self

    @staticmethod
    def _reset_terminal() -> None:
        w, h = _get_terminal_size()
        _print_to_terminal(
            '\x1b[?25h'  # show cursor
            f'\x1b[0;{h}r'  # reset margins
            f'\x1b[{h};1000H'  # move to bottom line
            '\n'
        )

    def __exit__(self, _exc_type: type, _exc_val: BaseException, _exc_tb: type) -> None:
        # TODO: this is to ensure that the bar draws the full width. it should have done this already?
        if self.is_exiting:
            return
        while True:
            try:
                next(self)
            except StopIteration:
                break
        self._reset_terminal()
        self.curr = self.t


if __name__ == '__main__':
    with PBar(200, *PBar.randgrad()) as pbar:
        for i in range(200):
            time.sleep(randint(int(0.01 * 100), int(0.2 * 100)) / 100)
            print(f'-> {i}', flush=True)
            pbar.update(1)
