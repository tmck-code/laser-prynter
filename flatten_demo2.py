#!/usr/bin/env python3

import json
from itertools import chain
from typing import Any, Generator, Iterator, Tuple

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexer import Lexer
from pygments.style import Style
from pygments.token import Token
from tabulate import tabulate


class ColumnStyle(Style):
    # Simply map tokens to property strings. No Color import required.
    styles = {
        Token.Column.Zero: 'ansired bold',
        Token.Column.One: 'ansigreen',
        Token.Column.Two: 'ansiblue',
        Token.Column.Three: 'ansiyellow',
        Token.Column.Four: 'ansimagenta',
        Token.Column.Five: 'ansicyan',
        Token.Column.Six: 'ansibrightred',
        Token.Column.Seven: 'ansibrightgreen',
        Token.Column.Eight: 'ansibrightblue',
        Token.Column.Nine: 'ansibrightyellow',
        Token.Column.Ten: 'ansibrightmagenta',
    }


class ColumnTabulateLexer(Lexer):
    COL_TOKENS = [
        Token.Column.Zero,
        Token.Column.One,
        Token.Column.Two,
        Token.Column.Three,
        Token.Column.Four,
        Token.Column.Five,
        Token.Column.Six,
        Token.Column.Seven,
        Token.Column.Eight,
        Token.Column.Nine,
        Token.Column.Ten,
    ]

    def get_tokens_unprocessed(self, text: str) -> Generator[Tuple[int, Token, str], None, None]:
        pos = 0
        for line in text.splitlines(keepends=True):
            parts = line.split('\t')
            nParts = len(parts)

            for col_idx, part in enumerate(parts):
                if not part:
                    yield pos, Token.Text, ''
                    pos += len(part)
                    continue

                tok_type = self.COL_TOKENS[col_idx % len(self.COL_TOKENS)]
                if col_idx < nParts - 1:
                    part += '\t'
                yield pos, tok_type, part
                pos += len(part)


def flatten(d: dict, prefix: str = "") -> dict:
    def pairs(d: dict[str, Any], prefix: str) -> Iterator[Tuple[str, Any]]:
        return chain.from_iterable(
            pairs(v, f'{prefix}{k}.') if isinstance(v, dict) else [(f'{prefix}{k}', v)]
            for k, v in d.items()
        )

    return dict(pairs(d, prefix))


lines = []
with open('test_logs.txt') as istream:
    for line in istream:
        lines.append(list(flatten(json.loads(line.strip())).values()))

table_data = tabulate(lines, tablefmt='tsv')
print(table_data)

result = highlight(table_data, ColumnTabulateLexer(), Terminal256Formatter(style=ColumnStyle))
print(result)
