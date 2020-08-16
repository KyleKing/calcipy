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
| `dash_dev/doit_doc.py` | 95 | 59 | 0 | 37.9% |
| `dash_dev/doit_lint.py` | 31 | 17 | 0 | 45.2% |
| `dash_dev/doit_test.py` | 20 | 9 | 0 | 55.0% |

Generated on: 2020-08-15T20:02:35.039293

<!-- /COVERAGE -->
