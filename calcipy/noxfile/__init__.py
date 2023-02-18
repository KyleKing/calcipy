try:
	from ._noxfile import build_check, build_dist, coverage, tests
except ImportError:
    raise RuntimeError("The 'calcipy[nox]' extras are missing") from None
