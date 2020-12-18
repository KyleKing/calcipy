# Testing Loguru in Packages

This is an orphaned branch (`git switch --orphan <branch_name>`) to test how Loguru behaves between packages

## Overview

This folders contains three packages that all have a short `__init__.py` file:

```py
from pathlib import Path
from loguru import logger

__pkg_name__ = Path(__file__).resolve().parent.name

logger.disable(__pkg_name__)

def main(label: str) -> None:
    """Print a logging event to test Loguru."""
    logger.info(f'I am package {__pkg_name__}')
    logger.debug(label)
```

Then in `pack_3`, both `pack_1` and `pack_2` are imported and run from [./pack_3/tests/test_loguru.py](./pack_3/tests/test_loguru.py)

## Quick Start

```sh
git clone https://github.com/KyleKing/calcipy.git
cd calcipy
git checkout examples/loguru-toggle
cd pack_3
poetry install

# Now run the test file on its own
poetry run python tests/test_loguru.py

# Or with pytest
poetry run pytest
```

Depending on how the file is configured, all of the output would look like this:

```sh
❯ poetry run python tests/test_loguru.py
2020-12-18 07:58:33.622 | INFO     | __main__:test_toggle:22 - Beep - Testing Start
2020-12-18 07:58:33.623 | INFO     | pack_1:main:10 - I am package pack_1
2020-12-18 07:58:33.623 | DEBUG    | pack_1:main:11 - label
2020-12-18 07:58:33.624 | INFO     | pack_2:main:10 - I am package pack_2
2020-12-18 07:58:33.624 | DEBUG    | pack_2:main:11 - label
2020-12-18 07:58:33.624 | INFO     | pack_3:main:10 - I am package pack_3
2020-12-18 07:58:33.625 | DEBUG    | pack_3:main:11 - label
2020-12-18 07:58:33.625 | INFO     | __main__:test_toggle:28 - Beep - Testing Complete
```

By only setting `logger.enable('pack_2')`, the output would be:

```sh
❯ poetry run python scripts/test_loguru.py
2020-12-18 07:58:33.622 | INFO     | __main__:test_toggle:22 - Beep - Testing Start
2020-12-18 07:58:33.624 | INFO     | pack_2:main:10 - I am package pack_2
2020-12-18 07:58:33.624 | DEBUG    | pack_2:main:11 - label
2020-12-18 07:58:33.625 | INFO     | __main__:test_toggle:28 - Beep - Testing Complete
```
