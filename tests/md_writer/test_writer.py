import json
import shlex
import shutil
import subprocess  # noqa: S404
from functools import partial
from pathlib import Path
from unittest.mock import Mock

import pytest
from beartype.typing import List

from calcipy.invoke_helpers import get_project_path
from calcipy.markup_writer._writer import (
    _format_cov_table,
    _handle_cli_output,
    _handle_coverage,
    _handle_source_file,
    _parse_var_comment,
    _ParseSkipError,
    _ReplacementMachine,
    write_template_formatted_sections,
)
from tests.configuration import TEST_DATA_DIR

SAMPLE_README_PATH = TEST_DATA_DIR / 'sample_doc_files' / 'README.md'

_COVERAGE_SAMPLE_DATA = {
    'meta': {'timestamp': '2021-06-03T19:37:11.980123'},
    'files': {
        'calcipy/doit_tasks/base.py': {
            'summary': {
                'covered_lines': 20,
                'num_statements': 22,
                'percent_covered': 90.9090909090909,
                'missing_lines': 2,
                'excluded_lines': 3,
            },
        },
        'calcipy/doit_tasks/code_tags.py': {
            'summary': {
                'covered_lines': 31,
                'num_statements': 75,
                'percent_covered': 41.333333333333336,
                'missing_lines': 44,
                'excluded_lines': 0,
            },
        },
    },
    'totals': {
        'covered_lines': 51,
        'num_statements': 97,
        'percent_covered': 52.57732,
        'missing_lines': 46,
        'excluded_lines': 3,
    },
}
"""Sample coverage data generated with `python -m coverage json`."""


def test_format_cov_table(snapshot):
    result = _format_cov_table(_COVERAGE_SAMPLE_DATA)

    assert '\n'.join(result) == snapshot


def test_write_template_formatted_sections(fix_test_cache, snapshot):
    path_new_readme = fix_test_cache / SAMPLE_README_PATH.name
    shutil.copyfile(SAMPLE_README_PATH, path_new_readme)
    path_cover = fix_test_cache / 'coverage.json'
    path_cover.write_text(json.dumps(_COVERAGE_SAMPLE_DATA))
    placeholder = '<!-- {cts} SOURCE_FILE_TEST=/tests/test_zz_calcipy.py; -->\n<!-- {cte} -->'
    was_placeholder = placeholder in path_new_readme.read_text()

    write_template_formatted_sections(
        handler_lookup={
            'SOURCE_FILE_TEST': _handle_source_file,
            'COVERAGE_TEST': partial(_handle_coverage, path_coverage=path_cover),
        },
        paths=[path_new_readme],
    )

    text = path_new_readme.read_text()
    assert was_placeholder
    assert placeholder not in text
    assert text == snapshot


@pytest.mark.parametrize(
    ('line', 'match'),
    [
        ('<!-- {cts} rating=1; (User can specify rating on scale of 1-5) -->', {'rating': '1'}),
        ('<!-- {cts} path_image=imgs/image_filename.png; -->', {'path_image': 'imgs/image_filename.png'}),
        ('<!-- {cts} tricky_var_3=-11e-21; -->', {'tricky_var_3': '-11e-21'}),
        ('  {% [cts] key=value; %}', {'key': 'value'}),
        ('<!-- {cts} COVERAGE table; -->', {}),
        ('text <!-- {cts} key=value; -->', {}),
    ],
)
def test_parse_var_comment(line, match):
    result = _parse_var_comment(line)

    assert result == match


def _star_parser(line: str, path_md: Path) -> List[str]:
    rating = int(_parse_var_comment(line)['rating'])
    return [f'RATING={rating}']


def test_write_template_formatted_sections_custom(fix_test_cache):
    path_new_readme = fix_test_cache / SAMPLE_README_PATH.name
    shutil.copyfile(SAMPLE_README_PATH, path_new_readme)

    write_template_formatted_sections(handler_lookup={'rating': _star_parser}, paths=[path_new_readme])

    text = path_new_readme.read_text()
    assert '\n<!-- {cts} rating=' in SAMPLE_README_PATH.read_text()
    assert '\n<!-- {cts} rating=' not in text
    assert '\n\nRATING=4\n\n' in text
    assert (
        """<!-- {cts} name_image=NA.png; (User can specify image name) -->
<!-- Capture image -->
<!-- {cte} -->"""
        in text
    )


_LOOKUP = {'KEY=': lambda _line, _path: ['NEW']}


def _skip(line: str, path_file: Path) -> List[str]:
    raise _ParseSkipError('skip')


