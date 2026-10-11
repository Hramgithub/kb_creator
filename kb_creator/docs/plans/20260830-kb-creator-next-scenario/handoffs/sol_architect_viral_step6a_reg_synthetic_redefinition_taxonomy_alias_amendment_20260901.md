# Viral Step 6A REG synthetic-redefinition, taxonomy, and alias amendment

## Receipt metadata and authority

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-reg-synthetic-redefinition-taxonomy-alias-amendment`.
- Role: architecture/root-cause only, policy `gpt-5.6-sol` / `high`; actual platform model/effort `unavailable`; assignment state `platform-unverified`; scoped override `explicit synthetic REG redefinition only`.
- Orchestrator policy owner remains the root/main chat, policy `gpt-5.6-sol` / `medium`; canonical plan/context/status, integration, dispatch, stop/ask, and user-facing ownership do not transfer.
- Result: `amendment_ready_for_fresh_independent_architecture_review`; implementation remains blocked pending the gate below.
- Timestamp: `2026-09-01T09:44:18+03:00` (Europe/Moscow). Elapsed time and token use: `unavailable`.
- Sole changed path: this absent-before immutable amendment. No code, test, candidate, source, recovery, protected, plan, context, project-status, Git, cache, live, promotion, or release path was changed.

This amendment binds and supersedes only the stopped REG clauses identified in
`sol_architect_viral_step6a_reg_historical_specimen_clarification_20260901.md`,
SHA-256 `F713704F12293AFA15BB0856D9680EA73755C9C85E03EC8D57C90CAA6928604D`.
The accepted parent packet remains bound at
`32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`.
The frozen current baseline is:

- library `kb_creator/scripts/scenario_source_reconstruction.py` — `34943D5E0008A01A1F3AFC3AF2D49091F06049187AE9D0CB7DA02654663862D4`;
- focused tests `kb_creator/tests/test_scenario_source_reconstruction.py` — `D3FA871BBA3DED04ECD216544B7A9A7EEECB95D4769DDF45612B412990F9D192`;
- accepted QAV-D2 correction — `32A714D453F4A895866267A8F47879DE554A53581E272A7908C3F92D695FC268`.

## Explicit redefinition and decision

`REG-P1-stale-metadata` is redefined as a **synthetic deterministic regression cluster derived independently from each fresh valid fixture**. It is not the lost historical QA-v2 file, is not evidence of historical bytes, and must never carry the historical raw-file hash `FE142A...` as its identity. Its inventory rows intentionally retain the fresh fixture's current bytes/hashes. This redefinition is an explicit orchestrator-selected replacement for the unavailable historical-byte specimen; it does not claim to reconstruct that specimen.

The minimal coherent shared taxonomy is accepted for review as follows:

1. retain the frozen shared phase-5 QA predicate in its current shape-first order;
2. root closed-shape mismatch remains `E_SHAPE_QA` for every family;
3. only a shape-complete wrong QA schema reaches `E_SCHEMA_QA`;
4. retire the REG expectation `E_QA_SCHEMA`; that code is not introduced anywhere;
5. the synthetic cluster deliberately removes the required top-level
   `recovery_evidence_sha256` key, so its canonical earliest outcome is
   `E_SHAPE_QA`, before its wrong schema or any phase-6/7/8 inconsistency;
6. family, case id, callable identity, audit identity, pytest identity, or an alias table must never enter `_strict_verify` or influence code selection.

This is shared taxonomy, not REG-specific routing. Existing
`SCH-QA-schema-wrong -> E_SCHEMA_QA` and QA missing-member cases
`-> E_SHAPE_QA` remain canonical.

## Exact synthetic QA transformation

### Admission and derivation

Each invocation starts from a newly created valid production-shaped TEST fixture that passes the ordinary factory validity check. No prior mutated fixture, live candidate, historical file, external source, or serialized synthetic fixture may be reused. Load the fixture's root `RECONSTRUCTED_EN.qa.json`, deep-copy it as `before`, and apply exactly the following final-state transformation:

1. set `schema` to exact literal `kb_creator.reconstructed_en_qa.v2`;
2. set `recovery_manifest_sha256` to
   `C32CCA2A85F8123A2BE9E015FB39642943E31FCD723FA466FA436F454B344C3A`;
3. remove exactly the top-level key `recovery_evidence_sha256`;
4. set `open_blocker_count` to integer `3`;
5. set `counts.open_blockers` to integer `3` — this amendment chooses an internally aligned synthetic QA summary, while the unchanged fixture ledger remains at four and would fail only at a later phase;
6. from the fresh fixture's exact 501-row `output_inventory`, remove exactly one row for each contact-sheet path `renders/contact_sheets/sheet-001.png` through `sheet-031.png`; retain all other 470 row objects without changing their `path`, `bytes`, or uppercase `sha256`, then order the retained complete records by ordinal path order;
7. set `output_inventory_count` to integer `470`;
8. recompute `output_inventory_sha256` as `manifest_digest(filtered_rows)`, i.e. SHA-256 over 470 UTF-8/LF records
   `path<TAB>bytes<TAB>UPPERCASE_SHA256<LF>` with a final LF;
9. preserve exact canonical rule literal
   `every regular file recursively present under candidate root except root-level RECONSTRUCTED_EN.qa.json`;
10. preserve `state=candidate_needs_review`;
11. preserve every other QA field and nested value exactly from the fresh valid fixture.

The mutator must first assert 501 unique current rows, exactly the 31 named sheet rows, no other `renders/contact_sheets/` row, 470 retained unique rows, ordinal order after filtering, `output_inventory_count == len(output_inventory) == 470`, and the recomputed uppercase 64-hex digest. Any failed assertion is a fixture-construction stop, not a verifier success.

The canonical rule intentionally describes the physical candidate rather than the stale synthetic array. If phase 5 were bypassed—which is forbidden—phase 6 would reject the omitted live sheet rows. The test proves earliest phase-5 shape authority; it does not weaken inventory authority or normalize the rule.

All 470 retained records are **synthetic current-fixture records**. Even where a path overlaps the old 470-path set, its bytes/hash are not claimed to be historical. The recomputed 470-record digest is fixture-derived audit evidence, not the historical digest and not a production constant.

### Exact case binding and pointer audit

- Case id: `REG-P1-stale-metadata`.
- Family: `REG`.
- Semantic selector: `candidate/RECONSTRUCTED_EN.qa.json#`.
- Declared reseal tuple: `()`.
- Expected and observed earliest code: `E_SHAPE_QA`.
- `strict_verify_calls=1`; `outside_fixture_reads=0`; `changed_by_reseal=[]`; `undeclared_changes=[]`; `residue=[]`; `result=PASS`.
- `semantic_before_sha256` and `semantic_after_sha256` are uppercase SHA-256 over the selected canonical QA-root bytes before and after the exact fixture-local transformation. They must differ and must be independently recomputed in the audit.

