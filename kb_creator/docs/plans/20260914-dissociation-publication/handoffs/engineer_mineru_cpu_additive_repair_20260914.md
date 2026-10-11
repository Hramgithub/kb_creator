# Engineering receipt — MinerU CPU additive profile repair

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-cpu-additive-profile-repair`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Result: the CPU lock now carries exact `six==1.17.0`, with an explicit,
  fail-closed additive repair path for an existing unverified CPU profile
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not a live runtime smoke,
reconstruction, publication, independent review, or release acceptance.

## Implemented result

`requirements.windows-cpu-pipeline.lock.txt` adds only `six==1.17.0`; the CUDA
lock was not changed. Ordinary `setup.ps1` still refuses to repair an installed
profile implicitly. The operator must select `-RepairProfile`, which is limited
to the existing receipted `pipeline-cpu-v1` profile and is mutually exclusive
with profile recreation.

Before dependency mutation, `profile_receipt.py plan-repair` proves all of the
following and emits a sealed plan atomically:

- no verification receipt exists;
- the install receipt seal, exact nested identities, profile, and CPython
  evidence are valid;
- installed inventory and profile Python identity equal the receipt;
- source identity and the old full pip report still equal their receipted
  identities;
- the old report has exactly one provenance row for every old exact pin;
- the new lock is precisely the old pins plus one or more new exact pins, with
  no removal, version change, overlap, duplicate, missing, or extra pin.

Setup installs only the planned additions with `pip install --no-deps` into the
same contained CPU profile and writes a separate delta report below that
profile. After `pip check`, `finalize-repair` revalidates the sealed plan and all
mutable inputs, requires the actual inventory to equal the complete new lock,
requires an exact delta report, and deterministically merges old and delta rows
in canonical distribution-name order. The merged full report and replacement
sealed install receipt are each published by atomic file replacement. The
shared JSON writer forces LF bytes so the precomputed report identity is stable
on Windows and exactly matches the published file.

All validation and receipt construction completes before publication. If the
process stops between the two atomic replacements, the old receipt/report pair
no longer matches and subsequent use fails closed rather than accepting
unreceipted state.

## Files changed

- `MinerU/requirements.windows-cpu-pipeline.lock.txt`
- `MinerU/scripts/setup.ps1`
- `MinerU/scripts/profile_receipt.py`
- `MinerU/README.md`
- `SETUP.md`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

`profile-common.ps1`, CUDA locks, MinerU source, model payloads, sealed prior
runs, canonical goal documents, critic receipts, `.codex` configuration, and
the actual `.tools` tree were not changed by this task. No package install,
download, deletion, real PDF/source run, remote call, API call, or commit was
performed.

## Verification

- PowerShell parser: PASS for `setup.ps1` and `profile-common.ps1`.
- Focused additive tests: `18 passed, 47 deselected`.
- Full focused regression: `85 passed in 21.41s` for
  `test_mineru_cpu_profile_packet_a.py` and
  `test_mineru_three_view_tools.py`.
- Adversarial coverage includes removed/changed pins, stale or resealed
  receipts, inventory/source drift, malformed/duplicate old reports,
  missing/extra/duplicate delta rows, existing verify receipt, a single-pin
  delta, exact explicit setup routing, successful report/receipt replacement,
  stable Windows report bytes, and preservation of old artifacts on validation
  failure.
- Scoped `git diff --check`: PASS (Git emitted only the existing Windows line
  ending conversion advisory for `setup.ps1`).

## Risks and next action

The repair intentionally has no automatic rollback or retry cleanup after pip
starts. A post-mutation failure leaves the old receipt authoritative and the
profile fail-closed; the lock-keyed repair evidence also prevents an ambiguous
retry. An operator must then make an explicit bounded recovery/recreation
decision.

Next: independent implementation review. Only after review should the
orchestrator authorize the live local command `setup.ps1 -RepairProfile`, then
run the required CPU model-load and `pipeline/txt` plus `pipeline/ocr` smoke.
