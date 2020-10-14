"""Custom Pytest Configuration.

To use the custom markers, create a file `tests/conftest.py` and add this import:

```py
from dash_dev.conftest import pytest_configure  # noqa: F401
```

For HTML Reports, see: https://pypi.org/project/pytest-html/.

"""


def pytest_configure(config):
    """Configure pytest with custom markers (SLOW, CHROME, and CURRENT).

    Args:
        config: pytest configuration object

    """
    config.addinivalue_line(
        'markers',
        'SLOW: tests that take a long time (>15s) and can be skipped with `-m "not SLOW"`',
    )
    config.addinivalue_line(
        'markers',
        'CHROME: tests that open a Chrome window and can be skipped with `-m "not CHROME"`',
    )
    config.addinivalue_line(
        'markers',
        'CURRENT: tests that are currently being developed. Useful for TDD with ptw `poetry run ptw -- -m CURRENT`',
    )
