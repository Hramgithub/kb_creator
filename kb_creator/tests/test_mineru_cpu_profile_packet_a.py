import copy
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest
from jsonschema import ValidationError, validate


REPO = Path(__file__).parents[2]
MINERU = REPO / "MinerU"
SCRIPTS = MINERU / "scripts"


def _load_receipt_helper():
    spec = importlib.util.spec_from_file_location("mineru_profile_receipt", SCRIPTS / "profile_receipt.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _provider_receipt():
    identity = {"path_hint": "profiles/pipeline-cpu-v1/verify-receipt.json", "bytes": 12, "sha256": "a" * 64}
    return {
        "schema": "nri.mineru_provider_capabilities.v1",
        "checked_at_utc": "2026-09-14T00:00:00Z",
        "execution_boundary": "current_station_local_only",
        "providers": [
            {
                "provider_id": "pipeline_cpu",
                "required": True,
                "state": "ready",
                "reason_code": "verified_cpu_profile",
                "profile": "mineru-pipeline-cpu-windows-v1",
                "verification_receipt": identity,
            },
            {
                "provider_id": "hybrid_cuda",
                "required": False,
                "state": "unavailable",
                "reason_code": "nvidia_device_not_detected",
                "profile": "mineru-local-windows-cu128-v1",
                "verification_receipt": None,
            },
            {
                "provider_id": "vlm_cuda",
                "required": False,
                "state": "unavailable",
                "reason_code": "nvidia_device_not_detected",
                "profile": "mineru-local-windows-cu128-v1",
                "verification_receipt": None,
            },
        ],
        "receipt_sha256": "b" * 64,
    }


def _verification_receipt(helper, profile=None):
    profile = helper.CPU_PROFILE if profile is None else profile
    manifest = json.loads((MINERU / "models/manifest.json").read_text(encoding="utf-8"))
    prefix = "models/pipeline/" if profile == helper.CPU_PROFILE else "models/"
    model_rows = [
        {"path": row["path"], "bytes": row["size"], "sha256": row["sha256"]}
        for row in manifest["files"]
        if row["path"].startswith(prefix)
    ]
    versions = {
        helper.CPU_PROFILE: {
            "mineru": "3.4.4",
            "torch": "2.8.0+cpu",
            "torch_cuda": None,
            "torchvision": "0.23.0+cpu",
            "transformers": "4.57.6",
            "onnxruntime": "1.28.0",
        },
        helper.CUDA_PROFILE: {
            "mineru": "3.4.4",
            "torch": "2.8.0+cu128",
            "torch_cuda": "12.8",
            "torchvision": "0.23.0+cu128",
            "transformers": "4.57.6",
            "onnxruntime": "1.28.0",
        },
    }[profile]
    proof = {
        name: {"loaded": True, "component_type": f"Fake{name.title()}", "usable_method": method}
        for name, (_, method) in helper.COMPONENT_METHODS.items()
    }
    smokes = []
    for name in helper.PROFILE_SMOKES[profile]:
        method, cli_argument, scope = helper.SMOKE_METHODS[name]
        outputs = [
            {"path": f"{name}/sample{suffix}", "bytes": 1, "sha256": "d" * 64}
            for suffix in ("_content_list.json", "_content_list_v2.json", "_middle.json", ".md", "_layout.pdf")
        ]
        smokes.append(
            {
                "name": name,
                "state": "succeeded",
                "method": method,
                "cli_method_argument": cli_argument,
                "effective_method_scope": scope,
                "outputs": outputs,
            }
        )
    wheels = [
        {
            "distribution": name,
            "version": versions["torch"] if name == "torch" else versions["torchvision"] if name == "torchvision" else versions["onnxruntime"],
            "wheel_filename": f"{name}.whl",
            "direct_url": f"https://example.invalid/{name}.whl",
            "archive_hashes": {"sha256": "e" * 64},
            "wheel_tags": ["cp312-cp312-win_amd64"],
        }
        for name in helper.CRITICAL_WHEELS
    ]
    return helper.seal(
        {
            "schema": "nri.mineru_profile_verification.v1",
            "profile": profile,
            "state": "ready",
            "versions": versions,
            "model_manifest": {"required_rows": len(model_rows), "rows": model_rows},
            "assembled_vlm": (
                None
                if profile == helper.CPU_PROFILE
                else {"bytes": manifest["assembled_vlm"]["size"], "sha256": manifest["assembled_vlm"]["sha256"]}
            ),
            "config": {"bytes": 1, "sha256": "1" * 64},
            "lock": {"bytes": 1, "sha256": "2" * 64, "entries": 1},
            "model_load_proof": proof,
            "synthetic_smoke": smokes,
            "install_receipt": {"bytes": 1, "sha256": "3" * 64, "receipt_sha256": "4" * 64},
            "critical_wheels": wheels,
        }
    )


def test_cpu_lock_is_exact_and_excludes_gpu_only_distributions():
    helper = _load_receipt_helper()
    lock = helper.parse_lock(MINERU / "requirements.windows-cpu-pipeline.lock.txt")
    assert lock["torch"] == "2.8.0+cpu"
    assert lock["torchvision"] == "0.23.0+cpu"
    assert lock["transformers"] == "4.57.6"
    assert lock["onnxruntime"] == "1.28.0"
    assert lock["pymupdf"] == "1.28.2"
    assert lock["pypdf"] == "6.16.0"
    assert lock["reportlab"] == "5.0.0"
    assert lock["six"] == "1.17.0"
    assert not (helper.CPU_FORBIDDEN & set(lock))


def _repair_report(pins):
    return {
        "version": "1",
        "pip_version": "25.2",
        "install": [
            {
                "metadata": {"name": name, "version": version},
                "download_info": {
                    "url": f"https://example.invalid/{name}-{version}-py3-none-any.whl",
                    "archive_info": {"hashes": {"sha256": "a" * 64}},
                },
            }
            for name, version in pins.items()
        ],
        "environment": {"implementation_name": "cpython"},
    }


def _repair_fixture(tmp_path):
    helper = _load_receipt_helper()
    source = tmp_path / "src"
    source.mkdir()
    (source / "mineru.py").write_text("VERSION = '3.4.4'\n", encoding="utf-8")
    old_pins = {"alpha": "1.0"}
    inventory = {"alpha": "1.0", "mineru": "3.4.4", "pip": "25.2"}
    old_report = tmp_path / "pip-install-report.json"
    old_report.write_text(json.dumps(_repair_report(old_pins), sort_keys=True), encoding="utf-8")
    old_lock = tmp_path / "old.lock"
    old_lock.write_text("alpha==1.0\n", encoding="utf-8")
    receipt = helper.seal(
        {
            "schema": "nri.mineru_profile_installation.v1",
            "profile": helper.CPU_PROFILE,
            "python": {
                "version": "3.12.14",
                "implementation": "CPython",
                "executable_bytes": 1,
                "executable_sha256": "b" * 64,
                "platform": "Windows-test",
                "machine": "AMD64",
                "compatible_tags": ["cp312-cp312-win_amd64"],
            },
            "lock": {**helper.file_identity(old_lock), "entries": 1},
            "pip_report": helper.file_identity(old_report),
            "source": {"version": "3.4.4", **helper.source_inventory(source)},
            "critical_wheels": [{"distribution": name} for name in helper.CRITICAL_WHEELS],
            "installed_distributions": inventory,
        }
    )
    receipt_path = tmp_path / "install-receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    new_lock = tmp_path / "new.lock"
    new_lock.write_text("alpha==1.0\nsix==1.17.0\n", encoding="utf-8")
    return helper, source, old_report, receipt_path, new_lock, inventory


def test_additive_repair_plan_happy_path_and_single_pin_delta(tmp_path):
    helper, source, old_report, receipt, lock, inventory = _repair_fixture(tmp_path)
    plan = helper.build_additive_repair_plan(
        profile=helper.CPU_PROFILE,
        current_lock_path=lock,
        source=source,
        old_report_path=old_report,
        receipt_path=receipt,
        verify_receipt_path=tmp_path / "verify-receipt.json",
        inventory=inventory,
    )
    helper.assert_receipt_seal(plan)
    assert plan["additions"] == {"six": "1.17.0"}
    merged = helper.merge_pip_reports(
        json.loads(old_report.read_text(encoding="utf-8")),
        _repair_report({"six": "1.17.0"}),
        plan["old_pins"],
        plan["additions"],
    )
    assert [row["metadata"]["name"] for row in merged["install"]] == ["alpha", "six"]


def test_additive_repair_finalize_reissues_exact_full_provenance_and_receipt(tmp_path, monkeypatch):
    helper, source, old_report, receipt, lock, inventory = _repair_fixture(tmp_path)
    plan = helper.build_additive_repair_plan(
        profile=helper.CPU_PROFILE,
        current_lock_path=lock,
        source=source,
        old_report_path=old_report,
        receipt_path=receipt,
        verify_receipt_path=tmp_path / "verify-receipt.json",
        inventory=inventory,
    )
    plan_path = tmp_path / "repair-plan.json"
    helper.write_json(plan_path, plan)
    delta_report = tmp_path / "pip-delta-report.json"
    helper.write_json(delta_report, _repair_report({"six": "1.17.0"}))
    repaired_inventory = {**inventory, "six": "1.17.0"}
    monkeypatch.setattr(helper, "installed_inventory", lambda: repaired_inventory)
    monkeypatch.setattr(
        helper,
        "wheel_metadata",
        lambda name, report: {
            "distribution": name,
            "version": "test",
            "wheel_filename": f"{name}.whl",
            "direct_url": "https://example.invalid/test.whl",
            "archive_hashes": {"sha256": "a" * 64},
            "wheel_tags": ["py3-none-any"],
        },
    )
    helper.finalize_repair(
        SimpleNamespace(
            profile=helper.CPU_PROFILE,
            lock=lock,
            source=source,
            pip_report=old_report,
            delta_report=delta_report,
            full_report_output=old_report,
            install_receipt=receipt,
            verify_receipt=tmp_path / "verify-receipt.json",
            plan=plan_path,
            output=receipt,
        )
    )
    merged = json.loads(old_report.read_text(encoding="utf-8"))
    assert [row["metadata"]["name"] for row in merged["install"]] == ["alpha", "six"]
    replacement = json.loads(receipt.read_text(encoding="utf-8"))
    helper.assert_receipt_seal(replacement)
    helper.validate_install_receipt(replacement, helper.CPU_PROFILE)
    assert replacement["lock"] == {**helper.file_identity(lock), "entries": 2}
    assert replacement["pip_report"] == helper.file_identity(old_report)
    assert replacement["installed_distributions"] == repaired_inventory


def test_additive_repair_finalize_validation_failure_preserves_old_artifacts(tmp_path, monkeypatch):
    helper, source, old_report, receipt, lock, inventory = _repair_fixture(tmp_path)
    plan = helper.build_additive_repair_plan(
        profile=helper.CPU_PROFILE,
        current_lock_path=lock,
        source=source,
        old_report_path=old_report,
        receipt_path=receipt,
        verify_receipt_path=tmp_path / "verify-receipt.json",
        inventory=inventory,
    )
    plan_path = tmp_path / "repair-plan.json"
    helper.write_json(plan_path, plan)
    delta_report = tmp_path / "pip-delta-report.json"
    helper.write_json(delta_report, _repair_report({}))
    before_report = old_report.read_bytes()
    before_receipt = receipt.read_bytes()
    monkeypatch.setattr(helper, "installed_inventory", lambda: {**inventory, "six": "1.17.0"})
    with pytest.raises(RuntimeError):
        helper.finalize_repair(
            SimpleNamespace(
                profile=helper.CPU_PROFILE,
                lock=lock,
                source=source,
                pip_report=old_report,
                delta_report=delta_report,
                full_report_output=old_report,
                install_receipt=receipt,
                verify_receipt=tmp_path / "verify-receipt.json",
                plan=plan_path,
                output=receipt,
            )
        )
    assert old_report.read_bytes() == before_report
    assert receipt.read_bytes() == before_receipt


@pytest.mark.parametrize("lock_text", ["six==1.17.0\n", "alpha==2.0\nsix==1.17.0\n"])
def test_additive_repair_rejects_removed_or_changed_pin(tmp_path, lock_text):
    helper, source, old_report, receipt, lock, inventory = _repair_fixture(tmp_path)
    lock.write_text(lock_text, encoding="utf-8")
    with pytest.raises(RuntimeError, match="not strictly additive"):
        helper.build_additive_repair_plan(
            profile=helper.CPU_PROFILE,
            current_lock_path=lock,
            source=source,
            old_report_path=old_report,
            receipt_path=receipt,
            verify_receipt_path=tmp_path / "verify-receipt.json",
            inventory=inventory,
        )


@pytest.mark.parametrize("attack", ["receipt", "inventory", "source", "verify", "malformed_report", "duplicate_report"])
def test_additive_repair_preflight_rejects_stale_or_tampered_state(tmp_path, attack):
    helper, source, old_report, receipt, lock, inventory = _repair_fixture(tmp_path)
    if attack == "receipt":
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        payload["profile"] = "tampered"
        receipt.write_text(json.dumps(payload), encoding="utf-8")
    elif attack == "inventory":
        inventory = {**inventory, "unexpected": "1"}
    elif attack == "source":
        (source / "mineru.py").write_text("tampered\n", encoding="utf-8")
    elif attack == "verify":
        (tmp_path / "verify-receipt.json").write_text("{}", encoding="utf-8")
    elif attack == "malformed_report":
        old_report.write_text("{}", encoding="utf-8")
    elif attack == "duplicate_report":
        report = _repair_report({"alpha": "1.0"})
        report["install"].append(copy.deepcopy(report["install"][0]))
        old_report.write_text(json.dumps(report), encoding="utf-8")
        sealed = json.loads(receipt.read_text(encoding="utf-8"))
        portable = {key: value for key, value in sealed.items() if key != "receipt_sha256"}
        portable["pip_report"] = helper.file_identity(old_report)
        receipt.write_text(json.dumps(helper.seal(portable)), encoding="utf-8")
    with pytest.raises(RuntimeError):
        helper.build_additive_repair_plan(
            profile=helper.CPU_PROFILE,
            current_lock_path=lock,
            source=source,
            old_report_path=old_report,
            receipt_path=receipt,
            verify_receipt_path=tmp_path / "verify-receipt.json",
            inventory=inventory,
        )


@pytest.mark.parametrize("delta", [{}, {"six": "1.17.0", "extra": "1"}, {"six": "1.17.0", "SIX": "1.17.0"}])
def test_additive_repair_rejects_missing_extra_or_duplicate_delta_report(tmp_path, delta):
    helper, _, old_report, _, _, _ = _repair_fixture(tmp_path)
    with pytest.raises(RuntimeError):
        helper.merge_pip_reports(
            json.loads(old_report.read_text(encoding="utf-8")),
            _repair_report(delta),
            {"alpha": "1.0"},
            {"six": "1.17.0"},
        )


def test_additive_repair_rejects_structurally_malformed_report():
    helper = _load_receipt_helper()
    with pytest.raises(RuntimeError, match="malformed"):
        helper.pip_report_rows({}, {"six": "1.17.0"}, "delta pip report")


def test_additive_repair_plan_failure_does_not_replace_existing_output(tmp_path, monkeypatch):
    helper, source, old_report, receipt, lock, inventory = _repair_fixture(tmp_path)
    lock.write_text("alpha==2.0\nsix==1.17.0\n", encoding="utf-8")
    monkeypatch.setattr(helper, "installed_inventory", lambda: inventory)
    output = tmp_path / "repair-plan.json"
    output.write_text("sentinel", encoding="utf-8")
    args = SimpleNamespace(
        profile=helper.CPU_PROFILE,
        lock=lock,
        source=source,
        pip_report=old_report,
        install_receipt=receipt,
        verify_receipt=tmp_path / "verify-receipt.json",
        output=output,
    )
    with pytest.raises(RuntimeError):
        helper.plan_repair(args)
    assert output.read_text(encoding="utf-8") == "sentinel"


def test_setup_requires_explicit_fail_closed_cpu_additive_repair():
    setup = (SCRIPTS / "setup.ps1").read_text(encoding="utf-8")
    assert "[switch]$RepairProfile" in setup
    for conflict in (
        "RecoverBootstrap",
        "RecreateBootstrap",
        "RecreateManagedPython",
        "RecreateProfiles",
        "BootstrapPythonPath",
    ):
        assert f'"{conflict}"' in setup
    assert '$PSBoundParameters.ContainsKey($_)' in setup
    assert "refusing bootstrap or profile creation" in setup
    assert "managed Python receipt is missing" in setup
    assert "the uv receipt is missing" in setup
    assert "forbidden after a verification receipt exists" in setup
    assert "plan-repair" in setup and "finalize-repair" in setup
    assert "Assert-MinerURequestedManagedPythonPath" in setup
    assert '& $Definition.Python -I (Join-Path $PSScriptRoot "profile_receipt.py") plan-repair' in setup
    assert setup.index("if ($RepairProfile) {") < setup.index("New-Item -ItemType Directory -Force -Path $roots.ToolRoot")
    assert setup.index('if ($RepairProfile) {', setup.index("function Install-MinerUProfile")) < setup.index(
        "if ($RecreateProfiles", setup.index("function Install-MinerUProfile")
    )
    assert 'if (-not $RepairProfile -and $hardware.gpu_state -eq "candidate")' in setup
    assert '"--no-deps"' not in setup  # PowerShell command uses the literal CLI token, not a quoted data surrogate.
    assert "--no-deps" in setup
    assert "--report $deltaReport @pins" in setup
    assert "Read-MinerUStrictJson -Path $planPath" in setup


def _repair_setup_control_fixture(tmp_path, *, cpu_profile=False, managed_receipt=False, uv_receipt=False):
    workspace = tmp_path / "NRI"
    scripts = workspace / "MinerU/scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(SCRIPTS / "setup.ps1", scripts / "setup.ps1")
    shutil.copy2(SCRIPTS / "profile-common.ps1", scripts / "profile-common.ps1")
    (scripts / "bootstrap-python.ps1").write_text(
        """[CmdletBinding()]
param([string]$ToolRoot, [string]$BootstrapPythonPath, [switch]$RecoverBootstrap,
  [switch]$RecreateBootstrap, [switch]$RecreateManagedPython)
[System.IO.File]::WriteAllText((Join-Path (Split-Path -Parent $PSScriptRoot) 'bootstrap-called'), 'called')
throw 'bootstrap child must not run during repair preflight'
""",
        encoding="utf-8",
    )
    tool_root = workspace / ".tools/MinerU"
    if cpu_profile:
        profile = tool_root / "profiles/pipeline-cpu-v1"
        (profile / ".venv/Scripts").mkdir(parents=True)
        (profile / ".venv/Scripts/python.exe").write_bytes(b"synthetic")
        (profile / "install-receipt.json").write_text("{}", encoding="utf-8")
    if managed_receipt:
        receipt = workspace / ".tools/python/cpython-3.12.14-windows-x86_64.receipt.json"
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text("{}", encoding="utf-8")
    if uv_receipt:
        receipt = workspace / ".tools/uv/bootstrap-uv-0.12.13/install-receipt.json"
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text("{}", encoding="utf-8")
    return workspace, scripts / "setup.ps1", tool_root


def _tree_snapshot(root):
    return [
        (path.relative_to(root).as_posix(), path.is_dir(), None if path.is_dir() else path.read_bytes())
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix())
    ]


