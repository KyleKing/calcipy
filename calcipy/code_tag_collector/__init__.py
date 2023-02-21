try:
    from ._collector import write_code_tag_file
except ImportError as exc:
    raise RuntimeError("The 'calcipy[tags]' extras are missing") from exc
