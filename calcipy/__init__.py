"""calcipy."""

from enum import Enum
from os import getenv

from beartype import BeartypeConf
from beartype.claw import beartype_this_package
from typing_extensions import Self  # noqa: UP035

__version__ = '1.6.0'
__pkg_name__ = 'calcipy'


class _BeartypeModes(Enum):
    """Supported global beartype modes."""

    ERROR = 'ERROR'
    WARNING = 'WARNING'
    OFF = None

    @classmethod
    def from_environment(cls) -> Self:
        """Return the configured mode."""
        beartype_mode = getenv('BEARTYPE_MODE') or None
        try:
            return cls(beartype_mode)
        except ValueError:
            msg = f"'BEARTYPE_MODE={beartype_mode}' is not an allowed mode from {[_e.value for _e in cls]}"
            raise ValueError(
                msg,
            ) from None


def configure_beartype() -> None:
    """Optionally configure beartype globally."""
    beartype_mode = _BeartypeModes.from_environment()

    if beartype_mode != _BeartypeModes.OFF:
        # PLANNED: Appease mypy and pyright, but this is a private import
        from beartype.roar._roarwarn import _BeartypeConfReduceDecoratorExceptionToWarningDefault
        beartype_warning_default = _BeartypeConfReduceDecoratorExceptionToWarningDefault

        beartype_this_package(conf=BeartypeConf(
            warning_cls_on_decorator_exception=(
                None if beartype_mode == _BeartypeModes.ERROR else beartype_warning_default
            ),
            is_color=getenv('BEARTYPE_NO_COLOR') is not None),
        )


configure_beartype()

# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======


# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======
