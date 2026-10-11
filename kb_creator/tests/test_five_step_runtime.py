from __future__ import annotations

from pathlib import Path


REPO = Path(__file__).resolve().parents[2]


def test_cpu_first_wrapper_uses_explicit_source_root_profile_common() -> None:
    wrapper = (REPO / "kb_creator" / "scripts" / "run_mineru_three_view.ps1").read_text(encoding="utf-8")
    assert "[string]$SourceRoot" in wrapper
    assert '$profileCommon = Join-Path $sourceRootPath "scripts\\profile-common.ps1"' in wrapper
    assert ". $profileCommon" in wrapper
    assert "CPU-first SourceRoot did not produce the verified MinerU profile root." in wrapper
    assert '. (Join-Path $PSScriptRoot "..\\..\\MinerU\\scripts\\profile-common.ps1")' not in wrapper


def test_cpu_first_runtime_root_is_contained_below_output_stage_parent() -> None:
    wrapper = (REPO / "kb_creator" / "scripts" / "run_mineru_three_view.ps1").read_text(encoding="utf-8")
    assert "[string]$RuntimeRoot" in wrapper
    assert 'Assert-MinerUPathContained -Base (Split-Path -Parent $output) -Candidate $runtime' in wrapper
    assert "foreach ($runtimePath in $runtimePaths)" in wrapper
    assert 'Assert-MinerUPathContained -Base $runtime -Candidate $runtimePath' in wrapper


def test_reconstruction_cpu_command_passes_bound_source_and_run_local_runtime() -> None:
    source = (REPO / "kb_creator" / "pipeline" / "reconstruction.py").read_text(encoding="utf-8")
    expected = '''"-ToolRoot",
                local["mineru_root"],
                "-SourceRoot",
                local["mineru_source_root"],
                "-RuntimeRoot",
                str(view_dir / "runtime"),'''
    assert expected in source
