# Migration Guide

## `calcipy 1.0.0`

calcipy `v1` was a rewrite for performance, both to reduce the number of dependencies and to make task loading lazy. A few tasks were removed, but the main functionality is still present, albeit with

calcipy `v0` was built on [doit](https://pypi.org/project/doit/) and required a `doit.py` file. With `doit`, each task was evaluated to get the list of tasks, but this became slower as the number of tasks grow.

The easiest way to migrate is to run `copier update` with [calcipy_template](https://github.com/KyleKing/calcipy_template)
