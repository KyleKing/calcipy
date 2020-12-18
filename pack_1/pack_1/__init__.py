from pathlib import Path
from loguru import logger

__pkg_name__ = Path(__file__).resolve().parent.name

logger.disable(__pkg_name__)

def main(label: str) -> None:
    """Print a logging event to test Loguru."""
    logger.info(f'I am package {__pkg_name__}')
    logger.debug(label)
