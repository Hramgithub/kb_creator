# Independent critic receipt: v2 source-visible text completeness implementation closure

- Review kind: implementation
- Candidate under review: v2 source-visible text completeness audit implementation described in `engineer_source_visible_text_completeness_audit_20260915.md`
- Verdict target: fresh reconstruction run `20260915-cpu-first-06`
- Critic role: independent implementation critic
- Implemented or materially designed candidate: no
- Orchestration ownership: remains with the main `20260914-dissociation-publication` orchestrator; this receipt does not transfer ownership
- Orchestrator policy owner: repository `AGENTS.md` plus `docs/governance/nri_goal_governance.md`
- Assignment state: complete
- Scoped override: implementation closure review only; no implementation, run, decision, source, `.tools`, live MinerU/PDF, network, GPU, remote/API, or Git mutation. This receipt is the only changed artifact.
- Timestamp: 2026-09-15T01:58:55.5881122+03:00
- Elapsed time: approximately 5.2 minutes of active goal accounting at receipt drafting
- Token use: goal tool reported 85,976 tokens used at receipt drafting

## Verdict

GO for a fresh local v2 reconstruction run `20260915-cpu-first-06`.

Do not resume pre-fix `20260915-cpu-first-05`; the implementation inventory changed and the engineer/architecture receipts correctly treat that run as stale.

## Files checked

- Governance, skill, and receipts:
  - `AGENTS.md`
  - `docs/governance/nri_goal_governance.md`
  - `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
  - `kb_creator/README.md`
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_source_visible_text_completeness_audit_20260915.md`
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_source_visible_text_completeness_architecture_20260915.md`
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_source_visible_text_completeness_audit_20260915.md`
- Bounded implementation surfaces:
  - `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
  - `kb_creator/scripts/materialize_mineru_ai_merge.py`
  - `kb_creator/pipeline/reconstruction.py`
  - `kb_creator/pipeline/reconstruction_promotion.py`
  - `kb_creator/contracts/ai_merge_fidelity_audit.v2.schema.json`
  - `kb_creator/contracts/ai_merge_fidelity_reviewed_allowlist.v2.schema.json`
  - `kb_creator/contracts/stage_manifest.v1.schema.json`
  - `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json`
- Tests inspected/run:
  - `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
  - `kb_creator/tests/test_materialize_mineru_ai_merge.py`
  - `kb_creator/tests/test_reconstruction_control_plane.py`
  - `kb_creator/tests/test_mineru_cpu_packet_b.py`
  - `kb_creator/tests/test_reconstruction_promotion.py`
  - `kb_creator/tests/test_reconstruction_promotion_adversarial.py`

## Static implementation evidence

- V2 mode is explicit in `audit_mineru_ai_merge_fidelity.py`; legacy mode is selected by `--mode legacy-v1`, while v2 requires queue, comparison, and decision-set authority arguments.
- The v2 ledger enumerates non-empty text units from the three required CPU views: `original_pipeline_txt`, `original_pipeline_ocr`, and `raster_pipeline_ocr`.
- The architecture critic's substring concern is closed: source-unit coverage is directional. A shorter selected/rendered substring cannot satisfy a longer source unit because the implementation checks whether the full normalized source unit is contained in selected anchors or their joined stream, not the inverse.
- The v2 gate has no low-text exemption. Short page starts and continuations fail unless covered or explicitly disposed.
- Ordered selected mappings use monotonic full Markdown spans; reordered selected blocks fail even with preserved multiset tokens.
- Source-text exclusions and visual assertions are closed, identity-bound, and unused rows fail. Production authority validation additionally binds visual evidence under fixed Stage04 visual output and checks `visual_only` against a selected logical asset referenced in Markdown.
- Stage05 cache inputs now include queue, comparison, decision, allowlist, and fidelity policy identities for v2.
- Stage06 requires exact Stage05 audit path/SHA, emits `kb_creator.mineru_ai_merge_provenance.v2`, and binds audit authorities in provenance.
- Promotion branches on run schema and rejects v2 downgrade/stale authority: v2 package verification requires v2 audit, v2 provenance, exact audit/provenance authority agreement, per-page completeness `1.0`, and zero unaccounted units.
- Legacy v1 audit and materializer behavior remain explicit and separate.

## File identity snapshot

These identities were captured without using Git:

