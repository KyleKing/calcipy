try:
    from ._noxfile import tests
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("The 'calcipy[nox]' extras are missing") from exc

__all__ = ('tests',)
