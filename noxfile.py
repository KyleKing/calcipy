"""nox-poetry configuration file."""

from calcipy.dev.noxfile import build_check, build_dist, coverage, pin_dev_dependencies, tests  # noqa: F401

# Ensure that non-calcipy dev-dependencies are available in Nox environments
pin_dev_dependencies([
    'hypothesis["cli"]>=6.46.9',
    'pytest-benchmark>=3.4.1"',
    'pytest-cache-assert>=3.0.5"',
    'pytest-recording>=0.12.0"',
    'pytest-shell-utilities>=1.7.0"',
    'pytest-subprocess>=1.4.1"',
])
