# calcipy

![./calcipy.svg](./calcipy.svg)

`calcipy` is a Python package that implements best practices such as code style (linting, auto-fixes), documentation, and logging. Like the calcium carbonate in hard coral, packages can be built on the `calcipy` foundation

## Installation

Create a new project with [kyleking/calcipy_template](https://github.com/KyleKing/calcipy_template/)

```sh
# See above link for latest documentation, but this snippet should work
pipx install copier
copier copy gh:KyleKing/calcipy_template new_project
cd new_project
```

!!! tip
    Note: If needed, the latest version of calcipy can be installed from git by modifying the `pyproject.toml`:

    ```toml
    [tool.poetry.dependencies.calcipy]
    git = "https://github.com/kyleking/calcipy.git"
    branch = "main"

    [tool.poetry.dev-dependencies.calcipy]
    git = "https://github.com/kyleking/calcipy.git"
    branch = "main"
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
- Also see: [Scripts](https://github.com/kyleking/calcipy/scripts) or [Tests](https://github.com/kyleking/calcipy/tests)

## Upgrades

Review the [./CHANGELOG.md](./CHANGELOG.md) before updating. Calcipy uses semantic versioning so once `^1.0.0`, breaking changes will only occur during major releases; however, while an alpha-release (`0.#.#`), the project may have breaking changes on minor increments until stable.

```sh
# Update dependencies
poetry update

# Update files
copier update
```

## Roadmap

See the `Open Issues` and `Milestones` for current status and [./CODE_TAG_SUMMARY.md](./CODE_TAG_SUMMARY.md) for annotations in the source code.

For release history, see the [./CHANGELOG.md](./CHANGELOG.md)

## Contributing

See the Developer Guide, Contribution Guidelines, etc

- [./DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
- [./STYLE_GUIDE.md](./STYLE_GUIDE.md)
- [./CONTRIBUTING.md](./CONTRIBUTING.md)
- [./CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- [./SECURITY.md](./SECURITY.md)

## License

[LICENSE](https://github.com/kyleking/calcipy/LICENSE)
