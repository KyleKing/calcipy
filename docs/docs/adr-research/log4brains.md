# log4brains - Architecture Decision Records Management Tool

## Overview

log4brains is an open-source tool that enables teams to document and publish Architecture Decision Records (ADRs) as a searchable knowledge base. It treats documentation as code, storing ADR files in markdown format within your git repository.

**Website**: https://github.com/thomvaill/log4brains **Live Example**: https://thomvaill.github.io/log4brains/adr/

## Key Features

- **Local preview with hot-reload editing**: Real-time preview of ADR changes during authoring
- **Interactive CLI**: Guided creation of new ADRs from customizable templates
- **Static site generation**: Publish to GitHub/GitLab Pages or S3
- **Automatic metadata extraction**: Pulls information from git history and document content
- **Multi-package support**: Works with both single and multi-package projects
- **Searchable timeline interface**: No enforced numbering schema, flexible organization

## How It Works

### Workflow

1. **Initialize**: Run `log4brains init` to configure the tool
1. **Preview**: Use `log4brains preview` to see changes in real-time
1. **Create**: Run `log4brains adr new` to create new decisions (uses MADR template by default)
1. **Build**: Execute `log4brains build` to generate static website for deployment

### ADR Properties

Each ADR record contains:

- **Slug**: Unique identifier (e.g., "20200924-use-markdown-architectural-decision-records")
- **Title**: Descriptive name of the decision
- **Status**: One of four states—proposed, accepted, superseded, or deprecated
- **Creation Date**: When the ADR was written
- **Publication Date**: When it became effective
- **Package**: Optional categorization (e.g., "web", "core", or null for project-wide)

### Status Workflow

The decision process follows these stages:

1. **Proposed** - Initial submission
1. **Accepted** - Approved and implemented
1. **Superseded** - Replaced by a newer ADR
1. **Deprecated** - No longer relevant

## ADR Philosophy

Following Michael Nygard's methodology, log4brains treats ADRs as immutable records capturing context, decisions, and consequences. As the documentation notes:

> "Only its status can change. Thanks to this, your documentation is never out-of-date!"

This approach prevents blind reversals of past decisions while facilitating developer onboarding through documented rationale rather than tribal knowledge.

## Storage and Integration

- **Format**: Markdown files
- **Version Control**: Stored alongside code in git (typically on `develop` branch)
- **Integration**: Automatically integrated into documentation
- **Collaboration**: Designed to support team decision-making backed by pull requests

## Benefits

- Creates a permanent architectural knowledge base
- Prevents loss of decision context when team members leave
- Reduces repetitive discussions about past decisions
- Improves onboarding for new developers
- Makes architectural evolution transparent

## Use Cases

- **Best for**: Teams that want a polished, searchable website for their ADRs
- **Project Size**: Small to large projects
- **Team Size**: Works well for distributed teams
- **Integration**: Teams already using git-based workflows
