# Dash_Dev

Development package to define common package requirements, linting, doit tasks, and other development activities

Add to a poetry project with:

```toml
[tool.poetry.dev-dependencies]
dash = {extras = ["testing"], version = "*, ^1.9"}
dash_dev = {git = "https://github.com/KyleKing/dash_dev.git"}
```

Where used:

- [KyleKing/dash_charts](https://github.com/KyleKing/dash_charts)
- [KyleKing/PiAlarm](https://github.com/KyleKing/PiAlarm)

## Coverage

Latest coverage table

<!-- COVERAGE -->

| File | Statements | Missing | Excluded | Coverage |
| --: | --: | --: | --: | --: |
| `dash_dev/__init__.py` | 1 | 0 | 0 | 100.0 |
| `dash_dev/conftest.py` | 2 | 0 | 0 | 100.0 |
| `dash_dev/doit_base.py` | 48 | 24 | 0 | 50.0 |
| `dash_dev/doit_doc.py` | 98 | 98 | 0 | 0.0 |
| `dash_dev/doit_lint.py` | 14 | 14 | 0 | 0.0 |
| `dash_dev/doit_test.py` | 13 | 7 | 0 | 46.2 |

Generated on: 2020-03-25T22:46:28.137749

<!-- /COVERAGE -->

## TODO List

- Make sure gitchangelog.rc and other relevant files are populated to working directory if needed
- Add tests
- Refactor and general cleanup. Is there a better way to handle `stage_examples` when no example files are needed?
