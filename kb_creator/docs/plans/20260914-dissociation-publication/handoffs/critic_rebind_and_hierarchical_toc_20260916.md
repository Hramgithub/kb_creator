# Critic receipt - MASTER_RU rebind provenance remediation and hierarchical TOC

Review kind: implementation
Date/time: 2026-09-16T01:23:02+03:00
Role: independent critic
Implemented or materially designed candidate: no
Recommendation A: GO for the MASTER_RU rebind P1 remediation.
Recommendation B: GO for the hierarchical TOC HTML/DOCX implementation.

## Scope

Reviewed two completed implementation packets before a fresh live publication run:

- A: P1 remediation in `kb_creator/scripts/scenario_master_ru.py`, tests in `kb_creator/tests/test_scenario_master_ru.py`, and engineer receipt `57A50A298E25F8DB24651A3A74C91021BEC3E2E41477FF422CF7C79F647A00C1`.
- B: hierarchical TOC implementation in `translator/translator.py`, `kb_creator/inputs/dissociation/publication/v1/configs/html.json`, `kb_creator/scripts/production_docx.py`, directly relevant tests, and engineer receipt `BBD8AB5A9DCFED35ADF9EC41B1BACE8200EC06436AA82C0A8436E19B784756EB`.

I did not edit implementation, configuration, run artifacts, accepted artifacts, canonical plan/context/status, or release files. The only write from this review is this immutable receipt.

Orchestrator policy owner: gpt-5.6-sol / medium, per repository governance
Assignment state: platform-unverified reviewer packet
Scoped override: none recorded for this reviewer
Review model/effort telemetry: unavailable from platform
Elapsed time: approximately 2 minutes 51 seconds at pre-receipt goal check
Token use: 124437 at pre-receipt goal check, exact final unavailable

## Files checked

- `kb_creator/scripts/scenario_master_ru.py` - SHA-256 `E5A4CD081A2BEAF3818A9A29DB7A5E091302FD928FD360901E61241A6641F725`
- `kb_creator/tests/test_scenario_master_ru.py` - SHA-256 `04AE92E18446643DD896D5216A201D7886C95EA93847F5C44894C11C5C11938C`
- `translator/translator.py` - SHA-256 `CED40F6F85DB2BEDA813C0C9AFE27D9C264D2BC1F7D5D8F139CF8E466EC5CC9F`
- `translator/tests/test_recovery_support.py` - SHA-256 `C9B0CC27DE267CFC02D8D57D4B474B34D39D1F3FFAB86014018B055EB362C4C1`
- `kb_creator/inputs/dissociation/publication/v1/configs/html.json` - SHA-256 `7C27A41974AB01EEAE274DCD9BB6257547E929A017C7103F60D7D428FBCB7BDC`
- `kb_creator/scripts/production_docx.py` - SHA-256 `1D070D03879832407D1C6338AF7B3F3C56B4F7C0C4D12EFC0698C79E86B1741A`
- `kb_creator/tests/test_production_docx.py` - SHA-256 `FAEA0D006620BE40B33943E4FCFA835C94D9D926ACC3AD89BCC4296F7296063E`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_master_ru_rebind_provenance_fix_20260916.md` - SHA-256 `57A50A298E25F8DB24651A3A74C91021BEC3E2E41477FF422CF7C79F647A00C1`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_hierarchical_toc_20260916.md` - SHA-256 `BBD8AB5A9DCFED35ADF9EC41B1BACE8200EC06436AA82C0A8436E19B784756EB`

## A - MASTER_RU rebind remediation evidence

- Current MASTER_EN v3 provenance is discovered from the packet-bound MASTER_EN through accepted MASTER_EN acceptance and the hash-bound `publication_stage_manifest.v1` producer stage; the producer output inventory must bind both `MASTER_EN.md` and `MASTER_EN.provenance.json`: `scenario_master_ru.py` lines 742-797.
- Provenance validation is closed at top level and validates v3 schema, scenario, inputs, projection, current master identity, derived metrics, transition shape, duplicate page pairs, and `derived.page_boundary_joins == len(page_boundary_transitions)`: lines 671-739.
- Non-exact rebinds require prior topology `from_page marker -> left -> to_page marker -> right`, current joined source immediately followed by the same `to_page` marker, exact mode, exact `from_page/to_page`, and exact left/right line SHA-256 match against an unused ledger transition: lines 800-928.
- Every provenance transition must be consumed exactly once. Exact-only rebind passes only with an empty ledger: lines 850, 891-893, 909, and 925-927.
- Rebind report now includes `current_master_en_provenance` identity and `counts.provenance_transitions`: lines 1003-1018.
- Focused resolver/rebind tests passed: 7 tests OK.
- Read-only run12 to run14 pure rebind probe resolved `outputs/10-master-en-candidate/artifacts/MASTER_EN.provenance.json`, consumed transitions `3->4 dehyphenated_word` and `4->5 continued_prose`, and produced counts `86 prior`, `84 current`, `82 exact`, `1 dehyphenated`, `1 continued`.

