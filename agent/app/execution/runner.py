from __future__ import annotations

import asyncio
import subprocess
from dataclasses import dataclass
from typing import Any


@dataclass
class RunResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0


async def run_command(
    command: list[str],
    cwd: str | None = None,
    timeout: float = 300,
    env: dict[str, str] | None = None,
) -> RunResult:
    """
    Run an arbitrary shell command asynchronously and capture output.
    """
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
        env=env,
    )
    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return RunResult(returncode=-1, stdout="", stderr="Command timed out")

    return RunResult(
        returncode=proc.returncode or 0,
        stdout=stdout_bytes.decode("utf-8", errors="replace"),
        stderr=stderr_bytes.decode("utf-8", errors="replace"),
    )


async def run_shell(
    script: str,
    cwd: str | None = None,
    timeout: float = 300,
) -> RunResult:
    """Run a shell script string via /bin/bash."""
    return await run_command(
        ["/bin/bash", "-c", script],
        cwd=cwd,
        timeout=timeout,
    )
