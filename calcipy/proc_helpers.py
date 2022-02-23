"""Process Helpers."""

import subprocess  # noqa: S404  # nosec
from io import BufferedReader

from beartype import beartype
from beartype.typing import Callable, Optional


@beartype
def run_cmd(cmd: str, printer: Optional[Callable[[str], None]] = None, **kwargs) -> str:
    """Run command with subprocess and return the output.

    Inspired by: https://stackoverflow.com/a/38745040/3219667

    Args:
        cmd: string command
        printer: optional callable to output the lines in real time
        kwargs: any additional keyword arguments to pass to `subprocess.Popen` (typically `cwd`)

    Returns:
        str: stripped output

    Raises:
        CalledProcessError: if return code is non-zero

    """
    with subprocess.Popen(  # noqa: DUO116  # nosec
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
        shell=True, **kwargs,  # noqa: S602
    ) as proc:
        stdout: BufferedReader = proc.stdout  # type: ignore
        lines = []
        return_code = None
        while return_code is None:
            line = stdout.readline()
            if line:
                lines.append(line)
                if printer:
                    printer(line.rstrip())
            else:
                return_code = proc.poll()

    output = ''.join(lines)
    if return_code != 0:
        raise subprocess.CalledProcessError(returncode=return_code, cmd=cmd, output=output)
    return output
