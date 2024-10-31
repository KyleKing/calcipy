"""Markdown Machine."""

from __future__ import annotations

import json
import re
from pathlib import Path

from beartype.typing import Any, Callable, Dict, List, Optional
from corallium.file_helpers import read_lines
from corallium.log import LOGGER

from calcipy.file_search import find_project_files_by_suffix
from calcipy.invoke_helpers import get_project_path
from calcipy.markdown_table import format_table

HandlerLookupT = Dict[str, Callable[[str, Path], List[str]]]
"""Handler Lookup."""


class _ParseSkipError(RuntimeError):
    """Exception caught if the handler does not want to replace the text."""


class _ReplacementMachine:
    """State machine to replace content with user-specified handlers.

    Uses `{cts}` and `{cte}` to demarcate sections (short for 'calcipy-template-start' or '...-end')

    Previously built with `transitions`: https://pypi.org/project/transitions

    """

    def __init__(self) -> None:
        """Initialize the state machine."""
        self.state_other = 'non-template'
        self.state_template = 'calcipy-template-formatted'
        self.state = self.state_other

    def change_template(self) -> None:
        """Transition from state_other to state_template."""
        if self.state == self.state_other:
            self.state = self.state_template

    def change_end(self) -> None:
        """Transition from state_template to state_other."""
        if self.state == self.state_template:
            self.state = self.state_other

    def parse(
        self,
        lines: List[str],
        handler_lookup: HandlerLookupT,
        path_file: Path,
    ) -> List[str]:
        """Parse lines and insert new_text based on provided handler_lookup.

        Args:
            lines: list of string from source file
            handler_lookup: Lookup dictionary for template-formatted sections
            path_file: optional path to the file. Only useful for debugging

        Returns:
            List[str]: modified list of strings

        """
        updated_lines = []
        for line in lines:
            updated_lines.extend(self._parse_line(line, handler_lookup, path_file))
        return updated_lines

    def _parse_line(
        self,
        line: str,
        handler_lookup: HandlerLookupT,
        path_file: Path,
    ) -> List[str]:
        """Parse lines and insert new_text based on provided handler_lookup.

        Args:
            line: single line
            handler_lookup: lookup dictionary for template-formatted sections
            path_file: optional path to the file. Only useful for debugging

        Returns:
            List[str]: modified list of strings

        """
        lines: List[str] = []
        if '{cte}' in line and self.state == self.state_template:  # end
            self.change_end()
        elif '{cts}' in line:  # start
            self.change_template()
            matches = [text_match for text_match in handler_lookup if text_match in line]
            if len(matches) == 1:
                [match] = matches
                try:
                    lines.extend(handler_lookup[match](line, path_file))
                except _ParseSkipError:
                    lines.append(line)
                    self.change_end()
            else:
                LOGGER.debug('Could not parse. Skipping:', line=line)
                lines.append(line)
                self.change_end()
        elif self.state == self.state_other:
            lines.append(line)
        # else: discard the lines in the template-section
        return lines


_VAR_COMMENT_HTML = r'<!-- {cts} (?P<key>[^=]+)=(?P<value>[^;]+);'
"""Regex for extracting the variable from an HTML code comment."""


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


def _handle_source_file(line: str, path_file: Path) -> List[str]:
    """Replace commented sections in README with linked file contents.

    Args:
        line: first line of the section
        path_file: path to the file that contained the string

    Returns:
        List[str]: list of template-formatted text

    """
    key, path_rel = next(iter(_parse_var_comment(line).items()))
    path_base = get_project_path() if path_rel.startswith('/') else path_file.resolve().parent
    path_source = path_base / path_rel.lstrip('/')
    language = path_source.suffix.lstrip('.')
    lines_source = [f'```{language}', *read_lines(path_source), '```']
    if not path_source.is_file():
        LOGGER.warning('Could not locate source file', path_source=path_source)

    line_start = f'<!-- {{cts}} {key}={path_rel}; -->'
    line_end = '<!-- {cte} -->'
    return [line_start, *lines_source, line_end]


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
        }
        for path_file, file_obj in coverage_data['files'].items()
    ]
    records.append(
        {
            'File': '**Totals**',
            **{col: coverage_data['totals'][key] for col, key in col_key_map.items()},
        },
    )
    records = [{**_r, 'Coverage': f"{round(_r['Coverage'], 1)}%"} for _r in records]

    delimiters = ['-', *(['-:'] * len(col_key_map))]
    lines_table = format_table(headers=['File', *col_key_map], records=records, delimiters=delimiters).split('\n')
    short_date = coverage_data['meta']['timestamp'].split('T')[0]
    lines_table.extend(['', f'Generated on: {short_date}'])
    return lines_table


def _handle_coverage(line: str, _path_file: Path, path_coverage: Optional[Path] = None) -> List[str]:
    """Read the coverage.json file and write a Markdown table to the README file.

    Args:
        line: first line of the section
        _path_file: path to the file that contained the string (unused)
        path_coverage: full path to a coverage.json file or defaults to the project

    Returns:
        List[str]: list of template-formatted text

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


def write_template_formatted_md_sections(
    handler_lookup: Optional[HandlerLookupT] = None,
    paths_md: Optional[List[Path]] = None,
) -> None:
    """Populate the template-formatted sections of markdown files with user-configured logic."""
    _lookup: HandlerLookupT = handler_lookup or {
        'COVERAGE ': _handle_coverage,
        'SOURCE_FILE=': _handle_source_file,
    }

    paths = paths_md or find_project_files_by_suffix(get_project_path()).get('md') or []
    for path_md in paths:
        LOGGER.text_debug('Processing', path_md=path_md)
        if md_lines := _ReplacementMachine().parse(read_lines(path_md), _lookup, path_md):
            path_md.write_text('\n'.join(md_lines) + '\n', encoding='utf-8')
