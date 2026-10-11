# Viral Step 6A reconstruction-builder bounded QA receipt

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6-source-reconstruction-step6a-reconstruction-builder`
- Role: bounded QA, requested `gpt-5.6-luna` / `low`
- Actual platform model/effort: unavailable
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- QA result: **fail / blocked**
- Candidate state observed: `candidate_needs_review`
- Token use: unavailable

## Scope and mutation boundary

The accepted packet, critic receipt, executor receipt, source, contract,
recovery root, predecessor roots, implementation, candidate, accepted/output
roots and Git were inspected read-only. No candidate mutation, promotion,
contract/plan/context/status mutation, Git index/ref/commit/push operation, or
runtime launch occurred. The only durable write in this worktree is this
receipt. No disposable probe was created, so probe cleanup is not applicable;
the candidate itself contains no reparse point.

## Binding checks

Pass: accepted builder packet
`terra_engineering_viral_step6a_reconstruction_builder_packet_20260831.md`
SHA-256 `F5B5684591586BFE7C22D0F73C67B4B3A849A206495FFEFF8261E3CE2E97138C`.
Pass: independent critic receipt SHA-256
`1F496F465C0A18A10DFC32FEA0535970603B1449ECC50E2C790E7E36D339E2AB`.
Pass: executor receipt SHA-256
`5E5A059BDD4CA9A431AAAE84079A66CE1BFD037215BE4AA9B505298162D4CFB0`.
Pass: admitted recovery manifest SHA-256
`41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169`.
Pass: admitted recovery evidence SHA-256
`F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC`.
Pass: source PDF is 20,718,150 bytes, SHA-256
`0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`,
124 pages, Letter `[612,792]`, rotation 0. Branch and HEAD match the packet.

## Structural and deterministic checks

Pass: candidate inventory is 471 files; 124 `pages/page-001.md` through
`page-124.md`; 124 source renders; no gaps or duplicate page numbers in
`evidence/PAGE_PROVENANCE.json`; engine admission is 209 payload files,
including 204 JPEGs; no PDF payload.

Pass: `HANDOUT_INVENTORY.json` contains exactly 39 rows. Fixed page roles are
104–110 `keeper_maps` (seven pages), 111–123
`pregenerated_investigators` (13 pages), and 124 `back_cover`. Pages 1–5 retain
contract value `unknown` and have five review rows; no contract mutation or
false final content mode was observed. Candidate state remains review-only;
there is no MASTER/accepted/production/publication promotion.

Pass: candidate QA counts are pages 124, renders 124, handouts 39, engine
payload 209, engine images 204. Markdown image references count 112; the
difference `204 - 112 = 92` matches retained unreferenced engine evidence.
Three open blocker rows are recorded and ordinary uncertainty is represented
as `needs_review`, not as final completeness.

Pass: exact command
`python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract
kb_creator/contracts/viral.json --source
<admitted Viral PDF> --recovery-root
kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate
--run-root
kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`
returned exit 0, `deterministic=true`, `pages=124`, `renders=124`,
`handouts=39`, and `verified_candidate_needs_review`. Repeated verify output
was identical.

Pass: `python -B -m pytest kb_creator/tests/test_scenario_contract.py
kb_creator/tests/test_scenario_source_reconstruction.py -q -p
no:cacheprovider` returned `124 passed`.

## Findings

### P1 — full visual QA evidence is absent

The required full contact-sheet review cannot be evidenced: candidate
`renders/contact_sheets` contains **0** files. The candidate has 124 source
renders, and spot inspection of original-resolution pages 001, 104 and 111
was possible, but that is not a substitute for full 124-page contact sheets
and per-risk selection evidence. The QA gate therefore remains
`visual_review=needs_review`; acceptance is blocked. No contact sheets were
generated because any such output would mutate candidate state.

### P1 — asset/navigation/provenance closure is not evidenced

`evidence/ASSET_PROVENANCE.json` has 0 rows and
`evidence/NAVIGATION_INVENTORY.json` has 0 rows. Entity inventory has 39 rows,
content-mode review has 5 rows, and blocker ledger has 3 open rows, but the
empty asset/navigation inventories do not establish the requested
asset/reference/entity/navigation/provenance closure. This is a candidate QA
deficiency, not repaired here.

### P2 — executor receipt command is stale against the checked-out CLI

The executor receipt's documented verify invocation uses `--source-pdf` and
`--candidate-root`, while the checked-out CLI requires `--source` and
`--run-root`. Replaying the receipt command failed at argparse before QA; the
corrected command above passed. This is evidence/documentation drift, not a
candidate mutation.

## Side-effect and forbidden-access audit

Pass for the executed QA: no MinerU, OCR, GPU/model, network, translation,
historical translation, or config access was invoked; tests used `python -B`
and disabled pytest cache. Candidate has no `.pdf`, cache/runtime, `.pyc`,
bridge/origin payload, or reparse paths. The implementation source contains
write helpers and subprocess/git helpers for the builder, but the QA invoked
only `verify` and did not run build/preflight or live extraction. The known
repository-wide 15 missing `kb_creator.pdf_raw` collection errors were not
replayed or repaired and no repo-wide green claim is made.

## Final disposition

**FAIL / BLOCKED.** Structural and deterministic checks pass, but the requested
visual coverage and asset/navigation/provenance closure are not demonstrated.
Do not promote, accept, or publish this candidate. Any remediation must be a
new bounded implementation/QA action; this QA made no findings fixes.

