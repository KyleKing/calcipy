"""DoIt Linting Utilities."""

from icecream import ic

from .doit_base import DIG, debug_action, if_found_unlink

# ----------------------------------------------------------------------------------------------------------------------
# General


def glob_path_list():
    """Find all Python files in project at the base directory, then relevant sub directories.

    Returns:
        list: List of paths to Python files (`*.py`)

    """
    path_list = [*DIG.cwd.glob('*.py')]
    for dir_name in [DIG.pkg_name, 'tests', 'examples', 'scripts', 'notebooks']:
        path_list.extend([*(DIG.cwd / dir_name).rglob('*.py')])
    return path_list


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
    """Configure `lint` as a task.

    Returns:
        dict: DoIt task

    """
    return lint(glob_path_list())


def radon_lint(path_list):
    """See documentation: https://radon.readthedocs.io/en/latest/intro.html. Lint project with Radon.

    Args:
        path_list: list of file paths to lint

    Returns:
        dict: DoIt task

    """
    actions = []
    for args in ['mi', 'cc --total-average -nb', 'hal']:
        actions.extend(
            [(ic, (f'# Radon with args: {args}', ))]
            + [f'poetry run radon {args} "{fn}"' for fn in path_list],
        )
    return debug_action(actions)


def task_radon_lint():
    """Configure `radon_lint` as a task.

    Returns:
        dict: DoIt task

    """
    return radon_lint(glob_path_list())


# ----------------------------------------------------------------------------------------------------------------------
# Formatting


def auto_format(path_list):
    """Format code with isort and autopep8.

    Args:
        path_list: list of file paths to modify

    Returns:
        dict: DoIt task

    """
    actions = [f'poetry run isort "{fn}" --settings-path "{DIG.isort_path}"' for fn in path_list]
    kwargs = f'--in-place --aggressive --global-config {DIG.flake8_path}'
    actions.extend([f'poetry run autopep8 "{fn}" {kwargs}' for fn in path_list])
    return debug_action(actions)


def task_auto_format():
    """Configure `auto_format` as a task.

    Returns:
        dict: DoIt task

    """
    return auto_format(glob_path_list())