For this parent-authorized multi-field case, `changed_before_reseal` contains exactly the following 38 stable logical selectors, in the order shown. Path-key row selectors use the same inventory-selector convention already accepted for INV/QAV audits; they do not depend on shifting numeric array indices.

```text
candidate/RECONSTRUCTED_EN.qa.json#/schema
candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256
candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256
candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count
candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-001.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-002.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-003.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-004.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-005.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-006.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-007.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-008.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-009.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-010.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-011.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-012.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-013.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-014.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-015.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-016.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-017.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-018.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-019.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-020.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-021.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-022.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-023.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-024.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-025.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-026.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-027.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-028.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-029.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-030.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-031.png
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count
candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256
```

The rule and state selectors are absent from this delta because their values are preserved, not rewritten to a different value. The parent 16-field audit object remains closed; this exact 38-entry list is the deliberate multi-field exception to the ordinary one-selector rule.

## Exact missing-enforcement binding

`REG-P1-missing-enforcement` is:

| Field | Exact binding |
|---|---|
| semantic selector | `candidate/evidence/COMMANDS.json#/counts/pages` |
| before / after | integer `124` -> integer `125` (`old + 1`) |
| direct mutation | change only `COMMANDS.counts.pages` |
| declared reseal tuple/order | `(INVENTORY, QA)` |
| expected/observed code | `E_COMMAND_COUNTS_PAGES` |
| verifier calls / reads | `1` / `0` outside fixture |

Inventory and QA reseals may change only their declared transport selectors; they must not repair `COMMANDS.counts.pages`. The phase-8 shared COMMANDS count loop reaches `pages` first and emits the exact code. This REG case uses a distinct case id, callable object/name, fresh fixture, semantic hashes, and audit row from `CMD-count-pages-wrong`.

## Exact alias ceiling supersession

The accepted five-pair ceiling is superseded only to **exactly six cross-family identical-state pairs / twelve members**:

