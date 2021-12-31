"""Calcipy Command Line."""

from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from loguru import logger

from .. import __pkg_name__
from .controllers.base_controller import BaseController
from .controllers.code_tag_collector_controller import CodeTagCollectorController
from .core.exceptions import CLIError

# Initialize nested dictionary for storing application defaults
_CONFIG = init_defaults(__pkg_name__)
# Access with: self.app.config[__pkg_name__].get('foo')
_CONFIG[__pkg_name__]['foo'] = 'bar-default'


class CLIApp(App):
    """My CLI Application."""

    class Meta:
        label = __pkg_name__

        config_defaults = _CONFIG
        """Configuration defaults."""

        exit_on_close = True
        """Call sys.exit() on close."""

        # PLANNED: Consider additional commands to add, such as `check_for_stale_packages` or to wrap copier
        #   More ideas here: https://github.com/KyleKing/calcipy/issues/69

        handlers = [BaseController, CodeTagCollectorController]
        """Register handlers."""


class CLIAppTest(TestApp, CLIApp):
    """A sub-class of CLIApp that is better suited for testing."""

    class Meta:
        label = __pkg_name__


def run() -> None:
    """Application Entry Point"""
    with CLIApp() as app:
        logger.enable(__pkg_name__)
        try:
            app.run()

        except AssertionError as exc:
            logger.error(f'AssertionError > {exc.args[0]}')
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CLIError as exc:
            logger.error(f'CLIError > {exc.args[0]}')
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            logger.exception('Unhandled Exception')
            app.exit_code = 0