## B - Hierarchical TOC evidence

- Dissociation config is opt-in: `toc_policy.mode=generated_hierarchical`, two balanced columns, `12.5pt`, line height `1.25`, item gap `7px`, excluded landing/statblock anchors, 6 configured top-level anchors, 13 configured children, and `require_all_heading_ids=true`: `html.json` lines 10-55.
- Renderer uses generic anchor-id config only; no `dissociation`, `vvedenie`, `okruzhenie`, `soprotivlenie`, or other Dissociation-specific anchors occur in `translator.py` or `production_docx.py`.
- HTML hierarchical mode rejects source TOC input, malformed anchors, duplicate top-level/child assignments, cyclic/role-overlapping assignments, unknown anchors, unresolved heading anchors, and missing anchors when `require_all_heading_ids=true`: `translator.py` lines 2890-2947.
- HTML output is unnumbered nested `<ul>` with DOCX metadata `data-toc-numbering="none"`, `data-toc-layout="hierarchical"`, and point-size metadata; groups are emitted as `toc-group` parents with nested `toc-children`: lines 2948-2962.
- CSS keeps hierarchical groups together and keeps legacy flat `<ol>` styling path: `.toc ol, .toc ul.toc-root` and `.toc-hierarchical .toc-group` rules.
- DOCX builder preserves legacy numbered/flat defaults unless nav metadata requests otherwise; hierarchical mode collects complete top-level groups and splits only between groups; invalid font metadata fails before output: `production_docx.py` lines 483-569 and 628-647.
- Focused TOC unittest passed: `translator.tests.test_recovery_support.RecoverySupportTests -k toc` ran 23 tests OK.
- Manual DOCX probe passed: unnumbered hierarchical TOC, first column `["Первый раздел", "Первый подраздел", "Второй подраздел"]`, second column `["Второй раздел", "Третий подраздел"]`, no numbering, child indent greater than parent, `keep_with_next` chain `[True, True, False]`, and 12.5pt XML marker present.
- Manual invalid-DOCX-font probe raised `ValueError: DOCX TOC font metadata must be numeric points` and left no output file.
- Manual Dissociation anchor graph probe produced exactly 6 groups and 13 children, no `<ol>`, landing excluded, statblock excluded, `data-toc-font-size-pt="12.5"`, `--toc-font-size: 12.5pt`, `data-toc-columns="2"`, and `--toc-column-fill: balance`.

## Shared verification

- `py_compile` passed for `scenario_master_ru.py`, `translator.py`, `production_docx.py`, `test_scenario_master_ru.py`, and `test_recovery_support.py`.
- `json.tool` passed for `kb_creator/inputs/dissociation/publication/v1/configs/html.json`.
- Scoped `git diff --check` passed for the reviewed implementation/config/test files.
- `pytest` was not available in this reviewer environment: `python` and `pytest` are not on PATH, `.tools/MinerU/.venv/Scripts/python.exe -m pytest` reports `No module named pytest`. I used bundled Codex Python, unittest, and direct manual probes instead.

## Severity findings

### A - Rebind remediation

P0: none.

P1: none. The prior NO-GO condition is remediated: non-exact joins are now authorized only by hash-bound current MASTER_EN v3 provenance and every ledger row is consumed exactly once.

P2: The previous crash-window remains: `os.replace(stage, target)` occurs before writing the report file. Normal report-write exceptions remove `target`, but an abrupt process crash between directory replace and report write can still leave output batches without the report. This is unchanged from the prior review and is acceptable before fresh live publication if the orchestrator treats absent report / existing destination as failed and reruns from a clean run root.

### B - Hierarchical TOC

P0: none.

P1: none.

P2: Verification did not use pytest because the available local runtimes lack pytest. Focused unittest and manual DOCX probes covered the assigned behavior, but the exact engineer pytest commands were not reproduced in this reviewer environment.

P2: Word pagination may still override keep constraints in pathological layouts. The implementation mitigates this by splitting DOCX TOC columns only between complete configured groups.

## Blockers

No blockers found for either implementation packet before a fresh governed live publication run. This receipt is not a release review and does not approve acceptance of any future generated artifact.

## Conclusion

A: GO. The MASTER_RU rebind P1 remediation now enforces hash-bound current MASTER_EN v3 provenance, exact transition identity, marker topology, and one-time ledger consumption.

B: GO. The hierarchical TOC implementation is generic opt-in config, validates the anchor graph strictly, excludes landing/statblock through config, emits the required 6 top-level groups and 13 children for Dissociation, and preserves unnumbered nested HTML/DOCX with 12.5pt styling and group-safe columns.