def _run_repair_setup(setup, tool_root, extra):
    powershell = shutil.which("pwsh.exe")
    if powershell is None:
        pytest.skip("PowerShell 7 is unavailable")
    return subprocess.run(
        [powershell, "-NoProfile", "-File", str(setup), "-RepairProfile", "-ToolRoot", str(tool_root), *extra],
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    "extra",
    [
        ["-RecoverBootstrap"],
        ["-RecreateBootstrap"],
        ["-RecreateManagedPython"],
        ["-RecreateProfiles"],
        ["-BootstrapPythonPath", "synthetic-bootstrap-python.exe"],
    ],
)
def test_repair_setup_rejects_bootstrap_create_knobs_without_side_effects(tmp_path, extra):
    workspace, setup, tool_root = _repair_setup_control_fixture(tmp_path)
    before = _tree_snapshot(workspace)
    completed = _run_repair_setup(setup, tool_root, extra)
    assert completed.returncode != 0
    assert "mutually exclusive with bootstrap/create/recreate inputs" in completed.stderr
    assert _tree_snapshot(workspace) == before
    assert not (workspace / "MinerU/bootstrap-called").exists()


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("cpu", "existing receipted CPU profile"),
        ("managed", "managed Python receipt is missing"),
        ("uv", "the uv receipt is missing"),
    ],
)
def test_repair_setup_missing_receipts_fail_before_bootstrap_or_directory_creation(tmp_path, state, expected):
    workspace, setup, tool_root = _repair_setup_control_fixture(
        tmp_path,
        cpu_profile=state != "cpu",
        managed_receipt=state == "uv",
        uv_receipt=state == "managed",
    )
    before = _tree_snapshot(workspace)
    extra = ["-ManagedPythonPath", str(tool_root / "profiles/pipeline-cpu-v1/.venv/Scripts/python.exe")]
    completed = _run_repair_setup(setup, tool_root, extra)
    assert completed.returncode != 0
    assert expected in completed.stderr
    assert "mutually exclusive" not in completed.stderr
    assert _tree_snapshot(workspace) == before
    assert not (workspace / "MinerU/bootstrap-called").exists()


