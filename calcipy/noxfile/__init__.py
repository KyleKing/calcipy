try:  # noqa: RUF067
    from ._noxfile import tests
except ImportError as exc:
    raise RuntimeError("The 'calcipy[nox]' extras are missing") from exc

__all__ = ('tests',)
