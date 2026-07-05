# Replace Nox with uv Multi-Version Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the nox-based multi-Python test runner with a `test.multi` calcipy task that uses `uv run --python` directly, eliminating the `noxfile.py` boilerplate from every downstream project.

**Architecture:** A new `multi` task in `calcipy/tasks/test.py` reads Python versions from `get_tool_versions()` (already used by the noxfile) and runs `uv run --python {ver} pytest ./tests` for each, using `UV_PROJECT_ENVIRONMENT=.uv-tests/py{ver}` to maintain per-version persistent envs (mirroring nox's `reuse_venv=True`). The `nox.py` task is soft-deprecated but kept for one-off use. The template's `noxfile.py` boilerplate is removed.

**Tech Stack:** Python, uv, invoke, corallium (`get_tool_versions`), pytest

---

## File Map

| File                                           | Action | Responsibility                                            |
| ---------------------------------------------- | ------ | --------------------------------------------------------- |
| `calcipy/tasks/test.py`                        | Modify | Add `multi` task                                          |
| `calcipy/tasks/nox.py`                         | Modify | Add deprecation note in docstring                         |
| `calcipy/tasks/all_tasks.py`                   | Modify | Replace `nox.noxfile` with `test.multi` in `_OTHER_TASKS` |
| `tests/tasks/test_test.py`                     | Modify | Add tests for `multi`                                     |
| `calcipy/noxfile/_noxfile.py`                  | Modify | Add deprecation note                                      |
| `calcipy_template/package_template/noxfile.py` | Delete | No longer needed                                          |
| `calcipy_template/.ctt/default/noxfile.py`     | Delete | No longer needed                                          |
| `pyproject.toml`                               | Modify | Remove `nox` from `recommended` optional-dependency       |
| `.gitignore`                                   | Modify | Add `.uv-tests/`                                          |
| `docs/README.md`                               | Modify | Replace nox usage with `calcipy test.multi`               |

---

### Task 1: Add `test.multi` task

**Files:**

- Modify: `calcipy/tasks/test.py`
- Test: `tests/tasks/test_test.py`

Background: `get_tool_versions()` is from `corallium.file_helpers` and returns a dict like `{'python': ['3.10.11', '3.13.11']}`. The version strings are full semver (e.g. `3.13.11`). `uv run --python 3.13.11` accepts this. The env directory slug strips the patch so `3.13.11` → `py3.13` for a stable cache path across patch upgrades.

The `run(ctx, cmd, **kwargs)` helper (in `calcipy/invoke_helpers.py`) passes all kwargs through to `ctx.run()`, so passing `env=` works as-is.

- [ ] **Step 1: Write the failing test**

In `tests/tasks/test_test.py`, add at the top of the parametrize list and add a standalone test (because `get_tool_versions` needs mocking — easier as its own test than in the parametrize fixture):

```python
from unittest.mock import call, patch
```

Merge `multi` into the existing import line (do not add a third `from calcipy.tasks.test import ...` line):

```python
# Before (line 6):
from calcipy.tasks.test import check, coverage, watch

# After:
from calcipy.tasks.test import check, coverage, multi, watch
```

Then add a new test function after the existing `test_test_with_min_cover`:

```python
def test_multi(ctx):
    versions = ['3.10.11', '3.13.11']
    with patch('calcipy.tasks.test.get_tool_versions', return_value={'python': versions}):
        multi(ctx)

    ctx.run.assert_has_calls(
        [
            call('uv run --python 3.10.11 pytest ./tests', env={'UV_PROJECT_ENVIRONMENT': '.uv-tests/py3.10'}),
            call('uv run --python 3.13.11 pytest ./tests', env={'UV_PROJECT_ENVIRONMENT': '.uv-tests/py3.13'}),
        ]
    )
```

- [ ] **Step 2: Run test to verify it fails**

```sh
uv run pytest tests/tasks/test_test.py::test_multi -v
```

Expected: `ImportError` or `AttributeError` — `multi` does not exist yet.

- [ ] **Step 3: Implement `multi` in `calcipy/tasks/test.py`**

Add import at the top of `calcipy/tasks/test.py` (with existing imports):

```python
from corallium.file_helpers import get_tool_versions
```

Add task after the `watch` task and before `coverage`:

```python
@task()
def multi(ctx: Context) -> None:
    """Run pytest against all configured Python versions using uv."""
    for ver in dict.fromkeys(get_tool_versions()['python']):
        major_minor = '.'.join(str(ver).split('.')[:2])
        run(ctx, f'uv run --python {ver} pytest ./tests', env={'UV_PROJECT_ENVIRONMENT': f'.uv-tests/py{major_minor}'})
```

Note: `dict.fromkeys()` deduplicates while preserving order, matching the noxfile's set-dedup behavior.

- [ ] **Step 4: Run test to verify it passes**

```sh
uv run pytest tests/tasks/test_test.py::test_multi -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite to check for regressions**

```sh
uv run pytest tests/tasks/test_test.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```sh
git add calcipy/tasks/test.py tests/tasks/test_test.py
git commit -m "feat: add test.multi task for uv-based multi-python testing"
```

---

### Task 2: Wire `test.multi` into `all_tasks.py`

**Files:**

- Modify: `calcipy/tasks/all_tasks.py`
- Test: `tests/tasks/test_all_tasks.py`

Background: `_OTHER_TASKS` currently contains `nox.noxfile.with_kwargs(session='tests')`. This should become `test.multi`. The `test_all_tasks.py` test only checks that `main` and `other` run without error (commands list is empty) so no test change is needed — but verify it still passes.

- [ ] **Step 1: Update `_OTHER_TASKS` in `calcipy/tasks/all_tasks.py`**

```python
# Before:
_OTHER_TASKS = [
    lint.pre_commit.with_kwargs(no_update=True),  # pyright: ignore[reportFunctionMemberAccess]
    nox.noxfile.with_kwargs(session='tests'),  # pyright: ignore[reportFunctionMemberAccess]
    pack.lock,
    tags.collect_code_tags,
    test.check,  # Expected to fail for calcipy
]

# After:
_OTHER_TASKS = [
    lint.pre_commit.with_kwargs(no_update=True),  # pyright: ignore[reportFunctionMemberAccess]
    pack.lock,
    tags.collect_code_tags,
    test.check,  # Expected to fail for calcipy
    test.multi,
]
```

Also remove the `nox` import from the import line at the top if `nox` is no longer referenced:

```python
# Before:
from . import cl, doc, lint, nox, pack, tags, test, types

# After:
from . import cl, doc, lint, pack, tags, test, types
```

- [ ] **Step 2: Run tests to verify nothing broke**

```sh
uv run pytest tests/tasks/test_all_tasks.py tests/tasks/test_nox.py -v
```

Expected: all PASS (`test_nox.py` tests `nox.py` directly and doesn't depend on `all_tasks.py`)

- [ ] **Step 3: Commit**

```sh
git add calcipy/tasks/all_tasks.py
git commit -m "refactor: replace nox.noxfile with test.multi in other task pipeline"
```

---

### Task 3: Deprecate `calcipy/tasks/nox.py` and `calcipy/noxfile/`

**Files:**

- Modify: `calcipy/tasks/nox.py`
- Modify: `calcipy/noxfile/_noxfile.py`

Background: Both are kept for backward compatibility — existing projects using `from calcipy.noxfile import tests` or calling `calcipy nox` will continue to work. A deprecation note in the docstring is sufficient; no runtime warning is needed since we're not breaking anything yet.

- [ ] **Step 1: Add deprecation note to `calcipy/tasks/nox.py`**

```python
# Before:
"""Nox CLI."""

# After:
"""Nox CLI.

Deprecated: Use `calcipy test.multi` instead, which runs pytest across all
configured Python versions via `uv run --python` without requiring nox.
"""
```

- [ ] **Step 2: Add deprecation note to `calcipy/noxfile/_noxfile.py`**

At the top of the module docstring:

```python
"""nox with uv backend configuration.

Deprecated: New projects should use `calcipy test.multi` instead.
This module is retained for projects that still have a noxfile.py.
...
```

- [ ] **Step 3: Verify tests still pass**

```sh
uv run pytest tests/tasks/test_nox.py tests/noxfile/ -v
```

Expected: all PASS

- [ ] **Step 4: Commit**

```sh
git add calcipy/tasks/nox.py calcipy/noxfile/_noxfile.py
git commit -m "deprecate: mark nox task and noxfile module as superseded by test.multi"
```

---

### Task 4: Update `pyproject.toml` and `.gitignore`

**Files:**

- Modify: `pyproject.toml`
- Modify: `.gitignore`

Background: The `nox` extra (`nox >=2025.11.12`) is removed from `recommended` since new projects won't need it. The `nox` extra itself stays so existing users pinning `calcipy[nox]` aren't broken. `.uv-tests/` needs to be git-ignored since `test.multi` creates per-version envs there.

- [ ] **Step 1: Remove `nox` from `recommended` in `pyproject.toml`**

```toml
# Before:
recommended = [
  "calcipy[doc,lint,nox,tags,test,types]",
]

# After:
recommended = [
  "calcipy[doc,lint,tags,test,types]",
]
```

- [ ] **Step 2: Add `.uv-tests/` to `.gitignore`**

Find the existing `.gitignore` and add `.uv-tests/` near other virtual-env entries (e.g. near `.venv/` or `.nox/`).

- [ ] **Step 3: Verify the project still installs cleanly**

```sh
uv sync
```

Expected: no errors

- [ ] **Step 4: Commit**

```sh
git add pyproject.toml .gitignore
git commit -m "chore: remove nox from recommended extra, ignore .uv-tests/"
```

---

### Task 5: Update `calcipy_template` (separate repo)

**Files (in `../calcipy_template/`):**

- Delete: `package_template/noxfile.py`
- Delete: `.ctt/default/noxfile.py`

Background: Every project generated from the template has a `noxfile.py` with just three lines importing from calcipy. Once `test.multi` is the standard, those files are dead weight. The template is a separate repo — this task is a follow-up change there, not in calcipy itself.

- [ ] **Step 1: Check for other references to `noxfile.py` in the template repo**

```sh
grep -r "noxfile" ../calcipy_template/ --include="*.py" --include="*.toml" --include="*.yml" --include="*.yaml" -l
```

Expected: only the two noxfile.py files themselves. If other files reference them, update those first.

- [ ] **Step 2: Delete both noxfile templates**

```sh
rm ../calcipy_template/package_template/noxfile.py
rm ../calcipy_template/.ctt/default/noxfile.py
```

- [ ] **Step 2: Verify the template still renders correctly with ctt**

```sh
cd ../calcipy_template && uv run ctt
```

Expected: no errors referencing missing noxfile

- [ ] **Step 3: Commit (in calcipy_template repo)**

```sh
git add -A
git commit -m "feat: remove noxfile.py - use calcipy test.multi instead"
```

---

### Task 6: Update `docs/README.md`

**Files:**

- Modify: `docs/README.md`

- [ ] **Step 1: Replace nox references with `test.multi`**

Find any documentation referring to `nox -s tests` or `calcipy nox` and update to:

```sh
# Run tests across all configured Python versions
calcipy test.multi

# Or directly with uv
uv run --python 3.13 pytest ./tests
```

- [ ] **Step 2: Commit**

```sh
git add docs/README.md
git commit -m "docs: replace nox instructions with test.multi / uv run pattern"
```
