# U8 normal DOCX fidelity QA v05

- Timestamp: 2026-10-04 23:20:37 UTC / 2026-10-05 02:20:37 Europe/Moscow.
- Goal: `20261004-user-docx-review`; frozen prospective normal-DOCX fidelity R1–R4 QA.
- Role: bounded QA `gpt-6-luna` / medium (platform unverified). Orchestrator/policy owner `/root`, gpt-6-sol / medium. Scoped override: none.
- Assignment state: finite v04 implementation regression and R1–R4 focused cases complete. No release decision; independent critic review remains separate.
- Elapsed time: approximately 6 minutes from this v05 assignment to receipt. Token usage unavailable.

## Frozen identities and preservation

At run start and after all testing, rehashed the full v04 implementation freeze, all 43 files including byte lengths and SHA-256. Both checks: 43/43 match, zero mismatches. Manifest SHA-256: `9A948C1264D64A48E551221E5604FC6435F2641A9B50AAEE13079C5F657C8BEC`.

Rehashed all six reviewed latest DOCX and all three fixed candidate DOCX before/after; identities match their predecessor receipts. Rechecked canonical terminology CSV SHA-256 `8F6A41A64CA5A90621F6B8C2F3B40B4FE3658D7DE88B0D0A82BF95C1F82E6800`; rechecked all nine explicitly retired HTML/PDF targets remain absent (9/9). No implementation, test, fixture, schema, book/source, latest, previous evidence, canonical or release file was changed by QA. Existing all-367-page candidate review is inherited solely by exact hashes; no pages were re-rendered or re-viewed. No actual reviewed book was replayed through the prospective normal v3/v2 route.

## Runner and test execution

The runner was verified as bundled Codex Python `C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`, `-B -X utf8`, with only existing local QA libraries appended from `D:\NRI\.tools\python-3.13.14\Lib\site-packages`. Pytest resolved to version **9.0.2** at `D:\NRI\.tools\python-3.13.14\Lib\site-packages\pytest\__init__.py`; no package installation, repository Python interpreter, or fixture/code edits.



Exact interpreter, pytest import location/version, flags, full 19-module and focused four-module argv, exits, result-log names and outcome counts are recorded in `pytest-run-manifest-v01.json`.

The full exact 19-module list is recorded in the engineering freeze/report and prior v04 QA receipt; this v05 run repeats that same list. No old output/log/root was reused. Test roots are under `audit/fidelity-qa-v05/pytest-basetemp-elevated-01` and `pytest-r1-r4-elevated-01`; failed ordinary attempts are preserved in `pytest-basetemp-sandbox-01` and `pytest-r1-r4-sandbox-01`.

## R1–R4 class and seam coverage

| Class | Prepared test evidence executed | Boundary exercised |
| --- | --- | --- |
| R1: whole numeric operand and real field | `test_numeric_field_and_reviewed_domain_misbinding_fails` includes final-digit partial operand and `Luck` selected as `STR`; `test_resealed_invalid_operation_fails_public_builder_before_output` includes resealed partial operand; `test_source_bound_characteristics_and_edu_exception` + approved projection/Word control | Invalid whole-operand/field bindings fail direct validation and before public-builder output; valid whole `STR 13 -> 65` positive remains accepted. |
| R2: reviewed physical-page/story/entity/occurrence ownership | Same direct misbinding test parametrizes source page 9999, absent story, foreign book, entity and occurrence, and changed source-render digest; public-builder test parametrizes foreign page/story | Out-of-domain edits reject; valid reviewed-domain control remains covered. This is evidence of explicit declared-domain enforcement, not a claim of semantic PDF image understanding. |
| R3: accepted canonical CSV/closed overlay mapping and exceptions | `test_accepted_registry_row_binds_label_and_review_required_does_not`, `test_terminology_requires_resolved_authority`, collision decision test, and `test_accepted_book_overlay_label_projects_and_reopens_word`; public builder test includes invented target | Valid accepted registry/overlay target passes; absent/invalid target or reference, review-required row, unresolved collision, and primary/editorial unbound dispositions fail closed; positive projection reopens in Word. |
| R4: inline drawing order including same paragraph | `test_word_observer_rejects_wrong_story_orphan_and_zero_extent` includes `inline_before_anchor`; `test_word_observer_matches_referenced_media_owner_and_extent`; guarded DOCX synthetic positive | Reopened package rejects image before paired anchor/text in same paragraph and retains valid placement/control; media ownership/extent checks remain exercised. |
| Cross-cutting surfaces | `test_resealed_invalid_operation_fails_public_builder_before_output`, `test_direct_builder_missing_guard_fails_before_output`, `test_offline_verifier_reopens_exact_plan_not_resealed_substitute`, `test_four_contract_documents_are_versioned_and_structurally_closed`, valid synthetic PDF->review->plan->projection->reopened Word and offline-verifier tests | Public prewrite rejection does not create an output; offline verifier binds exact sealed plan; four schemas remain versioned/closed. Mechanical verification remains pending output review. |

The tests establish mechanical fail-closed cases and valid synthetic controls only. They do not establish that a particular human-authored review row correctly interprets source semantics; automatic paint discovery is explicitly incomplete and requires all-page human review. Successful XML or offline verification does not establish visual visibility, source completeness, or semantic approval; package state remains `verified_pending_visual_review` / `needs_output_review`.

## Findings, files, next action

No new failure in the assigned prepared test sets. R1–R4 are addressed in the tested v04 code paths per the finite prepared fixtures above; this is bounded QA, not a general redesign or independent release decision. Candidate identities remain those previously reviewed and their visual QA is inherited by exact hash only.

Only new artifacts: `audit/fidelity-qa-v05/` (this report, four captured pytest logs and four fresh basetemp roots) plus immutable `handoffs/U8-fidelity-qa-v05.md`. No canonical plans/context/status/release files changed. Main owns integration and the next independent critic decision; final release and human book acceptance remain pending.
