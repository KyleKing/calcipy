import pytest

from calcipy.can_skip import can_skip


@pytest.mark.parametrize(
    ('create_order', 'prerequisites', 'targets', 'expected'),
    [
        (['poetry.lock', 'cache.json'], ['poetry.lock'], ['cache.json'], True),
        (['cache.json', 'poetry.lock'], ['poetry.lock'], ['cache.json'], False),
        (['poetry.lock', 'pyproject.toml', 'cache.json'], ['pyproject.toml', 'poetry.lock'], ['cache.json'], True),
        (['poetry.lock', 'cache.json', 'pyproject.toml'], ['pyproject.toml', 'poetry.lock'], ['cache.json'], False),
        (['poetry.lock', 'summary.txt', 'cache.json'], ['poetry.lock'], ['cache.json', 'summary.txt'], True),
        (['summary.txt', 'poetry.lock', 'cache.json'], ['poetry.lock'], ['cache.json', 'summary.txt'], False),
    ],
)
def test_skip(fix_test_cache, create_order, prerequisites, targets, expected):
    for sub_pth in create_order:
        (fix_test_cache / sub_pth).write_text('')

    result = can_skip(
        prerequisites=[fix_test_cache / sub_pth for sub_pth in prerequisites],
        targets=[fix_test_cache / sub_pth for sub_pth in targets],
    )

    assert result is expected
