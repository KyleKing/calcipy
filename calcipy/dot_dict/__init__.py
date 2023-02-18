try:
	from ._dot_dict import ddict
except ImportError:
    raise RuntimeError("The 'calcipy[ddict]' extras are missing") from None
