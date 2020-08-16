"""Global variables for testing."""

from pathlib import Path

import pytest
import snoop

from dash_dev.doit_base import DIG, DoItGlobals

TEST_DIR = Path(__file__).parent
"""Path to the `test` directory that contains this file and all other tests."""

TEST_DATA_DIR = TEST_DIR / 'data'
"""Path to subdirectory with test data within the Test Directory."""

DIG_CWD = TEST_DATA_DIR / 'doit_project'
"""Local directory used for testing the DoIt globals."""

DIG.set_paths(DIG_CWD)  # Warning: This modifies the global `DIG` which is necessary for some tests

TEST_SNOOPER = snoop.Config(out=TEST_DIR / 'test.log', overwrite=True)
"""Snoop configuration for logging to a test.log file in the test directory."""


@pytest.fixture()
def initialize_dig():
    """Initialize DoItGlobals as a fixture.

    Returns:
        class: DoItGlobals instance with the cwd set to `DIG_CWD`

    """
    dig = DoItGlobals
    dig.set_paths(DIG_CWD)
    return dig