def test_managed_python_override_accepts_only_the_exact_receipted_path(tmp_path):
    powershell = shutil.which("pwsh.exe")
    if powershell is None:
        pytest.skip("PowerShell 7 is unavailable")
    receipted = tmp_path / "managed/python.exe"
    other = tmp_path / "other/python.exe"
    receipted.parent.mkdir(parents=True)
    other.parent.mkdir(parents=True)
    receipted.write_bytes(b"managed")
    other.write_bytes(b"other")
    common = "'" + str(SCRIPTS / "profile-common.ps1").replace("'", "''") + "'"
    receipted_ps = "'" + str(receipted).replace("'", "''") + "'"
    other_ps = "'" + str(other).replace("'", "''") + "'"
    command = f"""
. {common}
$accepted = Assert-MinerURequestedManagedPythonPath -ReceiptedPython {receipted_ps} -RequestedPythonPath {receipted_ps}
$rejected = $false
try {{ Assert-MinerURequestedManagedPythonPath -ReceiptedPython {receipted_ps} -RequestedPythonPath {other_ps} | Out-Null }}
catch {{ $rejected = $_.Exception.Message -eq '-ManagedPythonPath does not match the exact receipted repository-local CPython executable.' }}
[ordered]@{{ accepted = $accepted; rejected = $rejected }} | ConvertTo-Json -Compress
"""
    completed = subprocess.run(
        [powershell, "-NoProfile", "-Command", command],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert Path(result["accepted"]).resolve() == receipted.resolve()
    assert result["rejected"] is True


def test_setup_documentation_uses_provider_local_capability_semantics():
    setup_doc = (REPO / "SETUP.md").read_text(encoding="utf-8")
    section = setup_doc.split("### 7.1 MinerU CPU baseline and optional GPU capability", 1)[1].split("### 7.2", 1)[0]
    assert r"$repo\.tools\MinerU\capabilities\providers.json" in section
    assert "`pipeline_cpu` is required" in section and "must be `ready`" in section
    assert "`hybrid_cuda`" in section and "`vlm_cuda`" in section
    assert "locally `unavailable`" in section
    assert "never turns the whole run into a global" in section
    assert r"$repo\.tools\MinerU\capability.json" not in section
    assert "records the GPU enrichment capability as" not in section


def test_optional_cuda_lock_is_separate_and_does_not_carry_torchaudio():
    helper = _load_receipt_helper()
    cpu = helper.parse_lock(MINERU / "requirements.windows-cpu-pipeline.lock.txt")
    cuda = helper.parse_lock(MINERU / "requirements.windows-cu128-provider.lock.txt")
    assert cuda["torch"] == "2.8.0+cu128"
    assert cuda["torchvision"] == "0.23.0+cu128"
    assert cuda["lmdeploy"] == "0.11.1"
    assert cuda["triton-windows"] == "3.4.0.post21"
    assert cuda["torch-c-dlpack-ext"] == "0.1.5"
    assert "torchaudio" not in cuda
    assert cpu["torch"] != cuda["torch"]


def test_provider_capability_schema_requires_ordered_cpu_and_optional_providers():
    schema = json.loads((REPO / "kb_creator/contracts/mineru_provider_capabilities.v1.schema.json").read_text(encoding="utf-8"))
    receipt = _provider_receipt()
    validate(receipt, schema)

    reordered = copy.deepcopy(receipt)
    reordered["providers"][1], reordered["providers"][2] = reordered["providers"][2], reordered["providers"][1]
    with pytest.raises(ValidationError):
        validate(reordered, schema)

    skipped_cpu = copy.deepcopy(receipt)
    skipped_cpu["providers"][0].update(state="unavailable", reason_code="nvidia_device_not_detected", verification_receipt=None)
    with pytest.raises(ValidationError):
        validate(skipped_cpu, schema)


def test_provider_capability_schema_requires_ready_receipt_and_output_free_unavailable():
    schema = json.loads((REPO / "kb_creator/contracts/mineru_provider_capabilities.v1.schema.json").read_text(encoding="utf-8"))
    receipt = _provider_receipt()
    receipt["providers"][0]["verification_receipt"] = None
    with pytest.raises(ValidationError):
        validate(receipt, schema)
    receipt = _provider_receipt()
    receipt["providers"][1]["verification_receipt"] = receipt["providers"][0]["verification_receipt"]
    with pytest.raises(ValidationError):
        validate(receipt, schema)


@pytest.mark.parametrize(
    ("provider_index", "state", "reason"),
    [
        (0, "invalid", "verified_cpu_profile"),
        (1, "unavailable", "verified_cuda_profile"),
        (1, "invalid", "nvidia_device_not_detected"),
        (2, "unavailable", "cuda_profile_invalid"),
    ],
)
def test_provider_schema_rejects_state_reason_cross_product_attacks(provider_index, state, reason):
    schema = json.loads((REPO / "kb_creator/contracts/mineru_provider_capabilities.v1.schema.json").read_text(encoding="utf-8"))
    receipt = _provider_receipt()
    receipt["providers"][provider_index].update(state=state, reason_code=reason, verification_receipt=None)
    with pytest.raises(ValidationError):
        validate(receipt, schema)


def test_verification_receipt_validator_rejects_mutated_seal_and_ready_looking_minimal_receipt():
    helper = _load_receipt_helper()
    receipt = _verification_receipt(helper)
    helper.validate_verification_receipt(receipt, helper.CPU_PROFILE, MINERU / "models/manifest.json")

    mutated = copy.deepcopy(receipt)
    mutated["versions"]["torch"] = "2.8.0+cu128"
    with pytest.raises(RuntimeError, match="seal"):
        helper.validate_verification_receipt(mutated, helper.CPU_PROFILE, MINERU / "models/manifest.json")

    ready_looking = helper.seal(
        {"schema": "nri.mineru_profile_verification.v1", "profile": helper.CPU_PROFILE, "state": "ready"}
    )
    with pytest.raises(RuntimeError, match="keys differ"):
        helper.validate_verification_receipt(ready_looking, helper.CPU_PROFILE, MINERU / "models/manifest.json")


def test_verification_receipt_validator_rejects_resealed_missing_profile_evidence():
    helper = _load_receipt_helper()
    receipt = _verification_receipt(helper)
    portable = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    portable["model_manifest"]["rows"] = portable["model_manifest"]["rows"][:-1]
    attacked = helper.seal(portable)
    with pytest.raises(RuntimeError, match="incomplete model evidence"):
        helper.validate_verification_receipt(attacked, helper.CPU_PROFILE, MINERU / "models/manifest.json")


@pytest.mark.parametrize(
    "smokes",
    [
        ["pipeline_txt=a"],
        ["pipeline_txt=a", "pipeline_txt=b"],
        ["pipeline_txt=a", "pipeline_ocr=b", "vlm_local=c"],
        ["pipeline_ocr=b", "pipeline_txt=a"],
    ],
)
def test_write_verify_rejects_missing_duplicate_extra_or_reordered_smokes(smokes):
    helper = _load_receipt_helper()
    with pytest.raises(ValueError):
        helper.parse_smoke_arguments(helper.CPU_PROFILE, smokes)


def test_model_load_proof_rejects_present_but_null_or_unusable_components():
    helper = _load_receipt_helper()

    class NullComponents:
        pass

    null_model = NullComponents()
    for _, (attribute, _) in helper.COMPONENT_METHODS.items():
        setattr(null_model, attribute, None)
    with pytest.raises(RuntimeError, match="not loaded and usable"):
        helper.build_model_load_proof(null_model)

    class Usable:
        def predict(self):
            return None

        def ocr(self):
            return None

    valid_model = NullComponents()
    for _, (attribute, _) in helper.COMPONENT_METHODS.items():
        setattr(valid_model, attribute, Usable())
    proof = helper.build_model_load_proof(valid_model)
    assert all(row["loaded"] and row["component_type"].endswith("Usable") and row["usable_method"] for row in proof.values())


def test_probe_runs_strict_profile_receipt_validator_before_ready_identity():
    probe = (SCRIPTS / "probe-capability.ps1").read_text(encoding="utf-8")
    validator_call = probe.index("validate-verify")
    identity_call = probe.index("Get-MinerUFileIdentity -Path $Definition.VerifyReceipt")
    assert validator_call < identity_call
    for required in ("$Definition.Python", "--receipt", "--profile", "--manifest", "$LASTEXITCODE -ne 0"):
        assert required in probe


def test_manifest_bound_formula_yaml_is_byte_stable_and_exact():
    path = MINERU / "models/pipeline/models/MFR/pp_formulanet_plus_m/PP-FormulaNet_plus-M_inference.yml"
    payload = path.read_bytes()
    assert len(payload) == 2_244_564
    assert hashlib.sha256(payload).hexdigest() == "87b5f3d7f2b2fe553627d77b37f496608ca150ebd0ef62d362591edca47b5538"
    assert b"\r\n" not in payload
    attributes = (REPO / ".gitattributes").read_text(encoding="utf-8")
    assert "MinerU/models/pipeline/models/MFR/pp_formulanet_plus_m/PP-FormulaNet_plus-M_inference.yml -text" in attributes


def test_profile_receipts_capture_wheel_platform_and_component_load_evidence():
    helper = (SCRIPTS / "profile_receipt.py").read_text(encoding="utf-8")
    for required in (
        '"compatible_tags"',
        '"wheel_filename"',
        '"direct_url"',
        '"archive_hashes"',
        '"wheel_tags"',
        '"layout"',
        '"formula"',
        '"ocr"',
        '"table_classification"',
        '"table_orientation"',
        '"wired_table"',
        '"wireless_table"',
    ):
        assert required in helper
    assert '"vlm_local": (None, "omitted", "not_applicable")' in helper


def test_profile_scripts_are_repository_local_cpu_first_and_do_not_use_legacy_venv():
    common = (SCRIPTS / "profile-common.ps1").read_text(encoding="utf-8")
    setup = (SCRIPTS / "setup.ps1").read_text(encoding="utf-8")
    initialize = (SCRIPTS / "initialize.ps1").read_text(encoding="utf-8")
    verify = (SCRIPTS / "verify.ps1").read_text(encoding="utf-8")
    probe = (SCRIPTS / "probe-capability.ps1").read_text(encoding="utf-8")
    assert '"profiles\\$Profile"' in common
    assert '"runtime\\$Profile"' in common
    assert '".venv\\Scripts\\python.exe"' not in setup
    assert 'Install-MinerUProfile -Profile "pipeline-cpu-v1"' in setup
    assert setup.index('Install-MinerUProfile -Profile "pipeline-cpu-v1"') < setup.index("-HardwareOnly")
    assert "--report" in setup and "--no-deps" in setup and "-m pip check" in setup
    assert '"pipeline-cpu-v1"' in initialize and 'if ($Profile -eq "windows-cu128-v1")' in initialize
    assert '"--backend", "pipeline", "--method", "txt"' in verify
    assert '"--backend", "pipeline", "--method", "ocr"' in verify
    vlm_line = next(line for line in verify.splitlines() if "$vlmArgs =" in line)
    assert '"--backend", "vlm-engine"' in vlm_line and '"--method"' not in vlm_line
    assert "MINERU setup: SKIPPED" not in setup
    assert "MinerU verification: SKIPPED" not in verify
    assert '"providers.json"' in probe and '"capability.json"' not in probe


def test_profile_environment_strips_remote_and_user_cache_inputs():
    common = (SCRIPTS / "profile-common.ps1").read_text(encoding="utf-8")
    for name in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "MINERU_API_URL",
        "MINERU_SERVER_URL",
        "MINERU_MODEL_SOURCE",
        "PYTHONPATH",
        "HF_HOME",
        "HUGGINGFACE_HUB_CACHE",
        "HF_XET_CACHE",
        "MODELSCOPE_CACHE",
        "TEMP",
        "TMP",
    ):
        assert name in common
    assert 'HF_HUB_OFFLINE = "1"' in common
    assert 'TRANSFORMERS_OFFLINE = "1"' in common


