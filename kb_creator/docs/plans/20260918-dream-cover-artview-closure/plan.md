# Number 7 Dream cover and ArtView closure plan

## Goal

Restore PDF-driven visual discovery for ArtView, carry an explicitly accepted
cover asset into Stage 40, fail closed when a declared cover has no binary, and
rebuild a successor ArtView/HTML candidate without changing the accepted
MASTER_EN or MASTER_RU bytes.

## Authority and stop conditions

- The accepted replay-21 reconstruction and accepted MASTER_EN/MASTER_RU remain
  immutable authorities.
- Run14 remains immutable defect evidence; its HTML is not accepted.
- No manual edit of generated HTML and no scenario-only output patch.
- Stage 30 is one deterministic ArtView tool invocation. Checked-in inputs may
  bind authorities/settings only; authored review rows, authored page roles,
  and scenario-specific preselection are forbidden.
- Stage 50 is authorized only by acceptance of the exact HTML bytes. Stage 60,
  PDF, package, commit, and push remain closed until the DOCX is accepted.

## Role ownership

- Orchestration/integration/status: `gpt-5.6-sol`, medium.
- Root-cause and remediation specification: `gpt-5.6-sol`, high, task A1.
- Engineering implementation: `gpt-5.6-terra`, medium, only after A1 closure.
- Bounded QA: `gpt-5.6-luna`, low, after rebuild.
- Independent release decision: `gpt-5.5`, medium, after QA; it must not own
  implementation.

## Tasks

| ID | Owner | State | Deliverable |
| --- | --- | --- | --- |
| A1 | architecture | complete | Root cause and scenario-neutral contract in `handoffs/A1-cover-root-cause.md` |
| A2 | orchestrator + engineering | complete | PDF visual discovery / ArtView input closure with regression tests |
| A3 | orchestrator + engineering | complete | Explicit accepted cover binding and Stage-40 fail-closed validation/tests |
| A4 | orchestrator | complete | Run18 Stage 30 candidate: 20 rows, required cover, accepted masters byte-identical |
| A5 | bounded QA | complete | PASS receipt in `handoffs/A5-run16-artview-qa.md` |
| A6 | independent critic | pending | Release-gate review of the exact replacement HTML candidate |
| A7 | user | pending | Explicit acceptance of the exact replacement HTML hash |
| A8 | bounded QA | complete | PASS receipt in `handoffs/A8-run18-artview-ui-qa.md` |
| A9 | bounded QA | complete | PASS with no blockers for the exact run21 Stage-40 HTML; receipt in `handoffs/A9-run21-html-qa.md` |
| A10 | orchestrator | complete | Generic semantic-before-cover ordering, v4 strict rebind, renderer-chrome validation, and fresh run21 HTML candidate |
| A11 | orchestrator | complete | Generic authored-only figure-caption policy, regression coverage, versioned v3 config/v10 contract, and fresh run22 HTML successor |
| A12 | orchestrator | complete | Source-owned TOC display hierarchy, fail-closed Stage-40 DOM validation, versioned v4 config/v11 contract, and fresh run24 HTML successor |
| A13 | orchestrator | complete | Read-only browser QA of exact run24 cover, flat TOC, caption policy and neutral statblocks; receipt in `handoffs/A13-run24-orchestrator-browser-qa.md` |
| A14 | orchestrator | complete | Restore strict previous-config import in the active v3/v4 ArtView UI, add regression coverage and build fresh run25 Stage 30 |
| A15 | user | complete | Exported run25 accepted ArtView JSON, 20/20 reviewed; exact run-local SHA-256 `6EE7217A9B995EC3143A022ED6D6D3360CD19F3AB44C7A8169CE6222DA875BED` |
| A16 | orchestrator | complete | Recorded run25 ArtView acceptance, completed Stage 31 and Stage 40, verified HTML and all 20 assets byte-identical to run24 |
| A17 | user | complete | Explicitly accepted run25 HTML SHA-256 `774F22BC2D1FF55BBCEF22ED5BC8539508F265A01D34E7AC8C6E87CE82AB7166` |
| A18 | orchestrator | complete | Diagnosed run25 Word COM `0x80070520`; preserved its failed Stage 50 in quarantine and rebound accepted authorities into local-LibreOffice run26 |
| A19 | orchestrator | complete | Closed explicit-flat TOC DOCX regression in shared builder and test; run26 is immutable defect evidence |
| A20 | orchestrator | complete | Rebuilt run27 through Stage 50, confirmed HTML/20 assets byte-identical to accepted run25, rendered and inspected 34 DOCX pages |
| A21 | user | complete | Edited run27 DOCX in place and directed continuation; edited SHA-256 `C29A5569820A3D2734F28089619F1BC273E1013A8CD040439C3F58899CE9F5BE` |
| A22 | orchestrator | complete | Generic reviewed-DOCX authority and 44 passing control-plane tests; run28 Stage 50 preserves exact edited bytes, 30 pages visually inspected and accepted |
| A23 | orchestrator | complete | Fresh run28 Stage-60 PDF from accepted edited DOCX; all 30 rendered pages byte-identical to Stage-50 page PNGs; stop for explicit PDF review |
| A24 | user | complete | Edited run28 Stage-50 DOCX again and requested PDF rebuild; updated SHA-256 `16ED29E537C6E87553A5BA4E8CB47725B96C2AE43E5F4ECA3E078716950970D5` |
| A25 | orchestrator | complete | Run29 imports exact updated DOCX as reviewed authority, rebinds accepted upstream inputs, and generates a fresh 30-page PDF with complete render match |
| A26 | user | complete | Explicitly accepted run29 PDF SHA-256 `B39214DD4CCD084A0867697F883E7B08CEEBAD6EF3B66D5CC5EB04C41D399EBD` |
| A27 | orchestrator | complete | Diagnosed Stage-80 rejection: copied offline verifier allowed only ArtView v3; added v3/v4 validation and two-schema regression coverage, 41 tests pass |
| A28 | orchestrator | complete | Fresh run30 binds corrected verifier and preserves accepted upstream and DOCX bytes; user directed package assembly after exact-PDF confirmation request |
| A29 | orchestrator | complete | Run30 Stage 70 package and Stage 71 copied offline verification passed; 20 assets, 1 PDF, 212 files, 23 roles, no protected package ACL |
| A30 | independent critic | pending | Release review of frozen run30 manifest `930965C745E0889B931CED46D738C94A0DCEB393F38F20CD913CFF42BC60B2C8`; no release claim yet |

Current gate: run30 package is `candidate_for_release_review`, not released.
The user directed package assembly immediately after the exact run30 PDF
confirmation request; its acceptance receipt binds SHA-256
`9D9E617D263AF3F81A772E575A394E362A46429ED248D77745A9B7618B5D7875`.
The copied offline verifier passed. Independent release review, commit and
push have not been performed.

## Definition of done

- ArtView discovery is not limited to Markdown/reconstruction asset references;
  it inventories the visual source required by the publication contract.
- A PDF cover assembled from one or more source objects has a deterministic
  review candidate, preferably a full-page source render when composition is
  the semantic unit.
- Stage 40 binds the accepted ArtView cover binary and refuses
  `cover.asset = null` for a non-deferred cover.
- The replacement HTML contains the cover image and preserves all already
  corrected frontmatter, TOC, Appendix C and neutral statblock behavior.
- Tests, README/status/context, and the live Number 7 Dream contract/config are
  updated; accepted MASTER_EN/MASTER_RU hashes do not change.
