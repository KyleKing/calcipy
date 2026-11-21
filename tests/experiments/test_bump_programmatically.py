from unittest.mock import Mock

import pytest
from griffe import BuiltinModuleError  # type: ignore[import-untyped]

from calcipy.experiments import bump_programmatically


def _breakage(error=None):
    breakage = Mock()
    breakage._explain_oneline.side_effect = error  # noqa: SLF001
    return breakage


@pytest.mark.parametrize(
    ('tag', 'tag_prefix', 'breakages', 'expected'),
    [
        ('v1.2.3', 'v', [], 'v1.2.4'),
        ('1.2.3', '', [_breakage()], '1.3.0'),
        ('v1.2.3', 'v', [_breakage(BuiltinModuleError('builtin')), _breakage(ValueError('other'))], 'v1.3.0'),
        ('vnot-semver', 'v', [], ''),
    ],
    ids=['patch', 'minor', 'unexplainable-breakages', 'invalid-tag'],
)
def test_bump_programmatically(monkeypatch, tag, tag_prefix, breakages, expected):
    griffe = Mock()
    griffe.find_breaking_changes.return_value = iter(breakages)
    monkeypatch.setattr(bump_programmatically, 'griffe', griffe)

    result = bump_programmatically.bump_tag(pkg_name='pkg', tag=tag, tag_prefix=tag_prefix)

    assert result == expected
    griffe.load_git.assert_called_once_with('pkg', ref=tag)
    griffe.load.assert_called_once_with('pkg')
    griffe.find_breaking_changes.assert_called_once_with(griffe.load_git.return_value, griffe.load.return_value)
    for breakage in breakages:
        breakage._explain_oneline.assert_called_once_with()  # noqa: SLF001
