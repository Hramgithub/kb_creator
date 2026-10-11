# Critic receipt: Packet L run08 audit-v3 remediation architecture review

- Timestamp: 2026-09-15T06:18:34+03:00
- Review kind: architecture
- Reviewer role: independent critic, gpt-5.5/medium per assignment
- Candidate implemented or materially designed by reviewer: no
- Orchestrator policy owner: main NRI orchestrator remains owner; this review does not transfer orchestration ownership
- Assignment state: completed
- Scoped override: Packet L architecture review only; no implementation edits, no code/run/decision/source/.tools mutation, no live replay/resume, no acceptance, no Git commit
- Receipt immutability: this file is the only intended change by this review

## Authority and files checked

Primary architecture:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_dissociation_run08_audit_v3_remediation_20260915.md`

Evidence inspected read-only:

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
- Prior Packet G/I/J/J2/J3 critic/engineer receipts as boundary context
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py` for current v3 behavior boundaries

## Evidence

Architecture scope and root cause:

- The architecture correctly classifies current Stage05 as NO-GO and a bounded consumer implementation packet as GO.
- The proposed root cause is downstream v3 ledger semantics, not decision omission or upstream replay drift:
  - the direct audit report is failed, not reusable;
  - the run08 Stage01-04 prefix validates as an eligible replay prefix;
  - all six page decisions are byte-identical to run07 page decisions;
  - `decision_set.json` differs from run07 only as an expected authority-bound wrapper, not as page content mutation;
  - the reviewed allowlist has the stated 24 exclusions, 2 visual assertions, 1 OCR class, and 0 substitutions.

Direct audit arithmetic:

```json
{
  "audit_bytes": 327470,
  "audit_sha256": "98DE38C205949BB987D9AB5732BB5B6C6F95766E428B23239070FE25FD913C40",
  "schema": "kb_creator.ai-merge-fidelity-audit/v3",
  "passed": false,
  "global_error_count": 84,
  "unaccounted_errors": 79,
  "header_errors": 4,
  "ocr_errors": 1,
  "other_errors": 0,
  "page_error_counts": {
    "1": 0,
    "2": 18,
    "3": 18,
    "4": 17,
    "5": 8,
    "6": 23
  }
}
```

No unused-allowlist, authority, schema, selected-mapping, proof-stream, assertion, or other errors were present in the failed report.

Decision/allowlist check:

```json
{
  "allowlist_bytes": 28483,
  "allowlist_sha256": "DBEBC0B9713F5E260D290D03C89958A398A66DC27AE36531314D3D92908383B5",
  "allowlist_counts": {
    "source_text_exclusions": 24,
    "visual_text_assertions": 2,
    "ocr_equivalence_classes": 1,
    "substitutions": 0
  },
  "page_decisions_equal_run07": true
}
```

Replay prefix check:

```json
{
  "valid_replay_prefix": true,
  "bridge_sha256": "C61DFC69A9913ACB66817E98B2D5D4A510B75A1F182ADA52F94560127D69681B",
  "comparison_exists": true,
  "geometry_plan_exists": true,
  "visual_manifest_exists": true
}
```

Independent text-match census:

```json
{
  "unaccounted_units": 79,
  "unique_exact_hash_matches": 70,
  "not_unique_exact_hash_matches": 9
}
```

The nine non-exact-hash examples are exactly the p5 split pair and p6 statblock segment population identified in the architecture; the audit report itself does not carry normalized text strings, so the final substring/Markdown-span proof must be implemented and tested in the consumer as specified.

## Architecture assessment

### Canonical geometry

The architecture correctly rejects the current raw `/1000` shortcut. It requires one shared source-page coordinate helper for all spatial consumers, using sealed MediaBox, CropBox, rotation, UserUnit, and effective displayed size. It also requires fail-closed behavior for missing/duplicate geometry rows, invalid boxes, unsupported rotation, bad UserUnit, CropBox outside MediaBox, and bbox frame violations.

This is sufficient and necessary. Comparing crop-local MinerU fractions across original and raster views is the observed p3 OCR-equivalence failure mode and would also make automatic exact equivalence unsafe.

### Exact whole-unit and strict-subspan equivalence

The design preserves the Packet I v3 intent while closing the new run08 shape:

- whole-unit equivalence remains exact normalized text plus unique same-page cross-view selected candidate plus canonical geometry bounds;
- strict-subspan equivalence is explicitly separate, exact-only, unique, Markdown-span-derived, geometry-contained, and non-overlapping;
- it forbids fuzzy text, cross-canonical concatenation, ambiguous phrases, same-view/page misuse, duplicate proof-stream content, and arbitrary v2-style substring containment.

This is a GO-level architecture. Required implementation tests must prove that the nine split/merge cases pass and that repeated/fuzzy/ambiguous/overlap/reorder/concatenation attacks fail closed.

### Repeated running-header guard

The repeated-running-furniture guard is appropriately narrow. It requires existing exact reviewed exclusions, exact visual identity, multi-page same-view cohort, top-margin canonical geometry, co-location, bounded one-character OCR tolerance only within the cohort, absent Markdown text, and no body/selected/equivalent correspondence.

This avoids the forbidden shortcut of relabeling arbitrary `text` blocks as `non_reader`. Required tests must include both run08 positive cohorts and body/title/shifted/bottom/two-character/wildcard/selected-overlap attacks.

### p3 OCR geometry evidence

The architecture gives a concrete p3 metric target after canonical transform: `IoU = 0.880009352350`, normalized center distance `0.001078737218`. It explicitly forbids threshold relaxation and keeps the existing reviewed OCR-equivalence row byte-identical. That is the right architectural boundary.

### Decision/allowlist mutation

I agree with the architecture: existing decisions and allowlist do not need semantic mutation. Adding 79 exclusions, changing unit ids, or editing Markdown would be weaker than the proposed consumer fix and would misclassify reader evidence.

## Findings

### P0

None found.

### P1

None found.

### P2

None found.

## Required implementation tests

Any implementation packet should include at minimum:

1. Canonical coordinate transform tests for MediaBox/CropBox offsets, non-zero origins, rotations `0/90/180/270`, valid non-default UserUnit, and agreement with `effective_displayed_size_points`.
2. Fail-closed geometry tests for missing/duplicate geometry rows, unsupported rotation, bad/non-finite/reversed bbox, non-positive UserUnit, CropBox outside MediaBox, and bbox outside `0..1000`.
3. Live-shaped p3 OCR test asserting corrected `IoU=0.880009352` and center distance `0.001078737`, and asserting old raw-frame metrics are not used.
4. Exact whole-unit equivalence positives for the 70 run08 alternates and attacks for wrong page, same view, duplicate candidate, geometry miss, and missing selected Markdown mapping.
5. Exact-subspan positives for p5 and p6 nine units, with substring offsets, Markdown spans, geometry containment, and no extra proof-stream item.
6. Exact-subspan attacks for repeated phrase, fuzzy edit, multi-canonical concatenation, ambiguous geometry, selected overlap, wrong page, duplicate mapping, reordered/overlapping spans.
7. Repeated-running-header positives for the two run08 cohorts and attacks for one-off top text, body repeated title, bottom text, shifted peer, two-character corruption, missing visual identity, wildcard row, selected/body correspondence.
8. Full direct run08 audit using byte-identical decisions/allowlist: `passed=true`, no page errors, no unaccounted units, authority hashes unchanged.
9. Replay boundary test proving Stage01-04 seals remain unchanged and Stage05 binds the new audit consumer closure before Stage06 can run.

## Forbidden shortcuts

- No raw `bbox/1000` spatial comparison across views.
- No global OCR/geometry threshold relaxation.
- No adding 79 manual exclusions or blanket reader suppressions.
- No `text -> non_reader` downgrade without the full repeated-running-furniture cohort proof.
- No return to v2 arbitrary substring or joined-anchor containment.
- No fuzzy subspan matching, multi-unit concatenation, duplicate proof-stream insertion, or Markdown auto-edit.
- No ignoring geometry/content/reader evidence to make the audit pass.
- No mutation of sealed Stage01-04 replay prefix, source packets, decisions, or allowlist as a substitute for the consumer fix.

## Recommendation

Current Stage05: NO-GO.

Bounded implementation of Packet L architecture: GO, subject to independent implementation closure.

After implementation and review, rerun the direct Stage05 audit against byte-identical run08 decisions/allowlist and only then proceed through the accepted replay-resume Stage05/06 authority. This receipt does not approve Stage06, reconstruction acceptance, promotion, or publication.

## Elapsed time and token use

- Elapsed wall time: approximately 18 minutes
- Reviewer token use: unavailable exactly in this environment; approximately 13k tokens
