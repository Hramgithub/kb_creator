# Viral Step 6A INV/QAV inventory-metadata taxonomy amendment

## 1. Immutable handoff identity and authority

- Goal / step: `20260830-kb-creator-next-scenario` / `6A-INV-QAV-inventory-metadata-taxonomy-amendment`.
- Result: `IMPLEMENTATION_READY_PENDING_FRESH_INDEPENDENT_ARCHITECTURE_REVIEW`.
- Role: architecture/root cause; repository policy `gpt-5.6-sol` / `high`.
- Actual platform model / effort: `unavailable`; repository role policy does not prove platform selection.
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`. Orchestration, canonical plan/context/status, integration, stop/ask decisions, release, and user-facing synthesis remain there.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.
- Worktree / branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Canonical absent-before path: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_inv_qav_inventory_metadata_taxonomy_amendment_20260901.md`.
- Accepted parent packet: SHA-256 `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`.
- Accepted parent design review: SHA-256 `B45198A548309258D08DE3CFBD4B0FA18F65580CBD94192E03044507E688E279`.
- Accepted SCH/QAV amendment / review: SHA-256 `0A692CD1A8F3067E551ACFB1581840BF9748FD2C308C6BBE79FD4B174FC75D2A` / `102383E2CD10EFE91DFBAD13A905DDCFB63DFE8ADF6BCC9B1D7937E40ADAA5DB`.
- Current library / focused-test baseline: SHA-256 `FCAE2693C03A35382CADF35B6474E7A173670D65FD6D428726E56E71FF4BDA46` / `3A7DB49164A11DF5C7EB5663639914668ACE1AAA22F72AEC2F69F66B0E474357`.
- INV receipt: SHA-256 `A559B08DFF5A4EB75F41AD075ECB91E74797956502A210B08B62C78FCFE78518`.
- QAV-D1 receipt: SHA-256 `12A38CB2267EDF6E85184BC8728A4BCCC8B1E14424F14D4BB8BE984FD37DA4E7`.
- Timestamp: `2026-09-01T08:57:58+03:00`.
- Elapsed time through initial seal: approximately `35 minutes`.
- Token use: `unavailable`.

This amendment is a remediation specification only. It is not code/test implementation, QA, live execution, candidate acceptance, semantic review, `MASTER_EN`, promotion, publication, release, Git, cache, or cleanup authority. Its immutable identity is this path plus the raw SHA-256 reported after creation and bound by the required fresh review. Any byte change invalidates that review.

## 2. Root cause, dependency trace, and evidence

The shared `_strict_verify` path loads the physical QA document and calls `_verify_inventory_authority(candidate_root, qa)` in binding phase 6, before later QAV policy semantics. Phase 6 already consumes the three proposed QAV-D2 invalid states:

1. changing `output_inventory_count` from `501` to `500` necessarily returns `E_INV_CARDINALITY`;
2. changing `output_inventory_sha256` to sixty-four zeroes necessarily returns `E_INV_DIGEST`; and
3. changing the inventory array by removing `RECONSTRUCTED_EN.md` necessarily returns `E_INV_ORDINARY_ROW_MISSING` before cardinality or digest.

The accepted INV receipt proves those exact physical mutations independently:

| Existing INV case | Exact selector | Mutation | Proven earliest code |
|---|---|---|---|
| `INV-cardinality-wrong` | `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count` | set to integer `500` | `E_INV_CARDINALITY` |
| `INV-digest-wrong` | `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256` | set to string `"0" * 64` | `E_INV_DIGEST` |
| `INV-ordinary-row-missing` | `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md` | remove exactly the row whose `path == "RECONSTRUCTED_EN.md"` | `E_INV_ORDINARY_ROW_MISSING` |

The verifier observes admitted bytes, not a pytest id or registry family. The same physical invalid document cannot return `E_INV_*` for an INV-labelled fixture and `E_QA_*` for a QAV-labelled fixture without prohibited family/case/pytest/environment/provider-prefix routing. The preferred minimal solution is therefore sound: preserve phase-6 INV authority and make the three QAV cases explicit cross-family audit aliases.

`output_inventory_rule` is different. Phase 6 does not consume it, so a wrong rule remains independently reachable in later phase-8 QA semantics and retains `E_QA_INVENTORY_RULE`.

The live read-only candidate already contains the production-shaped literal:

`every regular file recursively present under candidate root except root-level RECONSTRUCTED_EN.qa.json`

The current shared TEST/build writer instead emits `all_regular_except_qa`, and the later verifier currently omits a rule check while retaining unreachable array/count/digest QAV branches. Those are implementation gaps, not authority to weaken the live literal.

