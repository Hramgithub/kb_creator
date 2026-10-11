from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Mapping, Sequence


MAX_CAPTURE_CHARS = 16_384
SAFE_ENV_KEYS = (
    "SystemRoot",
    "WINDIR",
    "ComSpec",
    "PATHEXT",
    "PATH",
    "PYTHONPATH",
    "TEMP",
    "TMP",
    "NO_PROXY",
    "no_proxy",
    "HF_HOME",
    "HUGGINGFACE_HUB_CACHE",
    "HF_XET_CACHE",
    "HF_HUB_DISABLE_SYMLINKS_WARNING",
    "MINERU_TOOLS_CONFIG_JSON",
    "MINERU_LMDEPLOY_BACKEND",
    "TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER",
)


class ProcessFailure(RuntimeError):
    def __init__(
        self,
        argv: Sequence[str],
        returncode: int,
        stdout: str,
        stderr: str,
        *,
        stdout_truncated: bool = False,
        stderr_truncated: bool = False,
        environment: Mapping[str, str] | None = None,
    ):
        super().__init__(f"command failed with exit code {returncode}: {argv[0]}")
        self.argv = tuple(argv)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.stdout_truncated = stdout_truncated
        self.stderr_truncated = stderr_truncated
        self.environment = dict(environment or {})


def _bounded(value: str) -> str:
    if len(value) <= MAX_CAPTURE_CHARS:
        return value
    return value[:MAX_CAPTURE_CHARS] + "\n...[truncated]"


def _sanitized(value: str) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "?", value)


def run(
    argv: Sequence[str],
    *,
    cwd: Path | None = None,
    env_updates: Mapping[str, str] | None = None,
    inherit_environment: bool = True,
) -> dict[str, object]:
    if not argv or any(not isinstance(item, str) or not item for item in argv):
        raise ValueError("argv must contain non-empty strings")
    environment = os.environ.copy() if inherit_environment else {}
    if env_updates:
        environment.update(env_updates)
    completed = subprocess.run(
        list(argv),
        cwd=str(cwd) if cwd else None,
        env=environment,
        shell=False,
        check=False,
        capture_output=True,
        text=True,
    )
    raw_stdout = _sanitized(completed.stdout)
    raw_stderr = _sanitized(completed.stderr)
    stdout = _bounded(raw_stdout)
    stderr = _bounded(raw_stderr)
    recorded_environment = {
        key: environment[key] for key in SAFE_ENV_KEYS if key in environment
    }
    if completed.returncode:
        raise ProcessFailure(
            argv,
            completed.returncode,
            stdout,
            stderr,
            stdout_truncated=len(raw_stdout) > MAX_CAPTURE_CHARS,
            stderr_truncated=len(raw_stderr) > MAX_CAPTURE_CHARS,
            environment=recorded_environment,
        )
    return {
        "argv": list(argv),
        "exit_code": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "environment": recorded_environment,
    }
