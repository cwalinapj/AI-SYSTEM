from __future__ import annotations

import asyncio
import shlex
from dataclasses import dataclass

from app.execution.runner import RunResult, run_command


async def run_in_sandbox(
    command: list[str],
    image: str = "python:3.12-slim",
    cwd: str = "/workspace",
    timeout: float = 120,
) -> RunResult:
    """
    Execute a command inside a Docker container for sandboxed validation.
    Returns RunResult. Requires Docker to be available on the host.
    """
    docker_cmd = [
        "docker", "run", "--rm",
        "--network", "none",
        "-w", cwd,
        image,
    ] + command
    return await run_command(docker_cmd, timeout=timeout)


async def validate_script(
    script_content: bytes,
    language: str,
    image: str | None = None,
) -> RunResult:
    """Validate a script inside a Docker container and return the result."""
    _image = image or {
        "bash": "bash:latest",
        "python": "python:3.12-slim",
        "make": "alpine:latest",
    }.get(language, "ubuntu:22.04")

    ext = {"bash": "sh", "python": "py", "make": "mk"}.get(language, "sh")

    # Write script to temp file inside container using stdin
    interpreter = {"bash": "bash", "python": "python3", "make": "make -f"}.get(language, "bash")
    docker_cmd = [
        "docker", "run", "--rm",
        "--network", "none",
        "--memory", "256m",
        "--cpus", "0.5",
        "-i",
        _image,
        interpreter, "/dev/stdin",
    ]
    proc = await asyncio.create_subprocess_exec(
        *docker_cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(input=script_content), timeout=60
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return RunResult(returncode=-1, stdout="", stderr="Validation timed out")

    return RunResult(
        returncode=proc.returncode or 0,
        stdout=stdout_bytes.decode("utf-8", errors="replace"),
        stderr=stderr_bytes.decode("utf-8", errors="replace"),
    )
