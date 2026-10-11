# Packet I architecture — replay HR3, positional visual proof, and OCR equivalence

## Receipt

- **Timestamp:** 2026-09-15T04:04:38+03:00
- **Goal / packet:** `20260914-dissociation-publication`, Packet I.
- **Role / scoped override:** architecture and dependency/remediation specification, requested `gpt-5.6-sol` at `high`; read-only except for this assigned receipt.
- **Orchestrator policy owner:** main-chat `gpt-5.6-sol` at `medium`; ownership was not transferred.
- **Assignment state:** complete.
- **Scope:** design an additive downstream-only resume path for fresh replay Stage01-04 authority, plus fail-closed G1 positional visual assertions and G2 cross-view OCR equivalence for Dissociation run-07. No implementation or live replay was authorized.
- **Result:** **architecture GO, implementation/live replay NO-GO at present.** The design below changes no member of the accepted 19-path Stage01-04 producer closure. Implementation must not start on the current HR1/HR2 base until the independent critic's three P1 findings are remediated and re-reviewed.
- **Files changed:** this receipt only.
- **Blockers:** `critic_stage_scoped_replay_hr1_hr2_implementation_20260915.md` records P1 origin-path poisoning and generic/underclosed comparison/geometry/visual replay authority. HR3 must consume typed fresh authority and therefore cannot safely compensate for those defects downstream.
- **Next action:** remediate and independently close HR1/HR2 P1s; then implement Packets I1-I4 below, run focused/adversarial/synthetic tests, prove live run-07 eligibility read-only, and obtain an independent implementation review before creating a fresh replay root.
- **Elapsed time:** approximately 35 minutes in this bounded Packet I investigation.
- **Token use:** exact role token count unavailable.

## Evidence and current mismatch

The implemented HR1/HR2 public boundary is useful: `reconstruction_replay.validate_replayed_prefix()` validates the fresh run, intake/bridge seals, fresh identity, ancestry, four replay receipts/manifests, output inventories, semantic projection conservation, origin vault identities, producer-closure equality and fixed fresh run-local paths (`reconstruction_replay.py:917-1002`). It returns `FreshReplayAuthorities`, not caller-supplied origin paths (`:128-136`). Replay ends truthfully at `needs_review`, with `acceptance_inferred=false`, `decisions_replayed=false`, and `stages_05_06_replayed=false` (`:839-914`).

The legacy downstream route cannot be reused as a control plane:

- `reconstruction.resume_engine()` first invokes legacy live-run and Stage v1 validators (`reconstruction.py:1928-1944`) and writes Stage v1 manifests through private `_invoke_stage()` (`:1687-1774`). Those validators do not accept the fresh Stage v2/v3 replay authority.
- `production_resume_adapters()` assumes the legacy queue/comparison/visual schemas and passes caller-composed absolute paths (`:2289-2400`).
- the auditor requires comparison v2 and reopens the legacy Stage prefix (`audit_mineru_ai_merge_fidelity.py:373-451`);
- the materializer requires visual bundle v2, legacy geometry/input shapes and a v2 audit (`materialize_mineru_ai_merge.py:199-346,511-639`). Its v2 provenance also serializes absolute paths (`:602,624-633`).
- G1 is at audit lines `291-338`: selected spans are mapped, but all visual assertions are appended after every selected anchor.
- G2 is at audit lines `303-324`: loose substring coverage is accepted, while raster `ocr_artifact` is categorically rejected; neither branch proves a bounded cross-view OCR relationship.

Current HR1/HR2 is nevertheless not an acceptable dependency yet. The independent implementation critic found that `_rebase_comparison()` interprets origin absolute paths and that comparison v3, geometry v2 and visual bundle v3 leave critical nested authority generic. **Packet I must not be implemented against those generic envelopes.** The contracts below assume the remediated HR1/HR2 validator returns only closed, typed, contained fresh authorities.

## Accepted architecture

### 1. Additive CLI and API boundary

Add two explicit subcommands under the existing `replay` namespace:

```text
python -m kb_creator replay prepare-review \
  --run-root <fresh-replay-root> \
  --source-decisions <run-07-decision-set.json> \
  --source-decisions-root <run-07-decisions-root> \
  --output-root <absent-draft-root> --json

python -m kb_creator replay resume \
  --run-root <fresh-replay-root> \
  --decisions <fresh-submitted-decision-set.json> \
  --decisions-root <fresh-decisions-root> --json
```

