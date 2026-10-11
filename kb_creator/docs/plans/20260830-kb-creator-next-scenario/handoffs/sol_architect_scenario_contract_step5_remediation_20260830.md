# Step 5 scenario-contract remediation specification and architect receipt

Status: **architecture remediation proposed; material correction not yet authorized**  
Goal: `20260830-kb-creator-next-scenario`  
Step: `5-scenario-contract-implementation-remediation`  
Role: `nri-architect`  
Policy model / effort: `gpt-5.6-sol` / `high`  
Orchestrator policy owner: main chat, `gpt-5.6-sol` / `medium`  
Assignment state: matched by `nri-architect` role  
Scoped override: none  
Worktree: `D:\NRI\.worktrees\kb-creator-viral`  
Timestamp: `2026-08-30T22:22:43+03:00` (`Europe/Moscow`)  

## Decision

Use an **evidence-explicit, non-runtime Innsmouth compatibility shadow** in the existing `kb_creator/contracts/innsmouth.json` path.

The shadow proves only what current accepted Innsmouth evidence actually proves. It does not claim to identify, locate, or describe an authoritative raw source PDF. Every unavailable raw-PDF identity, page-count, and geometry fact is represented by JSON `null`, never by a positive placeholder and never by the SHA-256 of a different artifact. The validator accepts this document only under the explicit `compatibility_shadow` profile. Intake, reconstruction-ready, canonical runtime resolution, build, freeze, and release use must reject it before filesystem access.

Existing accepted Innsmouth packages, manifests, freeze verifiers, and production verifiers remain the authorities for Innsmouth behavior. The shadow is descriptive regression evidence only and must never become an upstream or runtime authority.

### Options considered

| Option | Benefit | Failure mode | Decision |
|---|---|---|---|
| Evidence-explicit compatibility shadow in the existing Innsmouth contract path | Preserves the two-scenario compatibility comparison and exact accepted-output evidence without inventing a raw source | Requires one narrow schema/API branch and explicit runtime rejection | **Selected** |
| Remove full contract validation for Innsmouth and test only Viral | Smallest validator surface | Loses the fixed architecture's compatibility objective and no longer proves that the shared boundary can represent legacy accepted state without mutating it | Rejected |
| Substitute the locally found `The Innsmouth terror.pdf` | Supplies real byte/page/geometry values | Its SHA-256 is `CFD72DD3B8702C07750DCBB9F721A704793D6D474167B288922E6F7EBEEA561F`, not the control identity recorded by the reconstruction code | Rejected |
| Use the retained Markdown candidate SHA as `source.sha256`, or retain `1` placeholders | Avoids nullable fields | Misidentifies Markdown as a PDF and turns unknown source facts into false facts | Rejected |
| Store only the reconstruction code's control-PDF SHA as a complete runtime source | Preserves one exact hash | The corresponding PDF bytes are absent from authoritative current inputs; byte count, raw page count, geometry, and a resolvable source are unproven | Rejected |

## Architecture classification

This is a **narrow amendment** to the fixed scenario-contract architecture, not a redesign:

- The original candidate required a complete `external_pdf` identity for every contract/profile. Live evidence proves that this cannot be stated truthfully for the Innsmouth compatibility document.
- The amendment adds one categorical top-level role, `compatibility_shadow`, and one validation profile of the same name.
- The seven-stage runtime graph, Viral's complete-source rules, build/freeze/verify identities, stable artifact names, translation lineage, visual/text/OCR policies, and release gates remain unchanged.
- The shadow branch is deliberately terminal: it describes evidence but contributes no nodes or edges to the runtime stage graph.
- This receipt does not modify the fixed architecture candidate. A fresh independent `gpt-5.5` architecture review must accept this amendment before any material correction begins.

## Root cause and severity

The rejected implementation conflated three different identities:

1. the unavailable Innsmouth reconstruction control PDF;
2. a retained reconstructed Markdown candidate with SHA-256 `1504A9C71CA995748E4125B7303C0D3064E588ABB226EBB5AB99A5F5763C993C`;
3. a locally available library PDF with a different SHA-256.

It then filled unknown raw-PDF facts with positive values (`byte_count=1`, `page_count=1`, one-point geometry, one-page scope). That crossed the executor packet's stop condition and made the validator capable of accepting fabricated authority.

Correction priorities:

