# calcipy

![./calcipy.svg](https://raw.githubusercontent.com/KyleKing/calcipy/main/docs/calcipy.svg)

`calcipy` is a Python package that implements best practices such as code style (linting, auto-fixes), documentation, CI/CD, and logging. Like the calcium carbonate in hard coral, packages can be built on the `calcipy` foundation.

`calcipy` has some configurability, but is tailored for my particular use cases. If you want the same sort of functionality, there are a number of alternatives to consider:

- [tidypy](https://github.com/jayclassless/tidypy#features) offers similar functionality of bundling and running static checkers, but makes far fewer assumptions about the project itself (and has a really nice progress indicator!)
- And many more such as [prospector](https://github.com/PyCQA/prospector), [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide) / [cjolowicz/cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python), etc.

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
2. Run `poetry run doit list` to see available tasks
3. And try `poetry run doit --continue` to see if the default tasks work

If you have any questions, please [start a Discussion on Github](https://github.com/KyleKing/calcipy/discussions/) or [open an issue for feature requests or bug reports](https://github.com/KyleKing/calcipy/issues/)

For more examples, see other projects that use `calcipy`:

- [KyleKing/dash_charts](https://github.com/KyleKing/dash_charts) - *WIP*
- [KyleKing/recipes](https://github.com/KyleKing/recipes) - *Actively Developer*
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
