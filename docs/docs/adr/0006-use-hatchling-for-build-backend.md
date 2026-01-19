# Use Hatchling for Build Backend

- Status: accepted
- Date: 2024-01-20 (backfilled 2024-11-20)
- Deciders: KyleKing
- Informed: calcipy users

## Context and Problem Statement

Python packages require a build backend to create distributable artifacts (wheels and sdists). When using Poetry for dependency management, the natural choice was poetry-core as the build backend. However, with the migration to uv (ADR-0004), we had the opportunity to reconsider the build backend choice.

The build backend should:

- Create standards-compliant packages (PEP 517/PEP 660)
- Support modern pyproject.toml configuration (PEP 621)
- Be fast and reliable
- Have minimal dependencies
- Be actively maintained
- Work well with uv and modern Python tooling

## Decision Drivers

- Must comply with PEP 517 (build backend interface)
- Must support PEP 621 (pyproject.toml metadata)
- Must produce valid wheels and sdists
- Must be fast (affects CI/CD and local builds)
- Must have minimal dependencies
- Must be actively maintained
- Prefer tools that integrate well with modern ecosystem
- Prefer simpler over more complex solutions

## Considered Options

- **Hatchling** - Modern, extensible build backend from PyPA
- **Poetry-core** - Build backend from Poetry project
- **Setuptools** - Traditional Python build system
- **Flit-core** - Minimal build backend
- **PDM-backend** - Build backend from PDM project

## Decision Outcome

Chosen option: "Hatchling", because it provides a modern, standards-compliant build backend with excellent performance and minimal dependencies. As a PyPA (Python Packaging Authority) project, it has strong governance and aligns with Python's packaging future.

Hatchling provides:

- Full PEP 517 and PEP 621 compliance
- Fast build times
- Minimal dependencies (just hatchling)
- Extensible plugin system
- Active maintenance by PyPA
- Clear and simple configuration
- Good integration with modern tools (uv, pip, etc.)

The migration from poetry-core to hatchling was straightforward, requiring only updating the `[build-system]` section in pyproject.toml.

### Consequences

- Good, because PyPA-maintained project (official Python packaging)
- Good, because fast builds with minimal overhead
- Good, because minimal dependencies reduce supply chain risk
- Good, because full PEP 621 support enables modern features
- Good, because extensible via plugins if needed
- Good, because simple configuration
- Good, because works seamlessly with uv
- Bad, because different from Poetry users' expectations (if they know Poetry)
- Neutral, because required migration from poetry-core (one-time effort)
- Neutral, because plugin system unused (we have simple needs)

## Pros and Cons of the Options

### Hatchling

- Good, because PyPA-maintained (official Python packaging authority)
- Good, because fast build performance
- Good, because minimal dependencies
- Good, because modern PEP 621 support
- Good, because extensible plugin system
- Good, because active development
- Good, because clear documentation
- Neutral, because newer than setuptools (but still mature)

### Poetry-core

- Good, because familiar if using Poetry
- Good, because mature and stable
- Good, because good documentation
- Bad, because tied to Poetry ecosystem
- Bad, because more opinionated
- Bad, because not PyPA-maintained
- Neutral, because would work but doesn't offer advantages

### Setuptools

- Good, because most widely used
- Good, because very mature (decades old)
- Good, because extensive documentation
- Good, because PyPA-maintained
- Bad, because complex configuration (setup.py or setup.cfg)
- Bad, because slower than modern alternatives
- Bad, because large dependency footprint
- Bad, because legacy baggage and complexity

### Flit-core

- Good, because extremely minimal
- Good, because very fast
- Good, because simple configuration
- Good, because PyPA-maintained
- Bad, because limited features (too minimal for some needs)
- Bad, because no plugin system
- Neutral, because simplicity is strength and weakness

### PDM-backend

- Good, because modern and fast
- Good, because PEP 621 compliant
- Good, because active development
- Bad, because tied to PDM ecosystem
- Bad, because smaller community than hatchling
- Bad, because not PyPA-maintained
- Neutral, because similar to hatchling in many ways

## Validation

This decision was validated through:

- Successful builds in CI/CD since migration
- Packages published to PyPI without issues
- Fast build times maintained
- No user reports of installation problems
- Compatibility with pip, uv, and other installers

We would revisit this decision if:

- Hatchling development slows or project becomes unmaintained
- Build issues emerge that hatchling can't address
- Python packaging ecosystem standardizes on different backend
- We need features that hatchling doesn't provide

## More Information

- Hatchling documentation: https://hatch.pypa.io/latest/config/build/
- Build configuration: `/pyproject.toml` under `[build-system]`
- PEP 517: https://peps.python.org/pep-0517/
- PEP 621: https://peps.python.org/pep-0621/