| Priority | Required correction |
|---|---|
| P0 | Remove every false Innsmouth source fact; introduce the non-runtime shadow role/profile; make runtime APIs reject it; make source resolution verify bytes, hash, and required caller-supplied PDF observations; reject duplicate JSON keys and Boolean-as-integer values. |
| P0 | Close the exception model so no exception can skip identity, acceptance, source disposition, generated-only, inventory, or release gates; reject overlap and ambiguous selectors. |
| P1 | Close artifact keys and suffixes, policy profiles/strategies, acceptance gates/authorities, page-role values and modes, exact list uniqueness/order, frozen-view canonicalization, and the full negative matrix. |
| P2 | Retain the scoped LF rule/probe evidence and the no-copied-Viral-script / no-translator-runtime-reference searches. These do not block schema correction but do block final Step 5 acceptance if absent. |

## Allowed Innsmouth facts

Only facts grounded in current code, accepted manifests, or accepted packages may appear in the shadow.

### Source object

`innsmouth.json` must use this exact semantic shape:

```json
{
  "contract_role": "compatibility_shadow",
  "source": {
    "kind": "external_pdf",
    "identity_status": "incomplete",
    "locator_hint": null,
    "sha256": null,
    "byte_count": null,
    "page_count": null,
    "page_number_base": null,
    "media_box_points": null,
    "rotation_degrees": null
  },
  "scope": null,
  "page_roles": [],
  "policies": null,
  "acceptance": null,
  "exceptions": []
}
```

All listed keys are required. `null` is the only valid value for unavailable source and runtime-policy facts in a shadow. Omission, `0`, `1`, empty string, an all-zero hash, the retained Markdown candidate hash, the local-library PDF hash, or the reconstruction code's control-PDF hash in `source.sha256` must fail validation.

The shadow may retain the already established exact `scenario_id`, display name, language declaration, and stable artifact names: `RECONSTRUCTED_EN.md`, `MASTER_EN.md`, `MASTER_RU.md`, `The_Innsmouth_Terror_RU.html`, `The_Innsmouth_Terror_RU.pdf`, and `PRODUCTION_MANIFEST.json`. Artifact names are compatibility expectations, not proof that the shadow is runtime authority.

### Compatibility evidence

Add a required, closed top-level `compatibility_evidence` object to the shadow branch and forbid it on runtime contracts. It must contain only these evidence classes:

- `control_pdf_sha256`: the exact SHA-256 constant read from `build_innsmouth_reconstructed_en.py`, `5850B26A077390ABFF4A321E754A3709D6148FA4AC7A9F4D63BDBEFF6949B1BB`, labeled as an unavailable control identity. This value must never populate `source.sha256`.
- `retained_markdown_candidate_sha256`: the exact retained Markdown candidate identity already checked by the reconstruction script, `1504A9C71CA995748E4125B7303C0D3064E588ABB226EBB5AB99A5F5763C993C`. It must be labeled `retained_markdown_candidate`, not `external_pdf`.
- `reconstructed_page_marker_domain`: `{ "base": 0, "first": 0, "last": 45, "count": 46 }`, explicitly typed as reconstructed Markdown page-marker evidence. It is not `source.page_count` and supplies no source geometry.
- `accepted_reconstructed_evidence`: the exact source evidence embedded by the accepted MASTER_EN manifest: reconstructed Markdown `138426` bytes / `8F5A35B6FBE545691EEF66C52A848F0F04776A247CCAAF40B16140FEB0C543BF`; reconstructed QA `75179` bytes / `8C351053E49AE3546BCA5857394DDCCBA2FF60AE05DA75C03ACB47E076B06DA9`; asset count `136` / inventory SHA-256 `B6F9BF00B01DB09ED06723871B97B424206C5A79EB624C8F5768A847B1CE3B39`.
- `accepted_stage_manifests`: the following exact closed four-entry map, copied from the production manifest's `source_packages` record:

  | Key | Root | Manifest | Bytes | SHA-256 |
  |---|---|---|---:|---|
  | `master_en` | `inputs/innsmouth/master_en/accepted_20260830_r6` | `MASTER_EN.acceptance.json` | 1320 | `AD9A6546EB7421F4387A4E6B547B2CD6B61346A3B326D25110A56028FC919B83` |
  | `master_ru` | `inputs/innsmouth/master_ru/accepted_20260830_r6` | `MASTER_RU.acceptance.json` | 4075 | `B87C34F312258FB349B6AE549A398637096CE3A29D9B623EEDA28D5ECF4EC384` |
  | `html` | `inputs/innsmouth/html/accepted_20260830_r6` | `HTML.acceptance.json` | 7208 | `F3A6EC483858060B46EB266893FEE7D4AE4F63D3A9A0A26CCB899D5903B4375A` |
  | `pdf` | `inputs/innsmouth/pdf/accepted_20260830_r7` | `PDF.acceptance.json` | 7890 | `5861569529394C8B04BD7903B1BD07C420812AD63DC1C669F7CA4E11E40E0154` |
