# calcipy

![./calcipy-banner-wide.svg](https://raw.githubusercontent.com/KyleKing/calcipy/main/docs/calcipy-banner-wide.svg)

`calcipy` is a Python package that implements best practices such as code style (linting, auto-fixes), documentation, CI/CD, and logging. Like the calcium carbonate in hard coral, packages can be built on the `calcipy` foundation.

`calcipy` has some configurability, but is tailored for my particular use cases. If you want the same sort of functionality, there are a number of alternatives to consider:

- [pyscaffold](https://github.com/pyscaffold/pyscaffold) is a much more mature project that aims for the same goals, but with a slightly different approach and tech stack (tox vs. nox, cookiecutter vs. copier, etc.)
- [tidypy](https://github.com/jayclassless/tidypy#features), [pylama](https://github.com/klen/pylama), and [codecheck](https://pypi.org/project/codecheck/) offer similar functionality of bundling and running static checkers, but makes far fewer assumptions
- [pytoil](https://github.com/FollowTheProcess/pytoil) is a general CLI tool for developer automation
- And many more such as [pyta](https://github.com/pyta-uoft/pyta), [prospector](https://github.com/PyCQA/prospector), [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide) / [cjolowicz/cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python), [formate](https://github.com/python-formate/formate), [johnthagen/python-blueprint](https://github.com/johnthagen/python-blueprint), [oxsecurity/megalinter](https://github.com/oxsecurity/megalinter), [trialandsuccess/su6](https://github.com/trialandsuccess/su6), [precious](https://github.com/houseabsolute/precious), etc.

## Installation

`calcipy` can be used in two ways:

### 1. As a Standalone Tool (Recommended for Linting & Code Analysis)

Use `calcipy` as a standalone tool without adding it as a dependency. This is ideal for:

- **Linting**: Running `ruff` on any Python codebase
- **Code Tag Collection**: Creating TODO/FIXME summaries for any project

```sh
# Install as a tool (minimal dependencies)
uv tool install 'calcipy[tool]'

# Or use without installing via uvx
uvx --from 'calcipy[tool]' calcipy-lint --help
uvx --from 'calcipy[tool]' calcipy-tags --help

# Examples
calcipy-lint lint --help
calcipy-lint lint  # Lint current directory

calcipy-tags tags --help
calcipy-tags tags --base-dir=~/path/to/my_project
```

**Tool Mode Capabilities:**

- ✅ `calcipy-lint` - Lint any Python codebase
- ✅ `calcipy-tags` - Collect code tags from any directory
- ⚠️ Other commands require project context (see below)

### 2. As a Project Dependency (Full Development Environment)

Add `calcipy` to your project for the complete development workflow including testing, documentation, type-checking, and more.

#### Quick Start with Template

Calcipy works best with its companion template project: [kyleking/calcipy_template](https://github.com/KyleKing/calcipy_template/)

```sh
# Create a new project from template
uvx copier copy gh:KyleKing/calcipy_template new_project
cd new_project

# Or add to existing project
cd my_project
uvx copier copy gh:KyleKing/calcipy_template .
uvx copier update
```

#### Manual Installation

```sh
# Add as development dependency with all tools
uv add --dev 'calcipy[dev]'

# Or install specific extras
uv add --dev 'calcipy[test,doc,types]'
```

**Project Mode Capabilities:**

- `calcipy-test` - Run pytest with coverage
- `calcipy-types` - Type checking with mypy/pyright
- `calcipy-docs` - Build and deploy documentation
- `calcipy-pack` - Package building and publishing
- `calcipy` - Full task automation

Note: the CLI output below is compressed for readability, but you can try running each of these commands locally to see the most up-to-date documentation and the full set of options. The "Usage", "Core options", and "Global Task Options" are the same for each subsequent command, so they are excluded for brevity.

```txt
> calcipy-lint
Usage: calcipy-lint [--core-opts] <subcommand> [--subcommand-opts] ...

Core options:

  --complete                         Print tab-completion candidates for given parse remainder.
  --hide=STRING                      Set default value of run()'s 'hide' kwarg.
  --print-completion-script=STRING   Print the tab-completion script for your preferred shell (bash|zsh|fish).
  --prompt-for-sudo-password         Prompt user at start of session for the sudo.password config value.
  --write-pyc                        Enable creation of .pyc files.
  -d, --debug                        Enable debug output.
  -D INT, --list-depth=INT           When listing tasks, only show the first INT levels.
  -e, --echo                         Echo executed commands before running.
  -f STRING, --config=STRING         Runtime configuration file to use.
  -F STRING, --list-format=STRING    Change the display format used when listing tasks. Should be one of: flat (default), nested, json.
  -h [STRING], --help[=STRING]       Show core or per-task help and exit.
  -l [STRING], --list[=STRING]       List available tasks, optionally limited to a namespace.
  -p, --pty                          Use a pty when executing shell commands.
  -R, --dry                          Echo commands instead of running.
  -T INT, --command-timeout=INT      Specify a global command execution timeout, in seconds.
  -V, --version                      Show version and exit.
  -w, --warn-only                    Warn, instead of failing, when shell commands fail.

Subcommands:

  lint.check (lint)   Run ruff as check-only.
  lint.fix            Run ruff and apply fixes.
  lint.prek           Run prek.
  lint.watch          Run ruff as check-only.

Global Task Options:

  *file_args             List of Paths available globally to all tasks. Will resolve paths with working_dir
  --keep-going           Continue running tasks even on failure
  --working_dir=STRING   Set the cwd for the program. Example: "../run --working-dir .. lint test"
  -v,-vv,-vvv            Globally configure logger verbosity (-vvv for most verbose)

> calcipy-pack

Subcommands:

  pack.bump-tag                  Experiment with bumping the git tag using `griffe` (experimental).
  pack.lock                      Update package manager lock file.
  pack.publish                   Build the distributed format(s) and publish.
  pack.sync-pyproject-versions   Experiment with setting the pyproject.toml dependencies to the version from uv.lock (experimental).

> calcipy-tags

Subcommands:

  tags.collect-code-tags (tags)   Create a `CODE_TAG_SUMMARY.md` with a table for TODO- and FIXME-style code comments.

> calcipy-types

Subcommands:

  types.mypy      Run mypy.
  types.pyright   Run pyright using the config in `pyproject.toml`.
```

### Calcipy Pre-Commit

`calcipy` can also be used as a `pre-commit` task by adding the below snippet to your `pre-commit` file:

```yaml
repos:
  - repo: https://github.com/KyleKing/calcipy
    rev: main
    hooks:
      - id: tags
      - id: lint-fix
      - id: types
```

<!-- {cts} CLI_OUTPUT=./run --help; -->
```txt
Usage: calcipy [--core-opts] <subcommand> [--subcommand-opts] ...

Core options:

  --complete                         Print tab-completion candidates for given
                                     parse remainder.
  --hide=STRING                      Set default value of run()'s 'hide' kwarg.
  --print-completion-script=STRING   Print the tab-completion script for your
                                     preferred shell (bash|zsh|fish).
  --prompt-for-sudo-password         Prompt user at start of session for the
                                     sudo.password config value.
  --write-pyc                        Enable creation of .pyc files.
  -d, --debug                        Enable debug output.
  -D INT, --list-depth=INT           When listing tasks, only show the first
                                     INT levels.
  -e, --echo                         Echo executed commands before running.
  -f STRING, --config=STRING         Runtime configuration file to use.
  -F STRING, --list-format=STRING    Change the display format used when
                                     listing tasks. Should be one of: flat
                                     (default), nested, json.
  -h [STRING], --help[=STRING]       Show core or per-task help and exit.
  -l [STRING], --list[=STRING]       List available tasks, optionally limited
                                     to a namespace.
  -p, --pty                          Use a pty when executing shell commands.
  -R, --dry                          Echo commands instead of running.
  -T INT, --command-timeout=INT      Specify a global command execution
                                     timeout, in seconds.
  -V, --version                      Show version and exit.
  -w, --warn-only                    Warn, instead of failing, when shell
                                     commands fail.

Subcommands:

  main                            Run main task pipeline.
  other                           Run tasks that are otherwise not exercised in
                                  main.
  release                         Run release pipeline.
  cl.bump                         Bumps project version based on commits &
                                  settings in pyproject.toml.
  cl.write                        Write a Changelog file with the raw Git
                                  history.
  doc.build                       Build documentation with mkdocs.
  doc.deploy                      Deploy docs to the Github `gh-pages` branch.
  doc.watch                       Serve local documentation for local editing.
  lint.check (lint)               Run ruff as check-only.
  lint.fix                        Run ruff and apply fixes.
  lint.pre-commit                 Run prek.
  lint.watch                      Run ruff as check-only.
  nox.noxfile (nox)               Run nox from the local noxfile.
  pack.bump-tag                   Experiment with bumping the git tag using
                                  `griffe` (experimental).
  pack.lock                       Update package manager lock file.
  pack.sync-pyproject-versions    Experiment with setting the pyproject.toml
                                  dependencies to the version from uv.lock
                                  (experimental).
  tags.collect-code-tags (tags)   Create a `CODE_TAG_SUMMARY.md` with a table
                                  for TODO- and FIXME-style code comments.
  test.check                      Run pytest checks, such as identifying.
  test.coverage                   Generate useful coverage outputs after
                                  running pytest.
  test.pytest (test)              Run pytest with default arguments.
  test.watch                      Run pytest with polling and optimized to stop
                                  on first error.
  types.mypy                      Run mypy.
  types.pyright                   Run pyright using the config in
                                  `pyproject.toml`.
  types.ty                        Run ty type checker.

Global Task Options:

  *file_args             List of Paths available globally to all tasks. Will
                         resolve paths with working_dir
  --keep-going           Continue running tasks even on failure
  --working_dir=STRING   Set the cwd for the program. Example: "../run
                         --working-dir .. lint test"
  -v,-vv,-vvv            Globally configure logger verbosity (-vvv for most
                         verbose)
```
<!-- {cte} -->

Tip: running pre-commit with prek is recommended for performance: https://pypi.org/project/prek

## Project Status

See the `Open Issues` and/or the [CODE_TAG_SUMMARY]. For release history, see the [CHANGELOG].

## Contributing

We welcome pull requests! For your pull request to be accepted smoothly, we suggest that you first open a GitHub issue to discuss your idea. For resources on getting started with the code base, see the below documentation:

- [DEVELOPER_GUIDE]
- [STYLE_GUIDE]

## Code of Conduct

We follow the [Contributor Covenant Code of Conduct][contributor-covenant].

### Open Source Status

We try to reasonably meet most aspects of the "OpenSSF scorecard" from [Open Source Insights](https://deps.dev/pypi/calcipy)

## Responsible Disclosure

If you have any security issue to report, please contact the project maintainers privately. You can reach us at [dev.act.kyle@gmail.com](mailto:dev.act.kyle@gmail.com).

## License

[LICENSE]

[changelog]: https://calcipy.kyleking.me/docs/CHANGELOG
[code_tag_summary]: https://calcipy.kyleking.me/docs/CODE_TAG_SUMMARY
[contributor-covenant]: https://www.contributor-covenant.org
[developer_guide]: https://calcipy.kyleking.me/docs/DEVELOPER_GUIDE
[license]: https://github.com/kyleking/calcipy/blob/main/LICENSE
[style_guide]: https://calcipy.kyleking.me/docs/STYLE_GUIDE
