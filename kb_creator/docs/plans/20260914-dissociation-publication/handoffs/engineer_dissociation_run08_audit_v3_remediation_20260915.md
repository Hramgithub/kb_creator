# Engineer receipt — run08 audit-v3 remediation

Date: 2026-09-15  
Role: engineering, `gpt-5.6-sol`, high (user-scoped override)  
Verdict: **implementation and direct content-ledger audit PASS; ready for independent closure.** No replay resume, Stage06, materialization, promotion, acceptance, MinerU, network, GPU, remote, or API operation was run.

## Result

- Implemented one canonical source-page geometry transform for every v3 spatial consumer. It validates exact MediaBox/CropBox/rotation/UserUnit geometry, maps bbox corners through the page rotation affine transform, checks the sealed effective displayed size, and fails closed on missing, duplicate, malformed, non-finite, out-of-frame, or inconsistent geometry.
- Implemented unique same-page cross-view whole-unit equivalence and a separate exact-only split/merge subspan disposition. Subspans require one selected canonical unit, one exact normalized occurrence, an existing selected Markdown mapping, monotonic non-overlapping Markdown spans, and canonical geometry containment.
- Implemented the narrow reviewed running-furniture guard for generic `text`: exact allowlist/visual evidence, a multi-page same-view top-margin cohort, bounded one-character OCR variance, co-location, absent Markdown text, and no reader/selected correspondence.
- Preserved legacy v1/v2 paths. The immutable run08 prefix, decisions, reviewed allowlist, and historical failed audit were not edited.

## Changed files

- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/contracts/ai_merge_fidelity_audit.v3.schema.json`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_reconstruction_replay_resume.py`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/validation/source-visible-completeness-audit.v3.remediated.json` (new direct-audit evidence only)
- this receipt

No member of the accepted Stage01-04 producer closure was modified by this packet.

## Verification

- Focused audit-v3 matrix: `73 passed in 0.71s`.
- Replay-resume integration regression: `9 passed in 1.23s`.
- Bounded relevant broad suite (audit v1/v2/v3, replay HR1/2, replay-resume, materializer): `235 passed in 7.92s`.
- Python compile: PASS for the audit implementation and both modified test modules.
- JSON Schema metaschema: PASS for `ai_merge_fidelity_audit.v3` and `ai_merge_fidelity_reviewed_allowlist.v3`.
- Scoped `git diff --check`: PASS.
- A larger collection containing control-plane/promotion tests was not executed because the existing local test dependency path lacks `reportlab`; collection stopped with `ModuleNotFoundError: reportlab`. No dependency was installed, as required.

Adversarial coverage includes non-zero page origins, CropBox offsets, rotations 0/90/180/270, non-default UserUnit, missing/duplicate/invalid geometry, page/view/identity mismatch, duplicate or ambiguous whole-unit candidates, fuzzy/partial/overlapping/reordered subspans, geometry misses, one-off/body/bottom/shifted/two-character header attacks, wildcard/missing visual evidence, and reader-correspondence downgrades.

## Direct run08 evidence

- Run identity: `D78CFBBC95AA51312C7339EAB3172D4CC8AA827801A42C23B3660104085E2F20`.
- Replayed-prefix bridge: `C61DFC69A9913ACB66817E98B2D5D4A510B75A1F182ADA52F94560127D69681B`.
- Prefix/review queue/decision set/reviewed allowlist and Stage03 packet projections were revalidated read-only before the audit.
- New report: `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/validation/source-visible-completeness-audit.v3.remediated.json`.
- Report identity: 544,386 bytes; SHA-256 `1D7E04E28C396446A9315162E63FF5B88371D6B599F8577251D20308BC005EF4`.
- Result: `passed=true`, 6 pages, 0 errors, page completeness `1.0` on every page.
- Unit dispositions: 86 selected, 162 exact-equivalent, 9 exact-subspan-equivalent, 2 reviewed OCR-equivalent, 24 reviewed exclusions. Of the 162 exact-equivalent units, 92 were already accepted by the previous consumer and the remediation closes the 70 formerly unaccounted exact alternates.
- Corrected p3 raster OCR-class metrics: IoU `0.880009352350`, center distance `0.001078737218`, smaller-box coverage `0.940009990010`; lexical token distance 1, string distance 1, similarity `0.981132075`.
- The old failed report remains byte-preserved at `validation/source-visible-completeness-audit.v3.json` (327,470 bytes; SHA-256 `98DE38C205949BB987D9AB5732BB5B6C6F95766E428B23239070FE25FD913C40`).

The new file is standalone direct content-ledger evidence. Its intentionally minimal authority envelope matches the prior direct-audit invocation and does **not** validate as the closed Stage05 report schema, which requires a materialized submission authority. Producing that receipt would require replay-resume/Stage05 execution and was explicitly out of scope. It must not be promoted or substituted for a sealed Stage05 receipt.

## Risks and next action

- P0: none found in the bounded implementation or direct ledger result.
- P1: independent review must confirm the new equivalence and running-furniture rules remain as narrow as the accepted architecture before any downstream execution.
- P2: the reportlab-dependent broad control-plane/promotion modules remain unexecuted in this environment; their Packet-I coverage was not altered by this packet.

Next action: independent critic closure. Only after GO may the orchestrator invoke the accepted downstream replay-resume path to create a schema-valid Stage05 receipt and Stage06 candidate; no acceptance may be inferred.
