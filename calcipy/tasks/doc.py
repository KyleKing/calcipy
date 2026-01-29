"""Document CLI."""

import webbrowser
from contextlib import suppress
from pathlib import Path

from corallium.file_helpers import (
    MKDOCS_CONFIG,
    open_in_browser,
    read_yaml_file,
)
from invoke.context import Context
from invoke.exceptions import UnexpectedExit

from calcipy.cli import task
from calcipy.invoke_helpers import get_project_path, run
from calcipy.markup_writer import write_template_formatted_sections

from .executable_utils import python_m


def get_out_dir() -> Path:
    """Returns the mkdocs-specified site directory."""
    mkdocs_config = read_yaml_file(get_project_path() / MKDOCS_CONFIG)
    return Path(mkdocs_config.get('site_dir', 'releases/site'))


@task()
def build(ctx: Context) -> None:
    """Build documentation with mkdocs."""
    write_template_formatted_sections()
    run(ctx, f'{python_m()} mkdocs build --site-dir {get_out_dir()}')


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
        run(ctx, f'{python_m()} mkdocs serve --dirtyreload')


@task()
def deploy(ctx: Context) -> None:
    """Deploy docs to the Github `gh-pages` branch."""
    if _is_mkdocs_local():  # pragma: no cover
        raise NotImplementedError('Not yet configured to deploy documentation without "use_directory_urls"')

    with suppress(UnexpectedExit):
        run(ctx, 'prek uninstall')  # To prevent prek failures when mkdocs calls push
    run(ctx, f'{python_m()} mkdocs gh-deploy --force')
    with suppress(UnexpectedExit):
        run(ctx, 'prek install')  # Restore prek
