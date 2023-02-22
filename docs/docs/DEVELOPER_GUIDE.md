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
| `calcipy/_log.py`                                               |            2 |         0 |          0 | 100.0%     |
| `calcipy/check_for_stale_packages/__init__.py`                  |            4 |         2 |          0 | 50.0%      |
| `calcipy/check_for_stale_packages/_check_for_stale_packages.py` |          109 |         9 |          2 | 91.7%      |
| `calcipy/code_tag_collector/__init__.py`                        |            4 |         2 |          0 | 50.0%      |
| `calcipy/code_tag_collector/_collector.py`                      |          127 |        19 |          0 | 85.0%      |
| `calcipy/dot_dict/__init__.py`                                  |            4 |         2 |          0 | 50.0%      |
| `calcipy/dot_dict/_dot_dict.py`                                 |            8 |         0 |          0 | 100.0%     |
| `calcipy/file_helpers.py`                                       |          125 |        18 |          8 | 85.6%      |
| `calcipy/file_search.py`                                        |           38 |         0 |          2 | 100.0%     |
| `calcipy/md_writer/__init__.py`                                 |            4 |         2 |          0 | 50.0%      |
| `calcipy/md_writer/_writer.py`                                  |           94 |         7 |          0 | 92.6%      |
| `calcipy/noxfile/__init__.py`                                   |            4 |         2 |          0 | 50.0%      |
| `calcipy/noxfile/_noxfile.py`                                   |           48 |         1 |         26 | 97.9%      |
| `calcipy/scripts.py`                                            |            7 |         7 |          0 | 0.0%       |
| `calcipy/tasks/__init__.py`                                     |            0 |         0 |          0 | 100.0%     |
| `calcipy/tasks/all_tasks.py`                                    |           54 |         6 |          0 | 88.9%      |
| `calcipy/tasks/cl.py`                                           |           28 |         6 |          0 | 78.6%      |
| `calcipy/tasks/defaults.py`                                     |            9 |         0 |          0 | 100.0%     |
| `calcipy/tasks/doc.py`                                          |           41 |        17 |          5 | 58.5%      |
| `calcipy/tasks/lint.py`                                         |           49 |         1 |          0 | 98.0%      |
| `calcipy/tasks/nox.py`                                          |            8 |         0 |          0 | 100.0%     |
| `calcipy/tasks/pack.py`                                         |           26 |         4 |          0 | 84.6%      |
| `calcipy/tasks/stale.py`                                        |            8 |         2 |          0 | 75.0%      |
| `calcipy/tasks/tags.py`                                         |           15 |         0 |          0 | 100.0%     |
| `calcipy/tasks/test.py`                                         |           37 |         1 |          2 | 97.3%      |
| `calcipy/tasks/types.py`                                        |           15 |         0 |          0 | 100.0%     |
| **Totals**                                                      |          870 |       108 |         45 | 87.6%      |

Generated on: 2023-02-21
<!-- {cte} -->
