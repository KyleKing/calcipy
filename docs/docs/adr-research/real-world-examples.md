# Real-World ADR Examples and Implementations

## Overview

This document examines real-world implementations of Architecture Decision Records across different projects to understand practical patterns and approaches.

## Arachne Framework

**Repository**: https://github.com/arachne-framework/architecture **Example**: https://github.com/arachne-framework/architecture/blob/master/adr-002-configuration.md

### ADR Structure Used

Arachne follows a clean, straightforward ADR format:

**1. Title**

- "Architecture Decision Record: [Topic]"
- Example: "Architecture Decision Record: Configuration"

**2. Context**

Describes the problem space and foundational principles:

- Goals and objectives
- Philosophical underpinnings
- Current situation
- Constraints

Example context from ADR-002:

- Modularity across different software packages
- Transparency and introspectability of applications
- Strong defaults with high configurability
- References to "data-first" design philosophy (Rich Hickey, Stuart Halloway)

**3. Decision**

States the chosen approach clearly and concisely.

Example:

> "Arachne will take the 'everything is data' philosophy to its logical extreme, and encode as much information about the application as possible in a single, highly general data structure."

Includes specific examples:

- Dependency injection
- Runtime entities
- HTTP routes
- Persistence schemas

**4. Status**

A single-line indicator of the current state:

- Proposed
- Accepted
- Deprecated
- Superseded

**5. Consequences**

Bullet-pointed outcomes, both positive and challenging:

- Benefits and advantages
- Challenges and trade-offs
- Impact on other components
- Future implications

### Key Characteristics

- **Philosophy-driven**: Explicitly references design principles and thought leaders
- **Data-centric**: Emphasizes the data structure approach
- **Clear sections**: Well-defined structure without extra complexity
- **Consequences-focused**: Honest about both benefits and challenges

## Structurizr Python

**Repository**: https://github.com/Midnighter/structurizr-python/tree/devel/docs/development/adr **Number of ADRs**: 9 documented decisions

### ADR Collection

The project maintains ADRs at `docs/development/adr/` with:

1. **ADR-0001**: "Record architecture decisions" - establishes the ADR practice itself
1. **ADR-0002**: Version control approach
1. **ADR-0003**: Python 3.6 compatibility requirement
1. **ADR-0004**: Package versioning strategy
1. **ADR-0005**: Code quality assurance standards
1. **ADR-0006**: Testing approach
1. **ADR-0007**: Unit testing specifics
1. **ADR-0008**: Package structure organization
1. **ADR-0009**: "Use pydantic for json de-serialization"

### Organization Approach

**Naming Convention**

- `NNNN-title.md` format
- Sequential numbering (0001, 0002, etc.)
- Descriptive but concise titles

**Documentation Integration**

- `.pages` configuration file for navigation
- Integrated with MkDocs documentation system
- Part of developer documentation structure

**Scope Coverage**

The ADRs cover diverse decision types:

- **Process decisions**: How to record decisions (ADR-0001)
- **Technical constraints**: Python version compatibility (ADR-0003)
- **Quality standards**: Code quality requirements (ADR-0005)
- **Architecture**: Package structure (ADR-0008)
- **Technology choices**: Library selection (ADR-0009)

### Key Characteristics

- **Comprehensive coverage**: From meta-decisions to specific library choices
- **Developer-focused**: Located in development documentation
- **Tooling integration**: Works with MkDocs for documentation site
- **Progressive adoption**: ADR-0001 establishes practice, then other decisions follow

## Concourse CI

**Website**: https://concourse-ci.org/internals.html **Type**: Public documentation of architectural decisions

### Approach

Concourse CI documents architectural decisions as part of their public "Internals" documentation:

- Integrated into main documentation site
- Explains internal architecture and design decisions
- Focuses on helping contributors understand the system
- Combines high-level architecture with detailed decisions

### Key Characteristics

- **Public-facing**: Not just for internal team
- **Educational**: Helps onboard contributors
- **Integrated**: Part of main documentation, not separate
- **Detailed**: Technical depth for implementation understanding

## Boltons

**Documentation**: https://boltons.readthedocs.io/en/latest/architecture.html **Type**: Architecture documentation page

### Approach

Boltons includes an "Architecture" page in their documentation that:

- Explains design philosophy
- Documents key architectural decisions
- Provides context for implementation choices
- Justifies the library's structure

### Key Characteristics

- **Single page**: All architecture documentation in one place
- **Narrative style**: Flows as connected text rather than discrete ADRs
- **Philosophy-focused**: Emphasizes the "why" behind design
- **User-facing**: Part of public documentation

## TimescaleDB

**Documentation**: https://docs.timescale.com/latest/introduction/architecture **Type**: Comprehensive architecture documentation

### Approach

TimescaleDB provides extensive architecture documentation:

- Detailed system design
- Technical architecture diagrams
- Design decision rationale
- Performance considerations

### Key Characteristics

- **Comprehensive**: Complete system overview
- **Visual**: Includes diagrams and illustrations
- **Technical depth**: Implementation details
- **User-focused**: Helps users understand system behavior

## Packet Cafe

**Documentation**: https://iqtlabs.gitbook.io/packet-cafe/design/architecture **Type**: Design and architecture section

