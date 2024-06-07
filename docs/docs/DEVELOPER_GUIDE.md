# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/calcipy.git
cd calcipy
poetry install --sync
poetry run calcipy-pack pack.install-extras

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
| `calcipy/__init__.py`                                           |           16 |         0 |         24 | 100.0%     |
| `calcipy/can_skip.py`                                           |           17 |         1 |          0 | 89.3%      |
| `calcipy/check_for_stale_packages/__init__.py`                  |            5 |         2 |          0 | 60.0%      |
| `calcipy/check_for_stale_packages/_check_for_stale_packages.py` |          118 |         8 |          3 | 87.2%      |
| `calcipy/cli.py`                                                |           35 |         1 |         78 | 93.0%      |
| `calcipy/code_tag_collector/__init__.py`                        |            5 |         2 |          0 | 60.0%      |
| `calcipy/code_tag_collector/_collector.py`                      |          143 |         2 |          0 | 94.0%      |
| `calcipy/dot_dict/__init__.py`                                  |            4 |         2 |          0 | 50.0%      |
| `calcipy/dot_dict/_dot_dict.py`                                 |            8 |         0 |          0 | 100.0%     |
| `calcipy/experiments/__init__.py`                               |            0 |         0 |          0 | 100.0%     |
| `calcipy/experiments/bump_programmatically.py`                  |           24 |        24 |          0 | 0.0%       |
| `calcipy/experiments/check_duplicate_test_names.py`             |           36 |         0 |          2 | 95.0%      |
| `calcipy/file_search.py`                                        |           38 |         0 |          2 | 91.8%      |
| `calcipy/invoke_helpers.py`                                     |           30 |         2 |          0 | 81.8%      |
| `calcipy/md_writer/__init__.py`                                 |            5 |         2 |          0 | 60.0%      |
| `calcipy/md_writer/_writer.py`                                  |           95 |         6 |          0 | 88.9%      |
| `calcipy/noxfile/__init__.py`                                   |            4 |         2 |          0 | 50.0%      |
| `calcipy/noxfile/_noxfile.py`                                   |           44 |         2 |         51 | 83.8%      |
| `calcipy/scripts.py`                                            |            5 |         0 |         37 | 100.0%     |
| `calcipy/tasks/__init__.py`                                     |            0 |         0 |          0 | 100.0%     |
| `calcipy/tasks/_invoke.py`                                      |           34 |         0 |         55 | 97.6%      |
| `calcipy/tasks/all_tasks.py`                                    |           48 |         0 |          0 | 95.5%      |
| `calcipy/tasks/cl.py`                                           |           28 |         5 |          0 | 75.0%      |
| `calcipy/tasks/defaults.py`                                     |           20 |         0 |          0 | 89.3%      |
| `calcipy/tasks/doc.py`                                          |           45 |         0 |          8 | 90.5%      |
| `calcipy/tasks/executable_utils.py`                             |           27 |         0 |          0 | 87.2%      |
| `calcipy/tasks/lint.py`                                         |           41 |         1 |          0 | 84.6%      |
| `calcipy/tasks/nox.py`                                          |            8 |         0 |          0 | 100.0%     |
| `calcipy/tasks/pack.py`                                         |           42 |        11 |          0 | 64.1%      |
| `calcipy/tasks/stale.py`                                        |            6 |         0 |          0 | 100.0%     |
| `calcipy/tasks/tags.py`                                         |           18 |         1 |          0 | 91.7%      |
| `calcipy/tasks/test.py`                                         |           45 |         1 |          2 | 89.2%      |
| `calcipy/tasks/types.py`                                        |           20 |         0 |          0 | 89.3%      |
| **Totals**                                                      |         1014 |        75 |        262 | 86.5%      |

Generated on: 2024-06-06
<!-- {cte} -->