def test_bootstrap_lock_is_exact_single_binary_uv_pin():
    helper = _load_receipt_helper()
    rows = helper.parse_lock(MINERU / "requirements.bootstrap.lock.txt")
    assert rows == {"uv": "0.12.13"}


def test_bootstrap_uses_external_python_only_for_receipted_repo_local_uv():
    bootstrap = (SCRIPTS / "bootstrap-python.ps1").read_text(encoding="utf-8")
    common = (SCRIPTS / "profile-common.ps1").read_text(encoding="utf-8")
    assert 'Invoke-MinerUNativeCaptured -FilePath $externalPython' in bootstrap
    assert 'Invoke-MinerUNativeCaptured -FilePath $bootstrap.UvPython' in bootstrap
    assert '"--no-deps", "--only-binary=:all:"' in bootstrap
    assert '"--report", $bootstrap.UvPipReport, "-r", $bootstrap.BootstrapLock' in bootstrap
    assert "-win_amd64\\.whl$" in bootstrap
    assert 'Invoke-MinerUNativeCaptured -FilePath $bootstrap.UvExe -ArgumentList @("python", "install", $bootstrap.PythonVersion)' in bootstrap
    assert '$env:UV_PYTHON_INSTALL_DIR = $bootstrap.PythonRoot' in bootstrap
    assert '$env:UV_CACHE_DIR = $bootstrap.UvCache' in bootstrap
    assert 'schema = "nri.mineru_uv_bootstrap.v1"' in common
    assert 'schema = "nri.mineru_python_bootstrap.v1"' in bootstrap
    assert bootstrap.count("Write-MinerUJsonAtomic") == 2
    assert 'UvVersion = "0.12.13"' in common
    assert 'PythonVersion = "3.12.14"' in common
    assert '"uv\\bootstrap-uv-0.12.13"' in common
    assert '"cpython-3.12.14-windows-x86_64.receipt.json"' in common
    assert "Get-Command uv" not in bootstrap
    assert "py -3.12" not in bootstrap


