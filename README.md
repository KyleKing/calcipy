# Dash_Dev

Development package to define common package requirements, linting, doit tasks, and other development activities

Add to a poetry project with:

```toml
[tool.poetry.dev-dependencies]
dash = {extras = ["testing"], version = "*, ^1.11"}
dash_dev = {git = "https://github.com/KyleKing/dash_dev.git"}
```

Then copy the [`dodo.py`](./dodo.py) file into your project and call with `poetry run doit`

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
| `dash_dev/__init__.py` | 1 | 0 | 0 | 100.0% |
| `dash_dev/conftest.py` | 4 | 0 | 0 | 100.0% |
| `dash_dev/doit_base.py` | 47 | 2 | 0 | 95.7% |
| `dash_dev/doit_doc.py` | 98 | 59 | 0 | 39.8% |
| `dash_dev/doit_lint.py` | 46 | 12 | 0 | 73.9% |
| `dash_dev/doit_test.py` | 22 | 10 | 0 | 54.5% |

Generated on: 2020-08-17T07:09:09.170896

<!-- /COVERAGE -->
