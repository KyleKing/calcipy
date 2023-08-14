"""Extend Invoke for Calcipy."""

import sys
from functools import wraps
from pathlib import Path
from types import ModuleType

from beartype import beartype
from beartype.typing import Any, Callable, Dict, List, Optional, Union
from invoke.collection import Collection as InvokeCollection  # noqa: TID251
from invoke.config import Config, merge_dicts
from invoke.program import Program

from .invoke_helpers import use_pty
from .tasks._invoke import TASK_ARGS_ATTR, TASK_KWARGS_ATTR, Collection, GlobalTaskOptions


class _CalcipyProgram(Program):
    """Customized version of Invoke's `Program`."""

    def print_help(self) -> None:  # pragma: no cover
        """Extend print_help with calcipy-specific global configuration.

        https://github.com/pyinvoke/invoke/blob/0bcee75e4a26ad33b13831719c00340ca12af2f0/invoke/program.py#L657-L667

        """
        super().print_help()
        print('Global Task Options:')  # noqa: T201
        print('')  # noqa: T201
        self.print_columns([
            ('*file_args', 'List of Paths available globally to all tasks. Will resolve paths with working_dir'),
            ('--keep-going', 'Continue running tasks even on failure'),
            ('--working_dir=STRING', 'Set the cwd for the program. Example: "../run --working-dir .. lint test"'),
            ('-v,-vv,-vvv', 'Globally configure logger verbosity (-vvv for most verbose)'),
        ])
        print('')  # noqa: T201


class CalcipyConfig(Config):
    """Opinionated Config with better defaults."""

    @staticmethod
    def global_defaults() -> Dict:  # type: ignore[type-arg]  # pragma: no cover
        """Override the global defaults."""
        invoke_defaults = Config.global_defaults()
        calcipy_defaults = {
            'run': {
                'echo': True,
                'echo_format': '\033[2;3;37mRunning: {command}\033[0m',
                'pty': use_pty(),
            },
        }
        return merge_dicts(invoke_defaults, calcipy_defaults)


@beartype
def start_program(  # noqa: CAC001
    pkg_name: str,
    pkg_version: str,
    module: Optional[ModuleType] = None,
    collection: Optional[Union[Collection, InvokeCollection]] = None,
) -> None:  # pragma: no cover
    """Run the customized Invoke Program.

    FYI: recommendation is to extend the `core_args` method, but this won't parse positional arguments:
    https://docs.pyinvoke.org/en/stable/concepts/library.html#modifying-core-parser-arguments

    """
    # Manipulate 'sys.argv' to hide arguments that invoke can't parse
    _gto = GlobalTaskOptions()
    sys_argv: List[str] = sys.argv[:1]
    last_argv = ''
    for argv in sys.argv[1:]:
        if not last_argv.startswith('-') and Path(argv).is_file():
            _gto.file_args.append(Path(argv))
        # Check for CLI flags
        elif argv in {'-v', '-vv', '-vvv', '--verbose'}:
            _gto.verbose = argv.count('v')
        elif argv == '--keep-going':
            _gto.keep_going = True
        # Check for CLI arguments with values
        elif last_argv in {'--working-dir'}:
            _gto.working_dir = Path(argv).resolve()
        elif argv not in {'--working-dir'}:
            sys_argv.append(argv)
        last_argv = argv
    _gto.file_args = [
        _f if _f.is_absolute() else Path.cwd() / _f
        for _f in _gto.file_args
    ]
    sys.argv = sys_argv

    class _CalcipyConfig(CalcipyConfig):

        gto: GlobalTaskOptions = _gto

    if module and collection:
        raise ValueError('Only one of collection or module can be specified')

    _CalcipyProgram(
        name=pkg_name,
        version=pkg_version,
        namespace=Collection.from_module(module) if module else collection,
        config_class=_CalcipyConfig,
    ).run()


def task(*dec_args: Any, **dec_kwargs: Any) -> Callable:  # type: ignore[type-arg] # noqa: CFQ004
    """Marks wrapped callable object as a valid Invoke task."""
    def wrapper(func: Any) -> Callable:  # type: ignore[type-arg] # noqa: CFQ004
        # Attach arguments for Task
        setattr(func, TASK_ARGS_ATTR, dec_args)
        setattr(func, TASK_KWARGS_ATTR, dec_kwargs)
        # Attach public attributes from invoke that are expected
        func.help = dec_kwargs.pop('help', {})

        def _with_kwargs(**extra_kwargs: Any) -> Callable:  # type: ignore[type-arg] # nosem
            """Support building partial tasks."""
            @wraps(func)  # nosem
            def _with_kwargs_inner(*args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs, **extra_kwargs)
            return _with_kwargs_inner

        func.with_kwargs = _with_kwargs

        @wraps(func)  # nosem
        def _inner(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return _inner

    # Handle the case when the decorator is called without arguments
    if (
        len(dec_args) == 1
        and callable(dec_args[0])
        and not hasattr(dec_args[0], TASK_ARGS_ATTR)
    ):
        return wrapper(dec_args[0])

    return wrapper