## 3. Binding count-neutral QAV-D2 matrix

The four QAV-D2 rows remain the final four QAV registry members in this exact order. Every row mutates only the physical root `candidate/RECONSTRUCTED_EN.qa.json`, has literal reseal tuple `()`, literal `allowed_transport_selectors == ()`, one fresh fixture, one distinct named callable, exactly one `_test_verify`, and one full closed audit object.

| # | Exact case id | Exact semantic selector | Exact physical mutation | Canonical earliest code | Reseal |
|---:|---|---|---|---|---|
| 1 | `QAV-inventory-rule-wrong` | `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule` | replace the canonical production literal with exact legacy short string `all_regular_except_qa` | `E_QA_INVENTORY_RULE` | `()` |
| 2 | `QAV-inventory-count-wrong` | `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count` | set exact integer `500` | `E_INV_CARDINALITY` | `()` |
| 3 | `QAV-inventory-digest-wrong` | `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256` | set exact string `"0" * 64` | `E_INV_DIGEST` | `()` |
| 4 | `QAV-inventory-array-wrong` | `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md` | remove exactly the row whose `path == "RECONSTRUCTED_EN.md"`; do not alter count or digest | `E_INV_ORDINARY_ROW_MISSING` | `()` |

The changed-before-reseal set is exactly the one selector in each row. `declared_reseals`, `changed_by_reseal`, and allowed transport selectors are empty. No QA regeneration or transport repair is permitted because QA is excluded from its own inventory and each selected invalid state must remain observable.

The array case deliberately narrows the former generic `#/output_inventory` selector to the already proven ordinary-row selector. “Wrong array” is otherwise under-specified and could collide with many earlier INV codes. This one physical mutation gives one deterministic earliest code without adding or removing a case.

## 4. Canonical production rule and writer/verifier contract

The library must define one immutable canonical value, preferably one `Final[str]` constant, with exactly these bytes:

```text
every regular file recursively present under candidate root except root-level RECONSTRUCTED_EN.qa.json
```

Binding behavior:

1. The common writer used by TEST fixtures and production-shaped staging emits only this literal.
2. Any direct TEST fixture construction in the focused test file also uses the same library constant; it may not carry a separate short form.
3. Phase-8 QA semantics, after the nine gates and the two false booleans but before phase-9 state, compares `qa.get("output_inventory_rule")` to the exact literal and emits `E_QA_INVENTORY_RULE` on inequality.
4. The verifier accepts no alias, normalized spelling, enum shorthand, prefix, or backwards-compatible `all_regular_except_qa` value.
5. The D2 rule mutation sets the exact legacy short form so the test proves that it is rejected.
6. The live candidate is read-only and already matches; no candidate QA rewrite or reseal is authorized.

This rule is a declarative explanation of the same inventory authority enforced in phase 6. It does not replace independent enumeration and does not authorize trusting the array metadata.

## 5. Binding phase order and unreachable-code policy

The accepted order remains:

0. context/profile/provider admission;
1. repository identity and containment;
2. argument/path admission;
3. source, sidecar, contract, source identity, and recovery authorities;
4. forbidden classes and topology;
5. schemas, closed shapes, and row shapes;
6. `_verify_inventory_authority`, with the accepted `E_INV_*` taxonomy;
7. production graph relations;
8. COMMANDS and QA authority hashes/scalars/count map/gates/booleans, then the exact inventory-rule literal;
9. no-fabricated-closure state.

After phase 6 succeeds, the QA array is already a complete, ordered, exact `{path, bytes, sha256}` representation of all 501 live non-QA regular files; its declared count and digest also match. Therefore the later `E_QA_INVENTORY_ARRAY`, `E_QA_INVENTORY_COUNT`, and `E_QA_INVENTORY_DIGEST` branches are unreachable duplicates, not defense in depth.

Terra must remove those three later branches and their redundant `candidate_records` recomputation. Their current test expectations are replaced by the three aliases in section 3. `E_QA_INVENTORY_ARRAY`, `E_QA_INVENTORY_COUNT`, and `E_QA_INVENTORY_DIGEST` must not remain emitted or expected in the two mutable material files. Historical immutable packets and receipts keep their old text and are never edited. Only `E_QA_INVENTORY_RULE` remains in the current QAV inventory-metadata taxonomy.

No internal-invariant code is added for this batch. If implementation discovers a genuinely reachable post-phase-6 inconsistency, it must stop for architecture rather than add a hidden fallback or reorder phases.

## 6. Exact alias ceiling and audit identities

