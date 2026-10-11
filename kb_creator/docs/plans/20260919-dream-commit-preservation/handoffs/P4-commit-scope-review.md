# P4 commit-scope review receipt

- goal_id: 20260919-dream-commit-preservation
- step_id: P4
- review_kind: process
- role: independent critic
- requested_model_effort: gpt-5.5 medium
- actual_model_effort: unavailable
- implemented_or_materially_designed_candidate: no
- orchestrator_policy_owner: gpt-5.6-sol medium
- assignment_state: platform-unverified
- scoped_override: none
- timestamp: 2026-09-19T14:31:23.2277328+03:00
- elapsed_time: unavailable
- token_use: unavailable

## Scope

Read-only review of frozen Number 7 Dream production package integrity,
provenance, offline verification, ignored-file boundary, Git/LFS/size risks,
secret or machine-local leakage risks, and whether commit preparation can claim
release status.

Checked paths:

- `kb_creator/docs/plans/20260919-dream-commit-preservation/plan.md`
- `kb_creator/docs/plans/20260919-dream-commit-preservation/context.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/working/number-7-dream/publication/20260919-publication-30/outputs/70-production-package/artifacts/package`
- `kb_creator/inputs/number-7-dream/production`
- `.gitignore`
- `.gitattributes`

Forbidden scope respected: no code/package/canonical status edits, no Git index
mutation, no commit, no deletion.

## Evidence

- Source run30 package and proposed tracked copy each contain 212 files and
  52,335,837 bytes.
- Full SHA-256 identity comparison between source package and tracked copy:
  `IDENTICAL`.
- Manifest:
  - schema: `kb_creator.production_package_manifest.v1`
  - scenario_id: `number-7-dream`
  - package_state: `candidate_for_release_review`
  - release_state: `not_reviewed`
  - manifest_sha256:
    `930965C745E0889B931CED46D738C94A0DCEB393F38F20CD913CFF42BC60B2C8`
  - manifest inventory: 211 files, excluding `PRODUCTION_MANIFEST.json`
  - stage manifests: 8
  - acceptance receipts: 6
  - assets role count under `assets/`: 20
  - PDFs in package: 1
- Offline verifier run with bundled Codex Python:
  `python.exe kb_creator\inputs\number-7-dream\production\pipeline\verify.py --package-root kb_creator\inputs\number-7-dream\production`
  returned:
  `{"html_local_reference_count": 20, "manifest_sha256": "930965C745E0889B931CED46D738C94A0DCEB393F38F20CD913CFF42BC60B2C8", "pdf_count": 1, "release_state": "not_reviewed", "schema": "kb_creator.production_package_verification.v1", "state": "candidate_for_release_review"}`.
- `README.md` inside the package says: `State: candidate_for_release_review.
  This package is not a release.`
- `git check-ignore -v` shows the run30 working package remains ignored by the
  repo default-deny rule, while `kb_creator/inputs/number-7-dream/production/**`
  is unignored by the tracked inputs exception and the Number 7 Dream PDF
  exception.
- `git ls-files --others --exclude-standard
  kb_creator/inputs/number-7-dream/production` reports 212 untracked files.
- `.gitattributes` marks `kb_creator/inputs/number-7-dream/production/**`
  `-text` and marks `Number_7_Dream_RU.pdf` for LFS.
- `git check-attr` confirms the production PDF has `filter=lfs diff=lfs
  merge=lfs -text`; DOCX and PNG package assets are binary/text-unset but not
  LFS-filtered.
- Targeted content scan for credential and local-machine markers found no
  credential material and no hard-coded user workspace paths. Matches were
  false positives in scenario prose (`secret place`) and generic code snapshot
  references to `LOCALAPPDATA` / AppData temp detection.

## Findings

- HIGH: none.
- MEDIUM: none.
- LOW: The tracked package is about 52.3 MB and includes duplicated binary
  payloads such as two 5.1 MB DOCX files and repeated cover PNGs. Only the
  production PDF is LFS-filtered. This is consistent with the current
  `.gitattributes` policy for this package, but the commit will still add
  substantial regular Git binary history.
- INFO: The Windows `py` launcher cannot run Python in this environment
  (`No installed Python found`), so repeatable verifier execution should use
  the bundled Codex Python path or another discovered Python, not bare `py`.
- INFO: The copied package is a release candidate only. Both manifest and
  verifier state are `candidate_for_release_review` / `not_reviewed`; commit
  preparation must not be described as release approval.

## Blockers

None for preparing a scoped commit, provided the staging step keeps the package
state wording as candidate-only and the user accepts the recorded binary size
policy.

## Recommendation

Proceed with commit preparation for the tracked production copy and reusable
pipeline changes, with these constraints:

- do not stage ignored `kb_creator/working/**` outputs;
- do not claim release approval or final release state;
- before the actual commit, review the final staged inventory for unrelated
  files and decide explicitly whether the non-LFS binary footprint is acceptable.

Any mutation of `kb_creator/inputs/number-7-dream/production/**` invalidates the
offline verification evidence above and requires a fresh verifier run and
review receipt.
