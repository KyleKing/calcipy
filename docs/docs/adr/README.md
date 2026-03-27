# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for calcipy - documents that capture important architectural decisions along with their context and consequences.

## What is an ADR?

An Architecture Decision Record (ADR) is a document that captures an architecturally significant decision, the context in which it was made, the alternatives considered, and the consequences of the choice.

## Why ADRs?

ADRs help us:

- **Preserve context**: Future maintainers understand why decisions were made
- **Prevent re-litigation**: Avoid repeatedly discussing settled questions
- **Improve onboarding**: New contributors learn architectural thinking
- **Support evolution**: Understand when to revisit decisions
- **Build consensus**: Structured discussion of trade-offs

## ADR Index

### Meta

- [ADR-0001](0001-record-architecture-decisions.md) - Record Architecture Decisions
    - Status: **accepted**
    - Establishes the ADR practice for calcipy using MADR format

### Task Automation and Development Workflow

- [ADR-0002](0002-use-invoke-for-task-automation.md) - Use Invoke for Task Automation

    - Status: **accepted**
    - Chose invoke over Make, Just, Taskipy, and other task runners

- [ADR-0007](0007-provide-multiple-cli-entry-points.md) - Provide Multiple CLI Entry Points

    - Status: **accepted**
    - Multiple specialized commands (calcipy-lint, calcipy-test, etc.) vs single monolithic CLI

- [ADR-0008](0008-run-as-tool-rather-than-dependency.md) - Run as Tool Rather Than Dependency

    - Status: **accepted**
    - Hybrid approach supporting both standalone tool usage (uvx/pipx) and project dependency installation

### Code Quality Tools

- [ADR-0003](0003-use-ruff-for-linting-and-formatting.md) - Use Ruff for Linting and Formatting

    - Status: **accepted**
    - Migrated from flake8 + pylint + black + isort to unified ruff

- [ADR-0005](0005-use-beartype-for-runtime-type-checking.md) - Use Beartype for Runtime Type Checking

    - Status: **accepted**
    - Runtime type validation with near-zero overhead

### Packaging and Dependencies

- [ADR-0004](0004-switch-to-uv-for-dependency-management.md) - Switch to uv for Dependency Management

    - Status: **accepted**
    - Recent migration from Poetry to uv (October 2024)

- [ADR-0006](0006-use-hatchling-for-build-backend.md) - Use Hatchling for Build Backend

    - Status: **accepted**
    - PyPA-maintained build backend for creating wheels and sdists

## Status Definitions

- **Proposed**: Under discussion, not yet decided
- **Accepted**: Approved and currently in use
- **Deprecated**: No longer recommended but still in use
- **Superseded**: Replaced by a newer decision (linked)
- **Rejected**: Considered but not approved

## How to Contribute

When making significant architectural decisions:

1. **Copy the MADR template** from the [research directory](../adr-research/madr.md)
1. **Number sequentially**: Use the next available ADR number (0008, 0009, etc.)
1. **Fill in all sections**: Context, drivers, options, outcome, consequences
1. **Be honest about trade-offs**: Include both positive and negative consequences
1. **Submit for review**: Include ADR in your pull request
1. **Update this index**: Add your ADR to the appropriate category

### What Warrants an ADR?

Create an ADR when a decision:

- **Has architectural significance**: Affects system structure, patterns, or standards
- **Is difficult to reverse**: High cost or risk to change later
- **Involves trade-offs**: Multiple valid options with different pros/cons
- **Affects multiple components**: Cross-cutting concerns
- **Needs to be remembered**: Important context for future maintainers

### What Does NOT Warrant an ADR?

Skip ADRs for:

- **Implementation details**: Specific code patterns (unless establishing standard)
- **Trivial decisions**: Easily reversible, low impact
- **Temporary solutions**: Known to be short-term
- **Individual preferences**: Style choices without broader impact

## Template

For new ADRs, use the MADR (Full) template:

```markdown
# [Short Title]

* Status: [proposed | accepted | rejected | deprecated | superseded]
* Date: YYYY-MM-DD
* Deciders: [list everyone involved]
* Consulted: [list anyone consulted]
* Informed: [list anyone informed]

## Context and Problem Statement

[Describe the context and problem]

## Decision Drivers

* [decision driver 1]
* [decision driver 2]
* ...

## Considered Options

* [option 1]
* [option 2]
* [option 3]
* ...

## Decision Outcome

Chosen option: "[option 1]", because [justification].

### Consequences

* Good, because [positive consequence]
* Bad, because [negative consequence]
* ...

## Pros and Cons of the Options

### [option 1]

* Good, because [argument 1]
* Bad, because [argument 2]
* ...

### [option 2]

* Good, because [argument 1]
* Bad, because [argument 2]
* ...

## Validation

[How will we validate this decision?]

We will revisit this decision if:

* [condition 1]
* [condition 2]

## More Information

[Links, references, etc.]
```

## Research and Guidance

For detailed guidance on ADR approaches and best practices, see:

- [ADR Research](../adr-research/) - Comprehensive research on different ADR approaches
- [AI Guidance for ADRs](../adr-research/ai-guidance-for-adrs.md) - Guide for writing and reviewing ADRs
- [Comparison and Recommendations](../adr-research/comparison-and-recommendations.md) - Comparison table and recommendations

## Additional Resources

- **MADR Documentation**: https://adr.github.io/madr/
- **Michael Nygard's ADR**: http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions
- **ADR GitHub Organization**: https://github.com/adr
