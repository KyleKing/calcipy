"""Document CLI."""

import webbrowser
from contextlib import suppress
from pathlib import Path

from beartype import beartype
from corallium.file_helpers import (
    MKDOCS_CONFIG,
    delete_dir,
    ensure_dir,
    open_in_browser,
    read_package_name,
    read_yaml_file,
    trim_trailing_whitespace,
)
from invoke.context import Context
from invoke.exceptions import UnexpectedExit

from ..cli import task
from ..invoke_helpers import get_doc_subdir, get_project_path, run
from ..md_writer import write_autoformatted_md_sections
from .executable_utils import python_dir


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
    pkg_name = read_package_name()
    path_diagram = pdoc_out_path / pkg_name / '_code_diagrams.md'
    ensure_dir(path_diagram.parent)
    path_diagram.write_text(diagram_md)
    run(ctx, f'{python_dir()}/pyreverse {pkg_name} --output svg --output-directory {path_diagram.parent}')


@beartype
def get_out_dir() -> Path:
    """Retrieve the mkdocs-specified site directory."""
    mkdocs_config = read_yaml_file(get_project_path() / MKDOCS_CONFIG)
    return Path(mkdocs_config.get('site_dir', 'releases/site'))


@task()
def build(ctx: Context) -> None:
    """Build documentation with mkdocs."""
    auto_doc_path = get_doc_subdir().parent / 'modules'
    write_autoformatted_md_sections()
    delete_dir(auto_doc_path)
    _diagram_task(ctx, auto_doc_path)

    # Find and trim trailing whitespace
    for path_md in auto_doc_path.rglob('*.md'):
        trim_trailing_whitespace(path_md)

    run(ctx, f'{python_dir()}/mkdocs build --site-dir {get_out_dir()}')


@beartype
def _is_mkdocs_local() -> bool:
    """Check if mkdocs is configured for local output.

    See notes on local-link configuration here: https://github.com/timothycrosley/portray/issues/65

    Additional information on using local search here: https://github.com/wilhelmer/mkdocs-localsearch

    Returns:
        bool: True if configured for local file output rather than hosted

    """
    mkdocs_config = read_yaml_file(get_project_path() / MKDOCS_CONFIG)
    return mkdocs_config.get('use_directory_urls') is False


@task()
def watch(ctx: Context) -> None:
    """Serve local documentation for local editing."""
    if _is_mkdocs_local():  # pragma: no cover
        path_doc_index = get_out_dir() / 'index.html'
        open_in_browser(path_doc_index)
    else:  # pragma: no cover
        webbrowser.open('http://localhost:8000')
        run(ctx, f'{python_dir()}/mkdocs serve --dirtyreload')


@task()
def deploy(ctx: Context) -> None:
    """Deploy docs to the Github `gh-pages` branch."""
    if _is_mkdocs_local():  # pragma: no cover
        raise NotImplementedError('Not yet configured to deploy documentation without "use_directory_urls"')

    with suppress(UnexpectedExit):
        run(ctx, 'pre-commit uninstall')  # To prevent pre-commit failures when mkdocs calls push
    run(ctx, f'{python_dir()}/mkdocs gh-deploy --force')
    with suppress(UnexpectedExit):
        run(ctx, 'pre-commit install')  # Restore pre-commit
