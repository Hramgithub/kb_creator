# Engineer receipt: stage-scoped replay authority bridge

- **Timestamp:** 2026-09-15T03:54:12+03:00
- **Goal / packet:** `20260914-dissociation-publication`, Packet H / HR1-HR2 bounded implementation.
- **Role / scoped override:** engineering, requested `gpt-5.6-sol` at high; platform identity remains unverified.
- **Orchestrator policy owner:** main-chat `gpt-5.6-sol` at medium; ownership was not transferred.
- **Result:** **coherent full-prefix HR1/HR2 core implemented and tested; full Packet H is not closed and live replay remains NO-GO.** A required shorter-prefix/fresh-suffix route cannot be implemented without changing a declared Stage01-04 producer-closure member. HR3 downstream Stage05/06 consumption is not implemented in this bounded result.
- **Scope observed:** no immutable run, decision root, source, `.tools`, canonical plan/status/context, Stage01-04 producer file/schema, network, GPU, remote/API, Git commit, live replay, Stage05/06 execution, decision copy, or acceptance mutation.
- **Elapsed time:** approximately 40 minutes.
- **Token use:** unavailable.

## Implemented coherent boundary

The additive replay layer provides:

- a sealed, scenario-neutral four-stage dependency registry with exact direct-upstream rows, closed selectors, conservative implementation closures, validator ids and argv recipe ids;
- legacy v1 source validation through the historical run/stage seals and current semantic validators, followed by exact current/source producer-closure equality;
- exact runtime, contract, source, provider, profile, tool and portable-field equivalence checks;
- stable eligibility reason codes and per-stage eligibility keys that exclude local/run-id noise;
- a typed resolver with explicit per-view `view_artifact_root` scope and no `source_run_root` base;
- exact artifact classification, path-aware JSON/text scans and byte/structure routing for PDF/PNG/JPEG payloads;
- a thirteen-entry sanitized live run-07 wrapper fixture containing only repository-relative artifact names, never private payloads or the user source path;
- opaque origin-vault copies, typed view/view-set/comparison/replay-command rebasing, projection hashes, conservation receipts, Stage v2 receipts and a final bridge;
- physical `xb` writes, flush/fsync/reopen verification, hardlink/reparse/ADS-like colon/traversal/device/trailing-alias/case-collision checks, distinct physical copy proof, exclusive same-volume sibling staging, no-replace publish, narrow marker-owned cleanup and post-publish quarantine;
- fresh queue/template generation with `acceptance_inferred=false`, `decisions_replayed=false`, and `stages_05_06_replayed=false`;
- dedicated `python -m kb_creator replay verify-source|run` dispatch. It has no default/latest source, force/trust/ignore flag, decision-copy route, remote route, or Stage05/06 selector.

The full-prefix synthetic run reaches only `needs_review` with exit `10`. Legacy resume does not accept Stage v2 receipts, so an incomplete bridge cannot silently enter the old downstream path.

## Upstream closure proof

No file in the accepted 19-path Stage01-04 producer union was edited. The read-only live command

```text
python -m kb_creator replay verify-source ... --source-run-root 20260915-cpu-first-07 --through-stage 04-visual-merge-bundle ... --json
```

passed against exact local receipts without creating a target. Eligibility seal: `6264B4D1A3A5FDD0DB2944F2E925C3DEEDA9673688FE00BE869DADD073115114`.

| Stage | Current/source-equal closure SHA-256 | Source manifest seal | Source output inventory |
|---|---|---|---|
| 01 | `943B3ED924167FC1648815FA40610C5A2061F5760C7F9773AB832A5A9A9E0B89` | `8CE1FB4231A918A05CAE4E0E5B4057D722854E33AD428895316C832D6CE746BC` | `64C43C2A82AE078DFE71B98091998E35F36A276437BFDE7E27A7C52A8F6DAF7D` |
| 02 | `E386EB483F76ECD87AEEF267030FB897D0211A88570ED77384D8D7B53233202A` | `0FF911385B13EDF3F524BFA555ED38B8E0AA642903EED341C060390C09FA7A62` | `6CEE0F07679E845763B21A04D9BDAF99614ED261255CDFDEA182F1F828BA7B63` |
| 03 | `BF1903B2BFB10811D48A69ECFBA53B8C51FD2B3036D4661D82C8C79C4E0C69A6` | `C1EA6EF8CF8AC4E978B0FDE59D0A50C8144EF15ABA796DB5C3D5786F58874ABB` | `E06E0D3A697D1DF0C3C28E05958D4F53C3E3F1886DE537DF1F626D764F2AB995` |
| 04 | `44DC6F29489E778DA420B02E7BB1528B3ECB01D663CAF72705390B07D0589AC1` | `2AFD79D9AAE71E043162F8C2D31445F95EF9D2EF6E5A20F9CD758CD49922023A` | `8C9F21589173B42226ADB42219C5E8BE00391294770093B4A76055BAB5FFF806` |

