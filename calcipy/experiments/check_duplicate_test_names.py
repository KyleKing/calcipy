"""Experiment with checking for duplicate test names."""

import ast
from pathlib import Path

from beartype import beartype
from beartype.typing import List


@beartype
def _show_info(function: [ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
    """Print info about the function."""
    print('> name:', function.name)
    if function.args.args:
        print(f"\t args: {', '.join([arg.arg for arg in function.args.args])}")


@beartype
def run(test_path: Path) -> List[str]:
    """Check for duplicates in the test suite.

    Inspired by: https://stackoverflow.com/a/67840804/3219667

    """
    summary = set()
    duplicates = []

    for path_test in test_path.rglob('test_*.py'):
        print(path_test.as_posix())
        parsed_ast = ast.parse(path_test.read_text())

        for node in parsed_ast.body:
            if isinstance(node, ast.FunctionDef):
                if node.name in summary:
                    duplicates.append(node.name)
                summary.add(node.name)
                _show_info(node)
            elif isinstance(node, ast.ClassDef):
                print('Class name:', node.name)
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        _show_info(method)

        for node in ast.walk(parsed_ast):
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name not in summary
            ):
                print('Found new function(s) through walking')
                _show_info(node)
                summary.add(node.name)

    if duplicates:
        print(f'Found Duplicates: {duplicates}')
    return duplicates


if __name__ == '__main__':
    run(Path('tests'))
