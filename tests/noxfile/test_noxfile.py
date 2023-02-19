from beartype.typing import Dict

from calcipy import file_helpers
from calcipy.noxfile._noxfile import _installable_dev_dependencies


def test__installable_dev_dependencies(monkeypatch):
    def stubbed_read_pyproject() -> Dict:
        return {
            'tool': {
                'poetry': {
                    'dependencies': {
                        'python': '^3.8.12',
                    },
                    'dev': {
                        'dependencies': {
                            'types-requests': '>=2.28.11.13',
                        },
                    },
                    'group': {
                        'dev': {
                            'dependencies': {
                                'hypothesis': {
                                    'extras': ['cli'],
                                    'version': '>=6.58.0',
                                },
                                'types-setuptools': '^67.3.0.1',
                            },
                        },
                    },
                },
            },
        }

    monkeypatch.setattr(file_helpers, 'read_pyproject', stubbed_read_pyproject)

    result = _installable_dev_dependencies()

    assert result == [
        'types-requests>=2.28.11.13',  # Reads both group and non-group dev-dependencies
        'hypothesis[cli]>=6.58.0',
        'types-setuptools==67.3.0.1',  # FYI: converts ^ to ==
    ]