def test_setup_profiles_can_only_use_receipted_repo_local_managed_python():
    setup = (SCRIPTS / "setup.ps1").read_text(encoding="utf-8")
    common = (SCRIPTS / "profile-common.ps1").read_text(encoding="utf-8")
    assert "[string]$BootstrapPythonPath" in setup
    assert '"bootstrap-python.ps1"' in setup
    assert '$bootstrapArguments = @{ ToolRoot = $roots.ToolRoot }' in setup
    assert '$bootstrapArguments.BootstrapPythonPath = $BootstrapPythonPath' in setup
    assert '$bootstrapArguments.RecreateBootstrap = $true' in setup
    assert '$bootstrapArguments.RecreateManagedPython = $true' in setup
    assert "Get-MinerUManagedPython -Roots $roots -Bootstrap $bootstrap" in setup
    assert "$bootstrapOutput.Count -ne 1" in setup
    assert "$bootstrapOutput[0] -isnot [string]" in setup
    assert "Assert-MinerUPathContained -Base $bootstrap.PythonRoot -Candidate $managedPython" in setup
    assert "Managed Python output does not match the exact contained receipted runtime." in setup
    assert "Assert-MinerURequestedManagedPythonPath" in setup
    assert 'throw "-ManagedPythonPath does not match the exact receipted repository-local CPython executable."' in common
    assert "& $managedPython -m venv $definition.VenvRoot" in setup
    assert "& $BootstrapPythonPath -m venv" not in setup
    assert "Get-Command uv" not in setup
    assert "Get-Command py" not in setup


