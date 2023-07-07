# calcipy

![./calcipy-banner-wide.svg](https://raw.githubusercontent.com/KyleKing/calcipy/main/docs/calcipy-banner-wide.svg)

`calcipy` is a Python package that implements best practices such as code style (linting, auto-fixes), documentation, CI/CD, and logging. Like the calcium carbonate in hard coral, packages can be built on the `calcipy` foundation.

`calcipy` has some configurability, but is tailored for my particular use cases. If you want the same sort of functionality, there are a number of alternatives to consider:

- [pyscaffold](https://github.com/pyscaffold/pyscaffold) is a much more mature project that aims for the same goals, but with a slightly different approach and tech stack (tox vs. nox, cookiecutter vs. copier, etc.)
- [tidypy](https://github.com/jayclassless/tidypy#features), [pylama](https://github.com/klen/pylama), and [codecheck](https://pypi.org/project/codecheck/) offer similar functionality of bundling and running static checkers, but makes far fewer assumptions
- [pytoil](https://github.com/FollowTheProcess/pytoil) is a general CLI tool for developer automation
- And many more such as [pyta](https://github.com/pyta-uoft/pyta), [prospector](https://github.com/PyCQA/prospector), [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide) / [cjolowicz/cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python), [formate](https://github.com/python-formate/formate), [johnthagen/python-blueprint](https://github.com/johnthagen/python-blueprint), [oxsecurity/megalinter](https://github.com/oxsecurity/megalinter), etc.

## Installation

Calcipy needs a few static files managed using copier and a template project: [kyleking/calcipy_template](https://github.com/KyleKing/calcipy_template/)

You can quickly use the template to create a new project or add calcipy to an existing one:

```sh
# Install copier. pipx is recommended
pipx install copier

# To create a new project
copier copy gh:KyleKing/calcipy_template new_project
cd new_project

# Or convert/update an existing one
cd my_project
copier copy gh:KyleKing/calcipy_template .
copier update
```

See [./Advanced_Configuration.md](./Advanced_Configuration.md) for documentation on the configurable aspects of `calcipy`

### Calcipy CLI

Additionally, `calcipy` can be run as a CLI application without adding the package as a dependency.

Quick Start:

```sh
# For the CLI, only install a few of the extras which can be used from a few different CLI commands
pipx install 'calcipy[flake8,lint,tags]'

# Use 'tags' to create a CODE_TAG_SUMMARY of the specified directory
calcipy-tags tags --help
calcipy-tags tags --base-dir=~/path/to/my_project

# You can list all provided CLI commands with
pipx list
```

```txt
venvs are in ~/.local/pipx/venvs
apps are exposed on your $PATH at ~/.local/bin
   package calcipy 1.4.0, installed using Python 3.11.4
    - calcipy
    - calcipy-lint
    - calcipy-pack
    - calcipy-tags
    - calcipy-types
```

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

  lint.autopep8       Run autopep8.
  lint.check (lint)   Run ruff as check-only.
  lint.fix            Run ruff and apply fixes.
  lint.flake8         Run flake8.
  lint.pre-commit     Run pre-commit.
  lint.pylint         Run pylint.
  lint.security       Attempt to identify possible security vulnerabilities.
  lint.watch          Run ruff as check-only.

Global Task Options:

  *file_args             List of Paths available globally to all tasks. Will resolve paths with working_dir
  --keep-going           Continue running tasks even on failure
  --working_dir=STRING   Set the cwd for the program. Example: "../run --working-dir .. lint test"
  -v,-vv,-vvv            Globally configure logger verbosity (-vvv for most verbose)

> calcipy-pack

Subcommands:

  pack.check-licenses   Check licenses for compatibility with `licensecheck`.
  pack.install-extras   Run poetry install with all extras.
  pack.lock             Ensure poetry.lock is  up-to-date.
  pack.publish          Build the distributed format(s) and publish.

> calcipy-tags

Subcommands:

  tags.collect-code-tags (tags)   Create a `CODE_TAG_SUMMARY.md` with a table          for TODO- and FIXME-style code comments.

> calcipy-types

Subcommands:

  types.mypy      Run mypy.
  types.pyright   Run pyright.
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
