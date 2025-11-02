from calcipy.noxfile._noxfile import _installable_ci_dependencies


def test__installable_ci_dependencies():
    pyproject_data = {
        'dependency-groups': {
            'ci': [
                'hypothesis[cli] >=6.112.4',
                'pytest-asyncio >=0.24.0',
                'types-setuptools >=75.1.0.20240917',
            ],
        },
    }

    result = _installable_ci_dependencies(pyproject_data)

    assert result == [
        'hypothesis[cli] >=6.112.4',
        'pytest-asyncio >=0.24.0',
        'types-setuptools >=75.1.0.20240917',
    ]
