"""Custom Pytest Configuration.

To use the custom markers, create a file `tests/conftest.py` and add this import:

```py
from calcipy.conftest import pytest_configure  # noqa: F401
```

For HTML Reports, see: https://pypi.org/project/pytest-html/.

```py
'''Custom PyTest-HTML Report Configuration.'''

from calcipy.conftest import pytest_html_results_table_header  # noqa: F401
from calcipy.conftest import pytest_html_results_table_row  # noqa: F401
from calcipy.conftest import pytest_runtest_makereport  # noqa: F401
```

"""

from datetime import datetime
from typing import Any

import pytest
from py.xml import html


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells: Any) -> None:
    """Modify results table in the pytest-html output.

    Args:
        cells: argument from pytest

    """
    cells.insert(1, html.th('Description'))
    cells.insert(1, html.th('Time', class_='sortable time', col='time'))
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_row(report: Any, cells: Any) -> None:
    """Modify results table in the pytest-html output.

    Args:
        report: argument from pytest
        cells: argument from pytest

    """
    try:
        cells.insert(1, html.td(report.description))
        cells.insert(1, html.td(datetime.utcnow(), class_='col-time'))
        cells.pop()
    except AttributeError:
        pass  # The test suite likely failed


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item: Any, call: Any) -> None:
    """Modify the pytest-html output.

    Args:
        item: argument from pytest
        call: argument from pytest

    Yields:
        outcome: required by pytest

    """
    try:
        outcome = yield
        report = outcome.get_result()
        report.description = str(item.function.__doc__)
    except AttributeError:
        pass  # The test suite likely failed


def pytest_configure(config: Any) -> None:
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
