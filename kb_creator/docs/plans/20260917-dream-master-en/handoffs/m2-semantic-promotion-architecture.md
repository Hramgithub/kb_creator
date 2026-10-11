# M2 semantic-structure promotion bridge architecture receipt

## Receipt

- Goal: `20260917-dream-master-en`; milestone: `M2`.
- Scope: shared reconstruction-promotion support for Stage 06 candidates that
  carry the reviewed `SEMANTIC_STRUCTURE.json` sidecar. This receipt specifies
  remediation only; it does not authorize or perform implementation,
  reconstruction acceptance, publication, or release.
- Result: `SPEC_READY`. The promotion failure is a shared bridge-contract lag,
  not a defect in the accepted Dream candidate.
- Orchestrator policy owner: `gpt-5.6-sol`, medium.
- Assignment: architecture/root-cause analysis, `gpt-5.6-sol`, high;
  assignment state `completed`; orchestration ownership remains with the main
  chat.
- Scoped override: none.
- Timestamp: `2026-09-17T23:54:57+03:00`.
- Elapsed time: approximately 18 minutes.
- Token use: approximately 17k tokens.

## Root cause and dependency trace

The current replay-v4 producer is internally closed:

1. A `kb_creator.reconstruction_decision_set.v2` declares
   `semantic_structure_profile: visually_reviewed_semantic_containers_v1`.
2. `reconstruction_replay_resume.build_replay_audit` selects the v4 fidelity
   auditor for that decision-set schema and recomputes semantic structure from
   the reviewed page decisions, merge packets, geometry, and sealed visual
   inventory.
3. Stage 06 independently validates the same structure, requires its
   `structure_sha256` to equal the v4 audit value, and emits
   `SEMANTIC_STRUCTURE.json` bound to the submission, fidelity audit, and every
   page-decision SHA-256.
4. The Stage 06 manifest inventories the sidecar as an exact output.

The promotion consumer predates step 3. In
`pipeline/reconstruction_promotion.py` it still requires exactly seven
top-level candidate entries at lines 609-620 and accepts only legacy page
decision key sets at lines 645-653. It therefore rejects the valid replay-v4
candidate before reaching the already sealed Stage 06 inventory comparison.
Its materializer also copies only three root content files at lines 889-894,
so merely relaxing the shape check would silently drop the sidecar.

Current Dream evidence proves the coherent structural triad:

- fidelity audit schema: `kb_creator.ai-merge-fidelity-audit/v4`;
- decision-set schema/profile: `kb_creator.reconstruction_decision_set.v2` /
  `visually_reviewed_semantic_containers_v1`;
- sidecar schema/profile:
  `kb_creator.reconstruction_semantic_structure.v1` /
  `visually_reviewed_semantic_containers_v1`;
- all three authorities bind submission
  `E7115387F10D2E5CE48450FEF7B48DE224A4456522EDD6C54359C86C2D034969`;
- audit and sidecar bind structure
  `155ACBF7EB4099ECD670868D4C6088B87F5FD9C269D5FFEF82B50A49E68D8785`;
- the Stage 06 inventory contains `SEMANTIC_STRUCTURE.json` and the sidecar
  contains 26 ordered page-decision identities.

## Required generic remediation

### 1. Select the candidate profile from sealed authority, not file presence

Define a structural mode only when all of the following are true:

- the replay submission's decision set has schema
  `kb_creator.reconstruction_decision_set.v2` and the fixed supported profile;
- the recomputed/passed fidelity audit has schema
  `kb_creator.ai-merge-fidelity-audit/v4` and the same profile;
- the audit authority binds the current replay submission.

For this mode, the exact candidate root is the existing seven entries plus
`SEMANTIC_STRUCTURE.json`. Every page decision must have the existing base
keys plus `semantic_structure`; `block_boundaries` remains independently
optional, so only the two exact structural variants (with or without
`block_boundaries`) are allowed.

