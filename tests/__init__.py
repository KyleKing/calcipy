from os import environ, getenv

environ['RUNTIME_TYPE_CHECKING_MODE'] = getenv('RUNTIME_TYPE_CHECKING_MODE', 'ERROR')
