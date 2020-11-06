"""DoIt Documentation Utilities."""

import json
import os
import re
import shutil
import subprocess  # noqa: S404
from pathlib import Path

from transitions import Machine

from .doit_base import DIG, debug_action, open_in_browser

# ----------------------------------------------------------------------------------------------------------------------
# Manage Tags


def task_create_tag():
    """Create a git tag based on the version in pyproject.toml.

    Returns:
        dict: DoIt task

    """
    message = 'New Revision from PyProject.toml'
    return debug_action([
        f'git tag -a {DIG.pkg_version} -m "{message}"',
        'git tag -n10 --list',
        'git push origin --tags',
    ])


def task_remove_tag():
    """Delete tag for current version in pyproject.toml.

    Returns:
        dict: DoIt task

    """
    return debug_action([
        f'git tag -d "{DIG.pkg_version}"',
        'git tag -n10 --list',
        f'git push origin :refs/tags/{DIG.pkg_version}',
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Update __init__.py with Documentation


def write_readme_to_init():
    """Write the README contents to the package `__init__.py` file."""
    readme = (DIG.source_path / 'README.md').read_text().replace('"', r'\"')  # Escape quotes
    init_text = (f'"""\n{readme}"""  # noqa\n\n# Generated with DoIt. Do not modify\n\n'
                 f"__version__ = '{DIG.pkg_version}'\n__pkg_name__ = '{DIG.pkg_name}'\n"
                 '\nfrom loguru import logger\n\nlogger.disable(__pkg_name__)\n')
    init_path = (DIG.source_path / DIG.pkg_name / '__init__.py')
    init_path.write_text(init_text.replace('\t', ' ' * 4))


# ----------------------------------------------------------------------------------------------------------------------
# Manage PDoc

PDOC_CONFIG = """<%!
    show_inherited_members = True
    hljs_stylename = 'atom-one-light'
    lunr_search = {'fuzziness': 1, 'index_docstrings': True}
%>"""
"""PDOC3 configuration."""

PDOC_HEAD = """<style>
    a {
        text-decoration: underline;
    }
    h1,h2,h3,h4 {
        font-weight: 400;
    }
    h2 {
        margin: 0.50em 0 .25em 0;
    }
    dd p {
        margin: 5px 0;
    }
    dl dl:last-child {
        margin-bottom: 2.5em;
    }
    main {
        margin-bottom: 80vh;
    }
    #content {
        max-width: 1100px;
    }
    .source summary {
        background-color: #fafafa; /* match HLJS background */
        padding: 1px 5px;
    }
    .source summary:focus {
        outline: none !important;
    }
    .source pre {
        background-color: #fafafa; /* match HLJS background */
    }
    .source pre code {
        padding-bottom: 1em;
    }
    table, th, td {
       border: 1px solid #d4d4d4;
       padding: 0 5px;
    }
</style>"""
"""PDOC3 custom CSS styles."""


def write_pdoc_config_files():
    """Write the head and config mako files for pdoc."""
    (DIG.template_dir / 'head.mako').write_text(PDOC_HEAD)
    (DIG.template_dir / 'config.mako').write_text(PDOC_CONFIG)

# ----------------------------------------------------------------------------------------------------------------------
# Manage Changelog


def task_update_cl():
    """Update a Changelog file with the raw Git history.

    Returns:
        dict: DoIt task

    """
    os.environ['GITCHANGELOG_CONFIG_FILENAME'] = DIG.path_gitchangelog.as_posix()
    return debug_action(['gitchangelog > CHANGELOG-raw.md'])


# ----------------------------------------------------------------------------------------------------------------------
# Manage README Updates


class ReadMeMachine:  # noqa: H601
    """State machine to replace commented sections of readme with new text."""

    states = ['readme', 'new']

    transitions = [
        {'trigger': 'start_new', 'source': 'readme', 'dest': 'new'},
        {'trigger': 'end', 'source': 'new', 'dest': 'readme'},
    ]

    readme_lines = None

    def __init__(self):
        """Initialize state machine."""
        self.machine = Machine(model=self, states=self.states, initial='readme', transitions=self.transitions)

    def parse(self, lines, comment_pattern, new_text):  # noqa: CCR001
        """Parse lines and insert new_text.

        Args:
            lines: list of text files
            comment_pattern: comment pattern to match (ex: ``)
            new_text: dictionary with comment string as key

        Returns:
            list: list of strings for README

        """
        self.readme_lines = []
        for line in lines:
            if comment_pattern.match(line):
                self.readme_lines.append(line)
                if line.strip().startswith('<!-- /'):
                    self.end()
                else:
                    key = comment_pattern.match(line).group(1)
                    self.readme_lines.extend(['', *new_text[key], ''])
                    self.start_new()
            elif self.state == 'readme':
                self.readme_lines.append(line)

        return self.readme_lines


def write_to_readme(comment_pattern, new_text):
    """Wrap ReadMeMachine. Handle reading then writing changes to the README.

    Args:
        comment_pattern: comment pattern to match (ex: ``)
        new_text: dictionary with comment string as key

    """
    readme_path = DIG.source_path / 'README.md'
    lines = readme_path.read_text().split('\n')
    readme_lines = ReadMeMachine().parse(lines, comment_pattern, new_text)
    readme_path.write_text('\n'.join(readme_lines))


def write_code_to_readme():
    """Replace commented sections in README with linked file contents."""
    comment_pattern = re.compile(r'\s*<!-- /?(CODE:.*) -->')
    fn = 'tests/examples/readme.py'
    script_path = DIG.source_path / fn
    if script_path.is_file():
        source_code = ['```py', *script_path.read_text().split('\n'), '```']
        new_text = {f'CODE:{fn}': [f'    {line}'.rstrip() for line in source_code]}
        write_to_readme(comment_pattern, new_text)


def write_coverage_to_readme():
    """Read the coverage.json file and write a Markdown table to the README file."""
    # Create the 'coverage.json' file from .coverage SQL database. Suppress errors if failed
    try:
        subprocess.run('poetry run python -m coverage json', shell=True, check=True)  # noqa: DUO116,S602,S607
    except subprocess.CalledProcessError:
        pass

    coverage_path = (DIG.source_path / 'coverage.json')
    if coverage_path.is_file():
        # Read coverage information from json file
        coverage = json.loads(coverage_path.read_text())
        # Collect raw data
        legend = ['File', 'Statements', 'Missing', 'Excluded', 'Coverage']
        int_keys = ['num_statements', 'missing_lines', 'excluded_lines']
        rows = [legend, ['--:'] * len(legend)]
        for file_path, file_obj in coverage['files'].items():
            rel_path = Path(file_path).resolve().relative_to(DIG.source_path).as_posix()
            per = round(file_obj['summary']['percent_covered'], 1)
            rows.append([f'`{rel_path}`'] + [file_obj['summary'][key] for key in int_keys] + [f'{per}%'])
        # Format table for Github Markdown
        table_lines = [f"| {' | '.join([str(value) for value in row])} |" for row in rows]
        table_lines.extend(['', f"Generated on: {coverage['meta']['timestamp']}"])
        # Replace coverage section in README
        comment_pattern = re.compile(r'<!-- /?(COVERAGE) -->')
        write_to_readme(comment_pattern, {'COVERAGE': table_lines})


def write_redirect_html():
    """Create an index.html file in the project directory that redirects to the pdoc output."""
    index_path = DIG.source_path / 'index.html'
    index_path.write_text(f"""<!-- Do not modify this file. It is automatically generated by dash_dev
If using github pages, make sure to check in this file to git and the files docs/{DIG.pkg_name}/*.html -->

<meta http-equiv="refresh" content="0; url=./docs/{DIG.pkg_name}/" />
""")


# ----------------------------------------------------------------------------------------------------------------------
# Main Documentation Tasks


def clear_docs():
    """Clear the documentation directory before running pdoc."""
    staging_dir = DIG.doc_dir / DIG.pkg_name
    if staging_dir.is_dir():
        shutil.rmtree(staging_dir)


def clear_examples():
    """Clear the examples from within the package directory."""
    if DIG.tmp_examples_dir.is_dir():
        shutil.rmtree(DIG.tmp_examples_dir)


def stage_examples():
    """Format the code examples as docstrings to be loaded into the documentation."""
    if DIG.src_examples_dir and DIG.src_examples_dir.is_dir():
        DIG.tmp_examples_dir.mkdir(exist_ok=False)
        (DIG.tmp_examples_dir / '__init__.py').write_text('"""Code Examples (documentation-only, not in package)."""')
        for file_path in DIG.src_examples_dir.glob('*.py'):
            content = file_path.read_text().replace('"', r'\"')  # read and escape quotes
            dest_fn = DIG.tmp_examples_dir / file_path.name
            docstring = f'From file: `{file_path.relative_to(DIG.source_path.parent)}`'
            dest_fn.write_text(f'"""{docstring}\n```\n{content}\n```\n"""')


def task_document():
    """Build the HTML documentation and push to gh-pages branch.

    Returns:
        dict: DoIt task

    """
    # Format the pdoc CLI args
    args = f'{DIG.pkg_name} --html --force --template-dir "{DIG.template_dir}" --output-dir "{DIG.doc_dir}"'
    return debug_action([
        (clear_docs, ()),
        (clear_examples, ()),
        (write_pdoc_config_files, ()),
        (stage_examples, ()),
        (write_code_to_readme, ()),
        (write_coverage_to_readme, ()),
        (write_readme_to_init, ()),
        f'poetry run pdoc3 {args}',
        (write_redirect_html, ()),
        (clear_examples, ()),
    ])


def task_open_docs():
    """Open the documentation files in the default browser.

    Returns:
        dict: DoIt task

    """
    return debug_action([
        (open_in_browser, (DIG.doc_dir / DIG.pkg_name / 'index.html',)),
    ])
