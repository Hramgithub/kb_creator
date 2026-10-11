# Independent critic receipt: MASTER_RU contextual terminology remediation

## Receipt metadata

- goal_id: `20260914-dissociation-publication`
- step_id: `master-ru-contextual-terminology-independent-review`
- review_kind: `implementation`
- assignment_state: `complete`
- timestamp: `2026-09-15T14:40:23.8058083+03:00`
- reviewer_role: independent critic, `gpt-5.5/medium` per assignment
- orchestrator_policy_owner: `gpt-5.6-sol/medium`; actual platform identity unverified
- scoped_override: read-only implementation review of generic contextual terminology remediation for MASTER_RU Stage20/Stage21 tooling
- implemented_candidate: no
- materially_designed_candidate: no
- edited_candidate_or_pipeline: no
- receipt_scope: this file only
- elapsed_time: unavailable as an exact platform metric; local active review segment approximately 25 minutes
- token_use: exact review delta unavailable

## Files checked

- `kb_creator/scripts/scenario_master_ru.py`
  - bytes: `50560`
  - sha256: `54C4A0DFA28D31C69F0E6BAABF1DE28DE758FF9C7F5B0361FF3381357A34CD19`
- `kb_creator/scripts/verify_scenario_master_ru.py`
  - bytes: `41398`
  - sha256: `515BBC51025B8CFB63E806035D8B38587A3D665669E970EF4F4090183B730B31`
- `kb_creator/tests/test_scenario_master_ru.py`
  - bytes: `26806`
  - sha256: `48DA0CC5CC2A0D947F21D8FAC770A23A102CAAF9A27C373C4DCCDAE32D435535`
- `kb_creator/tests/test_verify_scenario_master_ru.py`
  - bytes: `13002`
  - sha256: `DE6DA0349F517EEB38EE4AC330CCFAF53F697EFB6465E34AB839B1C9AF234A91`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_master_ru_contextual_terminology_20260915.md`
- Schema compatibility spot-check:
  - `kb_creator/contracts/master_ru_submission.v1.schema.json`

## Review focus and evidence

Reviewed the implementation against the assignment requirements:

- domain preservation and terminology authority merge;
- generic contextual classifier soundness;
- absence of Dissociation/Pilot/unit-specific production hard-coding;
- required skill vs occupation/name excluded vs ambiguous fail-closed behavior;
- producer/verifier independence;
- sealed evidence compatibility and exact verifier agreement;
- adversarial gaps and regression coverage.

Observed implementation properties:

- CSV and JSON terminology parsing now retains `domain`; strict Markdown skills table contributes implicit `skill`.
- Explicit-vs-explicit domain conflicts fail closed in producer and verifier.
- Explicit CSV/JSON domain is allowed to override compatible implicit Markdown skill-table classification when source/target are otherwise consistent.
- Skill-domain occurrences are classified from local structure/syntax into:
  - `required_skill`;
  - `excluded_non_skill_context`;
  - `ambiguous`.
- Ambiguous skill-domain source usage blocks author submission before destination write and blocks independent Stage21 verification.
- Non-skill domain terms retain required per-occurrence enforcement.
- Producer evidence records `domain`, `applicability`, `context`, required/excluded/ambiguous occurrence counts, and zero-based source line indexes.
- Independent verifier re-parses terminology authorities and re-derives context evidence; it does not import `kb_creator` producer helpers.
- Stage21 verifier exact-compares the producer `TERMINOLOGY.qa.json`, candidate inventory, QA, provenance, assets, and assembled `MASTER_RU`.
- No production script literals for `Dissociation`, `dissociation`, `unit-000`, `Passantino`, `Пасс`, `Пилотирование`, or scenario-specific unit identity were found. `Pilot` appears in tests/fixtures only.

## Tests and probes run

Commands:

```powershell
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI'
& 'C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe' -m py_compile kb_creator\scripts\scenario_master_ru.py kb_creator\scripts\verify_scenario_master_ru.py kb_creator\tests\test_scenario_master_ru.py kb_creator\tests\test_verify_scenario_master_ru.py
& 'C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe' -m pytest -q kb_creator\tests\test_scenario_master_ru.py kb_creator\tests\test_verify_scenario_master_ru.py
```

Result:

- `32 passed, 1 skipped, 23 subtests passed in 5.69s`

Additional smoke:

```powershell
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI'
& 'C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe' -m pytest -q kb_creator\tests\test_publication_registry_e2e.py
```

Result:

- `6 passed in 15.78s`

Independent adversarial probes:

- Producer and verifier both classified the following as `required_skill`:
  - `Skills: Pilot 40%`
  - `A successful Pilot roll reveals the route.`
  - `Pilot (Aircraft) 60%`
- Producer and verifier both classified the following as `excluded_non_skill_context`:
  - `Occupations: Pilot, Teacher`
  - `Names: Pilot, Guide`
  - `He is a sea-plane charter pilot, hired by the vessels.`
  - `History and geology students camped nearby.`
- Producer and verifier both classified the following as `ambiguous`:
  - `Pilot, Teacher`
  - `Pilot approaches the hangar.`
- Producer and verifier both rejected explicit CSV-vs-CSV domain conflict for the same source/target:
  - producer: `MasterRuError conflicting terminology domain: Pilot`
  - verifier: `MasterRuVerificationError conflicting terminology domain: Pilot`

## Findings

### P0

None.

### P1

None.

### P2-1: Classifier scope is intentionally English-source and bounded

Evidence:

- The classifier recognizes English structural labels and bounded English syntax such as `Skills`, `Occupations`, `Names`, `roll`, `check`, `hired as`, `students`, and similar patterns.
- Unrecognized source prose remains `ambiguous` and therefore fail-closed.

Impact:

- This is not a blocker for the current MASTER_EN/MASTER_RU flow because the source packets are English and ambiguous cases are rejected before publication.
- Future non-English source packets or new semantic fields may need deliberate classifier extension and tests rather than relying on implicit behavior.

Remediation:

- No remediation required before the next fresh Dissociation publication run.
- For any future source language or semantic field, add generic classifier cases and adversarial tests before allowing that authority/domain to pass.

## Recommendation

GO for a fresh publication run using this remediation.

Conditions:

- Do not resume or mutate any previously sealed run whose implementation identity predates this change.
- Start a fresh publication run so the Stage20/Stage21 implementation identity, packet manifest, submission validation, `TERMINOLOGY.qa.json`, and independent verifier evidence are sealed under the current scripts.
- Continue requiring explicit user acceptance for the fresh `MASTER_RU` candidate; this review does not accept any candidate text or release artifact.

Rationale:

- The implementation preserves terminology domain metadata, enforces required skill translations only in bounded skill contexts, excludes occupation/name/profession uses, and fails closed on ambiguous occurrences.
- Producer and verifier rederive the same evidence independently and exact-compare sealed terminology QA.
- Focused tests, registry smoke, and independent probes passed.
- No Dissociation/unit-specific production hard-coding was found.

## Next action

- Proceed with a fresh absent publication run from the accepted reconstruction and current config/glossary authorities.
- Migrate translation text only into the fresh Stage20 batch shapes, then run `scenario_master_ru author-submission` and Stage21 verification under the new implementation identity.
