# calcipy

![./calcipy.svg](./calcipy.svg)

`calcipy` is a Python package that implements best practices such as code style (linting, auto-fixes), documentation, CI/CD, and logging. Like the calcium carbonate in hard coral, packages can be built on the `calcipy` foundation.

`calcipy` has some configurability, but is still very opinionated for my particular use cases. There are a number of alternatives to consider:

- [tidypy](https://github.com/jayclassless/tidypy#features) offers similar functionality of bundling and running static checkers, but makes far fewer assumptions about the project itself (and has a really nice progress indicator!)
- [black](https://black.readthedocs.io/en/stable/) is an opinionated, but really popular formatter
- And many more such as [prospector](https://github.com/PyCQA/prospector), [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide) / [cjolowicz/cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python), etc.

## Installation

Create a new project with [kyleking/calcipy_template](https://github.com/KyleKing/calcipy_template/)

```sh
# See above link for latest documentation, but this snippet should work
pipx install copier
copier copy gh:KyleKing/calcipy_template new_project
cd new_project
# Static files can then be kept in sync with "copier update"!
```

!!! tip
    Note: If needed, the latest version of calcipy can be installed from git by modifying the `pyproject.toml`:

    ```toml
    [tool.poetry.dependencies.calcipy]
    git = "https://github.com/kyleking/calcipy.git"
    branch = "dev/development"
    rev = "56802cf"  # Always pin to a commit
    develop = true  # Optional: will reinstall each time

    [tool.poetry.dev-dependencies.calcipy]
    git = "https://github.com/kyleking/calcipy.git"
    branch = "dev/development"
    extras = [ "dev", "lint", "test",]
    ```

## Usage

1. Run `poetry install`
2. Check that `poetry run doit` works
3. Run `poetry run doit list` to see available tasks

If you have any questions, please [start a Discussion on Github](https://github.com/KyleKing/calcipy/discussions/)

For more examples, see other projects that use `calcipy`:

- [KyleKing/cz_legacy](https://github.com/KyleKing/cz_legacy) - *Published*
- [KyleKing/dash_charts](https://github.com/KyleKing/dash_charts) - *WIP*
- [KyleKing/PiAlarm](https://github.com/KyleKing/PiAlarm) - *On Hold*
- [KyleKing/Goodreads_Library_Availability](https://github.com/KyleKing/Goodreads_Library_Availability) - *On Hold*
- See other [projects tagged with the topic "calcipy"](https://github.com/topics/calcipy)
- Also see: [Scripts](https://github.com/KyleKing/calcipy/tree/main/scripts) or [Tests](https://github.com/KyleKing/calcipy/tree/main/tests)

## Upgrades

Review the [./docs/CHANGELOG.md](./docs/CHANGELOG.md) before updating. Calcipy uses semantic versioning so once `^1.0.0`, breaking changes will only occur during major releases; however, while an alpha-release (`0.#.#`), the project may have breaking changes on minor increments until stable.

```sh
# Update dependencies
poetry update

# Update files
copier update
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
