"""Collect code tags and output for review in a single location."""

import re
from collections import defaultdict
from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from subprocess import CalledProcessError  # nosec

import arrow
import pandas as pd
from beartype import beartype
from beartype.typing import Dict, List, Pattern, Sequence, Tuple
from corallium.file_helpers import read_lines
from corallium.log import logger
from corallium.shell import capture_shell
from pydantic import BaseModel, ConfigDict

SKIP_PHRASE = 'calcipy_skip_tags'
"""String that indicates the file should be excluded from the tag search."""

COMMON_CODE_TAGS = ['FIXME', 'TODO', 'PLANNED', 'HACK', 'REVIEW', 'TBD', 'DEBUG']
"""Most common code tags.

FYI and NOTE are excluded to not be tracked in the Code Summary.

"""

CODE_TAG_RE = r'((^|\s|\(|"|\')(?P<tag>{tag})(:| -)([^\r\n]))(?P<text>.+)'
"""Default code tag regex with `tag` and `text` matching groups.

Requires formatting with list of tags: `CODE_TAG_RE.format(tag='|'.join(tag_list))`

Commonly, the `tag_list` could be `COMMON_CODE_TAGS`

"""


class _CodeTag(BaseModel):
    """Code Tag (FIXME,TODO,etc) with contextual information."""

    lineno: int
    tag: str
    text: str  # noqa: CCE001
    model_config = ConfigDict(frozen=True)


class _Tags(BaseModel):
    """Collection of code tags with additional contextual information."""

    path_source: Path
    code_tags: List[_CodeTag]  # noqa: CCE001
    model_config = ConfigDict(frozen=True)


