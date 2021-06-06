# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/calcipy.git
cd calcipy
poetry install -E dev -E lint -E test -E commitizen_legacy

# See the available tasks
poetry run doit list

# Run the default task list (lint, auto-format, test coverage, etc.)
poetry run doit --continue

# Make code changes and run specific tasks as needed:
poetry run doit run test
```

## Publishing

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/). Replace `...` with the API token generated on TestPyPi|PyPi respectively

```sh
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi ...

poetry run doit run publish_test_pypi
# If you didn't configure a token, you will need to provide your username and password to publish
```

To publish to the real PyPi

```sh
poetry config pypi-token.pypi ...
poetry run doit run publish

# For a full release, increment the version, the documentation, and publish
poetry run doit run --continue
poetry run doit run cl_bump document deploy_docs publish
# Note: cl_bump_pre is helpful for pre-releases rather than full increments
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                       |   Statements |   Missing |   Excluded | Coverage   |
|:-------------------------------------------|-------------:|----------:|-----------:|:-----------|
| `calcipy/__init__.py`                      |            7 |         0 |          0 | 100.0%     |
| `calcipy/dev/__init__.py`                  |            0 |         0 |          0 | 100.0%     |
| `calcipy/dev/conftest.py`                  |           15 |         0 |         22 | 100.0%     |
| `calcipy/dev/noxfile.py`                   |           16 |         0 |         62 | 100.0%     |
| `calcipy/doit_tasks/__init__.py`           |           13 |         0 |          0 | 100.0%     |
| `calcipy/doit_tasks/base.py`               |           39 |         7 |          3 | 82.1%      |
| `calcipy/doit_tasks/code_tag_collector.py` |           75 |         6 |          0 | 92.0%      |
| `calcipy/doit_tasks/doc.py`                |          123 |         5 |          5 | 95.9%      |
| `calcipy/doit_tasks/doit_globals.py`       |          154 |         3 |         10 | 98.1%      |
| `calcipy/doit_tasks/file_search.py`        |           34 |         0 |          2 | 100.0%     |
| `calcipy/doit_tasks/lint.py`               |           77 |         1 |          0 | 98.7%      |
| `calcipy/doit_tasks/packaging.py`          |          128 |        12 |          3 | 90.6%      |
| `calcipy/doit_tasks/summary_reporter.py`   |           22 |         0 |         36 | 100.0%     |
| `calcipy/doit_tasks/test.py`               |           60 |        11 |          0 | 81.7%      |
| `calcipy/file_helpers.py`                  |           67 |         3 |          3 | 95.5%      |
| `calcipy/log_helpers.py`                   |           60 |         6 |          2 | 90.0%      |
| `calcipy/wrappers.py`                      |            6 |         0 |          0 | 100.0%     |
| **Totals**                                 |          896 |        54 |        148 | 94.0%      |

Generated on: 2021-06-06T09:02:09.249889
<!-- {cte} -->
