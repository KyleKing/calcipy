# Provide Multiple CLI Entry Points

* Status: accepted
* Date: 2021-08-15 (backfilled 2024-11-20)
* Deciders: KyleKing
* Informed: calcipy users

## Context and Problem Statement

calcipy provides task automation for Python projects, organized into functional areas:

* Linting (ruff, pre-commit)
* Type checking (mypy, pyright)
* Testing (pytest)
* Documentation (mkdocs)
* Packaging (build, publish)
* Code tags (TODO/FIXME collection)

Users install calcipy in different ways:

1. As a project dependency (for project-specific tasks)
2. As a global tool via `uv tool install` (for cross-project usage)
3. Both project and global (for flexibility)

When installed as a global tool, users want to run specific functionality without loading unnecessary dependencies. For example, `calcipy-tags` only needs a few dependencies (arrow, pyyaml) compared to the full calcipy with all extras.

How should we structure CLI entry points to support both project-based and global tool usage patterns while minimizing dependency overhead?

## Decision Drivers

* Must support both project and global installation patterns
* Must allow running specific functionality without loading everything
* Must enable installing only required dependencies for specific use cases
* Must provide clear, discoverable CLI commands
* Must maintain backward compatibility
* Should minimize startup time when possible
* Should follow Python packaging best practices

## Considered Options

* **Multiple specialized entry points** - Separate commands per functional area (calcipy-lint, calcipy-test, etc.)
* **Single entry point with subcommands** - One `calcipy` command with all functionality
* **Hybrid approach** - Main command plus specialized entry points
* **Plugin architecture** - Dynamic loading of functionality

## Decision Outcome

Chosen option: "Multiple specialized entry points", because it enables users to install and use only the functionality they need, particularly important for global tool installation where dependency minimization matters.

We provide seven entry points:

* `calcipy` - Main command with all tasks
* `calcipy-docs` - Documentation tasks (mkdocs)
* `calcipy-lint` - Linting tasks (ruff, pre-commit)
* `calcipy-pack` - Packaging tasks (build, publish)
* `calcipy-tags` - Code tag collection
* `calcipy-test` - Testing tasks (pytest)
* `calcipy-types` - Type checking tasks (mypy, pyright)

Each entry point loads only its required dependencies through optional extras in pyproject.toml.

### Consequences

* Good, because users can install only needed functionality (`uv tool install 'calcipy[tags]'`)
* Good, because minimal dependencies for specific use cases
* Good, because faster startup for specialized commands (less to import)
* Good, because clear command naming (calcipy-lint for linting)
* Good, because backward compatible (calcipy still works for everything)
* Good, because follows pattern of other tools (git-*, cargo-*)
* Good, because enables cross-project tool usage
* Bad, because more entry points to maintain
* Bad, because potential confusion about which command to use
* Bad, because namespace pollution (`calcipy-*` commands)
* Neutral, because requires documentation of which command for what
* Neutral, because more complex package configuration

## Pros and Cons of the Options

### Multiple Specialized Entry Points

* Good, because minimal dependencies per command
* Good, because faster startup for specific functionality
* Good, because clear purpose per command
* Good, because enables partial installation
* Good, because supports both project and global usage
* Bad, because more entry points to maintain
* Bad, because potential namespace pollution
* Bad, because requires decision about which command to use
* Neutral, because more package configuration

### Single Entry Point with Subcommands

* Good, because single command to remember
* Good, because simpler package configuration
* Good, because no namespace pollution
* Bad, because must load all dependencies even for simple tasks
* Bad, because slower startup (everything imports)
* Bad, because can't install just one functional area
* Bad, because poor fit for global tool installation

### Hybrid Approach

* Good, because flexibility (both patterns available)
* Good, because backward compatibility
* Neutral, because balances trade-offs
* Bad, because most complex to maintain
* Bad, because unclear which approach to use when

### Plugin Architecture

* Good, because very flexible
* Good, because clean separation
* Good, because extensible by users
* Bad, because complex implementation
* Bad, because discovery mechanism needed
* Bad, because slower due to dynamic loading
* Bad, because overkill for our needs

## Validation

This decision was validated through:

* Successful usage of `calcipy-tags` as global tool
* Positive feedback on specialized commands
* Reduced dependency installation for specific use cases
* No reported confusion about command selection
* Backward compatibility maintained (calcipy still works)

We would revisit this decision if:

* Maintenance burden becomes too high
* User confusion about command selection increases
* Python gains better plugin/entry point mechanisms
* Dependency management makes this optimization unnecessary

## More Information

* Entry point configuration: `/pyproject.toml` under `[project.scripts]`
* Script implementations: `/calcipy/scripts.py`
* Optional dependencies: `/pyproject.toml` under `[project.optional-dependencies]`
* Usage documentation: `/docs/README.md` CLI section