1. `SCH-QA-required-top-member-missing` <-> `QAV-top-asset_count-missing`;
2. `SCH-qa-unexpected-top-member` <-> `QAV-top-extra`;
3. `INV-cardinality-wrong` <-> `QAV-inventory-count-wrong`;
4. `INV-digest-wrong` <-> `QAV-inventory-digest-wrong`;
5. `INV-ordinary-row-missing` <-> `QAV-inventory-array-wrong`;
6. `CMD-count-pages-wrong` <-> `REG-P1-missing-enforcement`.

Every member has a distinct callable object/name, fresh fixture, case id, and audit row. Physical selector/mutation/reseal/final state/code match only within its declared pair. The synthetic stale cluster is not an alias member because its complete 38-selector final state is unique. The alias table is test/audit evidence only and is never passed to production or test `_strict_verify`.

No seventh alias pair is permitted. A discovered seventh identical-state collision, callable reuse, or any need for family-aware verifier routing is an immediate stop requiring a new architecture amendment/review.

## Counts and prior evidence

No node is added or removed. Only the two already-counted REG identities gain real explicit mutation callables and corrected authority:

- `REG=2`;
- selector-specific negatives `368`;
- distinct case ids `368`;
- distinct mutation callable objects/names `368`;
- `BLD=3`;
- focused total `371`.

The accepted QAV-D2 correction remains valid for its four cases, INV/QAV outcomes, count evidence, and first five aliases. This amendment supersedes only “exactly five/no sixth” with the six-pair table above. The old REG `E_QA_SCHEMA` registry expectation and any proxy/generic REG callable are invalid for the current baseline and must be replaced; no prior receipt proves the new synthetic cluster. Current SCH/QAV phase-5 receipts remain historical bounded evidence and require the targeted current-baseline reruns below, not retroactive rewriting.

## Terra implementation boundary

Implementation is blocked until the fresh independent architecture gate below accepts this exact artifact and SHA. After acceptance, Terra's entire write allowlist is exactly:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. absent-before `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_reg_20260901.md`.

The library may change only if needed for a reusable case/audit primitive that preserves shared verifier behavior; no production phase order, schema/shape predicate, inventory authority, graph, COMMANDS, public route, or writer semantics may change. If tests alone plus the receipt suffice, the library hash must remain exact and be reported as unchanged. No fourth path is permitted.

Candidate, source/recovery, CLI, protected 119 tests, prior receipts, plan/context/status, Git, cache, live material, promotion, publication, and release paths remain read-only. No live preflight/verify/build/remediate is authorized in this Terra batch.

## Exact acceptance commands and evidence

All commands use `python -B` and `-p no:cacheprovider`. Terra must capture native exit codes and SHA-256 of UTF-8 stdout/stderr streams without writing logs.

```powershell
$reg = @(
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[REG-P1-stale-metadata]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[REG-P1-missing-enforcement]'
)
python -B -m pytest @reg -q -p no:cacheprovider

$taxonomy = @(
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[REG-P1-stale-metadata]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[SCH-QA-schema-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[SCH-QA-required-top-member-missing]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-top-recovery_evidence_sha256-missing]'
)
python -B -m pytest @taxonomy -q -p no:cacheprovider

$aliases = @(
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[SCH-QA-required-top-member-missing]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-top-asset_count-missing]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[SCH-qa-unexpected-top-member]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-top-extra]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[INV-cardinality-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-inventory-count-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[INV-digest-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-inventory-digest-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[INV-ordinary-row-missing]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-inventory-array-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[CMD-count-pages-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[REG-P1-missing-enforcement]'
)
python -B -m pytest @aliases -q -p no:cacheprovider

python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -k 'test_bld_' -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider

$retired = rg -n 'E_QA_SCHEMA' kb_creator/scripts/scenario_source_reconstruction.py kb_creator/tests/test_scenario_source_reconstruction.py
if ($LASTEXITCODE -eq 0) { throw "retired REG taxonomy remains: $retired" }
if ($LASTEXITCODE -ne 1) { throw 'retired-code search failed' }
```

Required native results are `2 passed`, `4 passed`, `12 passed`, `3 passed` for BLD, exactly `371 tests collected`, and retired-code search exit `1` with empty output. Registry inspection must prove the exact counts and six-pair table, all twelve distinct callable identities/names, the synthetic cluster outside the alias table, and no verifier route input.

The two-row REG case-audit stream is exactly:

