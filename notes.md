# TODO

1. Replace MockLogger

## Replace MockLogger with more Generic Intercept Logger

[Create new `dev/log_intercept.py` file](https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/)

## Other

```sh
poetry add it -D
poetry run it --help
poetry run it calcipy --show-plugins

poetry run doit run lint_python
poetry run diff-quality --violations=flake8 --fail-under=90 --compare-branch=origin/main  --html-report report.html
```