`prepare-review` is optional and produces a **draft review migration proposal only**. It may copy semantically revalidated page-decision payloads, but it must leave `submission_state=draft`, record `acceptance_inferred=false`, and be rejected by `resume`. It never copies an allowlist and never converts review into acceptance. A human reviewer must author the new v3 allowlist and explicitly submit the fresh decision set.

`resume` has a fixed graph: fresh Stage05 followed by fresh Stage06. It has no `--through-stage`, source-run path, comparison/bundle/visual override, force/trust/ignore flag, decision migration flag, remote target, acceptance option, or replay selector. It resolves all upstream paths only from:

```python
authorities = validate_replayed_prefix(run_root, expected_through="04-visual-merge-bundle")
```

The new public API is `replay_resume_engine(run_root, decision_set, decisions_root)`. It may call the public `reconstruction.validate_decision_set()` after validating queue v2 itself. It must not call legacy `resume_engine`, `_validate_live_run_bindings`, `_validate_stage_prefix`, `_invoke_stage`, `_materialize_submission_snapshot`, or `production_resume_adapters`.

The additive downstream adapter exposes only:

```python
validate_replay_review_queue(authorities) -> ReplayReviewAuthorities
materialize_replay_submission_snapshot(authorities, decision_set, decisions_root) -> SubmissionAuthorities
replay_downstream_adapters(authorities, submission) -> {"fidelity_audit", "materialize_candidate"}
replay_resume_engine(...) -> ReplayResumeResult
```

Every returned path is fixed beneath the validated fresh `run_root`. The Stage05/06 scripts gain `replay-v3` entry points taking `--run-root` plus exact bridge/submission/audit hashes; they call `validate_replayed_prefix()` themselves before use. They do not accept individual Stage02-04 paths in replay mode.

### 2. Downstream state machine and receipts

State is derived from sealed artifacts; existing `result.json` is not overwritten.

| State | Required evidence | Permitted transition |
|---|---|---|
| `needs_review` | valid replay prefix/bridge; exactly Stage01-04; no Stage05/06 | seal a fresh validated submission |
| `submission_sealed` | `review/validated-submission-v2/submission_inventory.json`; exact fresh queue/bridge/decision/allowlist authority | execute Stage05 |
| `fidelity_passed` | passing audit v3 plus sealed `stages/05-fidelity-audit/stage.json` | execute Stage06 |
| `candidate_ready_for_reconstruction_qa` | sealed Stage06 manifest and candidate provenance v3 | idempotently return success; no acceptance |
| `needs_review` after audit | a sealed failure attempt containing the non-passing report | require a new external submission; do not publish Stage05/06 |

Unknown stage directories, output/manifest half-pairs, conflicting snapshots, a Stage06 without valid Stage05, or any Stage05/06 replay-mode receipt fail closed. Existing valid Stage05 may be revalidated and used only to continue the same fresh run after an interrupted Stage06; it is never imported from another run.

New canonical contracts:

- `validated_reconstruction_submission.v2`: fresh run identity, bridge SHA, queue SHA, contract/source SHA, exact decision set, page decisions, reviewed allowlist v3, complete files inventory and seal. Fixed path: `review/validated-submission-v2`.
- `replay_downstream_stage_manifest.v1`: only Stage05/06; `execution.mode=executed`, `producer_invoked=true`, `reusable=false`; fresh run/bridge authority; exact upstream receipts; exact typed inputs; current per-stage producer closure; output inventory; command receipt; timestamps/exit code; reproducible seal.
- `replay_resume_result.v1`: state, fresh run identity, bridge SHA, Stage05/06 manifest seals and candidate root hint. It contains no acceptance field other than `acceptance_inferred=false`.
- `mineru_ai_merge_provenance.v3`: only portable run-relative records for bridge, submission, comparison, packets, decisions, Stage05 audit and candidate files. Execution diagnostics may contain current fresh local paths, but no absolute path is permitted in reproducible manifests or candidate provenance.

Stage05 binds all four exact bridge stage rows, the bridge, queue, submission inventory, decision set/pages, allowlist v3, comparison v3, geometry v2, visual bundle v3 and audit policy/schema. Stage06 binds the Stage05 manifest/audit plus the same bridge and submission authority. The Stage05/06 manifest producer closure is captured immediately before invocation and recomputed after output validation; any concurrent file drift fails.

