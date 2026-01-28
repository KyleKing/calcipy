# ADR Research and Documentation

Research on Architecture Decision Records (ADRs) approaches, tools, and best practices based on [GitHub Issue #42](https://github.com/KyleKing/calcipy/issues/42).

## Table of Contents

### Individual Approach Summaries

Each document provides a comprehensive overview of a specific ADR approach or tool:

1. **[log4brains](log4brains.md)** - Architecture Decision Records management tool with automated site generation
1. **[AWS ADR Guide](aws-adr-guide.md)** - AWS's structured approach to documenting architectural decisions
1. **[MADR](madr.md)** - Markdown Architectural Decision Records, a lightweight template
1. **[Y-Statements](y-statements.md)** - Abbreviated single-sentence format for quick decision capture
1. **[Prefect PINs](prefect-pins.md)** - Prefect Improvement Notices for open source proposal-driven decisions
1. **[Ethereum EIPs](ethereum-eips.md)** - Ethereum Improvement Proposals, rigorous protocol-level decision process
1. **[Real-World Examples](real-world-examples.md)** - Practical implementations from Arachne, Structurizr, and other projects

### Comparison and Guidance

1. **[Comparison and Recommendations](comparison-and-recommendations.md)** - Side-by-side comparison with recommendations for different project scales
1. **[AI Guidance for ADRs](ai-guidance-for-adrs.md)** - Comprehensive guide for AI assistants to write and review ADRs

## Quick Decision Guide

### Choose by Project Size

| Team Size          | Project Duration   | Recommended Approach                    |
| ------------------ | ------------------ | --------------------------------------- |
| 1-2 developers     | < 6 months         | Y-Statements or notes in README         |
| 2-5 developers     | 6 months - 2 years | MADR (Minimal)                          |
| 5-15 developers    | 2-5 years          | MADR (Full) or AWS ADR                  |
| 15-50 developers   | 5+ years           | log4brains or MADR + documentation site |
| 50+ developers     | Enterprise         | AWS ADR + governance                    |
| Open Source        | Any                | MADR + public docs or PIN-style         |
| Protocol/Standards | Any                | EIP-style rigorous process              |

### Choose by Use Case

- **Fast-moving startup**: Y-Statements → MADR Minimal as you grow
- **Enterprise/Regulated**: AWS ADR Guide with full templates
- **Open source with community**: PIN-style proposals or MADR with public docs
- **Need searchable website**: log4brains
- **Protocol development**: EIP-style rigorous specification

## Key Takeaways

### What is an ADR?

An Architecture Decision Record (ADR) is a document that captures an important architectural decision along with its context and consequences.

### Why Use ADRs?

- **Preserve context**: Future team members understand why decisions were made
- **Prevent re-litigation**: Avoid repeatedly discussing settled questions
- **Improve onboarding**: New developers learn architectural thinking
- **Support evolution**: Understand when to revisit decisions
- **Build consensus**: Structured discussion of trade-offs

### Essential Elements

Every ADR should include:

1. **What** was decided
1. **Why** it was needed (context and problem)
1. **How** the decision was made (alternatives considered)
1. **What** the consequences are (positive and negative)

## Comparison Matrix

| Approach      | Formality   | Time to Create | Best For                     |
| ------------- | ----------- | -------------- | ---------------------------- |
| Y-Statements  | Low         | 5-15 min       | Quick decisions, small teams |
| MADR          | Medium      | 30-60 min      | Most projects                |
| AWS ADR       | Medium-High | 1-2 hours      | Enterprise teams             |
| log4brains    | Medium      | 30-60 min      | Teams wanting website        |
| Prefect PINs  | Medium-High | Days-Weeks     | Open source proposals        |
| Ethereum EIPs | Very High   | Weeks-Months   | Protocol/standards           |

## Getting Started

### For a New Project

1. **Start with ADR-0001**: "Record architecture decisions"

    - Establishes the practice
    - Documents which template you'll use
    - Defines when to create ADRs

1. **Choose your template**:

    - Small team: MADR Minimal
    - Growing team: MADR Full
    - Enterprise: AWS ADR Guide

1. **Set up storage**:

    ```
    project/
    └── docs/
        └── adr/
            ├── README.md (index)
            └── 0001-record-architecture-decisions.md
    ```

1. **Document your next decision**: Practice the process

1. **Review and iterate**: Adjust based on what works

### For an Existing Project

1. **Backfill key decisions**: Document the most important existing decisions
1. **Start using for new decisions**: Make it part of your workflow
1. **Update as you learn**: Refine your template and process

## Common Patterns

### File Organization

```
docs/adr/
├── README.md                          # Index of all ADRs
├── 0001-record-decisions.md          # Meta-ADR establishing practice
├── 0002-choose-database.md           # Technical decision
├── 0003-api-versioning-strategy.md   # Architecture pattern
└── 0004-testing-approach.md          # Process decision
```

### Naming Convention

Most projects use: `NNNN-title-with-dashes.md`

- `NNNN`: Sequential number (0001, 0002, etc.)
- `title-with-dashes`: Lowercase, hyphenated
- `.md`: Markdown file extension

### Status Values

Common status values across approaches:

- **Proposed**: Under discussion
- **Accepted**: Approved and active
- **Rejected**: Not approved
- **Deprecated**: No longer recommended
- **Superseded**: Replaced by another ADR

## Resources

### Tools

- **log4brains**: https://github.com/thomvaill/log4brains
- **adr-tools**: Command-line tools for ADR management
- **MkDocs**: Static site generator for documentation
- **Docusaurus**: Modern documentation framework

### Templates

- **MADR Templates**: https://github.com/adr/madr
- **ADR Templates Collection**: https://adr.github.io/adr-templates/
- **AWS Templates**: Provided in their ADR guide

### Further Reading

- **Michael Nygard's ADR**: Original ADR blog post that started the practice
- **Thoughtworks Technology Radar**: Discussion of ADR adoption
- **ADR GitHub Organization**: https://github.com/adr

## Contributing to This Research

This research was compiled from:

- Official documentation from each tool/approach
- Real-world examples from open source projects
- Best practices from enterprise adoption
- Community discussions and feedback

For updates or corrections, please reference the source materials in each individual document.

## Summary

The best ADR approach is the one your team actually uses. Start simple, document your first decision, and evolve your practice as your project grows. The goal is to capture the "why" behind decisions to help future readers (including future you) understand and trust the choices made.

**Quick recommendation**: If you're unsure, start with MADR Minimal. It's lightweight enough to not slow you down but structured enough to capture what matters. You can always expand to the full template later as your needs grow.
