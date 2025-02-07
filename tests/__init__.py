import sys
from os import environ, getenv

DEF_MODE = 'ERROR' if sys.version_info >= (3, 10) else 'WARNING'
environ['RUNTIME_TYPE_CHECKING_MODE'] = getenv('RUNTIME_TYPE_CHECKING_MODE', DEF_MODE)

# Set for testing the `publish` task
environ['UV_PUBLISH_USERNAME'] = 'pypi_user'
environ['UV_PUBLISH_PASSWORD'] = 'pypi_password'  # noqa: S105
