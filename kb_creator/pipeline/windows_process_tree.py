from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path
from typing import Any


RESULT_SCHEMA = "kb_creator.windows_process_tree_result.v2"
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
INFINITE = 0xFFFFFFFF
CREATE_SUSPENDED = 0x00000004
CREATE_UNICODE_ENVIRONMENT = 0x00000400
EXTENDED_STARTUPINFO_PRESENT = 0x00080000
STARTF_USESTDHANDLES = 0x00000100
PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
ERROR_PROCESS_ABORTED = 1067


class RunnerError(RuntimeError):
    pass


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = (
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
        ("bInheritHandle", wintypes.BOOL),
    )


class STARTUPINFOW(ctypes.Structure):
    _fields_ = (
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(wintypes.BYTE)),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    )


class STARTUPINFOEXW(ctypes.Structure):
    _fields_ = (("StartupInfo", STARTUPINFOW), ("lpAttributeList", wintypes.LPVOID))


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = (
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    )


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = (
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    )


class IO_COUNTERS(ctypes.Structure):
    _fields_ = tuple((name, ctypes.c_ulonglong) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
    ))


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION_STRUCT(ctypes.Structure):
    _fields_ = (
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    )


class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION_STRUCT(ctypes.Structure):
    _fields_ = (
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    )


KERNEL32_ABI = {
    "CreateJobObjectW": ((wintypes.LPVOID, wintypes.LPCWSTR), wintypes.HANDLE),
    "SetInformationJobObject": ((wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD), wintypes.BOOL),
    "QueryInformationJobObject": ((wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)), wintypes.BOOL),
    "TerminateJobObject": ((wintypes.HANDLE, wintypes.UINT), wintypes.BOOL),
    "AssignProcessToJobObject": ((wintypes.HANDLE, wintypes.HANDLE), wintypes.BOOL),
    "CreateFileW": ((wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(SECURITY_ATTRIBUTES), wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE), wintypes.HANDLE),
    "InitializeProcThreadAttributeList": ((wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.c_size_t)), wintypes.BOOL),
    "UpdateProcThreadAttribute": ((wintypes.LPVOID, wintypes.DWORD, ctypes.c_size_t, wintypes.LPVOID, ctypes.c_size_t, wintypes.LPVOID, wintypes.LPVOID), wintypes.BOOL),
    "DeleteProcThreadAttributeList": ((wintypes.LPVOID,), None),
    "ResumeThread": ((wintypes.HANDLE,), wintypes.DWORD),
    "WaitForSingleObject": ((wintypes.HANDLE, wintypes.DWORD), wintypes.DWORD),
    "GetExitCodeProcess": ((wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)), wintypes.BOOL),
    "TerminateProcess": ((wintypes.HANDLE, wintypes.UINT), wintypes.BOOL),
    "CloseHandle": ((wintypes.HANDLE,), wintypes.BOOL),
    "CreateProcessW": ((wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.LPVOID, wintypes.LPVOID, wintypes.BOOL, wintypes.DWORD, wintypes.LPVOID, wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFOW), ctypes.POINTER(PROCESS_INFORMATION)), wintypes.BOOL),
}


def _win_error(label: str) -> RunnerError:
    return RunnerError(f"{label} failed with Windows error {ctypes.get_last_error()}")


def _contained(base: Path, candidate: Path, label: str) -> Path:
    base = base.resolve(strict=True)
    candidate = candidate.resolve(strict=False)
    try:
        candidate.relative_to(base)
    except ValueError as error:
        raise RunnerError(f"{label} must be contained by runtime root") from error
    return candidate


