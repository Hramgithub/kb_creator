# Number 7 Dream post-package DOCX revision

Goal id: `20260919-dream-docx-revision`. State: active.

## Objective and authority

The user edited the tracked `inputs/number-7-dream/production/Number_7_Dream_RU.docx`,
asked to commit the edit, then confirmed the separate-revision route and added
that the PDF must be updated. Preserve the user's exact DOCX bytes, restore the
frozen base package from its committed identity only after a verified copy,
build a new DOCX-derived PDF and revision package with the existing
`publication revise-docx` command, visually inspect the result, and commit
only a correctly identified successor. Do not infer PDF acceptance or release.
No push was requested.

The current `docs/governance/nri_goal_governance.md` role contract applies.
Policy orchestrator: `gpt-5.6-sol` medium, assignment `platform-unverified`,
scoped override `none`; main chat owns orchestration, integration, status and
stop/ask decisions. Engineering `gpt-5.6-terra` medium, architecture
`gpt-5.6-sol` high, independent critic `gpt-5.5` medium, bounded executor
`gpt-5.6-luna` medium and QA `gpt-5.6-luna` low are defined but not assigned.
An independent release decision remains separate.

## Initial evidence

- Only the production DOCX is modified in Git. Its edited identity is
  5,167,147 bytes / SHA-256
  `BBF475FC50E0465CE6997BC2F819833B00AE4B08AE6F7C7A689C9DACA74E520D`.
- The frozen manifest expects 5,350,241 bytes / SHA-256
  `16ED29E537C6E87553A5BA4E8CB47725B96C2AE43E5F4ECA3E078716950970D5`.
- Edited DOCX ZIP integrity and required OOXML members pass; the copied base
  verifier currently fails `package inventory mismatch`, as expected.
- `revise-docx` first verifies its base package. The base must be restored only
  after the user's edited bytes are copied and rehashed elsewhere.

## Steps

| ID | Owner | State | Evidence / gate |
| --- | --- | --- | --- |
| D1 | orchestrator | done | Exact edited bytes, Git diff and failed base verifier recorded |
| D2 | orchestrator | done | Run-local reviewed submission copied: 5,167,147 bytes / `BBF475FC...E520D`; source remained stable |
| D3 | orchestrator | done | Restored only the frozen DOCX from HEAD; copied base verifier passed manifest `930965C745...42BC60B2C8`; user edit retained byte-for-byte |
| D4 | orchestrator | done | Reusable revision builder exported 30-page PDF from exact edited DOCX; `verify-revision` passed with `awaiting_visual_review`; PDF SHA-256 `C3DD457412567A1EB89AF8DA27BE973F0B84993DE0B8CB79A8BC1C1CC84E3B4F` |
| D5 | orchestrator / user | awaiting user | Inspected all 30 page PNGs from an independent DOCX render. PDF text differs from frozen base only on pages 23–24: missing handout-2 letter added. New pagination leaves the handout-4 label alone at bottom of page 23; user must decide whether to accept this layout or edit DOCX again. No automatic acceptance |
| D6 | orchestrator | done | Commit only the exact reviewed submission, DOCX-derived PDF preview, reusable builder fix, tests and documentation as a clearly pending preservation checkpoint under `inputs/number-7-dream/revisions/20260919-post-package-docx-01/`; do not label it accepted or replace frozen production; no push |

## Definition of done

The user's edited DOCX is preserved byte-for-byte, the old production package
again verifies with its original manifest, a new PDF is produced solely from
the revised DOCX, the successor is verified and visually reviewable, and any
Git commit does not mislabel an unaccepted PDF as accepted or mutate the frozen
base authority.

The full self-contained successor remains run-local and awaits the user's
pagination decision. The tracked checkpoint is intentionally only its exact
DOCX submission and PDF preview, not a release candidate replacement.
