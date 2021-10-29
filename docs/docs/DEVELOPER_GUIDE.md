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

# For a full release, triple check the default tasks, increment the version, rebuild documentation, and publish!
poetry run doit run --continue
poetry run doit run cl_bump lock document deploy_docs publish

# For pre-releases use cl_bump_pre
poetry run doit run cl_bump_pre -p rc
poetry run doit run lock document deploy_docs publish
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                       |   Statements |   Missing |   Excluded | Coverage   |
|:-------------------------------------------|-------------:|----------:|-----------:|:-----------|
| `calcipy/__init__.py`                      |            7 |         0 |          0 | 100.0%     |
| `calcipy/dev/__init__.py`                  |            0 |         0 |          0 | 100.0%     |
| `calcipy/dev/conftest.py`                  |           16 |         0 |         23 | 100.0%     |
| `calcipy/dev/noxfile.py`                   |           16 |         0 |         74 | 100.0%     |
| `calcipy/doit_tasks/__init__.py`           |           13 |         0 |          0 | 100.0%     |
| `calcipy/doit_tasks/base.py`               |           49 |         9 |          3 | 81.6%      |
| `calcipy/doit_tasks/code_tag_collector.py` |           75 |         6 |          0 | 92.0%      |
| `calcipy/doit_tasks/doc.py`                |          132 |         5 |          5 | 96.2%      |
| `calcipy/doit_tasks/doit_globals.py`       |          163 |         4 |         10 | 97.5%      |
| `calcipy/doit_tasks/file_search.py`        |           34 |         0 |          2 | 100.0%     |
| `calcipy/doit_tasks/lint.py`               |           81 |         3 |          0 | 96.3%      |
| `calcipy/doit_tasks/packaging.py`          |          132 |        12 |          3 | 90.9%      |
| `calcipy/doit_tasks/summary_reporter.py`   |           22 |         0 |         40 | 100.0%     |
| `calcipy/doit_tasks/test.py`               |           58 |         9 |          0 | 84.5%      |
| `calcipy/dot_dict.py`                      |            7 |         0 |          0 | 100.0%     |
| `calcipy/file_helpers.py`                  |           67 |         4 |          3 | 94.0%      |
| `calcipy/log_helpers.py`                   |           62 |         6 |          2 | 90.3%      |
| **Totals**                                 |          934 |        58 |        165 | 93.8%      |

Generated on: 2021-10-29T06:54:05.391636
<!-- {cte} -->
