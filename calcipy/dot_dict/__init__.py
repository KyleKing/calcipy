try:
    from ._dot_dict import ddict
except ImportError as exc:
    raise RuntimeError("The 'calcipy[ddict]' extras are missing") from exc
