# From:
# https://github.com/charliermarsh/ruff/blob/3e80c0d43e801c837eea81c6b75fd586ad532b1f/flake8_to_ruff/src/plugin.rs#L39-L60
in_ruff = {
    'flake8-annotations',
    'flake8-bandit',
    'flake8-blind-except',
    'flake8-bugbear',
    'flake8-builtins',
    'flake8-comprehensions',
    'flake8-datetimez',
    'flake8-debugger',
    'flake8-docstrings',
    'flake8-eradicate',
    'flake8-errmsg',
    'flake8-implicit-str-concat',
    'flake8-print',
    'flake8-pytest-style',
    'flake8-quotes',
    'flake8-return',
    'flake8-simplify',
    'flake8-tidy-imports',
    'mccabe',
    'pandas-vet',
    'pep8-naming',
    'pyupgrade',
}

in_calcipy = {
    'absolufy-imports',
    'autoflake',
    'cohesion',
    'dlint',
    # "flake8-2020", # https://github.com/charliermarsh/ruff/pull/688
    'flake8-aaa',
    'flake8-absolute-import',
    'flake8-adjustable-complexity',
    'flake8-annotations',
    'flake8-annotations-complexity',
    # "flake8-assertive",  # Wasn't using this anyway...https://pypi.org/project/flake8-assertive/
    'flake8-bandit',
    'flake8-blind-except',
    # "flake8-breakpoint",  # Would be caught in pre-commit anyway
    'flake8-broken-line',
    'flake8-bugbear',
    'flake8-builtins',
    'flake8-class-attributes-order',
    'flake8-comprehensions',
    'flake8-datetimez',
    'flake8-debugger',
    'flake8-docstrings',
    'flake8-eradicate',
    'flake8-executable',
    'flake8-expression-complexity',
    'flake8-fine-pytest',
    'flake8-fixme',
    'flake8-functions',
    'flake8-implicit-str-concat',
    'flake8-isort',  # Probably covered?
    'flake8-logging-format',
    'flake8-markdown',
    'flake8-pep3101',
    'flake8-pie',
    # "flake8-plone-hasattr",  # recommends using getattr(..., ..., None) with try/catch, but otherwise duplicate of bandit
    'flake8-print',
    'flake8-printf-formatting',
    'flake8-pytest-style',
    'flake8-quotes',
    'flake8-raise',
    'flake8-return',
    'flake8-simplify',
    'flake8-SQL',
    'flake8-string-format',
    'flake8-super',
    'flake8-tuple',
    'flake8-typing-imports',
    'flake8-use-pathlib',
    'flake8-variables-names',
    'pandas-vet',
    'pep8-naming',
    'proselint',
    'pylint',  # Ruff only partially replaces
    # "semgrep",  # ruff is considering ast-grep/plugins
    'tryceratops',
    'unimport',
    'vulture',  # ruff supports eradicate?
    'xenon',  # Radon wrapper
}


print(sorted(in_calcipy - in_ruff))
[
    'absolufy-imports',
    'cohesion',
    'dlint',
    'flake8-SQL',
    'flake8-aaa',
    'flake8-absolute-import',
    'flake8-adjustable-complexity',
    'flake8-annotations-complexity',
    'flake8-broken-line',
    'flake8-class-attributes-order',
    'flake8-executable',
    'flake8-expression-complexity',
    'flake8-fine-pytest',
    'flake8-fixme',
    'flake8-functions',
    'flake8-isort',
    'flake8-logging-format',
    'flake8-markdown',
    'flake8-pep3101',
    'flake8-pie',
    'flake8-printf-formatting',
    'flake8-raise',
    'flake8-string-format',
    'flake8-super',
    'flake8-tuple',
    'flake8-typing-imports',
    'flake8-use-pathlib',
    'flake8-variables-names',
    'proselint',
    'pylint',
    'tryceratops',
    'unimport',
    'vulture',
    'xenon',
]

print(sorted(in_ruff - in_calcipy))
[
    'flake8-errmsg',
    'flake8-tidy-imports',
    # [tool.ruff.flake8-tidy-imports]
    # banned-modules =
    #   mock = Use unittest.mock
    #  {python2to3}
    # TODO: Try out https://github.com/seddonym/import-linter
    #   For enforcing import contracts?
    # And example: https://github.com/charliermarsh/ruff/issues/1422#issuecomment-1370397812
    'mccabe',
    'pyupgrade',
]


# Example Projects with ruff:
# https://github.com/zulip/zulip/blob/main/pyproject.toml
# https://github.com/pypa/hatch/pull/607/files
