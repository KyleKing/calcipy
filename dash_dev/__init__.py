"""
# [Dash_Dev](https://github.com/KyleKing/dash_dev)

Python package to simplify developing Python applications. Includes functionality for task running, testing, linting, documenting, and more

Note: the package name is a misnomer and I haven't thought of a better replacement. Use [dash_charts](https://github.com/KyleKing/dash_charts) for building plotly/Dash applications

## Quick Start

Add to a poetry project in `pyproject.toml`:

```toml
[tool.poetry.dev-dependencies.dash_dev]
git = \"https://github.com/KyleKing/dash_dev.git\"
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
| `dash_dev/__init__.py` | 2 | 0 | 0 | 100.0% |
| `dash_dev/conftest.py` | 22 | 3 | 0 | 86.4% |
| `dash_dev/doit_base.py` | 105 | 26 | 0 | 75.2% |
| `dash_dev/doit_doc.py` | 101 | 64 | 0 | 36.6% |
| `dash_dev/doit_lint.py` | 68 | 20 | 0 | 70.6% |
| `dash_dev/doit_test.py` | 27 | 13 | 0 | 51.9% |

Generated on: 2020-11-05T21:51:04.872739

<!-- /COVERAGE -->
"""  # noqa

# Generated with DoIt. Do not modify

__version__ = '0.0.1'
__pkg_name__ = 'dash_dev'

from loguru import logger

logger.disable(__pkg_name__)
