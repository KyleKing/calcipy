# Dash_Dev ([Github](https://github.com/KyleKing/dash_dev))

Python package to simplify development. Includes functionality for task running, testing, linting, documenting, and more

Note: the package name is a misnomer and is not specific to Plotly/Dash projects (and I haven't thought of a better replacement yet). If you want to build Plotly/Dash applications, see [dash_charts](https://github.com/KyleKing/dash_charts)

## Quick Start

<!-- TODO: Replace with CookieCutter Instructions -->

Add to a poetry project in `pyproject.toml`:

```toml
[tool.poetry.dev-dependencies.dash_dev]
git = "https://github.com/KyleKing/dash_dev.git"
branch = "main"
```

Then copy the [`https://github.com/KyleKing/dash_dev/blob/master/dodo.py`](https://github.com/KyleKing/dash_dev/blob/master/dodo.py) file into your project and call with `poetry run doit`

If you have any questions, please [open an issue on Github](https://github.com/KyleKing/dash_dev/issues/new)

## Where Used

- [KyleKing/dash_charts](https://github.com/KyleKing/dash_charts)
- [KyleKing/PiAlarm](https://github.com/KyleKing/PiAlarm)
- [KyleKing/Kitsu_Library_Availability](https://github.com/KyleKing/Kitsu_Library_Availability)
- [KyleKing/Goodreads_Library_Availability](https://github.com/KyleKing/Goodreads_Library_Availability) - *Planned*

## Test Coverage

<!-- COVERAGE -->

| File | Statements | Missing | Excluded | Coverage |
| --: | --: | --: | --: | --: |
| `dash_dev/__init__.py` | 11 | 0 | 0 | 100.0% |
| `dash_dev/conftest.py` | 22 | 3 | 0 | 86.4% |
| `dash_dev/doit_base.py` | 82 | 11 | 0 | 86.6% |
| `dash_dev/doit_dev.py` | 36 | 36 | 0 | 0.0% |
| `dash_dev/doit_doc.py` | 110 | 70 | 0 | 36.4% |
| `dash_dev/doit_lint.py` | 66 | 18 | 0 | 72.7% |
| `dash_dev/doit_test.py` | 27 | 13 | 0 | 51.9% |
| `dash_dev/log_helpers.py` | 18 | 5 | 0 | 72.2% |
| `dash_dev/tag_collector.py` | 64 | 16 | 0 | 75.0% |

Generated on: 2020-11-12T23:58:38.946472

<!-- /COVERAGE -->
