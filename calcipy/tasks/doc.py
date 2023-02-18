"""Document CLI."""

import shutil
import webbrowser
from pathlib import Path

from beartype import beartype
from beartype.typing import Literal
from invoke import Context
from shoal.cli import task

from ..file_helpers import _MKDOCS_CONFIG_NAME, _read_yaml_file, open_in_browser, trim_trailing_whitespace
from ..md_writer import write_autoformatted_md_sections


@beartype
def _diagram_task(ctx: Context, pdoc_out_path: Path) -> None:
    """Return actions to generate code diagrams in the module documentation directory.

    Note: must be run after `document` because pdoc will delete these files

    PUML support may be coming in a future release: https://github.com/PyCQA/pylint/issues/4498

    Args:
        pdoc_out_path: path to the top-level pdoc output. Expect subdir with module name

    """
    diagram_md = """# Code Diagrams

> Auto-generated with `pylint-pyreverse`

## Packages

![./packages.svg](./packages.svg)

[Full Size](./packages.svg)

## Classes

![./classes.svg](./classes.svg)

[Full Size](./classes.svg)
"""
    path_diagram = pdoc_out_path / dg.meta.pkg_name / '_code_diagrams.md'
    path_diagram.write_text(diagram_md)
    ctx.run(
        f'poetry run pyreverse {dg.meta.pkg_name} --output svg --output-directory {path_diagram.parent}',
    )


@beartype
def _ensure_handler_lookup() -> None:
    """Configure the handler lookup if not already configured."""
    if dg.doc.handler_lookup is None:
        dg.doc.handler_lookup = {
            'COVERAGE ': _handle_coverage,
            'SOURCE_FILE=': _handle_source_file,
        }


@task()  # type: ignore[misc]
def build(ctx: Context) -> None:
    """Build documentation with mkdocs."""
    _ensure_handler_lookup()

    auto_doc_path = dg.doc.auto_doc_path
    write_autoformatted_md_sections()
    shutil.rmtree(auto_doc_path)
    _diagram_task(ctx, auto_doc_path)

    # Find and trim trailing whitespace
    for path_md in auto_doc_path.rglob('*.md'):
        trim_trailing_whitespace(path_md)

    ctx.run(f'poetry run mkdocs build --site-dir {dg.doc.path_out}')


@beartype
def _is_mkdocs_local() -> bool:
    """Check if mkdocs is configured for local output.

    See notes on local-link configuration here: https://github.com/timothycrosley/portray/issues/65

    Additional information on using local search here: https://github.com/wilhelmer/mkdocs-localsearch

    Returns:
        bool: True if configured for local file output rather than hosted

    """
    mkdocs_config = _read_yaml_file(dg.meta.path_project / _MKDOCS_CONFIG_NAME)
    return mkdocs_config.get('use_directory_urls') is False


@task()  # type: ignore[misc]
def watch(ctx: Context) -> None:
    """Serve local documentation for local editing."""
    if _is_mkdocs_local():  # pragma: no cover
        path_doc_index = dg.doc.path_out / 'index.html'
        open_in_browser(path_doc_index)
    else:
        webbrowser.open('http://localhost:8000')
        ctx.run('poetry run mkdocs serve --dirtyreload')


@task()  # type: ignore[misc]
def deploy(ctx: Context) -> None:
    """Deploy docs to the Github `gh-pages` branch."""
    if _is_mkdocs_local():  # pragma: no cover
        raise NotImplementedError('Not yet configured to deploy documentation without "use_directory_urls"')

    ctx.run('poetry run mkdocs gh-deploy')
