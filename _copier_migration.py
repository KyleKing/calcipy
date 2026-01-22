"""Migration Script for Poetry to uv conversion.

Run this script to migrate an existing poetry-based project to uv.
The script will self-delete after completion.

Usage:
    python _copier_migration.py
"""

from __future__ import annotations

import re
import sys
from itertools import starmap
from pathlib import Path

try:
    import tomlkit
except ImportError:
    print('tomlkit is required: pip install tomlkit')  # noqa: T201
    sys.exit(1)


def _log(message: str) -> None:
    print(f'[migration] {message}')  # noqa: T201


def _should_skip_migration(doc: dict) -> str | None:
    """Check if migration should be skipped, return reason if so."""
    if 'tool' not in doc or 'poetry' not in doc.get('tool', {}):
        return 'No [tool.poetry] section found, skipping pyproject.toml migration'

    build_system = doc.get('build-system', {})
    is_poetry_backend = 'poetry' in build_system.get('build-backend', '')
    if not is_poetry_backend:
        return 'Not using poetry backend, skipping pyproject.toml migration'

    return None


def _create_build_system() -> dict:
    """Create build-system table for uv."""
    build_system = tomlkit.table()
    build_system['build-backend'] = 'uv_build'
    build_system['requires'] = ['uv_build>=0.9.7']
    return build_system


def _format_dependency_spec(name: str, spec: str | dict) -> str:
    """Format a dependency specification string."""
    if isinstance(spec, str):
        return f'{name}{spec}'

    version = spec.get('version', '>=0')
    extras = spec.get('extras', [])
    if not extras:
        return f'{name}{version}'

    extras_str = ','.join(extras)
    old_extras = ['doc', 'lint', 'nox', 'tags', 'test', 'types']
    if name == 'calcipy' and set(extras) == set(old_extras):
        return 'calcipy[dev]>=5.0.0'

    return f'{name}[{extras_str}]{version}'


def _convert_dev_dependencies(poetry: dict) -> list[str] | None:
    """Convert Poetry dev dependencies to uv dependency-groups format."""
    if 'group' not in poetry or 'dev' not in poetry['group']:
        return None

    dev_deps = poetry['group']['dev'].get('dependencies', {})
    if not dev_deps:
        return None

    return list(starmap(_format_dependency_spec, dev_deps.items()))


def _parse_author(author: str) -> dict:
    """Parse author string into name/email dict."""
    if '<' not in author or '>' not in author:
        return {'name': author}

    if match := re.match(r'(.+?)\s*<(.+?)>', author):
        return {'email': match.group(2), 'name': match.group(1)}

    return {'name': author}


def _convert_authors(poetry: dict) -> list[dict] | None:
    """Convert Poetry authors to project format."""
    if 'authors' not in poetry:
        return None

    return [_parse_author(author) for author in poetry['authors']]


def _convert_dependencies(deps: dict) -> tuple[list[str], str | None]:
    """Convert Poetry dependencies to project format, extracting python version."""
    dep_list = []
    python_version = None

    for name, spec in deps.items():
        if name == 'python':
            python_version = spec
            continue
        dep_list.append(_format_dependency_spec(name, spec))

    return dep_list, python_version


def _format_python_version(version_spec: str) -> str:
    """Format python version spec for requires-python."""
    version_clean = version_spec.lstrip('^~>=<!')
    return f'>={version_clean}'


def _build_urls_table(poetry: dict) -> dict | None:
    """Build URLs table from poetry configuration."""
    if 'urls' in poetry:
        return poetry['urls']

    urls = tomlkit.table()
    if 'repository' in poetry:
        urls['Repository'] = poetry['repository']
    if 'documentation' in poetry:
        urls['Documentation'] = poetry['documentation']

    return urls or None


def _copy_tool_sections(source_doc: dict, target_doc: dict) -> None:
    """Copy non-poetry tool sections from source to target document."""
    if 'tool' not in source_doc:
        return

    for key, value in source_doc['tool'].items():
        if key == 'poetry':
            continue
        if 'tool' not in target_doc:
            target_doc.add('tool', tomlkit.table())
        target_doc['tool'][key] = value


def _add_uv_config(doc: dict) -> None:
    """Add uv configuration to document."""
    if 'tool' not in doc:
        doc.add('tool', tomlkit.table())
    doc['tool']['uv'] = tomlkit.table()
    doc['tool']['uv']['default-groups'] = ['dev']
    doc['tool']['uv']['required-version'] = '>=0.9.0'


def _build_project_section(poetry: dict) -> dict:
    """Build the project section from poetry configuration."""
    project = tomlkit.table()

    if authors := _convert_authors(poetry):
        project['authors'] = tomlkit.array(authors)

    if 'classifiers' in poetry:
        project['classifiers'] = poetry['classifiers']

    deps = poetry.get('dependencies', {})
    dep_list, python_version = _convert_dependencies(deps)
    if dep_list:
        project['dependencies'] = tomlkit.array(dep_list)

    simple_fields = ['description', 'keywords', 'license', 'maintainers', 'name', 'readme', 'version']
    for key in simple_fields:
        if key in poetry:
            project[key] = poetry[key]

    if python_version:
        project['requires-python'] = _format_python_version(python_version)

    if 'scripts' in poetry:
        project['scripts'] = poetry['scripts']

    if urls := _build_urls_table(poetry):
        project['urls'] = urls

    return project


