"""calcipy."""

from loguru import logger

__version__ = '0.21.4'
__pkg_name__ = 'calcipy'

logger.disable(__pkg_name__)

# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======

# Load entry point for CLI
from .cli.main import run  # noqa: E402

__all__ = ('run',)
