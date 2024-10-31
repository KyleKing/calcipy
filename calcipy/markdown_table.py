"""Markdown table formatting."""

from __future__ import annotations

from collections.abc import Iterable
from itertools import starmap
from typing import Any


def format_table(
    headers: list[str],
    records: list[dict[str, Any]],
    delimiters: list[str] | None = None,
) -> str:
    """Returns a formatted Github Markdown table.

    Args:
        headers: ordered keys to use as column title
        records: list of key:row-value dictionaries
        delimiters: optional list to allow for alignment

    """
    table = [[str(_r[col]) for col in headers] for _r in records]
    widths = [max(len(row[col_idx].strip()) for row in [headers, *table]) for col_idx in range(len(headers))]

    def pad(values: list[str]) -> list[str]:
        return [val.strip().ljust(widths[col_idx]) for col_idx, val in enumerate(values)]

    def join(row: Iterable[str], spacer: str = ' ') -> str:
        return f'|{spacer}' + f'{spacer}|{spacer}'.join(row) + f'{spacer}|'

    def expand_delimiters(delim: str, width: int) -> str:
        expanded = '-' * (width + 2)
        if delim.startswith(':'):
            expanded = ':' + expanded[1:]
        if delim.endswith(':'):
            expanded = expanded[:-1] + ':'
        return expanded

    if delimiters:
        errors = []
        if len(delimiters) != len(headers):
            errors.append(f'Incorrect number of delimiters provided ({len(delimiters)}). Expected: ({len(headers)})')
        allowed_delimiters = {'-', ':-', '-:', ':-:'}
        if not all(delim in allowed_delimiters for delim in delimiters):
            errors.append(f'Delimiters must one of ({len(allowed_delimiters)}). Received: ({len(delimiters)})')
        if errors:
            raise ValueError(' and '.join(errors))

    lines = [
        join(pad(headers)),
        join(starmap(expand_delimiters, zip(delimiters or ['-'] * len(headers), widths)), ''),
        *[join(pad(row)) for row in table],
    ]
    return '\n'.join(lines)