def _exact(value: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise RunnerError(f"{label} has unexpected or missing fields")
    return value


def _load_spec(path: Path, runtime_root: Path) -> dict[str, Any]:
    path = _contained(runtime_root, path, "spec path")
    value = _exact(
        json.loads(path.read_text(encoding="utf-8")),
        {
            "schema", "executable", "arguments", "working_directory", "environment",
            "stdout_path", "stderr_path", "active_timeout_seconds", "cleanup_timeout_seconds",
        },
        "process spec",
    )
    if value["schema"] != "kb_creator.windows_process_tree_spec.v1":
        raise RunnerError("unsupported process spec schema")
    executable = Path(value["executable"])
    working = Path(value["working_directory"])
    if not executable.is_absolute() or not executable.is_file():
        raise RunnerError("executable must be an existing absolute file")
    if not working.is_absolute() or not working.is_dir():
        raise RunnerError("working directory must be an existing absolute directory")
    arguments = value["arguments"]
    if not isinstance(arguments, list) or any(not isinstance(item, str) or "\0" in item for item in arguments):
        raise RunnerError("arguments must be an array of NUL-free strings")
    environment = value["environment"]
    if not isinstance(environment, dict) or not environment or any(
        not isinstance(key, str) or not key or "=" in key or "\0" in key
        or not isinstance(item, str) or "\0" in item
        for key, item in environment.items()
    ):
        raise RunnerError("environment must be a nonempty string map")
    if len({key.upper() for key in environment}) != len(environment):
        raise RunnerError("environment contains case-insensitive duplicate keys")
    resolved_logs: list[Path] = []
    for name in ("stdout_path", "stderr_path"):
        target = _contained(runtime_root, Path(value[name]), name)
        if not target.is_absolute() or not target.parent.is_dir():
            raise RunnerError(f"{name} parent must exist")
        value[name] = str(target)
        resolved_logs.append(target)
    if resolved_logs[0] == resolved_logs[1]:
        raise RunnerError("stdout_path and stderr_path must be distinct")
    for name, maximum in (("active_timeout_seconds", 86_400), ("cleanup_timeout_seconds", 300)):
        number = value[name]
        if isinstance(number, bool) or not isinstance(number, (int, float)) or number <= 0 or number > maximum:
            raise RunnerError(f"invalid {name}")
    value["executable"] = str(executable.resolve(strict=True))
    value["working_directory"] = str(working.resolve(strict=True))
    return value


def _environment_block(environment: dict[str, str]) -> ctypes.Array[ctypes.c_wchar]:
    ordered = sorted(environment.items(), key=lambda row: row[0].upper())
    return ctypes.create_unicode_buffer("\0".join(f"{key}={value}" for key, value in ordered) + "\0\0")


def _active_processes(kernel32: Any, job: wintypes.HANDLE) -> tuple[int, int]:
    accounting = JOBOBJECT_BASIC_ACCOUNTING_INFORMATION_STRUCT()
    if not kernel32.QueryInformationJobObject(
        job,
        JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
        ctypes.byref(accounting),
        ctypes.sizeof(accounting),
        None,
    ):
        raise _win_error("QueryInformationJobObject")
    return int(accounting.ActiveProcesses), int(accounting.TotalProcesses)


def _load_kernel32() -> Any:
    if os.name != "nt":
        raise RunnerError("Windows process-tree runner requires Windows")
    if ctypes.sizeof(wintypes.HANDLE) != ctypes.sizeof(ctypes.c_void_p) or ctypes.sizeof(wintypes.BOOL) != 4:
        raise RunnerError("unsupported Windows HANDLE/BOOL ABI")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    for name, (argtypes, restype) in KERNEL32_ABI.items():
        function = getattr(kernel32, name, None)
        if function is None:
            raise RunnerError(f"required Windows API is unavailable: {name}")
        function.argtypes = argtypes
        function.restype = restype
    return kernel32


def _run_windows(spec: dict[str, Any]) -> dict[str, Any]:
    kernel32 = _load_kernel32()
    handles: list[wintypes.HANDLE] = []
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        raise _win_error("CreateJobObjectW")
    handles.append(job)
    process_handle: wintypes.HANDLE | None = None
    thread_handle: wintypes.HANDLE | None = None
    assigned_to_job = False
    attribute_buffer: ctypes.Array[ctypes.c_char] | None = None
    attribute_initialized = False
    state = "helper_error"
    exit_code = 125
    timed_out = False
    cleanup_completed = False
    helper_error: str | None = None
    try:
        limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION_STRUCT()
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel32.SetInformationJobObject(
            job,
            JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            raise _win_error("SetInformationJobObject")

        security = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
        file_handles: list[wintypes.HANDLE] = []
        for path, access, disposition in (
            (spec["stdout_path"], GENERIC_WRITE, CREATE_ALWAYS),
            (spec["stderr_path"], GENERIC_WRITE, CREATE_ALWAYS),
            ("NUL", GENERIC_READ, OPEN_EXISTING),
        ):
            handle = kernel32.CreateFileW(
                path,
                access,
                FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                ctypes.byref(security),
                disposition,
                FILE_ATTRIBUTE_NORMAL,
                None,
            )
            if handle == INVALID_HANDLE_VALUE:
                raise _win_error(f"CreateFileW({path})")
            file_handles.append(handle)
            handles.append(handle)
        stdout_handle, stderr_handle, stdin_handle = file_handles

        attribute_size = ctypes.c_size_t()
        kernel32.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(attribute_size))
        attribute_buffer = ctypes.create_string_buffer(attribute_size.value)
        attribute_list = ctypes.cast(attribute_buffer, wintypes.LPVOID)
        if not kernel32.InitializeProcThreadAttributeList(attribute_list, 1, 0, ctypes.byref(attribute_size)):
            raise _win_error("InitializeProcThreadAttributeList")
        attribute_initialized = True
        inherited = (wintypes.HANDLE * 3)(stdin_handle, stdout_handle, stderr_handle)
        if not kernel32.UpdateProcThreadAttribute(
            attribute_list,
            0,
            PROC_THREAD_ATTRIBUTE_HANDLE_LIST,
            ctypes.cast(inherited, wintypes.LPVOID),
            ctypes.sizeof(inherited),
            None,
            None,
        ):
            raise _win_error("UpdateProcThreadAttribute")

        startup = STARTUPINFOEXW()
        startup.StartupInfo.cb = ctypes.sizeof(startup)
        startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES
        startup.StartupInfo.hStdInput = stdin_handle
        startup.StartupInfo.hStdOutput = stdout_handle
        startup.StartupInfo.hStdError = stderr_handle
        startup.lpAttributeList = attribute_list
        process_info = PROCESS_INFORMATION()
        command_line = ctypes.create_unicode_buffer(
            subprocess.list2cmdline([spec["executable"], *spec["arguments"]])
        )
        environment_block = _environment_block(spec["environment"])
        if not kernel32.CreateProcessW(
            spec["executable"],
            command_line,
            None,
            None,
            True,
            CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT | EXTENDED_STARTUPINFO_PRESENT,
            environment_block,
            spec["working_directory"],
            ctypes.byref(startup.StartupInfo),
            ctypes.byref(process_info),
        ):
            raise _win_error("CreateProcessW")
        process_handle = process_info.hProcess
        thread_handle = process_info.hThread
        if not kernel32.AssignProcessToJobObject(job, process_handle):
            raise _win_error("AssignProcessToJobObject")
        assigned_to_job = True
        if kernel32.ResumeThread(thread_handle) == 0xFFFFFFFF:
            raise _win_error("ResumeThread")
        kernel32.CloseHandle(thread_handle)
        thread_handle = None

        wait_ms = min(int(float(spec["active_timeout_seconds"]) * 1000), INFINITE - 1)
        wait_result = kernel32.WaitForSingleObject(process_handle, wait_ms)
        if wait_result == WAIT_TIMEOUT:
            timed_out = True
            state = "active_timeout"
            exit_code = 124
        elif wait_result == WAIT_OBJECT_0:
            code = wintypes.DWORD()
            if not kernel32.GetExitCodeProcess(process_handle, ctypes.byref(code)):
                raise _win_error("GetExitCodeProcess")
            exit_code = int(code.value)
            state = "completed"
        else:
            raise _win_error("WaitForSingleObject")

        active, _ = _active_processes(kernel32, job)
        if active and not kernel32.TerminateJobObject(job, ERROR_PROCESS_ABORTED):
            raise _win_error("TerminateJobObject")
        cleanup_deadline = time.monotonic() + float(spec["cleanup_timeout_seconds"])
        while True:
            active, _ = _active_processes(kernel32, job)
            if active == 0:
                cleanup_completed = True
                break
            if time.monotonic() >= cleanup_deadline:
                state = "cleanup_timeout"
                break
            time.sleep(0.025)
    except Exception as error:
        helper_error = str(error)
        if process_handle and not assigned_to_job:
            kernel32.TerminateProcess(process_handle, ERROR_PROCESS_ABORTED)
        if job:
            kernel32.TerminateJobObject(job, ERROR_PROCESS_ABORTED)
    finally:
        if attribute_initialized and attribute_buffer is not None:
            kernel32.DeleteProcThreadAttributeList(ctypes.cast(attribute_buffer, wintypes.LPVOID))
        for handle in (thread_handle, process_handle):
            if handle:
                kernel32.CloseHandle(handle)
        for handle in reversed(handles):
            if handle:
                kernel32.CloseHandle(handle)
    if state == "completed" and not cleanup_completed:
        state = "cleanup_timeout"
    return {
        "schema": RESULT_SCHEMA,
        "state": state,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "cleanup_completed": cleanup_completed,
        "helper_error": helper_error,
    }


def _write_result(path: Path, runtime_root: Path, value: dict[str, Any]) -> None:
    path = _contained(runtime_root, path, "result path")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--runtime-root", required=True, type=Path)
    args = parser.parse_args(argv)
    result: dict[str, Any]
    try:
        runtime_root = args.runtime_root.resolve(strict=True)
        result_path = _contained(runtime_root, args.result, "result path")
        spec = _load_spec(args.spec, runtime_root)
        result = _run_windows(spec)
    except Exception as error:
        result = {
            "schema": RESULT_SCHEMA,
            "state": "helper_error",
            "exit_code": 125,
            "timed_out": False,
            "cleanup_completed": False,
            "helper_error": str(error),
        }
        try:
            runtime_root = args.runtime_root.resolve(strict=True)
            result_path = _contained(runtime_root, args.result, "result path")
        except Exception:
            return 125
    _write_result(result_path, runtime_root, result)
    return 0 if result["state"] != "helper_error" else 125


if __name__ == "__main__":
    raise SystemExit(main())
