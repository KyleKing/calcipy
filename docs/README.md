# calcipy

![./calcipy-banner-wide.svg](https://raw.githubusercontent.com/KyleKing/calcipy/main/docs/calcipy-banner-wide.svg)

`calcipy` is a Python package that implements best practices such as code style (linting, auto-fixes), documentation, CI/CD, and logging. Like the calcium carbonate in hard coral, packages can be built on the `calcipy` foundation.

`calcipy` has some configurability, but is tailored for my particular use cases. If you want the same sort of functionality, there are a number of alternatives to consider:

- [pyscaffold](https://github.com/pyscaffold/pyscaffold) is a much more mature project that aims for the same goals, but with a slightly different approach and tech stack (tox vs. nox, cookiecutter vs. copier, etc.)
- [tidypy](https://github.com/jayclassless/tidypy#features), [pylama](https://github.com/klen/pylama), and [codecheck](https://pypi.org/project/codecheck/) offer similar functionality of bundling and running static checkers, but makes far fewer assumptions
- [pytoil](https://github.com/FollowTheProcess/pytoil) is a general CLI tool for developer automation
- And many more such as [pyta](https://github.com/pyta-uoft/pyta), [prospector](https://github.com/PyCQA/prospector), [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide) / [cjolowicz/cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python), [formate](https://github.com/python-formate/formate), [johnthagen/python-blueprint](https://github.com/johnthagen/python-blueprint), [oxsecurity/megalinter](https://github.com/oxsecurity/megalinter)etc.

## Installation

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

See [./Advanced_Configuration.md](./Advanced_Configuration.md) for documentation on the configurable aspects of `calcipy`

### Calcipy CLI

Additionally, `calcipy` can be run as a CLI application without adding the package as a dependency.

Quick Start:

```sh
pipx install calcipy

# Use the Collect Code Tags command to write all code tags to a single file
calcipy collect-code-tags -h
calcipy collect-code-tags -b=~/Some/Project

# See additional documentation from the CLI help
calcipy -h
```

### Calcipy Pre-Commit

`calcipy` can also be used as a `pre-commit` task by adding the below snippet to your `pre-commit` file:

```yaml
repos:
  - repo: https://github.com/KyleKing/calcipy
    rev: main
    hooks:
      - id: calcipy-code-tags
```

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
    - **pre_commit_hooks**: Run the pre-commit hooks on all files.
    - **lint_project**: Lint all project files that can be checked. (py, yaml, json, etc.)
    - **static_checks**: General static checkers (Inspection Tiger, etc.).
    - **security_checks**: Use linting tools to identify possible security vulnerabilities.
    - **check_types**: Run type annotation checks.

- Additional tasks include:

  - **nox**/**test**/**coverage**: Tasks for running nox sessions, pytest in the local environment, and pytest coverage
  - **ptw\_\***: Variations of tasks to run pytest watch
  - **cl_bump** (**cl_bump_pre**):Bumps project version based on commits & settings in pyproject.toml.
  - **deploy_docs**: Deploy docs to the Github `gh-pages` branch.
  - **publish**: Build the distributable format(s) and publish.
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

> NOTE
>
> For the full list of available tasks, run `poetry run doit list`

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

[changelog]: ./docs/CHANGELOG.md
[code_tag_summary]: ./docs/CODE_TAG_SUMMARY.md
[contributor-covenant]: https://www.contributor-covenant.org
[developer_guide]: ./docs/DEVELOPER_GUIDE.md
[license]: https://github.com/kyleking/calcipy/LICENSE
[style_guide]: ./docs/STYLE_GUIDE.md
