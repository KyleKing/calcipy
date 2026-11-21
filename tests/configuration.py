"""Global variables for testing."""

import os
import subprocess  # noqa: S404
import sys
from pathlib import Path

from corallium.file_helpers import delete_dir, ensure_dir

TEST_DIR = Path(__file__).resolve().parent
"""Path to the `test` directory that contains this file and all other tests."""

APP_DIR = TEST_DIR.parent
"""Application directory."""

TEST_DATA_DIR = TEST_DIR / 'data'
"""Path to subdirectory with test data within the Test Directory."""

TEST_TMP_CACHE = TEST_DIR / '_tmp_cache'
"""Path to the temporary cache folder in the Test directory."""


def clear_test_cache() -> None:
    """Remove the test cache directory if present."""
    delete_dir(TEST_TMP_CACHE)
    ensure_dir(TEST_TMP_CACHE)


def run_in_ascii_locale(script: str, cwd: Path) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    """Run a Python script in a subprocess whose default file encoding is ASCII and stdio is UTF-8.

    Returns:
        CompletedProcess: the finished subprocess with captured text output

    """
    env = {**os.environ, 'LC_ALL': 'C', 'PYTHONCOERCECLOCALE': '0', 'PYTHONUTF8': '0', 'PYTHONIOENCODING': 'utf-8'}
    return subprocess.run(  # noqa: S603
        [sys.executable, '-c', script], cwd=cwd, env=env, capture_output=True, text=True, check=False
    )