def _migrate_pyproject_toml() -> None:
    """Convert pyproject.toml from Poetry to uv format."""
    pyproject_path = Path('pyproject.toml')
    if not pyproject_path.is_file():
        _log('pyproject.toml not found, skipping')
        return

    content = pyproject_path.read_text(encoding='utf-8')
    doc = tomlkit.parse(content)

    if skip_reason := _should_skip_migration(doc):
        _log(skip_reason)
        return

    _log('Migrating pyproject.toml from Poetry to uv...')

    poetry = doc['tool']['poetry']
    new_doc = tomlkit.document()

    new_doc.add('build-system', _create_build_system())

    if dev_deps := _convert_dev_dependencies(poetry):
        new_doc.add('dependency-groups', tomlkit.table())
        new_doc['dependency-groups']['dev'] = tomlkit.array(dev_deps)

    new_doc.add('project', _build_project_section(poetry))

    _copy_tool_sections(doc, new_doc)
    _add_uv_config(new_doc)

    pyproject_path.write_text(tomlkit.dumps(new_doc), encoding='utf-8')
    _log('pyproject.toml migrated successfully')


def _update_file_content(path: Path, replacements: list[tuple[str, str]]) -> bool:
    """Update file content with the given replacements."""
    if not path.is_file():
        return False

    content = path.read_text(encoding='utf-8')
    original = content

    for old, new in replacements:
        content = content.replace(old, new)

    if content != original:
        path.write_text(content, encoding='utf-8')
        return True
    return False


def _migrate_workflow_files() -> None:
    """Update GitHub workflow files."""
    workflows_dir = Path('.github/workflows')
    if not workflows_dir.is_dir():
        return

    replacements = [
        ('poetry run ', 'uv run '),
        ('poetry.lock', 'uv.lock'),
        ('poetry install', 'uv sync'),
        ('cache: poetry', 'enable-cache: true'),
    ]

    for workflow in workflows_dir.glob('*.yml'):
        if _update_file_content(workflow, replacements):
            _log(f'Updated {workflow}')

    setup_action = Path('.github/actions/setup/action.yml')
    if setup_action.is_file():
        content = setup_action.read_text(encoding='utf-8')
        if 'poetry' in content.lower() or 'pipx' in content.lower():
            _log(f'Action {setup_action} needs manual review for uv migration')


def _migrate_pre_commit() -> None:
    """Update .pre-commit-config.yaml."""
    pre_commit_path = Path('.pre-commit-config.yaml')
    replacements = [
        ('poetry run ', 'uv run '),
        ('poetry.lock', 'uv.lock'),
        ('poetry\\.lock', 'uv\\.lock'),
        ('lint.pre-commit', 'lint.prek'),
        ('pre-commit install', 'prek install -f'),
        ('pre-commit autoupdate', 'prek autoupdate'),
        ('pre-commit run', 'prek run'),
    ]

    if _update_file_content(pre_commit_path, replacements):
        _log('Updated .pre-commit-config.yaml')


def _migrate_run_script() -> None:
    """Update run script."""
    run_path = Path('run')
    replacements = [
        ('poetry run ', 'uv run '),
    ]

    if _update_file_content(run_path, replacements):
        _log('Updated run script')


def _migrate_docs() -> None:
    """Update documentation files."""
    doc_dirs = [Path('docs'), Path('doc')]
    replacements = [
        ('poetry install --sync', 'uv sync --all-extras'),
        ('poetry install', 'uv sync'),
        ('poetry run ', 'uv run '),
        ('poetry config ', '# (uv uses UV_PUBLISH_TOKEN env var) '),
    ]

    for doc_dir in doc_dirs:
        if not doc_dir.is_dir():
            continue
        for md_file in doc_dir.rglob('*.md'):
            if _update_file_content(md_file, replacements):
                _log(f'Updated {md_file}')


def _cleanup_poetry_files() -> None:
    """Remove Poetry-specific files."""
    poetry_lock = Path('poetry.lock')
    if poetry_lock.is_file():
        _log('Removing poetry.lock')
        poetry_lock.unlink()

    poetry_toml = Path('poetry.toml')
    if poetry_toml.is_file():
        _log('Removing poetry.toml')
        poetry_toml.unlink()


def _delete_myself() -> None:
    """Delete this script after completion."""
    script_path = Path(__file__)
    if script_path.is_file():
        script_path.unlink()
        _log(f'Deleted migration script: {script_path.name}')


def main() -> None:
    """Run the migration."""
    _log('Starting Poetry to uv migration...')
    _log('')

    _migrate_pyproject_toml()
    _migrate_workflow_files()
    _migrate_pre_commit()
    _migrate_run_script()
    _migrate_docs()
    _cleanup_poetry_files()

    _log('')
    _log('Migration complete!')
    _log('')
    _log('Next steps:')
    _log('  1. Run: uv lock')
    _log('  2. Run: uv sync --all-extras')
    _log('  3. Test: ./run main')
    _log('  4. Review changes and commit')
    _log('')

    _delete_myself()


if __name__ == '__main__':
    main()
