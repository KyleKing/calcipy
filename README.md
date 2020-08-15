# Dash_Dev

Development package to define common package requirements, linting, doit tasks, and other development activities

Add to a poetry project with:

```toml
[tool.poetry.dev-dependencies]
dash = {extras = ["testing"], version = "*, ^1.11"}
dash_dev = {git = "https://github.com/KyleKing/dash_dev.git"}
```

Where used:

- [KyleKing/dash_charts](https://github.com/KyleKing/dash_charts)
- [KyleKing/PiAlarm](https://github.com/KyleKing/PiAlarm)
- [KyleKing/Kitsu_Library_Availability](https://github.com/KyleKing/Kitsu_Library_Availability)
- [KyleKing/Goodreads_Library_Availability](https://github.com/KyleKing/Goodreads_Library_Availability) - *Planned*

## Coverage

Latest coverage table

<!-- COVERAGE -->

| File | Statements | Missing | Excluded | Coverage |
| --: | --: | --: | --: | --: |
| `dash_dev/__init__.py` | 1 | 0 | 0 | 100.0 |
| `dash_dev/conftest.py` | 2 | 0 | 0 | 100.0 |
| `dash_dev/doit_base.py` | 49 | 24 | 0 | 51.0 |
| `dash_dev/doit_doc.py` | 106 | 106 | 0 | 0.0 |
| `dash_dev/doit_lint.py` | 31 | 31 | 0 | 0.0 |
| `dash_dev/doit_test.py` | 13 | 7 | 0 | 46.2 |

Generated on: 2020-08-15T16:23:57.361034

<!-- /COVERAGE -->

## TODO List

- Queue
  - Make sure gitchangelog.rc (and other relevant files) are pushed to directory - add note that they are automatically overwritten
  - Allow for building of docs within master branch (see issue on pdoc for best practices with index.html redirect)

- Planned
  - Add tests!
  - Refactor and general cleanup. Is there a better way to handle `stage_examples` when no example files are needed?