@beartype
def _search_lines(
    lines: List[str], regex_compiled: Pattern[str],
    skip_phrase: str = 'calcipy_skip_tags',
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

    max_len = 400
    comments = []
    for lineno, line in enumerate(lines):
        if match := regex_compiled.search(line):
            if len(line) <= max_len:  # FYI: Suppress long lines
                group = match.groupdict()
                comments.append(_CodeTag(lineno=lineno + 1, tag=group['tag'], text=group['text']))
            else:
                logger.text_debug('Skipping long line', lineno=lineno, line=line[:200])
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
        except UnicodeDecodeError as err:  # noqa: PERF203
            logger.text_debug('Could not parse', path_source=path_source, err=err)

        if comments := _search_lines(lines, regex_compiled):
            matches.append(_Tags(path_source=path_source, code_tags=comments))

    return matches


_GITHUB_ORIGIN = r'^.+github.com[:/](?P<owner>[^/]+)/(?P<repository>[^.]+)(?:\.git)?$'
"""Match owner and repository from a GitHub git origin URI."""


@beartype
def github_blame_url(clone_uri: str) -> str:
    """Format the blame URL.

    Args:
        clone_uri: git remote URI

    Returns:
       str: `repo_url`

    """
    # Could be ssh or http (with or without .git)
    # > git@github.com:KyleKing/calcipy.git
    # > https://github.com/KyleKing/calcipy.git
    if matches := re.compile(_GITHUB_ORIGIN).match(clone_uri):
        github_url = 'https://github.com/'
        return f"{github_url}{matches['owner']}/{matches['repository']}"
    return ''


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
    git_dir = Path(capture_shell('git rev-parse --show-toplevel', cwd=cwd))
    clone_uri = ''
    with suppress(CalledProcessError):
        clone_uri = capture_shell('git remote get-url origin', cwd=cwd)
    return git_dir, github_blame_url(clone_uri)


class _CollectorRow(BaseModel):
    """Each row of the Code Tag table."""

    tag_name: str
    comment: str
    last_edit: str
    source_file: str

    @classmethod
    @beartype
    def from_code_tag(cls, code_tag: _CodeTag, last_edit: str, source_file: str) -> '_CollectorRow':
        return cls(
            tag_name=f'{code_tag.tag:>7}',
            comment=code_tag.text,
            last_edit=last_edit,
            source_file=source_file,
        )


@beartype
def _format_from_blame(
    *, collector_row: _CollectorRow, blame: str, repo_url: str, cwd: Path, rel_path: Path,
) -> _CollectorRow:
    """Parse the git blame for useful timestamps and author when available."""
    # Note: line number may be different in older blame (and relative path)
    revision, old_line_number = blame.split('\n')[0].split(' ')[:2]
    # If the change has not yet been committed, use the branch name as best guess
    if all(_c == '0' for _c in revision):
        revision = capture_shell('git branch --show-current', cwd=cwd)
    # Format a nice timestamp of the last edit to the line
    blame_dict = {
        line.split(' ')[0]: ' '.join(line.split(' ')[1:])
        for line in blame.split('\n')
    }

    # Handle uncommitted files that only have author-time and author-tz
    user = 'committer' if 'committer-tz' in blame_dict else 'author'
    dt = arrow.get(int(blame_dict[f'{user}-time']))
    tz = blame_dict[f'{user}-tz'][:3] + ':' + blame_dict[f'{user}-tz'][-2:]
    collector_row.last_edit = arrow.get(dt.isoformat()[:-6] + tz).format('YYYY-MM-DD')

    if repo_url:
        # Filename may not be present if uncommitted. Use local path as fallback
        remote_file_path = blame_dict.get('filename', rel_path.as_posix())
        # Assumes Github format
        git_url = f'{repo_url}/blame/{revision}/{remote_file_path}#L{old_line_number}'
        collector_row.source_file = f'[{collector_row.source_file}]({git_url})'

    return collector_row


@beartype
def _format_record(base_dir: Path, file_path: Path, comment: _CodeTag) -> _CollectorRow:
    """Format each table row for the code tag summary file. Include git permalink.

    Args:
        base_dir: base path of the project if git directory is not known
        file_path: path to the file of interest
        comment: _CodeTag information for the matched tag

    Returns:
        Dict[str, str]: formatted dictionary with file info

    """
    cwd = file_path.parent
    _git_dir, repo_url = _git_info(cwd=cwd)

    # Set fallback values if git logic doesn't work
    rel_path = file_path.relative_to(base_dir)
    collector_row = _CollectorRow.from_code_tag(
        code_tag=comment,
        last_edit='N/A',
        source_file=f'{rel_path.as_posix()}:{comment.lineno}',
    )

    try:
        blame = capture_shell(f'git blame {file_path} -L {comment.lineno},{comment.lineno} --porcelain', cwd=cwd)
        collector_row = _format_from_blame(
            collector_row=collector_row, blame=blame, repo_url=repo_url, cwd=cwd, rel_path=rel_path,
        )
    except CalledProcessError as exc:
        handled_errors = (128,)
        if exc.returncode not in handled_errors:
            raise
        logger.text_debug('Skipping blame', file_path=file_path, exc=exc)

    return collector_row


@beartype
def _format_report(  # noqa: CAC001
    base_dir: Path, code_tags: List[_Tags], tag_order: List[str],
) -> str:
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
                collector_row = _format_record(base_dir, comments.path_source, comment)
                records.append({
                    'Type': collector_row.tag_name,
                    'Comment': collector_row.comment,
                    'Last Edit': collector_row.last_edit,
                    'Source File': collector_row.source_file,
                })
                counter[comment.tag] += 1
    if records:
        df_tags = pd.DataFrame(records)
        # Prevent URLs from appearing on multiple lines
        content = df_tags.to_markdown(index=False, tablefmt='github', maxcolwidths=None) or ''
        for line in content.split('\n'):
            if not line.startswith('/'):
                output += '\n'
            output += line
    logger.text_debug('counter', counter=counter)

    sorted_counter = {tag: counter[tag] for tag in tag_order if tag in counter}
    logger.text_debug('sorted_counter', sorted_counter=sorted_counter)
    if formatted_summary := ', '.join(
        f'{tag} ({count})' for tag, count in sorted_counter.items()
    ):
        output += f'\n\nFound code tags for {formatted_summary}\n'
    return output


@beartype
def write_code_tag_file(
    path_tag_summary: Path,
    paths_source: List[Path],
    base_dir: Path,
    regex: str = '',
    tags: str = '',
    header: str = '# Task Summary\n\nAuto-Generated by `calcipy`',
) -> None:
    """Create the code tag summary file.

    Args:
        path_tag_summary: Path to the output file
        paths_source: list of source files to parse
        base_dir: base directory relative to the searched files
        regex: compiled regular expression. Expected to have matching groups `(tag, text)`.
            Default is CODE_TAG_RE with tags from tag_order
        tags: subset of all tags to include in the report and specified order. Default is COMMON_CODE_TAGS
        header: header text

    """
    tag_order = [_t.strip() for _t in tags.split(',') if _t] or COMMON_CODE_TAGS
    matcher = (regex or CODE_TAG_RE).format(tag='|'.join(tag_order))

    matches = _search_files(paths_source, re.compile(matcher))
    if report := _format_report(
        base_dir, matches, tag_order=tag_order,
    ).strip():
        path_tag_summary.write_text(f'{header}\n\n{report}\n\n<!-- {SKIP_PHRASE} -->\n')
        logger.text('Created Code Tag Summary', path_tag_summary=path_tag_summary)
    elif path_tag_summary.is_file():
        path_tag_summary.unlink()
