# calcipy

![./calcipy.svg](./calcipy.svg)

`calcipy` is a Python package that implements best practices such as code style (linting, auto-fixes), documentation, and logging. Like the calcium carbonate in hard coral, packages can be built on the `calcipy` foundation

## Where Used

- [KyleKing/cz_legacy](https://github.com/KyleKing/cz_legacy) - *Published*
- [KyleKing/dash_charts](https://github.com/KyleKing/dash_charts) - *WIP*
- [KyleKing/PiAlarm](https://github.com/KyleKing/PiAlarm) - *On Hold*
- [KyleKing/Goodreads_Library_Availability](https://github.com/KyleKing/Goodreads_Library_Availability) - *On Hold*

## Quick Start

<!-- TODO: Replace with Copier Instructions (#26 / #38) And when calcipy is published to PyPi... -->
Add to a poetry project in `pyproject.toml`:

```toml
[tool.poetry.dependencies.calcipy]
git = "https://github.com/kyleking/calcipy.git"
branch = "main"

[tool.poetry.dev-dependencies.calcipy]
git = "https://github.com/kyleking/calcipy.git"
branch = "main"
extras = [ "dev", "lint", "test",]
```

Then copy the [`https://github.com/KyleKing/calcipy/blob/main/dodo.py`](https://github.com/KyleKing/calcipy/blob/main/dodo.py) file into your project and call with `poetry run doit`

If you have any questions, please [open an issue on Github](https://github.com/KyleKing/calcipy/issues/new)

### Developer Information

See [./DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) and [./CONTRIBUTING.md](./CONTRIBUTING.md)
