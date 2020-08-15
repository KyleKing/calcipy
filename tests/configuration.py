"""Global variables for testing."""

from pathlib import Path

import snoop

TEST_DIR = Path(__file__).parent
"""Path to the `test` directory that contains this file and all other tests."""

TEST_DATA_DIR = TEST_DIR / 'data'
"""Path to subdirectory with test data within the Test Directory."""

TEST_SNOOPER = snoop.Config(out=TEST_DIR / 'test.log', overwrite=True)
"""Snoop configuration for logging to a test.log file in the test directory."""
