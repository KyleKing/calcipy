<!-- TODO: Add a banner image -->

`calcipy` is named after the calcium carbonate in hard coral. As a package, `calcipy` implements the best practices for code style (linting, auto-fixes, and more), generating documentation, configuring logging, and many more common tasks and features.

## Quick Start

<!-- TODO: Replace with ~CookieCutter~ (Copier) Instructions -->

Add to a poetry project in `pyproject.toml`:

```toml
[tool.poetry.dev-dependencies.calcipy]
git = "https://github.com/KyleKing/calcipy.git"
branch = "main"
```

Then copy the [`https://github.com/KyleKing/calcipy/blob/main/dodo.py`](https://github.com/KyleKing/calcipy/blob/main/dodo.py) file into your project and call with `poetry run doit`

If you have any questions, please [open an issue on Github](https://github.com/KyleKing/calcipy/issues/new)

## Where Used

- [KyleKing/dash_charts](https://github.com/KyleKing/dash_charts)
- [KyleKing/PiAlarm](https://github.com/KyleKing/PiAlarm)
- [KyleKing/Kitsu_Library_Availability](https://github.com/KyleKing/Kitsu_Library_Availability)
- [KyleKing/Goodreads_Library_Availability](https://github.com/KyleKing/Goodreads_Library_Availability) - *Planned*

## Test Coverage

<!-- COVERAGE -->

| File | Statements | Missing | Excluded | Coverage |
| --: | --: | --: | --: | --: |
| `calcipy/__init__.py` | 10 | 0 | 0 | 100.0% |
| `calcipy/conftest.py` | 29 | 11 | 0 | 62.1% |
| `calcipy/doit_helpers/__init__.py` | 0 | 0 | 0 | 100.0% |
| `calcipy/doit_helpers/base.py` | 51 | 14 | 0 | 72.5% |
| `calcipy/doit_helpers/doc.py` | 141 | 82 | 0 | 41.8% |
| `calcipy/doit_helpers/doit_globals.py` | 54 | 2 | 0 | 96.3% |
| `calcipy/doit_helpers/lint.py` | 81 | 19 | 0 | 76.5% |
| `calcipy/doit_helpers/test.py` | 42 | 16 | 0 | 61.9% |
| `calcipy/log_helpers.py` | 24 | 5 | 0 | 79.2% |
| `calcipy/registered_tasks.py` | 5 | 5 | 0 | 0.0% |
| `calcipy/tag_collector.py` | 91 | 29 | 0 | 68.1% |

Generated on: 2020-12-10T20:43:26.996114

<!-- /COVERAGE -->
