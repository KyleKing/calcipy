# TODO

1. Fix pdocs output for type
2. Fix podcs 4-indented code block errors
3. Fix deepsource issues
4. Replace MockLogger

## Replace MockLogger with more Generic Intercept Logger

[Create new `dev/log_intercept.py` file](https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/)

## Other

```sh
poetry run prospector package_name --strictness high

poetry run it --help
poetry run it package_name --show-plugins

poetry run doit run lint_python
poetry run diff-quality --violations=flake8 --fail-under=90 --compare-branch=origin/main  --html-report report.html
```

[autoflake](https://pypi.org/project/autoflake/)

```sh
poetry run autoflake --in-place --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports --remove-duplicate-keys ...files...

# Might be useful...
poetry run autoflake --in-place --expand-star-imports ...files...
```