### Approach

Uses GitBook for documentation with dedicated architecture section:

- Design decisions documented
- Architecture overview
- Component descriptions
- System interactions

### Key Characteristics

- **GitBook platform**: Modern documentation hosting
- **Organized sections**: Clear navigation structure
- **Design-focused**: Emphasizes design choices
- **Accessible**: Public documentation for users and contributors

## Common Patterns Across Examples

### 1. Location

**Within Repository**

- Most store ADRs in the repository
- Common paths:
    - `docs/adr/`
    - `docs/development/adr/`
    - `docs/architecture/`

**Integration with Documentation**

- Often part of larger documentation system
- MkDocs, Sphinx, GitBook, or custom static sites
- Publicly accessible, not just internal

### 2. Format Variations

**Discrete ADRs**

- Individual files per decision (Arachne, Structurizr)
- Sequential numbering
- Consistent template

**Integrated Documentation**

- Architecture decisions woven into larger docs (Boltons, TimescaleDB)
- Narrative flow
- Single or few pages

**Hybrid Approach**

- Both discrete ADRs and overview documentation
- ADRs for specific decisions
- Architecture guides for big picture

### 3. Scope of Decisions Documented

**Technical Decisions**

- Library choices (Pydantic in Structurizr)
- Technology stack
- Framework selection

**Process Decisions**

- Testing approach
- Code quality standards
- Version control strategy

**Architecture Decisions**

- System structure
- Component organization
- Design patterns

**Philosophy and Principles**

- Design philosophy (Arachne)
- Core values
- Guiding principles

### 4. Audience Considerations

**Internal Team**

- Help future team members understand decisions
- Prevent re-litigating settled questions
- Maintain consistency

**External Contributors**

- Help open source contributors understand system
- Explain non-obvious choices
- Lower barrier to contribution

**Users**

- Help users understand system behavior
- Explain performance characteristics
- Build trust through transparency

### 5. Maintenance Approaches

**Active Maintenance**

- Regular updates
- Status changes tracked
- Deprecated decisions marked

**Static Records**

- Written once, rarely updated
- Historical record
- Immutable documentation

**Evolving Documentation**

- Living documents
- Updated as system changes
- Reflects current state

## Lessons Learned

### What Works Well

**1. Start Simple**

- ADR-0001: "Record architecture decisions"
- Establishes practice before demanding compliance
- Low barrier to adoption

**2. Integrate with Existing Tools**

- Use documentation system already in place
- Version control in git
- No special tools required

**3. Document Why, Not Just What**

- Context and rationale most valuable
- Technical details can be found in code
- "Why" endures while "how" changes

**4. Make It Public**

- Even internal projects benefit from public ADRs
- Transparency builds trust
- Helps future contributors

**5. Cover Different Decision Types**

- Not just architecture
- Process, tools, standards
- Any significant decision benefits from documentation

### Common Challenges

**1. Consistency**

- Maintaining format across ADRs
- Getting team buy-in
- Making it habit

**2. Finding Balance**

- Too detailed → maintenance burden
- Too brief → missing context
- Right level varies by project

**3. Keeping Current**

- Updating status when decisions change
- Marking deprecated ADRs
- Linking superseding decisions

**4. Discoverability**

- Making ADRs easy to find
- Organizing for browsing
- Search functionality

## Recommendations by Project Type

### Small Projects (1-3 developers)

**Approach**: Integrated documentation or Y-Statements

- Single architecture.md file
- Lightweight decision capture
- Focus on major decisions only

**Example**: Boltons approach

### Medium Projects (4-10 developers)

**Approach**: Discrete ADRs with simple structure

- Individual ADR files
- Sequential numbering
- Standard template (MADR or similar)

**Example**: Structurizr approach

### Large Projects (10+ developers)

**Approach**: Comprehensive ADR system with tooling

- Structured ADR collection
- Automated site generation (log4brains)
- Integration with development workflow
- Multiple categories or packages

**Example**: Arachne approach

### Open Source Projects

**Approach**: Public, accessible ADRs

- Part of public documentation
- Helps contributors understand decisions
- Builds community trust
- Consider PIN-style for community input

**Example**: Structurizr, Concourse CI approaches

### Enterprise/Regulated

**Approach**: Formal, comprehensive ADRs

- Detailed rationale
- Security considerations
- Compliance documentation
- Audit trail

**Example**: AWS ADR Guide approach

## Implementation Checklist

Based on successful examples:

### Getting Started

- [ ] Create ADR-0001 to establish practice
- [ ] Choose storage location (docs/adr/)
- [ ] Select template (MADR, custom, etc.)
- [ ] Document in CONTRIBUTING or README

### Ongoing Practice

- [ ] Create ADR for each significant decision
- [ ] Review ADRs in pull requests
- [ ] Update status when decisions change
- [ ] Link ADRs from related code/docs

### Maintenance

- [ ] Maintain index or list of ADRs
- [ ] Integrate with documentation site
- [ ] Review periodically for currency
- [ ] Mark deprecated decisions clearly

### Quality

- [ ] Ensure consistent format
- [ ] Capture sufficient context
- [ ] Document alternatives considered
- [ ] Explain rationale clearly
- [ ] Note consequences honestly
