# Orchestrator receipt — MinerU CPU live verification

- Goal: `20260914-dissociation-publication`
- Timestamp: `2026-09-14T19:18:17+03:00`
- Station boundary: current local Windows station only
- Command: `MinerU/scripts/setup.ps1 -RepairProfile`
- Exit code: `0`
- Real scenario source executed: no
- GPU, remote host, external API or handoff used: no

## Result

The independently approved additive repair installed only `six==1.17.0` into
the existing receipted `mineru-pipeline-cpu-windows-v1` profile. `pip check`
reported no broken requirements. MinerU completed both one-page synthetic CPU
pipeline smokes (`txt` and `ocr`) and the profile verifier passed.

The provider capability receipt records:

- `pipeline_cpu`: `ready`, reason `verified_cpu_profile`;
- `hybrid_cuda`: `unavailable`, reason `nvidia_device_not_detected`;
- `vlm_cuda`: `unavailable`, reason `nvidia_device_not_detected`.

GPU unavailability is provider-local evidence and did not skip or fail the CPU
setup. The old globally skipped reconstruction run remains sealed and is not a
resume source.

## Exact evidence identities

- `.tools/MinerU/profiles/pipeline-cpu-v1/install-receipt.json`
  - bytes: `5843`
  - file SHA-256: `8625D56FC4BFC74D027C98416AEAFDF8222BFB14391C94478EB81D3841F6BEB3`
  - receipt seal: `8e15c0101d570f12cddadabbb6e98eccf896636c17c00ce50a2f22d828411b3a`
  - dependency lock SHA-256: `e6a63b31ef9182710b6cee518d6cd3cf82275bf7d5d001e07bf8a8ebb387bccc`
  - lock entries: `86`
  - installed distributions: `88`
  - MinerU source version: `3.4.4`
  - MinerU source inventory SHA-256:
    `a97e466f6d0a401689102cd86fc7494c6b01c7a8ed8ed6d529ee66a723cc05ae`
- `.tools/MinerU/profiles/pipeline-cpu-v1/verify-receipt.json`
  - bytes: `16044`
  - file SHA-256: `A57CE67FD4EAE57DBDB3770B4FBECD6BED589EE3ECA78B9F45FD0449C6AEC87D`
  - receipt seal: `44a9a85ecbbdb8d3658ea3e82d0402f413d2cb36c36b5398f1695f33dc7f31b3`
- `.tools/MinerU/capabilities/providers.json`
  - bytes: `1193`
  - file SHA-256: `3F95264A1028E4738140FF02C891A06741B249AB3F387B4CF17722046DCD213F`
  - receipt seal: `f0925f03ce014e12ff407786286c90db74077f73db00b06153b045957347dccf`

## Cleanup and diagnostics

MinerU logged that two managed service processes did not exit within its first
force-stop wait and emitted Intel Fortran window-close diagnostics during final
shutdown. The setup command still returned `0`, both smokes and receipt writing
completed, and a post-run exact process-path check found no process executing
from `.tools/MinerU`. No manual process termination or filesystem deletion was
required.

## Next gate

Complete and independently review Packet B (RunSpec v2, provider/view execution,
dynamic comparison and synthetic six-stage resume) before creating a fresh real
Dissociation reconstruction run root.
