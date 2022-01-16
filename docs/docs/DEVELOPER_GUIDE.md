# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/calcipy.git
cd calcipy
poetry install -E dev -E lint -E test -E commitizen_legacy
# Note that the new "poetry --sync" will remove optional groups

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
| File                                                       |   Statements |   Missing |   Excluded | Coverage   |
|:-----------------------------------------------------------|-------------:|----------:|-----------:|:-----------|
| `calcipy/__init__.py`                                      |            9 |         0 |          0 | 100.0%     |
| `calcipy/cli/__init__.py`                                  |            0 |         0 |          0 | 100.0%     |
| `calcipy/cli/controllers/__init__.py`                      |            0 |         0 |          0 | 100.0%     |
| `calcipy/cli/controllers/base_controller.py`               |           19 |         2 |          0 | 89.5%      |
| `calcipy/cli/controllers/code_tag_collector_controller.py` |           26 |        12 |          0 | 53.8%      |
| `calcipy/cli/core/__init__.py`                             |            0 |         0 |          0 | 100.0%     |
| `calcipy/cli/core/exceptions.py`                           |            2 |         0 |          0 | 100.0%     |
| `calcipy/cli/core/version.py`                              |            8 |         0 |          0 | 100.0%     |
| `calcipy/cli/main.py`                                      |           39 |        19 |          0 | 51.3%      |
| `calcipy/code_tag_collector.py`                            |           74 |         5 |          0 | 93.2%      |
| `calcipy/dev/__init__.py`                                  |            0 |         0 |          0 | 100.0%     |
| `calcipy/dev/conftest.py`                                  |           16 |         0 |         23 | 100.0%     |
| `calcipy/dev/noxfile.py`                                   |           23 |         1 |         90 | 95.7%      |
| `calcipy/doit_tasks/__init__.py`                           |           13 |         0 |          0 | 100.0%     |
| `calcipy/doit_tasks/base.py`                               |           50 |        10 |          3 | 80.0%      |
| `calcipy/doit_tasks/code_tags.py`                          |           10 |         0 |          0 | 100.0%     |
| `calcipy/doit_tasks/doc.py`                                |          136 |         7 |          5 | 94.9%      |
| `calcipy/doit_tasks/doit_globals.py`                       |          168 |         5 |          8 | 97.0%      |
| `calcipy/doit_tasks/lint.py`                               |           89 |         5 |          0 | 94.4%      |
| `calcipy/doit_tasks/packaging.py`                          |          131 |        12 |          3 | 90.8%      |
| `calcipy/doit_tasks/summary_reporter.py`                   |           23 |         0 |         40 | 100.0%     |
| `calcipy/doit_tasks/test.py`                               |           58 |         9 |          0 | 84.5%      |
| `calcipy/dot_dict.py`                                      |            7 |         0 |          0 | 100.0%     |
| `calcipy/file_helpers.py`                                  |           78 |         6 |          3 | 92.3%      |
| `calcipy/file_search.py`                                   |           34 |         0 |          2 | 100.0%     |
| `calcipy/log_helpers.py`                                   |           61 |         6 |          0 | 90.2%      |
| **Totals**                                                 |         1074 |        99 |        177 | 90.8%      |

Generated on: 2022-01-16T16:30:32.741036
<!-- {cte} -->