For legacy/direct/replay-v3 modes, retain the existing exact seven-entry root
and existing decision-key variants. A sidecar or a page-level
`semantic_structure` key in those modes is an unadvertised semantic upgrade
and must fail closed. Conversely, v4/v2 authority without the sidecar or
without page semantic structure must fail closed; there is no downgrade to a
non-structural candidate.

### 2. Validate the Stage 06 sidecar before any write

Add one shared internal validator used by promotion preflight and package
reopen validation. It must enforce:

- exact top-level keys from
  `reconstruction_semantic_structure.v1.schema.json`, exact schema/profile,
  and an ordered page domain equal to the reconstruction contract;
- the base projection `{schema, profile, pages, structure_sha256}` is exactly
  equal to the freshly recomputed v4 audit's `semantic_structure` object;
- `submission_sha256` equals the validated replay submission seal;
- `fidelity_audit` has the fixed run-relative path
  `outputs/05-fidelity-audit/audit.json` and the exact byte/hash identity of
  the validated Stage 05 audit;
- `page_decisions` is exactly ordered by source page, has only
  `{source_page, sha256}`, and each digest equals both the submission record and
  the copied Stage 06 decision file;
- all hashes are uppercase SHA-256 and no duplicate/missing page is tolerated.

The preflight already rebuilds the replay audit from sealed source authorities;
exact equality to that audit is the independent semantic recomputation. Do not
trust the sidecar's self-description or validate only its JSON schema.

Return the validated sidecar (or `None` for an older profile) in the candidate
context so the materializer cannot make a second, file-existence-based profile
decision.

### 3. Copy and seal without changing the four-role publication contract

For a structural candidate, copy the sidecar byte-for-byte to the fixed package
path `content/SEMANTIC_STRUCTURE.json`. Keep the existing upstream inventory at
exactly four roles:

- `reconstructed_en`;
- `reconstruction_manifest`;
- `reconstruction_qa`;
- `source_identity`.

The sidecar is subordinate reconstruction content/evidence, not a fifth
publication artifact role. Adding a role would unnecessarily break the
publication blueprint/contract schemas and all existing consumers that
correctly require the exact four-role interface.

The unchanged manifest schema can already seal the sidecar through three
existing closures:

- `manifest.candidate.files` records the exact Stage 06 product;
- `manifest.content.files` records `content/SEMANTIC_STRUCTURE.json`;
- `manifest.package_files` records the complete package.

Do not rewrite the sidecar during copy. On reopen, require equal byte/hash
identity between its `candidate.files` record and the fixed content copy, then
revalidate its audit/submission/page-decision bindings against packaged
authorities. `content/SEMANTIC_STRUCTURE.json` must be present if and only if
the packaged fidelity authority is v4. Existing non-structural packages remain
valid without it.

Add `content/SEMANTIC_STRUCTURE.json` to the reconstruction acceptance
receipt's evidence array only in structural mode. Acceptance still names
`artifact_kind: reconstructed_en`, but now explicitly binds the semantic
evidence needed to interpret that Markdown. The receipt validator must derive
the expected evidence set from the validated package profile: the historical
five records for old packages, those five plus the sidecar for structural
packages.

### 4. Bind the bridge implementation identity

Because promotion will now interpret the semantic contract, add these reusable
files to its implementation inventory:

- `kb_creator/pipeline/semantic_structure.py` if the shared validator imports
  or calls it;
- `kb_creator/contracts/reconstruction_semantic_structure.v1.schema.json`;
- any v4 audit/page-semantic schema directly consumed by the implementation.

Do not add Dream-specific code or a `build_number_7_dream_*` route. Code,
schemas, tests, and this receipt are Git-visible reusable changes; generated
promotion output stays under ignored `kb_creator/working/**`.

## Fail-closed and atomicity requirements

- Profile selection must never depend solely on whether a filename happens to
  exist.
- Candidate root, page decision key sets, Stage 06 inventory, package content
  inventory, and package topology remain exact closed sets.
