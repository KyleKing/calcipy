"""Custom doit reporter.

Based on conversation here:
https://groups.google.com/g/python-doit/c/SgoiGt_XYDU/m/PQ8JmlKFAgAJ

"""

from enum import IntEnum
from typing import Any, List, OrderedDict

import attr
from attrs_strict import type_validator
from beartype import beartype
from doit.reporter import ConsoleReporter
from doit.task import Task
from sty import fg


class _TaskExitCode(IntEnum):  # noqa: H601
    """Enum for identifying the task exit code."""

    PASS = 0
    FAIL = 1
    NOT_RUN = 2
    SKIP_IGNORED = 3
    SKIP_UP_TO_DATE = 4


@attr.s(auto_attribs=True, kw_only=True)
class _TaskSummary:  # noqa: H601
    """Task Summary."""

    name: str = attr.ib(validator=type_validator())
    exit_code: _TaskExitCode = attr.ib(validator=type_validator())


@beartype
def _format_task_summary(task_summary: _TaskSummary) -> str:
    """Format the string task summary for printing."""
    lookup = {  # noqa: DAR101, DAR201
        _TaskExitCode.PASS: (fg.green, 'was successful'),
        _TaskExitCode.FAIL: (fg.red, 'failed'),
        _TaskExitCode.NOT_RUN: (fg.white, 'was not run'),
        _TaskExitCode.SKIP_IGNORED: (fg.yellow, 'was ignored'),
        _TaskExitCode.SKIP_UP_TO_DATE: (fg.yellow, 'was skipped'),
    }
    foreground, exit_summary = lookup.get(task_summary.exit_code, ('', 'is UNKNOWN'))
    return f'{foreground}{task_summary.name} {exit_summary}' + fg.rs


class SummaryReporter(ConsoleReporter):  # pragma: no cover # noqa: H601
    """Summarize results of doit tasks."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize data members."""  # noqa: DAR101
        super().__init__(*args, **kwargs)
        self._all_tasks = []
        self._task_summaries = {}

    def initialize(self, tasks: OrderedDict[str, Task], selected_tasks: List[str]) -> None:
        """Initialize the data members for tracking task run status."""  # noqa: DAR101
        super().initialize(tasks, selected_tasks)
        self._all_tasks = selected_tasks

    def _add_summary(self, task: Task, exit_code: _TaskExitCode) -> None:
        """Store summary for later reference."""  # noqa: DAR101
        task_summary = _TaskSummary(name=task.name, exit_code=exit_code)
        self._task_summaries[task_summary.name] = task_summary

    def add_failure(self, task: Task, exception: Any) -> None:
        """Catch tasks that failed."""  # noqa: DAR101
        super().add_failure(task, exception)
        self._add_summary(task, _TaskExitCode.FAIL)

    def add_success(self, task: Task) -> None:
        """Catch tasks that succeeded."""  # noqa: DAR101
        super().add_success(task)
        self._add_summary(task, _TaskExitCode.PASS)

    def skip_uptodate(self, task: Task) -> None:
        """Catch tasks skipped."""  # noqa: DAR101
        super().skip_uptodate(task)
        self._add_summary(task, _TaskExitCode.SKIP_IGNORED)

    def skip_ignore(self, task: Task) -> None:
        """Catch tasks skipped."""  # noqa: DAR101
        super().skip_ignore(task)
        self._add_summary(task, _TaskExitCode.SKIP_UP_TO_DATE)

    def complete_run(self) -> None:
        """Output a concise summary."""
        super().complete_run()

        # Inspired by "nox"
        prefix = 'doit> '
        self.write(f'\n{prefix}Summary:\n')
        not_run_kwargs = {'exit_code': _TaskExitCode.NOT_RUN}
        for task_name in self._all_tasks:
            task_summary = self._task_summaries.get(task_name, _TaskSummary(name=task_name, **not_run_kwargs))
            self.write(prefix + _format_task_summary(task_summary) + '\n')
