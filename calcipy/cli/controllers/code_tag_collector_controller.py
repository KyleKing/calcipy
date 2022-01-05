"""Code Tag Collector CLI Controller."""

import re
from pathlib import Path

from cement import Controller, ex
from loguru import logger

from ...code_tag_collector import CODE_TAG_RE, COMMON_CODE_TAGS, write_code_tag_file
from ...file_search import find_project_files


class CodeTagCollectorController(Controller):
    """Base CLI Controller."""

    class Meta:
        label = 'CodeTagCollector'

        arguments = []
        """Controller level arguments. ex: 'calcipy --version'."""

    def _default(self) -> None:
        """Default action if no sub-command is passed."""
        self.app.args.print_help()

    @ex(
        help='Code Tag Collector subcommand',
        arguments=[
            (
                ['-b', '--base-dir'],
                {
                    'help': 'Working Directory\n(Default: %(default)s)',
                    'action': 'store', 'dest': 'base_dir', 'default': '.',
                },
            ),
            (
                ['-f', '--filename'],
                {
                    'help': 'Code Tag Summary Filename\n(Default: %(default)s)',
                    'action': 'store', 'dest': 'filename', 'default': 'CODE_TAG_SUMMARY.md',
                },
            ),
            (
                ['-t', '--code-tags'],
                {
                    'help': 'Ordered list of code tags to locate (Comma-separated)\n(Default: %(default)s)',
                    'action': 'store', 'dest': 'tag_order', 'default': ','.join(COMMON_CODE_TAGS),
                },
            ),
            (
                ['-r', '--regex'],
                {
                    'help': 'Custom Code Tag Regex. Must contain "{tag}"\n(Default: `%(default)s`)',
                    'action': 'store', 'dest': 'regex', 'default': CODE_TAG_RE,
                },
            ),
            (
                ['-i', '--ignore-patterns'],
                {
                    'help': 'Glob patterns to ignore files and directories when searching (Comma-separated)',
                    'action': 'store', 'dest': 'ignore_patterns', 'default': '',
                },
            ),
        ],
    )
    def collect_code_tags(self) -> None:
        """Main subcommand to collect code tags."""
        pargs = self.app.pargs

        base_dir = Path(pargs.base_dir).resolve().absolute()
        path_tag_summary = base_dir / pargs.filename
        ignore_patterns = pargs.ignore_patterns.split(',') if pargs.ignore_patterns else []
        paths_source = find_project_files(base_dir, ignore_patterns=ignore_patterns)

        tag_order = pargs.tag_order.split(',')
        if not tag_order:
            raise ValueError('tag_order must contain at least one tag (i.e. `TODO`)')
        regex_compiled = re.compile(pargs.regex.format(tag='|'.join(tag_order)))

        write_code_tag_file(
            path_tag_summary=path_tag_summary,
            paths_source=paths_source,
            base_dir=base_dir,
            regex_compiled=regex_compiled,
            tag_order=tag_order,
            header='# Collected Code Tags',
        )
        logger.info(f'Created: {path_tag_summary}')