```text
REG-P1-stale-metadata<TAB>candidate/RECONSTRUCTED_EN.qa.json#<TAB><TAB>E_SHAPE_QA<TAB>E_SHAPE_QA<TAB>PASS<LF>
REG-P1-missing-enforcement<TAB>candidate/evidence/COMMANDS.json#/counts/pages<TAB>inventory,qa<TAB>E_COMMAND_COUNTS_PAGES<TAB>E_COMMAND_COUNTS_PAGES<TAB>PASS<LF>
```

It is 224 UTF-8 bytes and has SHA-256
`73A0B02AFC715AFA1EBC738FB2241329C76752342E67916A5376FC9659A43F4C`.
Terra must also recompute the parent-format full 368-row audit digest, not carry it forward. The receipt includes both complete 16-field REG audit objects, the stale object's exact 38-selector delta, its fixture-local 470-record digest and independent recomputation, all six alias pairs, pre/post material hashes, exact path delta, native command evidence, and zero outside-fixture reads/undeclared changes/residue.

## Fresh review and downstream boundaries

Before Terra writes, a fresh independent `gpt-5.5` / `high` architecture critic, with no implementation/material-design/QA participation, must write only absent-before
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reg_synthetic_redefinition_taxonomy_alias_amendment_review_20260901.md`.
It must verify this amendment's raw SHA, the clarification and frozen hashes, exact synthetic transform, 38-selector audit, shape-first outcome, absence of REG routing, missing-enforcement mutation, six-pair ceiling, counts, commands, and three-path scope. Terra admission requires `ACCEPT` with no unresolved P0/P1; any P2 requires explicit orchestrator resolution.

After Terra, separate bounded QA (`gpt-5.6-luna` / `high`) independently inspects actual code and runs the affected groups, full focused 371, protected 119, combined 490, and read-only live preflight plus deterministic verify twice, proving protected/candidate/cache identities unchanged. A fresh independent `gpt-5.5` / `high` implementation/process critic then reviews the frozen implementation and QA with no unresolved P0/P1/P2. This architect is not the final release reviewer. Semantic acceptance, `MASTER_EN`, promotion, release, publication, staging, commit, and push remain separate and unauthorized.

## Risks, acceptance criteria, stop conditions, and next action

Primary risks are accidentally claiming historical bytes, carrying historical row hashes into the synthetic array, omitting a sheet selector from the audit, allowing array index shifts to hide rows, changing the canonical rule, allowing shape validation to occur after schema, reintroducing `E_QA_SCHEMA`, sharing the CMD/REG callable, failing to declare the sixth alias, or feeding test identity into the verifier.

Acceptance requires all of the following:

- one fresh valid fixture per invocation and the exact fixture-local transform;
- exactly 31 named sheet rows removed, exactly 470 unchanged current records retained, count/digest recomputed and checked twice, rule/state preserved;
- exact 38-selector direct delta, empty reseals for stale cluster, and exact `E_SHAPE_QA` after one shared verifier call;
- missing-enforcement `124 -> 125`, `(INVENTORY, QA)`, exact `E_COMMAND_COUNTS_PAGES`;
- exactly six alias pairs/twelve distinct identities and no seventh;
- `REG=2`, negatives `368`, BLD `3`, focused `371` unchanged;
- all commands/audits/digests pass with zero residue and only the exact three-path scope;
- downstream QA and independent implementation/process criticism remain open.

Stop before first Terra write on any bound hash drift, absent/rejecting review, inability to derive the exact 501-row fresh fixture, noncanonical rule, pre-existing Terra receipt, or required fourth path. Stop after first write with a truthful blocked receipt on any wrong id/selector/value/reseal/code/order, fewer/more than 31 sheet removals, non-470 array, digest mismatch, historical-byte claim, `E_QA_SCHEMA`, schema-first or family-aware routing, shared callable, seventh alias, count drift, multiple verifier calls, outside-fixture read, undeclared change, residue, out-of-scope/live/protected/candidate/Git/cache mutation, or any weakening of production enforcement.

Next action: seal this amendment's SHA, obtain the fresh independent `gpt-5.5` / `high` architecture verdict, and dispatch Terra only after an exact `ACCEPT` and unchanged baselines.

## Files checked read-only

- `AGENTS.md`, `docs/governance/nri_goal_governance.md`, assigned plan/context.
- Accepted parent packet/review, injection authority, SCH/QAV and INV/QAV amendments/reviews, QAV-D2 correction.
- Historical clarification SHA `F713...`, frozen library/test, current REG registry, QA shape predicate, inventory algorithm, CMD pages callable, and alias evidence.

