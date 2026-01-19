# AI Guidance for Writing and Reviewing Architecture Decision Records

## Purpose

This document provides comprehensive guidance for AI assistants helping users write and review Architecture Decision Records (ADRs). It covers best practices, common pitfalls, review criteria, and practical examples.

## Quick Reference

### When to Create an ADR

An ADR should be created when a decision:

- **Has architectural significance**: Affects system structure, patterns, or standards
- **Is difficult to reverse**: High cost or risk to change later
- **Involves trade-offs**: Multiple valid options with different pros/cons
- **Affects multiple components**: Cross-cutting concerns
- **Needs to be remembered**: Important context for future team members
- **Is contentious**: Multiple stakeholders with different views

### When NOT to Create an ADR

Skip ADRs for:

- **Implementation details**: Specific code patterns (unless establishing standard)
- **Trivial decisions**: Easily reversible, low impact
- **Temporary solutions**: Known to be short-term
- **Individual preferences**: Style choices without broader impact
- **Obvious choices**: No meaningful alternatives

## Understanding the Project Context

Before helping with an ADR, determine:

### 1. Project Size and Team

```
Questions to ask:
- How many developers?
- How long has the project existed?
- What's the expected lifetime?
- Internal or open source?
```

This determines formality level needed.

### 2. Existing ADR Practice

```
Questions to ask:
- Do you have existing ADRs?
- What template do you use?
- Where are ADRs stored?
- What's your review process?
```

Match existing conventions or help establish new ones.

### 3. Decision Scope

```
Questions to assess:
- Who is affected by this decision?
- What's the impact if we're wrong?
- How expensive is it to change later?
- Are there regulatory/compliance concerns?
```

This determines detail level needed.

## Template Selection

### Decision Tree for Template Choice

```
1. Quick decision, small team?
   → Use Y-Statement format

2. Following existing ADR practice?
   → Use their template

3. Starting fresh, medium team?
   → Use MADR (Minimal for starters, Full as needed)

4. Enterprise/compliance needs?
   → Use AWS ADR Guide template

5. Open source with community input?
   → Consider PIN-style proposal

6. Protocol/standards development?
   → Use EIP-style rigorous template
```

### Y-Statement Template

Use when: Quick capture, small teams, lightweight documentation

```markdown
## [Decision Title]

In the context of [use case/user story],
facing [concern/problem],
we decided for [option chosen]
and against [alternatives not chosen],
to achieve [desired quality/benefit],
accepting [downside/trade-off].
```

**Example**:

```markdown
## Use PostgreSQL for Primary Database

In the context of our multi-tenant SaaS application,
facing the need for reliable ACID transactions and complex queries,
we decided for PostgreSQL
and against MongoDB and MySQL,
to achieve data consistency and rich query capabilities,
accepting increased operational complexity and infrastructure costs.
```

### MADR Minimal Template

Use when: Most projects, balances detail with simplicity

```markdown
# [Short Title]

## Context and Problem Statement

[Describe the context and problem statement, e.g., in free form using two to three sentences. You may want to articulate the problem in the form of a question.]

## Decision Drivers

* [decision driver 1, e.g., a force, facing concern, ...]
* [decision driver 2, e.g., a force, facing concern, ...]
* ...

## Considered Options

* [option 1]
* [option 2]
* [option 3]
* ...

## Decision Outcome

Chosen option: "[option 1]", because [justification. e.g., only option that meets k.o. criterion decision driver 1 | which resolves force 2 | ...].

### Consequences

* Good, because [positive consequence, e.g., improvement of quality attribute satisfaction, follow-up decisions required, ...]
* Bad, because [negative consequence, e.g., compromising quality attribute, follow-up decisions required, ...]
* ...
```

### MADR Full Template

Use when: Complex decisions, larger teams, need comprehensive documentation