- `authority`: the exact enum `existing_accepted_manifests_and_verifiers`.
- `runtime_authority`: the exact Boolean `false`.

The schema and semantic validator must reject any filesystem locator, build instruction, runtime source override, inferred page geometry, approval flag, or gate-bypass field inside `compatibility_evidence`.

These are the only accepted-package identities authorized in the shadow. The executor must stop rather than abbreviate, infer, normalize, substitute, or expand them into a second production manifest.

## Runtime contract invariants

### Topology and profiles

Add required top-level `contract_role` with exactly two values:

- `runtime`: eligible for `intake` validation; eligible for `reconstruction_ready` only when every page is classified and every runtime invariant passes.
- `compatibility_shadow`: eligible only for `compatibility_shadow`; categorically ineligible for all runtime operations.

Profile behavior must be fail closed:

| Document role | `compatibility_shadow` | `intake` | `reconstruction_ready` | source resolution |
|---|---:|---:|---:|---:|
| `runtime` | reject | validate complete source and intake modes | validate complete source and reject any `unknown` page mode | verify file and observations, then return path |
| `compatibility_shadow` | validate null/evidence-only shape | reject | reject | reject before filesystem access |

No implicit profile selection from filename is allowed. `load_contract` may select the semantic validation branch from `contract_role`, but public validation and source resolution must require or enforce the profile appropriate to the requested operation.

### Viral facts that must not drift

`viral.json` remains a `runtime` contract and must preserve all fixed exact facts:

- scenario id `viral`;
- immutable external PDF SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
- byte count `20718150`;
- `124` English Letter pages;
- the fixed Letter media box and zero-rotation declaration already in the candidate/packet;
- full scope covering pages 1 through 124;
- the fixed page-role partition and the exact role/mode/trait declarations already in the candidate;
- pages 1 through 5 remain `unknown` at intake, so `intake` passes and `reconstruction_ready` fails;
- exact stable artifact names, including `Viral_RU.html` and `Viral_RU.pdf`;
- new Russian translation from the accepted current `MASTER_EN`; historical translations are terminology/comparison evidence only and never translation source;
- all-page text, OCR, visual, asset-closure, navigation, HTML, PDF, and release evidence requirements from the fixed architecture.

No correction may classify Viral pages 1 through 5, copy or rename an Innsmouth script family, read an old Russian translation as source, render/build/OCR/translate, or introduce a configurable DAG.

### Exact artifact vocabulary

Both schema and semantic validation must require exactly these six keys and no others:

- `reconstructed_en`
- `master_en`
- `master_ru`
- `html`
- `pdf`
- `production_manifest`

Values must be trimmed, nonempty, basename-only strings; reject `/`, `\\`, `..`, drive/URI prefixes, control characters, leading/trailing whitespace, duplicate names, accepted/date/release version suffixes, and placeholders. Require suffixes: `.md` for reconstructed and both masters, `.html` for HTML, `.pdf` for PDF, and `.json` for the production manifest. Viral's exact names are `RECONSTRUCTED_EN.md`, `MASTER_EN.md`, `MASTER_RU.md`, `Viral_RU.html`, `Viral_RU.pdf`, and `PRODUCTION_MANIFEST.json`. Innsmouth names must equal the currently accepted stable names read from its manifests, not invented aliases.

### Closed policy vocabulary

Keep the fixed six-domain policy topology, but close each domain to the minimum values already proven by Viral. Require all six domains and no extras:

| Domain | Exact v1 fields/values |
|---|---|
| `reconstruction` | `strategies`: unique nonempty subset of `embedded_text`, `reading_order`, `ocr_region`, `visual_preserve`; `required_review: true` |
| `publication` | `strategies: ["reading_order"]`; `required_review: true` |
| `translation` | `strategies: ["reading_order"]`; `lineage_source: accepted_current_master_en`; `historical_source_mode: terminology_or_comparison_only`; `required_review: true` |
| `visual` | `strategies: ["visual_preserve"]`; `required_review: true` |
| `navigation` | `strategies: ["reading_order"]`; `required_review: true` |
| `render` | `strategies: ["visual_preserve"]`; `profile: viral_print`; `required_review: true` |

`viral_print` is the only v1 render profile because it is the only new-scenario profile proven in scope; adding another requires review. Reject executable fields, commands, script paths, tool selection, stage ordering, arbitrary environment data, and any profile/strategy outside these enums. `policies` is required and non-null only for runtime contracts; it is exactly `null` in a shadow.

