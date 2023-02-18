try:
    from ._writer import write_autoformatted_md_sections
except ImportError as exc:
    raise RuntimeError("The 'calcipy[doc]' extras are missing") from exc
