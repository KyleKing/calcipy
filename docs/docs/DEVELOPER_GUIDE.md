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
| `calcipy/can_skip.py`                                           |           18 |         1 |          0 | 93.3%      |
| `calcipy/check_for_stale_packages/__init__.py`                  |            4 |         2 |          0 | 50.0%      |
| `calcipy/check_for_stale_packages/_check_for_stale_packages.py` |          109 |         9 |          3 | 90.9%      |
| `calcipy/cli.py`                                                |           90 |        21 |         13 | 70.3%      |
| `calcipy/code_tag_collector/__init__.py`                        |            4 |         2 |          0 | 50.0%      |
| `calcipy/code_tag_collector/_collector.py`                      |          127 |         2 |          0 | 96.9%      |
| `calcipy/dot_dict/__init__.py`                                  |            4 |         2 |          0 | 50.0%      |
| `calcipy/dot_dict/_dot_dict.py`                                 |            8 |         0 |          0 | 100.0%     |
| `calcipy/experiments/__init__.py`                               |            0 |         0 |          0 | 100.0%     |
| `calcipy/experiments/check_duplicate_test_names.py`             |           36 |         0 |          2 | 98.3%      |
| `calcipy/file_search.py`                                        |           38 |         0 |          2 | 100.0%     |
| `calcipy/invoke_helpers.py`                                     |           31 |         3 |          0 | 90.6%      |
| `calcipy/md_writer/__init__.py`                                 |            4 |         2 |          0 | 50.0%      |
| `calcipy/md_writer/_writer.py`                                  |           95 |         7 |          0 | 91.9%      |
| `calcipy/noxfile/__init__.py`                                   |            4 |         2 |          0 | 50.0%      |
| `calcipy/noxfile/_noxfile.py`                                   |           52 |         2 |         32 | 95.3%      |
| `calcipy/scripts.py`                                            |           10 |         0 |         23 | 100.0%     |
| `calcipy/tasks/__init__.py`                                     |            0 |         0 |          0 | 100.0%     |
| `calcipy/tasks/all_tasks.py`                                    |           43 |         2 |          0 | 96.6%      |
| `calcipy/tasks/cl.py`                                           |           26 |         6 |          0 | 76.5%      |
| `calcipy/tasks/defaults.py`                                     |           19 |         0 |          0 | 92.6%      |
| `calcipy/tasks/doc.py`                                          |           44 |         0 |          8 | 100.0%     |
| `calcipy/tasks/lint.py`                                         |           54 |         1 |          0 | 92.9%      |
| `calcipy/tasks/nox.py`                                          |            8 |         0 |          0 | 100.0%     |
| `calcipy/tasks/pack.py`                                         |           26 |         4 |          0 | 81.6%      |
| `calcipy/tasks/stale.py`                                        |            8 |         2 |          0 | 80.0%      |
| `calcipy/tasks/tags.py`                                         |           15 |         0 |          0 | 100.0%     |
| `calcipy/tasks/test.py`                                         |           44 |         1 |          2 | 95.3%      |
| `calcipy/tasks/types.py`                                        |           15 |         0 |          0 | 100.0%     |
| **Totals**                                                      |          938 |        71 |         85 | 91.1%      |

Generated on: 2023-04-22
<!-- {cte} -->
