# Code Tags Cleanup

## Current Tags (from CODE_TAG_SUMMARY.md)

### FIXME (2) - Port to Corallium [DONE]

| Location                                | Description                                            | Status   |
| --------------------------------------- | ------------------------------------------------------ | -------- |
| `calcipy/_corallium/file_helpers.py:60` | `get_tool_versions()` extended for mise.lock/mise.toml | RESOLVED |
| `calcipy/_corallium/file_helpers.py:85` | `read_package_name()` extended for uv `[project]`      | RESOLVED |

Changes ported to `../corallium/corallium/file_helpers.py`. The `calcipy/_corallium/` directory has been deleted.

### TODO (1)

| Location                   | Description                             | Action                   |
| -------------------------- | --------------------------------------- | ------------------------ |
| `calcipy/tasks/lint.py:33` | Support `./src/<>/` and `./<>/` layouts | Implement path detection |

### PLANNED (4)

| Location             | Description                            | Priority |
| -------------------- | -------------------------------------- | -------- |
| `pyproject.toml:195` | Finish updating docstrings for Returns | Low      |
| `calcipy/cli.py:103` | Support completions                    | Medium   |
| `calcipy/cli.py:112` | usage.jdx.dev spec for completions     | Medium   |
| `calcipy/cli.py:114` | Ruff-style shell autocompletion        | Medium   |

## Action Items

### 1. Port to Corallium (High Priority) [COMPLETED]

The `calcipy/_corallium/file_helpers.py` extensions have been upstreamed to corallium.

**Changes made in `../corallium/corallium/file_helpers.py`:**

1. Added `_parse_mise_lock()` function
1. Added `_parse_mise_toml()` function
1. Added `_parse_tool_versions()` helper function
1. Updated `get_tool_versions()` to check mise.lock > mise.toml > .tool-versions
1. `read_package_name()` already supports `[project]` before `[tool.poetry]`

**Completed:**

- Deleted `calcipy/_corallium/` directory
- Updated imports in `calcipy/tasks/{lint,test}.py` and `calcipy/noxfile/_noxfile.py`
- Added `[tool.uv.sources]` override for local development
- All 77 calcipy tests pass

### 2. Lint Path Detection (Medium Priority)

`calcipy/tasks/lint.py:33` - Support both layouts:

- `./src/<package>/` (src layout)
- `./<package>/` (flat layout)

Options:

- Read from pyproject.toml `[tool.uv]` or heuristic detection
- Check which path exists at runtime

### 3. CLI Completions (Low Priority)

Three related PLANNED items for shell completions:

- Basic completion support
- usage.jdx.dev spec integration
- Ruff-style completion generation

Defer until CLI architecture stabilizes (see tooling-refactor.md).

### 4. Docstring Cleanup (Low Priority)

Review pyproject.toml PLANNED item for docstring Returns formatting.

## Corallium Sync Checklist

- [x] Create branch in ../corallium
- [x] Port mise.lock parsing
- [x] Port mise.toml parsing
- [x] Update get_tool_versions() priority order
- [x] Add tests for new functionality
- [ ] Release corallium (pending)
- [x] Update calcipy to use new corallium version (via local editable install)
- [x] Remove calcipy/\_corallium/file_helpers.py overrides

Note: calcipy pyproject.toml has `[tool.uv.sources]` pointing to local corallium. Once corallium is released, remove the source override and update version requirement.
