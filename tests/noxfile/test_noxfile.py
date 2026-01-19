from calcipy.noxfile._noxfile import _has_ci_group


def test__has_ci_group_with_ci():
    """Test that _has_ci_group returns True when ci group exists."""
    pyproject_data = {
        'dependency-groups': {
            'ci': [
                'hypothesis[cli] >=6.112.4',
                'pytest-asyncio >=0.24.0',
                'types-setuptools >=75.1.0.20240917',
            ],
        },
    }

    assert _has_ci_group(pyproject_data)


def test__has_ci_group_without_ci():
    """Test that _has_ci_group returns False when ci group doesn't exist."""
    pyproject_data = {
        'dependency-groups': {
            'docs': ['mkdocs >=1.6.1'],
        },
    }

    assert not _has_ci_group(pyproject_data)


def test__has_ci_group_no_groups():
    """Test that _has_ci_group returns False when no dependency groups exist."""
    pyproject_data = {}

    assert not _has_ci_group(pyproject_data)
