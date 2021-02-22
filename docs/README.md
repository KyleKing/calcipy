# calcipy

<!-- TODO: Add a banner image (#27) -->

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

## Test Coverage

<!-- COVERAGE -->

| File | Statements | Missing | Excluded | Coverage |
| --: | --: | --: | --: | --: |
| `calcipy/__init__.py` | 4 | 0 | 0 | 100.0% |
| `calcipy/conftest.py` | 29 | 11 | 0 | 62.1% |
| `calcipy/doit_tasks/__init__.py` | 7 | 0 | 0 | 100.0% |
| `calcipy/doit_tasks/base.py` | 35 | 11 | 0 | 68.6% |
| `calcipy/doit_tasks/doc.py` | 98 | 63 | 0 | 35.7% |
| `calcipy/doit_tasks/doit_globals.py` | 102 | 9 | 0 | 91.2% |
| `calcipy/doit_tasks/lint.py` | 69 | 17 | 0 | 75.4% |
| `calcipy/doit_tasks/tag_collector.py` | 87 | 36 | 0 | 58.6% |
| `calcipy/doit_tasks/test.py` | 30 | 13 | 0 | 56.7% |
| `calcipy/log_helpers.py` | 43 | 16 | 0 | 62.8% |

Generated on: 2021-02-21T15:51:52.684476

<!-- /COVERAGE -->
