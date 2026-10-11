# Viral v2 external verifier-report checkpoint

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-external-verifier-report`
- Owner: current `nri-engineer`, `gpt-5.6-terra` / `medium`
- Completion token: `READY_TO_RESUME_VISUAL_QA_V2`

## Objective and ownership

Add the external, canonical, candidate-bound v2 verification report required by
Slice 4. It must never be written inside or accepted as part of the candidate.

Owned paths:

- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_external_verifier_report_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required API/CLI

- Add optional `--report-path` for full v2 candidate verification only.
  Preflight-only and v1 routes reject/ignore no report silently: fail closed if
  report output is requested where unsupported.
- Report target must be explicit, absent, non-symlink, outside candidate, with
  an existing safe parent. Write canonical JSON through same-parent private temp
  then atomic rename; clean temp on failure.
- Schema `kb_creator.master_en_verification.v2` contains exactly:
  status, scenario id, candidate root name, candidate inventory digest,
  inventory-file SHA-256, publication-config SHA-256, source-PDF SHA-256,
  reconstruction-inventory SHA-256, verifier-script SHA-256, independently
  recomputed candidate metrics, review-unit count/groups/priority/hash.
- No timestamp, hostname, username, absolute/device path, acceptance state or
  user decision.
- Add an independent `validate_v2_verification_report(...)` API which
  canonical-parses the report and recomputes every binding from the current
  candidate/config/source/reconstruction/verifier before returning success.
- Candidate root/inventory remains unchanged and contains no report or sidecar.

## Tests/evidence

Add success, deterministic-two-report, existing path, symlink, in-candidate,
preflight/v1 misuse, interrupted atomic write and every-field tampering tests.
Run full verifier module, `py_compile`, real v1 preflight, no-builder-import and
diff checks. Write the exact receipt and return the token only when complete.

No builder/visual-QA/real config/evidence/candidate/Git/Step 8A changes.
