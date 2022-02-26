# calcipy

![./calcipy-banner-wide.svg](https://raw.githubusercontent.com/KyleKing/calcipy/main/docs/calcipy-banner-wide.svg)

`calcipy` is a Python package that implements best practices such as code style (linting, auto-fixes), documentation, CI/CD, and logging. Like the calcium carbonate in hard coral, packages can be built on the `calcipy` foundation.

`calcipy` has some configurability, but is tailored for my particular use cases. If you want the same sort of functionality, there are a number of alternatives to consider:

- [pyscaffold](https://github.com/pyscaffold/pyscaffold) is a much more mature project that aims for the same goals, but with a slightly different approach and tech stack (tox vs. nox, cookiecutter vs. copier, etc.)
- [tidypy](https://github.com/jayclassless/tidypy#features), [pylama](https://github.com/klen/pylama), and [codecheck](https://pypi.org/project/codecheck/) offer similar functionality of bundling and running static checkers, but makes far fewer assumptions
- [pytoil](https://github.com/FollowTheProcess/pytoil) is a general CLI tool for developer automation
- And many more such as [prospector](https://github.com/PyCQA/prospector), [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide) / [cjolowicz/cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python), etc.

## Calcipy CLI

`calcipy` can be run as a CLI application without adding the package as a dependency!

Quick Start:

```sh
pipx install calcipy

# Use the Collect Code Tags command to write all code tags to a single file
calcipy collect-code-tags -h
calcipy collect-code-tags -b=~/Some/Project


# See additional documentation from the CLI help
calcipy -h
```

To utilize all of the functionality from `calcipy`, see the following sections on adding `calcipy` as a dependency

## Calcipy Pre-Commit (beta!)

`calcipy` can also be used as a `pre-commit` task by adding the below snippet to your `pre-commit` file:

```yaml
repos:
  - repo: https://github.com/KyleKing/calcipy
    rev: main
    hooks:
      - id: calcipy-code-tags
```

This is a beta-feature that will be expanded with additional functionality as the CLI features are extended

## Calcipy Module Features

The core functionality of calcipy is the rich set of tasks run with `doit`

- `poetry run doit --continue`: runs all default tasks. On CI (AppVeyor), this is a shorter list that should PASS, while locally the list is longer that are much more strict for linting and quality analysis

  - The local default tasks include:
    - **collect_code_tags**: Create a summary file with all of the found code tags. (i.e. TODO/FIXME, default output is [./docs/CODE_TAG_SUMMARY.md](./docs/CODE_TAG_SUMMARY.md))
    - **cl_write**: Auto-generate the changelog based on commit history and tags.
    - **lock**: Ensure poetry.lock and requirements.txt are up-to-date.
    - **nox_coverage**: Run the coverage session in nox.
    - **auto_format**: Format code with isort, autopep8, and others.
    - **document**: Build the HTML documentation. (along with creating code diagrams!)
    - **check_for_stale_packages**: Check for stale packages.
    - **pre_commit_hooks**: Run the pre-commit hooks  on all files.
    - **lint_project**: Lint all project files that can be checked. (py, yaml, json, etc.)
    - **static_checks**: General static checkers (Inspection Tiger, etc.).
    - **security_checks**: Use linting tools to identify possible security vulnerabilities.
    - **check_types**: Run type annotation checks.

- Additional tasks of not:

  - **nox**/**test**/**coverage**: Tasks for running nox sessions, pytest in the local environment, and pytest coverage
  - **ptw\_\***: Variations of tasks to run pytest watch
  - **cl_bump** (**cl_bump_pre**):Bumps project version based on commits & settings in pyproject.toml.
  - **deploy_docs**: Deploy docs to the Github `gh-pages` branch.
  - **publish**: Build the distributable format(s) and publish.

- Other additional tasks include:

  - **check_license**: Check licenses for compatibility.
  - **lint_critical_only**: Suppress non-critical linting errors. Great for gating PRs/commits.
  - **lint_python**: Lint all Python files and create summary of errors.
  - **open_docs**: Open the documentation files in the default browser.
  - **open_test_docs**: Open the test and coverage files in default browser.
  - **zip_release**: Zip up important information in the releases directory.

- **calcipy** also provides a few additional nice features

  - **dev.conftest**: some additional pytest configuration logic that outputs better HTML reports. Automatically implemented (imported to `tests/conftest.py`) when using `calcipy_template`
  - **dev.noxfile**: nox functions that can be imported and run with or without the associated doit tasks. Also automatically configured when using `calcipy_template`
  - **file_helpers**: some nice utilities for working with files, such as `sanitize_filename`, `tail_lines`, `delete_old_files`, etc. See documentation for most up-to-date documentation
  - **log_heleprs**: where the most common use will be for `activate_debug_logging` or the more customizable `build_logger_config`
  - **dot_dict**: has one function `ddict`, which is a light-weight wrapper around whatever is the most [maintained dotted-dictionary package in Python](https://pypi.org/search/?q=dot+accessible+dictionary&o=). Dotted dictionaries can sometimes improve code readability, but they aren't a one-size fits all solution. Sometimes `attr.s` or `dataclass` are more appropriate.
    - The benefit of this wrapper is that there is a stable interface and you don't need to rewrite code as packages are born and die (i.e. [Bunch](https://pypi.org/project/bunch/) > [Chunk](https://pypi.org/project/chunk/) > [Munch](https://pypi.org/project/munch/) > [flexible-dotdict](https://pypi.org/project/flexible-dotdict/) > [Python-Box](https://pypi.org/project/python-box/) > ...)
    - Note: if you need nested dotted dictionaries, check out [classy-json](https://pypi.org/project/classy-json/)

**Tip**: For the full list of available tasks, run `poetry run doit list`

## Calcipy Installation

Calcipy needs a few static files managed using copier and a template project: [kyleking/calcipy_template](https://github.com/KyleKing/calcipy_template/)

You can quickly use the template to create a new project or add calcipy to an existing one:

```sh
# Install copier. Pipx is recommended
pipx install copier

# To create a new project
copier copy gh:KyleKing/calcipy_template new_project
cd new_project

# Or update an existing one
cd my_project
copier copy gh:KyleKing/calcipy_template .
```

## Usage

1. Run `poetry install`
1. Run `poetry run doit list` to see available tasks
1. And try `poetry run doit --continue` to see if the default tasks work

If you have any questions, please [start a Discussion on Github](https://github.com/KyleKing/calcipy/discussions/) or [open an issue for feature requests or bug reports](https://github.com/KyleKing/calcipy/issues/)

See [./Advanced_Configuration.md](./Advanced_Configuration.md) for documentation on the configurable aspects of `calcipy`

Additionally, for more examples, see other projects that use `calcipy`:

- [KyleKing/dash_charts](https://github.com/KyleKing/dash_charts) - *Active*
- [KyleKing/recipes](https://github.com/KyleKing/recipes) - *Active*
- [KyleKing/Goodreads_Library_Availability](https://github.com/KyleKing/Goodreads_Library_Availability) - *On Hold*
- [KyleKing/cz_legacy](https://github.com/KyleKing/cz_legacy) - *Published*
- See other [projects tagged with the topic "calcipy"](https://github.com/topics/calcipy)

## Updating Calcipy

Review the [./docs/CHANGELOG.md](./docs/CHANGELOG.md) before updating. Calcipy uses the year followed by standard semantic versioning to indicate major and minor changes. Note that this is a personal project and may change dramatically, but for the most part, the project should be relatively stable

```sh
# Update files
copier update
# and update dependencies
poetry update
```

## Roadmap

See the `Open Issues` and `Milestones` for current status and [./docs/CODE_TAG_SUMMARY.md](./docs/CODE_TAG_SUMMARY.md) for annotations in the source code.

For release history, see the [./docs/CHANGELOG.md](./docs/CHANGELOG.md)

## Contributing

See the Developer Guide, Contribution Guidelines, etc

- [./docs/DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md)
- [./docs/STYLE_GUIDE.md](./docs/STYLE_GUIDE.md)
- [./docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md)
- [./docs/CODE_OF_CONDUCT.md](./docs/CODE_OF_CONDUCT.md)
- [./docs/SECURITY.md](./docs/SECURITY.md)

## License

[LICENSE](https://github.com/KyleKing/calcipy/tree/main/LICENSE)
