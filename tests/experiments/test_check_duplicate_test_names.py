from pathlib import Path

from calcipy.experiments.check_duplicate_test_names import run


class ClassTest:

    def method_test(self) -> None:
        """Code located by `run`."""


def test_intentional_duplicate():
    """Intentional duplicate of a test function with the same name."""


def test_check_duplicate_test_names():
    duplicates = run(Path(__file__).parents[1])

    assert duplicates == ['test_intentional_duplicate']
