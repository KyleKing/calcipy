"""Markdown utilities."""

from beartype.typing import Any, Dict, List


def _format_md_table(headers: List[str], records: List[Dict[str, Any]]) -> List[str]:
    """Format the input as a Github markdown table."""
    table = [[str(_r[col]) for col in headers] for _r in records]
    widths = [max(len(row[col_idx].strip()) for row in [headers, *table]) for col_idx in range(len(headers))]

    def pad(values: List[str]) -> List[str]:
        return [val.strip().ljust(widths[col_idx]) for col_idx, val in enumerate(values)]

    def join(row: List[str], spacer: str = ' ') -> str:
        return f'|{spacer}' + f'{spacer}|{spacer}'.join(row) + f'{spacer}|'

    return [
        join(pad(headers)),
        join(['-' * widths[col_idx] for col_idx in range(len(headers))], '-'),
        *[join(pad(row)) for row in table],
    ]
