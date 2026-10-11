"""Standalone verifier must use PowerShell initialization success, not native state."""

from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.mark.parametrize("native_state", ["unset", "stale_failure"])
@pytest.mark.parametrize("valid_config", [True, False])
def test_verify_initialization_is_independent_of_native_exit_code(
    tmp_path, native_state, valid_config
):
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell is required")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    source = Path(__file__).parents[2] / "MinerU/scripts/verify.ps1"
    shutil.copy2(source, scripts / "verify.ps1")
    (tmp_path / "models").mkdir()
    (tmp_path / "models/manifest.json").write_text("{}", encoding="utf-8")
    (scripts / "profile_receipt.py").write_text("", encoding="utf-8")
    (tmp_path / "required-input").write_text("fixture", encoding="utf-8")
    if valid_config:
        (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    (scripts / "profile-common.ps1").write_text(
        '''
function Get-MinerUProfileRoots {
  param($ToolRoot)
  [pscustomobject]@{ ToolRoot = $ToolRoot; SourceRoot = $ToolRoot }
}
function Get-MinerUProfileDefinition {
  param($Profile, $Roots)
  $inputPath = Join-Path $Roots.ToolRoot 'required-input'
  [pscustomobject]@{
    Python = $inputPath; MinerU = $inputPath; Lock = $inputPath
    InstallReceipt = $inputPath; RuntimeRoot = $Roots.ToolRoot
  }
}
function Set-MinerUProfileEnvironment {
  param($RuntimeRoot)
  throw 'TEST_REACHED_RUNTIME_AFTER_VALID_INITIALIZATION'
}
''', encoding="utf-8"
    )
    (scripts / "initialize.ps1").write_text(
        "param($Profile, $ToolRoot)\nJoin-Path $ToolRoot 'config.json'\n",
        encoding="utf-8",
    )
    native_setup = (
        "Remove-Variable LASTEXITCODE -Scope Global -ErrorAction SilentlyContinue"
        if native_state == "unset" else "$global:LASTEXITCODE = 71"
    )
    wrapper = scripts / "invoke.ps1"
    wrapper.write_text(
        "param($ToolRoot)\n" + native_setup
        + "\n& (Join-Path $PSScriptRoot 'verify.ps1') -ToolRoot $ToolRoot\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [pwsh, "-NoProfile", "-File", str(wrapper), str(tmp_path)],
        capture_output=True, text=True, timeout=30,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0  # Deliberate stop before invoking heavy tools.
    expected = (
        "TEST_REACHED_RUNTIME_AFTER_VALID_INITIALIZATION"
        if valid_config else "MinerU profile initialization failed."
    )
    assert expected in output, output
    assert "cannot be retrieved because it has not been set" not in output
