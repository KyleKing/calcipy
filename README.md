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
| dash_dev/0EX/__init__.py | 0 | 0 | 0 | 100.0 |
| dash_dev/__init__.py | 1 | 0 | 0 | 100.0 |
| dash_dev/conftest.py | 2 | 0 | 0 | 100.0 |
| dash_dev/doit_base.py | 48 | 24 | 0 | 50.0 |
| dash_dev/doit_doc.py | 96 | 96 | 0 | 0.0 |
| dash_dev/doit_lint.py | 14 | 14 | 0 | 0.0 |
| dash_dev/doit_test.py | 13 | 7 | 0 | 46.2 |

Generated on: 2020-03-21T15:11:02.296762

<!-- /COVERAGE -->

## TODO List

- Make sure gitchangelog.rc and other relevant files are populated to working directory if needed
- Add tests
- Add documentation and gh_pages
- Better generalize. Specific snippets for `commit_docs` / handling the examples directory were very specific to `dash_charts` and could be generalized
