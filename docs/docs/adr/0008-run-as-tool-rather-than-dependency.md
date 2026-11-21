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

Install with individual extras for efficiency:
- `uv tool install 'calcipy[lint]'` - For linting only
- `uv tool install 'calcipy[tags]'` - For code tag collection only
- `uv tool install 'calcipy[experimental]'` - For experimental features
- `uv tool install 'calcipy[lint,tags]'` - For multiple features

Or use transiently via uvx:
- `uvx --from 'calcipy[lint]' calcipy-lint lint.check file.py`
- `uvx --from 'calcipy[tags]' calcipy-tags tags --base-dir=.`

**Supported tasks:**
- ✅ **calcipy-lint** - Linting with ruff (requires `[lint]` extra)
  - Works with explicit file arguments: `calcipy-lint lint.check file.py`
  - Works in projects with pyproject.toml: `calcipy-lint lint.check`
  - Limitation: Without explicit files and without pyproject.toml, will fail trying to detect package
- ✅ **calcipy-tags** - Code tag collection (requires `[tags]` extra)
  - Works on any directory (use `--ignore-repo-root` flag for non-git directories)
  - Example: `calcipy-tags tags --base-dir=/path/to/project --ignore-repo-root`
- ✅ **calcipy-experiments** - Experimental features (requires `[experimental]` extra)
  - `bump-tag` - Suggest version bump using griffe to detect breaking changes
  - `sync-pyproject-versions` - Sync pyproject.toml versions from uv.lock
  - `check-duplicate-tests` - Check for duplicate test names in test suite

**Benefits of tool mode:**
- No dependency conflicts with project
- calcipy can use newer Python features independently
- Faster to try out without modifying project
- Works across multiple projects
- Composable extras allow installing only what you need

**Limitations:**
- Cannot fully access project-specific configuration
- May make assumptions about project structure

### Project Dependency Mode

Install with: `uv add --dev 'calcipy[recommended]'` or specific extras

**Required for:**
- ❌ **calcipy-test** - Requires project's test dependencies and package name
- ❌ **calcipy-types** - Requires project's type stubs and code
- ❌ **calcipy-docs** - Requires project's documentation dependencies and structure
- ⚠️ **calcipy-pack** - Most tasks require project context
- ⚠️ **calcipy (full)** - Main task pipeline requires project context

**Benefits of dependency mode:**
- Full integration with project configuration
- Access to project dependencies
- Coordinated version management
- All tasks available

### Composable Extras Design

Instead of a monolithic `[tool]` extra, calcipy uses composable extras that users can mix and match:

- `[lint]` - Minimal linting (ruff only)
- `[tags]` - Code tag collection (arrow, pyyaml)
- `[experimental]` - Experimental features (griffe, semver)
- `[test]` - Testing tools (pytest, coverage)
- `[types]` - Type checking (mypy, ty)
- `[doc]` - Documentation (mkdocs and plugins)
- `[recommended]` - All common development tools

Users install only what they need:
- Tool mode: `calcipy[lint]` or `calcipy[lint,tags]`
- Dev dependency: `calcipy[recommended]` or custom combinations

### Consequences

- Good, because reduces dependency conflicts for tool-mode usage
- Good, because calcipy can drop Python version support independently
- Good, because clear documentation prevents confusion
- Good, because composable extras allow installing only what you need
- Good, because adopters can try calcipy without committing
- Good, because supports both use cases based on actual capabilities
- Good, because experimental features exposed as tool without project dependency
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

- Composable extras configuration: `/pyproject.toml` under `[project.optional-dependencies]`
- CLI entry points: `/pyproject.toml` under `[project.scripts]`
- Installation examples: `/docs/README.md` Installation section
- Related: ADR-0007 (Multiple CLI Entry Points)
- Future roadmap: `/wip-tooling-refactor.md`
- Issue: "Run as 'Tool' rather than a Dependency"
