# Critic receipt - MASTER_EN boundary cleanup and lining numerals

Review kind: implementation
Date/time: 2026-09-16T00:41:57.2783276+03:00
Role: independent critic
Implemented or materially designed candidate: no
Recommendation: GO for reusable pipeline/script candidate; fresh publication rebuild is still required before claiming the current run12 reader artifact is fixed.

## Scope

Reviewed only the reusable candidate changes for MASTER_EN page-boundary normalization and production lining numerals. I did not edit implementation, source/reconstruction inputs, accepted artifacts, canonical plan/context/status, release files, or existing run outputs. The only write from this review is this immutable receipt.

Orchestrator policy owner: gpt-5.6-sol / medium, per repository governance
Assignment state: platform-unverified reviewer packet; review role executed in this thread
Scoped override: none recorded for this reviewer
Review model/effort telemetry: unavailable from platform
Elapsed time: approximately 4 minutes
Token use: 120529 at pre-receipt goal check, exact final unavailable

## Files checked

- `kb_creator/scripts/build_scenario_master_en.py` - SHA-256 `C68148519F5C3AFAAAEB125BD83CFD2143045D21194750DE99F7F0DD26A1A5F1`
- `kb_creator/scripts/verify_scenario_master_en.py` - SHA-256 `5CE3511BFBDBF3BA88A6C90E6A528B86E650582D8567C5B159A05035DB1FB4A0`
- `translator/translator.py` - SHA-256 `F9CC50CB592C4921FE117B12E65CB8F159A30CE19D6128B90B708E7643FB4F3A`
- `kb_creator/tests/test_build_scenario_master_en.py` - SHA-256 `1971624CB8C276B13742DC621498BD25D9EB4058ABA394918AA023943C596366`
- `kb_creator/tests/test_publication_html_adapter.py` - SHA-256 `9099B77E5AFF1C4984B180786B3ACA7A155E883D2DB41552255BEF4FD4574A6B`
- Engineer receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_master_en_boundary_lining_numerals_fix_20260916.md`
- Read-only historical probe: `kb_creator/working/dissociation/publication/20260915-publication-12`

## Evidence

- Static review confirms the MASTER_EN fix is in the V3 assembly path, after excluded-page projection and before derived counts/materialization: `build_scenario_master_en.py` lines 2012 and 2025.
- Boundary join guard is fail-closed for marker topology, consecutive pages, plain prose, lowercase continuation, terminal punctuation, dehyphenation, and non-hyphenated prose continuation: `build_scenario_master_en.py` lines 1974-2006.
- Provenance/QA now record `derived.page_boundary_joins` and `page_boundary_transitions`: `build_scenario_master_en.py` lines 2019 and 2039.
- Independent verifier recomputes expected MASTER_EN, derived count, and transition ledger before byte comparison and provenance comparison: `verify_scenario_master_en.py` lines 618, 626, 634-636, and 650-652.
- Production CSS explicitly sets `font-variant-numeric: lining-nums` on `body`, inherited by normal body and statblock text; statblock spacing remains scoped to `.statblock-card`: `translator.py` lines 4316-4319 and 4387-4389.
- Test coverage includes positive dehyphenated and continued-prose joins, marker-count preservation, transition modes, fail-closed non-prose cases, independent verifier agreement, and production HTML assertion for `lining-nums` with no `tabular-nums`: `test_build_scenario_master_en.py` lines 162-179; `test_publication_html_adapter.py` lines 223-233.
- `py_compile` passed for builder, verifier, and translator with bundled Codex Python.
- `unittest kb_creator.tests.test_build_scenario_master_en.MasterEnV3NeutralTests` passed: `Ran 5 tests ... OK`.
- `git diff --check -- kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py translator/translator.py kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_publication_html_adapter.py` passed.
- `pytest` could not be run in the available Python runtimes in this reviewer environment: bundled Codex Python and `.tools/MinerU/.venv` both reported `No module named pytest`; Windows `py` reported `No installed Python found`.
- Read-only recalculation from run12 accepted reconstruction authority produced exactly the intended reusable transitions: page `3->4` `dehyphenated_word`, page `4->5` `continued_prose`; marker count stayed `6`; `malleability of the human body` and `end of the same day` are present in the normalized expected output; expected normalized MASTER_EN SHA-256 is `2EB528C44A2B1A20C00D167AD255BA0C767B74653564A9FE9182D6A3FC51CABE`.
- Read-only historical run12 artifacts remain old, as expected for immutable outputs: current run12 `MASTER_EN.md` SHA-256 is `571F96B077ACA59072C0399433E8372E997C9FC5D07428698D5580A2D5A1BED5`, still contains the split `malle-` and `same day` boundaries; current run12 HTML SHA-256 is `4AED240DBA16BC99E5EFEFCEF6759DA0944CB340FEBFE8D747F456012E74299A` and does not contain `font-variant-numeric: lining-nums`.

## Severity findings

P0: none.

P1: none for the reusable implementation candidate.

P2: The verifier is independent in authority resolution and final byte/provenance comparison, but the page-boundary heuristic is intentionally mirrored in builder and verifier. This satisfies the current "do not import builder code" boundary, but it is not a diverse algorithmic check for future heuristic mistakes. Current tests partially mitigate this by covering positive and fail-closed cases.

P2: Marker relocation preserves marker count and records transition hashes, but after a join the page marker is placed after the completed reader paragraph. This is acceptable for reader flow with the added transition ledger, but consumers that interpret `<!-- source-page-NNN -->` as "all following content belongs to this source page until next marker" must use `page_boundary_transitions` for exact boundary traceability.

P2: Historical candidates are deliberately invalidated by the new derived/provenance contract. That is the correct fail-closed behavior, but any user-facing claim that the current run12 HTML is fixed requires a fresh governed rebuild from the changed scripts.

## Blockers

No implementation blockers found for the reusable candidate. The only verification limitation is local pytest availability in this reviewer environment; the focused unittest suite and static/read-only probes passed.

## Conclusion

GO for merging/using the reusable pipeline-script fix. Do not mark the existing run12 MASTER_EN/HTML artifact as fixed or accepted; rebuild a new candidate through the governed pipeline before user-facing acceptance or release review.
