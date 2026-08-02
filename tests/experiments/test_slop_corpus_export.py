import json

from calcipy.experiments.slop_corpus_export import build_corpus, to_prose, write_corpus_jsonl


def test_to_prose_strips_markdown_structure():
    raw = """---
title: x
---
# Heading

Some `inline code` and a [link](https://example.com) survive as prose.

```python
dropped()
```
"""

    prose = to_prose(raw)

    assert 'title: x' not in prose
    assert 'dropped()' not in prose
    assert '`inline code`' not in prose
    assert 'link' in prose
    assert 'https://example.com' not in prose


def test_build_corpus_drops_short_documents(tmp_path):
    short = tmp_path / 'short.md'
    short.write_text('Too short.')
    long_ = tmp_path / 'long.md'
    long_.write_text(' '.join(['word'] * 200))

    records = list(build_corpus([short, long_], source='repo', min_word_count=150))

    assert [r['id'] for r in records] == [long_.as_posix()]
    assert records[0]['model'] == 'repo'
    assert records[0]['source'] == 'repo'


def test_write_corpus_jsonl(tmp_path):
    doc = tmp_path / 'doc.md'
    doc.write_text(' '.join(['word'] * 200))
    output_dir = tmp_path / 'out'

    target = write_corpus_jsonl([doc], output_dir, source='repo')

    assert target == output_dir / 'generated_repo.jsonl'
    record = json.loads(target.read_text().splitlines()[0])
    assert record['id'] == doc.as_posix()
