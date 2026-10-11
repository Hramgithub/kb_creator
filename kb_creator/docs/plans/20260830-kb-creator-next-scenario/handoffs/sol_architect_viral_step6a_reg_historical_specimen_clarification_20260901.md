# Viral Step 6A REG historical-specimen clarification

## Receipt and authority

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-reg-historical-specimen-clarification`.
- Role: architecture/root-cause only, policy `gpt-5.6-sol` / `high`; actual platform model/effort `unavailable`; assignment state `platform-unverified`; scoped override `architecture clarification only`.
- Orchestrator policy owner remains the root/main chat, policy `gpt-5.6-sol` / `medium`; this receipt does not transfer canonical plan/context/status, integration, dispatch, stop/ask, or user-facing ownership.
- Result: **STOP — not implementation-ready**. No synthetic historical specimen is authorized. Terra must not start REG implementation from this packet.
- Timestamp: `2026-09-01T09:40:01+03:00` (Europe/Moscow). Elapsed time and token use: `unavailable`.
- Sole changed path: this absent-before immutable receipt. No code, test, candidate, source, recovery, protected, plan, context, project-status, Git, cache, live, promotion, or release path was changed.

This clarification is subordinate to the accepted parent packet
`sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md`, SHA-256
`32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`,
and its accepted independent review, SHA-256
`B45198A548309258D08DE3CFBD4B0FA18F65580CBD94192E03044507E688E279`,
except that it identifies two parent REG clauses that cannot presently be executed truthfully.
The accepted QAV-D2 correction remains current evidence at SHA-256
`32A714D453F4A895866267A8F47879DE554A53581E272A7908C3F92D695FC268`.
The frozen current library/test baseline is exactly:

- `kb_creator/scripts/scenario_source_reconstruction.py` — `34943D5E0008A01A1F3AFC3AF2D49091F06049187AE9D0CB7DA02654663862D4`;
- `kb_creator/tests/test_scenario_source_reconstruction.py` — `D3FA871BBA3DED04ECD216544B7A9A7EEECB95D4769DDF45612B412990F9D192`.

## Decision

The exact physical historical specimen required by `REG-P1-stale-metadata` is **not retained in local authority**. Local evidence proves several properties of the old QA-v2 object, its raw SHA-256, and its inventory path set, but it does not preserve the object bytes, all 470 inventory records, or all old inventory-metadata fields. Reconstructing those missing bytes from present files would invent historical evidence and is forbidden by the parent packet's named-historical-specimen requirement.

There is a second independent conflict: the frozen shared verifier cannot return `E_QA_SCHEMA`. Its phase-5 QA predicate returns `E_SHAPE_QA` before checking schema, then returns `E_SCHEMA_QA`; the string `E_QA_SCHEMA` does not exist in the frozen library. The accepted `SCH-QA-schema-wrong` case also canonically expects `E_SCHEMA_QA`. Hidden REG-aware routing is forbidden. Therefore the requested claim that the old specimen “deterministically returns `E_QA_SCHEMA`” is false for the bound baseline.

`REG-P1-missing-enforcement` can be bound physically, but its exact mutation is identical to the existing `CMD-count-pages-wrong` state. Implementing it honestly would create a sixth cross-family identical-state alias, while the accepted QAV-D2 amendment/review binds exactly five alias pairs and explicitly stops on a sixth. It therefore also needs a reviewed supersession before Terra writes.

## Exact historical facts proved locally

### QA-v2 object

The historical QA file was root `RECONSTRUCTED_EN.qa.json`, raw SHA-256
`FE142A0C8749B0D139265659A08F88F6CB67B3D34EB9815DB2B62875FA6B75DE`.
The following values are directly proved by the post-remediation independent critic's read-only inspection while that file still existed:

| Selector | Proved historical value |
|---|---|
| `candidate/RECONSTRUCTED_EN.qa.json#/schema` | exact literal `kb_creator.reconstructed_en_qa.v2` |
| `candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256` | `C32CCA2A85F8123A2BE9E015FB39642943E31FCD723FA466FA436F454B344C3A` |
| `candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256` | property/value absent from QA |
| `candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count` | integer `3` |
| `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory` | array length `470` |
| `candidate/RECONSTRUCTED_EN.qa.json#/state` | `candidate_needs_review` |

The stale recovery-manifest value is the pre-admission binding carried by QA; it differs from the admitted recovery manifest raw SHA-256
`41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169`.
An earlier review reported old candidate metadata containing recovery-evidence value
`050F8A1AB81B660D3F1CF1809C77DB5AE57B41C9545EF72DA945A7204582FCFE`;
the later direct QA inspection explicitly proved that value was **not present in QA**. It must not be inserted into the REG QA specimen.

