import logging
from invoke import Program, Collection, Config
from shoal._log import configure_logger
from beartype import beartype
from beartype.typing import Optional, List
from . import __version__, __pkg_name__
from .tasks import all_tasks
from pathlib import Path
import sys
from pydantic import BaseModel

@beartype
def run() -> None:
    # FIXME: Move this logic to shoal

    # FYI: recommendation is to extend the `core_args` method, but this won't parse positional arguments
    #   https://docs.pyinvoke.org/en/stable/concepts/library.html#modifying-core-parser-arguments

    # FIXME: nest global options in a pydantic class, like 'gto: GlobalTaskOptions' and accessed with:
    #   ctx.gto.file_args or ctx.gto.verbosity

    class GlobalTaskOptions(BaseModel):

        file_args: List[Path]
        verbose: int

    # Manipulate 'sys.argv' to hide arguments that invoke can't parse
    file_argv: List[Path] = []
    verbose_argv: int = 0
    sys_argv: List[str] = []
    last_argv = ''
    for argv in sys.argv:
        if not last_argv.startswith('-') and Path(argv).is_file():
            file_argv.append(Path(argv))
        elif argv in {'-v', '-vv', '-vvv', '--verbose'}:
            verbose_argv = argv.count('v')
        else:
            sys_argv.append(argv)
        last_argv = argv
    sys.argv = sys_argv


    class ShoalConfig(Config):

        gto: GlobalTaskOptions = GlobalTaskOptions(file_args=file_argv, verbose=verbose_argv)


    class ShoalProgram(Program):

        def print_help(self) -> None:
            """Extend print_help with shoal-specific global configuration.

            https://github.com/pyinvoke/invoke/blob/0bcee75e4a26ad33b13831719c00340ca12af2f0/invoke/program.py#L657-L667

            """
            super().print_help()
            print('Global Task Options:')
            print('')
            self.print_columns([
                ('*file_args', 'List of Paths available globally to all tasks'),
                ('verbose', 'Globally configure logger verbosity (-vvv for most verbose)'),
            ])
            print('')

    ShoalProgram(name=__pkg_name__, version=__version__, namespace=Collection.from_module(all_tasks), config_class=ShoalConfig).run()