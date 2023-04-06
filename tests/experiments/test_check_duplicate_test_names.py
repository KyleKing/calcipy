from pathlib import Path

from calcipy.experiments.check_duplicate_test_names import run


class ClassTest:
    """Test check_duplicate_test_names for searching by Class."""

    def method_test(self) -> None:
        """Test check_duplicate_test_names for searching by method."""


def intentional_duplicate():
    """Intentional duplicate, but should be ignored."""


def test_intentional_duplicate():
    """Intentional duplicate of a test function with the same name."""


def test_check_duplicate_test_names():
    duplicates = run(Path(__file__).parents[1])

    assert duplicates == ['test_intentional_duplicate']
