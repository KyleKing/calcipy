"""Collect code tags and output for review in a single location."""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Pattern, Sequence

import attr
from attrs_strict import type_validator
from beartype import beartype
from loguru import logger

from .file_helpers import read_lines
from .log_helpers import log_fun

SKIP_PHRASE = 'calcipy:skip_tags'
"""String that indicates the file should be excluded from the tag search."""

COMMON_CODE_TAGS = ['FIXME', 'TODO', 'PLANNED', 'HACK', 'REVIEW', 'TBD', 'DEBUG']  # noqa: T100,T101,T103
"""Most common code tags. FYI and NOTE are excluded to not be tracked in the Code Summary."""

CODE_TAG_RE = r'((\s|\()(?P<tag>{tag})(:| -)([^\r\n]))(?P<text>.+)'
"""Default code tag regex with `tag` and `text` matching groups.

Requires formatting with list of tags: `CODE_TAG_RE.format(tag='|'.join(tag_list))`

Commonly, the `tag_list` could be `COMMON_CODE_TAGS`

"""


@attr.s(auto_attribs=True)
class _CodeTag:  # noqa: H601
    """Code Tag (FIXME,TODO,etc) with contextual information."""  # noqa: T100,T101

    lineno: int = attr.ib(validator=type_validator())
    tag: str = attr.ib(validator=type_validator())
    text: str = attr.ib(validator=type_validator())


@attr.s(auto_attribs=True)
class _Tags:  # noqa: H601
    """Collection of code tags with additional contextual information."""

    path_source: Path = attr.ib(validator=type_validator())
    code_tags: List[_CodeTag] = attr.ib(validator=type_validator())


@beartype
def _search_lines(
    lines: List[str], regex_compiled: Pattern[str],
    skip_phrase: str = 'calcipy:skip_tags',
) -> List[_CodeTag]:
    """Search lines of text for matches to the compiled regular expression.

    Args:
        lines: lines of text as list
        regex_compiled: compiled regular expression. Expected to have matching groups `(tag, text)`
        skip_phrase: skip file if string is found in final two lines. Default is `SKIP_PHRASE`

    Returns:
        List[_CodeTag]: list of all code tags found in lines

    """
    if skip_phrase in '\n'.join(lines[-2:]):
        return []

    comments = []
    for lineno, line in enumerate(lines):
        match = regex_compiled.search(line)
        if match:
            group = match.groupdict()
            comments.append(_CodeTag(lineno + 1, tag=group['tag'], text=group['text']))
    return comments


@beartype
def _search_files(paths_source: Sequence[Path], regex_compiled: Pattern[str]) -> List[_Tags]:
    """Collect matches from multiple files.

    Args:
        paths_source: list of source files to parse
        regex_compiled: compiled regular expression. Expected to have matching groups `(tag, text)`

    Returns:
        List[_Tags]: list of all code tags found in files

    """
    matches = []
    for path_source in paths_source:
        lines = []
        try:
            lines = read_lines(path_source)
        except UnicodeDecodeError as err:
            logger.debug(f'Could not parse: {path_source}', err=err)

        comments = _search_lines(lines, regex_compiled)
        if comments:
            matches.append(_Tags(path_source, comments))

    return matches


@beartype
def _format_report(
    base_dir: Path, code_tags: List[_Tags], tag_order: List[str],
) -> str:  # noqa: CCR001
    """Pretty-format the code tags by file and line number.

    Args:
        base_dir: base directory relative to the searched files
        code_tags: list of all code tags found in files
        tag_order: subset of all tags to include in the report and specified order

    Returns:
        str: pretty-formatted text

    """
    output = ''
    counter: Dict[str, int] = defaultdict(lambda: 0)
    for comments in sorted(code_tags, key=lambda tc: tc.path_source, reverse=False):
        output += f'- {comments.path_source.relative_to(base_dir).as_posix()}\n'
        for comment in comments.code_tags:
            if comment.tag in tag_order:
                output += f'    - line {comment.lineno:>3} {comment.tag:>7}: {comment.text}\n'
                counter[comment.tag] += 1
        output += '\n'
    logger.debug('counter={counter}', counter=counter)

    sorted_counter = {tag: counter[tag] for tag in tag_order if tag in counter}
    logger.debug('sorted_counter={sorted_counter}', sorted_counter=sorted_counter)
    formatted_summary = ', '.join(f'{tag} ({count})' for tag, count in sorted_counter.items())
    if formatted_summary:
        output += f'Found code tags for {formatted_summary}\n'
    return output


@log_fun
@beartype
def write_code_tag_file(
    path_tag_summary: Path, paths_source: List[Path], base_dir: Path,
    regex_compiled: Optional[Pattern[str]] = None, tag_order: Optional[List[str]] = None,
    header: str = '# Task Summary',
) -> None:  # noqa: CCR001
    """Create the code tag summary file.

    Args:
        path_tag_summary: Path to the output file
        paths_source: list of source files to parse
        base_dir: base directory relative to the searched files
        regex_compiled: compiled regular expression. Expected to have matching groups `(tag, text)`.
            Default is CODE_TAG_RE with tags from tag_order
        tag_order: subset of all tags to include in the report and specified order. Default is COMMON_CODE_TAGS
        header: optional header text. Default is '# Task Summary'

    """
    tag_order = tag_order or COMMON_CODE_TAGS
    regex_compiled = regex_compiled or re.compile(CODE_TAG_RE.format(tag='|'.join(tag_order)))

    matches = _search_files(paths_source, regex_compiled)
    report = _format_report(base_dir, matches, tag_order=tag_order).strip()

    if report:
        path_tag_summary.write_text(f'{header}\n\n{report}\n\n<!-- {SKIP_PHRASE} -->\n')
    else:
        path_tag_summary.unlink(missing_ok=True)
