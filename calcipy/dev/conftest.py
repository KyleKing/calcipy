"""Custom Pytest Configuration.

To use the custom markers, create a file `tests/conftest.py` and add this import:

```python3
from calcipy.dev.conftest import pytest_configure  # noqa: F401
```

For HTML Reports, see: https://pypi.org/project/pytest-html/.

```python3
'''Custom PyTest-HTML Report Configuration.'''

from calcipy.dev.conftest import pytest_html_results_table_header  # noqa: F401
from calcipy.dev.conftest import pytest_html_results_table_row  # noqa: F401
from calcipy.dev.conftest import pytest_runtest_makereport  # noqa: F401
```

"""

from datetime import datetime
from typing import Any, Generator

from loguru import logger

_HAS_TEST_IMPORTS = False
try:
    import pytest
    from py.xml import html
    _HAS_TEST_IMPORTS = True
except ImportError:  # pragma: no cover
    ...

if _HAS_TEST_IMPORTS:
    @pytest.mark.optionalhook()
    def pytest_html_results_table_header(cells: Any) -> None:  # pragma: no cover
        """Modify results table in the pytest-html output.

        Args:
            cells: argument from pytest

        """
        cells.insert(1, html.th('Description'))
        cells.insert(1, html.th('Time', class_='sortable time', col='time'))

    @pytest.mark.optionalhook()
    def pytest_html_results_table_row(report: Any, cells: Any) -> None:  # pragma: no cover
        """Modify results table in the pytest-html output.

        Args:
            report: argument from pytest
            cells: argument from pytest

        """
        try:
            cells.insert(1, html.td(report.description))
            cells.insert(1, html.td(str(datetime.utcnow()), class_='col-time'))
        except AttributeError:
            ...  # The test suite likely failed

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(item: Any, call: Any) -> Generator:  # type: ignore[type-arg]  # pragma: no cover
        """Modify the pytest-html output.

        Args:
            item: argument from pytest
            call: argument from pytest

        Yields:
            outcome: required by pytest

        """
        try:
            logger.debug('call excinfo={excinfo}', excinfo=call.excinfo)
            outcome = yield
            report = outcome.get_result()
            report.description = str(item.function.__doc__)
            report.duration_formatter = '%H:%M:%S.%f'
        except AttributeError:
            ...  # The test suite likely failed

    def pytest_configure(config: Any) -> None:
        """Configure pytest with custom markers (SLOW, INTERACTIVE, and CURRENT).

        Args:
            config: pytest configuration object

        """
        config.addinivalue_line(
            'markers',
            'SLOW: tests that take a long time (>15s) and can be skipped with `-m "not SLOW"`',
        )
        config.addinivalue_line(
            'markers',
            'INTERACTIVE: tests that open a Chrome window and can be skipped with `-m "not INTERACTIVE"`',
        )
        config.addinivalue_line(
            'markers',
            'CURRENT: tests that are currently being developed. Useful for TDD with ptw `poetry run ptw -- -m CURRENT`',
        )
