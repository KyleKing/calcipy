# Use Ruff for Linting and Formatting

- Status: accepted
- Date: 2023-03-15 (backfilled 2024-11-20)
- Deciders: KyleKing
- Informed: calcipy users

## Context and Problem Statement

calcipy bundles linting and code formatting tools to enforce code quality standards across projects. Historically, this required running multiple tools:

- flake8 for linting
- pylint for additional linting
- black for code formatting
- isort for import sorting
- pyupgrade for syntax modernization
- autoflake for removing unused imports

Each tool had its own configuration, ran independently, and required separate dependencies. The combined execution time was significant (30-60 seconds for medium projects), and configuration conflicts between tools were common.

How can we provide comprehensive linting and formatting while minimizing dependencies, execution time, and configuration complexity?

## Decision Drivers

- Must provide comprehensive linting coverage (equivalent to flake8 + pylint + others)
- Must support auto-fixing for common issues
- Must be fast (developers won't use slow tools)
- Must minimize dependency count (calcipy aims to be lightweight)
- Must have good configuration story (ideally in pyproject.toml)
- Must be actively maintained with regular updates
- Prefer Rust-based tools for performance (already proven with ripgrep, fd, etc.)
- Must support all rules needed for calcipy's strict quality standards

## Considered Options

- **Ruff** - Fast Python linter and formatter written in Rust
- **Flake8 + Black + isort** - Traditional combination of tools
- **Pylint + Black + isort** - More comprehensive linting
- **Flake8 + Pylint + Black + isort** - Maximum coverage
- **Pylama** - Meta-linter that wraps multiple tools

## Decision Outcome

Chosen option: "Ruff", because it consolidates multiple tools into one fast executable while providing equivalent or better linting coverage. The performance improvement (10-100x faster) and simplified configuration justify the switch from the traditional toolchain.

Ruff provides:

- All flake8 plugins (100+) in a single tool
- Import sorting (isort compatibility)
- Auto-fixing for hundreds of rules
- Pyupgrade and autoflake functionality built-in
- Extremely fast execution (written in Rust)
- Single configuration in pyproject.toml
- Active development and frequent releases
- Growing adoption in the Python community

We later removed pylint entirely (v4.1.0) after validating that ruff's coverage was sufficient.

### Consequences

- Good, because linting is 10-100x faster than previous toolchain
- Good, because single tool simplifies dependency management
- Good, because unified configuration in pyproject.toml
- Good, because auto-fixing is comprehensive and reliable
- Good, because active development with frequent rule additions
- Good, because growing community adoption reduces risk
- Good, because can remove black, isort, flake8, pylint, pyupgrade, autoflake dependencies
- Bad, because requires Rust toolchain for building from source (rare case)
- Bad, because some pylint rules not yet available (gap closing)
- Bad, because newer tool (less battle-tested than flake8/pylint)
- Neutral, because different rule codes require configuration migration
- Neutral, because some unique pylint patterns need refactoring

## Pros and Cons of the Options

### Ruff

- Good, because extremely fast (10-100x faster than flake8)
- Good, because consolidates 8+ tools into one
- Good, because comprehensive rule coverage (1000+ rules)
- Good, because excellent auto-fixing support
- Good, because single configuration location
- Good, because active development (weekly releases)
- Good, because reducing to single tool simplifies maintenance
- Bad, because newer tool (less mature than flake8/pylint)
- Bad, because some niche pylint rules not available
- Bad, because requires configuration migration

### Flake8 + Black + isort

- Good, because mature, well-tested tools
- Good, because widespread adoption
- Good, because stable APIs and configurations
- Bad, because slow execution (multiple processes)
- Bad, because multiple configurations to maintain
- Bad, because dependency on 10+ packages (flake8 plugins)
- Bad, because configuration conflicts between tools
- Bad, because limited auto-fixing

### Pylint + Black + isort

- Good, because comprehensive linting (pylint finds complex issues)
- Good, because mature tools
- Bad, because very slow (pylint is slowest major linter)
- Bad, because pylint produces many false positives
- Bad, because configuration is complex
- Bad, because multiple tools to run and configure
- Bad, because poor auto-fixing support

### Flake8 + Pylint + Black + isort

- Good, because maximum linting coverage
- Good, because catches most issues
- Bad, because extremely slow (60+ seconds for medium projects)
- Bad, because highest dependency count
- Bad, because most complex configuration
- Bad, because overlapping/conflicting rules
- Bad, because diminishing returns for marginal coverage increase

### Pylama

- Good, because consolidates multiple linters
- Good, because single configuration
- Bad, because just a wrapper (doesn't improve speed)
- Bad, because adds abstraction layer
- Bad, because limited compared to individual tools
- Bad, because less active development

## Validation

This decision was validated through:

- Migration completed in v3.x without major issues
- Linting time reduced from ~45 seconds to ~2 seconds
- Removal of 8+ tool dependencies
- Successful use in production for 2+ years
- Pylint removed in v4.1.0 without negative impact
- Community adoption of ruff has grown significantly

We would revisit this decision if:

- Ruff development slows or project becomes unmaintained
- Critical pylint functionality is needed that ruff can't provide
- Performance degrades significantly
- Configuration becomes too complex

## More Information

- Ruff documentation: https://docs.astral.sh/ruff/
- Ruff configuration: `/pyproject.toml` under `[tool.ruff]`
- Changelog entry removing pylint: v4.1.0
- Performance benchmarks: https://github.com/astral-sh/ruff#benchmarks
