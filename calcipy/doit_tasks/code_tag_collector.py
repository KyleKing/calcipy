"""Collect code tags and output for review in a single location."""

from collections import defaultdict
from pathlib import Path
from typing import List, Pattern, Sequence

import attr
from loguru import logger

from ..log_helpers import log_fun
from .base import debug_task, read_lines
from .doit_globals import DIG, DoitTask


@attr.s(auto_attribs=True)
class _CodeTag:  # noqa: H601
    """Code Tag (FIXME,TODO,etc) with contextual information."""  # noqa: T100,T101

    lineno: int
    tag: str
    text: str


@attr.s(auto_attribs=True)
class _Tags:  # noqa: H601
    """Collection of code tags with additional contextual information."""

    path_source: Path
    code_tags: List[_CodeTag]


def _search_lines(lines: Sequence[str], regex_compiled: Pattern[str]) -> List[_CodeTag]:
    """Search lines of text for matches to the compiled regular expression.

    Args:
        lines: lines of text as list
        regex_compiled: compiled regular expression. Expected to have matching groups `(tag, text)`

    Returns:
        List[_CodeTag]: list of all code tags found in lines

    """
    comments = []
    for lineno, line in enumerate(lines):
        match = regex_compiled.search(line)
        # FIXME: Replace with tail-like check for the last line of the file for any calcipy rules - use seek
        if lineno <= 3 and ':skip_tags:' in line:
            break
        if match:
            mg = match.groupdict()
            comments.append(_CodeTag(lineno + 1, tag=mg['tag'], text=mg['text']))
    return comments


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
            logger.warning(f'Could not parse: {path_source}', err=err)

        comments = _search_lines(lines, regex_compiled)
        if comments:
            matches.append(_Tags(path_source, comments))

    return matches


def _format_report(base_dir: Path, code_tags: List[_Tags]) -> str:  # noqa: CCR001
    """Pretty-format the code tags by file and line number.

    Args:
        base_dir: base directory relative to the searched files
        code_tags: list of all code tags found in files

    Returns:
        str: pretty-formatted text

    """
    output = ''
    counter = defaultdict(lambda: 0)
    for comments in sorted(code_tags, key=lambda tc: tc.path_source, reverse=False):
        output += f'- {comments.path_source.relative_to(base_dir).as_posix()}\n'
        for comment in comments.code_tags:
            output += f'    - line {comment.lineno:>3} {comment.tag:>7}: {comment.text}\n'
            counter[comment.tag] += 1
        output += '\n'
    logger.debug('counter={counter}', counter=counter)

    sorted_counter = {tag: counter[tag] for tag in DIG.ct.tags if tag in counter}
    logger.debug('sorted_counter={sorted_counter}', sorted_counter=sorted_counter)
    formatted_summary = ', '.join(f'{tag} ({count})' for tag, count in sorted_counter.items())
    if formatted_summary:
        output += f'Found code tags for {formatted_summary}\n'
    return output


# TODO: Ensure that code_tag_summary.md is ignored. Remove one-off workarounds (Should be fixed with :skip_tags:)
# FIXME: Standardize lookup to ignore some keyphrase in header and gitignore rules
def _find_files() -> List[Path]:
    """Find files within the project directory that should be parsed for tags. Ignores .venv, output, etc.

    Returns:
        List[Path]: list of file paths to parse

    """
    # TODO: Move all of these configuration items into DIG
    dot_directories = [pth for pth in DIG.meta.path_project.glob('.*') if pth.is_dir()]
    ignored_sub_dirs = [DIG.test.path_out.parent.name] + dot_directories
    ignored_filenames = []
    supported_suffixes = ['.py']

    paths_source = DIG.doc.paths_md
    # NOTE: THE TOP LEVEL path_project MUST USE GLOB (NOT RGLOB!)
    for suffix in supported_suffixes:
        paths = [*DIG.meta.path_project.glob(f'*{suffix}')]
        paths_source.extend([pth for pth in paths if pth.name not in ignored_filenames])

    paths_sub_dir = [pth for pth in DIG.meta.path_project.glob('*') if pth.is_dir() and pth not in ignored_sub_dirs]
    for path_dir in paths_sub_dir:
        for suffix in supported_suffixes:
            paths_source.extend([pth for pth in path_dir.rglob(f'*{suffix}') if pth.name not in ignored_filenames])
    logger.info(
        f'Found {len(paths_source)} files in {len(paths_sub_dir)} dir', paths_source=paths_source,
        paths_sub_dir=paths_sub_dir,
    )
    return paths_source


@log_fun
def _write_code_tag_file(path_tag_summary: Path) -> None:
    """Create the code tag summary file.

    Args:
        path_tag_summary: Path to the output file

    """
    header = f'# Task Summary\n\n<!-- :skip_tags: -->\n\nAuto-Generated by {DIG.meta.pkg_name}'
    regex_compiled = DIG.ct.compile_issue_regex()
    matches = _search_files(_find_files(), regex_compiled)
    report = _format_report(DIG.meta.path_project, matches).strip()
    if report:
        path_tag_summary.write_text(f'{header}\n\n{report}\n')
    elif path_tag_summary.is_file():
        path_tag_summary.unlink()


def task_collect_code_tags() -> DoitTask:
    """Create a summary file with all of the found code tags.

    Returns:
        DoitTask: doit task

    """
    path_tag_summary = DIG.meta.path_project / DIG.ct.path_code_tag_summary
    return debug_task([(_write_code_tag_file, (path_tag_summary,))])
