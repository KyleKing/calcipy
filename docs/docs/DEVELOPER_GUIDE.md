# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/calcipy.git
cd calcipy
poetry install --sync -E ddict -E doc -E flake8 -E lint -E nox -E pylint -E stale -E tags -E test -E types

# See the available tasks
poetry run calcipy
# Or use a local 'run' file (so that 'calcipy' can be extended)
./run

# Run the default task list (lint, auto-format, test coverage, etc.)
./run main

# Make code changes and run specific tasks as needed:
./run lint.fix test
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
./run release --suffix=rc
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                                            |   Statements |   Missing |   Excluded | Coverage   |
|-----------------------------------------------------------------|--------------|-----------|------------|------------|
| `calcipy/__init__.py`                                           |            2 |         0 |          0 | 100.0%     |
| `calcipy/can_skip.py`                                           |           17 |         1 |          0 | 92.9%      |
| `calcipy/check_for_stale_packages/__init__.py`                  |            4 |         2 |          0 | 50.0%      |
| `calcipy/check_for_stale_packages/_check_for_stale_packages.py` |          112 |         8 |          3 | 90.7%      |
| `calcipy/cli.py`                                                |           93 |        22 |         13 | 70.2%      |
| `calcipy/code_tag_collector/__init__.py`                        |            4 |         2 |          0 | 50.0%      |
| `calcipy/code_tag_collector/_collector.py`                      |          146 |         2 |          0 | 96.9%      |
| `calcipy/dot_dict/__init__.py`                                  |            4 |         2 |          0 | 50.0%      |
| `calcipy/dot_dict/_dot_dict.py`                                 |            8 |         0 |          0 | 100.0%     |
| `calcipy/experiments/__init__.py`                               |            0 |         0 |          0 | 100.0%     |
| `calcipy/experiments/check_duplicate_test_names.py`             |           36 |         0 |          2 | 98.3%      |
| `calcipy/file_search.py`                                        |           38 |         0 |          2 | 100.0%     |
| `calcipy/invoke_helpers.py`                                     |           35 |         4 |          0 | 88.1%      |
| `calcipy/md_writer/__init__.py`                                 |            4 |         2 |          0 | 50.0%      |
| `calcipy/md_writer/_writer.py`                                  |           95 |         7 |          0 | 91.9%      |
| `calcipy/noxfile/__init__.py`                                   |            4 |         2 |          0 | 50.0%      |
| `calcipy/noxfile/_noxfile.py`                                   |           50 |         2 |         32 | 95.2%      |
| `calcipy/scripts.py`                                            |           12 |         0 |         27 | 100.0%     |
| `calcipy/tasks/__init__.py`                                     |            0 |         0 |          0 | 100.0%     |
| `calcipy/tasks/all_tasks.py`                                    |           47 |         2 |          0 | 96.8%      |
| `calcipy/tasks/cl.py`                                           |           27 |         6 |          0 | 77.1%      |
| `calcipy/tasks/defaults.py`                                     |           20 |         0 |          0 | 92.9%      |
| `calcipy/tasks/doc.py`                                          |           45 |         0 |          8 | 100.0%     |
| `calcipy/tasks/executable_utils.py`                             |           20 |         1 |          0 | 97.5%      |
| `calcipy/tasks/lint.py`                                         |           56 |         1 |          0 | 93.0%      |
| `calcipy/tasks/nox.py`                                          |            8 |         0 |          0 | 100.0%     |
| `calcipy/tasks/pack.py`                                         |           32 |         4 |          0 | 85.4%      |
| `calcipy/tasks/stale.py`                                        |            9 |         2 |          0 | 81.8%      |
| `calcipy/tasks/tags.py`                                         |           15 |         0 |          0 | 100.0%     |
| `calcipy/tasks/test.py`                                         |           45 |         1 |          2 | 95.4%      |
| `calcipy/tasks/types.py`                                        |           20 |         2 |          0 | 92.3%      |
| **Totals**                                                      |         1008 |        75 |         89 | 91.3%      |

Generated on: 2023-06-25
<!-- {cte} -->