def test_setup_style_named_splat_binds_bootstrap_child_parameters(tmp_path):
    child = tmp_path / "bootstrap-child.ps1"
    child.write_text(
        """[CmdletBinding()]
param(
  [string]$BootstrapPythonPath,
  [string]$ToolRoot,
  [switch]$RecoverBootstrap,
  [switch]$RecreateBootstrap,
  [switch]$RecreateManagedPython
)
[ordered]@{
  bootstrap_python_path = $BootstrapPythonPath
  tool_root = $ToolRoot
  recover_bootstrap = [bool]$RecoverBootstrap
  recreate_bootstrap = [bool]$RecreateBootstrap
  recreate_managed_python = [bool]$RecreateManagedPython
} | ConvertTo-Json -Compress
""",
        encoding="utf-8",
    )
    child_path = json.dumps(str(child))
    command = (
        '$bootstrapArguments = @{ ToolRoot = "repo tools with spaces" }; '
        '$bootstrapArguments.BootstrapPythonPath = "external python with spaces.exe"; '
        '$bootstrapArguments.RecoverBootstrap = $true; '
        '$bootstrapArguments.RecreateBootstrap = $true; '
        '$bootstrapArguments.RecreateManagedPython = $true; '
        f"& {child_path} @bootstrapArguments"
    )
    powershell = shutil.which("pwsh.exe") or shutil.which("powershell.exe")
    assert powershell is not None
    completed = subprocess.run(
        [powershell, "-NoProfile", "-Command", command],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(completed.stdout) == {
        "bootstrap_python_path": "external python with spaces.exe",
        "tool_root": "repo tools with spaces",
        "recover_bootstrap": True,
        "recreate_bootstrap": True,
        "recreate_managed_python": True,
    }


def test_bootstrap_state_is_sealed_coupled_and_recreation_is_narrow():
    bootstrap = (SCRIPTS / "bootstrap-python.ps1").read_text(encoding="utf-8")
    common = (SCRIPTS / "profile-common.ps1").read_text(encoding="utf-8")
    for required in (
        "Repository-local uv bootstrap is partial or unreceipted.",
        "Bootstrap dependency lock changed after uv installation.",
        "Repository-local uv pip report is missing.",
        "Repository-local uv pip report identity mismatch.",
        "uv artifact provenance does not match the pip report row.",
        "Use -RecreateManagedPython",
        "Remove-ContainedTree -Base",
        'Directory -Filter "cpython-3.12.14-windows-x86_64*"',
    ):
        assert required in bootstrap
    for required in (
        "Managed Python executable identity mismatch.",
        "Managed Python uv receipt file identity mismatch.",
        "Managed Python uv receipt seal or version mismatch.",
        "Assert-MinerUUvExecutableReceiptSet",
        "uv executable receipt identity mismatch",
        "Assert-MinerUReceiptSeal -Value $receipt",
        "Assert-MinerUReceiptSeal -Value $uvReceipt",
        "Assert-MinerUExactObjectShape",
        "Assert-MinerUFileIdentityShape",
    ):
        assert required in common
    assert "Move-Item -LiteralPath $temporary -Destination $Path -Force" in common
    assert "Refusing to remove an entire bootstrap root." in bootstrap
    assert "Remove-Item -LiteralPath $roots.WorkspaceTools -Recurse" not in bootstrap


def test_native_capture_helper_contains_mock_stdout_as_data(tmp_path):
    mock = tmp_path / "noisy-native.cmd"
    mock.write_text("@echo off\r\necho contaminating stdout\r\necho second record\r\nexit /b 0\r\n", encoding="ascii")
    common_path = json.dumps(str(SCRIPTS / "profile-common.ps1"))
    mock_path = json.dumps(str(mock))
    command = (
        f". {common_path}; "
        f"$result = Invoke-MinerUNativeCaptured -FilePath {mock_path} -ArgumentList @(); "
        "[ordered]@{ object_count = @($result).Count; exit_code = $result.ExitCode; "
        "lines = @($result.Lines) } | ConvertTo-Json -Compress"
    )
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload == {
        "object_count": 1,
        "exit_code": 0,
        "lines": ["contaminating stdout", "second record"],
    }


def test_bootstrap_receipts_have_closed_nested_shapes_and_portable_docs():
    common = (SCRIPTS / "profile-common.ps1").read_text(encoding="utf-8")
    bootstrap = (SCRIPTS / "bootstrap-python.ps1").read_text(encoding="utf-8")
    readme = (MINERU / "README.md").read_text(encoding="utf-8")
    assert 'Keys @("implementation", "version", "architecture_bits", "executable")' in common
    assert 'Keys @("wheel_filename", "direct_url", "archive_hashes")' in common
    assert 'Keys @("sha256")' in common
    assert "Assert-MinerUUvReceiptShape -Value $receipt" in bootstrap
    assert 'Keys @("bytes", "sha256", "receipt_sha256")' in common
    assert 'Keys @("tool", "tool_version", "requested_python", "source", "execution_boundary")' in common
    assert "D:\\" not in readme


def test_uv_version_parser_accepts_only_pinned_short_or_official_build_output():
    accepted = [
        "uv 0.12.13",
        "uv 0.12.13 (0ebbd9274 2026-09-10 x86_64-pc-windows-msvc)",
    ]
    rejected = [
        "uv 0.12.12",
        "uv 0.12.130",
        "junk uv 0.12.13",
        "uv 0.12.13 trailing-junk",
        "uv 0.12.13 (0ebbd927 2026-09-10 x86_64-pc-windows-msvc)",
        "uv 0.12.13 (0ebbd9274 2026-02-30 x86_64-pc-windows-msvc)",
        "uv 0.12.13 (0ebbd9274 2026-09-10 x86_64-pc-windows-gnu)",
        "uv 0.12.13 (0ebbd9274 2026-09-10 x86_64-pc-windows-msvc) suffix",
    ]
    common_path = json.dumps(str(SCRIPTS / "profile-common.ps1"))
    accepted_json = "'" + json.dumps(accepted) + "'"
    rejected_json = "'" + json.dumps(rejected) + "'"
    command = (
        f". {common_path}; "
        f"$accepted = ConvertFrom-Json {accepted_json}; "
        f"$rejected = ConvertFrom-Json {rejected_json}; "
        "$results = [ordered]@{ "
        "accepted = @($accepted | ForEach-Object { Test-MinerUUvVersionOutput -Output $_ -ExpectedVersion '0.12.13' }); "
        "rejected = @($rejected | ForEach-Object { Test-MinerUUvVersionOutput -Output $_ -ExpectedVersion '0.12.13' }) }; "
        "$results | ConvertTo-Json -Compress"
    )
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["accepted"] == [True, True]
    assert result["rejected"] == [False] * len(rejected)
    bootstrap = (SCRIPTS / "bootstrap-python.ps1").read_text(encoding="utf-8")
    assert bootstrap.count("Test-MinerUUvVersionOutput") == 2


def _run_recovery_fixture(tmp_path, attack=None, python_version="3.13.7"):
    fixture = tmp_path / f"recovery {attack or 'valid'} {python_version}"
    tools = fixture / ".tools"
    uv_root = tools / "uv/bootstrap-uv-0.12.13"
    venv = uv_root / ".venv"
    scripts = venv / "Scripts"
    scripts.mkdir(parents=True)
    external = fixture / "bootstrap-python.exe"
    external.write_bytes(b"external-python-fixture")
    uv_python = scripts / "python.exe"
    uv_python.write_bytes(b"uv-venv-python-fixture")
    uv_exe = scripts / "uv.exe"
    uv_exe.write_bytes(b"uv-executable-fixture")
    uvw_exe = scripts / "uvw.exe"
    uvw_exe.write_bytes(b"uvw-executable-fixture")
    uvx_exe = scripts / "uvx.exe"
    uvx_exe.write_bytes(b"uvx-executable-fixture")
    python_major_minor = ".".join(python_version.split(".")[:2])
    for pip_name in ("pip.exe", "pip3.exe", f"pip{python_major_minor}.exe"):
        (scripts / pip_name).write_bytes(f"{pip_name}-fixture".encode("ascii"))
    dist_info = venv / "Lib/site-packages/uv-0.12.13.dist-info"
    dist_info.mkdir(parents=True)
    record_rows = []
    for executable in (uv_exe, uvw_exe, uvx_exe):
        digest = base64.urlsafe_b64encode(hashlib.sha256(executable.read_bytes()).digest()).decode("ascii").rstrip("=")
        record_relative = Path("../..") / "Scripts" / executable.name
        record_rows.append(f"{record_relative.as_posix()},sha256={digest},{executable.stat().st_size}\n")
    (dist_info / "RECORD").write_text("".join(record_rows), encoding="utf-8")
    lock = fixture / "requirements.bootstrap.lock.txt"
    lock.write_text("uv==0.12.13\n", encoding="utf-8")
    report = uv_root / "pip-install-report.json"
    report_payload = {
        "install": [
            {
                "metadata": {"name": "uv", "version": "0.12.13"},
                "download_info": {
                    "url": "https://files.pythonhosted.org/packages/uv-0.12.13-py3-none-win_amd64.whl",
                    "archive_info": {"hashes": {"sha256": "a" * 64}},
                },
            }
        ]
    }
    report.write_text(json.dumps(report_payload), encoding="utf-8")
    config = {
        "home": str(external.parent),
        "include-system-site-packages": "false",
        "version": python_version,
        "executable": str(external),
        "command": f"{external} -m venv {venv}",
    }
    uv_version = "uv 0.12.13 (0ebbd9274 2026-09-10 x86_64-pc-windows-msvc)"
    post_receipt_tamper = attack == "post_receipt_tampered_companion"
    if attack == "missing_report":
        report.unlink()
    elif attack == "tampered_report":
        report_payload["install"][0]["download_info"]["archive_info"]["hashes"]["sha256"] = "bad"
        report.write_text(json.dumps(report_payload), encoding="utf-8")
    elif attack == "uv_version":
        uv_version = "uv 0.12.12"
    elif attack == "pyvenv":
        config["version"] = "3.12.14"
    elif attack == "base_executable":
        external.unlink()
    elif attack == "path":
        config["command"] = f"{external} -m venv {fixture / 'other-venv'}"
    elif attack == "missing_companion":
        uvw_exe.unlink()
    elif attack == "extra_companion":
        (scripts / "uv-debug.exe").write_bytes(b"unexpected")
    elif attack == "tampered_companion":
        uvx_exe.write_bytes(b"tampered-after-record")
    elif attack == "mismatched_pip_launcher":
        (scripts / "pip3.9.exe").write_bytes(b"wrong-version-pip")
    elif attack == "wrong_record_depth":
        record_path = dist_info / "RECORD"
        record_path.write_text(record_path.read_text(encoding="utf-8").replace("../../Scripts/", "../../../Scripts/"), encoding="utf-8")
    (venv / "pyvenv.cfg").write_text(
        "".join(f"{key} = {value}\n" for key, value in config.items()),
        encoding="utf-8",
    )

    def ps(value):
        return "'" + str(value).replace("'", "''") + "'"

    common_path = ps(SCRIPTS / "profile-common.ps1")
    receipt = uv_root / "install-receipt.json"
    command = f"""
. {common_path}
$roots = [pscustomobject]@{{ WorkspaceTools = {ps(tools)} }}
$bootstrap = [pscustomobject]@{{
  UvVersion = '0.12.13'
  UvRoot = {ps(uv_root)}
  UvVenv = {ps(venv)}
  UvPython = {ps(uv_python)}
  UvExe = {ps(uv_exe)}
  UvwExe = {ps(uvw_exe)}
  UvxExe = {ps(uvx_exe)}
  UvReceipt = {ps(receipt)}
  UvPipReport = {ps(report)}
  BootstrapLock = {ps(lock)}
}}
$externalPath = {ps(external)}
$uvExePath = {ps(uv_exe)}
$uvPythonPath = {ps(uv_python)}
$uvVersionOutput = {json.dumps(uv_version)}
$postReceiptTamper = ${str(post_receipt_tamper).lower()}
$invoker = {{
  param($filePath, $argumentList)
  if ($filePath -eq $externalPath) {{
    return [pscustomobject]@{{ ExitCode = 0; Lines = @('{{"implementation":"CPython","version":"{python_version}","architecture_bits":64}}') }}
  }}
  if ($filePath -eq $uvExePath) {{
    return [pscustomobject]@{{ ExitCode = 0; Lines = @($uvVersionOutput) }}
  }}
  if ($filePath -eq $uvPythonPath -and $argumentList -contains 'list') {{
    return [pscustomobject]@{{ ExitCode = 0; Lines = @('[{{"name":"pip","version":"25.2"}},{{"name":"uv","version":"0.12.13"}}]') }}
  }}
  if ($filePath -eq $uvPythonPath -and $argumentList -contains 'check') {{
    return [pscustomobject]@{{ ExitCode = 0; Lines = @('No broken requirements found.') }}
  }}
  throw ("Unexpected mocked native invocation: " + $filePath + " :: " + ($argumentList -join '|'))
}}.GetNewClosure()
try {{
  $recovered = Recover-MinerUUvBootstrap -Roots $roots -Bootstrap $bootstrap -BootstrapPythonPath {ps(external)} -NativeInvoker $invoker
  if ($postReceiptTamper) {{
    [System.IO.File]::WriteAllText($bootstrap.UvwExe, 'tampered-after-receipt')
    try {{
      Assert-MinerUUvExecutableReceiptSet -Bootstrap $bootstrap -Value $recovered.uv_executables
      [ordered]@{{ ok = $false; receipt_exists = $true; revalidation_rejected = $false }} | ConvertTo-Json -Compress
    }}
    catch {{
      [ordered]@{{ ok = $true; receipt_exists = $true; revalidation_rejected = $true }} | ConvertTo-Json -Compress
    }}
    return
  }}
  [ordered]@{{ ok = $true; receipt_exists = Test-Path -LiteralPath $bootstrap.UvReceipt; version = $recovered.version; companions = @($recovered.uv_executables.name) }} | ConvertTo-Json -Compress
}}
catch {{
  [ordered]@{{ ok = $false; receipt_exists = Test-Path -LiteralPath $bootstrap.UvReceipt; error = $_.Exception.Message }} | ConvertTo-Json -Compress
}}
"""
    powershell = shutil.which("pwsh.exe") or shutil.which("powershell.exe")
    assert powershell is not None
    completed = subprocess.run(
        [powershell, "-NoProfile", "-Command", command],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_explicit_bootstrap_recovery_seals_valid_temp_tree(tmp_path):
    result = _run_recovery_fixture(tmp_path)
    assert result == {
        "ok": True,
        "receipt_exists": True,
        "version": "0.12.13",
        "companions": ["uv.exe", "uvw.exe", "uvx.exe"],
    }


@pytest.mark.parametrize("python_version", ["3.10.14", "3.11.9", "3.12.14", "3.13.7"])
def test_recovery_accepts_exact_versioned_pip_launcher_for_supported_bootstrap_python(tmp_path, python_version):
    result = _run_recovery_fixture(tmp_path, python_version=python_version)
    assert result["ok"] is True
    assert result["receipt_exists"] is True


@pytest.mark.parametrize(
    "attack",
    [
        "missing_report",
        "tampered_report",
        "uv_version",
        "pyvenv",
        "base_executable",
        "path",
        "missing_companion",
        "extra_companion",
        "tampered_companion",
        "mismatched_pip_launcher",
        "wrong_record_depth",
    ],
)
def test_explicit_bootstrap_recovery_rejects_tampering_without_receipt(tmp_path, attack):
    result = _run_recovery_fixture(tmp_path, attack)
    assert result["ok"] is False
    assert result["receipt_exists"] is False


def test_uv_companion_receipt_revalidation_rejects_post_receipt_tamper(tmp_path):
    result = _run_recovery_fixture(tmp_path, "post_receipt_tampered_companion")
    assert result == {"ok": True, "receipt_exists": True, "revalidation_rejected": True}


def test_recovery_switch_is_explicit_and_named_through_setup():
    bootstrap = (SCRIPTS / "bootstrap-python.ps1").read_text(encoding="utf-8")
    setup = (SCRIPTS / "setup.ps1").read_text(encoding="utf-8")
    assert "[switch]$RecoverBootstrap" in bootstrap
    assert "[switch]$RecoverBootstrap" in setup
    assert "$RecoverBootstrap -and $RecreateBootstrap" in bootstrap
    assert "-BootstrapPythonPath is required for explicit uv bootstrap recovery." in bootstrap
    assert "$bootstrapArguments.RecoverBootstrap = $true" in setup
    assert "if (-not $RecoverBootstrap)" in setup


def test_windows_powershell_51_fails_with_explicit_runtime_floor():
    powershell = shutil.which("powershell.exe")
    if powershell is None:
        pytest.skip("Windows PowerShell is unavailable")
    common = "'" + str(SCRIPTS / "profile-common.ps1").replace("'", "''") + "'"
    command = (
        f". {common}; "
        "try { Get-MinerUProfileRoots | Out-Null; 'unexpected-pass' } "
        "catch { $_.Exception.Message }"
    )
    completed = subprocess.run(
        [powershell, "-NoProfile", "-Command", command],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == (
        "MinerU local profile scripts require PowerShell 7.5 or newer with "
        "ConvertFrom-Json -DateKind String."
    )


def test_exact_shape_validator_preserves_zero_one_many_cardinality_and_uv_archive_shape():
    powershell = shutil.which("pwsh.exe")
    if powershell is None:
        pytest.skip("PowerShell 7 is unavailable")
    common = "'" + str(SCRIPTS / "profile-common.ps1").replace("'", "''") + "'"
    command = f"""
. {common}
function Test-Rejected($value) {{
  try {{ Assert-MinerUExactObjectShape -Value $value -Keys @('sha256') -Label 'fixture'; return $false }}
  catch {{ return $true }}
}}
$hash = 'a' * 64
$oneObject = [pscustomobject]@{{ sha256 = $hash }}
$oneDictionary = [ordered]@{{ sha256 = $hash }}
$zeroObject = [pscustomobject]@{{}}
$zeroDictionary = [ordered]@{{}}
$manyObject = [pscustomobject]@{{ sha256 = $hash; extra = 1 }}
$manyDictionary = [ordered]@{{ sha256 = $hash; extra = 1 }}
Assert-MinerUExactObjectShape -Value $oneObject -Keys @('sha256') -Label 'one object'
Assert-MinerUExactObjectShape -Value $oneDictionary -Keys @('sha256') -Label 'one dictionary'
$receipt = [pscustomobject]@{{
  schema = 'nri.mineru_uv_bootstrap.v1'
  version = '0.12.13'
  bootstrap_python = [pscustomobject]@{{ implementation = 'CPython'; version = '3.13.7'; architecture_bits = 64; executable = [pscustomobject]@{{ bytes = 1; sha256 = $hash }} }}
  lock = [pscustomobject]@{{ bytes = 1; sha256 = $hash }}
  pip_report = [pscustomobject]@{{ bytes = 1; sha256 = $hash }}
  uv_executables = @(
    [pscustomobject]@{{ name = 'uv.exe'; bytes = 1; sha256 = $hash }},
    [pscustomobject]@{{ name = 'uvw.exe'; bytes = 1; sha256 = $hash }},
    [pscustomobject]@{{ name = 'uvx.exe'; bytes = 1; sha256 = $hash }}
  )
  artifact_provenance = [pscustomobject]@{{ wheel_filename = 'uv-0.12.13-py3-none-win_amd64.whl'; direct_url = 'https://example.invalid/uv.whl'; archive_hashes = [pscustomobject]@{{ sha256 = $hash }} }}
  checked_at_utc = '2026-09-14T00:00:00Z'
  receipt_sha256 = $hash
}}
Add-MinerUReceiptSeal -Value $receipt | Out-Null
$receiptJson = $receipt | ConvertTo-Json -Depth 16
$receipt = ConvertFrom-MinerUStrictJson -Json $receiptJson
Assert-MinerUUvReceiptShape -Value $receipt
Assert-MinerUReceiptSeal -Value $receipt
$unsupportedRejected = $false
try {{
  Assert-MinerUJsonDateStringSupport -ConvertFromJsonCommand ([pscustomobject]@{{ Parameters = @{{}} }})
}}
catch {{
  $unsupportedRejected = $true
}}
[ordered]@{{
  one_object = $true
  one_dictionary = $true
  zero_object_rejected = Test-Rejected $zeroObject
  zero_dictionary_rejected = Test-Rejected $zeroDictionary
  many_object_rejected = Test-Rejected $manyObject
  many_dictionary_rejected = Test-Rejected $manyDictionary
  uv_receipt_one_key_archive_valid = $true
  checked_at_type = $receipt.checked_at_utc.GetType().FullName
  checked_at_value = $receipt.checked_at_utc
  seal_valid = $true
  unsupported_parser_rejected = $unsupportedRejected
}} | ConvertTo-Json -Compress
"""
    completed = subprocess.run(
        [powershell, "-NoProfile", "-Command", command],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(completed.stdout) == {
        "one_object": True,
        "one_dictionary": True,
        "zero_object_rejected": True,
        "zero_dictionary_rejected": True,
        "many_object_rejected": True,
        "many_dictionary_rejected": True,
        "uv_receipt_one_key_archive_valid": True,
        "checked_at_type": "System.String",
        "checked_at_value": "2026-09-14T00:00:00Z",
        "seal_valid": True,
        "unsupported_parser_rejected": True,
    }
    common_source = (SCRIPTS / "profile-common.ps1").read_text(encoding="utf-8")
    bootstrap_source = (SCRIPTS / "bootstrap-python.ps1").read_text(encoding="utf-8")
    assert "Read-MinerUStrictJson -Path $Bootstrap.UvReceipt" in common_source
    assert "Read-MinerUStrictJson -Path $Bootstrap.PythonReceipt" in common_source
    assert "Read-MinerUStrictJson -Path $bootstrap.UvReceipt" in bootstrap_source
