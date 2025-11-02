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
| File                                                    | Statements | Missing | Excluded | Coverage |
|---------------------------------------------------------|-----------:|--------:|---------:|---------:|
| `src/calcipy/__init__.py`                               | 4          | 0       | 0        | 100.0%   |
| `src/calcipy/_corallium/__init__.py`                    | 2          | 0       | 0        | 100.0%   |
| `src/calcipy/_corallium/file_helpers.py`                | 44         | 0       | 0        | 95.0%    |
| `src/calcipy/_runtime_type_check_setup.py`              | 13         | 0       | 37       | 100.0%   |
| `src/calcipy/can_skip.py`                               | 14         | 1       | 0        | 88.9%    |
| `src/calcipy/cli.py`                                    | 34         | 1       | 90       | 92.1%    |
| `src/calcipy/code_tag_collector/__init__.py`            | 5          | 2       | 0        | 60.0%    |
| `src/calcipy/code_tag_collector/_collector.py`          | 130        | 2       | 0        | 97.0%    |
| `src/calcipy/collection.py`                             | 41         | 3       | 52       | 87.2%    |
| `src/calcipy/dot_dict/__init__.py`                      | 5          | 2       | 0        | 60.0%    |
| `src/calcipy/dot_dict/_dot_dict.py`                     | 6          | 0       | 0        | 100.0%   |
| `src/calcipy/experiments/__init__.py`                   | 0          | 0       | 0        | 100.0%   |
| `src/calcipy/experiments/bump_programmatically.py`      | 22         | 22      | 0        | 0.0%     |
| `src/calcipy/experiments/check_duplicate_test_names.py` | 33         | 0       | 2        | 98.2%    |
| `src/calcipy/experiments/sync_package_dependencies.py`  | 47         | 47      | 0        | 0.0%     |
| `src/calcipy/file_search.py`                            | 32         | 0       | 2        | 100.0%   |
| `src/calcipy/invoke_helpers.py`                         | 27         | 4       | 0        | 79.3%    |
| `src/calcipy/markdown_table.py`                         | 28         | 4       | 0        | 80.0%    |
| `src/calcipy/md_writer/__init__.py`                     | 5          | 2       | 0        | 60.0%    |
| `src/calcipy/md_writer/_writer.py`                      | 93         | 6       | 0        | 89.7%    |
| `src/calcipy/noxfile/__init__.py`                       | 5          | 2       | 0        | 60.0%    |
| `src/calcipy/noxfile/_noxfile.py`                       | 12         | 0       | 30       | 100.0%   |
| `src/calcipy/scripts.py`                                | 6          | 0       | 51       | 100.0%   |
| `src/calcipy/tasks/__init__.py`                         | 0          | 0       | 0        | 100.0%   |
| `src/calcipy/tasks/all_tasks.py`                        | 37         | 0       | 0        | 100.0%   |
| `src/calcipy/tasks/cl.py`                               | 26         | 5       | 0        | 75.0%    |
| `src/calcipy/tasks/defaults.py`                         | 17         | 0       | 0        | 94.7%    |
| `src/calcipy/tasks/doc.py`                              | 29         | 0       | 8        | 100.0%   |
| `src/calcipy/tasks/executable_utils.py`                 | 32         | 0       | 0        | 97.2%    |
| `src/calcipy/tasks/lint.py`                             | 38         | 2       | 0        | 87.0%    |
| `src/calcipy/tasks/most_tasks.py`                       | 29         | 0       | 0        | 100.0%   |
| `src/calcipy/tasks/nox.py`                              | 8          | 0       | 0        | 100.0%   |
| `src/calcipy/tasks/pack.py`                             | 53         | 16      | 3        | 63.5%    |
| `src/calcipy/tasks/tags.py`                             | 18         | 1       | 0        | 90.0%    |
| `src/calcipy/tasks/test.py`                             | 40         | 1       | 2        | 93.8%    |
| `src/calcipy/tasks/types.py`                            | 11         | 0       | 0        | 100.0%   |
| **Totals**                                              | 946        | 123     | 277      | 83.2%    |

Generated on: 2025-11-02
<!-- {cte} -->