### Closed acceptance vocabulary

Require exactly six stage records and no extras. Gate lists are exact ordered lists for contract v1, not extensible subsets:

| Stage | Exact gates | Exact authority |
|---|---|---|
| `reconstructed_en` | `source_identity`, `page_coverage`, `role_partition`, `text_ocr_provenance`, `required_entity_closure`, `asset_closure`, `no_open_blockers` | `configured_reconstruction_review` |
| `master_en` | `accepted_reconstructed`, `source_disposition`, `semantic_navigation`, `handout_mapping`, `table_statblock_closure`, `asset_closure`, `no_technical_reader_noise` | `explicit_user_reading_acceptance` |
| `master_ru` | `accepted_master_en_lineage`, `structural_parity`, `terminology`, `untranslated_terms`, `links`, `asset_closure` | `explicit_user_reading_acceptance` |
| `html` | `accepted_master_ru`, `deterministic_output`, `links`, `assets`, `unique_ids`, `generated_only`, `navigation` | `explicit_user_visual_navigation_acceptance` |
| `pdf` | `accepted_html`, `print_only_delta`, `render_coverage`, `no_blank_pages`, `destinations`, `section_boundaries`, `full_visual_qa`, `generated_only` | `explicit_user_print_acceptance` |
| `production` | `accepted_packages`, `closed_inventory`, `stable_names`, `asset_union`, `contract_schema_code_snapshots`, `qa_closure` | `explicit_production_snapshot_acceptance` |

Every record is closed. Reject missing, extra, duplicated, reordered, or unknown gates; reject arbitrary authority strings. `acceptance` is required and non-null only for runtime contracts; it is exactly `null` in a shadow. These declarations describe gates; they do not grant acceptance.

### Page-role taxonomy and strict types

Preserve the fixed primary roles only: `cover`, `credits`, `front_matter`, `contents`, `scenario_body`, `player_handouts`, `keeper_maps`, `pregenerated_investigators`, `back_cover`. Preserve the fixed content modes only: `text`, `mixed`, `visual`, `unknown`. Preserve the fixed traits only: `multi_column`, `low_text`, `zero_text`, `table_heavy`, `statblock`, `form_like`. Preserve the fixed named strategies only: `embedded_text`, `reading_order`, `ocr_region`, `visual_preserve`.

Require:

- exact JSON integer types for every count/index; Boolean is not an integer;
- finite JSON numbers for geometry; Boolean, NaN, and infinity fail;
- page-role ranges sorted, gap-free, non-overlapping, and exactly covering runtime scope;
- each trait/mode list unique; each language list unique;
- exact runtime publication language order `en`, `ru`;
- `unknown` permitted only by `intake` and rejected by `reconstruction_ready`;
- all objects closed and all arrays checked for duplicates where duplicates are meaningless.

### Exception anti-bypass model

Exceptions remain a finite data repair mechanism, never a gate waiver. Replace free-form selectors/evidence with closed objects.

Each exception must contain exactly:

```json
{
  "id": "safe-kebab-id",
  "stage": "master_en",
  "kind": "publication_suppression",
  "operation": "suppress_exact_block",
  "scope": {
    "pages": [42],
    "selector": { "kind": "block_id", "value": "block-42-a" }
  },
  "expected_matches": 1,
  "rationale": "Trimmed, substantive rationale.",
  "evidence": [
    { "kind": "source_page", "ref": "source:42" },
    { "kind": "review_receipt", "ref": "handoffs/example.md" }
  ],
  "approval": "required"
}
```

Allowed selector kinds: `exact_text`, `block_id`, `heading_id`, `asset_id`, `page_boundary`. Allowed evidence kinds: `source_page`, `review_receipt`, `accepted_manifest`. Selector/evidence values must be trimmed, nonempty strings. Evidence records must be unique. IDs must be unique safe kebab identifiers. `scope.pages` must be a sorted unique nonempty integer list inside runtime scope. `expected_matches` is the exact integer `1`. `approval` is exactly `required`.

Allowed kind/stage/operation triples are closed:

| Kind | Allowed stage(s) | Exact operation |
|---|---|---|
| `text_repair` | `reconstructed_en` | `replace_exact_text` |
| `reading_order` | `reconstructed_en` | `reorder_exact_blocks` |
| `list_continuation` | `reconstructed_en` | `continue_numbering` |
| `publication_suppression` | `master_en` | `suppress_exact_block` |
| `semantic_link` | `master_en`, `html` | `retarget_exact_reference` |
| `asset_owner` | `master_en`, `master_ru`, `html` | `relocate_exact_asset_owner` |
| `render_placement` | `html`, `pdf` | `apply_named_placement` |
| `page_break` | `pdf` | `insert_page_break_before_heading` |

