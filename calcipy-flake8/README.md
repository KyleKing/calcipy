# Calcipy-Flake8

In order to reduce the size of `calcipy`, I have split the flake8 packages that are yet to be supported by ruff into a separate package to be used in `pre-commit`.

```yaml
repos:
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [calcipy-flake8 >= 0.0.1]
```
