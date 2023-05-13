"""Experiment with checking for duplicate test names."""

import ast
from pathlib import Path

from beartype import beartype
from beartype.typing import List, Union
from corallium.log import logger


@beartype
def _show_info(function: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
    """Print info about the function."""
    logger.info('> name', name=function.name)
    if function.args.args:
        logger.info('\t args', args=function.args.args)


@beartype
def run(test_path: Path) -> List[str]:  # noqa: C901,CAC001  # pylint: disable=too-complex
    """Check for duplicates in the test suite.

    Inspired by: https://stackoverflow.com/a/67840804/3219667

    """
    summary = set()
    duplicates = []

    for path_test in test_path.rglob('test_*.py'):  # pylint: disable=too-many-nested-blocks
        logger.info(path_test.as_posix())
        parsed_ast = ast.parse(path_test.read_text())

        for node in parsed_ast.body:
            if isinstance(node, ast.FunctionDef):
                if node.name in summary and node.name.startswith('test_'):
                    duplicates.append(node.name)
                summary.add(node.name)
                _show_info(node)
            elif isinstance(node, ast.ClassDef):
                logger.info('Class name', name=node.name)
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        _show_info(method)

        for node in ast.walk(parsed_ast):  # type: ignore[assignment]
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name not in summary
            ):
                logger.info('Found new function(s) through walking')
                _show_info(node)
                summary.add(node.name)

    if duplicates:
        logger.error('Found Duplicates', duplicates=duplicates)
    return duplicates


if __name__ == '__main__':  # pragma: no cover
    run(Path('tests'))