Reject overlapping exceptions when two records have the same stage and `scope.selector` kind/value and their `scope.pages` sets intersect. Reject any field or operation suggesting `skip`, `ignore`, `waive`, `allow_extra`, `manual_edit`, `accepted_upstream`, source substitution, output mutation, inventory bypass, or release approval. Closed objects plus the exact triple table are both required; substring filtering alone is insufficient. Shadows require an empty exception array.

## Authorized corrections by material path

The material correction allowlist remains exactly six paths. No seventh product/config/module/test path is authorized.

### 1. `.gitattributes`

- Preserve exactly one scoped rule: `kb_creator/inputs/**/*.html text eol=lf`.
- Do not add repository-wide text/EOL rules and do not renormalize unrelated files.
- If the exact rule is already present once, this path requires no content change.

### 2. `kb_creator/contracts/scenario_contract.v1.schema.json`

- Add the required `contract_role` discriminator and conditional `runtime` versus `compatibility_shadow` branches using closed `$defs`/`oneOf` or an equivalently unambiguous draft-2020-12 structure.
- Close exact artifact keys and suffix patterns.
- Close enums and shapes for page roles, modes, traits, policy domains/profiles/strategies, acceptance stages/gates/authorities, exception triples/selectors/evidence, and compatibility evidence.
- Model complete runtime source facts as non-null required values and shadow source facts as required nulls.
- Require all declared top-level keys in both branches; forbid branch-inapplicable content.
- Keep this a declarative schema only. Do not encode a configurable DAG or executable behavior.

### 3. `kb_creator/contracts/innsmouth.json`

- Convert the rejected pseudo-runtime contract into the compatibility shadow specified above.
- Remove `1` placeholders and the Markdown SHA from the PDF source identity.
- Copy only full exact evidence values from the inspected reconstruction script and accepted/production manifests.
- Preserve existing accepted artifact names and scenario metadata.
- Do not add a source path or point to the local library PDF.

### 4. `kb_creator/contracts/viral.json`

- Add `contract_role: runtime` and conform policy/acceptance/exception shapes to the closed v1 vocabulary.
- Preserve every fixed Viral source fact, page-role range, role/mode/trait, artifact name, language rule, and intake-only unknown mode.
- Do not classify pages 1 through 5 and do not add a runtime path.

### 5. `kb_creator/scripts/scenario_contract.py`

- Load JSON with an `object_pairs_hook` that rejects duplicate keys at every nesting level.
- Reject Boolean where an integer/number is required; reject non-finite numbers and untrimmed strings.
- Enforce all semantic invariants that JSON Schema alone cannot reliably express: exact coverage/order, exact acceptance lists, kind/stage/operation mappings, exception overlap, exact artifact uniqueness/safety, profile-role compatibility, and anti-bypass rules.
- Support immutable loaded views by recursively thawing `Mapping`/tuple values for validation and canonical serialization. `canonical_contract_bytes(load_contract(...))` must work and equal canonicalization of the equivalent raw mapping.
- Keep canonical JSON deterministic, newline-free, UTF-8, key-sorted, and independent of runtime filesystem paths.
- Change source resolution to a verification boundary with this semantic API:

  ```python
  resolve_source_path(
      contract,
      runtime_path,
      *,
      observed_page_count,
      observed_media_box_points,
      observed_rotation_degrees,
  ) -> Path
  ```

  It must first require a valid runtime `intake` contract, reject a shadow before filesystem access, require a regular file, stream and compare byte count and SHA-256, then compare all required caller-supplied PDF observations to the contract. Missing or mismatched observations fail. The function returns a resolved path only after every check succeeds.
- Do not add a PDF parser in this slice. The observations are an explicit future inspector dependency; tests supply them. Do not add build, freeze, render, OCR, translation, manifest emission, or stage execution.

### 6. `kb_creator/tests/test_scenario_contract.py`

Expand the same test file; do not add another test module. The required matrix is below.

## Required test matrix

### Positive and identity cases

- Schema parses and declares draft 2020-12; representative branch objects are structurally closed.
- Viral exact source hash/bytes/pages/Letter geometry/rotation, scope, roles, names, policies, and gates.
- Viral passes `intake`; unchanged Viral fails `reconstruction_ready` only because pages 1 through 5 are `unknown`.
- A test-local deep copy with only the fixed unknown modes resolved passes `reconstruction_ready`; the repository contract must not be edited to create it.
- Innsmouth passes only `compatibility_shadow`; all its unavailable raw-source fields are exactly null; evidence identities equal authoritative files.
- Raw and frozen-view canonical bytes and SHA are equal; input key order is irrelevant; runtime path is absent from the digest.
- A temporary runtime source with exact observed bytes/hash/page/geometry/rotation resolves successfully.

