"""Markdown Machine."""

import json
import re
from pathlib import Path

import pandas as pd
from beartype import beartype
from beartype.typing import Any, Callable, Dict, List, Optional
from corallium.file_helpers import read_lines
from corallium.log import logger
from transitions import Machine

from ..file_search import find_project_files_by_suffix
from ..invoke_helpers import get_project_path

HandlerLookupT = Dict[str, Callable[[str, Path], List[str]]]
"""Handler Lookup."""


class _ParseSkipError(RuntimeError):
    """Exception caught if the handler does not want to replace the text."""


class _ReplacementMachine(Machine):
    """State machine to replace content with user-specified handlers.

    Uses `{cts}` and `{cte}` to demarcate sections (short for calcipy_template start|end)

    """

    def __init__(self) -> None:
        """Initialize the state machine."""
        self.state_user = 'user'
        self.state_auto = 'autoformatted'
        transitions = [
            {
                'trigger': 'start_auto',
                'source': self.state_user,
                'dest': self.state_auto,
            }, {
                'trigger': 'end',
                'source': self.state_auto,
                'dest': self.state_user,
            },
        ]
        super().__init__(
            states=[self.state_user, self.state_auto],
            initial=self.state_user,
            transitions=transitions,
        )

    @beartype
    def parse(
        self, lines: List[str], handler_lookup: HandlerLookupT,
        path_file: Path,
    ) -> List[str]:
        """Parse lines and insert new_text based on provided handler_lookup.

        Args:
            lines: list of string from source file
            handler_lookup: Lookup dictionary for autoformatted sections
            path_file: optional path to the file. Only useful for debugging

        Returns:
            List[str]: modified list of strings

        """
        updated_lines = []
        for line in lines:
            updated_lines.extend(self._parse_line(line, handler_lookup, path_file))
        return updated_lines

    @beartype
    def _parse_line(
        self, line: str, handler_lookup: HandlerLookupT, path_file: Path,
    ) -> List[str]:
        """Parse lines and insert new_text based on provided handler_lookup.

        Args:
            line: single line
            handler_lookup: Lookup dictionary for autoformatted sections
            path_file: optional path to the file. Only useful for debugging

        Returns:
            List[str]: modified list of strings

        """
        lines: List[str] = []
        if '{cte}' in line and self.state == self.state_auto:  # end
            self.end()
        elif '{cts}' in line:  # start
            self.start_auto()
            matches = [text_match for text_match in handler_lookup if text_match in line]
            if len(matches) == 1:
                try:
                    lines.extend(handler_lookup[matches[0]](line, path_file))
                except _ParseSkipError:
                    lines.append(line)
                    self.end()
            else:
                logger.error('Could not parse', line=line)
                lines.append(line)
                self.end()
        elif self.state == self.state_user:
            lines.append(line)
        # else: discard the lines in the auto-section
        return lines


_VAR_COMMENT_HTML = r'<!-- {cts} (?P<key>[^=]+)=(?P<value>[^;]+);'
"""Regex for extracting the variable from an HTML code comment."""


@beartype
def _parse_var_comment(line: str, matcher: str = _VAR_COMMENT_HTML) -> Dict[str, str]:
    """Parse the variable from a matching comment.

    Args:
        line: string from source file
        matcher: string regex pattern to match. Default is `_RE_VAR_COMMENT_HTML`

    Returns:
        Dict[str, str]: single key and value pair based on the parsed comment

    """
    if match := re.compile(matcher).match(line.strip()):
        matches = match.groupdict()
        return {matches['key']: matches['value']}
    return {}


@beartype
def _handle_source_file(line: str, path_file: Path) -> List[str]:
    """Replace commented sections in README with linked file contents.

    Args:
        line: first line of the section
        path_file: path to the file that contained the string

    Returns:
        List[str]: list of auto-formatted text

    """
    key, path_rel = [*_parse_var_comment(line).items()][0]
    path_base = get_project_path() if path_rel.startswith('/') else path_file.resolve().parent
    path_source = path_base / path_rel.lstrip('/')
    language = path_source.suffix.lstrip('.')
    lines_source = [f'```{language}', *read_lines(path_source), '```']
    if not path_source.is_file():
        logger.warning('Could not locate source file', path_source=path_source)

    line_start = f'<!-- {{cts}} {key}={path_rel}; -->'
    line_end = '<!-- {cte} -->'
    return [line_start, *lines_source, line_end]


@beartype
def _format_cov_table(coverage_data: Dict[str, Any]) -> List[str]:
    """Format code coverage data table as markdown.

    Args:
        coverage_data: dictionary created by `python -m coverage json`

    Returns:
        List[str]: list of string lines to insert

    """
    col_key_map = {
        'Statements': 'num_statements',
        'Missing': 'missing_lines',
        'Excluded': 'excluded_lines',
        'Coverage': 'percent_covered',
    }
    records = [
        {
            'File': f'`{Path(path_file).as_posix()}`',
            **{col: file_obj['summary'][key] for col, key in col_key_map.items()},
        } for path_file, file_obj in coverage_data['files'].items()
    ]
    records.append({
        'File': '**Totals**',
        **{col: coverage_data['totals'][key] for col, key in col_key_map.items()},
    })
    # Format table for Github Markdown
    df_cov = pd.DataFrame(records)
    df_cov['Coverage'] = df_cov['Coverage'].round(1).astype(str) + '%'
    lines_table = str(df_cov.to_markdown(index=False, tablefmt='github')).split('\n')
    short_date = coverage_data['meta']['timestamp'].split('T')[0]
    lines_table.extend(['', f'Generated on: {short_date}'])
    return lines_table


@beartype
def _handle_coverage(line: str, _path_file: Path, path_coverage: Optional[Path] = None) -> List[str]:
    """Read the coverage.json file and write a Markdown table to the README file.

    Args:
        line: first line of the section
        path_file: path to the file that contained the string

    Returns:
        List[str]: list of auto-formatted text

    Raises:
        _ParseSkipError: if the "coverage.json" file is not available

    """
    path_coverage = path_coverage or get_project_path() / 'coverage.json'
    if not path_coverage.is_file():
        msg = f'Could not locate: {path_coverage}'
        raise _ParseSkipError(msg)
    coverage_data = json.loads(path_coverage.read_text())
    lines_cov = _format_cov_table(coverage_data)
    line_end = '<!-- {cte} -->'
    return [line, *lines_cov, line_end]


@beartype
def write_autoformatted_md_sections(
    handler_lookup: Optional[HandlerLookupT] = None,
    paths_md: Optional[List[Path]] = None,
) -> None:
    """Populate the auto-formatted sections of markdown files with user-configured logic."""
    _lookup: HandlerLookupT = handler_lookup or {
        'COVERAGE ': _handle_coverage,
        'SOURCE_FILE=': _handle_source_file,
    }

    paths = paths_md or find_project_files_by_suffix(get_project_path()).get('md') or []
    for path_md in paths:
        logger.text_debug('Processing', path_md=path_md)
        if md_lines := _ReplacementMachine().parse(read_lines(path_md), _lookup, path_md):
            path_md.write_text('\n'.join(md_lines) + '\n', encoding='utf-8')
