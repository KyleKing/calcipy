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
| File                                                            | Statements | Missing | Excluded | Coverage |
|-----------------------------------------------------------------|------------|---------|----------|----------|
| `calcipy/__init__.py`                                           | 4          | 0       | 0        | 100.0%   |
| `calcipy/_md_helpers.py`                                        | 9          | 0       | 0        | 100.0%   |
| `calcipy/_runtime_type_check_setup.py`                          | 13         | 0       | 33       | 100.0%   |
| `calcipy/can_skip.py`                                           | 14         | 1       | 0        | 88.9%    |
| `calcipy/check_for_stale_packages/__init__.py`                  | 5          | 2       | 0        | 60.0%    |
| `calcipy/check_for_stale_packages/_check_for_stale_packages.py` | 132        | 13      | 3        | 86.6%    |
| `calcipy/cli.py`                                                | 34         | 1       | 88       | 92.9%    |
| `calcipy/code_tag_collector/__init__.py`                        | 5          | 2       | 0        | 60.0%    |
| `calcipy/code_tag_collector/_collector.py`                      | 130        | 2       | 0        | 93.9%    |
| `calcipy/collection.py`                                         | 41         | 3       | 52       | 86.5%    |
| `calcipy/dot_dict/__init__.py`                                  | 5          | 2       | 0        | 60.0%    |
| `calcipy/dot_dict/_dot_dict.py`                                 | 6          | 0       | 0        | 100.0%   |
| `calcipy/experiments/__init__.py`                               | 0          | 0       | 0        | 100.0%   |
| `calcipy/experiments/bump_programmatically.py`                  | 22         | 22      | 0        | 0.0%     |
| `calcipy/experiments/check_duplicate_test_names.py`             | 33         | 0       | 2        | 98.2%    |
| `calcipy/experiments/sync_package_dependencies.py`              | 47         | 47      | 0        | 0.0%     |
| `calcipy/file_search.py`                                        | 32         | 0       | 2        | 100.0%   |
| `calcipy/invoke_helpers.py`                                     | 27         | 4       | 0        | 83.8%    |
| `calcipy/md_writer/__init__.py`                                 | 5          | 2       | 0        | 60.0%    |
| `calcipy/md_writer/_writer.py`                                  | 91         | 6       | 0        | 89.6%    |
| `calcipy/noxfile/__init__.py`                                   | 5          | 2       | 0        | 60.0%    |
| `calcipy/noxfile/_noxfile.py`                                   | 39         | 2       | 51       | 91.5%    |
| `calcipy/scripts.py`                                            | 6          | 0       | 51       | 100.0%   |
| `calcipy/tasks/__init__.py`                                     | 0          | 0       | 0        | 100.0%   |
| `calcipy/tasks/all_tasks.py`                                    | 36         | 0       | 0        | 93.8%    |
| `calcipy/tasks/cl.py`                                           | 26         | 5       | 0        | 78.1%    |
| `calcipy/tasks/defaults.py`                                     | 17         | 0       | 0        | 90.5%    |
| `calcipy/tasks/doc.py`                                          | 29         | 0       | 8        | 94.9%    |
| `calcipy/tasks/executable_utils.py`                             | 32         | 0       | 0        | 90.9%    |
| `calcipy/tasks/lint.py`                                         | 38         | 2       | 0        | 86.2%    |
| `calcipy/tasks/most_tasks.py`                                   | 32         | 0       | 0        | 100.0%   |
| `calcipy/tasks/nox.py`                                          | 8          | 0       | 0        | 100.0%   |
| `calcipy/tasks/pack.py`                                         | 47         | 13      | 0        | 62.0%    |
| `calcipy/tasks/stale.py`                                        | 6          | 0       | 0        | 100.0%   |
| `calcipy/tasks/tags.py`                                         | 18         | 1       | 0        | 90.9%    |
| `calcipy/tasks/test.py`                                         | 39         | 1       | 2        | 90.9%    |
| `calcipy/tasks/types.py`                                        | 11         | 0       | 0        | 93.3%    |
| **Totals**                                                      | 1044       | 133     | 292      | 83.0%    |

Generated on: 2024-10-31
<!-- {cte} -->
