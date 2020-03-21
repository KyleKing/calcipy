"""DoIt Linting Utilities."""

from .doit_base import DIG, debug_action, if_found_unlink

# ----------------------------------------------------------------------------------------------------------------------
# Linting


def check_linting_errors(flake8_log_path):
    """Check for errors reported in flake8 log file. Removes log file if no errors detected.

    Args:
        flake8_log_path: path to flake8 log file created with flag: `--output-file=flake8_log_path`

    Raises:
        RuntimeError: if flake8 log file contains any text results

    """
    if len(flake8_log_path.read_text().strip()) > 0:
        raise RuntimeError(f'Found Linting Errors. Review: {flake8_log_path}')
    if_found_unlink(flake8_log_path)


def lint(path_list, flake8_path=DIG.flake8_path):
    """Lint specified files creating summary log file of errors.

    Args:
        path_list: list of file paths to lint
        flake8_path: path to flake8 configuration file. Default is `DIG.flake8_path`

    Returns:
        dict: DoIt task

    """
    flake8_log_path = DIG.cwd / 'flake8.log'
    flags = f'--config={flake8_path}  --output-file={flake8_log_path} --exit-zero'
    return debug_action([
        (if_found_unlink, (flake8_log_path, )),
        *[f'poetry run flake8 "{fn}" {flags}' for fn in path_list],
        (check_linting_errors, (flake8_log_path, )),
    ])


def task_lint():
    """Configure linting as a task.

    Returns:
        dict: DoIt task

    """
    path_list = [*DIG.cwd.glob('*.py')]
    for base_path in [DIG.cwd / DIG.pkg_name, DIG.cwd / 'tests']:
        path_list.extend([*base_path.glob('**/*.py')])
    return lint(path_list)
