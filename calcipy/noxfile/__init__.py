try:
    from ._noxfile import build_check, build_dist, tests
except ImportError as exc:
    raise RuntimeError("The 'calcipy[nox]' extras are missing") from exc