```markdown
# [Short Title]

* Status: [proposed | rejected | accepted | deprecated | superseded by [ADR-0005](0005-example.md)]
* Date: [YYYY-MM-DD when the decision was last updated]
* Deciders: [list everyone involved in the decision]
* Consulted: [list anyone consulted]
* Informed: [list anyone informed]

## Context and Problem Statement

[Describe the context and problem statement]

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

## Validation

[How will we validate the decision is correct? How will we know if we need to revisit?]

## Pros and Cons of the Options

### [option 1]

[example | description | pointer to more information | ...]

* Good, because [argument 1]
* Good, because [argument 2]
* Neutral, because [argument 3]
* Bad, because [argument 4]
* ...

### [option 2]

[example | description | pointer to more information | ...]

* Good, because [argument 1]
* Good, because [argument 2]
* Neutral, because [argument 3]
* Bad, because [argument 4]
* ...

### [option 3]

[example | description | pointer to more information | ...]

* Good, because [argument 1]
* Good, because [argument 2]
* Neutral, because [argument 3]
* Bad, because [argument 4]
* ...

## More Information

[Any additional information, links, or context]
```

## Writing Effective ADRs

### 1. Title

**Good titles**:

- Concise (< 10 words)
- Action-oriented (verb + object)
- Specific enough to differentiate

**Examples**:

- ✅ "Use PostgreSQL for primary database"
- ✅ "Implement event sourcing for order processing"
- ✅ "Migrate from REST to GraphQL API"
- ❌ "Database decision" (too vague)
- ❌ "We need to decide on our database architecture approach" (too long)

### 2. Context and Problem Statement

**What to include**:

- Background: What led to this decision point?
- Problem: What are we trying to solve?
- Constraints: What limits our options?
- Requirements: What must the solution provide?

**What to avoid**:

- Assuming reader knows the background
- Jumping to solutions before stating problem
- Technical jargon without explanation
- Missing the "why now?"

**Good example**:

```markdown
## Context and Problem Statement

Our monolithic application has grown to 500K LOC with 15 developers working on it.
Deployment takes 2 hours and any bug requires redeploying the entire application.
Teams are blocked waiting for others to finish features in shared modules.

We need to improve development velocity, reduce deployment risk, and enable teams
to work independently. However, we have limited DevOps resources and our team has
minimal microservices experience.

How should we restructure our application to improve development velocity while
managing operational complexity?
```

**Bad example**:

```markdown
## Context

We should use microservices because they're better.
```

### 3. Decision Drivers

**What makes a good decision driver**:

- Specific and measurable when possible
- Prioritized (if order matters)
- Balanced between business and technical

**Categories to consider**:

- **Business**: Cost, time-to-market, competitive advantage
- **Technical**: Performance, scalability, reliability, security
- **Team**: Skills, learning curve, hiring market
- **Operational**: Monitoring, debugging, maintenance
- **Compliance**: Regulatory, legal, policy requirements

**Good example**:

```markdown
## Decision Drivers

* Must support 10,000 concurrent users (current: 1,000)
* Team has strong Python expertise, limited Java/Go experience
* Budget constraint: max $5,000/month infrastructure cost
* Must comply with HIPAA security requirements
* Prefer open-source to avoid vendor lock-in
* Need to deploy within 3 months
```

**Bad example**:

```markdown
## Decision Drivers

* Performance
* Cost
* Easy to use
```

### 4. Considered Options

**Best practices**:

- List 2-5 realistic options (not straw men)
- Put chosen option first (aids scanning)
- Brief description if not obvious
- Link to detailed analysis if extensive

**Good example**:

```markdown
## Considered Options

* PostgreSQL with read replicas - Industry-standard RDBMS, strong consistency
* MongoDB - Document database, flexible schema
* DynamoDB - Managed NoSQL, serverless pricing
* Cassandra - Distributed database, eventual consistency
```

**Bad example**:

```markdown
## Considered Options

* PostgreSQL
* Everything else (rejected because PostgreSQL is better)
```

### 5. Decision Outcome

**Structure**:

1. State the choice clearly
1. Provide brief justification (1-3 sentences)
1. Reference decision drivers satisfied

**Good example**:

```markdown
## Decision Outcome

Chosen option: "PostgreSQL with read replicas", because it best satisfies
our needs for ACID transactions and complex queries while leveraging our
team's existing SQL expertise. Read replicas address our scaling concerns
for the 10,000 concurrent users requirement at a predictable cost within
our $5,000/month budget.
```

**Bad example**:

```markdown
## Decision Outcome

We chose PostgreSQL because it's good.
```

### 6. Consequences

**What to include**:

