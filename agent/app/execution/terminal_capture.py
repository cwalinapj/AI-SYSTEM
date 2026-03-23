from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TerminalSession:
    """Captures the output of a shell session for later storage."""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    lines: list[str] = field(default_factory=list)

    def write(self, line: str) -> None:
        self.lines.append(line)

    def dump(self) -> str:
        return "\n".join(self.lines)

    def clear(self) -> None:
        self.lines.clear()


async def capture_command(
    command: list[str],
    cwd: str | None = None,
    timeout: float = 300,
) -> tuple[int, str]:
    """
    Run a command and return (returncode, full_output).
    Both stdout and stderr are merged in order.
    """
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=cwd,
    )
    session = TerminalSession()
    assert proc.stdout is not None

    async def _read() -> None:
        async for raw_line in proc.stdout:  # type: ignore[attr-defined]
            session.write(raw_line.decode("utf-8", errors="replace").rstrip())

    try:
        await asyncio.wait_for(
            asyncio.gather(proc.wait(), _read()),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        session.write("<<TIMEOUT>>")

    return proc.returncode or 0, session.dump()
