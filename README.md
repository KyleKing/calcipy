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
| `dash_dev/conftest.py` | 19 | 3 | 0 | 84.2% |
| `dash_dev/doit_base.py` | 70 | 8 | 0 | 88.6% |
| `dash_dev/doit_doc.py` | 99 | 60 | 0 | 39.4% |
| `dash_dev/doit_lint.py` | 65 | 17 | 0 | 73.8% |
| `dash_dev/doit_test.py` | 27 | 13 | 0 | 51.9% |

Generated on: 2020-10-14T06:57:48.654525

<!-- /COVERAGE -->
