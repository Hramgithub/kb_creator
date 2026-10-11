# Critic receipt: Packet L run08 audit-v3 remediation implementation closure

- Timestamp: 2026-09-15T06:43:21+03:00
- Review kind: implementation
- Reviewer role: independent critic, gpt-5.5/medium per assignment
- Candidate implemented or materially designed by reviewer: no
- Orchestrator policy owner: main NRI orchestrator remains owner; this review does not transfer orchestration ownership
- Assignment state: completed after bounded interrupt recovery
- Scoped override: Packet L implementation/content closure only; no implementation edits, no run/decision/source/.tools mutation, no replay resume, no Stage06, no reconstruction acceptance, no promotion, no network/GPU/remote/API/Git commit
- Receipt immutability: this file is the only intended change by this review

## Authority and files checked

Primary handoffs:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_dissociation_run08_audit_v3_remediation_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_dissociation_run08_audit_v3_remediation_architecture_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_dissociation_run08_audit_v3_remediation_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_dissociation_run08_allowlist_v3_audit_20260915.md`

Implementation and schema inspected:

- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/contracts/ai_merge_fidelity_audit.v3.schema.json`
- `kb_creator/contracts/ai_merge_fidelity_reviewed_allowlist.v3.schema.json`
- `kb_creator/pipeline/reconstruction_replay_resume.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_reconstruction_replay_resume.py`

Run08 evidence inspected read-only:

- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08/run.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08/replay/bridge.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08/review/review_queue.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08/outputs/03-compare-views/comparison.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08/outputs/04-visual-merge-bundle/visual/geometry_plan.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08/outputs/04-visual-merge-bundle/visual/visual_manifest.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08/outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json` through `page-006.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/decision_set.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/pages/page-001.json` through `page-006.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/reviewed_allowlist.v3.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/validation/source-visible-completeness-audit.v3.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-08-decisions/validation/source-visible-completeness-audit.v3.remediated.json`

## Independent verification

Focused tests with the requested repo-local CPU interpreter and `.tools/python-test-deps` injection:

```text
$env:PYTHONPATH='.tools/python-test-deps'
& '.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe' -m pytest -q `
  'kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py' `
  'kb_creator/tests/test_reconstruction_replay_resume.py'

82 passed in 1.61s
```

Compile/schema/diff checks:

```text
py_compile: audit_mineru_ai_merge_fidelity.py, reconstruction_replay_resume.py,
            test_audit_mineru_ai_merge_fidelity.py, test_reconstruction_replay_resume.py
