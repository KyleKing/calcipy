try:
    from ._writer import write_template_formatted_sections
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("The 'calcipy[doc]' extras are missing") from exc

__all__ = ('write_template_formatted_sections',)
