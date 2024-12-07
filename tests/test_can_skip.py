import time

import pytest

from calcipy.can_skip import can_skip


@pytest.mark.parametrize(
    ('create_order', 'prerequisites', 'targets', 'expected'),
    [
        (['uv.lock', 'cache.json'], ['uv.lock'], ['cache.json'], True),
        (['cache.json', 'uv.lock'], ['uv.lock'], ['cache.json'], False),
        (['uv.lock', 'pyproject.toml', 'cache.json'], ['pyproject.toml', 'uv.lock'], ['cache.json'], True),
        (['uv.lock', 'cache.json', 'pyproject.toml'], ['pyproject.toml', 'uv.lock'], ['cache.json'], False),
        (['uv.lock', 'summary.txt', 'cache.json'], ['uv.lock'], ['cache.json', 'summary.txt'], True),
        (['summary.txt', 'uv.lock', 'cache.json'], ['uv.lock'], ['cache.json', 'summary.txt'], False),
    ],
)
def test_skip(fix_test_cache, create_order, prerequisites, targets, expected):
    for sub_pth in create_order:
        (fix_test_cache / sub_pth).write_text('')
        time.sleep(0.25)  # Reduces flakiness on Windows

    result = can_skip(
        prerequisites=[fix_test_cache / sub_pth for sub_pth in prerequisites],
        targets=[fix_test_cache / sub_pth for sub_pth in targets],
    )

    assert result is expected