The original pre-remediation blocker ledger is proved as `open_count=3` with three rows; after remediation it became four open rows while QA remained at `open_blocker_count=3`. No retained authority proves whether the old QA-v2 `counts` map had an `open_blockers` key or, if present, its exact value. Only `open_blocker_count=3` may be bound without recovery of the old object.

The QA-v3 remediation packet explicitly required v3 to add
`output_inventory_rule`, `output_inventory_count=501`, and
`output_inventory_sha256=<501-record digest>`. No direct dump of the old QA-v2 key set survives. Consequently the exact historical presence/absence and values of the corresponding v2 count/digest/rule fields are not independently recoverable; they must not be guessed. The strongest safe inference is that they were v3 additions, but an inference is not executable historical authority.

### Exact 470-path set, but not the exact 470 records

The old candidate contained 471 regular files including QA. Its QA inventory excluded root QA and therefore had 470 paths. After remediation, exactly 31 new paths were added:
`renders/contact_sheets/sheet-001.png` through
`renders/contact_sheets/sheet-031.png`; no old inventory path was added or removed.
The exact old inventory **path set** is therefore reproducible as:

> the current 501-row non-QA inventory, minus exactly those 31 contact-sheet paths, sorted with `StringComparer.Ordinal`.

Its path-only serialization `path + LF`, with one final LF, has 470 paths,
34,300 UTF-8 bytes, and SHA-256
`131167D0486650B026F047FF61861AF8BB73BE342D607BA10403B1D8E072BDD5`.
This path-only digest is clarification evidence; it is **not** the historical inventory record digest.

Of those 470 paths, 461 files were not regenerated by the intervening remediation, so their present `{path,bytes,sha256}` records are usable as historical records. Exactly nine non-QA JSON paths were regenerated and therefore require their old bytes/record values:

1. `SOURCE_IDENTITY.json`
2. `evidence/ASSET_PROVENANCE.json`
3. `evidence/NAVIGATION_INVENTORY.json`
4. `evidence/PAGE_PROVENANCE.json`
5. `evidence/CONTENT_PROVENANCE.json`
6. `evidence/ENTITY_INVENTORY.json`
7. `evidence/HANDOUT_INVENTORY.json`
8. `evidence/BLOCKER_LEDGER.json`
9. `evidence/COMMANDS.json`

Only two old row hashes were recorded:

- `SOURCE_IDENTITY.json` — `1F6E4157CBD01C1A435DE360CD0577BBBD005DB895FC3047723B0C28A058B900`;
- `evidence/ASSET_PROVENANCE.json` — `506E9F62BDF2EA7ED85FA242F5067807A238ADD951146B93737F92ED35D2D5F8`.

Their historical byte counts were not retained, and none of the other seven old row byte counts/hashes or file bytes were retained. Thus neither the complete 470 records nor their canonical `path<TAB>bytes<TAB>SHA256<LF>` digest can be reproduced from local authority. One current QA-v3 file is the only `RECONSTRUCTED_EN.qa.json` found anywhere in the worktree; it has schema v3, 501 inventory rows, and SHA-256
`C38CB0A4667B1D4344C5E5DD91AEAAE7A2FD3101A3BB76611104EAA13BBD8FA6`.

## Why the phase-5 code is not `E_QA_SCHEMA`

The shared verifier loads QA, then calls `_verify_qa_root_shape`, then proceeds to phase-6 `_verify_inventory_authority`. The frozen predicate is exactly shape-first:

1. `set(qa) != expected_keys` -> `E_SHAPE_QA`;
2. otherwise `qa["schema"] != "kb_creator.reconstructed_en_qa.v3"` -> `E_SCHEMA_QA`.

An authentic v2 object with the proved absent recovery-evidence property and unproved/likely absent v3 inventory-metadata keys is a root-shape mismatch and therefore stops as `E_SHAPE_QA` in the frozen baseline. A synthetic v3-shaped object with only its schema changed would stop as `E_SCHEMA_QA`. Neither branch can produce `E_QA_SCHEMA`. The accepted abstract phase order saying “schema then shape” and preserving `E_QA_SCHEMA` is inconsistent with current code and the accepted SCH taxonomy.

The smallest coherent taxonomy branch is:

- recover the exact old QA-v2 bytes first;
- issue a fresh amendment that chooses one shared phase-5 rule for every family, with no case/family/audit/pytest routing;
- preferably restore schema-first and map both SCH QA schema and the REG historical specimen to canonical `E_SCHEMA_QA`; or, if shape-first is intentionally retained, map the authentic historical specimen to `E_SHAPE_QA` and retain `SCH-QA-schema-wrong -> E_SCHEMA_QA` only for a shape-complete wrong-schema object;
- retire the unreachable `E_QA_SCHEMA` expectation from REG rather than add a REG-only code.

