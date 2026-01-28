# Mise Migration Plan for Calcipy Tasks

## Overview

This document outlines the migration strategy for converting calcipy invoke tasks to mise tasks where appropriate.

## Task Inventory

| Task Name                        | Shell Command                                          | Miseable | Notes                                             |
| -------------------------------- | ------------------------------------------------------ | -------- | ------------------------------------------------- |
| **pack.lock**                    | `uv lock`                                              | Y        | Simple, no args                                   |
| **pack.bump_tag**                | Python: griffe API analysis                            | N        | Complex semver logic                              |
| **pack.sync_pyproject_versions** | Python: parse lock, update pyproject                   | N        | File manipulation                                 |
| **tags.collect_code_tags**       | Python: regex parse, markdown gen                      | N        | Code analysis                                     |
| **lint.check**                   | `python -m ruff check <target>`                        | Y        | Supports file args                                |
| **lint.fix**                     | `python -m ruff check --fix [--unsafe-fixes] <target>` | Y        | Optional flag                                     |
| **lint.watch**                   | `python -m ruff check --watch <target>`                | Y        | Simple                                            |
| **lint.pre_commit**              | `prek install && prek autoupdate && prek run ...`      | Y        | Multi-command chain                               |
| **doc.build**                    | Python preprocessing + `mkdocs build`                  | N        | Requires `write_template_formatted_md_sections()` |
| **doc.watch**                    | `python -m mkdocs serve --dirtyreload`                 | Y        | Simple                                            |
| **doc.deploy**                   | `prek uninstall; mkdocs gh-deploy; prek install`       | Y        | Multi-command                                     |
| **cl.write**                     | `cz changelog` + file move                             | N        | Post-command file ops                             |
| **cl.bump**                      | `cz bump && git push && gh release`                    | Y        | Chain, optional suffix                            |
| **nox.noxfile**                  | `python -m nox [--session <s>]`                        | Y        | Optional arg                                      |
| **test.check**                   | Python: AST parse for duplicates                       | N        | Code analysis                                     |
| **test.pytest**                  | `python -m pytest ./tests --cov=<pkg> ...`             | Y        | Many optional args                                |
| **test.watch**                   | `ptw . --now ./tests ...`                              | Y        | Optional filters                                  |
| **test.coverage**                | `coverage run && report && html && json`               | Y        | Multi-command                                     |
| **types.pyright**                | `pyright`                                              | Y        | No args                                           |
| **types.mypy**                   | `python -m mypy`                                       | Y        | No args                                           |

**Summary:** 14 tasks miseable, 6 require Python/calcipy

## Mise Usage Syntax Reference

### Argument Types

| Type                | Syntax                                     | Description                 |
| ------------------- | ------------------------------------------ | --------------------------- |
| Required positional | `arg "<name>"`                             | Must be provided            |
| Optional positional | `arg "[name]"`                             | Can be omitted              |
| Variadic            | `arg "<name>" var=#true`                   | Captures all remaining args |
| Flag (boolean)      | `flag "-s --long"`                         | True if present             |
| Option (with value) | `flag "-o --option <value>"`               | Requires value              |
| Default value       | `arg "<name>" default="value"`             | Fallback if not provided    |
| Choices             | `flag "-t --type <t>" { choices "a" "b" }` | Constrained values          |

### Variable Reference in `run`

| Pattern                  | Meaning                           |
| ------------------------ | --------------------------------- |
| `${usage_name}`          | Raw value (empty string if unset) |
| `${usage_name?}`         | Value or error if unset           |
| `${usage_name:-default}` | Value or default if unset         |

### Argument Passing Behavior

| Scenario                | Args Passed To        |
| ----------------------- | --------------------- |
| Single command          | That command          |
| Multiple `run` commands | **Last command only** |
| `depends` tasks         | **Not forwarded**     |
| `pre`/`post` tasks      | **Not forwarded**     |
| Explicit `:::`          | Each task separately  |

### Examples

