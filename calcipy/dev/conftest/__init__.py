try:
	from ._conftest import pytest_configure  # noqa: F401
	from ._conftest import pytest_html_results_table_header  # noqa: F401
	from ._conftest import pytest_html_results_table_row  # noqa: F401
	from ._conftest import pytest_runtest_makereport  # noqa: F401
except ImportError as exc:
    raise RuntimeError("The 'test' dependencies are missing") from exc
