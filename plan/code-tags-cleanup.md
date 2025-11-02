# Code Tags Cleanup

## Overview

The codebase contains several TODO and FIXME tags that need to be addressed. The project has tooling to collect and track these via `CODE_TAG_SUMMARY.md`.

## Current Status

Active TODOs (6 total):

- `pyproject.toml:1`: Sync with copier-uv template
- `calcipy/collection.py:50`: How to capture output?
- `calcipy/experiments/sync_package_dependencies.py:52`: Handle ">=3.0.0,\<4" version constraints
- `calcipy/noxfile/_noxfile.py:55`: Migrate to uv
- `calcipy/tasks/pack.py:77`: Add unit test for pack functionality
- `calcipy/tasks/pack.py:110`: Add unit test for pack functionality

PLANNED items (4 total) in docstrings.

## Proposed Mini-Project

Systematically address each TODO:

1. **Copier-UV Sync**: Research and implement changes from pawamoy/copier-uv
1. **Output Capture**: Implement proper output capturing in collection.py
1. **Version Constraints**: Add support for complex version ranges in sync_package_dependencies.py
1. **NOX UV Migration**: Complete UV integration in noxfile
1. **Unit Tests**: Add comprehensive tests for pack.py functions
1. **PLANNED Items**: Convert PLANNED docstring items to implemented features or remove if obsolete

## Benefits

- Cleaner codebase with resolved technical debt
- Improved functionality (output capture, version handling)
- Better test coverage
- Alignment with project goals

## Estimated Effort

Medium-High (1-2 weeks): Research, implementation, testing for each TODO