```toml
# Simple command, no args
[tasks.lock]
description = "Update uv lock file"
run = "uv lock"

# Optional flag
[tasks."lint:fix"]
description = "Run ruff with fixes"
usage = 'flag "-u --unsafe" help="Apply unsafe fixes"'
run = '''
#!/usr/bin/env bash
unsafe_flag=""
if [ "${usage_unsafe:-false}" = "true" ]; then
  unsafe_flag="--unsafe-fixes"
fi
uv run ruff check --fix $unsafe_flag "./src/calcipy" ./tests
'''

# Variadic passthrough
[tasks.ruff]
description = "Run ruff with arbitrary args"
usage = 'arg "[args]" var=#true help="Arguments passed to ruff"'
run = "uv run ruff ${usage_args?}"

# Optional value with default
[tasks.nox]
description = "Run nox sessions"
usage = 'flag "-s --session <session>" help="Specific session to run"'
run = '''
#!/usr/bin/env bash
session_arg=""
if [ -n "${usage_session:-}" ]; then
  session_arg="--session ${usage_session}"
fi
uv run nox --error-on-missing-interpreters $session_arg
'''

# Multiple flags and args
[tasks.pytest]
description = "Run pytest with options"
usage = '''
flag "-k --keyword <kw>" help="Filter by keyword expression"
flag "-m --marker <marker>" help="Filter by marker"
flag "--min-cover <n>" help="Minimum coverage threshold"
'''
run = '''
#!/usr/bin/env bash
args=""
[ -n "${usage_keyword:-}" ] && args="$args -k \"${usage_keyword}\""
[ -n "${usage_marker:-}" ] && args="$args -m \"${usage_marker}\""
[ -n "${usage_min_cover:-}" ] && args="$args --cov-fail-under=${usage_min_cover}"
uv run pytest ./tests --cov=calcipy --cov-branch --cov-report=term-missing $args
'''
```

## Migration Strategy

### Phase 1: Direct Mise Tasks (Simple Commands)

Tasks that are pure shell commands with no Python preprocessing:

```toml
[tasks.lock]
run = "uv lock"

[tasks."types:pyright"]
run = "pyright"

[tasks."types:mypy"]
run = "uv run mypy"

[tasks."doc:watch"]
run = "uv run mkdocs serve --dirtyreload"
```

### Phase 2: Mise Calling Calcipy (Complex Tasks)

Tasks requiring Python logic should be called via calcipy:

```toml
[tasks."tags:collect"]
description = "Collect code tags (via calcipy)"
usage = 'arg "[args]" var=#true'
run = "uv run calcipy tags.collect-code-tags ${usage_args:-}"

[tasks."doc:build"]
description = "Build docs (via calcipy)"
run = "uv run calcipy doc.build"

[tasks."pack:bump-tag"]
description = "Bump git tag using griffe (via calcipy)"
usage = '''
flag "-t --tag <tag>" help="Current tag"
flag "-p --prefix <prefix>" help="Tag prefix"
'''
run = "uv run calcipy pack.bump-tag --tag=${usage_tag?} --tag-prefix=${usage_prefix:-}"
```

### Phase 3: Hybrid Tasks with Dependencies

For tasks with pre/post requirements, flatten the chain in mise:

```toml
# Instead of relying on calcipy's pre=[write] for bump
[tasks."cl:bump"]
description = "Write changelog and bump version"
usage = 'flag "-s --suffix <suffix>" help="Prerelease suffix (alpha, beta, rc)"'
run = '''
#!/usr/bin/env bash
set -euo pipefail
# Pre-task: write changelog
uv run cz changelog
mv CHANGELOG.md docs/

# Main task: bump
suffix_arg=""
[ -n "${usage_suffix:-}" ] && suffix_arg="--prerelease=${usage_suffix}"
uv run cz bump $suffix_arg --annotated-tag --no-verify --gpg-sign
git push origin --tags --no-verify
gh release create --generate-notes "$(git tag --list --sort=-creatordate | head -n 1)" ${usage_suffix:+--prerelease}
'''
```

## Command Examples

```sh
# Run with no args
mise run lock
mise run types:pyright

# Run with flags
mise run lint:fix --unsafe
mise run nox --session=tests

# Run with variadic args
mise run ruff check --fix ./src

# Run multiple tasks
mise run lint:check ::: types:pyright

# Pass args after --
mise run -- pytest -k "test_foo"
```

## Considerations

### Keep in Calcipy (N)

1. **pack.bump_tag** - griffe API for semver analysis
1. **pack.sync_pyproject_versions** - parses uv.lock, modifies pyproject.toml
1. **tags.collect_code_tags** - regex code parsing, markdown generation
1. **doc.build** - `write_template_formatted_md_sections()` preprocessing
1. **cl.write** - file move after cz changelog (could be mise but has edge cases)
1. **test.check** - AST parsing for duplicate test detection

### Migrate to Mise (Y)

All other tasks are straightforward shell commands or chains that mise can handle directly.

### Hybrid Approach

For consistency, consider having mise as the sole entry point:

```sh
mise run <task>          # All tasks go through mise
mise run tags:collect    # Mise calls calcipy internally for complex tasks
mise run lint:check      # Mise runs shell directly for simple tasks
```

This provides a unified interface while keeping complex logic in Python.
