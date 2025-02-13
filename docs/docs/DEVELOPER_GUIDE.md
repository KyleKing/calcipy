# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/calcipy.git
cd calcipy
uv sync --all-extras

# See the available tasks
uv run calcipy
# Or use a local 'run' file (so that 'calcipy' can be extended)
./run

# Run the default task list (lint, auto-format, test coverage, etc.)
./run main

# Make code changes and run specific tasks as needed:
./run lint.fix test

# Install globally
uv tool install ".[ddict,doc,experimental,lint,nox,tags,test,types]" --force --editable
```

### Maintenance

Dependency upgrades can be accomplished with:

```sh
uv lock --upgrade
uv sync --all-extras
```

## Publishing

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy). Either set 'UV_PUBLISH_TOKEN' or input the generated token when prompted by the command.

```sh
./run main pack.publish --to-test-pypi
```

To publish to the real PyPi

```sh
./run release

# Or for a pre-release
./run release --suffix=rc
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                                | Statements | Missing | Excluded | Coverage |
|-----------------------------------------------------|-----------:|--------:|---------:|---------:|
| `calcipy/__init__.py`                               | 4          | 0       | 0        | 100.0%   |
| `calcipy/_corallium/__init__.py`                    | 0          | 0       | 0        | 100.0%   |
| `calcipy/_corallium/file_helpers.py`                | 11         | 1       | 0        | 90.9%    |
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
| `calcipy/markdown_table.py`                         | 28         | 4       | 0        | 80.0%    |
| `calcipy/md_writer/__init__.py`                     | 5          | 2       | 0        | 60.0%    |
| `calcipy/md_writer/_writer.py`                      | 91         | 7       | 0        | 88.7%    |
| `calcipy/noxfile/__init__.py`                       | 5          | 5       | 0        | 0.0%     |
| `calcipy/noxfile/_noxfile.py`                       | 10         | 10      | 27       | 0.0%     |
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
| `calcipy/tasks/pack.py`                             | 53         | 19      | 3        | 58.7%    |
| `calcipy/tasks/tags.py`                             | 18         | 1       | 0        | 90.0%    |
| `calcipy/tasks/test.py`                             | 40         | 1       | 2        | 93.8%    |
| `calcipy/tasks/types.py`                            | 11         | 0       | 0        | 100.0%   |
| **Totals**                                          | 894        | 150     | 272      | 79.9%    |

Generated on: 2025-02-13
<!-- {cte} -->