### Structural and type negatives

- Duplicate JSON keys at the top level and in nested objects fail loading.
- Missing/extra top-level and nested fields fail.
- Boolean in every integer/number class fails; zero/negative counts fail; invalid hash case/length/characters fail; NaN/infinity fail.
- Invalid scenario id, language order/duplicates, source kind/status, page base, geometry, rotation, scope, and contract-role/profile combinations fail.
- Artifact missing/extra keys, duplicate names, wrong suffix, path separator, traversal, drive/URI prefix, control character, whitespace, versioned name, and placeholder fail.

### Page and policy negatives

- Page-role gap, overlap, out-of-order range, outside-scope range, duplicate trait/mode, unknown role/mode/trait, and incorrect full coverage fail.
- `unknown` remains valid in intake and fails reconstruction-ready; no test may weaken that rule.
- Missing/extra policy domains and fields, wrong profile, invalid/duplicate strategy, false review, wrong translation lineage/historical mode, and executable fields fail.
- Missing/extra acceptance stages and fields, missing/extra/reordered/duplicate/unknown gate, and wrong/free-form authority fail.

### Exception negatives

- Duplicate id; unsafe id; empty/short/untrimmed rationale; missing/duplicate/unknown evidence; empty/untrimmed `scope.selector`; invalid page; duplicate/unsorted `scope.pages`; Boolean/zero/multiple expected matches; wrong approval all fail.
- Every invalid kind/stage/operation combination fails.
- Same-selector overlapping page exceptions fail; demonstrably disjoint page sets may pass.
- Attempted operations/fields for identity bypass, skipped gates, extra files, manual output edits, upstream acceptance, source substitution, inventory waiver, or release approval fail.
- Any nonempty shadow exception list fails.

### Source-resolution negatives

- Shadow rejection occurs before probing a nonexistent runtime path.
- Missing path, directory path, byte mismatch, hash mismatch, missing observation, page mismatch, geometry mismatch, and rotation mismatch fail without returning a path.
- Contract identity remains unchanged after successful and failed resolution.

## Dependencies and boundary

The correction may use only the Python standard library and existing repository test tooling. JSON Schema is an interchange artifact; semantic enforcement remains in `scenario_contract.py` because no new runtime schema-validator dependency is authorized.

The source-resolution boundary depends on a future trusted PDF-inspection caller for observed page count, media box, and rotation. That caller is intentionally outside this slice. Until it exists, no runtime build may claim reconstruction readiness from this API. This is a fail-closed dependency, not permission to infer observations.

The compatibility shadow depends only on static evidence already present in current code/manifests. It must not be imported by Innsmouth build/freeze/verify scripts. Existing scripts and accepted manifests continue to define and verify accepted Innsmouth behavior.

## Executor stop conditions

Stop without editing further and report the blocker if any of the following occurs:

- a full authoritative Innsmouth value cannot be copied directly from an inspected current script or accepted/production manifest;
- a proposed value requires inferring raw-PDF bytes, raw page count, geometry, rotation, or locator;
- any correction would require a seventh material path, a new dependency, a PDF parser, a configurable DAG, or build/render/OCR/translation behavior;
- an accepted/production/source/translator file would need to change;
- Viral's exact source facts, role ranges, stable names, translation direction, or intake-only unknown state would change;
- existing Innsmouth accepted tests/verifiers would need to be weakened, skipped, or rebaselined because of the contract;
- runtime code would import or treat the compatibility shadow as authority;
- the LF correction would require broad renormalization or accepted-file mutation;
- a fresh independent review has not accepted this remediation specification.

## Acceptance procedure

### Prerequisite independent review

Before material correction, obtain a new immutable `gpt-5.5` independent architecture review of this receipt. The review must explicitly decide the shadow/profile amendment, null representation, runtime rejection, source-resolution observation boundary, exception anti-bypass table, and six-path allowlist. `accept_with_conditions` is sufficient only if every P0 condition is incorporated into the executor packet before editing.

### Correction allowlist and diff audit

After review, the executor may change only:

```text
.gitattributes
kb_creator/contracts/scenario_contract.v1.schema.json
kb_creator/contracts/innsmouth.json
kb_creator/contracts/viral.json
kb_creator/scripts/scenario_contract.py
kb_creator/tests/test_scenario_contract.py
```