- A missing/tampered/stale/extra sidecar, mismatched structure hash, stale audit
  identity, wrong submission seal, reordered/duplicate page identities, or a
  symlink/reparse point must fail before publication.
- Continue to stage under the fixed hidden directory, publish by no-replace
  rename, reopen-validate, and roll back only the unchanged package created by
  the current invocation. Never remove a pre-existing destination.
- Recording acceptance must remain exclusive-create. If post-write validation
  fails, remove only the exact receipt written by that invocation.

## Regression specification

Focused tests must cover at least:

1. Structural positive path: v2/profile decisions + v4 audit + valid sidecar
   pass preflight; materialization copies identical bytes to the fixed content
   path; candidate/content/package inventories contain it; reopen validation
   passes; acceptance evidence contains it.
2. Backward compatibility: existing legacy/direct/replay-v3 fixtures and the
   existing accepted Dissociation upstream package validate unchanged with four
   roles and no sidecar.
3. Missing-sidecar downgrade: v4/v2 authority with no sidecar is rejected.
4. Unadvertised upgrade: v1/v3 authority with a sidecar or page
   `semantic_structure` is rejected.
5. Structural tampering matrix: mutate schema/profile, pages/order,
   `structure_sha256`, `submission_sha256`, fidelity path/bytes/hash, one page
   decision SHA, duplicate/missing page, or sidecar bytes after packaging; each
   must reject before acceptance.
6. Closed shape: an unrelated eighth/ninth root file and an extra packaged
   content file remain rejected.
7. Atomicity: a structural validation failure leaves neither promotion package
   nor acceptance receipt; existing race/rollback tests continue to pass.
8. Contract stability: publication contract/blueprint still require the exact
   four upstream roles; no schema or runtime consumer is widened to five.
9. Real authority smoke test, when the ignored Dream fixture exists: read-only
   preflight reports `promotion_preflight_passed` and the expected Stage 06
   candidate inventory hash before the live materialization command is retried.

Prefer a small synthetic structural helper/fixture committed with the tests;
the optional real-Dream smoke test is evidence, not the sole regression guard.

## Acceptance criteria

- The exact Dream replay-16/v27 candidate passes read-only promotion preflight
  without modifying Stage 01-06 artifacts.
- Promotion produces one package containing byte-identical
  `content/SEMANTIC_STRUCTURE.json`, and full package validation passes before
  any acceptance receipt exists.
- The four-role reconstruction inventory and current publication schemas remain
  unchanged.
- The user's explicit reconstruction acceptance can then be recorded, and the
  resulting receipt includes the sidecar only as structural evidence.
- Focused promotion, replay-resume, semantic-structure, schema, publication
  preflight, adversarial rollback, and existing-package tests pass.
- `git status` shows every reusable implementation/test/schema/document change
  outside ignored `working/**`; no generated run artifact is staged for a
  future commit.

## Files checked, files changed, verification, blockers, next action

Files checked:

- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/pipeline/reconstruction_replay_resume.py`
- `kb_creator/pipeline/semantic_structure.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/contracts/reconstruction_semantic_structure.v1.schema.json`
- `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json`
- `kb_creator/contracts/reconstruction_upstream_inventory.v1.schema.json`
- `kb_creator/contracts/artifact_acceptance.v1.schema.json`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_replay_resume.py`
- `kb_creator/tests/test_semantic_structure.py`
- replay-16 Stage 05 audit, Stage 06 manifest/candidate sidecar, validated
  submission, decision set, and representative page decisions.

Files changed: only this assigned immutable receipt.

Verification/evidence: static code-path trace plus read-only comparison of the
current Dream audit/sidecar/submission/stage identities. No test execution was
needed for this architecture assignment, and no live artifact was mutated.

Blockers: none for implementation. Promotion and acceptance remain correctly
blocked until the generic bridge change and regression suite pass.

Next action: the orchestrator should assign or implement the bounded generic
change above, run focused tests, run read-only Dream preflight, then retry
materialization and only afterward record the user's explicit reconstruction
acceptance.
