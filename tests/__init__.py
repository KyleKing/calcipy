import sys
from os import environ, getenv

DEF_MODE = 'ERROR' if sys.version_info >= (3, 10) else 'WARNING'  # noqa: RUF067
environ['RUNTIME_TYPE_CHECKING_MODE'] = getenv('RUNTIME_TYPE_CHECKING_MODE', DEF_MODE)  # noqa: RUF067
