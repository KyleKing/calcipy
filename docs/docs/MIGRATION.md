# Migration Guide

## `v5`

The breaking changes include removing `stale` and `pack.check_license`

### Speed Test

After further reduction of dependencies, the CLI performance has continued to improve:

```sh
> poetry run pip freeze | wc -l
79
```

```sh
> hyperfine -m 20 --warmup 5 ./run
Benchmark 1: ./run
  Time (mean ± σ):     397.1 ms ±  12.2 ms    [User: 268.4 ms, System: 57.0 ms]
  Range (min … max):   385.9 ms … 421.5 ms    20 runs
```

## `v4`

The total number of dependencies was reduce even further by replacing flake8, isort, and other tooling with ruff; fewer mkdocs plugins; and fewer steps in the `main` run task to speed up normal usage.

The only breaking [change impacted `recipes`](https://github.com/KyleKing/recipes/commit/b3fcf8136af77ccf1bd3ee1fb4297b79dd7e86ea#diff-4bf564fcd9dbaec9e9807f16f649791c1e333f89db8160ad715d3c0c09a1a65c) when `write_autoformatted_md_sections` was renamed to `write_template_formatted_md_sections`.

### Speed Test

Following up on performance checks from the `v2` migration. The performance is comparable, but you will see savings in cache size and poetry install and when running `main` (`./run main` for Calcipy, currently takes ~20s)

```sh
> hyperfine -m 20 --warmup 5 ./run
Benchmark 1: ./run
Time (mean ± σ):     863.9 ms ±  10.0 ms    [User: 550.7 ms, System: 102.3 ms]
Range (min … max):   848.5 ms … 885.3 ms    20 runs
> hyperfine -m 20 --warmup 5 "poetry run calcipy-tags"
Benchmark 1: poetry run calcipy-tags
Time (mean ± σ):     770.5 ms ±   5.7 ms    [User: 470.6 ms, System: 89.5 ms]
Range (min … max):   760.1 ms … 780.3 ms    20 runs
```

## `v3`

Replaced features from flake8 and plugins with corresponding checks from ruff, however both are still used in parallel.

## `v2`

### Background

calcipy `v1` was a complete rewrite to switch from `doit` to `invoke`:

- with `invoke`, tasks can be run from anywhere without a `dodo.py` file
- tasks can be loaded lazily, which means that some performance gains are possible
- since there is no shared state file, tasks can be more easily run from pre-commit or generally in parallel

`doit` excelled at clearly delineated task output and run summary, but `invoke` isn't designed that way. I would like to improve the CLI output, but the benefits are worth this tradeoff.

calcipy `v0` was built on [doit](https://pypi.org/project/doit/) and thus required a `dodo.py` file. I began adding `cement` to support a separate CLI for `calcipy` installed with `pipx` or `uvx`, but that required a lot of boilerplate code. With `doit`, the string command needed to be complete at task evaluation rather than runtime, so globbing files couldn't be resolved lazily.

### Migration

While refactoring, the global configuration was mostly removed (`DoitGlobals`) along with a few tasks, but the main functionality is still present. Any project dependent on `calcipy` will need substantial changes. The easiest way to start migrating is to run `copier copy gh:KyleKing/calcipy_template .` for [calcipy_template](https://github.com/KyleKing/calcipy_template)

### Speed Test

It turns out that switching to `invoke` appears to have only saved 100ms

```sh
> hyperfine -m 20 --warmup 5 ./run
Benchmark 1: ./run
Time (mean ± σ):     863.9 ms ±  10.0 ms    [User: 550.7 ms, System: 102.3 ms]
Range (min … max):   848.5 ms … 885.3 ms    20 runs
> hyperfine -m 20 --warmup 5 "poetry run calcipy-tags"
Benchmark 1: poetry run calcipy-tags
Time (mean ± σ):     770.5 ms ±   5.7 ms    [User: 470.6 ms, System: 89.5 ms]
Range (min … max):   760.1 ms … 780.3 ms    20 runs
```

```sh
> hyperfine -m 20 --warmup 5 "poetry run python -c 'print(1)'"
Benchmark 1: poetry run python -c 'print(1)'
Time (mean ± σ):     377.9 ms ±   3.1 ms    [User: 235.0 ms, System: 61.8 ms]
Range (min … max):   372.7 ms … 384.0 ms    20 runs
> hyperfine -m 20 --warmup 5 ./run
Benchmark 1: ./run
Time (mean ± σ):     936.0 ms ±  26.9 ms    [User: 1548.2 ms, System: 1687.7 ms]
Range (min … max):   896.4 ms … 1009.4 ms    20 runs
> hyperfine -m 20 --warmup 5 "poetry run calcipy_tags"
Benchmark 1: poetry run calcipy_tags
Time (mean ± σ):     618.5 ms ±  29.7 ms    [User: 1536.8 ms, System: 1066.2 ms]
Range (min … max):   578.2 ms … 694.9 ms    20 runs
> hyperfine -m 20 --warmup 5 "poetry run doit list"
Benchmark 1: poetry run doit list
Time (mean ± σ):      1.002 s ±  0.015 s    [User: 1.643 s, System: 1.682 s]
Range (min … max):    0.974 s …  1.023 s    20 runs
```

Additionally, the major decrease in dependencies will make install and update actions much faster. With the recommended extras installed, `calcipy-v1` has 124 dependencies (with all extras, 164) vs. `calcipy-v0`'s 259. Counted with: `cat .calcipy_packaging.lock | jq 'keys' | wc -l`

### Code Comparison

Accounting for code extracted to `corallium`, the overall number of lines decreased from 1772 to 1550 or only 12%, while increasing the CLI and `pre-commit` capabilities.

```sh
~/calcipy-v0 > cloc calcipy
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                          26            942           1075           1772
-------------------------------------------------------------------------------
SUM:                            26            942           1075           1772
-------------------------------------------------------------------------------
~/calcipy > cloc calcipy
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                          27            454            438           1185
-------------------------------------------------------------------------------
SUM:                            27            454            438           1185
-------------------------------------------------------------------------------
~/corallium > cloc corallium
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                           7            176            149            365
-------------------------------------------------------------------------------
SUM:                             7            176            149            365
-------------------------------------------------------------------------------

~/calcipy > cloc tests
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
YAML                             2              0              0            580
Python                          19            176             68            578
JSON                             2              0              0             60
Markdown                         3              9             10              8
Text                             1              0              0              2
-------------------------------------------------------------------------------
SUM:                            27            185             78           1228
-------------------------------------------------------------------------------
~/calcipy-v0 > cloc tests
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
JSON                            30              0              0            762
YAML                             2              0              0            580
Python                          24            314            186            578
Markdown                         3              9             10              8
-------------------------------------------------------------------------------
SUM:                            59            323            196           1928
-------------------------------------------------------------------------------
~/corallium > cloc tests
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                           6             36             15             69
Markdown                         1              1              0              2
-------------------------------------------------------------------------------
SUM:                             7             37             15             71
-------------------------------------------------------------------------------
```

### doit output

I would like to restore the `doit` task summary, but `invoke`'s architecture doesn't really make this possible. The `--continue` option was extremely useful, but that also might not be achievable.

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
