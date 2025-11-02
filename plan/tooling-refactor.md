# Tooling Refactor Based on Ideas

## Overview

The `ideas.txt` file contains proposals to refactor the tooling architecture, moving components to templates and simplifying calcipy's scope.

## Current Status

Ideas from `ideas.txt`:

- Move noxfile import to calcipy-template instead of calcipy
- Move most CLI functionality to `mise.toml` (distributed with copier-template)
- Keep only first-party tooling in calcipy (wrappers around flake8, etc.)

## Proposed Mini-Project

Implement the architectural changes:

1. **NOX Template Migration**: Move noxfile logic to calcipy-template, make calcipy's noxfile a minimal wrapper
1. **CLI to Mise**: Migrate CLI commands from calcipy scripts to mise.toml tasks
1. **Scope Reduction**: Identify and move third-party tool wrappers to templates, keep only calcipy-specific functionality
1. **Template Updates**: Update copier-answers and template files to support new structure
1. **Documentation**: Update docs to reflect new tooling boundaries

## Benefits

- Clearer separation of concerns between calcipy (library) and calcipy-template (project setup)
- Better maintainability with mise handling project-level tasks
- Reduced complexity in calcipy core
- Easier adoption and customization for users

## Estimated Effort

High (2-3 weeks): Architecture changes, template updates, testing, migration guides