- **Positive consequences**: Benefits, improvements, opportunities
- **Negative consequences**: Trade-offs, limitations, risks
- **Neutral consequences**: Changes without clear value judgment
- **Follow-up decisions**: What decisions does this enable/require?

**Be honest**: Don't hide downsides. Future you will thank you.

**Good example**:

```markdown
### Consequences

* Good, because PostgreSQL ACID guarantees ensure data consistency
* Good, because team already has SQL expertise, minimal learning curve
* Good, because rich ecosystem of tools and libraries
* Bad, because we'll need to implement caching layer for read-heavy workloads
* Bad, because horizontal scaling is more complex than with NoSQL options
* Neutral, because we'll need to establish backup and recovery procedures
* Follow-up, because we need to decide on caching strategy (Redis vs. Memcached)
```

**Bad example**:

```markdown
### Consequences

* It will be great!
```

### 7. Pros and Cons of Options

For each considered option:

- **Good**: Benefits and advantages
- **Bad**: Drawbacks and disadvantages
- **Neutral**: Facts without judgment

**Good example**:

```markdown
### PostgreSQL with Read Replicas

* Good, because mature, battle-tested technology with 25+ years of development
* Good, because strong ACID guarantees prevent data inconsistency issues
* Good, because team has 5 years of PostgreSQL experience
* Good, because rich support for JSON columns provides schema flexibility
* Bad, because read replicas add operational complexity (monitoring, lag)
* Bad, because vertical scaling limits on single-node writes
* Bad, because replication lag can cause read-after-write inconsistency
* Neutral, because requires managed hosting or dedicated DBA time

### MongoDB

* Good, because flexible schema enables rapid iteration
* Good, because horizontal scaling built into architecture
* Good, because JSON-native storage matches API format
* Bad, because team has no MongoDB production experience (hiring/training cost)
* Bad, because eventual consistency model complicates some use cases
* Bad, because smaller ecosystem than PostgreSQL for our language (Python)
* Neutral, because requires learning new query language and patterns
```

### 8. Validation/Confirmation (Optional but Recommended)

**Include for important decisions**:

- How will we know if this was the right choice?
- What metrics will we track?
- What would trigger revisiting this decision?
- How will we enforce this decision?

**Good example**:

```markdown
## Validation

We will validate this decision after 6 months by measuring:

* Query performance: 95th percentile < 100ms (baseline: 150ms)
* System uptime: 99.9% (baseline: 99.5%)
* Developer productivity: Story cycle time reduced by 20%
* Infrastructure cost: Remains under $5,000/month

We will revisit this decision if:

* Query performance degrades below baseline despite optimization
* Infrastructure costs exceed $7,500/month (50% over budget)
* Team grows beyond 25 developers (scaling concerns)
* Regulatory requirements change (ACID may not be sufficient)
```

## AI Assistant Review Checklist

When reviewing an ADR, check:

### Completeness

- [ ] Title is clear and concise
- [ ] Context explains the situation and problem
- [ ] Decision drivers are specific and prioritized
- [ ] Multiple options were considered (minimum 2)
- [ ] Decision outcome is clearly stated
- [ ] Consequences include both positive and negative
- [ ] Metadata is present (status, date, deciders if using full template)

### Quality

- [ ] Problem is clearly articulated before solution
- [ ] Decision drivers are specific, not vague
- [ ] Options are realistic, not straw men
- [ ] Justification references decision drivers
- [ ] Consequences are honest about trade-offs
- [ ] Appropriate detail level for decision significance
- [ ] Links to supporting materials where appropriate

### Style

- [ ] Written in past tense (records decision made, not proposal)
- [ ] Clear, concise language
- [ ] Technical terms explained or linked
- [ ] Consistent formatting
- [ ] Proper markdown syntax

### Content Issues to Flag

- [ ] **Solution in search of problem**: Starts with "we should use X" without explaining why
- [ ] **Missing context**: Assumes reader knows background
- [ ] **Only one option**: No alternatives considered
- [ ] **Vague decision drivers**: "Better performance" without specifics
- [ ] **Hiding trade-offs**: Only positive consequences
- [ ] **Straw man alternatives**: Unrealistic options that make choice obvious
- [ ] **Too detailed**: Implementation details instead of decision rationale
- [ ] **Too vague**: No specific information to understand decision
- [ ] **Status unclear**: No indication if proposed, accepted, or superseded

