try:
    from ._dot_dict import ddict
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("The 'calcipy[ddict]' extras are missing") from exc

__all__ = ('ddict',)
