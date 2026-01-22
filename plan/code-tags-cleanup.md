# Code Tags Cleanup

## Current Tags (from CODE_TAG_SUMMARY.md)

### FIXME (2) - Port to Corallium

| Location                                | Description                                            | Action               |
| --------------------------------------- | ------------------------------------------------------ | -------------------- |
| `calcipy/_corallium/file_helpers.py:60` | `get_tool_versions()` extended for mise.lock/mise.toml | Port to ../corallium |
| `calcipy/_corallium/file_helpers.py:85` | `read_package_name()` extended for uv `[project]`      | Port to ../corallium |

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

### 1. Port to Corallium (High Priority)

The `calcipy/_corallium/file_helpers.py` contains extensions that should be upstreamed to corallium.

**Target file:** `../corallium/corallium/file_helpers.py`

**Changes needed in corallium:**

1. Add `_parse_mise_lock()` function (lines 13-33)
1. Add `_parse_mise_toml()` function (lines 36-57)
1. Update `get_tool_versions()` to check mise.lock > mise.toml > .tool-versions (lines 61-82)
1. Update `read_package_name()` to check `[project]` before `[tool.poetry]` (already done in corallium:143-144)

**After porting:**

- Remove `calcipy/_corallium/file_helpers.py` overrides
- Update imports in calcipy to use corallium directly
- Bump corallium version requirement

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

- [ ] Create branch in ../corallium
- [ ] Port mise.lock parsing
- [ ] Port mise.toml parsing
- [ ] Update get_tool_versions() priority order
- [ ] Add tests for new functionality
- [ ] Release corallium
- [ ] Update calcipy to use new corallium version
- [ ] Remove calcipy/\_corallium/file_helpers.py overrides