The executor also writes one immutable receipt, not a seventh product path:

```text
kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_scenario_contract_step5_correction_20260830.md
```

Run and record:

```powershell
git status --short
git diff --check
git diff --name-only
git diff -- .gitattributes kb_creator/contracts/scenario_contract.v1.schema.json kb_creator/contracts/innsmouth.json kb_creator/contracts/viral.json kb_creator/scripts/scenario_contract.py kb_creator/tests/test_scenario_contract.py
```

Any material path outside the six-item allowlist is a hard failure. Preserve other agents' existing changes and do not revert them.

### Contract tests

```powershell
python -B -m pytest kb_creator/tests/test_scenario_contract.py -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py --collect-only -q -p no:cacheprovider
```

Both commands must exit zero. The receipt records the collected and passed counts.

The repository-wide test command remains a required diagnostic:

```powershell
python -B -m pytest kb_creator/tests -q -p no:cacheprovider
```

At architecture inspection time it stopped during collection with 15 pre-existing `kb_creator.pdf_raw` import errors in page-proof/raw-authority/Step-5-non-live families. The six-path correction is not authorized to create those missing modules or alter those tests. The executor must record the fresh full-suite result and compare it with this baseline; no new collection or test failure is allowed, and the full suite must not be falsely reported green.

Run the collectable Innsmouth regression family independently from the missing-module families:

```powershell
$innsmouthTests = Get-ChildItem kb_creator/tests -File | Where-Object { $_.Name -match '^(test_(build|freeze)_innsmouth|test_innsmouth_)' } | ForEach-Object { $_.FullName }
python -B -m pytest @innsmouthTests -q -p no:cacheprovider
```

The command must exit zero and its exact file/test counts must be recorded. An empty `$innsmouthTests` list is a hard failure.

### Existing verifier authority

Run the existing Innsmouth EN, RU, and PDF verify modes read-only against their currently accepted roots using each script's documented required arguments. Run HTML and production verification in the retained disposable LF probe, because the active checkout's accepted HTML currently retains CRLF worktree bytes while the scoped `.gitattributes` rule materializes the canonical LF blob. Do not edit an accepted file merely to make a verifier green.

At minimum record the exact commands, exit codes, resolved accepted roots/manifests, manifest hashes, inventory counts, and output identities. If a verifier's CLI contract differs from the architecture packet, use `--help`, document the exact current CLI, and stop if satisfying it would mutate accepted state.

### LF probe

Preserve exactly:

```gitattributes
kb_creator/inputs/**/*.html text eol=lf
```

In a disposable clean-index probe, prove that both accepted HTML and production verification succeed against the LF materialization, and record:

- `Innsmouth_Terror_RU.html` byte count `226114`;
- SHA-256 `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`;
- zero accepted/production/source changes in the active worktree.

If the retained probe cannot be shown clean and scenario-scoped, recreate a disposable probe without modifying accepted state; do not commit it.

### P2 anti-copy searches

```powershell
rg -n --glob 'kb_creator/scripts/**' --glob 'kb_creator/contracts/**' --glob 'kb_creator/tests/**' '(build|freeze)_viral_.*\.py'
rg -n --glob 'kb_creator/scripts/**' --glob 'kb_creator/contracts/**' --glob 'kb_creator/tests/**' 'translator[\\/]config[\\/]viral\.package\.json|viral\.package\.json'
```

Both searches must return no runtime/config dependency or copied Viral script family. Test/doc mentions used only to assert absence must be classified explicitly; any executable reference is a hard failure.

### Contract-specific evidence

The correction receipt must also record:

- canonical SHA-256 of raw and frozen Viral contract views, proving equality;
- canonical SHA-256 of raw and frozen Innsmouth shadow views, proving equality;
- shadow rejection results for intake, reconstruction-ready, and source resolution;
- source-resolution positive and every negative observation case;
- all full Innsmouth evidence values and their authoritative source paths;
- exact Viral source identity/page/geometry/scope/role/artifact assertions;
- no mutation of accepted/production/source trees, preferably with before/after status and hashes for the referenced manifests;
- no commit or push.

## Risks and unresolved decisions

