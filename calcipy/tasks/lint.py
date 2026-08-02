"""Lint CLI."""

from contextlib import suppress
from pathlib import Path

from beartype.typing import Optional
from corallium.file_helpers import read_package_name
from corallium.file_search import find_project_files_by_suffix
from corallium.log import LOGGER
from invoke.context import Context

from calcipy.cli import task
from calcipy.invoke_helpers import run

from .executable_utils import PRE_COMMIT_MESSAGE, VALE_MESSAGE, check_installed, python_dir, python_m

# ==============================================================================
# Linting


def _resolve_package_target() -> str:
    """Resolve package directory for src or flat layouts."""
    pkg = read_package_name()
    src_path = Path(f'./src/{pkg}')
    flat_path = Path(f'./{pkg}')
    if src_path.is_dir():
        return f'"{src_path.as_posix()}"'
    if flat_path.is_dir():
        return f'"{flat_path.as_posix()}"'
    return '.'


def _inner_task(
    ctx: Context,
    *,
    command: str,
    cli_args: str = '',
    run_as_module: bool = True,
    target: Optional[str] = None,
) -> None:
    """Shared task logic."""
    file_args = []
    with suppress(AttributeError):
        file_args = ctx.config.gto.file_args
    if file_args:
        target = ' '.join([f'"{a_}"' for a_ in file_args])
    elif target is None:
        target = f'{_resolve_package_target()} ./tests'

    cmd = f'{python_m()} {command}' if run_as_module else f'{python_dir() / command}'
    run(ctx, f'{cmd} {target} {cli_args}'.strip())


@task(default=True)
def check(ctx: Context) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, command='ruff check')


@task(
    help={
        'unsafe': 'if provided, attempt even fixes considered unsafe',
    },
)
def fix(ctx: Context, *, unsafe: bool = False) -> None:
    """Run ruff and apply fixes."""
    cli_args = '--fix'
    if unsafe:
        cli_args += ' --unsafe-fixes'
    _inner_task(ctx, command='ruff check', cli_args=cli_args)


@task()
def watch(ctx: Context) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, command='ruff check', cli_args='--watch')


# ==============================================================================
# Prose


@task(
    help={
        'target': 'Space-separated directories or files to lint. Defaults to the whole repository',
        'glob': "Filter the files under `target` (for example, '*.md'). Passed to `vale --glob`",
        'no_sync': 'Skip `vale sync`, which pulls the ai-tells style package',
    },
)
def prose(ctx: Context, *, target: str = '.', glob: str = '', no_sync: bool = False) -> None:
    """Run vale with the ai-tells style to flag AI-generated prose tells (beta).

    Requires a `.vale.ini` with `ai-tells` as a `BasedOnStyles` entry. See
    https://github.com/tbhb/vale-ai-tells for the style package and rule list.

    A glob given as a `target` would be read as a file path and silently linted as empty stdin,
    so patterns must go through `--glob` instead.

    """
    check_installed(ctx, executable='vale', message=VALE_MESSAGE)
    if not no_sync:
        run(ctx, 'vale sync')
    cli_args = f" --glob='{glob}'" if glob else ''
    run(ctx, f'vale{cli_args} {target}')


@task(
    help={
        'target': 'Directory to search for Markdown files. Defaults to the whole repository',
        'output_dir': 'Directory to write the `generated_<source>.jsonl` corpus file into',
        'source': 'Corpus label used for the `model`/`source` fields and the output filename',
    },
)
def slop_export(_ctx: Context, *, target: str = '.', output_dir: str = 'out/slop-corpus', source: str = 'repo') -> None:
    """Export a Markdown corpus as slop-forensics JSONL, the occasional-batch-job companion to `lint.prose` (beta).

    Strips fences, front matter, inline code, links, and headings, then keeps documents over 150
    words. Building the corpus-specific word list is the piece that survives a model version
    change, unlike `lint.prose`'s fixed rule pack, but the profiling step itself needs a separate
    checkout of https://github.com/sam-paech/slop-forensics (its own venv with nltk/wordfreq/etc).

    """
    from calcipy.experiments.slop_corpus_export import write_corpus_jsonl  # noqa: PLC0415

    paths = sorted(find_project_files_by_suffix(Path(target)).get('md', []))
    corpus_path = write_corpus_jsonl(paths, Path(output_dir), source=source)
    LOGGER.text(
        f'Wrote {corpus_path}. Run slop-forensics against it with:\n'
        f'    python scripts/slop_profile.py --input-dir {output_dir} '
        '--analysis-output-dir out/analysis --combined-output-file out/results.json',
    )


# ==============================================================================
# prek

PRE_COMMIT_HOOK_STAGES = [
    'manual',
    'post-checkout',
    'post-commit',
    'post-merge',
    'post-rewrite',
    'pre-commit',
    'pre-merge-commit',
    'pre-push',
    'pre-rebase',
]


@task(
    help={
        'no_update': 'Skip updating the prek hooks',
    },
)
def pre_commit(ctx: Context, *, no_update: bool = False) -> None:
    """Run prek."""
    check_installed(ctx, executable='prek', message=PRE_COMMIT_MESSAGE)

    run(ctx, 'prek install')
    if not no_update:
        run(ctx, 'prek autoupdate')

    for stage in PRE_COMMIT_HOOK_STAGES:
        run(ctx, f'prek run --all-files --hook-stage {stage}')
