import json

import pytest

from calcipy.experiments.slop_corpus_export import build_corpus, to_prose, write_corpus_jsonl


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        (
            (
                '---\ntitle: x\n---\n# Heading\n\n'
                'Some `inline code` and a [link](https://example.com) survive as prose.\n\n```python\ndropped()\n```\n'
            ),
            'Heading\n\nSome  and a link survive as prose.',
        ),
        ('Intro\n\n---\nnot: frontmatter\n---\n', 'Intro\n\n---\nnot: frontmatter\n---'),
        ('###### Deep\n####### Seven', 'Deep\n####### Seven'),
        ('a [](empty) b `x` c', 'a  b  c'),
    ],
    ids=['all-structure', 'rule-not-at-start', 'heading-levels', 'inline'],
)
def test_to_prose(raw, expected):
    assert to_prose(raw) == expected


def test_build_corpus_honors_min_word_count(tmp_path):
    short, long_ = tmp_path / 'short.md', tmp_path / 'long.md'
    short.write_text('one two')
    long_.write_text('# one two `x` three')

    records = list(build_corpus([short, long_], source='src', min_word_count=3))

    assert records == [{'model': 'src', 'source': 'src', 'id': long_.as_posix(), 'output': 'one two  three'}]


def test_write_corpus_jsonl(tmp_path):
    kept, dropped = tmp_path / 'kept.md', tmp_path / 'dropped.md'
    kept.write_text(' '.join(['word'] * 150))
    dropped.write_text(' '.join(['word'] * 149))
    output_dir = tmp_path / 'nested' / 'out'

    write_corpus_jsonl([kept], output_dir, source='other')
    target = write_corpus_jsonl([dropped, kept], output_dir, source='repo')

    assert target == output_dir / 'generated_repo.jsonl'
    record = {'model': 'repo', 'source': 'repo', 'id': kept.as_posix(), 'output': ' '.join(['word'] * 150)}
    assert target.read_text() == json.dumps(record) + '\n'
    assert sorted(p.name for p in output_dir.iterdir()) == ['generated_other.jsonl', 'generated_repo.jsonl']
