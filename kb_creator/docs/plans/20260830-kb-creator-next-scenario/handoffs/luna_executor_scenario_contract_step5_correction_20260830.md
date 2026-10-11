# Luna executor receipt — ScenarioContract.v1 Step 5 correction

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `5-scenario-contract-implementation-correction`
- Role: bounded executor
- Policy model / effort: `gpt-5.6-luna` / `medium`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; policy role honored
- Scoped override: `none`
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch: `codex/kb-creator-viral`
- Base / HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Timestamp: `2026-08-30T23:33:32.5901212+03:00`
- Runtime-goal time at pre-receipt checkpoint: `897` seconds
- Runtime-goal token count at pre-receipt checkpoint: `203794`

## Result

The rejected first Luna candidate was corrected against the accepted amendment.
The six-path product candidate now has an evidence-explicit, non-runtime
Innsmouth `compatibility_shadow`; a closed runtime Viral contract; duplicate-key
and strict JSON-type rejection; frozen/raw canonicalization; exact policy,
acceptance, artifact, exception and anti-bypass rules; and a verifying source
resolution API that rejects shadows before filesystem access.

Focused ScenarioContract acceptance is green. Step 5 cannot yet be declared
fully accepted because the prescribed collectable Innsmouth family is red on
pre-existing/missing working fixtures and active-checkout CRLF bytes, and the RU
verifier's required authoritative glossary file is absent. These blockers were
not improvised around and are outside the six-path correction allowlist.

No runtime wiring, source copy, PDF parsing, configurable DAG, build, freeze,
OCR, translation, rendering, generated output, accepted/production mutation,
Git index/history mutation, commit, or push was performed.

## Reviewed immutable inputs

- Amendment:
  `handoffs/sol_architect_scenario_contract_step5_remediation_20260830.md`
  - required SHA-256: `211134E8BB2A642BC9E61B1670BD07894B68A2F2E134030A9058CC7395A8A58F`
  - verified SHA-256 before edits: `211134E8BB2A642BC9E61B1670BD07894B68A2F2E134030A9058CC7395A8A58F`
- Independent amendment review:
  `handoffs/gpt55_critic_scenario_contract_step5_remediation_review_20260830.md`
  - required SHA-256: `D81B5A277DB1CAA020A586ADD05605F2BEF4BF476D2508A998620A8A1EA923B8`
  - verified SHA-256 before edits: `D81B5A277DB1CAA020A586ADD05605F2BEF4BF476D2508A998620A8A1EA923B8`
  - recommendation: `accept`; no P0/P1/P2 findings

The fixed architecture, active `plan.md` and `context.md`, governance, every
current goal packet/receipt, existing Innsmouth verifier code, reconstruction
constants, accepted manifests, and production manifest were read before edits.
The first Luna implementation and receipt were treated only as rejected
evidence.

## Material paths

The complete authorized candidate surface remains exactly:

1. `.gitattributes`
2. `kb_creator/contracts/scenario_contract.v1.schema.json`
3. `kb_creator/contracts/innsmouth.json`
4. `kb_creator/contracts/viral.json`
5. `kb_creator/scripts/scenario_contract.py`
6. `kb_creator/tests/test_scenario_contract.py`

Content corrected in this task: paths 2–6. Path 1 already contained the exact
accepted rule from the rejected candidate and was deliberately left byte-identical:
`kb_creator/inputs/**/*.html text eol=lf`, exactly one occurrence.

This receipt is the only additional write and is a governance handoff, not a
seventh product path. No other material path was edited.

### Before / after material identities

| Path | Before correction SHA-256 | After correction SHA-256 | After bytes |
|---|---|---|---:|
| `.gitattributes` | `943503F18B58DF37D7E33A29C44A1364A86D6B187978D2964A303B2B4A5D9F9D` | same | 622 |
| schema | `147312D3BB4E42650A77B4AD130799E4455D550432A45165D32E14785B776D86` | `25BF02364D4CE16E7D7DA96BD3E6B41D0E36B3642224F0989589B2335C5C07F2` | 13426 |
| Innsmouth shadow | `E4A9DB3C18FA36DD95018C2D16D45CF8E78D2F3B57501326943DFAD59BEF19C3` | `56E3B89B474CC466EBF6C84B8797E3D9AC56E34AD2B2294235415A073C98AD60` | 3137 |
| Viral runtime | `83E20610351299B2F6A0C53090A1E74A92E5DE33DDA9ED9FA38021D006AFDF00` | `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D` | 4582 |
| validator/API | `0F502DC5897C0CE089A01CC1CD704E0F076EFC2EA4FA9873BF5CCA8CC5ADBDF3` | `51DFFCF62D0DFD41716FCD0B1330E9C6FF82A3A81A0578FB57B49BC34708C6F3` | 23157 |
| tests | `F2D8A6F8C0B9338FEC0FFD04D13DAC1525AFA689D3563D1BDFB1A6244D2265BB` | `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3` | 18252 |

