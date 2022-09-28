"""Check that all imports work as expected.

Primarily checking that:

1. No optional dependencies are required

FIXME: Replace with programmatic imports? Maybe explicit imports to check backward compatibility of public API?
    https://stackoverflow.com/questions/34855071/importing-all-functions-from-a-package-from-import

"""

from pprint import pprint

from calcipy.dev.conftest import *  # noqa: F401, F403, H303
from calcipy.dev.noxfile import *  # noqa: F401, F403, H303
from calcipy.doit_tasks import *  # noqa: F401, F403, H303
from calcipy.dot_dict import *  # noqa: F401, F403, H303
from calcipy.file_helpers import *  # noqa: F401, F403, H303
from calcipy.log_helpers import *  # noqa: F401, F403, H303

pprint(locals())  # noqa: T003
