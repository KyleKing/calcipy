"""DoIt tasks for development functionality, such as code running."""

from pathlib import Path
from typing import Any, Optional, Sequence

import attr
from doit.tools import Interactive
from ruamel.yaml import YAML

from .doit_base import DIG, DoItTask, debug_task

# ======================================================================================================================
# Watch Code Tasks


_WATCHCODE_TEMPLATE: dict = {
    'filesets': {
        'default': {
            'include': ['.watchcode.yaml'],
            'exclude': ['.watchcode.log', '*.pyc', '__pycache__'],
            'exclude_gitignore': True,
            'match_mode': 'gitlike',
        },
    },
    'tasks': {
        'default': {
            'commands': [],
            'fileset': 'default',
            'queue_events': False,
            'clear_screen': True,
        },
    },
    'notifications': False,
    'sound': False,
    'log': False,
    'default_task': 'default',
}
"""Template dictionary with WatchCode defaults."""


@attr.s(auto_attribs=True, kw_only=True)
class _WatchCodeYAML:  # noqa: H601
    """Watchcode YAML file."""

    commands: Sequence[str]
    include: Sequence[str]
    exclude: Sequence[str] = ()
    dict_watchcode: dict = _WATCHCODE_TEMPLATE
    path_wc: Optional[Path] = None

    def __attrs_post_init__(self) -> None:
        """Complete initialization and merge settings."""
        self.merge_settings()

    def _merge_nested_setting(self, key: str, task_name: str, sub_key: str, values: Sequence[Any]) -> None:
        """Merge nested settings in the WatchCode YAML dictionary.

        Args:
            key: first, main keyname
            task_name: second, key for task name
            sub_key: third, sub-task keyname
            values: sequence of values to add to the WatchDog dictionary for specified keys

        """
        _values = self.dict_watchcode[key][task_name][sub_key]
        _values.extend(values)
        self.dict_watchcode[key][task_name][sub_key] = [*set(_values)]

    def merge_settings(self) -> None:
        """Merge all user-specified settings in the WatchCode YAML dictionary."""
        for file_key in ['include', 'exclude']:
            self._merge_nested_setting('filesets', 'default', file_key, getattr(self, file_key))
        self._merge_nested_setting('tasks', 'default', 'commands', self.commands)

    def write(self) -> None:
        """Write the WatchCode YAML file."""
        yaml = YAML()
        if self.path_wc is None:
            self.path_wc = DIG.source_path
        yaml.dump(self.dict_watchcode, self.path_wc / '.watchcode.yaml')


def _create_yaml(py_path: str) -> None:
    """Create the YAML file.

    Args:
        py_path: path to the Python file to run with poetry

    """
    wc_yaml = _WatchCodeYAML(
        commands=[f'poetry run python {py_path}'],
        include=[py_path],
    )
    wc_yaml.write()


def task_watchcode() -> DoItTask:
    """Return Interactive `watchcode` task for specified file.

    Example: `doit run watchcode -p scripts/main.py`

    Returns:
        DoItTask: DoIt task

    """
    action = debug_task([
        (_create_yaml, ),
        Interactive('poetry run watchcode'),
    ])
    action['params'] = [{
        'name': 'py_path', 'short': 'p', 'long': 'py_path', 'default': '',
        'help': ('Python file to re-run on changes\nSee: '
                 'https://github.com/bluenote10/watchcode'),
    }]
    return action
