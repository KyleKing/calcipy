# TODO

[Current Milestone](https://github.com/KyleKing/calcipy/milestone/1)

[Next Milestone](https://github.com/KyleKing/calcipy/milestone/2)

## Doc

> Code documentation first!

## Replace MockLogger with more Generic Intercept Logger

[Create new `dev/log_intercept.py` file](https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/)

## Even Better Toml

Schema for git not matching? See "dash_charts"

- https://github.com/tamasfe/taplo/pull/45/files
- https://github.com/tamasfe/taplo/issues/35#issuecomment-699277894

## Other

```sh
poetry run prospector package_name --strictness high

poetry run it --help
poetry run it package_name --show-plugins

poetry run doit run lint_python
poetry run diff-quality --violations=flake8 --fail-under=90 --compare-branch=origin/main  --html-report report.html
```