@pytest.mark.parametrize(
    ('lines', 'lookup', 'expected'),
    [
        (['a', 'b'], _LOOKUP, ['a', 'b']),
        (['a', '<!-- {cts} KEY=1; -->', 'old', '<!-- {cte} -->', 'b'], _LOOKUP, ['a', 'NEW', 'b']),
        (['{% [cts] KEY=1; %}', 'old', '{% [cte] %}', '{% [cte] %}'], _LOOKUP, ['NEW', '{% [cte] %}']),
        (
            ['<!-- {cts} OTHER=1; -->', 'old', '<!-- {cte} -->'],
            _LOOKUP,
            ['<!-- {cts} OTHER=1; -->', 'old', '<!-- {cte} -->'],
        ),
        (
            ['<!-- {cts} KEY=1; -->', 'old', '<!-- {cte} -->'],
            {**_LOOKUP, 'KEY': _LOOKUP['KEY=']},
            ['<!-- {cts} KEY=1; -->', 'old', '<!-- {cte} -->'],
        ),
        (
            ['<!-- {cts} KEY=1; -->', 'old', '<!-- {cte} -->'],
            {'KEY=': _skip},
            ['<!-- {cts} KEY=1; -->', 'old', '<!-- {cte} -->'],
        ),
    ],
    ids=['no-markers', 'replaced', 'jinja-and-stray-end', 'no-handler', 'ambiguous-handlers', 'handler-skips'],
)
def test_replacement_machine(lines, lookup, expected):
    assert _ReplacementMachine().parse(lines, lookup, Path('test.md')) == expected


def test_write_template_formatted_sections_skips_missing_coverage(fix_test_cache):
    path_md = fix_test_cache / 'skip_test.md'
    original = '# Doc\n<!-- {cts} COVERAGE test; -->\nold content\n<!-- {cte} -->\n'
    path_md.write_text(original)
    handler = partial(_handle_coverage, path_coverage=fix_test_cache / 'missing.json')

    write_template_formatted_sections(handler_lookup={'COVERAGE': handler}, paths=[path_md])

    assert path_md.read_text() == original


@pytest.mark.parametrize(
    ('start', 'end'),
    [
        ('<!-- {cts} SOURCE_FILE=src/code.py; -->', '<!-- {cte} -->'),
        ('{% [cts] SOURCE_FILE=src/code.py; %}', '{% [cte] %}'),
    ],
)
def test_handle_source_file_relative_to_markdown(tmp_path, start, end):
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src' / 'code.py').write_text('a = 1\nb = 2\n')
    path_md = tmp_path / 'doc.md'
    path_md.write_text(f'{start}\nstale\n{end}\n')

    write_template_formatted_sections(handler_lookup={'SOURCE_FILE=': _handle_source_file}, paths=[path_md])

    assert path_md.read_text() == f'{start}\n\n```py\na = 1\nb = 2\n```\n\n{end}\n'


def _completed(returncode=0, stdout='', stderr=''):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


@pytest.mark.parametrize(
    ('line', 'result', 'output'),
    [
        (
            '<!-- {cts} CLI_OUTPUT=./run --help; -->',
            _completed(stdout='usage\n  detail\n\n'),
            ['usage', '  detail'],
        ),
        ('<!-- {cts} CLI_OUTPUT=uv run "a b"; -->', _completed(returncode=1, stderr='failed\n'), ['failed']),
        ('{% [cts] CLI_OUTPUT=python -m pkg; %}', _completed(stdout='out', stderr='err'), ['out']),
        ('<!-- {cts} CLI_OUTPUT=python3 -m pkg; -->', _completed(), ['']),
    ],
    ids=['run', 'uv-stderr', 'python-jinja', 'python3-empty'],
)
def test_handle_cli_output(monkeypatch, line, result, output):
    subprocess_run = Mock(return_value=result)
    monkeypatch.setattr(subprocess, 'run', subprocess_run)
    command = _parse_var_comment(line)['CLI_OUTPUT']
    html = line.startswith('<!--')

    lines = _handle_cli_output(line, Path('fake.md'))

    start = f'<!-- {{cts}} CLI_OUTPUT={command}; -->' if html else f'{{% [cts] CLI_OUTPUT={command}; %}}'
    end = '<!-- {cte} -->' if html else '{% [cte] %}'
    assert lines == [start, '', '```txt', *output, '```', '', end]
    subprocess_run.assert_called_once_with(
        shlex.split(command), capture_output=True, text=True, cwd=get_project_path(), timeout=30, check=False
    )


@pytest.mark.parametrize(
    ('line', 'side_effect', 'match'),
    [
        ('<!-- {cts} CLI_OUTPUT=rm -rf /; -->', None, 'Command not allowed'),
        ('<!-- {cts} CLI_OUTPUT=uvx tool; -->', None, 'Command not allowed'),
        ('<!-- {cts} CLI_OUTPUT_MISSING; -->', None, 'Command not allowed'),
        ('<!-- {cts} CLI_OUTPUT=uv run x; -->', [_completed(returncode=2)], 'Command failed with exit code 2'),
        ('<!-- {cts} CLI_OUTPUT=uv run x; -->', subprocess.TimeoutExpired('uv', 30), 'timed out'),
    ],
)
def test_handle_cli_output_skips(monkeypatch, line, side_effect, match):
    subprocess_run = Mock(side_effect=side_effect)
    monkeypatch.setattr(subprocess, 'run', subprocess_run)

    with pytest.raises(_ParseSkipError, match=match):
        _handle_cli_output(line, Path('fake.md'))

    assert subprocess_run.call_count == (0 if side_effect is None else 1)
