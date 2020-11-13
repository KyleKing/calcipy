"""Collect issue tags and output for review in a single location."""

# PLANNED: Finish documenting arguments and returns

import re
from collections import defaultdict
from pathlib import Path
from typing import List, Pattern, Sequence

import attr


@attr.s(auto_attribs=True)
class _TaggedComment:  # noqa: H601
    """Tagged (FIXME,TODO,etc) with contextual information."""

    lineno: int
    tag: str
    text: str


@attr.s(auto_attribs=True)
class _TaggedComments:  # noqa: H601
    """Collection of tagged comments with additional contextual information."""

    file_path: Path
    tagged_comments: List[_TaggedComment]


def _compile_issue_regex(regex_raw: str, tags: List[str]) -> Pattern[str]:
    """Compile the regex for the specified raw regular expression string and tags.

    """
    return re.compile(regex_raw.format(tag='|'.join(tags)))


_regex_raw = r'((\s|\()(?P<tag>{tag})(:[^\r\n]))(?P<text>.+)'
_tags = ['DEBUG', 'FIXME', 'FYI', 'HACK', 'NOTE', 'PLANNED', 'REVIEW', 'TBD', 'TODO']

_COMPILED_RE = _compile_issue_regex(_regex_raw, _tags)
"""Default compiled regular expression."""


def _read_lines(file_path: Path) -> List[str]:
    """Read a file and split on newlines for later parsing.

    """
    return file_path.read_text().split('\n')


def _search_lines(lines: Sequence[str],
                  regex_compiled: Pattern[str] = _COMPILED_RE) -> List[_TaggedComment]:
    """Search lines of text for matches to the compiled regular expression.

    """
    comments = []
    for lineno, line in enumerate(lines):
        match = regex_compiled.search(line)
        if match:
            mg = match.groupdict()
            comments.append(_TaggedComment(lineno + 1, tag=mg['tag'], text=mg['text']))
    return comments


def _search_files(file_paths: Sequence[Path],
                  regex_compiled: Pattern[str] = _COMPILED_RE) -> List[_TaggedComments]:
    """Collect matches from multiple files.

    """
    matches = []
    for file_path in file_paths:
        comments = _search_lines(_read_lines(file_path), regex_compiled)
        if comments:
            matches.append(_TaggedComments(file_path, comments))
    return matches


def _format_report(base_dir: Path, tagged_collection: List[_TaggedComments]) -> str:
    """Pretty-format the tagged items by file and line number.

    """
    output = ''
    counter = defaultdict(lambda: 0)
    for comments in sorted(tagged_collection, key=lambda tc: tc.file_path, reverse=False):
        output += f'{comments.file_path.relative_to(base_dir)}\n'
        for comment in comments.tagged_comments:
            output += f'    line {comment.lineno:>3} {comment.tag:>7}: {comment.text}\n'
            counter[comment.tag] += 1
        output += '\n'

    formatted_summary = ',  '.join([f'{tag} ({count})' for tag, count in counter.items()])
    if formatted_summary:
        output += f'Found tagged comments for {formatted_summary}\n'
    return output


# FIXME: Create a DoIt task using DIG
