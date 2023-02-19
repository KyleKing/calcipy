try:
    from ._check_for_stale_packages import check_for_stale_packages
except ImportError as exc:
    raise RuntimeError("The 'calcipy[stale]' extras are missing") from exc
