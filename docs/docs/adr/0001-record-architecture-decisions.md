# Record Architecture Decisions

* Status: accepted
* Date: 2024-11-20
* Deciders: KyleKing
* Consulted: ADR research documentation
* Informed: calcipy users and contributors

## Context and Problem Statement

calcipy is a Python package that implements best practices for development tooling. As the project evolved over 5+ major versions with multiple breaking changes (switch to uv, removal of pylint, migration away from pydantic), the rationale behind architectural decisions was often lost to time or buried in commit messages and issue discussions.

New contributors and future maintainers need to understand why certain technical choices were made to avoid:

* Re-litigating settled decisions
* Making changes that contradict established architecture
* Breaking compatibility without understanding the original constraints
* Losing institutional knowledge when team members move on

How should we capture and preserve the context, reasoning, and consequences of significant architectural decisions?

## Decision Drivers

* Solo maintainer project with occasional contributors - need to preserve decision context
* 5+ years of evolution with breaking changes - history is important
* Small project scope - overhead must be minimal
* Documentation already uses Markdown and MkDocs - should integrate naturally
* Decisions span technology choices, architecture patterns, and process - need flexible format
* Want to encourage documentation without creating barriers - must be lightweight

## Considered Options

* Y-Statements in README - Single sentence format for each decision
* MADR (Minimal) - Lightweight Markdown ADR template
* MADR (Full) - Comprehensive Markdown ADR template with all sections
* No formal ADRs - Continue documenting in commit messages and issues

## Decision Outcome

Chosen option: "MADR (Full) with flexible application", because it provides enough structure to capture important context while remaining lightweight enough for a small project. We will use the full template for significant architectural decisions but allow abbreviated versions for simpler choices.

The full MADR template provides:

* Structured sections that prompt thorough thinking
* Flexibility to omit optional sections when not applicable
* Compatibility with existing Markdown/MkDocs documentation
* No special tooling required beyond a text editor
* Status tracking for evolving decisions
* Industry-standard format with good examples available

### Consequences

* Good, because future maintainers will understand decision rationale
* Good, because new contributors can learn architectural thinking
* Good, because we avoid re-discussing settled questions
* Good, because Markdown integrates with existing documentation workflow
* Good, because MADR is lightweight enough to not slow development
* Bad, because requires discipline to create ADRs for significant decisions
* Bad, because adds one more document type to maintain
* Neutral, because we may need to backfill ADRs for existing major decisions

## Validation

We will validate this decision by:

* Creating ADRs for at least 5 significant existing architectural decisions within 1 month
* Including ADR creation as part of PR review for future architectural changes
* Reviewing ADR usefulness after 6 months of practice

We will revisit this decision if:

* ADRs are not being created (too much overhead)
* ADRs are not being referenced (not useful enough)
* Project grows to multiple active maintainers (may need different approach)

## More Information

* ADR research documentation: `/docs/docs/adr-research/`
* MADR template: https://adr.github.io/madr/
* Michael Nygard's original ADR proposal: http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions
