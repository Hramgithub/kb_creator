# Frozen model-handoff candidate — v03 (superseded)

- Goal ID: `20261011-model-handoff`
- Freeze time: `2026-10-11T18:25:04Z`
- Orchestrator policy owner: main chat, `gpt-6-sol` / medium
- Actual orchestrator model/effort: unavailable
- Release state: superseded by `../20261011-output-pdf-history-cleanup/`
- User authorization: prepare summary/spec; no commit or push authorized

## Frozen candidate

| File | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `kb_creator/docs/handoff/MODEL_HANDOFF_SUMMARY.md` | 12585 | 157 | `87B2B29BE33D3EB62D86D02C76C708F2C73A98463832256D020BC17D151DD5D1` |
| `kb_creator/docs/handoff/MODEL_HANDOFF_SPEC.md` | 34571 | 559 | `668A269479D9090964CC7B38639F8BEC89368147079401828D0E218E80505C7A` |

Any candidate-byte change invalidates this review and requires a new freeze.

Candidate v03 was valid for the original import baseline. The user-approved
history cleanup changed the baseline and both handoff documents. The current
candidate identity and release decision are therefore owned by
`../20261011-output-pdf-history-cleanup/release.md`; the receipts below remain
immutable historical evidence only.

## Evidence

- Architecture/dependency receipt:
  `handoffs/H2-architect-receipt.md`.
- Bounded QA initial receipt:
  `handoffs/H4-qa-receipt.md`.
- Bounded QA correction recheck:
  `handoffs/H4-qa-recheck-v02.md`, pass.
- Independent review of candidate v01:
  `handoffs/H5-release-critic-v01.md`, changes required. Candidate v01 was
  rejected because it described `git lfs fsck` as guaranteed read-only and
  omitted the current CPU-first MinerU run-spec branch.
- Independent recheck of candidate v02:
  `handoffs/H5-release-critic-v02.md`, changes required. It closed the LFS
  finding and narrowed the remaining issues to template-selection wording and
  incorrect freeze chronology.
- Independent release decision for candidate v03:
  `handoffs/H5-release-critic-v03.md`, approved within documentation-handoff
  scope.
- Orchestrator mechanical recheck: 3017 tracked paths, zero tracked
  `kb_creator/working/**` paths, zero ambiguous `3017 objects` wording, zero
  candidate trailing whitespace, all 18 relative handoff links resolved.

## Previous rejected freeze

Candidate v01 was frozen at `2026-10-11T18:17:02Z`:

- summary: 12585 bytes, 157 lines,
  `87B2B29BE33D3EB62D86D02C76C708F2C73A98463832256D020BC17D151DD5D1`;
- specification: 32891 bytes, 538 lines,
  `29065236A5A8C29A89CA2170C1163356427C3EFF67B405789C1EE3D68AA247AA`.

The v02 specification corrects both critic findings: it classifies
`git lfs pull` and `git lfs fsck` as state-changing/repair-capable operations,
and documents the legacy and CPU-first MinerU run-spec branches, including the
revision-3/v4 selection used by the current five-step contract.

Candidate v02 was frozen with the unchanged summary and a 34478-byte,
558-line specification at
`1891ABF1307A4ABE7461673C4DC8501B94908C833E45934B720C2BD8BBE552F3`.
Its narrow recheck found that the recorded freeze time was later than the host
clock and that the intake wording implied revision 3 was the only offered
template. Candidate v03 records an actual post-edit freeze time and states that
intake offers both the compatibility template and the revision-3 template.

## Scope and intentional exclusions

This candidate documents the repository and its continuation boundary. It does
not make the repository executable, restore missing corrected DOCX, vendor the
translator, supply the CoC registry or runtimes, run the broad test suite,
start a book, accept a book, commit files, or push them.

The independent critic must not implement or materially redesign the candidate.
It should verify factual sufficiency, current-vs-historical separation, safe
continuation guidance, explicit portability gaps, acceptance semantics, and
fitness for transfer to another frontier model.

## Independent decision

**Approved** for documentation handoff by the independent critic in
`handoffs/H5-release-critic-v03.md`. The decision applies only to the exact v03
bytes recorded above. It does not establish standalone runtime readiness, book
acceptance, publication, deployment, commit, or push.
