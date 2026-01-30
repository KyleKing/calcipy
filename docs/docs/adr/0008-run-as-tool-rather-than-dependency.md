# Run as Tool Rather Than Dependency

- Status: accepted
- Date: 2026-01-30
- Deciders: KyleKing
- Informed: calcipy users

## Context and Problem Statement

calcipy can be used either as a project dependency or as a standalone tool. Users encounter several challenges when using calcipy as a dependency:

1. **Dependency conflicts** that complicate or prevent installation
2. **Python version constraints** - Projects may be limited by calcipy's minimum Python version
3. **Unclear usage patterns** - Some tasks work standalone, others require project context
4. **Complex extras management** - Users must choose the right extras for their needs

The question is: Should calcipy prioritize being a standalone tool or a project dependency?

## Decision Drivers

- Must minimize dependency conflicts for users
- Must allow calcipy to drop support for older Python versions independently
- Must provide clear guidance on tool vs dependency usage
- Must identify which tasks can run standalone vs in project context
- Should make adoption easier by reducing integration friction
- Should simplify dependency management

## Considered Options

- **Tool-only approach** - Refactor all tasks to run standalone via uvx/pipx
- **Dependency-only approach** - Require calcipy as project dependency
- **Hybrid approach with clear boundaries** - Document and package for both, with clear guidance
- **Split into separate packages** - calcipy-tool and calcipy-lib

## Decision Outcome

Chosen option: "Hybrid approach with clear boundaries", because it provides the best balance of flexibility while acknowledging that some tasks genuinely require project context.

We document which tasks work in each mode:

### Tool Mode (Standalone via `uvx` or `uv tool install`)

Install with: `uv tool install 'calcipy[tool]'` or use via `uvx --from 'calcipy[tool]' calcipy-lint`

**Supported tasks:**
- ✅ **calcipy-lint** - Linting with ruff (minimal assumptions about project structure)
- ✅ **calcipy-tags** - Code tag collection (works on any directory)

**Benefits of tool mode:**
- No dependency conflicts with project
- calcipy can use newer Python features independently
- Faster to try out without modifying project
- Works across multiple projects

**Limitations:**
- Cannot access project-specific configuration deeply
- May make assumptions about project structure

### Project Dependency Mode

Install with: `uv add --dev 'calcipy[recommended]'` or specific extras

**Required for:**
- ❌ **calcipy-test** - Requires project's test dependencies and package name
- ❌ **calcipy-types** - Requires project's type stubs and code
- ❌ **calcipy-docs** - Requires project's documentation dependencies and structure
- ⚠️ **calcipy-pack** - Most tasks require project context (lock is standalone)
- ⚠️ **calcipy (full)** - Main task pipeline requires project context

**Benefits of dependency mode:**
- Full integration with project configuration
- Access to project dependencies
- Coordinated version management
- All tasks available

### Tool Extra Definition

The `[tool]` extra includes minimal dependencies for standalone usage:

```toml
[project.optional-dependencies]
tool = [
  "calcipy[lint,tags]",
]
```

This installs:
- Core: beartype, corallium, invoke
- Lint: ruff
- Tags: arrow, pyyaml

### Consequences

- Good, because reduces dependency conflicts for tool-mode usage
- Good, because calcipy can drop Python version support independently
- Good, because clear documentation prevents confusion
- Good, because lightweight tool installation for lint/tags
- Good, because adopters can try calcipy without committing
- Good, because supports both use cases based on actual capabilities
- Bad, because maintains complexity of two installation modes
- Bad, because some tasks still require project installation
- Neutral, because requires user to understand which mode for which task

## Validation Strategy

This decision will be validated through:

1. **Installation testing** - Verify tool mode works with uvx/pipx
2. **Cross-project usage** - Test lint/tags on projects without calcipy installed
3. **Documentation feedback** - Monitor user questions about installation
4. **Adoption metrics** - Track if tool mode increases adoption

We would revisit this decision if:

- Majority of tasks can be refactored to work standalone
- User confusion about modes becomes significant
- Python ecosystem provides better isolation mechanisms
- Template-based approach (calcipy_template) makes dependency mode obsolete

## Future Work

Potential improvements (not part of this minimal implementation):

1. **Refactor more tasks to be tool-safe** - Reduce dependency on project context
2. **Move project-specific tasks to template** - Distribute via calcipy_template instead
3. **Improve lint to work without pyproject.toml** - Accept explicit targets
4. **Create calcipy-tool package** - Separate ultra-lightweight tool-only package
5. **Migrate to mise/task-based approach** - See wip-tooling-refactor.md

## More Information

- Tool extra configuration: `/pyproject.toml` under `[project.optional-dependencies]`
- Installation examples: `/docs/README.md` Installation section
- Related: ADR-0007 (Multiple CLI Entry Points)
- Future roadmap: `/wip-tooling-refactor.md`
- Issue: "Run as 'Tool' rather than a Dependency"
