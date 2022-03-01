"""Test proc_helpers."""

import shlex
from subprocess import CalledProcessError  # nosec

import pytest

from calcipy.proc_helpers import run_cmd


def test_run_cmd():
    """Test run_cmd."""
    with pytest.raises(CalledProcessError):
        run_cmd('gibberish')


def test_run_cmd(fake_process):
    """Test run_cmd."""
    process = 'git branch'
    expected = 'fake output'
    fake_process.register(shlex.split(process), stdout=[expected, ''])

    result = run_cmd(process)

    assert result == expected + '\n\n'