## Common Pitfalls and How to Avoid Them

### Pitfall 1: Writing a Proposal Instead of a Record

**Problem**: ADR written in future tense, sounds like a proposal

**Wrong**:

```markdown
We should use React because it will be better.
```

**Right**:

```markdown
We decided to use React because our team has 3 years of React experience
and it best supports our need for complex interactive UIs.
```

**AI Guidance**: Ensure ADR is written in past tense documenting a decision made, not proposing a decision to make.

### Pitfall 2: Assuming Context

**Problem**: ADR assumes reader knows the background

**Wrong**:

```markdown
## Context

The current situation isn't working.
```

**Right**:

```markdown
## Context

Our current REST API serves 50 endpoints across 10 resources. Each client
makes an average of 15 requests per page load, causing poor mobile performance.
Our mobile team has requested a more efficient data fetching mechanism.
```

**AI Guidance**: Ask questions to extract context. Who? What? When? Why now?

### Pitfall 3: Solution-First Thinking

**Problem**: Starting with the solution instead of the problem

**Wrong**:

```markdown
## Problem

We need to use Kubernetes.
```

**Right**:

```markdown
## Problem

Our application experiences unpredictable traffic spikes (10x baseline)
during events, causing outages. Manual scaling takes 30+ minutes,
resulting in lost revenue and poor user experience.
```

**AI Guidance**: Ask "What problem are we solving?" before discussing solutions.

### Pitfall 4: Vague Decision Drivers

**Problem**: Decision drivers too generic to be useful

**Wrong**:

```markdown
* Good performance
* Low cost
* Easy to use
```

**Right**:

```markdown
* Must handle 10,000 requests/second (current: 1,000)
* Infrastructure cost must stay under $5,000/month
* Team should be productive within 2 weeks of learning
```

**AI Guidance**: Ask for specifics. "How much?" "By when?" "Compared to what?"

### Pitfall 5: Ignoring Trade-offs

**Problem**: Only listing benefits, hiding downsides

**Wrong**:

```markdown
### Consequences

* Good, because Kubernetes is great
* Good, because everyone uses it
* Good, because it scales
```

**Right**:

```markdown
### Consequences

* Good, because handles our traffic spikes automatically
* Good, because enables zero-downtime deployments
* Bad, because adds significant operational complexity
* Bad, because requires 6 months for team to become proficient
* Bad, because increases infrastructure costs by $3,000/month
```

**AI Guidance**: Explicitly ask "What are the downsides of this decision?"

### Pitfall 6: Analysis Paralysis

**Problem**: Too much detail, loses the forest for the trees

**Wrong**: 50-page document with every technical detail

**Right**: 2-3 page ADR with links to detailed analysis

**AI Guidance**: Focus on decision rationale, not implementation. Details can be links.

### Pitfall 7: Straw Man Alternatives

**Problem**: Listing unrealistic options to make choice obvious

**Wrong**:

```markdown
## Options

* PostgreSQL - mature, reliable
* Building our own database from scratch in PHP - terrible idea
* Using Excel files on a shared drive - obviously won't work
```

**Right**:

```markdown
## Options

* PostgreSQL - mature RDBMS, strong consistency
* MongoDB - flexible schema, horizontal scaling
* DynamoDB - managed service, serverless pricing
```

**AI Guidance**: Ensure alternatives are realistic options actually considered.

## Asking Good Questions

As an AI assistant, ask questions to extract information:

### Understanding the Problem

- "What problem are you trying to solve?"
- "What happens if you don't make this decision?"
- "What's the impact of the current situation?"
- "Who is affected and how?"
- "Why is this a priority now?"

### Understanding Constraints

- "What constraints limit your options?" (time, budget, skills, etc.)
- "Are there regulatory or compliance requirements?"
- "What's your team's existing expertise?"
- "What infrastructure do you already have?"
- "What's your risk tolerance for this decision?"

### Understanding Options

- "What alternatives have you considered?"
- "Why were other options rejected?"
- "What would it take to make [alternative] work?"
- "Are there hybrid approaches?"

### Understanding Trade-offs

- "What are the downsides of this choice?"
- "What will be harder because of this decision?"
- "What future options does this close off?"
- "What's the worst-case scenario?"
- "What will you lose by not choosing [alternative]?"

