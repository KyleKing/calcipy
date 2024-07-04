try:
    from ._writer import write_template_formatted_md_sections
except ImportError as exc:
    raise RuntimeError("The 'calcipy[doc]' extras are missing") from exc

__all__ = ('write_template_formatted_md_sections',)