Each stage builds under a unique same-volume, contained, owner-marked sibling staging path. It validates output and manifest before no-replace publication. Because `outputs/` and `stages/` are separate canonical roots, publication uses a sealed commit intent and two renames; on interruption, recovery completes only an exact owner/intent/hash match, otherwise moves only the owned partial pair to quarantine. It never recursively deletes or moves an unverified Windows path. Stage06 cannot start until the Stage05 pair is fully published and revalidated.

### 3. G1 — positional visual assertions

Add allowlist/audit v3. A visual assertion row is closed and contains:

```text
assertion_id
source_page
text + original_text_sha256 + normalized_text_sha256
source_region {view_id, coordinate_space=mineru_page_1000_top_left_v1, bbox}
placement {
  relation = before_anchor | anchor_prefix
  anchor_unit = exact full unit identity
  expected_pair_sha256 = SHA256(normalized(assertion.text) + normalized(anchor.text))
}
visual {fresh Stage04 run-relative path, bytes, sha256}
visual_verdict = source_text_visible_at_region
rationale
```

`anchor_unit` must exist exactly once on the page, belong to a required succeeded view, have a non-null bbox, be selected exactly once and map to one monotonic Markdown span. The assertion uses the same view coordinate system. The fixed geometry predicates are:

- `before_anchor`: positive horizontal overlap and the assertion box precedes the anchor box in the same reading lane;
- `anchor_prefix`: positive vertical overlap and the assertion center lies in the leftmost 25% of the anchor box.

No row controls tolerances. The auditor normalizes boxes through the sealed Stage04 geometry authority and applies fixed policy constants. Failure to establish the predicate is an error, not a reviewer override.

Markdown proof is position-first, not search-first. After mapping selected units monotonically, the assertion span is exactly `[anchor_start-len(assertion_normalized), anchor_start]`; that slice must equal the assertion, be adjacent after Markdown/image syntax removal, and satisfy `expected_pair_sha256`. Assertions, selected spans and exact split/join equivalents are then sorted by Markdown span. The union must be non-overlapping, cover the normalized Markdown exactly once with no gaps, and preserve selected source order. Multiple assertions for the same `(anchor, relation)` are rejected in v3.

This closes both Dissociation cases without changing reader Markdown:

- p1 `DISSOCIATION` is `before_anchor` of selected `original_pipeline_txt:0` (`by matthew sanderson`);
- p2 `T` is `anchor_prefix` of selected `original_pipeline_txt:3` (`he mi-go ...`), yielding the already correct `The mi-go ...`.

Assertion characters are included in both the required and covered character totals. Appending either assertion at page end, selecting a stale anchor, ambiguous reuse, overlap, bbox contradiction, or a missing/extra Markdown character fails.

### 4. G2 — explicit cross-view OCR-equivalence classes

Add top-level `ocr_equivalence_classes` to reviewed allowlist v3. A class contains a unique id, source page, one exact canonical unit, one or two exact alternate units from distinct required views, exact fresh visual evidence, `visual_verdict=canonical_text_visible_alternate_text_absent`, and a non-empty rationale. Thresholds are fixed by audit policy, never row-supplied.

For each alternate the auditor must prove all of the following:

1. canonical unit is selected exactly once and has one exact Markdown span; alternate is unselected, belongs to another required succeeded view, and appears in no exclusion or other equivalence class;
2. both are reader-text block types on the same page and neither is page furniture;
3. Stage04 geometry converts both bboxes to `source_media_box_fraction_top_left_v1`; IoU is at least `0.50`, center distance at most `0.035` of the page diagonal, and neither box is missing;
4. NFKC/casefold lexical tokenization gives equal token counts, exactly one differing token, differing-token Levenshtein distance at most `1`, whole-string Levenshtein distance at most `2`, and whole-string similarity at least `0.92`;
5. the canonical normalized text is fully proven in Markdown and the exact fresh Stage04 visual identity is present in the sealed visual inventory.

A passing alternate receives `included_ocr_equivalent` with class id and computed metrics. Its corrupted spelling is not appended to the reader stream; its source unit is accounted exactly once by the selected canonical span. Exact automatic cross-view equality remains allowed only for a unique geometry-corresponding unit/span; the current unrestricted substring-in-any-anchor shortcut is removed.

`ocr_artifact` is not a way to discard a geometry-matched reader unit. In v3 it is permitted only for an exact OCR hallucination whose characters are visually absent **and** for which no geometry-corresponding reader unit exists in any required view. `non_reader` remains limited to visually proven folios, running furniture, advertisements or decoration; any body-region or canonical-matched text is rejected. Thus neither classification can substitute for an OCR-equivalence class.