### Understanding Validation

- "How will you know if this was the right decision?"
- "What would make you revisit this decision?"
- "What metrics will you track?"
- "When will you evaluate the outcome?"

## Example: Helping Write an ADR

### User Query

> "Help me write an ADR about using React for our new web app"

### Good AI Response Process

**Step 1: Understand Context**

```
I'll help you write an ADR for choosing React. First, let me understand
the context:

1. What problem are you solving that led to choosing React?
2. What other frameworks did you consider (Vue, Angular, Svelte, etc.)?
3. What are your team's constraints (expertise, timeline, budget)?
4. Are there specific requirements driving this decision (performance,
   ecosystem, hiring, etc.)?
5. What's your project size and expected team size?
```

**Step 2: Extract Decision Drivers**

```
Based on your answers, it sounds like your key decision drivers are:

* Team already has 2 React developers, 0 for other frameworks
* Need to hire 3 more developers (React hiring pool larger)
* Application requires complex interactive UI with state management
* Timeline: must launch in 6 months
* Prefer strong TypeScript support

Does that capture it? Any other important factors?
```

**Step 3: Identify Trade-offs**

```
What are the downsides of choosing React over the alternatives?
For example:
* Does React's frequent breaking changes concern you?
* Are you worried about the learning curve for Redux/state management?
* Any concerns about bundle size compared to lighter alternatives?
```

**Step 4: Draft ADR**

```
Here's a draft ADR. Let me know what needs adjustment:

# Use React for Web Application Frontend

## Context and Problem Statement

We are building a new web application for [purpose] that requires
[specific UI requirements]. Our current team has [team composition]
and we need to hire [number] additional frontend developers within
[timeline].

We need to choose a frontend framework that enables us to deliver
a production application in 6 months while setting us up for long-term
maintainability and team growth.

## Decision Drivers

* Team has 2 developers with React experience, 0 with other frameworks
* Must hire 3 developers within 6 months (hiring market considerations)
* Requires complex state management for [specific features]
* Need strong TypeScript support for type safety
* Timeline pressure: 6 months to production

[... rest of ADR ...]

Does this accurately capture your decision? What should I adjust?
```

## Example: Reviewing an ADR

### User Submission (Problematic)

```markdown
# Use Microservices

## Context

Our app is slow.

## Decision

We decided to use microservices because they're better and Netflix uses them.

## Consequences

* Everything will be faster
* It will scale better
```

### Good AI Review Response

```
I've reviewed your ADR and have several suggestions to make it more useful:

**Missing Context**:
* What specifically is slow? (API response times? Deployment? Development?)
* How slow? (Quantify: "API p95 is 2s, need < 500ms")
* Why is this a priority now?
* What's your current architecture? (Monolith? Distributed? Size?)

**Vague Decision**:
* What specific microservices architecture? (How many services? Boundaries?)
* What alternatives did you consider? (Modular monolith? Serverless? Different service boundaries?)
* What criteria led to this choice beyond "better"?

**Missing Decision Drivers**:
* What requirements must the solution meet?
* What constraints do you have? (Team size, skills, budget, timeline)
* What qualities matter most? (Development velocity? Scalability? Reliability?)

**Unrealistic Consequences**:
* "Everything will be faster" - What specific improvements do you expect?
* Missing trade-offs - What will be harder? (Deployment? Debugging? Distributed transactions?)
* No concrete metrics or validation plan

**Comparison Issues**:
* "Netflix uses them" - Netflix has very different scale and challenges
* No evaluation of whether your needs match Netflix's situation

Would you like help filling in these gaps? Let's start with: What specific
problem led to this decision?
```

## Conclusion

When helping with ADRs, remember:

1. **Understand context first**: Ask questions before writing
1. **Focus on "why"**: The decision rationale matters most
1. **Be honest about trade-offs**: Every choice has downsides
1. **Match formality to need**: Don't over-engineer for simple decisions
1. **Make it useful**: Future readers should understand the decision
1. **Guide, don't dictate**: Help users think through the decision

A good ADR answers:

- **What** was decided
- **Why** it was needed
- **How** the decision was made (alternatives considered)
- **Who** was involved
- **When** it was decided
- **What** the consequences are

If an ADR answers these questions clearly, it will serve its purpose: helping future readers understand and trust the decision.
