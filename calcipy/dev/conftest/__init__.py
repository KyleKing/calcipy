try:
	from ._conftest import (  # noqa: F401
		pytest_configure,
		pytest_html_results_table_header,
		pytest_html_results_table_row,
		pytest_runtest_makereport,
	)
except ImportError as exc:
    raise RuntimeError("The 'test' dependencies are missing") from exc