The three contract files are ignored by the repository's catch-all
`.gitignore:2:*`; therefore ordinary `git status`/`git diff` cannot enumerate
them. Their existence and before/after content identities were audited directly.
No `.gitignore` change or Git staging was authorized or performed.

## Contract and evidence closure

### Innsmouth compatibility shadow

- `contract_role=compatibility_shadow`.
- All unavailable raw-PDF locator/hash/bytes/page-count/base/geometry/rotation
  fields are required and exactly JSON `null`.
- `scope=null`, `page_roles=[]`, `policies=null`, `acceptance=null`, and
  `exceptions=[]` are mandatory.
- Closed compatibility evidence uses only:
  - reconstruction control PDF hash from
    `kb_creator/scripts/build_innsmouth_reconstructed_en.py`:
    `5850B26A077390ABFF4A321E754A3709D6148FA4AC7A9F4D63BDBEFF6949B1BB`;
  - retained reconstructed Markdown candidate hash:
    `1504A9C71CA995748E4125B7303C0D3064E588ABB226EBB5AB99A5F5763C993C`;
  - reconstructed Markdown marker domain `0..45`, count `46`;
  - accepted reconstructed Markdown `138426` bytes /
    `8F5A35B6FBE545691EEF66C52A848F0F04776A247CCAAF40B16140FEB0C543BF`;
  - reconstructed QA `75179` bytes /
    `8C351053E49AE3546BCA5857394DDCCBA2FF60AE05DA75C03ACB47E076B06DA9`;
  - `136` assets / inventory
    `B6F9BF00B01DB09ED06723871B97B424206C5A79EB624C8F5768A847B1CE3B39`;
  - exact four-entry accepted-stage manifest map from
    `kb_creator/inputs/innsmouth/production/PRODUCTION_MANIFEST.json`.
- Manifest evidence rechecked after correction:
  - MASTER_EN acceptance: `AD9A6546EB7421F4387A4E6B547B2CD6B61346A3B326D25110A56028FC919B83`;
  - MASTER_RU acceptance: `B87C34F312258FB349B6AE549A398637096CE3A29D9B623EEDA28D5ECF4EC384`;
  - HTML acceptance: `F3A6EC483858060B46EB266893FEE7D4AE4F63D3A9A0A26CCB899D5903B4375A`;
  - PDF acceptance: `5861569529394C8B04BD7903B1BD07C420812AD63DC1C669F7CA4E11E40E0154`;
  - production manifest: `40DEB53603F1D4E14769C236663015B125C88EFA62F6F57CC61FBFC6FDBDF103`.

Shadow rejection evidence: `compatibility_shadow` validation passes; `intake`
rejects; `reconstruction_ready` rejects; source resolution rejects before any
filesystem probe. The dedicated rejection test passed.

### Viral runtime contract

Exact retained facts: source SHA-256
`0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`,
`20718150` bytes, `124` pages, `[612,792]` pt, rotation `0`, full scope
`1..124`, `39` numbered handouts, reviewed role ranges, pages `1..5` with
intake-only `unknown` content modes, and stable `Viral_RU.html` /
`Viral_RU.pdf` names. Translation lineage is only
`accepted_current_master_en`; historical sources are
`terminology_or_comparison_only`.

The six policy domains, exact ordered acceptance gates/authorities, artifact
vocabulary/suffixes, exception selector/evidence objects, allowed
kind/stage/operation triples, overlap rule, and anti-bypass closure are enforced
by both the closed schema artifact and semantic validation where cross-field
logic is required.

## Canonicalization and source-resolution evidence

- Viral raw/frozen canonical equality: `true`; canonical SHA-256
  `C2EF2DD143E304F59C8973E8DB82CF83B094BC35DDA37BB2299686E1FE6DA194`.
- Innsmouth raw/frozen canonical equality: `true`; canonical SHA-256
  `46D10BE6B4D639AAE0C28CDF510E7CB96B3DB66CE1FB98190E2FCB95532B523E`.
