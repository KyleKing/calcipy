"""Base CLI Controller."""

from cement import Controller, ex
from cement.utils.version import get_version_banner
from loguru import logger

from ... import __pkg_name__
from ..core.version import get_version

VERSION_BANNER = f"""
Calcipy CLI: {get_version()}
{get_version_banner()}
"""


class BaseController(Controller):
    """Base CLI Controller."""

    class Meta:
        label = 'base'

        description = 'Calcipy CLI'
        """Text displayed at the top of --help output."""

        epilog = 'Usage: calcipy echo'
        """Text displayed at the bottom of --help output."""

        arguments = [
            (['-v', '--version'], {'action': 'version', 'version': VERSION_BANNER}),
        ]
        """Controller level arguments. ex: 'calcipy --version'."""

    def _default(self) -> None:
        """Default action if no sub-command is passed."""
        self.app.args.print_help()

    @ex(
        help='Example echo subcommand',
        arguments=[
            (['-f', '--foo'], {'help': 'Placeholder foo option', 'action': 'store', 'dest': 'foo'}),
        ],
    )
    def echo(self) -> None:
        """Example sub-command."""
        data = {
            'foo': self.app.pargs.foo or self.app.config[__pkg_name__].get('foo', 'bar'),
        }
        logger.info(data)
