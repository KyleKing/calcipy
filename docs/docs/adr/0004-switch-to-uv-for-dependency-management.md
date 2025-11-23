# Switch to uv for Dependency Management

* Status: accepted
* Date: 2024-10-31
* Deciders: KyleKing
* Informed: calcipy users and contributors

## Context and Problem Statement

calcipy used Poetry for dependency management and packaging since its inception. Poetry provided:

* Unified dependency resolution
* Lock file for reproducible builds
* Publishing to PyPI
* Virtual environment management
* pyproject.toml-based configuration

However, Poetry had several pain points:

* Slow dependency resolution (minutes for complex projects)
* Slow installation compared to pip
* Occasional resolution failures requiring manual intervention
* Large dependency footprint (Poetry itself has many dependencies)
* Complex codebase making contributions difficult
* Unclear roadmap and governance

Meanwhile, uv emerged in 2024 as a new Rust-based Python package manager from Astral (creators of ruff). Early benchmarks showed 10-100x speed improvements over Poetry/pip.

Should we migrate from Poetry to uv for dependency management?

## Decision Drivers

* Must support pyproject.toml standards (PEP 621)
* Must provide lock files for reproducible builds
* Must support publishing to PyPI
* Must be fast (developers value quick iteration)
* Must be reliable (dependency resolution must work)
* Must support optional dependencies (calcipy has many extras)
* Must support Python 3.9+ (our minimum version)
* Prefer tools from Astral (already using ruff successfully)
* Prefer Rust-based tools for performance
* Must have active development and community support

## Considered Options

* **uv** - Extremely fast Python package manager and resolver
* **Poetry** - Current solution, established tool
* **PDM** - Modern Python package manager
* **pip-tools** - Minimalist approach using pip + requirements files
* **Pipenv** - Official PyPA package manager

## Decision Outcome

Chosen option: "uv", because it provides 10-100x faster dependency resolution and installation while maintaining compatibility with pyproject.toml standards. The migration was straightforward, and early experience showed significant quality-of-life improvements.

uv provides:

* Extremely fast dependency resolution (seconds vs. minutes)
* Fast package installation (Rust-based)
* Drop-in pip replacement with `uv pip`
* Lock file support with `uv lock`
* Tool management with `uv tool`
* Virtual environment management
* Publishing support
* pyproject.toml compatibility (PEP 621)
* Active development from Astral (ruff creators)
* Growing community adoption

The migration required updating CI/CD workflows and documentation but was completed successfully in PR #134.

### Consequences

* Good, because dependency resolution is 10-100x faster
* Good, because installation is significantly faster
* Good, because same team as ruff (proven track record)
* Good, because active development with frequent improvements
* Good, because simplified workflow (uv tool install, uv run, etc.)
* Good, because better integration with modern Python packaging standards
* Good, because can remove Poetry dependency
* Good, because uvx provides better tool isolation than pipx
* Bad, because newer tool (less mature than Poetry)
* Bad, because some Poetry-specific features may be missing
* Bad, because migration required updating all documentation and CI/CD
* Bad, because smaller community (though growing rapidly)
* Neutral, because different CLI commands require learning
* Neutral, because lock file format differs from poetry.lock

## Pros and Cons of the Options

### uv

* Good, because 10-100x faster than Poetry/pip
* Good, because written in Rust (performance and reliability)
* Good, because created by Astral (ruff team)
* Good, because active development (weekly releases)
* Good, because growing community adoption
* Good, because excellent tool management (uv tool)
* Good, because unified interface (uv pip, uv run, uv lock, etc.)
* Good, because better adherence to Python packaging standards
* Bad, because newer tool (released 2024)
* Bad, because smaller ecosystem than Poetry
* Bad, because some advanced Poetry features may be missing
* Neutral, because requires migration effort

### Poetry (Keep Current)

* Good, because established and mature
* Good, because large community and ecosystem
* Good, because comprehensive documentation
* Good, because known quantity (no migration risk)
* Bad, because slow dependency resolution
* Bad, because slow installation
* Bad, because occasional resolution failures
* Bad, because large dependency footprint
* Bad, because complex codebase
* Bad, because unclear governance and roadmap

### PDM

* Good, because modern and PEP 621 compliant
* Good, because faster than Poetry
* Good, because active development
* Bad, because slower than uv
* Bad, because smaller community than Poetry
* Bad, because still requires migration effort
* Neutral, because different ecosystem

### pip-tools

* Good, because minimal and simple
* Good, because uses standard pip
* Good, because widely understood
* Bad, because lacks integrated workflow
* Bad, because no pyproject.toml support for dependencies
* Bad, because manual lock file management
* Bad, because no publishing support
* Bad, because slower than uv

### Pipenv

* Good, because official PyPA project
* Good, because mature and stable
* Bad, because slow performance
* Bad, because development has slowed
* Bad, because community migrating to other tools
* Bad, because uses Pipfile instead of pyproject.toml
* Bad, because frequent resolution issues

## Validation

We will validate this decision through:

* Successful CI/CD builds with uv for 6 months
* Dependency resolution speed monitoring (should remain fast)
* Community feedback on installation experience
* Tracking uv development and stability

We will revisit this decision if:

* uv development slows or project becomes unmaintained
* Critical features are missing that Poetry provided
* Dependency resolution becomes unreliable
* Performance degrades significantly
* Python packaging ecosystem standardizes on different tool

## More Information

* Migration PR: #134
* uv documentation: https://docs.astral.sh/uv/
* Changelog entry: v4.2.0 "feat: switch to uv"
* Developer guide: `/docs/docs/DEVELOPER_GUIDE.md`
* pyproject.toml configuration: `/pyproject.toml`
