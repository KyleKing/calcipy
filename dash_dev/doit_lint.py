"""DoIt Linting Utilities."""

from icecream import ic

from .doit_base import DIG, debug_action, if_found_unlink

# ----------------------------------------------------------------------------------------------------------------------
# General


def glob_path_list(dir_names=None):
    """Find all Python files in project at the base directory, then relevant sub directories.

    Args:
        dir_names: list of string directory names to parse in DIG.source_path. Default is `[pkg_name, tests, examples, scripts]`

    Returns:
        list: List of paths to Python files (`*.py`)

    """
    if dir_names is None:
        dir_names = [DIG.pkg_name, 'tests', 'examples', 'scripts']
    path_list = [*DIG.source_path.glob('*.py')]
    for dir_name in dir_names:
        path_list.extend([*(DIG.source_path / dir_name).rglob('*.py')])
    return path_list


# ----------------------------------------------------------------------------------------------------------------------
# Linting


def check_linting_errors(flake8_log_path, ignore_errors=None):  # noqa: CCR001
    """Check for errors reported in flake8 log file. Removes log file if no errors detected.

    Args:
        flake8_log_path: path to flake8 log file created with flag: `--output-file=flake8_log_path`
        ignore_errors: list of error codes to ignore (beyond the flake8 config settings). Default is None

    Raises:
        RuntimeError: if flake8 log file contains any text results

    """
    flake8_full_path = flake8_log_path.parent / f'{flake8_log_path.stem}-full{flake8_log_path.suffix}'
    log_contents = flake8_log_path.read_text().strip()
    review_info = f'. Review: {flake8_log_path}'
    if ignore_errors is not None:
        # Backup the full list of errors
        flake8_full_path.write_text(log_contents)
        # Exclude the errors specificed to be ignored by the user
        lines = []
        for line in log_contents.split('\n'):
            if not any(f': {error_code}' in line for error_code in ignore_errors):
                lines.append(line)
        log_contents = '\n'.join(lines)
        flake8_log_path.write_text(log_contents)
        review_info = (f' even when ignoring {ignore_errors}.\nReview: {flake8_log_path}'
                       f'\nNote: the full list linting errors are reported in {flake8_full_path}')
    else:
        if_found_unlink(flake8_full_path)

    # Raise an exception if any errors were found. Remove the files if not
    if len(log_contents) > 0:
        raise RuntimeError(f'Found Linting Errors{review_info}')
    if_found_unlink(flake8_log_path)


def lint(path_list, flake8_path=DIG.flake8_path, ignore_errors=None):
    """Lint specified files creating summary log file of errors.

    Args:
        path_list: list of file paths to lint
        flake8_path: path to flake8 configuration file. Default is `DIG.flake8_path`
        ignore_errors: list of error codes to ignore (beyond the flake8 config settings). Default is None

    Returns:
        dict: DoIt task

    """
    flake8_log_path = DIG.source_path / 'flake8.log'
    flags = f'--config={flake8_path}  --output-file={flake8_log_path} --exit-zero'
    return debug_action([
        (if_found_unlink, (flake8_log_path, )),
        *[f'poetry run flake8 "{fn}" {flags}' for fn in path_list],
        (check_linting_errors, (flake8_log_path, ignore_errors)),
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
    actions = [f'poetry run isort "{fn}" --settings-path "{DIG.toml_path}"' for fn in path_list]
    kwargs = f'--in-place --aggressive --global-config {DIG.flake8_path}'
    actions.extend([f'poetry run autopep8 "{fn}" {kwargs}' for fn in path_list])
    return debug_action(actions)


def task_auto_format():
    """Configure `auto_format` as a task.

    Returns:
        dict: DoIt task

    """
    return auto_format(glob_path_list())