JSON Schema metaschema: ai_merge_fidelity_audit.v3, ai_merge_fidelity_reviewed_allowlist.v3
Result: compile_schema_ok
git diff --check: exit 0; only existing LF-to-CRLF working-copy warnings
```

I did not run a broad reportlab-dependent suite and did not install anything. No live replay, resume, Stage06, MinerU, network, GPU, remote, API, or commit operation was performed.

## Direct run08 audit result

I reran the v3 content audit in memory from the run08 replay prefix, external decisions root, and reviewed allowlist. The check revalidated the replay prefix, review queue, decision set, allowlist authority, packet-vs-comparison projections, visual inventory identities, and a production-shaped audit authority envelope before schema validation. It did not create `review/validated-submission-v2`, Stage05 output, or Stage06 output.

Direct evidence:

```json
{
  "run_identity_sha256": "D78CFBBC95AA51312C7339EAB3172D4CC8AA827801A42C23B3660104085E2F20",
  "bridge_sha256": "C61DFC69A9913ACB66817E98B2D5D4A510B75A1F182ADA52F94560127D69681B",
  "decision_set": {
    "bytes": 1446,
    "sha256": "6F44D4F236C4172F30CC21DD905C724ED9802DBC417A79F3A57F024C11AF46F5"
  },
  "reviewed_allowlist": {
    "bytes": 28483,
    "sha256": "DBEBC0B9713F5E260D290D03C89958A398A66DC27AE36531314D3D92908383B5"
  },
  "audit_schema_errors": 0,
  "passed": true,
  "errors": [],
  "page_count": 6,
  "page_results": [
    [1, true, 0, 1.0, 0],
    [2, true, 0, 1.0, 0],
    [3, true, 0, 1.0, 0],
    [4, true, 0, 1.0, 0],
    [5, true, 0, 1.0, 0],
    [6, true, 0, 1.0, 0]
  ],
  "dispositions": {
    "excluded_reviewed": 24,
    "included_equivalent_exact": 162,
    "included_equivalent_exact_subspan": 9,
    "included_ocr_equivalent": 2,
    "included_selected": 86
  }
}
```

The corrected p3 OCR geometry evidence is present in the in-memory audit:

```json
[
  {
    "iou": 1.0,
    "center_distance": 0.0,
    "smaller_box_coverage": 1.0,
    "token_levenshtein": 1,
    "string_levenshtein": 1,
    "similarity": 0.962962963
  },
  {
    "iou": 0.88000935235,
    "center_distance": 0.001078737218,
    "smaller_box_coverage": 0.94000999001,
    "token_levenshtein": 1,
    "string_levenshtein": 1,
    "similarity": 0.981132075
  }
]
```

Historical/remediated report identities:

```json
{
  "failed_report": {
    "bytes": 327470,
    "sha256": "98DE38C205949BB987D9AB5732BB5B6C6F95766E428B23239070FE25FD913C40"
  },
  "remediated_direct_evidence_report": {
    "bytes": 544386,
    "sha256": "1D7E04E28C396446A9315162E63FF5B88371D6B599F8577251D20308BC005EF4"
  }
}
```

The saved `source-visible-completeness-audit.v3.remediated.json` is direct evidence only. It has the old minimal authority envelope and does not validate as the closed Stage05 audit schema. The production-shaped in-memory report does validate with zero schema errors. Therefore the saved remediated JSON must not be promoted or substituted for a sealed Stage05 receipt, but this is not a blocker for running the dedicated replay-resume Stage05/06 path.

## Assessment

The implementation matches the accepted architecture:

- Canonical spatial comparison no longer uses raw `/1000` shortcuts; tests cover non-zero origins, CropBox offsets, rotations `0/90/180/270`, non-default UserUnit, effective displayed size mismatch, invalid boxes, non-finite values, missing/duplicate geometry, and out-of-frame bboxes.
- Whole-unit equivalence remains exact, same-page, cross-view, unique, geometry-bound, and selected-mapping-bound.
- Strict subspan equivalence is a separate exact-only route with selected canonical context, exact rendered Markdown span, geometry coverage, and overlap/reorder rejection. The run08 direct audit accounts for the expected 9 exact-subspan units.
- Reviewed running furniture is narrowly gated by exact allowlist rows, exact visual evidence, top-margin canonical geometry, multi-page same-view cohort, bounded one-character OCR variance, no rendered Markdown presence, and no reader/selected/equivalent correspondence. The run08 direct audit accounts for the expected 4 reviewed text running-furniture exclusions.
- The p3 OCR class is closed by canonical geometry metrics rather than threshold relaxation.
- The tests include adversarial crop/rotation/UserUnit geometry, ambiguous/duplicate exact equivalence, fuzzy/partial/overlap/reorder subspans, body/title/shifted/bottom/two-character/wildcard running-furniture attacks, and replay-resume audit/provenance authority checks.
- Decisions and allowlist were inspected read-only and not mutated by this review.

## Findings

### P0

None found.

### P1

None found.

### P2

1. The saved remediated direct-audit evidence file is not a closed Stage05 receipt and fails the closed v3 schema at `authorities` because it carries only the minimal direct-audit authority hashes. This matches the engineer receipt caveat and is safe only if the orchestrator treats it as evidence, not as a promotable Stage05 output. The production-shaped audit report generated in memory validates with zero schema errors.

## Recommendation

GO for the dedicated replay-resume path to run Stage05 and Stage06 for run08.

This is a technical authorization only. It does not approve reconstruction acceptance, publication, promotion, or any inference that the materialized candidate is final. The downstream run must still produce sealed Stage05/Stage06 evidence through the accepted replay-resume authority path, and any resulting candidate still requires its own reconstruction/content QA before acceptance.

## Elapsed time and token use

- Elapsed wall time: approximately 7 minutes in the recovered turn, plus approximately 5 minutes of preserved pre-interrupt evidence gathering
- Reviewer token use: exact tool total unavailable in this environment; active goal reported 126,609 tokens before the recovery receipt write