- `audit_mineru_ai_merge_fidelity.py`: 34435 bytes / `E018F5DD3CF1DCC6B1A70595CBA24B5AA005C08AB5338A64C4E485F5067B563A`
- `materialize_mineru_ai_merge.py`: 35522 bytes / `23F6C7AC927A2FA9E3BADDB01C0A0C8C16B8B07297D977B8D23C5E26C93352F3`
- `reconstruction.py`: 94117 bytes / `81BE7DF8B95DA4B8BE970A8D557A28B79BDFA128F951E1F947F1299C702516B0`
- `reconstruction_promotion.py`: 62580 bytes / `536E0EB26751A472D9A286F2E6846F50114D36F151A4F51939E115F78BCAB8FC`
- `ai_merge_fidelity_audit.v2.schema.json`: 7582 bytes / `C4E06EF54BB4AEE840CF7E659AF961B70989490B13CE556F1BF840B07CEEF587`
- `ai_merge_fidelity_reviewed_allowlist.v2.schema.json`: 3752 bytes / `938C5CF7B8778E950CFFE2FA36AF9FE6F63E44D8F34798548F6A28CD07E89E20`
- `stage_manifest.v1.schema.json`: 4854 bytes / `7B9CBEE6DBC4DFD7F0787EB9662BBEA0513416319B5262516B6DB4008004CCB7`
- `test_audit_mineru_ai_merge_fidelity.py`: 10713 bytes / `DA9F4206CED1BBA599FA663906DA9DBD958B600F71602CBCB5115A0A792B8957`
- `test_mineru_cpu_packet_b.py`: 68643 bytes / `38C2442520DC4F5B5EAFF3D658FAC0BA6F156639626C80B99D9E7C1631002121`
- `test_reconstruction_control_plane.py`: 24473 bytes / `1CEADB70D4891B66CFC34005778A14EC4D2C9196DD1ACB50A27CC47EED63589A`
- `kb_creator/README.md`: 19289 bytes / `7F31140A77243BA429D78F16F6421C61D157CA2E41DBBEA7EE622CFCA8C0F114`

Git diff/status was not run because the task explicitly forbade Git. The bounded change set was checked from the engineer receipt and current file contents/identities instead.

## Verification run

- Initial environment check:
  - `.tools/MinerU/.venv/Scripts/python.exe -B -m pytest ...` failed because that Python has no `pytest`.
  - Codex bundled Python also lacked `pytest` until the existing repo-local `.tools/python-test-deps` path was added to `PYTHONPATH`.
  - No install/download was attempted.
- Focused suite:
  - Command used existing `PYTHONPATH=C:\_Hobby\_work\NRI\.tools\python-test-deps`
  - `test_audit_mineru_ai_merge_fidelity.py`
  - `test_materialize_mineru_ai_merge.py`
  - `test_reconstruction_control_plane.py`
  - `test_reconstruction_promotion.py`
  - `test_reconstruction_promotion_adversarial.py`
  - Result: `158 passed, 1 skipped in 34.39s`
- Broad engineer-declared regression:
  - Same existing `PYTHONPATH`
  - Added `test_mineru_cpu_packet_b.py`
  - Result: `186 passed, 1 skipped in 103.25s`
- In-memory compile check, without writing `.pyc`:
  - `audit_mineru_ai_merge_fidelity.py`: passed
  - `materialize_mineru_ai_merge.py`: passed
  - `reconstruction.py`: passed
  - `reconstruction_promotion.py`: passed
- JSON Schema draft-2020-12 meta-validation:
  - `ai_merge_fidelity_audit.v2.schema.json`: passed
  - `ai_merge_fidelity_reviewed_allowlist.v2.schema.json`: passed
  - `stage_manifest.v1.schema.json`: passed
  - `reconstruction_upstream_manifest.v1.schema.json`: passed
- Additional read-only targeted probes:
  - split selected units covering a longer equivalent raster unit: passed
  - duplicate selected unit rejection: passed
  - visual assertion present in Markdown when all extractors miss it: passed
  - missing visual assertion text: failed as expected
  - Result marker: `TARGETED_V2_PROBES_OK split_merge duplicate visual_assertion`

## Findings

### P0

None found.

### P1

None found.

### P2

None requiring remediation before the fresh run.

One residual boundary remains as designed: automatic completeness is limited to text extracted by at least one required CPU view. Text visible only to a human visual reviewer must be represented by an explicit visual assertion. The implementation enforces that assertion path rather than claiming impossible OCR-complete coverage.

## Recommendation

Proceed to fresh local run `20260915-cpu-first-06` under the new v2 implementation identity. Do not resume `20260915-cpu-first-05`. After the fresh run, decisions must be validated against that run's exact queue/comparison/packet/audit/provenance identities before any Stage05/Stage06, promotion, or release decision.