The test/audit registry must declare exactly five identical-state cross-family alias pairs, and no more:

1. `SCH-QA-required-top-member-missing` / `QAV-top-asset_count-missing`;
2. `SCH-qa-unexpected-top-member` / `QAV-top-extra`;
3. `INV-cardinality-wrong` / `QAV-inventory-count-wrong`;
4. `INV-digest-wrong` / `QAV-inventory-digest-wrong`;
5. `INV-ordinary-row-missing` / `QAV-inventory-array-wrong`.

The first two remain governed by the accepted SCH/QAV amendment. This amendment adds exactly three pairs. The global exception therefore rises from exactly two pairs to exactly five pairs; it does not create a general permission for duplicate mutations.

For each pair, selector, physical mutation, reseal tuple, and canonical code are identical, but case id, mutation callable object, callable name, fixture identity, audit object, and audit row are distinct. Required QAV callable names are:

- `mutate_QAV_inventory_rule_wrong`;
- `mutate_QAV_inventory_count_wrong`;
- `mutate_QAV_inventory_digest_wrong`;
- `mutate_QAV_inventory_array_wrong`.

All 368 mutation callables remain non-null and object-distinct. The five-pair table is test/audit evidence only and must never be passed to `_strict_verify` or used for production error selection. Semantic selector remains intentionally non-unique. The verifier receives neither case id, family, expected code, callable name, audit object, pytest state, nor environment marker.

The three new QAV alias mutators may use the same helper factories as INV, but each factory call must create a new wrapper object and descriptive name. `QAV_D2_CASE_IDS` may control only whether the focused test invokes `apply_case`; it cannot influence the verifier or observed code. The current generic COMMANDS proxy fallback is forbidden for all four D2 nodes.

## 7. Count proof

No registry membership changes:

- `INV = 18`: the 18 accepted INV cases remain untouched.
- `QAV = 90`: `24 root-shape + 1 state + 4 authority-hash + 9 scalar + 28 count-map + 20 gate/boolean D1 + 4 D2 = 90`.
- The family arithmetic remains `2+18+30+21+33+6+18+28+15+21+18+61+90+2+5 = 368` selector-specific negatives.
- `368 negatives + 3 BLD = 371` focused tests.

The three aliases change expected-code literals and the array selector/mutation specification only. They neither merge audit rows nor add nodes. Selector uniqueness is not used as a count proxy.

## 8. Prior evidence and invalidation boundary

Completed receipts remain immutable historical evidence:

- INV `A559B08DFF5A4EB75F41AD075ECB91E74797956502A210B08B62C78FCFE78518` remains semantically valid and proves the three canonical phase-6 outcomes.
- QAV-A/B/C/D1 receipts `5A08C25D42FCCAE87C154FCBC505125F4D71BEF9196FECA1BEC8D2CE9FFEE5EC`, `652DEEDC0DD415853FB7193148DBABC5041C06909DAE0AC83C1C0295E01B8DEA`, `346AEB9D11EB6749471DDB9218F4CB6AC86C5F8B1982F8ACED5EE6E79D61D0C6`, and `12A38CB2267EDF6E85184BC8728A4BCCC8B1E14424F14D4BB8BE984FD37DA4E7` remain semantically valid for their bounded cases.
- The accepted SCH/QAV amendment/review remains valid and continues to govern the first two alias pairs.
- No receipt digest, audit object, plan, context, status, candidate, or protected identity is rewritten by this amendment.

Narrow invalidations/supersessions:

1. Parent-packet QAV expectations `QAV-inventory-count-wrong -> E_QA_INVENTORY_COUNT`, `QAV-inventory-digest-wrong -> E_QA_INVENTORY_DIGEST`, and `QAV-inventory-array-wrong -> E_QA_INVENTORY_ARRAY` are superseded by section 3.
2. The corresponding current focused-registry expected-code literals are invalid.
3. The current short writer literal and absence of an exact phase-8 rule check are invalid implementation behavior.
4. The current later array/count/digest QAV branches are retired as unreachable.

Historical validity is not current-baseline sufficiency. After D2 implementation, Terra must rerun all ten members of the five alias pairs on the post-write baseline: the four SCH/QAV nodes, the three INV nodes, and the three aliased QAV-D2 nodes. It must also run `QAV-inventory-rule-wrong`. Final bounded QA must later rerun the full 371.

## 9. Exact Terra three-path scope

Terra remains blocked until a fresh independent review accepts this exact immutable amendment. After the orchestrator binds that review, Terra may change only:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. absent-before `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_d2_20260901.md`.

