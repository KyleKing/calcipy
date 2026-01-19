# MADR - Markdown Architectural Decision Records

## Overview

MADR (pronounced like "matter") stands for "Markdown Architectural Decision Records". It's a streamlined template for documenting architectural decisions in a structured, lightweight format using Markdown files stored directly in code repositories.

**Website**: https://adr.github.io/madr/ **Repository**: https://github.com/adr/madr **Latest Version**: MADR 4.0.0 (released 2024-09-17)

## Core Definition

According to MADR documentation:

> "An Architectural Decision (AD) is a justified software design choice that addresses a functional or non-functional requirement of architectural significance."

## Template Versions

MADR provides four template versions to suit different needs:

1. **adr-template.md**: All sections with explanations
1. **adr-template-minimal.md**: Only mandatory sections with explanations
1. **adr-template-bare.md**: All sections, empty (no explanations)
1. **adr-template-bare-minimal.md**: Mandatory sections only, no explanations

## Template Structure

### Full MADR Template Sections

**1. Title**

Assigns a name to the decision for easy identification and searching, ideally conveying both problem and solution.

**2. Metadata (Optional)**

- **Status**: proposed, rejected, accepted, deprecated, or superseded
- **Date**: When last updated (YYYY-MM-DD format)
- **Deciders**: Those involved in making the decision
- **Consulted**: Subject matter experts with two-way communication
- **Informed**: Stakeholders kept updated one-way

**3. Context and Problem Statement**

Describes the context and problem in a few sentences, potentially as a question or narrative inviting discussion.

**4. Decision Drivers**

Lists desired qualities, forces, and concerns guiding the choice. Examples:

- Performance requirements
- Security constraints
- Team expertise
- Budget limitations
- Time constraints

**5. Considered Options**

Enumerates alternatives investigated at the same abstraction level. The template recommends listing the chosen option first for clarity.

**6. Chosen Option**

References the selected option with justification explaining why it best addresses the decision drivers.

**7. Consequences**

Discusses outcomes in both positive and negative forms:

- **Good, because...**: Benefits and advantages
- **Bad, because...**: Drawbacks and trade-offs

**8. Validation/Confirmation (Optional)**

Describes how implementation compliance is evaluated or enforced. May include:

- Code review checkpoints
- Automated tests
- Architecture fitness functions
- Periodic audits

**9. Pros and Cons of Options**

Provides detailed analysis of alternatives with:

- **Positive properties**: Advantages
- **Negative properties**: Disadvantages
- **Neutral properties**: Neither good nor bad, but worth noting

**10. More Information**

Supplies additional evidence, team agreements, confidence levels, and related decision links.

### Minimal Template ("MADR Light")

The essential core includes only:

1. Title
1. Context and Problem Statement
1. Decision Drivers
1. Considered Options
1. Chosen Option with Consequences

## File Organization

### Naming Convention

ADRs follow the pattern: `NNNN-title-with-dashes.md`

- `NNNN`: Four-digit sequential number (e.g., 0001, 0002)
- `title-with-dashes`: Lowercase, hyphen-separated description

Examples:

- `0001-use-markdown-for-adrs.md`
- `0042-switch-to-postgresql.md`

### Directory Structure

**Simple Projects**: Store all ADRs in a single directory (e.g., `docs/adr/`)

**Complex Projects**: Use subdirectories for categorization:

```
docs/adr/
  backend/
    0001-use-postgresql.md
    0002-implement-caching.md
  frontend/
    0001-choose-react.md
    0002-state-management.md
  infrastructure/
    0001-use-kubernetes.md
```

### YAML Front Matter

MADR supports metadata using YAML front matter:

```yaml
---
status: accepted
date: 2024-01-15
deciders: [Alice, Bob, Carol]
consulted: [Dave, Eve]
informed: [Frank]
---
```

## What Makes MADR Distinctive

### 1. Accessibility

Uses Markdown files stored in projects rather than external tools. Developers work where they already are.

### 2. Simplicity

Emphasizes lean documentation over heavyweight processes. Can be as minimal or comprehensive as needed.

### 3. Flexibility

- Supports "neutral" arguments (neither pro nor con)
- Optional sections for tailoring to project needs
- Multiple template variants for different use cases

### 4. Organization

Allows categorization through subdirectories for large projects while maintaining simplicity for small ones.

### 5. Standardization

Established conventions for:

- Filenames (NNNN-title-with-dashes.md)
- Metadata (YAML front matter)
- Status values (proposed, accepted, rejected, deprecated, superseded)

## Philosophy

MADR centers on making decision documentation integral to development rather than a separate burden. Key principles:

- **Low friction**: Easy to create and maintain
- **Version controlled**: Same workflow as code
- **Searchable**: Plain text, git history
- **Reviewable**: Pull request workflow
- **Accessible**: No special tools required

## Integration with Tools

MADR works well with:

- **log4brains**: Uses MADR as default template
- **adr-tools**: Command-line tools for managing ADRs
- **Static site generators**: Convert to websites (MkDocs, Docusaurus, etc.)
- **Git**: Native version control support

## Use Cases

- **Best for**: Teams wanting lightweight, flexible ADR documentation
- **Project Size**: Any size (scales from small to large)
- **Team Size**: Individual developers to large teams
- **Integration**: Teams using git-based workflows
- **Learning Curve**: Minimal - just Markdown knowledge needed

## Benefits

- No vendor lock-in
- Works offline
- Easy to backup and migrate
- Supports pull request workflows
- Low barrier to adoption
- Can start minimal and grow as needed
