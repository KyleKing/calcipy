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
| `calcipy/_temp_dg.py`                                           |            9 |         9 |          0 | 0.0%       |
| `calcipy/check_for_stale_packages/__init__.py`                  |            1 |         1 |          0 | 0.0%       |
| `calcipy/check_for_stale_packages/_check_for_stale_packages.py` |          111 |       111 |          0 | 0.0%       |
| `calcipy/code_tag_collector/__init__.py`                        |            1 |         1 |          0 | 0.0%       |
| `calcipy/code_tag_collector/_collector.py`                      |          127 |       127 |          0 | 0.0%       |
| `calcipy/dot_dict/__init__.py`                                  |            4 |         4 |          0 | 0.0%       |
| `calcipy/dot_dict/_dot_dict.py`                                 |            8 |         8 |          0 | 0.0%       |
| `calcipy/file_helpers.py`                                       |          116 |        53 |          6 | 54.3%      |
| `calcipy/file_search.py`                                        |           37 |        37 |          2 | 0.0%       |
| `calcipy/md_writer/__init__.py`                                 |            4 |         4 |          0 | 0.0%       |
| `calcipy/md_writer/_writer.py`                                  |           94 |        94 |          0 | 0.0%       |
| `calcipy/noxfile/__init__.py`                                   |            4 |         4 |          0 | 0.0%       |
| `calcipy/noxfile/_noxfile.py`                                   |           72 |        72 |          2 | 0.0%       |
| `calcipy/scripts.py`                                            |            7 |         7 |          0 | 0.0%       |
| `calcipy/tasks/__init__.py`                                     |            0 |         0 |          0 | 100.0%     |
| `calcipy/tasks/all_tasks.py`                                    |           44 |        44 |          0 | 0.0%       |
| `calcipy/tasks/cl.py`                                           |           28 |        28 |          0 | 0.0%       |
| `calcipy/tasks/defaults.py`                                     |            9 |         3 |          0 | 66.7%      |
| `calcipy/tasks/doc.py`                                          |           37 |        37 |          5 | 0.0%       |
| `calcipy/tasks/invoke_helpers.py`                               |           10 |         1 |          0 | 90.0%      |
| `calcipy/tasks/lint.py`                                         |           51 |        51 |          0 | 0.0%       |
| `calcipy/tasks/nox.py`                                          |            8 |         8 |          0 | 0.0%       |
| `calcipy/tasks/pack.py`                                         |           26 |        26 |          0 | 0.0%       |
| `calcipy/tasks/stale.py`                                        |            7 |         7 |          0 | 0.0%       |
| `calcipy/tasks/tags.py`                                         |           14 |        14 |          0 | 0.0%       |
| `calcipy/tasks/test.py`                                         |           35 |         0 |          2 | 100.0%     |
| `calcipy/tasks/types.py`                                        |           15 |         0 |          0 | 100.0%     |
| **Totals**                                                      |          883 |       751 |         17 | 14.9%      |

Generated on: 2023-02-19
<!-- {cte} -->
