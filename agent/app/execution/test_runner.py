from __future__ import annotations

import json
import tempfile
from typing import Any

from app.execution.runner import RunResult, run_command, run_shell


async def run_pytest(
    repo_path: str,
    test_path: str = ".",
    extra_args: list[str] | None = None,
    timeout: float = 300,
    report_path: str | None = None,
) -> RunResult:
    """Run pytest and return the result."""
    _report_path = report_path or f"{tempfile.gettempdir()}/test-report.json"
    cmd = ["python", "-m", "pytest", test_path, "-v", "--tb=short", "--json-report", f"--json-report-file={_report_path}"]
    if extra_args:
        cmd.extend(extra_args)
    return await run_command(cmd, cwd=repo_path, timeout=timeout)


async def parse_pytest_results(report_path: str | None = None) -> dict[str, Any]:
    """Parse a pytest JSON report."""
    import aiofiles
    _report_path = report_path or f"{tempfile.gettempdir()}/test-report.json"
    try:
        async with aiofiles.open(_report_path) as f:
            return json.loads(await f.read())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


async def run_custom_tests(
    repo_path: str,
    test_command: str,
    timeout: float = 300,
) -> RunResult:
    """Run an arbitrary test command."""
    return await run_shell(test_command, cwd=repo_path, timeout=timeout)
