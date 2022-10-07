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

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/). Replace `...` with the API token generated on TestPyPi or PyPi respectively

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

# For a full release, triple check the default tasks, increment the version, rebuild documentation (twice), and publish!
poetry run doit run --continue
poetry run doit run cl_bump lock document deploy_docs publish

# For pre-releases use cl_bump_pre
poetry run doit run cl_bump_pre -p rc
poetry run doit run lock document deploy_docs publish
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                                       |   Statements |   Missing |   Excluded | Coverage   |
|------------------------------------------------------------|--------------|-----------|------------|------------|
| `calcipy/__init__.py`                                      |            6 |         0 |          0 | 100.0%     |
| `calcipy/bump_dependencies.py`                             |           44 |        44 |          0 | 0.0%       |
| `calcipy/cli/__init__.py`                                  |            0 |         0 |          0 | 100.0%     |
| `calcipy/cli/controllers/__init__.py`                      |            0 |         0 |          0 | 100.0%     |
| `calcipy/cli/controllers/code_tag_collector_controller.py` |           27 |        12 |          0 | 55.6%      |
| `calcipy/cli/core/__init__.py`                             |            0 |         0 |          0 | 100.0%     |
| `calcipy/cli/core/exceptions.py`                           |            2 |         0 |          0 | 100.0%     |
| `calcipy/cli/core/version.py`                              |            8 |         8 |          0 | 0.0%       |
| `calcipy/cli/main.py`                                      |           38 |        19 |          0 | 50.0%      |
| `calcipy/code_tag_collector.py`                            |          116 |        23 |          0 | 80.2%      |
| `calcipy/dev/__init__.py`                                  |            0 |         0 |          0 | 100.0%     |
| `calcipy/dev/conftest.py`                                  |           16 |         0 |         23 | 100.0%     |
| `calcipy/dev/noxfile.py`                                   |           23 |         1 |         75 | 95.7%      |
| `calcipy/doit_tasks/__init__.py`                           |           11 |         0 |          0 | 100.0%     |
| `calcipy/doit_tasks/base.py`                               |           50 |        10 |          3 | 80.0%      |
| `calcipy/doit_tasks/code_tags.py`                          |           11 |         0 |          0 | 100.0%     |
| `calcipy/doit_tasks/doc.py`                                |          146 |        10 |          5 | 93.2%      |
| `calcipy/doit_tasks/doit_globals.py`                       |          186 |         5 |          4 | 97.3%      |
| `calcipy/doit_tasks/lint.py`                               |          103 |         9 |          0 | 91.3%      |
| `calcipy/doit_tasks/packaging.py`                          |          132 |        12 |          0 | 90.9%      |
| `calcipy/doit_tasks/summary_reporter.py`                   |           21 |         0 |         40 | 100.0%     |
| `calcipy/doit_tasks/test.py`                               |           67 |         4 |          0 | 94.0%      |
| `calcipy/dot_dict.py`                                      |            7 |         0 |          0 | 100.0%     |
| `calcipy/file_helpers.py`                                  |           76 |         6 |          3 | 92.1%      |
| `calcipy/file_search.py`                                   |           34 |         0 |          2 | 100.0%     |
| `calcipy/log_helpers.py`                                   |           81 |        13 |          0 | 84.0%      |
| `calcipy/proc_helpers.py`                                  |           20 |         1 |          0 | 95.0%      |
| **Totals**                                                 |         1225 |       177 |        155 | 85.6%      |

Generated on: 2022-10-05
<!-- {cte} -->