For Dissociation p3, create one class with canonical selected `original_pipeline_txt:36`, text `Examining Vessels (Now and Later)`, and alternates `original_pipeline_ocr:36` (`fow`) plus `raster_pipeline_ocr:37` (`ow`). Their single-token edit distance is 1. Geometry must be evaluated after the crop/media-box transform; raw y coordinates from original and raster views must not be compared directly.

### 5. Run-07 decision migration and exact remediation set

`prepare-review` may create a draft only when source decision set contract/source hashes equal the fresh run; all six page decision bytes match their declared hashes; every selected block/asset exists in the byte-conserved fresh packet; comparison semantic projection and packet identities are those sealed by the fresh bridge; visual review is true; and unresolved lists are empty. The old queue hash is recorded as provenance but never accepted as fresh authority. The proposal contains a sealed per-page result and `acceptance_inferred=false`; any mismatch leaves that page open.

The six page-decision payloads may therefore remain byte-identical if the bridge proof and revalidation pass. The decision set must be regenerated with the fresh queue SHA. The reviewed allowlist is newly authored under v3 and explicitly reviewed; it is not migrated from run-07 (run-07 has none).

The closed Dissociation allowlist is: 24 exact exclusions from Packet G (2 cover `visual_only`, 20 `non_reader` folio/running-header units, 2 decorative footer units), 2 positional assertions (p1 title and p2 drop cap), and 1 OCR-equivalence class containing the two p3 alternates. The two p3 reader variants are removed from exclusions. Submission is explicit and remains reconstruction evidence, not artifact acceptance.

## Producer-closure consequence

No edit to any of the accepted 19 Stage01-04 producer-closure members is needed. In particular, do not modify `reconstruction.py`, `identity.py`, `manifests.py`, `mineru_cpu_first.py`, the Stage01-04 producer scripts, their v1/v2 producer schemas, or `MinerU/scripts/probe-capability.ps1` for Packet I.

G1/G2 and HR3 can land before replay because run-07 eligibility compares current hashes only for the stage-specific 19-path upstream closure. The audit, materializer, additive downstream module, new downstream contracts/tests and `kb_creator/__main__.py` are outside that closure. A fresh replay created afterward binds the current overall implementation in its fresh run identity; the Stage05/06 manifests additionally bind their smaller exact current producer closures. If implementation requires changing any of the 19 paths, stop: run-07 becomes ineligible and the no-full-CPU workflow is NO-GO.

## Implementation ownership packets

### I0 — prerequisite HR1/HR2 remediation

Owner: replay bridge engineer, then independent critic. Close P1-HR1HR2-01/02/03: no origin path interpretation; closed comparison v3; explicit typed geometry v2 and visual v3 fresh refs/recomputation. Packet I implementation remains blocked until the critic reports no P0/P1. No Packet I workaround may parse `semantic_projection` as an ambient authority.

### I1 — G1/G2 fidelity ledger

Owned changes: `scripts/audit_mineru_ai_merge_fidelity.py`; new `ai_merge_fidelity_reviewed_allowlist.v3.schema.json` and `ai_merge_fidelity_audit.v3.schema.json`; focused audit tests. Preserve legacy/v2 behavior only on explicit legacy modes. Implement the exact span, geometry, equivalence and forbidden-classification rules above.

### I2 — additive replay downstream control plane

Owned changes: new `pipeline/reconstruction_replay_resume.py`; additive dispatch only in `__main__.py`; closed queue-v2 runtime/schema hardening; new migration/submission/downstream-stage/result schemas; new focused replay-resume tests. Reuse only public validators. Do not edit or duplicate the Stage01-04 producer engine.

### I3 — replay-aware materializer

Owned changes: `scripts/materialize_mineru_ai_merge.py`; new provenance-v3 schema; materializer tests. Add the replay-v3 authority branch, require passing audit v3 and fresh bridge/submission authority, and emit only run-relative portable provenance. Do not add a legacy fallback from unknown v3 authority.

### I4 — bounded QA and live preflight

Owner: bounded QA. Run schema parsing, compile, focused suites, broad reconstruction regressions, synthetic full-prefix replay -> draft review -> submitted review -> Stage05 -> Stage06, path/identity poisoning, crash recovery and read-only live run-07 eligibility. No fresh live root is created until independent implementation review closes P0/P1.

## Required tests and adversarial acceptance

