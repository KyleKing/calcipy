"""Collect code tags and output for review in a single location."""

import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from subprocess import CalledProcessError  # nosec

import pandas as pd
import pendulum
from attrs import field, frozen
from attrs_strict import type_validator
from beartype import beartype
from beartype.typing import Dict, List, Optional, Pattern, Sequence, Tuple
from loguru import logger

from .file_helpers import read_lines
from .log_helpers import log_fun
from .proc_helpers import run_cmd

SKIP_PHRASE = 'calcipy:skip_tags'
"""String that indicates the file should be excluded from the tag search."""

COMMON_CODE_TAGS = ['FIXME', 'TODO', 'PLANNED', 'HACK', 'REVIEW', 'TBD', 'DEBUG']  # noqa: T100,T101,T103
"""Most common code tags. FYI and NOTE are excluded to not be tracked in the Code Summary."""

CODE_TAG_RE = r'((^|\s|\(|"|\')(?P<tag>{tag})(:| -)([^\r\n]))(?P<text>.+)'
"""Default code tag regex with `tag` and `text` matching groups.

Requires formatting with list of tags: `CODE_TAG_RE.format(tag='|'.join(tag_list))`

Commonly, the `tag_list` could be `COMMON_CODE_TAGS`

"""


@frozen
class _CodeTag:
    """Code Tag (FIXME,TODO,etc) with contextual information."""  # noqa: T100,T101

    lineno: int = field(validator=type_validator())
    tag: str = field(validator=type_validator())
    text: str = field(validator=type_validator())


@frozen
class _Tags:
    """Collection of code tags with additional contextual information."""

    path_source: Path = field(validator=type_validator())
    code_tags: List[_CodeTag] = field(validator=type_validator())


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
            if len(line) <= 400:  # FYI: Suppress long lines
                group = match.groupdict()
                comments.append(_CodeTag(lineno + 1, tag=group['tag'], text=group['text']))
            else:
                logger.debug('Skipping long line {lineno}: `{line}`', lineno=lineno, line=line[:200])
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
            logger.debug('Could not parse: {path_source}', path_source=path_source, err=err)

        comments = _search_lines(lines, regex_compiled)
        if comments:
            matches.append(_Tags(path_source, comments))

    return matches


@lru_cache(maxsize=128)
@beartype
def _git_info(cwd: Path) -> Tuple[Path, str]:
    """Collect information about the local git repository.

    Based on snippets from: https://gist.github.com/abackstrom/4034721#gistcomment-3982270
    and: https://github.com/rscherf/GitLink/blob/e2e7c412630246efc86de4fe71192f15bf11209e/GitLink.py

    Args:
        cwd: Path to the current working directory (typically file_path.parent)

    Returns:
        Tuple[Path, str]: (git_dir, repo_url)

    """
    git_dir = Path(run_cmd('git rev-parse --show-toplevel', cwd=str(cwd)))
    clone_uri = run_cmd('git remote get-url origin', cwd=str(cwd))
    # Could be ssh or http (with or without .git)
    # git@github.com:KyleKing/calcipy.git
    # https://github.com/KyleKing/calcipy.git
    sub_url = re.findall(r'^.+github.com[:/]([^.]+)(?:\.git)?$', clone_uri)[0]
    repo_url = f'https://github.com/{sub_url}'
    return (git_dir, repo_url)


@beartype
def _format_record(base_dir: Path, file_path: Path, comment: _CodeTag) -> Dict[str, str]:
    """Format each table row for the code tag summary file. Include git permalink.

    Args:
        base_dir: base path of the project if git directory is not known
        file_path: path to the file of interest
        comment: _CodeTag information for the matched tag

    Returns:
        Dict[str, str]: formatted dictionary with file info

    """
    cwd = file_path.parent
    git_dir, repo_url = _git_info(cwd=cwd)
    blame = None
    try:
        blame = run_cmd(f'git blame {file_path} -L {comment.lineno},{comment.lineno} --porcelain', cwd=cwd)
    except CalledProcessError as exc:
        if exc.returncode != 128:
            raise
        logger.debug('Skipping blame of: {exc}', file_path=file_path, exc=exc)

    # Set fallback values if git logic doesn't work
    rel_path = file_path.relative_to(base_dir)
    source_file = f'{rel_path.as_posix()}:{comment.lineno}'
    ts = 'N/A'
    if blame:
        # Note: line number may be different in older blame (and relative path)
        revision, old_line_number = blame.split('\n')[0].split(' ')[:2]
        # If the change has not yet been committed, use the branch name as best guess
        if all(_c == '0' for _c in revision):
            revision = run_cmd('git branch --show-current', cwd=cwd)
        # Format a nice timestamp of the last edit to the line
        blame_dict = {
            line.split(' ')[0]: ' '.join(line.split(' ')[1:])
            for line in blame.split('\n')
        }
        # Handle uncommitted files that only have author-time and author-tz
        user = 'committer' if 'committer-tz' in blame_dict else 'author'
        dt = pendulum.from_timestamp(int(blame_dict[f'{user}-time']))
        tz = blame_dict[f'{user}-tz'][:3] + ':' + blame_dict[f'{user}-tz'][-2:]
        ts = pendulum.parse(dt.isoformat()[:-6] + tz).format('YYYY-MM-DD')
        # Filename may not be present if uncommitted. Use local path as fallback
        remote_file_path = blame_dict.get('filename', rel_path.as_posix())
        # PLANNED: Consider making "blame" configurable
        git_url = f'{repo_url}/blame/{revision}/{remote_file_path}#L{old_line_number}'
        source_file = f'[{source_file}]({git_url})'

    return {
        'Type': f'{comment.tag:>7}',
        'Comment': comment.text,
        'Last Edit': ts,
        'Source File': source_file,
    }


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
    records = []
    counter: Dict[str, int] = defaultdict(lambda: 0)
    for comments in sorted(code_tags, key=lambda tc: tc.path_source, reverse=False):
        for comment in comments.code_tags:
            if comment.tag in tag_order:
                records.append(_format_record(base_dir, comments.path_source, comment))
                counter[comment.tag] += 1
    if records:
        df_tags = pd.DataFrame(records)
        output += df_tags.to_markdown(index=False, tablefmt='github')
    logger.debug('counter={counter}', counter=counter)

    sorted_counter = {tag: counter[tag] for tag in tag_order if tag in counter}
    logger.debug('sorted_counter={sorted_counter}', sorted_counter=sorted_counter)
    formatted_summary = ', '.join(f'{tag} ({count})' for tag, count in sorted_counter.items())
    if formatted_summary:
        output += f'\n\nFound code tags for {formatted_summary}\n'
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
    elif path_tag_summary.is_file():
        path_tag_summary.unlink()
