try:
	from ._noxfile import pin_dev_dependencies, tests, coverage, build_dist, build_check  # noqa: F401
except ImportError as exc:
    raise RuntimeError("The 'test' dependencies are missing") from exc