Either choice changes accepted taxonomy evidence and requires targeted SCH/QAV/REG reruns plus fresh review. This receipt does not select or authorize an implementation branch while the historical object is absent.

## Exact `REG-P1-missing-enforcement` binding

Conditional on a new reviewed alias-ceiling amendment, the exact case is:

| Field | Binding |
|---|---|
| case id | `REG-P1-missing-enforcement` |
| selector | `candidate/evidence/COMMANDS.json#/counts/pages` |
| before value | integer `124` |
| mutation | set only `COMMANDS.counts.pages` to integer `125` (`old + 1`) |
| reseal tuple/order | `(INVENTORY, QA)` |
| expected/earliest code | `E_COMMAND_COUNTS_PAGES` |
| verifier order | phase 5 shapes -> phase 6 inventory -> phase 7 graph -> phase 8 COMMANDS actions/state/flags/arguments/external-locator, then counts in declared order with `pages` first |

This is physically identical to `CMD-count-pages-wrong`; REG must nevertheless have a distinct case id, distinct callable object/name, fresh fixture, and distinct 16-field audit row. The explicit global identical-state alias table must be superseded from exactly five pairs/ten members to exactly six pairs/twelve members by adding only:
`CMD-count-pages-wrong <-> REG-P1-missing-enforcement`.
No seventh pair, shared callable, hidden routing, or count increase is allowed.

## Historical multi-field mutation and audit contract

If and only if the exact old QA-v2 object is recovered and hash-verifies to
`FE142A0C...B75DE`, the REG stale mutator may replace the fresh fixture's whole QA document with those exact recovered bytes/object. It must not synthesize fields or rebuild historical inventory rows from current files.

- Case id: `REG-P1-stale-metadata`.
- Semantic selector: `candidate/RECONSTRUCTED_EN.qa.json#` (the QA document root, denoting one historical transaction).
- Reseal tuple: `()`.
- `semantic_before_sha256`: hash of the valid fixture QA root bytes.
- `semantic_after_sha256`: exactly `FE142A0C8749B0D139265659A08F88F6CB67B3D34EB9815DB2B62875FA6B75DE` when the historical canonical file bytes are installed.
- `changed_before_reseal`: for this parent-authorized multi-field exception only, the complete ordinal JSON-Pointer symmetric difference between valid QA-v3 and recovered QA-v2, including every changed inventory row; at minimum it must contain `#/schema`, `#/recovery_manifest_sha256`, `#/recovery_evidence_sha256`, `#/open_blocker_count`, and `#/output_inventory`. Any `#/counts/open_blockers` or inventory rule/count/digest pointer is included only if the recovered object proves it. A single root token is not a complete delta audit.
- `changed_by_reseal`: `[]`; `undeclared_changes`: `[]`; `strict_verify_calls=1`; `outside_fixture_reads=0`; `residue=[]`; expected code equals the newly reviewed canonical phase-5 code; result `PASS`.

Because the exact symmetric difference cannot currently be computed, the required complete audit cannot currently be produced.

## Count and evidence impact

No case is added or removed. Implementing the two already-counted REG identities would keep:

- `REG=2`;
- selector-specific negatives `368`;
- `BLD=3`;
- focused collection `371`.

The sixth alias pair changes only declared collision evidence, not node arithmetic: callable identities remain 368/368 distinct even when two callables create the same post-mutation state.

The current QAV-D2 correction and prior INV/QAV engineering receipts remain valid historical evidence for their bounded cases and current hashes. They are not REG proof. A reviewed sixth-pair amendment would supersede only their five-pair-ceiling claim; it would not invalidate their case outcomes. Any shared phase-5 taxonomy change invalidates current-result carry-forward for `SCH-QA-schema-wrong`, QA root-shape aliases, and both REG nodes; those nodes must rerun on the new baseline. None of these receipts is final QA, protected-119, combined-490, candidate acceptance, release, promotion, publication, or Git evidence.

## Permitted recovery/amendment branches

Exactly two branches are permitted; neither is authorized by this receipt to write code/tests.

1. **Evidence recovery branch (preferred).** The orchestrator supplies a locally authoritative immutable copy or byte dump of the historical QA-v2 file. Admission requires raw SHA-256 `FE142A0C...B75DE` and parsing that proves every top-level field plus all 470 exact rows and metadata. A narrative reconstruction, current-row substitution, partial row table, guessed metadata, or hash-only claim is insufficient.
2. **Explicit redefinition branch.** If the old bytes cannot be recovered, the orchestrator must issue new authority explicitly renaming/redefining `REG-P1-stale-metadata` as a synthetic regression cluster, providing its complete exact object/row values and admitting that it is not the historical physical specimen. The amendment must also resolve the canonical phase-5 code and the sixth alias pair. The present accepted goal does not authorize this branch implicitly.

