<!-- TODO: Add a banner image -->

`calcipy` is named after the calcium carbonate in hard coral. As a package, `calcipy` implements the best practices for code style (linting, auto-fixes, and more), generating documentation, configuring logging, and many more common tasks and features.

## Quick Start

<!-- TODO: Replace with ~CookieCutter~ (Copier) Instructions -->

Add to a poetry project in `pyproject.toml`:

```toml
[tool.poetry.dependencies.calcipy]
git = "https://github.com/kyleking/calcipy.git"
branch = "main"

[tool.poetry.dev-dependencies.calcipy]
git = "https://github.com/kyleking/calcipy.git"
branch = "main"
extras = [ "development", "serializers",]
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
| `calcipy/__init__.py` | 4 | 0 | 0 | 100.0% |
| `calcipy/conftest.py` | 29 | 11 | 0 | 62.1% |
| `calcipy/doit_tasks/__init__.py` | 8 | 0 | 0 | 100.0% |
| `calcipy/doit_tasks/base.py` | 42 | 14 | 0 | 66.7% |
| `calcipy/doit_tasks/doc.py` | 96 | 62 | 0 | 35.4% |
| `calcipy/doit_tasks/doit_globals.py` | 97 | 6 | 0 | 93.8% |
| `calcipy/doit_tasks/lint.py` | 76 | 20 | 0 | 73.7% |
| `calcipy/doit_tasks/tag_collector.py` | 87 | 36 | 0 | 58.6% |
| `calcipy/doit_tasks/test.py` | 30 | 16 | 0 | 46.7% |
| `calcipy/log_helpers.py` | 43 | 16 | 0 | 62.8% |

Generated on: 2020-12-21T21:53:07.298420

<!-- /COVERAGE -->
