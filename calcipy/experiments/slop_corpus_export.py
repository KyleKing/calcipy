"""Experiment with exporting a Markdown corpus to the JSONL format slop-forensics expects."""

import json
import re
from pathlib import Path

from beartype.typing import Iterable

FENCE = re.compile(r'^```.*?^```', re.MULTILINE | re.DOTALL)
FRONTMATTER = re.compile(r'\A---\n.*?\n---\n', re.DOTALL)
INLINE_CODE = re.compile(r'`[^`]+`')
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')
HEADING_MARK = re.compile(r'^#{1,6}\s+', re.MULTILINE)

MIN_WORD_COUNT = 150
"""Documents shorter than this are dropped as too thin a sample for a slop fingerprint."""


def to_prose(raw: str) -> str:
    """Strip Markdown structure that would otherwise skew the word/n-gram counts."""
    text = FRONTMATTER.sub('', raw)
    text = FENCE.sub('', text)
    text = INLINE_CODE.sub('', text)
    text = LINK.sub(r'\1', text)
    return HEADING_MARK.sub('', text).strip()


def build_corpus(
    paths: Iterable[Path],
    *,
    source: str,
    min_word_count: int = MIN_WORD_COUNT,
) -> Iterable[dict[str, str]]:
    """Yield slop-forensics records (`model`, `source`, `id`, `output`) for each qualifying file."""
    for path in paths:
        body = to_prose(path.read_text())
        if len(body.split()) < min_word_count:
            continue
        yield {'model': source, 'source': source, 'id': path.as_posix(), 'output': body}


def write_corpus_jsonl(paths: Iterable[Path], output_dir: Path, *, source: str) -> Path:
    """Write a `generated_<source>.jsonl` file that `slop_profile.py --input-dir` can read.

    Returns:
        Path: to the written file

    """
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f'generated_{source}.jsonl'
    records = list(build_corpus(paths, source=source))
    with target.open('w') as handle:
        for record in records:
            handle.write(json.dumps(record) + '\n')
    return target
