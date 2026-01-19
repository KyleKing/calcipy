# Y-Statements - Abbreviated Architecture Decision Format

## Overview

Y-Statements (also called (WH)Y-Statements) are an abbreviated, lightweight format for documenting architectural decisions. They condense decision documentation into a single structured sentence, making them ideal for quick capture and communication.

**Source**: https://medium.com/olzzio/y-statements-10eb07b5a177
**Origin**: Evolved from George Fairbanks' Architecture Haikus notation
**Published**: Featured in "Making Architectural Knowledge Sustainable: Industrial Practice Report and Outlook" at SATURN 2012 and in IEEE Software/InfoQ article

## Format Structure

Y-Statements reduce documentation to a single statement following this template:

> "In the context of `<use case/user story u>`, facing `<concern c>` we decided for `<option o>` to achieve `<quality q>`, accepting `<downside d>`."

### Six Core Components

**1. Context** (In the context of...)

- Functional requirement (user story or use case)
- Or an architecture component
- Establishes the scope and situation

**2. Facing** (facing...)

- Non-functional requirement
- Desired quality attribute
- The problem or concern driving the decision

**3. We decided for** (we decided for...)

- Decision outcome
- The most important part - what was chosen
- Clear statement of the solution

**4. Neglected** (and against...)

- Alternatives not chosen
- Important to remember what was considered but rejected
- Prevents revisiting dismissed options

**5. To achieve** (to achieve...)

- Benefits of the decision
- Full or partial satisfaction of the requirement
- Positive outcomes expected

**6. Accepting that** (accepting that...)

- Drawbacks and trade-offs
- Impact on other properties/context
- Effort/cost implications
- Honest acknowledgment of downsides

## Example Y-Statement

> In the context of the **Web shop service**, facing the need to **keep user session data consistent and current across shop instances**, we decided for the **Database Session State pattern** and against **Client Session State or Server Session State**, to achieve **data consistency and cloud elasticity**, accepting that **a session database needs to be designed and implemented**.

## Visual Representation

The template forms the letter "Y" when visualized:

```
                Context
                   |
                Facing
                   |
        ┌──────────┴──────────┐
    Decided              Neglected
        │
    To Achieve
        │
    Accepting
```

The "Y" shape gives the format its name and is pronounced like the word "why", which reinforces the focus on explaining the reasoning.

## Key Characteristics

### 1. Brevity

- Single (long) sentence
- Forces conciseness
- Easy to scan and understand quickly

### 2. Completeness

Despite brevity, captures:

- Problem (context + facing)
- Solution (decided for)
- Alternatives (neglected)
- Benefits (to achieve)
- Trade-offs (accepting)

### 3. Structured

The six sections provide a consistent template that:

- Guides thinking
- Ensures key information is captured
- Makes decisions comparable

### 4. Lightweight

Much leaner than full ADR templates while still capturing essential information.

## When to Use Y-Statements

### Ideal Use Cases

- **Lightweight documentation needs**: When full ADRs feel too heavy
- **Quick decision capture**: During meetings or design sessions
- **Decision summaries**: As TL;DR for longer documents
- **Intermediate decisions**: Not architecturally significant enough for full ADR
- **Rapid iteration**: Early in design when things are fluid

### Consider Full ADRs Instead When

- Decision is highly complex with many nuances
- Multiple stakeholders need detailed justification
- Regulatory or compliance documentation required
- Decision needs extensive technical detail
- Long-term reference documentation needed

## Relationship to ADRs

Y-Statements can work alongside ADRs:

- **ADR Summary**: Use Y-Statement as the summary at the top of a full ADR
- **Lightweight ADRs**: Use Y-Statement as the entire ADR for simpler decisions
- **Decision Register**: Maintain a list of Y-Statements with links to full ADRs when they exist
- **Hybrid Approach**: Start with Y-Statement, expand to full ADR if needed

## Benefits

### For Teams

- **Fast to create**: Can capture decisions in real-time
- **Easy to review**: Quick to read and understand
- **Encourages documentation**: Lower barrier than full ADRs
- **Consistent format**: Same structure every time

### For Communication

- **Concise**: Gets to the point quickly
- **Complete**: Still captures essential elements
- **Memorable**: Structure makes it stick
- **Shareable**: Easy to include in emails, chat, presentations

### For Decision Making

- **Forces clarity**: Must distill to essentials
- **Highlights trade-offs**: "Accepting" clause ensures honest assessment
- **Shows alternatives**: "Neglected" prevents tunnel vision
- **Links to goals**: "To achieve" connects decision to objectives

## Limitations

### What Y-Statements Don't Capture Well

- **Detailed technical analysis**: Not enough space for deep dive
- **Complex multi-faceted decisions**: Hard to fit in one sentence
- **Multiple alternatives**: Can list but not analyze in detail
- **Detailed consequences**: Only high-level trade-offs
- **Implementation guidance**: Not enough room for "how"

### Potential Issues

- **Oversimplification**: Complex decisions may be trivialized
- **Missing context**: Background information often needed
- **Limited traceability**: Hard to reference specific requirements
- **One-size-fits-all**: Same format for very different decisions

## Best Practices

### Writing Effective Y-Statements

1. **Be specific**: Avoid vague terms like "better" or "improved"
2. **Be honest**: Don't hide or minimize trade-offs
3. **Be complete**: Fill in all six components
4. **Be concise**: Each component should be short
5. **Be clear**: Avoid jargon and acronyms when possible

### Organizing Y-Statements

- **Decision log**: Maintain a numbered or dated list
- **Categorize**: Group by component, layer, or concern
- **Link**: Reference related decisions
- **Version control**: Store in git like code
- **Review**: Revisit periodically to validate or supersede

## Integration with Workflows

### Design Meetings

1. Discuss problem and options
2. Draft Y-Statement collaboratively
3. Review for completeness
4. Document in decision log
5. Expand to full ADR if needed

### Pull Requests

- Include Y-Statement in PR description
- Helps reviewers understand intent
- Captures decision at implementation time
- Creates historical record

### Documentation

- Include in README or design docs
- Link to relevant code
- Maintain index of decisions
- Update status as needed

## Use Cases

- **Best for**: Agile teams needing quick decision capture
- **Project Size**: Small to medium projects
- **Team Size**: Small, co-located teams
- **Integration**: Works with any version control system
- **Learning Curve**: Very low - just one sentence format
- **Formality**: Informal to semi-formal documentation needs
