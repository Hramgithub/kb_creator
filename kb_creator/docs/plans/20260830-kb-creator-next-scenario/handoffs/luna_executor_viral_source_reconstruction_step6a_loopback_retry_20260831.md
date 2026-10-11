# Luna executor receipt — Viral Step 6A loopback retry

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-loopback-retry`
- Role / policy effort: `gpt-5.6-luna` bounded execution / `medium`
- Actual platform model / effort: `unavailable`
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; scoped override: `none`
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch / HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Successor run root: `kb_creator/working/viral/source_reconstruction/20260831_step6a_loopback_retry`
- Result: `blocked`

## Mandatory stop

The original Step 6 packet, accepted MinerU bridge/cache/protected-prefix
amendments and reviews, prior retry/continuation receipts, and the accepted
loopback/output delta and critic review were read. Required packet identities
were rechecked; the supplied loopback delta matched SHA-256
`12EA488E8732FF8523DC996725A915B43BD628BF5AC7506A2A02F74AAA437857` and its
critic review matched SHA-256
`D7EB6A6FDBBE97469EFD930A4B93E4ED74E961C4F89FAA032D06E8186A5BA61F`.

The fresh successor preflight passed the exact branch/HEAD gate, pinned
MinerU/model/code gate, protected-prefix baseline, independent PDF observer,
`ScenarioContract.resolve_source_path()`, and `pdfinfo`. The source observed
was the admitted 124-page Letter PDF with 20,718,150 bytes and SHA-256
`0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.

The single authorized direct pinned MinerU launch then created a copy of the
immutable source PDF below the successor run root:

`engine/mineru_hybrid_high/_bridge_runtime/tmp/mineru-api-client-taxsj413/output/af4c1080-5206-4a9e-8164-8cb897fcfea2/uploads/Call_of_Cthulhu_Viral.pdf`

The copied file is 20,718,150 bytes. This is the packet stop condition
`source-copy`; it violates the no-source-copy boundary even though it is under
the otherwise allowlisted runtime evidence directory. The exact related
MinerU process tree was stopped after the stop was observed. No unrelated
process was stopped. No repair, cleanup, fallback, second launch, or `verify`
was performed.

## Commands and outcomes

1. Focused diagnostic:
   `PYTHONDONTWRITEBYTECODE=1 python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider`
   — exit `0`, `22 passed`.
2. Successor preflight with the exact absolute successor root — exit `0`;
   fresh runtime/model/protected-prefix/PDF/contract/pdfinfo evidence written.
3. One build launch with the exact direct executable and argv profile
   `--backend hybrid-engine --effort high --formula True --table True` —
   stopped after the source-copy artifact was observed; process exit code is
   `unavailable` because the related process tree was stopped at the mandatory
   boundary.
4. `py_compile` was not invoked. MinerU `verify.ps1`, `run-hybrid.ps1`, and
   `initialize.ps1` were not invoked.

Child-only environment used the accepted controls, including:
`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `http_proxy`, `https_proxy`, and
`all_proxy` set to `http://127.0.0.1:9`; `MODELSCOPE_ENDPOINT` set to the same
unbound sink; and both `NO_PROXY` and `no_proxy` set exactly to
`127.0.0.1,localhost,::1`. The parent environment was not mutated.

## Evidence and mutation audit

- Immutable predecessor root `kb_creator/working/viral/source_reconstruction/20260831_step6a/` was not written, renamed, cleaned, or reused.
- Successor root contains the preflight contract/source identity and only
  runtime evidence under `engine/mineru_hybrid_high/_bridge_runtime/**`.
- No `RECONSTRUCTED_EN.md`, page output, acceptance manifest, publication
  output, historical translation input, or contract mutation was produced.
- No `.pyc`, `__pycache__`, pytest cache, browser profile, credential/token
  artifact, or raw tool log was observed in the successor inventory.
- Before/after Git status preserved all pre-existing worktree lines. The task
  delta is limited to the three allowlisted seam/test paths, the exact
  successor root, and this receipt; no stage, commit, push, branch move, or
  remote mutation occurred.
- `git diff --check` reported only the pre-existing `.gitattributes` LF/CRLF
  warning and no whitespace error.

## Blocker and next action

- Blocker class: `source_copy_inside_bridge_runtime`
- Earliest failing layer: `MinerU bridge output/cache containment`
- State: `open`
- Required action: orchestrator must decide whether a separately reviewed
  architecture delta can make the pinned MinerU API path avoid copying the
  source PDF, or retain this run as blocked evidence. This receipt does not
  authorize cleanup or another successor run.

No `candidate_needs_review` claim is made because the candidate build did not
complete. This task made no accepted, production, publication, translation,
`MASTER_EN`, contract, commit, push, or remote claim.

- Elapsed time: unavailable
- Token use: unavailable
- Receipt SHA-256: intentionally detached; compute after final write without
  editing this receipt.
