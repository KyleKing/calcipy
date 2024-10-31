"""Markdown table formatting."""

from __future__ import annotations

from typing import Any


def format_table(headers: list[str], records: list[dict[str, Any]]) -> str:
    """Returns a formatted Github Markdown table."""
    table = [[str(_r[col]) for col in headers] for _r in records]
    widths = [max(len(row[col_idx].strip()) for row in [headers, *table]) for col_idx in range(len(headers))]

    def pad(values: list[str]) -> list[str]:
        return [val.strip().ljust(widths[col_idx]) for col_idx, val in enumerate(values)]

    def join(row: list[str], spacer: str = ' ') -> str:
        return f'|{spacer}' + f'{spacer}|{spacer}'.join(row) + f'{spacer}|'

    lines = [
        join(pad(headers)),
        join(['-' * widths[col_idx] for col_idx in range(len(headers))], '-'),
        *[join(pad(row)) for row in table],
    ]
    return '\n'.join(lines)