- Canonical JSON is UTF-8, key-sorted, compact, newline-free, and has no
  runtime path.
- Duplicate top-level and nested JSON keys reject during loading.
- Boolean-as-integer, non-finite geometry, untrimmed/control strings and all
  other strict type classes in the amendment's negative matrix reject.
- `resolve_source_path(contract, runtime_path, *, observed_page_count,
  observed_media_box_points, observed_rotation_degrees)` validates a runtime
  intake contract, rejects a shadow first, requires a regular file, streams and
  checks byte count/SHA-256, checks every caller-supplied observation, and only
  then returns the resolved path.
- Dedicated source-resolution matrix: `10 passed` (positive plus shadow-first,
  missing path, directory, byte mismatch, hash mismatch, missing observation,
  page mismatch, geometry mismatch, rotation mismatch); contract digests were
  unchanged after success and failure.
- No PDF parser or runtime builder consumes this API in this slice.

## Tests

### Focused contract suite

Command:

`python -B -m pytest kb_creator/tests/test_scenario_contract.py -q -p no:cacheprovider`

Result: exit `0`; `119 passed in 0.21s`.

Collect-only command:

`python -B -m pytest kb_creator/tests/test_scenario_contract.py --collect-only -q -p no:cacheprovider`

Result: exit `0`; `119 tests collected in 0.04s`.

The matrix covers both roles/profiles, exact Viral and Innsmouth evidence,
closed schema branches, duplicate keys, strict bool/int/finite/string checks,
missing/extra fields, source/scope/role/geometry/hash negatives, artifact
safety/suffix/version/placeholder/case-insensitive duplication, complete role
coverage, policy and acceptance closure, every exception class and anti-bypass
shape, canonicalization, shadow rejection, and all source-resolution cases.

An optional direct `jsonschema` execution diagnostic exited `1` only because
the environment has no `jsonschema` module. No dependency was added: the
accepted correction explicitly requires stdlib semantic enforcement and treats
the schema as an interchange artifact. Schema JSON parsing and branch-closure
tests are green.

### Full-suite baseline diagnostic

Command:

`python -B -m pytest kb_creator/tests -q -p no:cacheprovider`

Result: exit `1`; collection stopped with exactly the known `15` errors:
missing `kb_creator.pdf_raw.page_proof`, `kb_creator.pdf_raw.errors`, and
`kb_creator.pdf_raw.raw_authority_projection` across the same page-proof and
raw-authority families recorded by the amendment. Comparison with baseline:
exact error count and missing-module classes match; no new collection or test
failure was introduced by the correction. The full suite is not reported green.

### Collectable Innsmouth family

The prescribed regex selected `13` files (nonempty). Command:

`python -B -m pytest @innsmouthTests -q -p no:cacheprovider`

Result: exit `1`; `82 passed, 14 skipped, 14 failed in 7.52s`.

The failures are outside ScenarioContract and fall into two pre-existing
environment/fixture classes:

1. missing ignored working candidates
   `kb_creator/working/innsmouth_direct_html/accepted_20260830_candidate_r11/The_Innsmouth_Terror_RU.html`
   and `kb_creator/working/innsmouth_direct_master_ru/MASTER_RU.md`;
2. active-worktree CRLF materialization causing accepted/production HTML byte
   identity failures.

Neither missing fixture was present in the retained LF probe. Creating/copying
them or editing the existing test/scripts would exceed the six-path allowlist,
so no substitution or rebaseline was attempted.

## Existing verifier authority

All CLIs were first inspected with `--help` and real required arguments were
used.

- EN command:
  `python -B kb_creator/scripts/verify_innsmouth_master_en_repo_input.py --root kb_creator/inputs/innsmouth/master_en/accepted_20260830_r6`
  - exit `0`; `INNSMOUTH_ACCEPTED_MASTER_EN_REPO_INPUT_OK`
  - 36 files, 33 assets, 9505373 bytes, inventory
    `E1665ED05CE8C19443DB98D02D0FA9B2A957EA2C34114E438217DE95DB26CB8B`.
- RU command:
  `python -B kb_creator/scripts/freeze_innsmouth_master_ru_repo_input.py --verify --glossary <required glossary> --master-en-root kb_creator/inputs/innsmouth/master_en/accepted_20260830_r6 --target kb_creator/inputs/innsmouth/master_ru/accepted_20260830_r6`
  - exit `1` before verification because required
    `docs/terminology/CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md` is absent from this
    worktree, retained probe, and exact-name workspace search;
  - no substitute glossary was inferred or created.
