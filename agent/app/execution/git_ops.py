from __future__ import annotations

from pathlib import Path

from app.execution.runner import RunResult, run_command


async def git_status(repo_path: str) -> str:
    result = await run_command(["git", "status", "--short"], cwd=repo_path)
    return result.stdout


async def git_diff(repo_path: str, staged: bool = False) -> str:
    args = ["git", "diff"]
    if staged:
        args.append("--cached")
    result = await run_command(args, cwd=repo_path)
    return result.stdout


async def git_log(repo_path: str, n: int = 10) -> str:
    result = await run_command(
        ["git", "log", f"-{n}", "--oneline"], cwd=repo_path
    )
    return result.stdout


async def git_add_all(repo_path: str) -> RunResult:
    return await run_command(["git", "add", "-A"], cwd=repo_path)


async def git_commit(repo_path: str, message: str) -> RunResult:
    return await run_command(
        ["git", "commit", "-m", message],
        cwd=repo_path,
    )


async def git_clone(url: str, target: str) -> RunResult:
    return await run_command(["git", "clone", url, target])


async def apply_patch(repo_path: str, patch: str) -> RunResult:
    """Apply a unified diff patch via stdin."""
    import asyncio

    proc = await asyncio.create_subprocess_exec(
        "git", "apply", "--index", "-",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=repo_path,
    )
    stdout_bytes, stderr_bytes = await proc.communicate(input=patch.encode("utf-8"))
    return RunResult(
        returncode=proc.returncode or 0,
        stdout=stdout_bytes.decode("utf-8", errors="replace"),
        stderr=stderr_bytes.decode("utf-8", errors="replace"),
    )
