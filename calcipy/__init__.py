"""calcipy."""

from enum import Enum
from os import getenv

from beartype import BeartypeConf
from beartype.claw import beartype_this_package
from typing_extensions import Self  # noqa: UP035

__version__ = '1.6.2'
__pkg_name__ = 'calcipy'


class _RuntimeTypeCheckingModes(Enum):
    """Supported global runtime type checking modes."""

    ERROR = 'ERROR'
    WARNING = 'WARNING'
    OFF = None

    @classmethod
    def from_environment(cls) -> Self:
        """Return the configured mode."""
        rtc_mode = getenv('CALCIPY_RUNTIME_TYPE_CHECKING_MODE') or None
        try:
            return cls(rtc_mode)
        except ValueError:
            modes = [_e.value for _e in cls]
            msg = f"'CALCIPY_RUNTIME_TYPE_CHECKING_MODE={rtc_mode}' is not an allowed mode from {modes}"
            raise ValueError(msg) from None


def configure_runtime_type_checking_mode() -> None:
    """Optionally configure runtime type checking mode globally."""
    rtc_mode = _RuntimeTypeCheckingModes.from_environment()

    if rtc_mode is not _RuntimeTypeCheckingModes.OFF:
        from beartype.roar import BeartypeClawDecorWarning

        beartype_this_package(conf=BeartypeConf(
            warning_cls_on_decorator_exception=(
                None if rtc_mode is _RuntimeTypeCheckingModes.ERROR else BeartypeClawDecorWarning
            ),
        ))


configure_runtime_type_checking_mode()

# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======