Library scope is limited to the canonical rule constant/writer/check and removal of the three unreachable later branches. Phase-6 INV code, selectors, order, and error taxonomy are protected.

Focused-test scope is limited to the four section-3 expectations/mutators, exact D2 audit routing, the five-pair closed alias invariant, canonical writer assertion, and retirement checks for the three dead `E_QA_*` codes. INV membership and existing INV mutators are protected. QAV-A/B/C/D1, SCH, all other families, BLD membership, and 368/371 membership remain unchanged.

The receipt records all four full closed D2 audit objects in registry order; their canonical UTF-8/LF audit rows, byte length, and SHA-256; a separate five-pair callable-identity table using non-secret within-process ordinals rather than addresses; commands/native exits/output hashes; material/cache pre/post identities; exact changed paths; elapsed time; and token use or `unavailable`.

No candidate, live, source, sidecar, contract, recovery, protected CLI/test, plan, context, project status, README, governance, prior receipt, release, Git index/ref, cache, cleanup, fixture, temp, marker, probe, or log write is allowed.

## 10. Terra acceptance commands and audit

Run from the exact worktree with `python -B` and pytest cache disabled. Before first write, verify this amendment and its fresh review hashes, the section-1 material/receipt hashes, the absent D2 receipt, the live rule literal, and the protected dispatch snapshot.

```powershell
Set-Location 'D:\NRI\.worktrees\kb-creator-viral'

$qavD2 = @(
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-inventory-rule-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-inventory-count-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-inventory-digest-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-inventory-array-wrong]'
)
$invAliases = @(
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[INV-cardinality-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[INV-digest-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[INV-ordinary-row-missing]'
)
$shapeAliases = @(
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[SCH-QA-required-top-member-missing]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-top-asset_count-missing]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[SCH-qa-unexpected-top-member]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-top-extra]'
)
if ($qavD2.Count -ne 4 -or (@($qavD2 | Sort-Object -Unique)).Count -ne 4) { throw 'QAV-D2 node set mismatch' }
if ($invAliases.Count -ne 3 -or (@($invAliases | Sort-Object -Unique)).Count -ne 3) { throw 'INV alias node set mismatch' }
if ($shapeAliases.Count -ne 4 -or (@($shapeAliases | Sort-Object -Unique)).Count -ne 4) { throw 'shape alias node set mismatch' }

python -B -m pytest @qavD2 -q -p no:cacheprovider
python -B -m pytest @invAliases -q -p no:cacheprovider
python -B -m pytest @shapeAliases -q -p no:cacheprovider

$representative = @(
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-gate-visual_review-closed]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[QAV-counts-pages-wrong]',
  'kb_creator/tests/test_scenario_source_reconstruction.py::test_selector_specific_mutation[CMD-count-pages-wrong]'
)
python -B -m pytest @representative -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -k 'test_bld_' -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider

$dead = rg -n 'E_QA_INVENTORY_(ARRAY|COUNT|DIGEST)' kb_creator/scripts/scenario_source_reconstruction.py kb_creator/tests/test_scenario_source_reconstruction.py
if ($LASTEXITCODE -eq 0) { throw "retired QAV inventory code remains: $dead" }
if ($LASTEXITCODE -ne 1) { throw 'retired-code search failed' }
```

Required native results are `4 passed`, `3 passed`, `4 passed`, `3 passed`, `3 passed` for BLD, and exactly `371 tests collected`. All four D2 audits must report exact expected/observed codes, `strict_verify_calls == 1`, `outside_fixture_reads == 0`, empty declared/actual reseals, empty undeclared changes/residue, and uppercase `PASS`.

Registry evidence must prove `len(CASES) == 368`, 368 unique case ids, 368 unique mutation callable objects, QAV `90`, INV `18`, exactly five declared alias pairs, and distinct callable/audit identities for all ten alias members. The four D2 rows retain the parent packet's 16-field audit shape and digest formula; the alias table remains separate and does not widen those objects.

These are batch commands, not final Step-6A acceptance. Terra must not run live `build`, `remediate`, preflight, verify, protected 119, combined 490, or release commands.

## 11. Fresh review, downstream QA, and critic boundaries

Implementation remains blocked until a fresh independent `gpt-5.5` / `high` architecture critic:

1. verifies this amendment's exact path and raw SHA-256;
2. verifies the accepted parent packet/review, SCH/QAV amendment/review, INV and QAV-D1 receipts, current code/test hashes, live rule literal, and absence of the D2 receipt;
3. independently assesses phase order, three new aliases, five-pair ceiling, count preservation, literal choice, dead-code removal, and prior-evidence carry-forward;
4. declares no implementation, material-design, or QA participation for the implementation it will gate; and
5. writes only absent-before `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_inv_qav_inventory_metadata_taxonomy_amendment_review_20260901.md`.

