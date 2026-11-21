import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from invoke.exceptions import UnexpectedExit
from invoke.runners import Result

from calcipy.tasks.doc import build, deploy, watch
from calcipy.tasks.executable_utils import python_m, resolve_python

_README = """# Title

<!-- {cts} SOURCE_FILE=/src.py; -->
stale
<!-- {cte} -->

<!-- {cts} COVERAGE table; -->
stale
<!-- {cte} -->

<!-- {cts} UNKNOWN=1; -->
kept
<!-- {cte} -->
"""

_README_BUILT = """# Title

<!-- {cts} SOURCE_FILE=/src.py; -->

```py
x = 1
```

<!-- {cte} -->

<!-- {cts} COVERAGE table; -->

| File       | Statements | Missing | Excluded | Coverage |
|------------|-----------:|--------:|---------:|---------:|
| `src.py`   | 2          | 1       | 0        | 50.0%    |
| **Totals** | 2          | 1       | 0        | 50.0%    |

Generated on: 2024-01-02

<!-- {cte} -->

<!-- {cts} UNKNOWN=1; -->
kept
<!-- {cte} -->
"""

_SUMMARY = {'num_statements': 2, 'missing_lines': 1, 'excluded_lines': 0, 'percent_covered': 50.0}


def _ghp_import(site_dir: str) -> str:
    return f'{python_m()} ghp_import --no-jekyll --push --force --message "Deployed docs" {site_dir}'


def test_build_formats_markdown_then_runs_zensical(ctx, tmp_project):
    (tmp_project / 'mkdocs.yml').write_text('docs_dir: documentation\n')
    (tmp_project / 'src.py').write_text('x = 1\n')
    coverage_data = {
        'meta': {'timestamp': '2024-01-02T03:04:05'},
        'files': {'src.py': {'summary': _SUMMARY}},
        'totals': _SUMMARY,
    }
    (tmp_project / 'coverage.json').write_text(json.dumps(coverage_data))
    readme = tmp_project / 'README.md'
    readme.write_text(_README)

    build(ctx)

    assert readme.read_text() == _README_BUILT
    assert [c.args for c in ctx.run.call_args_list] == [
        (f'{resolve_python()} documentation/gen_ref_nav.py',),
        (f'{python_m()} zensical build',),
    ]


def _fail_prek(command, *_args, **_kwargs):
    if command.startswith('prek'):
        raise UnexpectedExit(Result(command=command, exited=1))
    return Result(command=command)


@pytest.mark.parametrize(
    ('mkdocs_yml', 'run_side_effect', 'site_dir'),
    [
        (None, None, 'releases/site'),
        (None, _fail_prek, 'releases/site'),
        ('site_dir: public\nuse_directory_urls: true\n', None, 'public'),
        ('use_directory_urls: false\n', None, None),
        ('', None, 'releases/site'),
    ],
    ids=['defaults', 'prek-fails', 'hosted', 'local-urls', 'empty-config'],
)
def test_deploy(ctx, tmp_project, assert_run_commands, mkdocs_yml, run_side_effect, site_dir):
    ctx.run.side_effect = run_side_effect
    if mkdocs_yml is not None:
        (tmp_project / 'mkdocs.yml').write_text(mkdocs_yml)

    if site_dir is None:
        with pytest.raises(NotImplementedError, match='use_directory_urls'):
            deploy(ctx)
        ctx.run.assert_not_called()
    else:
        deploy(ctx)
        assert_run_commands(ctx, ['prek uninstall', _ghp_import(site_dir), 'prek install'])


@pytest.mark.parametrize(
    ('mkdocs_yml', 'local'),
    [
        ('use_directory_urls: false\nsite_dir: out\n', True),
        ('use_directory_urls: true\nsite_dir: out\n', False),
        ('', False),
    ],
    ids=['local-urls', 'hosted', 'empty-config'],
)
def test_watch(ctx, tmp_project, monkeypatch, assert_run_commands, mkdocs_yml, local):
    (tmp_project / 'mkdocs.yml').write_text(mkdocs_yml)
    open_in_browser = Mock()
    open_url = Mock()
    monkeypatch.setattr('calcipy.tasks.doc.open_in_browser', open_in_browser)
    monkeypatch.setattr('calcipy.tasks.doc.webbrowser.open', open_url)

    watch(ctx)

    if local:
        open_in_browser.assert_called_once_with(Path('out/index.html'))
        open_url.assert_not_called()
        assert_run_commands(ctx, [])
    else:
        open_in_browser.assert_not_called()
        open_url.assert_called_once_with('http://localhost:8000')
        assert_run_commands(ctx, [f'{resolve_python()} docs/gen_ref_nav.py', f'{python_m()} zensical serve'])
