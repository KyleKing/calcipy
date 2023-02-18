# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/calcipy.git
cd calcipy
poetry install --sync -E ddict -E doc -E flake8 -E lint -E nox -E pylint -E stale -E tags -E test -E types

# See the available tasks
./run

# Run the default task list (lint, auto-format, test coverage, etc.)
./run main

# Make code changes and run specific tasks as needed:
./run lint test
```

## Publishing

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/). Replace `...` with the API token generated on TestPyPi or PyPi respectively

```sh
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi ...

./run main pack.publish --to-test-pypi
# If you didn't configure a token, you will need to provide your username and password to publish
```

To publish to the real PyPi

```sh
poetry config pypi-token.pypi ...
./run release

# Or for a pre-release
./run cl_bump --suffix=rc doc.build doc.deploy pack.publish
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                                            |   Statements |   Missing |   Excluded | Coverage   |
|-----------------------------------------------------------------|--------------|-----------|------------|------------|
| `calcipy/__init__.py`                                           |            2 |         0 |          0 | 100.0%     |
| `calcipy/check_for_stale_packages/__init__.py`                  |            1 |         1 |          0 | 0.0%       |
| `calcipy/check_for_stale_packages/_check_for_stale_packages.py` |          108 |       108 |          0 | 0.0%       |
| `calcipy/code_tag_collector/__init__.py`                        |            1 |         1 |          0 | 0.0%       |
| `calcipy/code_tag_collector/_collector.py`                      |          126 |       126 |          0 | 0.0%       |
| `calcipy/dot_dict/__init__.py`                                  |            4 |         4 |          0 | 0.0%       |
| `calcipy/dot_dict/_dot_dict.py`                                 |            8 |         8 |          0 | 0.0%       |
| `calcipy/file_helpers.py`                                       |           89 |        47 |          6 | 47.2%      |
| `calcipy/file_search.py`                                        |           35 |        35 |          2 | 0.0%       |
| `calcipy/main.py`                                               |            7 |         7 |          0 | 0.0%       |
| `calcipy/noxfile/__init__.py`                                   |            4 |         4 |          0 | 0.0%       |
| `calcipy/noxfile/_noxfile.py`                                   |           30 |        30 |          1 | 0.0%       |
| `calcipy/tasks/__init__.py`                                     |            0 |         0 |          0 | 100.0%     |
| `calcipy/tasks/all_tasks.py`                                    |           11 |        11 |          0 | 0.0%       |
| `calcipy/tasks/cached_utilities.py`                             |           23 |         5 |          0 | 78.3%      |
| `calcipy/tasks/defaults.py`                                     |            9 |         0 |          0 | 100.0%     |
| `calcipy/tasks/lint.py`                                         |           27 |        27 |          0 | 0.0%       |
| `calcipy/tasks/nox.py`                                          |           30 |        30 |          0 | 0.0%       |
| `calcipy/tasks/stale.py`                                        |           16 |        16 |          0 | 0.0%       |
| `calcipy/tasks/tags.py`                                         |           26 |        26 |          0 | 0.0%       |
| `calcipy/tasks/test.py`                                         |           44 |         0 |          2 | 100.0%     |
| `calcipy/tasks/types.py`                                        |           30 |         1 |          0 | 96.7%      |
| **Totals**                                                      |          631 |       487 |         11 | 22.8%      |

Generated on: 2023-02-17
<!-- {cte} -->