The gate requires `ACCEPT` with no unresolved P0/P1. Any P2 must be explicitly resolved by the orchestrator before dispatch; any byte change to this amendment requires a fresh review.

After Terra's immutable D2 receipt, bounded independent QA (`gpt-5.6-luna` / `high`) must inspect actual code rather than trust Terra's tables; run full focused `371`, protected `119`, combined `490`; prove the 368/3 split, 18/90 counts, exact five alias pairs, canonical writer/rule check, phase order, and absence of retired branches; run live preflight and deterministic live verify twice read-only; and prove protected/candidate/cache identities unchanged. Live `build` and `remediate` remain forbidden.

A fresh independent `gpt-5.5` implementation/process critic, with no implementation/material-design/QA participation, must then return no unresolved P0/P1/P2 before orchestrator integration. Neither this architect nor the amendment critic acts as final release reviewer. Release review remains a separate later gate for a frozen release candidate.

## 12. Assumptions, risks, acceptance criteria, and stop conditions

Assumptions:

- phase 6 remains before phase 8 and first-error selection remains deterministic;
- the live candidate continues to carry the exact production rule literal;
- QA remains excluded from its own inventory, so all D2 reseals are empty;
- no current D2 implementation receipt exists.

Primary risks are accidental family routing, retaining misleading dead error branches, accepting the short TEST literal as a synonym, merging alias audit identities, changing the array mutation so another INV code wins, or treating historical receipts as post-change proof.

Acceptance criteria:

- all four section-3 ids/selectors/mutations/codes/reseals/order are exact;
- one canonical production literal is emitted by TEST and production-shaped writers and checked exactly at phase 8;
- phase-6 INV behavior and all 18 INV cases remain unchanged;
- the three shadowed `E_QA_INVENTORY_*` branches/expectations are absent from current code/test while historical receipts remain untouched;
- exactly five cross-family alias pairs exist, with ten distinct callable/fixture/audit identities and no verifier routing;
- INV/QAV/negative/focused counts remain 18/90/368/371;
- all section-10 commands and audit invariants pass with zero new residue;
- only the exact Terra three-path allowlist changes; and
- downstream QA, implementation/process criticism, semantic review, and release remain open.

Before first Terra write, stop if this amendment or review is missing/hash-mismatched/rejecting; any section-1 authority differs; the D2 receipt exists; the live rule differs; or work cannot fit the exact three-path allowlist.

After first write, create a truthful blocked D2 receipt and stop on any id/selector/mutation/code/reseal/order/audit/count/native-result mismatch; any alias callable reuse or sixth identical-state alias; any family/case/audit/pytest/environment/provider-prefix influence on production error selection; any acceptance of the short literal; any retained/emitted `E_QA_INVENTORY_ARRAY`, `E_QA_INVENTORY_COUNT`, or `E_QA_INVENTORY_DIGEST`; any phase-6 weakening/reorder; multiple strict-verifier calls, QA regeneration, undeclared delta, outside-fixture read, or residue; any out-of-scope/live/protected/candidate/Git/cache/cleanup write; or any live build/remediate, promotion, publication, release, staging, commit, or push.

No failure authorizes widening scope, editing prior receipts, changing the candidate, refreshing baselines, hidden routing, or weakening inventory authority.

## 13. Files checked, files changed, blockers, and next action

Files checked read-only:

- `AGENTS.md`;
- `docs/governance/nri_goal_governance.md`;
- current goal `plan.md` and `context.md` checkpoint;
- accepted parent architecture packet/review;
- accepted SCH/QAV amendment/review;
- INV assignment and immutable INV receipt;
- QAV-A/B/C and QAV-D1 receipts plus D1 assignment;
- current `kb_creator/scripts/scenario_source_reconstruction.py`;
- current `kb_creator/tests/test_scenario_source_reconstruction.py`;
- live candidate `RECONSTRUCTED_EN.qa.json` rule field;
- verifier/test registry and current target/review/D2-receipt absence.

Files changed: only this absent-before amendment. No code, test, candidate, source, recovery, contract, protected test, plan, context, project status, README, governance, prior receipt, release, Git, cache, or cleanup path was edited.

Blocker: Terra D2 implementation is procedurally blocked pending a fresh independent `gpt-5.5` / `high` architecture review of this exact immutable amendment.

Next action: compute this file's raw SHA-256 and dispatch only the fresh independent amendment review. Orchestration ownership remains with the main chat.
