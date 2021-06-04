"""Test log_helpers."""

from calcipy.log_helpers import build_logger_config, serializable_compact


def test_build_logger_config():
    """Test build_logger_config."""
    result = build_logger_config(production=True)

    assert isinstance(result['handlers'][1]['format'], type(serializable_compact))