Registry internal seal is `B4F439FDF6425820B41676D5D04F08497838A16989751AC3BE2C4113DD5D244C`; its current file identity is `5793` bytes / `1A53C4C9E0C2DF98D849E0F3D420D581C0BC9EF8013329EFA626040356582950`.

## Verification

- Focused replay suite: **55 passed**.
- Relevant broad regression set (`test_reconstruction_replay`, reconstruction control plane, Packet B, fidelity audit, materializer): **166 passed in 120.86s**.
- Synthetic E2E: executed-fixture S1-S4 graph -> typed full-prefix replay -> fresh physical root -> sealed bridge/queue -> terminal `needs_review`; upstream producer invocation is represented truthfully as false, no Stage05/06 output or acceptance claim exists.
- Adversarial coverage includes closed prefix aliases; Stage05/06/gap/latest rejection; drive/UNC/device/traversal/backslash/reserved/trailing aliases; typed per-view cross-scope rejection; succeeded/skipped projection; resealed unknown/tampered view; absolute/old-identity projection poisoning; binary-vs-text scan routing; physical identity/hardlink/root nesting/pre-existing target; exact 13-wrapper coverage; unknown artifacts; semantic comparison mutations; forbidden CLI flags/routes; schema parsing and implementation-inventory binding.
- `py_compile`: clean for replay module, CLI and focused tests.
- Draft 2020-12 schema parsing: all 13 replay schemas pass; registry instance validates against its schema.
- `git diff --check` on the owned files: clean.

## Exact changed files

- `kb_creator/__main__.py` — additive replay CLI only; explicitly absent from the S1-S4 producer closure.
- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/contracts/reconstruction_stage_dependency_registry.v1.json`
- `kb_creator/contracts/stage_dependency_registry.v1.schema.json`
- `kb_creator/contracts/stage_replay_intake.v1.schema.json`
- `kb_creator/contracts/stage_rebase_receipt.v1.schema.json`
- `kb_creator/contracts/stage_replay_bridge.v1.schema.json`
- `kb_creator/contracts/stage_manifest.v2.schema.json`
- `kb_creator/contracts/replay_command.v1.schema.json`
- `kb_creator/contracts/mineru_view_execution.v2.schema.json`
- `kb_creator/contracts/mineru_view_set.v2.schema.json`
- `kb_creator/contracts/mineru_multi_view_comparison.v3.schema.json`
- `kb_creator/contracts/mineru_geometry_plan.v2.schema.json`
- `kb_creator/contracts/mineru_visual_merge_bundle.v3.schema.json`
- `kb_creator/contracts/visual_replay_execution.v1.schema.json`
- `kb_creator/contracts/review_queue.v2.schema.json`
- `kb_creator/tests/test_reconstruction_replay.py`
- this receipt.

## Blockers and risks

### P1-H-implementation-01 — shorter-prefix fresh suffix requires a frozen producer change

The accepted CLI permits prefixes ending at 01, 02, 03 or 04. A prefix ending before 04 must freshly invoke the remaining upstream stages. Current `reconstruction.py` exposes only a complete Stage01-04 `run_engine`; it has no safe start-at-stage/supplied-prefix entry point. Adding that entry point requires editing `kb_creator/pipeline/reconstruction.py`, which the accepted registry and user packet explicitly freeze as a common producer dependency. Per the stop rule, this implementation rejects 01/02/03 run requests before destination creation with `partial_prefix_execution_not_implemented`; it does not pretend they succeeded.

### P1-H-implementation-02 — downstream replay consumers are not closed

The existing Stage05 auditor and Stage06 materializer still consume legacy operational schemas. They were not edited in this bounded coherent result, so replayed runs cannot yet resume. Full typed Stage03/04 recomputation and downstream `FreshReplayAuthorities` consumption still require HR3 work and independent tests. No claim is made that the current replay envelopes are accepted by those consumers.

### P2-H-implementation-03 — nested schema/runtime parity needs hardening

All schemas close their top-level object and runtime validators reject the exercised extra/missing fields, but several provenance/inventory subobjects remain intentionally generic at this boundary. Before live use, HR3 must close every nested shape and add producer-shaped v1-to-v2/v3 golden fixtures for every optional GPU state and dynamic 3-5-view topology.

## Verdict and next action

The result is safe as a tested, additive **full-prefix HR1/HR2 development boundary**, but it is **not ready for independent implementation closure or live replay**. The orchestrator must decide between:

1. approve a new architecture revision that adds a start-at-stage API to the producer closure, knowingly invalidating run-07 and requiring one fresh upstream execution; or
2. narrow replay v1 to exact S1-S4 only, then authorize HR3 downstream adapters/schemas/tests without touching the producer closure.

Do not run `replay run` against Dissociation until that decision, HR3 completion, and an independent critic close P0/P1.
