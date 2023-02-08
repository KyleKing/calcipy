try:
	from ._dot_dict import ddict
except ImportError as exc:
	# FIXME: Which dependency has bbox?
    raise RuntimeError("The '(TBD)' dependency is missing") from exc