1. **Future Innsmouth runtime onboarding:** a real runtime contract remains impossible until the exact authoritative PDF bytes are located and independently inspected. That is outside this goal; do not promote the shadow.
2. **PDF observation provider:** the remediation defines the verifier boundary but not a PDF parser. A later bounded design must choose the trusted inspector and normalization rules before any runtime builder consumes `resolve_source_path`.
3. **JSON Schema execution:** no schema runtime dependency is added here. If later consumers need direct schema execution, dependency selection and schema/semantic conformance tests require separate approval.
4. **Accepted HTML CRLF worktree state:** the scoped LF rule is proven by a disposable probe, but safe active-worktree rematerialization remains a separate operation. Do not mutate accepted bytes in this slice.
5. **Full-suite missing modules:** the 15 collection errors are pre-existing and outside this six-path correction. They prevent a repository-wide green claim; focused and collectable-regression evidence is therefore mandatory.
6. **Compatibility evidence verbosity:** accepted-package evidence is intentionally finite and closed. Do not expand it into arbitrary provenance or a second manifest system.

## Rejected extensions

- a scenario-specific Viral build/freeze script family;
- a generic configurable workflow/DAG engine;
- runtime use of `translator/config/viral.package.json`;
- importing historical Russian text as translation source;
- source copying, rendering, OCR, translation, or release production in this step;
- modifying accepted/production artifacts to satisfy line-ending checks;
- auto-approving exceptions or acceptance gates;
- changing existing Innsmouth verifier authority to the shadow.

## Receipt

### Scope and result

Read-only root-cause and architecture analysis of the rejected Step 5 implementation. Result: a concrete fail-closed remediation is specified for the same six material paths. No implementation, generated output, source processing, accepted mutation, Git mutation, commit, or push was performed.

### Files checked

- `D:\NRI\AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_scenario_contract_20260830.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_scenario_contract_architecture_review_20260830.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_scenario_contract_implementation_packet_20260830.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_scenario_contract_implementation_20260830.md`
- `.gitattributes`
- `kb_creator/contracts/scenario_contract.v1.schema.json`
- `kb_creator/contracts/innsmouth.json`
- `kb_creator/contracts/viral.json`
- `kb_creator/scripts/scenario_contract.py`
- `kb_creator/tests/test_scenario_contract.py`
- `kb_creator/scripts/build_innsmouth_reconstructed_en.py`
- current Innsmouth freeze/verifier scripts for MASTER_EN, MASTER_RU, HTML, PDF, and production
- current Innsmouth accepted and production manifests/config-like artifacts referenced by those scripts
- `translator/config/viral.package.json` read-only as legacy evidence, not authority
- local `The Innsmouth terror.pdf` identity/page/geometry observation supplied to this task, treated as non-authoritative because its hash mismatches the control hash
- `C:\Users\BogdanD\.codex\memories\MEMORY.md` quick registry search; no memory-derived project fact was used as current authority

### Only file changed

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_scenario_contract_step5_remediation_20260830.md`

### Verification performed

- Compared the current schema, validator, contracts, and tests with the fixed architecture and engineering packet.
- Confirmed the Innsmouth false-positive source fields and the Markdown/PDF identity category error.
- Confirmed the current validator does not verify resolved file hash/bytes/pages/geometry, does not reject duplicate JSON keys, accepts Boolean through ordinary integer checks, cannot canonically serialize its frozen view, and under-enforces policy/acceptance/exception closure.
- Confirmed the current test matrix is substantially smaller than the fixed negative matrix.
- Confirmed the scoped LF rule and retained probe evidence recorded by the executor packet/receipt; no accepted file was changed here.
- Confirmed the design retains Viral intake-only unknown-mode behavior and exact stable RU HTML/PDF names.
- Final read-only verification confirmed the receipt exists, `git diff --check` reports no whitespace error for it, and the worktree still contains broader pre-existing/unowned Step 5 changes. The initial managed-shell attempt returned an environment-level `UnsupportedOperation`; the same checks succeeded through the approved read-only Windows backend.

### Blockers

- Material correction is blocked pending fresh independent `gpt-5.5` review of this amendment.
- Full repository test acceptance is independently blocked by the pre-existing missing `kb_creator.pdf_raw` modules; the correction must not conceal or broaden into that problem.
- Exact authoritative Innsmouth raw PDF identity remains unavailable; that is why the shadow must remain non-runtime.

### Next action

Main-chat orchestrator assigns an independent `gpt-5.5` review of this immutable receipt. After an acceptable decision, issue a bounded executor packet implementing only the six-path allowlist and requiring the immutable correction receipt named above.

### Time and token accounting

- Elapsed architect work: approximately 70 minutes including evidence inspection and remediation drafting.
- Token use: unavailable to this role; no precision invented.
- Self SHA-256: cannot be embedded in the hashed file without changing its own bytes. Compute and record the detached SHA-256 after this immutable write in the orchestrator state/review receipt.
