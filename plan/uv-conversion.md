# UV Conversion Completion

## Overview

The repository has been partially converted from Poetry to UV, with `uv.lock` present and `[tool.uv]` configured in `pyproject.toml`. However, there are remaining TODOs indicating incomplete migration.

## Current Status

- `pyproject.toml` uses Hatchling build system (not Poetry)
- UV lockfile exists (`uv.lock`)
- UV dev dependencies configured
- TODO in `pyproject.toml`: "Sync with https://github.com/pawamoy/copier-uv"
- TODO in `calcipy/noxfile/_noxfile.py`: "Migrate to uv"

## Proposed Mini-Project

Complete the UV migration by:

1. Reviewing and syncing `pyproject.toml` with the copier-uv template
1. Migrating noxfile configurations to use UV instead of virtualenv
1. Updating CI workflows to use UV commands
1. Removing any remaining Poetry references
1. Testing the full UV workflow (install, dev install, lock updates)

## Benefits

- Faster dependency resolution and installation
- Better Python version management integration with mise
- Simplified tooling stack
- Alignment with modern Python packaging practices

## Estimated Effort

Medium (2-3 days): Configuration updates, testing, CI changes
