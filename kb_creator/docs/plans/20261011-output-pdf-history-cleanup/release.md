# Generated PDF history cleanup release candidate

- Goal ID: `20261011-output-pdf-history-cleanup`
- Freeze time: `2026-10-11T18:50:49Z`
- Release state: independent review pending
- Old remote baseline: `91db0491f3fa0876ab0c44d45151f8006f812d5a`
- Clean root baseline: `141758c2d7e67acde0f4a9f28b2822379e3f5a18`
- Publication method: exact `--force-with-lease` against the old remote baseline

## Frozen handoff candidate

| File | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `kb_creator/docs/handoff/MODEL_HANDOFF_SUMMARY.md` | 12757 | 159 | `8DBAEEA4A0D292C9878E9FA0CE7DD6117CD8A79A7B1B5B0C204FBD3B1A6D181F` |
| `kb_creator/docs/handoff/MODEL_HANDOFF_SPEC.md` | 35571 | 566 | `4AA337E6CA0629CFFE2446D29BD294E6B33C0E93B43E5A3F365AB2231EEB17FD` |

Any candidate-byte change invalidates the handoff portion of this review.

## Exact history delta

Relative to old remote baseline `91db049`, clean root `141758c` deletes only:

1. `kb_creator/output/innsmouth_final/runs/20260730T172713Z/Pdf/The_Innsmouth_Terror_Full_RU_two_column.pdf` — 65,261,797 bytes;
2. `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/Pdf/The_Innsmouth_Terror_RU.pdf` — 64,314,373 bytes.

No other baseline path or blob is intentionally changed. Reports and manifests
remain as historical evidence and may contain references to the removed binary
artifacts. Accepted/production inputs and Git LFS payloads remain.

## QA evidence

- `handoffs/C4-qa-v01.md`: changes required for premature publication wording
  and an over-specific ignore-rule claim; deletion scope and counts passed.
- `handoffs/C4-qa-v02.md`: pass after both wording corrections.
- Root import count: 3015 tracked paths.
- Root `kb_creator/output/`: three tracked non-PDF paths.
- Root `pdf_raw/`: five tracked paths, unchanged.
- The old `origin/main` tracking ref remains `91db049`; no remote mutation has
  occurred at this freeze.

## Release boundary

Approval may authorize the orchestrator to commit the reviewed documentation,
fetch the remote, require the lease to remain at `91db049`, and publish with
`--force-with-lease`. It does not authorize plain force, deletion of any other
path, mutation of the original NRI checkout, book acceptance, pipeline launch,
or restoration/removal of unrelated assets.

## Independent decision

Pending C5 receipt.
