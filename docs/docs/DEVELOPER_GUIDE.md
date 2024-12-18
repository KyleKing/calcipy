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
| File                                                | Statements | Missing | Excluded | Coverage |
|-----------------------------------------------------|-----------:|--------:|---------:|---------:|
| `calcipy/__init__.py`                               | 4          | 0       | 0        | 100.0%   |
| `calcipy/_runtime_type_check_setup.py`              | 12         | 0       | 37       | 100.0%   |
| `calcipy/can_skip.py`                               | 14         | 1       | 0        | 88.9%    |
| `calcipy/cli.py`                                    | 34         | 2       | 88       | 89.5%    |
| `calcipy/code_tag_collector/__init__.py`            | 5          | 2       | 0        | 60.0%    |
| `calcipy/code_tag_collector/_collector.py`          | 126        | 2       | 0        | 96.9%    |
| `calcipy/collection.py`                             | 37         | 4       | 52       | 83.7%    |
| `calcipy/dot_dict/__init__.py`                      | 5          | 2       | 0        | 60.0%    |
| `calcipy/dot_dict/_dot_dict.py`                     | 5          | 0       | 0        | 100.0%   |
| `calcipy/experiments/__init__.py`                   | 0          | 0       | 0        | 100.0%   |
| `calcipy/experiments/bump_programmatically.py`      | 22         | 22      | 0        | 0.0%     |
| `calcipy/experiments/check_duplicate_test_names.py` | 33         | 0       | 2        | 98.2%    |
| `calcipy/experiments/sync_package_dependencies.py`  | 47         | 47      | 0        | 0.0%     |
| `calcipy/file_search.py`                            | 32         | 0       | 2        | 100.0%   |
| `calcipy/invoke_helpers.py`                         | 27         | 6       | 0        | 72.4%    |
| `calcipy/markdown_table.py`                         | 29         | 4       | 0        | 80.5%    |
| `calcipy/md_writer/__init__.py`                     | 5          | 2       | 0        | 60.0%    |
| `calcipy/md_writer/_writer.py`                      | 91         | 7       | 0        | 88.7%    |
| `calcipy/noxfile/__init__.py`                       | 5          | 2       | 0        | 60.0%    |
| `calcipy/noxfile/_noxfile.py`                       | 39         | 2       | 51       | 91.1%    |
| `calcipy/scripts.py`                                | 6          | 0       | 51       | 100.0%   |
| `calcipy/tasks/__init__.py`                         | 0          | 0       | 0        | 100.0%   |
| `calcipy/tasks/all_tasks.py`                        | 36         | 2       | 0        | 94.7%    |
| `calcipy/tasks/cl.py`                               | 25         | 6       | 0        | 70.4%    |
| `calcipy/tasks/defaults.py`                         | 17         | 0       | 0        | 94.7%    |
| `calcipy/tasks/doc.py`                              | 29         | 0       | 8        | 100.0%   |
| `calcipy/tasks/executable_utils.py`                 | 31         | 2       | 0        | 91.4%    |
| `calcipy/tasks/lint.py`                             | 38         | 2       | 0        | 87.0%    |
| `calcipy/tasks/most_tasks.py`                       | 29         | 0       | 0        | 100.0%   |
| `calcipy/tasks/nox.py`                              | 8          | 0       | 0        | 100.0%   |
| `calcipy/tasks/pack.py`                             | 39         | 12      | 0        | 61.7%    |
| `calcipy/tasks/tags.py`                             | 18         | 1       | 0        | 90.0%    |
| `calcipy/tasks/test.py`                             | 39         | 1       | 2        | 93.6%    |
| `calcipy/tasks/types.py`                            | 11         | 0       | 0        | 100.0%   |
| **Totals**                                          | 898        | 131     | 293      | 81.7%    |

Generated on: 2024-12-07
<!-- {cte} -->