Absent one of those branches and a fresh independent architecture acceptance, REG remains blocked.

## Conditional Terra scope, commands, and audit

Only after the evidence and taxonomy/alias blockers are resolved and independently accepted, Terra's exact three-path allowlist is:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. absent-before `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_reg_20260901.md`.

No fourth path is permitted. In particular, the live candidate, source/recovery, protected tests, CLI, prior receipts, plan/context/status, Git, and cache remain read-only.

Conditional cache-disabled acceptance commands are:

```powershell
python -B -m pytest `
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[REG-P1-stale-metadata]' `
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[REG-P1-missing-enforcement]' `
  -q -p no:cacheprovider

python -B -m pytest `
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[CMD-count-pages-wrong]' `
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[REG-P1-missing-enforcement]' `
  -q -p no:cacheprovider

python -B -m pytest `
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[SCH-QA-schema-wrong]' `
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[REG-P1-stale-metadata]' `
  -q -p no:cacheprovider

python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -k 'test_bld_' -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
```

Required native results are `2 passed`, `2 passed`, `2 passed`, `3 passed` for BLD, and exactly `371 tests collected`. Registry audit must prove `REG=2`, `len(CASES)=368`, 368 unique ids, 368 unique callable objects/names, exactly six explicitly declared alias pairs/twelve members, and no production verifier input containing family/case/audit/pytest identity. The Terra receipt must contain the two complete 16-field REG audits, the six-pair identity table, command/native exit/stdout-stderr hashes, pre/post code/test hashes, exact path delta, and zero residue/outside-fixture reads.

These are batch acceptance commands only. Terra may not run live preflight/verify/build/remediate or protected/combined/final acceptance commands.

## Independent review and downstream boundaries

Before any implementation dispatch, a fresh independent `gpt-5.5` / `high` architecture critic, with no implementation/material-design/QA participation, must write only absent-before:
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reg_historical_specimen_clarification_review_20260901.md`.
It must hash-bind this receipt and the current code/test/QAV-D2 evidence; independently verify the absence or admission of the old blob; decide the shared phase-5 taxonomy; review the sixth alias ceiling and exact missing-enforcement binding; and return `ACCEPT` with no unresolved P0/P1 before Terra can start. Acceptance of this receipt's **STOP diagnosis alone does not clear the missing evidence**.

After a valid Terra receipt, separate bounded QA (`gpt-5.6-luna` / `high`) must inspect actual code and rerun the affected aliases/taxonomy nodes, full focused 371, protected 119, combined 490, and read-only live preflight plus deterministic verify twice, with candidate/protected/cache hashes unchanged. A fresh independent `gpt-5.5` / `high` implementation/process critic then reviews the frozen implementation and QA with no unresolved P0/P1/P2. This architect is not the final release reviewer. Release, semantic acceptance, `MASTER_EN`, promotion, publication, staging, commit, and push remain separate and unauthorized.

## Stop conditions and next action

Stop before any Terra write if the old QA-v2 bytes are absent/hash-mismatched; any old row or metadata value is guessed; phase-5 code remains undecided; `E_QA_SCHEMA` is retained through REG-specific routing; the six-pair alias ceiling is not explicitly reviewed; any bound hash differs; the critic gate is absent/rejecting; or work cannot fit the exact three-path allowlist.

After a future first write, stop with a truthful blocked Terra receipt on any selector/value/reseal/code/order/audit/count mismatch, shared callable, seventh alias, outside-fixture read, multiple strict-verifier calls, undeclared mutation, residue, scope widening, live/protected/candidate/Git/cache write, or weakening of schema, inventory, evidence-graph, COMMANDS, no-fabricated-closure, or production-route enforcement.

Next action: the orchestrator either obtains the exact hash-bound historical QA-v2 blob or creates an explicit redefinition/taxonomy/alias amendment. Until then, keep REG unimplemented and do not dispatch Terra.

## Files checked read-only

- `AGENTS.md`; `docs/governance/nri_goal_governance.md`; assigned `plan.md` and `context.md`.
- Accepted parent packet/review; enforcement-injection amendment/review chain; SCH/QAV and INV/QAV taxonomy amendments/reviews; QAV-D2 correction.
- Builder, builder-remediation, QA-metadata remediation, critic, QA, executor, dispatch, and correction handoffs relevant to the old 471/470 state.
- All worktree files named `RECONSTRUCTED_EN.qa.json`; exact historical literals across the worktree; failure/candidate roots discoverable locally.
- Frozen reconstruction library and focused tests, including QA phase order, inventory admission, COMMANDS page-count enforcement, REG registry entries, CMD callable, and alias evidence.
- Current candidate read-only for QA identity and the reproducible 470-path-set calculation.

No broad search continues after sealing this receipt.