1. **Authority:** replay resume rejects missing/tampered bridge, old identity injection, generic projection authority, external/absolute/symlink/junction path, stale queue, wrong comparison/geometry/visual identity, partial prefix, Stage05/06 imported from another run, and any upstream closure drift.
2. **Fixed graph:** spies prove no MinerU/Stage01-04 adapter executes; CLI rejects Stage05-only/Stage06-only selection, source-run override, force/trust/decision-copy/acceptance flags; no Stage06 starts after a failing audit.
3. **Submission:** draft is rejected; exact submitted fresh queue binding passes; old queue hash, missing/extra/duplicate page, changed decision byte, unreviewed/unresolved page, absent selected unit/asset, stale/unused allowlist row and conflicting existing snapshot fail.
4. **G1 positive:** p1 title before author and p2 `T` prefix reconstruct the existing Markdown exactly. **G1 negative:** title after author, `T` at page end, wrong/unselected anchor, duplicate anchor/assertion, two candidate spans, bbox predicate failure, overlap, gap, extra or missing Markdown character all fail.
5. **G2 positive:** the two exact p3 variants pass only through the single class and produce the fixed distance/spatial metrics. **G2 negative:** distance 3, ratio below 0.92, two changed tokens, wrong page/view, selected alternate, unselected canonical, missing bbox/visual, IoU/center failure, duplicate class membership, canonical absent from Markdown, visually present alternate corruption, blanket raster `ocr_artifact`, or `non_reader` on a matched body unit all fail.
6. **Ledger:** all allowlist entries are used exactly once; assertions enter required/covered totals; equivalent units are covered once; normalized Markdown has complete non-overlapping span coverage; each Dissociation page has completeness `1.0`, no unaccounted unit and no errors.
7. **Stage receipts:** Stage05/06 schema/runtime parity, pre/post producer-closure equality, exact input/output inventories, truthful `executed/producer_invoked=true`, fixed fresh paths and no acceptance claim. Mutating audit, candidate or manifest after sealing fails.
8. **Windows transaction:** pre-existing destination, case/trailing-dot alias, ADS-like colon, reserved name, reparse point, cross-volume staging, publish race and interruption between the two canonical renames fail or recover only from the exact sealed owner intent; unrelated paths remain untouched.
9. **Synthetic E2E:** full replay prefix ends `needs_review`; draft migration remains unresumable; explicit fresh submission runs exactly Stage05/06 and ends `candidate_ready_for_reconstruction_qa`; no promotion or acceptance file exists.
10. **Live run-07 proof:** after I0-I3, read-only `verify-source --through-stage 04` still passes all 19 closure rows. Then, and only after independent closure, a new physical replay root can be created and the six-page workflow above executed without a full CPU/MinerU run. Run-07 and its decision directory remain byte-identical.

## Forbidden shortcuts

- Do not call legacy resume with patched acceptance of Stage v2/v3 or weaken old validators.
- Do not parse/dereference origin-vault paths, stale absolute paths or generic semantic projections as operational authority.
- Do not search/replace identities, use symlinks/hardlinks, manually copy files into a run root, mutate/reseal run-07, or accept partial/unknown authority.
- Do not auto-submit migrated decisions, copy an allowlist, infer review/acceptance, reuse another run's Stage05/06, or skip the fidelity audit.
- Do not append assertions to the reader stream, reorder correct Markdown, lower completeness below `1.0`, accept fuzzy text without exact class/geometry/visual proof, or relabel reader text as `ocr_artifact`/`non_reader`.

## Files checked

- active Dissociation plan/status and NRI goal governance; reconstruction skill;
- Packet G receipt and Packet H architecture/bridge/critic/engineering receipts, including the latest HR1/HR2 implementation critic NO-GO;
- `pipeline/reconstruction_replay.py`, `pipeline/reconstruction.py`, `pipeline/mineru_cpu_first.py`, `__main__.py`;
- fidelity auditor/materializer and their current tests/contracts;
- replay v2/v3 schemas, bridge, queue v2 and Stage v2 manifest;
- immutable run-07 comparison/geometry/visual/queue and p1-p3 decisions.

## Verdict

**GO for this Packet I architecture. NO-GO for implementation on the current HR1/HR2 base, and NO-GO for live replay.** Once I0 closes the independent critic's P1 findings, I1-I4 are additive downstream work with zero change to the 19-path upstream producer closure. If that invariant holds, the final fresh workflow can reuse run-07 Stage01-04, revalidate the six decisions, author the exact v3 allowlist, execute only fresh Stage05/06, and avoid a full CPU/MinerU rerun. Final acceptance remains a separate user-authorized promotion after reconstruction QA and independent release review.
