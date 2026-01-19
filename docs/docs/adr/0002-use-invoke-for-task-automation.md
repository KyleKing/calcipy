# Use Invoke for Task Automation

- Status: accepted
- Date: 2019-01-15 (backfilled 2024-11-20)
- Deciders: KyleKing
- Informed: calcipy users

## Context and Problem Statement

calcipy aims to provide a unified interface for common development tasks (linting, testing, documentation generation, publishing, etc.). The package needs a task automation framework that allows:

- Defining tasks in Python rather than shell scripts
- Organizing tasks into namespaces (lint.fix, test.watch, pack.publish, etc.)
- Accepting command-line arguments with type safety
- Composing tasks (calling other tasks from within a task)
- Providing help documentation automatically
- Working cross-platform (Windows, macOS, Linux)

The chosen solution must be stable, well-maintained, and familiar to Python developers.

## Decision Drivers

- Must support Python-based task definition (not shell-based like Make)
- Must provide argument parsing and help generation
- Must support task namespacing for organization
- Must work cross-platform without modification
- Prefer established, maintained tools over experimental ones
- Must integrate well with Python packaging ecosystem
- Should be familiar to Python developers (lower learning curve)

## Considered Options

- **Invoke** - Python task execution library inspired by Fabric
- **Make** - Traditional Unix build automation tool
- **Just** - Modern command runner written in Rust
- **Taskipy** - Simple task runner for Python projects
- **Poe the Poet** - Task runner for Python projects using pyproject.toml
- **Nox** - Python test automation tool (considered but better suited for test matrices)

## Decision Outcome

Chosen option: "Invoke", because it provides the most comprehensive Python-native task automation with excellent support for complex workflows, argument handling, and task composition.

Invoke offers:

- Pure Python task definition with decorators
- Rich argument parsing with type annotations
- Namespace organization (e.g., `lint.fix`, `test.watch`)
- Task composition and calling
- Automatic help generation from docstrings
- Cross-platform compatibility
- Stable, mature project with active maintenance
- Integration with Fabric for remote execution (future possibility)

### Consequences

- Good, because tasks are defined in Python with full access to the ecosystem
- Good, because namespace organization keeps related tasks grouped
- Good, because argument parsing is built-in with good defaults
- Good, because mature project (10+ years) reduces risk of abandonment
- Good, because familiar to many Python developers (from Fabric)
- Good, because task composition enables building complex workflows
- Bad, because adds invoke as a required dependency
- Bad, because invoke has slower release cycle (minor inconvenience)
- Bad, because some users may prefer simpler shell-based tools
- Neutral, because requires learning invoke API for task authors
- Neutral, because `invoke` command conflicts with system tools on some systems (mitigated with `./run` wrapper)

## Pros and Cons of the Options

### Invoke

- Good, because pure Python with access to full ecosystem
- Good, because excellent namespace organization
- Good, because mature and well-tested (10+ years)
- Good, because comprehensive argument parsing
- Good, because task composition support
- Good, because cross-platform by design
- Bad, because slower release cadence than newer tools
- Bad, because requires Python knowledge (not simple shell scripts)
- Neutral, because more complex than minimal task runners

### Make

- Good, because ubiquitous and familiar to many developers
- Good, because no additional dependencies
- Good, because simple for basic tasks
- Bad, because shell-based limits type safety
- Bad, because poor cross-platform support (Windows issues)
- Bad, because namespace organization is limited
- Bad, because argument passing is cumbersome
- Bad, because difficult to compose complex workflows

### Just

- Good, because modern with good ergonomics
- Good, because simpler syntax than Make
- Good, because better cross-platform support than Make
- Bad, because requires Rust installation
- Bad, because another language/tool to learn
- Bad, because less integration with Python ecosystem
- Bad, because newer tool with smaller community

### Taskipy

- Good, because simple and Python-based
- Good, because uses pyproject.toml (no extra files)
- Bad, because limited namespace support
- Bad, because minimal argument parsing
- Bad, because no task composition
- Bad, because too simple for calcipy's needs

### Poe the Poet

- Good, because uses pyproject.toml configuration
- Good, because growing community adoption
- Bad, because configuration-heavy rather than code-based
- Bad, because less flexible than programmatic approach
- Bad, because newer tool (less proven)

### Nox

- Good, because excellent for test matrices
- Good, because well-maintained by Python community
- Bad, because designed for testing, not general task automation
- Bad, because session-based model doesn't fit all use cases
- Neutral, because we do use nox for test matrices (complementary)

## Validation

This decision has been validated through:

- 5+ years of production use without major issues
- Successful support for complex workflows (linting, testing, publishing)
- Positive feedback from users on task organization
- Ability to evolve tasks without breaking changes

We would revisit this decision if:

- Invoke becomes unmaintained or deprecated
- Python gains native task runner in standard library
- A significantly better Python task framework emerges
- Cross-platform issues become problematic

## More Information

- Invoke documentation: https://www.pyinvoke.org/
- calcipy task definitions: `/calcipy/tasks/`
- Example usage: `/docs/docs/DEVELOPER_GUIDE.md`
