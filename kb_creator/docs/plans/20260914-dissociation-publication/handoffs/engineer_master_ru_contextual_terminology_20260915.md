# Engineer receipt: contextual MASTER_RU terminology

Date: 2026-09-15  
Scope: generic Stage20 submission validation and independent Stage21 terminology verification  
Result: implemented and focused regression green

## Root cause

Both `scenario_master_ru` and the independent verifier validated the shared CSV header, including its existing `domain` column, but discarded `domain` while parsing. They then treated every lexical source-term occurrence as requiring the glossary target. Consequently a skill authority such as `source term -> skill translation` was incorrectly applied to occupations, names, and ordinary meanings of the same English word.

## Implementation

- CSV `domain` is now retained as explicit authority metadata. JSON terminology may optionally provide the same generic metadata. The strict Markdown skills table contributes an implicit `skill` domain; an explicit CSV/JSON domain wins over a compatible implicit table classification, while conflicting explicit domains fail closed.
- Terms outside the `skill` domain retain the existing per-occurrence enforcement.
- Each skill occurrence is independently classified from source structure and bounded local syntax:
  - `required_skill`: skill/ability field, roll/check/test/percentage/mechanics context;
  - `excluded_non_skill_context`: occupation/profession/career/name/role/cast field, bounded occupational attribution, or academic-field use;
  - `ambiguous`: no authoritative positive or exclusion context.
- A required occurrence must contain an accepted Russian variant and no declared bad variant. Excluded occurrences do not demand the skill translation. Any ambiguous occurrence produces `terminology_context_ambiguous` and blocks author-submission before destination publication.
- Producer evidence now records `domain`, `applicability`, and a prose-free context record containing occurrence counts and zero-based source line indexes. Stage21 seals this under `TERMINOLOGY.qa.json` and the candidate inventory.
- `verify_scenario_master_ru.py` independently parses domains and independently rederives the same context evidence without importing producer helpers. It rejects ambiguous context or a missing required skill target and still verifies exact producer terminology evidence.
- No contract/schema/config/glossary change was necessary. Existing `packet_policy` and submission schema remain unchanged; implementation inventory changes provide the freshness boundary.

The reusable implementations contain no Dissociation, unit-id, source-sentence, or individual-term constants.

## Read-only run04 audit

The current run04 packet authorities and translated batches were read only. Across 50 merged skill-domain terms, 12 source unit matches were found:

- 9 `required_skill` matches;
- 3 `excluded_non_skill_context` matches;
- 0 ambiguous matches;
- 0 producer/verifier classification disagreements;
- 0 required targets missing from the corrected Russian batches.

The two reported occupation uses in units 00032 and 00069 are both excluded. The remaining excluded match is an academic-field use. Statblock and prose mechanics matches remain required.

## Files and identities

- `kb_creator/scripts/scenario_master_ru.py`: 50,560 bytes; SHA-256 `54C4A0DFA28D31C69F0E6BAABF1DE28DE758FF9C7F5B0361FF3381357A34CD19`
- `kb_creator/scripts/verify_scenario_master_ru.py`: 41,398 bytes; SHA-256 `515BBC51025B8CFB63E806035D8B38587A3D665669E970EF4F4090183B730B31`
- `kb_creator/tests/test_scenario_master_ru.py`: 26,806 bytes; SHA-256 `48DA0CC5CC2A0D947F21D8FAC770A23A102CAAF9A27C373C4DCCDAE32D435535`
- `kb_creator/tests/test_verify_scenario_master_ru.py`: 13,002 bytes; SHA-256 `DE6DA0349F517EEB38EE4AC330CCFAF53F697EFB6465E34AB839B1C9AF234A91`

## Tests

Runtime: repository CPython 3.12 plus existing flat pytest dependencies; nothing installed.

- `py_compile` for both implementations and both focused test modules: pass.
- `pytest -q kb_creator/tests/test_scenario_master_ru.py kb_creator/tests/test_verify_scenario_master_ru.py`: `32 passed, 1 skipped, 23 subtests passed`.
- `pytest -q kb_creator/tests/test_publication_registry_e2e.py`: `6 passed`.
- Adversarial coverage includes: skill target required; occupation and name fields excluded; bounded occupational prose excluded; percentage/statblock skills required; plain prose and unlabeled lists ambiguous/fail-closed; explicit/implicit domain binding; producer/verifier evidence parity; author no-write failure; independent Stage21 rejection.
- `git diff --check` on the four owned implementation/test paths: pass.

No OCR, MinerU, CPU/GPU provider, network, live publication, acceptance, commit, or push command was run. Run03/run04 outputs and submissions, source, configs, contracts, glossaries, and canonical project documents were not modified.

## Migration / next execution

1. Do not resume or mutate run04: its sealed implementation identity predates this change.
2. Start a fresh absent publication run with the same accepted reconstruction and unchanged config/glossary authorities; reproduce Stage10 and obtain the required fresh explicit MASTER_EN acceptance.
3. Generate a fresh Stage20 packet. Migrate translation text only into its exact fresh ordered batch shapes; do not reuse run04 submission identities.
4. Run canonical `scenario_master_ru author-submission`. It should now accept the occupation translations while continuing to enforce every required skill occurrence.
5. Validate the sealed submission read-only, resume once to Stage21, and require the exact producer QA plus independent verification before any user acceptance.

## Findings

- P0/P1: none in the focused implementation and registry matrix.
- P2: the contextual vocabulary is intentionally bounded and English-source oriented. A future source language or new semantic field not covered by the declared glossary domain must remain ambiguous/fail-closed until the generic classifier is deliberately extended with tests.
- Blockers: none.
