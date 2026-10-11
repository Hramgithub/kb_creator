# Critic receipt - MASTER_RU translation rebind

Review kind: implementation
Date/time: 2026-09-16T00:58:32.3637758+03:00
Role: independent critic
Implemented or materially designed candidate: no
Recommendation: NO-GO for the reusable rebind implementation until allowed non-exact joins are bound to the current MASTER_EN v3 provenance, not inferred only from string adjacency. Run14 evidence itself is internally consistent and useful, but it does not close the reusable invariant.

## Scope

Reviewed only the new reusable MASTER_RU translation rebind in `kb_creator/scripts/scenario_master_ru.py`, its focused tests in `kb_creator/tests/test_scenario_master_ru.py`, and read-only run14 evidence under `kb_creator/working/dissociation/publication/20260916-publication-14`.

I did not edit implementation, accepted artifacts, run outputs, later stages, canonical plan/context/status, or release files. The only write from this review is this immutable receipt.

Orchestrator policy owner: gpt-5.6-sol / medium, per repository governance
Assignment state: platform-unverified reviewer packet
Scoped override: none recorded for this reviewer
Review model/effort telemetry: unavailable from platform
Elapsed time: approximately 1 minute 27 seconds at pre-receipt goal check
Token use: 112787 at pre-receipt goal check, exact final unavailable

## Files checked

- `kb_creator/scripts/scenario_master_ru.py` - SHA-256 `6F3AC9C71F7C335DA54C00995BD298D47D8D0E143D054ED18E9FCEBE983BC106`
- `kb_creator/tests/test_scenario_master_ru.py` - SHA-256 `7B66A8183A6B661D38A0F59ED106C01B20502E774879BA34A39997AB92D2492F`
- `kb_creator/working/dissociation/publication/20260916-publication-14/submissions/master_ru/translation-rebind.report.json` - SHA-256 `FC3C956B96492CD7856A4C74D5C5AF35188C73D65291CBEDA6A2A1E03B721D15`
- `kb_creator/working/dissociation/publication/20260916-publication-14/outputs/21-master-ru-candidate/evidence/MASTER_RU.qa.json` - SHA-256 `09E3740BAB282CE53BDC913BF4998BBDE64740EE3D73419E1C03DF45E8D3C081`
- `kb_creator/working/dissociation/publication/20260916-publication-14/outputs/21-master-ru-candidate/evidence/MASTER_RU.verification.json` - SHA-256 `FD99C463643EA1FC0C283C0E3E89E32B5C9A0E76674785B88037208B8C5ED58A`
- `kb_creator/working/dissociation/publication/20260916-publication-14/outputs/40-html-candidate/artifacts/Dissociation_RU.html` - SHA-256 `1E0AF3ECD764DF5E1231F5E1228332C4B587F56A221C8580682D932F2B7790F7`

## Evidence

- Separate current/prior authority roots are present in the CLI and implementation: `rebind_batches(..., authority_root, prior_authority_root)` resolves `packet_root` under current authority and prior packet/batches under prior authority, lines 737-753.
- Current and prior packet manifests are validated and scenario ids compared before materialization, lines 756-759.
- Prior translated batches are validated against prior packet inputs using `_closed_translated_batch` and `validate_batch`, lines 710-733.
- Exact-source reuse is deterministic by `source_text`, with duplicate source candidates consumed in order and tracked in `used`, lines 642-665.
- The implementation handles the expected joined source shape by matching prior `left, marker, right` against current `joined, same marker`, lines 667-683.
- Output batches are staged in a temporary directory and moved into place only after translated batch files and the sealed report payload are computed, lines 772-794; report write failures attempt to remove the output directory, lines 795-799.
- Tests cover both supported join modes and one unproved-edit failure: `test_scenario_master_ru.py` lines 139-173.
- `py_compile` passed for `scenario_master_ru.py`.
- Focused unittest passed: `test_translation_rebind_handles_both_master_en_page_boundary_modes` and `test_translation_rebind_fails_closed_on_unproved_edit`.
- `git diff --check -- kb_creator/scripts/scenario_master_ru.py kb_creator/tests/test_scenario_master_ru.py` passed.
- Run14 rebind report counts match the assignment: `exact_source=82`, `dehyphenated_word=1`, `continued_prose=1`, `prior_units=86`, `current_units=84`.
- Run14 MASTER_EN provenance has exactly two v3 page-boundary transitions: `3->4 dehyphenated_word` and `4->5 continued_prose`; `derived.page_boundary_joins=2`.
- Run14 Stage21 QA passed with no findings; Stage21 independent verification status is `verified_candidate_pending_user_acceptance` with no findings.
- Run14 MASTER_RU and HTML both contain the joined Russian phrases `пластичность человеческого тела` and `конец того же дня`.
- Run14 HTML contains `font-variant-numeric: lining-nums`.
- Synthetic read-only probe showed the reusable function accepts an unproven page-marker join if prior/current strings happen to match: prior `alpha`, `<!-- source-page-099 -->`, `beta` rebounded to current `alpha beta`, marker as `continued_prose`, even though no MASTER_EN v3 provenance was supplied or checked.

## Severity findings

P0: none.

P1: Reusable join authorization is broader than the stated invariant. `_rebind_translation_units` treats any unique prior `left, source-page marker, right` sequence as a proved join when `left + " " + right` or dehyphenated `left[:-1] + right` equals the current source and the next current unit is the same marker. It does not read the current MASTER_EN provenance, does not check `page_boundary_transitions`, does not compare transition page pairs, modes, or boundary line hashes, and therefore does not enforce "exactly the two proved MASTER_EN v3 page-boundary joins" as a Python invariant. Run14 happens to match the two real transitions, but the reusable script can accept other accidental page-marker joins.

P2: Atomic output/report behavior is rollback-on-exception, not fully crash-atomic as a pair. `os.replace(stage, target)` happens before `_write(report_target, report)`. If report writing raises, the code removes `target`; if the process crashes between the replace and report write, a destination directory may exist without its report. This is probably acceptable for an operational script with rerunnable absent-destination checks, but it is not a single atomic commit of both outputs.

P2: Test coverage proves the happy join modes and one unrelated changed-source failure, but it does not cover the key over-acceptance case: a synthetically matching page-marker join not listed in MASTER_EN v3 provenance. It also does not exercise the `rebind_batches` file-level path with separate current/prior authority roots, stale prior packet/batch identity, destination/report collision, or report-write rollback.

## Blockers

The P1 authorization gap blocks GO for the reusable implementation. The smallest fix is to bind rebind authorization to current MASTER_EN v3 provenance or an equivalent hash-bound transition ledger: only allow non-exact rebind rows whose mode, marker/page transition, left/right source hashes, and current packet sequence match a recorded `page_boundary_transitions` entry. Add a negative test where a matching `left marker right` split exists but is absent from that ledger and must fail closed.

## Conclusion

NO-GO for the reusable MASTER_RU translation rebind as a permanent pipeline invariant. Run14 evidence is consistent and shows the intended result for this scenario, but the script currently proves joins by local string topology instead of the MASTER_EN v3 transition authority.
