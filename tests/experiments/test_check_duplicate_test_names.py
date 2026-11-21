import pytest

from calcipy.experiments.check_duplicate_test_names import run


class ClassTest:
    """Test check_duplicate_test_names for searching by Class."""

    def method_test(self) -> None:
        """Test check_duplicate_test_names for searching by method."""


def intentional_duplicate():
    """Intentional duplicate, but should be ignored."""


def test_intentional_duplicate():
    """Intentional duplicate of a test function with the same name."""


@pytest.mark.parametrize(
    ('files', 'expected'),
    [
        ({'test_a.py': 'def test_x(): ...\ndef test_x(): ...\n'}, [['test_x']]),
        ({'test_a.py': 'def test_x(): ...\n', 'sub/test_b.py': 'def test_x(): ...\n'}, [['test_x']]),
        ({f'test_{n}.py': 'def test_x(): ...\n' for n in 'abc'}, [['test_x', 'test_x']]),
        ({'test_a.py': 'def helper(): ...\n', 'test_b.py': 'def helper(): ...\n'}, [[]]),
        ({'test_a.py': 'def test_x(): ...\n', 'helper.py': 'def test_x(): ...\n'}, [[]]),
        (
            {
                'test_a.py': 'class TestA:\n    def test_a(self): ...\ndef test_b(): ...\n',
                'test_b.py': 'class TestB:\n    def test_b(self): ...\ndef test_a(): ...\n',
            },
            [['test_a'], ['test_b']],
        ),
        (
            {
                'test_a.py': 'def outer():\n    def test_a(): ...\ndef test_b(): ...\n',
                'test_b.py': 'def outer2():\n    def test_b(): ...\ndef test_a(): ...\n',
            },
            [['test_a'], ['test_b']],
        ),
    ],
    ids=['same-file', 'across-files', 'three-files', 'non-test-helpers', 'non-test-module', 'methods', 'nested'],
)
def test_run_reports_duplicate_test_names(tmp_path, files, expected):
    """With nested names, the file read first decides which top-level name repeats one already seen."""
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    assert run(tmp_path) in expected