- PDF command:
  `python -B kb_creator/scripts/freeze_innsmouth_pdf_repo_output.py --verify --html-root kb_creator/inputs/innsmouth/html/accepted_20260830_r6 --target kb_creator/inputs/innsmouth/pdf/accepted_20260830_r7`
  - exit `0`; `INNSMOUTH_ACCEPTED_PDF_REPO_OUTPUT_OK`;
  - manifest `7890` bytes /
    `5861569529394C8B04BD7903B1BD07C420812AD63DC1C669F7CA4E11E40E0154`;
  - PDF `11557577` bytes /
    `6883AE5D15FB498477239B98B3D278E458223EACA1691B3C73EB17F987D5E0E5`,
    36 pages, 45/45 exact heading landings.
- HTML retained-probe command used the probe script with explicit probe
  `--master-ru-root` and `--target` paths.
  - exit `0`; `INNSMOUTH_ACCEPTED_HTML_REPO_INPUT_OK`;
  - manifest `7208` bytes /
    `F3A6EC483858060B46EB266893FEE7D4AE4F63D3A9A0A26CCB899D5903B4375A`;
  - 32 assets; inventory
    `849C8238A9165EADC8A796B6A2501C84E9CD220F303CD70E46940FAF6C1E3019`.
- Production retained-probe command:
  `python -B D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\scripts\build_innsmouth_production_package.py --verify --target D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\inputs\innsmouth\production`
  - exit `0`; `INNSMOUTH_PRODUCTION_PACKAGE_VERIFY_OK`;
  - 70 files, 33 assets, manifest
    `40DEB53603F1D4E14769C236663015B125C88EFA62F6F57CC61FBFC6FDBDF103`,
    inventory
    `9A44C69454F243C8717C0A7B41FC34F99A8ABFE440653311090FDB1A084C5E71`.

## LF probe

Retained probe: `D:\NRI\_scenario_contract_lf_probe_20260830_d`.

For both accepted HTML and production HTML:

- `git check-attr`: `text: set`, `eol: lf`;
- `git ls-files --eol`: `i/lf w/lf attr/text eol=lf`;
- index blob: `327c4f2a2d30468f8895213b295324e2457af67b`;
- raw bytes: `226114`;
- raw SHA-256:
  `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`.

The active accepted/production/source status check remained empty. No accepted,
production, source, manifest, or Git blob was mutated.

## P2 and scope audits

- `rg` over only `kb_creator/scripts`, `kb_creator/contracts`, and
  `kb_creator/tests` for `(build|freeze)_viral_.*\.py`: exit `1`, no match.
- Same surface search for
  `translator[\\/]config[\\/]viral\.package\.json|viral\.package\.json`:
  exit `1`, no match. The test constructs the forbidden name in split literals
  solely to assert absence from both contracts; there is no executable or
  config dependency.
- `git diff --check`: exit `0`; only Git's existing CRLF checkout warning for
  `.gitattributes`, no whitespace error.
- `git diff --name-only`: `.gitattributes`; explicit allowed-path diff confirms
  only the one LF rule against HEAD. Untracked/ignored allowed paths were
  audited by direct identity as recorded above.
- Before status: branch `codex/kb-creator-viral`; `.gitattributes` modified;
  goal documentation, validator and test file untracked; contracts ignored.
- Pre-receipt post status: the same ownership classes and no new product path
  outside the six-path allowlist. Existing goal documents were preserved.
- No accepted/production/source status entry; no commit and no push.

## Blockers and next action

Blockers to full Step 5 acceptance:

1. Restore or explicitly supply the authoritative glossary required by the RU
   verifier, without modifying this correction candidate.
2. Provide the established ignored Innsmouth working candidates in an approved
   disposable QA environment, then rerun the 13-file collectable family under
   LF materialization. Do not copy them into this worktree without separate
   authority.
3. The known 15 missing `kb_creator.pdf_raw` collection errors remain a
   separate repository baseline and prevent a full-suite green claim.

Recommended next action: main-chat orchestration verifies this receipt and
candidate hashes, resolves the two QA-fixture inputs above, reruns bounded QA,
then assigns a fresh independent implementation review. Source reconstruction
and publication remain blocked until Step 5 QA/review acceptance.

Receipt SHA-256 is intentionally detached; compute it after this final write.
