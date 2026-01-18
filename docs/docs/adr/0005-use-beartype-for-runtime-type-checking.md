# Use Beartype for Runtime Type Checking

* Status: accepted
* Date: 2022-06-10 (backfilled 2024-11-20)
* Deciders: KyleKing
* Informed: calcipy users

## Context and Problem Statement

calcipy uses type hints extensively for static type checking with mypy and pyright. While static type checking catches many issues during development, runtime type errors can still occur:

* Incorrect types passed from user configuration
* Data from external sources (files, APIs) not matching expected types
* Dynamic code paths that static checkers can't analyze
* Integration points between typed and untyped code

Python's type hints are not enforced at runtime by default - they're just metadata. While this provides flexibility, it means type violations can go undetected until they cause crashes or data corruption.

How can we catch type errors at runtime during development and testing without significant performance overhead in production?

## Decision Drivers

* Must validate type hints at runtime during development
* Must have minimal performance overhead in production
* Must work with existing Python type hints (no custom syntax)
* Must support complex types (generics, unions, protocols, etc.)
* Must be configurable (can be disabled in production)
* Must integrate well with existing codebase
* Prefer zero-configuration approach when possible
* Must not break existing functionality

## Considered Options

* **Beartype** - Near-zero overhead runtime type checker
* **Typeguard** - Comprehensive runtime type checker
* **Pydantic** - Data validation library with runtime checking
* **No runtime checking** - Rely on static type checking only
* **Manual assertions** - Add isinstance checks manually

## Decision Outcome

Chosen option: "Beartype", because it provides near-zero overhead runtime type checking that can be enabled globally via environment variable without modifying code. The "claw" feature allows automatic decoration of all functions in the package.

Beartype provides:

* Automatic type checking via decorator
* Near-zero overhead (O(1) complexity per call)
* Global package-wide enforcement with beartype_this_package
* Environment variable configuration (RUNTIME_TYPE_CHECKING_MODE)
* Support for all Python type hints (including complex types)
* Can be configured as warning or error
* No changes to function signatures required
* Excellent error messages for debugging

The implementation in `_runtime_type_check_setup.py` allows runtime checking to be enabled/disabled via environment variable without code changes.

### Consequences

* Good, because catches type errors at runtime during development
* Good, because minimal performance overhead (O(1) per call)
* Good, because no code changes required (automatic via claw)
* Good, because configurable via environment variable
* Good, because excellent error messages aid debugging
* Good, because supports all Python type hints including complex types
* Good, because can be enabled only in development/testing
* Good, because active development and maintenance
* Bad, because adds beartype as required dependency
* Bad, because runtime overhead exists even if minimal
* Bad, because can produce verbose error messages
* Bad, because may catch issues in third-party code (noise)
* Neutral, because requires environment variable to enable
* Neutral, because different from Pydantic's validation approach

## Pros and Cons of the Options

### Beartype

* Good, because near-zero overhead (O(1) complexity)
* Good, because automatic decoration via claw
* Good, because supports all Python type hints
* Good, because configurable severity (error/warning)
* Good, because excellent error messages
* Good, because no code changes required
* Good, because active development
* Bad, because adds dependency
* Bad, because requires understanding of configuration
* Neutral, because opt-in via environment variable

### Typeguard

* Good, because comprehensive type checking
* Good, because detailed validation
* Good, because supports complex types
* Bad, because higher performance overhead
* Bad, because more invasive (requires decorators on each function)
* Bad, because can be slow for complex types
* Bad, because less flexible configuration
* Neutral, because more thorough but slower

### Pydantic

* Good, because comprehensive validation framework
* Good, because excellent for data models
* Good, because runtime validation built-in
* Bad, because requires defining data models (not automatic)
* Bad, because heavier weight solution
* Bad, because performance overhead
* Bad, because code changes required (define models)
* Neutral, because better for data validation than function signatures
* Neutral, because we already use Pydantic for data models (complementary use)

### No Runtime Checking

* Good, because no performance overhead
* Good, because no additional dependencies
* Good, because simpler system
* Bad, because type errors only caught by static checkers
* Bad, because runtime type violations go undetected
* Bad, because harder to debug dynamic code paths
* Bad, because external data not validated

### Manual Assertions

* Good, because full control over validation
* Good, because no dependencies
* Good, because clear and explicit
* Bad, because requires manual work for every function
* Bad, because easy to forget or skip
* Bad, because verbose and repetitive
* Bad, because doesn't use type hints (redundant code)
* Bad, because maintenance burden

## Validation

This decision was validated through:

* Successfully catching type errors in development that static checkers missed
* Negligible performance impact in benchmarks
* Clean integration with existing codebase
* Positive experience with configuration flexibility
* No production issues from runtime checking

We would revisit this decision if:

* Performance overhead becomes problematic
* Beartype development slows or project becomes unmaintained
* Python adds native runtime type checking
* Better alternatives emerge with similar benefits

## More Information

* Beartype documentation: https://beartype.readthedocs.io/
* Implementation: `/calcipy/_runtime_type_check_setup.py`
* Configuration: Set `RUNTIME_TYPE_CHECKING_MODE=ERROR` or `WARNING`
* pyproject.toml dependency: beartype >=0.19.0
