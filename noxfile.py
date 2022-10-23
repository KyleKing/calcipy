"""nox-poetry configuration file."""

from calcipy.dev.noxfile import build_check, build_dist, coverage, pin_dev_dependencies, tests  # noqa: F401

# Ensure that non-calcipy dev-dependencies are available in Nox environments
pin_dev_dependencies([
    'pytest-cache-assert>=2.0.0',
    'pytest-benchmark>=3.4.1',
    'pytest-recording>=0.12.0',
    'pytest-subprocess>=1.4.1',
])
