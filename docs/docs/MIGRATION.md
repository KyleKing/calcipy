# Migration Guide

## `calcipy 1.0.0`

calcipy `v1` was a rewrite for performance, both to reduce the number of dependencies and to make task loading lazy. Switching to invoke also meant the tasks could be vendored and run from anywhere without a `dodo.py` file. While refactoring, the global configuration was mostly removed along with a few tasks, but the main functionality is still present. The major loss with these changes was the highly readable output from doit, which I don't yet have a way of replicating with invoke.

calcipy `v0` was built on [doit](https://pypi.org/project/doit/) and required a `doit.py` file. With `doit`, each task was evaluated to get the list of tasks, but this became slower as the number of tasks grow.

The easiest way to migrate is to run `copier update` with [calcipy_template](https://github.com/KyleKing/calcipy_template)

### Speed Test

It turns out that switching to `invoke` appears to have only saved 100ms

```sh
> hyperfine -m 20 --warmup 5 "poetry run python -c 'print(1)'"
Benchmark 1: poetry run python -c 'print(1)'
  Time (mean ± σ):     377.9 ms ±   3.1 ms    [User: 235.0 ms, System: 61.8 ms]
  Range (min … max):   372.7 ms … 384.0 ms    20 runs
> hyperfine -m 20 --warmup 5 ./run
Benchmark 1: ./run
  Time (mean ± σ):     936.0 ms ±  26.9 ms    [User: 1548.2 ms, System: 1687.7 ms]
  Range (min … max):   896.4 ms … 1009.4 ms    20 runs
> hyperfine -m 20 --warmup 5 "poetry run doit list"
Benchmark 1: poetry run doit list
  Time (mean ± σ):      1.002 s ±  0.015 s    [User: 1.643 s, System: 1.682 s]
  Range (min … max):    0.974 s …  1.023 s    20 runs
```

### doit output

<!-- TODO: Look into running tasks from within other tasks -->

I would like to restore the `doit` task summary and more readable task descriptions, but `invoke`'s architecture doesn't really make this possible. The `--continue` option was extremely useful, but that also might not be achievable.

```sh
> poetry run doit run
.  format_recipes > [
        Python: function format_recipes
]

2023-02-19 10:40:23.954 | INFO     | recipes.formatter:_write_toc:287 - Creating TOC for: ./recipes/docs/breakfast
2023-02-19 10:40:23.957 | INFO     | recipes.formatter:_write_toc:287 - Creating TOC for: ./recipes/docs/rice
2023-02-19 10:40:23.959 | INFO     | recipes.formatter:_write_toc:287 - Creating TOC for: ./recipes/docs/meals
2023-02-19 10:40:23.964 | INFO     | recipes.formatter:_write_toc:287 - Creating TOC for: ./recipes/docs/seafood
2023-02-19 10:40:23.967 | INFO     | recipes.formatter:_write_toc:287 - Creating TOC for: ./recipes/docs/pizza
2023-02-19 10:40:23.969 | INFO     | recipes.formatter:_write_toc:287 - Creating TOC for: ./recipes/docs/poultry
2023-02-19 10:40:23.972 | INFO     | recipes.formatter:_write_toc:287 - Creating TOC for: ./recipes/docs/sushi
.  collect_code_tags > [
        Python: function write_code_tag_file
]

.  cl_write > [
        Cmd: poetry run cz changelog
        Python: function _move_cl
]

.  lock > [
        Cmd: poetry lock --no-update
]

Resolving dependencies...
.  nox_coverage > [
        Cmd: poetry run nox --error-on-missing-interpreters --session coverage
]

...

doit> Summary:
doit> format_recipes was successful
doit> collect_code_tags was successful
doit> cl_write was successful
doit> lock was successful
doit> nox_coverage was successful
doit> auto_format was successful
doit> document was successful
doit> check_for_stale_packages was successful
doit> pre_commit_hooks failed (red)
doit> lint_project was not run
doit> static_checks was not run
doit> security_checks was not run
doit> check_types was not run
```
