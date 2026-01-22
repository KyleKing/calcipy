# Tooling Refactor: Mise to Replace NOX

## Overview

Migrate from NOX-based multi-Python testing to mise tasks. Calcipy should become a thin library while project-level tooling moves to calcipy-template.

## Current State

### Mise (mise.toml)

Already configured with:

- `test`, `test:310`, `test:311`, `test:312` tasks
- `test:all` and `test:all-verbose` for multi-version testing
- Python versions defined in `[tools]` section
- Uses `uv run --group ci pytest tests/`

### NOX (calcipy/noxfile/)

- `_noxfile.py`: Single `tests` session using uv backend
- Reads Python versions from mise.lock/mise.toml/.tool-versions
- Installed via `calcipy[nox]` extra

### Root noxfile.py

```python
from calcipy.noxfile import tests
```

## Migration Path

### Phase 1: Validate Mise Parity

- [ ] Confirm mise tasks match nox session behavior
- [ ] Test `mise run test:all` across Python versions
- [ ] Verify CI can use mise instead of nox

### Phase 2: Move NOX to Template

- [ ] Add noxfile.py to calcipy-template (for projects that prefer nox)
- [ ] Make calcipy's noxfile a deprecated optional import
- [ ] Document mise as the recommended approach

### Phase 3: CLI to Mise

Per ideas.txt:

- [ ] Identify CLI commands that are wrappers (lint, test, docs)
- [ ] Add equivalent mise tasks to calcipy-template
- [ ] Keep only first-party tooling in calcipy (code_tag_collector, custom validators)

### Phase 4: Scope Reduction

- [ ] Audit calcipy modules: which are library vs tooling?
- [ ] Move tooling modules to template-distributed mise tasks
- [ ] Update documentation boundaries

## Key Differences: NOX vs Mise

| Feature     | NOX                      | Mise                                          |
| ----------- | ------------------------ | --------------------------------------------- |
| Isolation   | Creates venv per session | Uses specified Python version                 |
| Parallelism | `-j` flag                | `depends` for sequential, parallel by default |
| Reuse       | `reuse_venv=True`        | Inherent (no venv creation)                   |
| Discovery   | Programmatic via calcipy | Declarative in mise.toml                      |

## Benefits

- Simpler tooling stack (mise replaces asdf + nox)
- Faster execution (no venv creation overhead)
- Template-distributed configuration (users customize mise.toml)
- Reduced calcipy surface area

## Open Questions

1. Should calcipy retain a minimal noxfile module for backwards compatibility?
1. How to handle projects that need custom pytest configuration per Python version?
1. Timeline for deprecating `calcipy[nox]` extra?
