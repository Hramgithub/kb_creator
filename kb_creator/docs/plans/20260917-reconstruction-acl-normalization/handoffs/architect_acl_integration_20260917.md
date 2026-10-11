# Architecture receipt: Stage 06 ACL integration

## Receipt

- Goal ID: `20260917-reconstruction-acl-normalization`
- Step ID: `1-diagnose-defect-class`
- Role: architecture (`gpt-5.6-sol`, policy effort `high`)
- Orchestrator policy owner: `gpt-5.6-sol`, effort `medium`, main chat
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-17T13:16:48+03:00`
- Elapsed time: approximately 25 minutes
- Token use: unavailable
- Scope: read-only architecture of the reusable replay/resume Stage 06 ACL gate, its failure atomicity, inventory contract, test seam, and documentation/implementation-inventory consequences. No implementation, source, candidate, canonical plan/context/status, acceptance, publication, Git, or release files were edited.
- Result: `READY_FOR_IMPLEMENTATION`. The safe hook is the final Stage 06 output path after `os.replace(temp_output, output)` and before the Stage 06 manifest is published or `candidate_ready_for_reconstruction_qa` can be returned.

## Files checked or changed

Checked:

- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/docs/plans/20260917-reconstruction-acl-normalization/{plan.md,context.md}`
- `kb_creator/docs/plans/20260916-dream-reconstruction/{plan.md,context.md}`
- `kb_creator/docs/plans/20260916-dream-reconstruction/handoffs/architect_contract_review_20260916.md`
- `kb_creator/contracts/number-7-dream.reconstruction.json`
- `kb_creator/pipeline/reconstruction_replay_resume.py`
- `kb_creator/scripts/normalize_publication_access.py`
- `kb_creator/contracts/{replay_downstream_stage_manifest.v1.schema.json,replay_resume_result.v1.schema.json}`
- `kb_creator/tests/{test_reconstruction_replay_resume.py,test_normalize_publication_access.py,test_publication_registry_e2e.py,test_publication_docx_revision.py}`
- live Number 7 Dream Stage 05/06 manifests and final candidate ACL/hash state

Changed: this immutable handoff receipt only.

## Earliest failing layer and dependency trace

The source, decisions, Stage 05 audit, materialized bytes, and Stage 06 output inventory are valid. The defect begins at the Windows process boundary after the candidate tree is moved out of sandbox-created staging: the final directory can retain a protected DACL that the Codex desktop process and ordinary user processes cannot traverse.

```text
sealed Stage 04 + validated submission
  -> Stage 05 passing fidelity audit
  -> Stage 06 build in outputs/.06-...stage-<operation>
  -> deterministic byte inventory + temporary command/manifest
  -> os.replace(temp_output, outputs/06-materialize-candidate)
  -> REQUIRED final-tree ACL normalization gate
  -> os.replace(temp_stage, stages/06-materialize-candidate)
  -> final downstream-stage validation
  -> candidate_ready_for_reconstruction_qa
```

Stage 05 must not run the ACL callback. Stage 06 must not expose a successful final manifest or replay-resume result before the callback has returned an accepted `normalized` or declared `skipped` state and the byte inventory has been rechecked.

## Concrete remediation specification

1. Import `normalize_publication_access_if_managed` into `reconstruction_replay_resume.py` and add `kb_creator/scripts/normalize_publication_access.py` to `DOWNSTREAM_IMPLEMENTATION`. The normalizer is part of the Stage 05/06 producer closure even though it is invoked only for Stage 06.
2. Give `_publish_stage` an optional injected post-publish callback (preferred test seam) or an equivalently narrow Stage 06-only module callback. Pass it only at the Stage 06 call site.
3. Fresh-stage branch:
   - build and inventory the temporary output as today;
   - atomically rename the temporary output to the exact final Stage 06 output;
   - invoke the callback on that final path, never on the staging path;
   - accept only the normalizer's documented `normalized` state or `skipped` with reason `non_windows_host` / `outside_managed_working_tree`;
   - recompute `deterministic_inventory(output)` and require exact equality with the pre-normalization inventory;
   - only then atomically publish the temporary stage manifest and run `_validate_downstream_stage`.
4. Existing-pair/rerun branch:
   - validate the existing output/manifest pair first;
   - invoke the same callback on the final Stage 06 output;
   - validate the pair again before returning its stage reference;
   - on callback failure, return no success but do not quarantine or delete a pair that this invocation did not create.
5. Keep the callback result out of the candidate tree and do not rewrite an existing stage manifest. The structured normalizer return is the invocation gate; live QA and the goal receipts carry the OS-level evidence. This preserves the sealed artifact authority and avoids introducing host-specific absolute paths into the manifest.

## Failure atomicity

- A fresh invocation owns only its operation-specific temporary roots and any final output/manifest it successfully renamed during that invocation.
- If ACL normalization or the post-normalization inventory check fails after output rename, move the just-created final output to an operation-unique path below `run_root/failures`, clean or quarantine the temporary stage metadata, leave both canonical final paths absent, and re-raise. Never return the replay success result.
- If final manifest rename or final validation fails, quarantine the just-created output and any just-created manifest together (or in clearly paired operation-specific failure paths). Do not leave a misleading final output/manifest pair.
- If quarantine itself fails, the operation still fails closed and reports the cleanup failure and exact residual paths; it must not convert the error into success.
- Never quarantine, delete, or overwrite a pre-existing validated pair on a rerun failure. A mismatched output/manifest pair remains a hard error as today.

This extends the current manifest-rename quarantine rule to every post-output-publish failure. It preserves forensic evidence without mutating source inputs or inferring acceptance.

## Data-contract and identity analysis

No schema revision is required.

- `deterministic_inventory` binds relative file path, byte count, and SHA-256; it does not bind owner, DACL, inheritance flags, timestamps, or directory metadata.
- `icacls /inheritance:e` therefore does not change Stage 06 `outputs.files`, `outputs.inventory_sha256`, `manifest_sha256`, merge provenance, or candidate file identities.
- The post-normalization inventory equality check is still mandatory: it turns the helper's “metadata only” promise into a fail-closed pipeline assertion.
- Do not add an ACL receipt file beneath `outputs/06-materialize-candidate`; that would change the exact candidate inventory and break promotion's flat Stage 06 authority.
- Adding the normalizer script to `DOWNSTREAM_IMPLEMENTATION` intentionally changes the current producer closure. Older Stage 05/06 manifests cannot be resumed under the new code. Repair an already sealed candidate with the reusable helper, then validate its unchanged existing manifest/inventory; do not rewrite the old manifest or pretend it was produced by the new closure.

Current live evidence after the already authorized scoped repair:

- candidate `AreAccessRulesProtected=False`;
- owner remains `KAMAZNOTEBOOK\\CodexSandboxOnline`, which is not itself a failure once inherited user-readable ACEs are active;
- `RECONSTRUCTED_EN.md` SHA-256 remains `38B2D376E119D989656223A8909E93D9C295BE9D69CFF1A46B469998702BF72F`;
- Stage 06 output inventory SHA remains `85A204C292BCF9F506061DDCC9F6F9F243B866CF8B5BCBC24070931B314DEDE8`;
- Stage 06 manifest SHA remains `681F580AC37CD9D7D32C2CD2C725FA3A86FE482E6D22B26559F17A63B3CD938B`;
- `_validate_downstream_stage` still returns the same Stage 06 manifest and inventory identities.

## Required tests

Add focused integration coverage in `test_reconstruction_replay_resume.py`, using the injected callback or a monkeypatch of the module-level normalizer:

1. **Ordering/final-path:** callback observes `outputs/06-materialize-candidate`, not a `.stage-*` path; the final output exists and the final Stage 06 manifest does not yet exist at callback time.
2. **Stage scope:** Stage 05 never calls the callback; Stage 06 calls it exactly once per successful engine invocation.
3. **Managed success:** a `normalized` result permits success; pre/post file identities and inventory SHA are identical.
4. **Declared skip:** isolated temp-tree `outside_managed_working_tree` (and, where practical, `non_windows_host`) permits success without weakening the managed Windows path.
5. **Injected ACL failure:** failure after final output rename yields no canonical Stage 06 output, no canonical Stage 06 manifest, no replay success result, and an operation-specific quarantined candidate; Stage 05 remains intact.
6. **Unexpected callback state:** an unrecognized state/reason fails closed exactly like an exception.
7. **Byte-mutation shield:** a malicious/injected callback that changes a candidate byte fails the inventory equality check and quarantines the fresh candidate.
8. **Rerun:** an already completed fresh pair is validated, gated on its final path, revalidated, and returned without rebuilding or changing its manifest/inventory identities. A rerun callback failure leaves the pre-existing pair untouched and returns no success.
9. **Closure binding:** assert `kb_creator/scripts/normalize_publication_access.py` is present in `DOWNSTREAM_IMPLEMENTATION` and therefore in the producer closure.

Retain the existing helper tests for managed confinement, `.obsidian` exclusion, recursive children, non-Windows skip, and isolated-tree skip. Baseline before implementation: `13 passed` for `test_reconstruction_replay_resume.py` plus `test_normalize_publication_access.py` using repository `.tools/python-test-deps` with the bundled Codex Python. The bare MinerU and bundled Python environments do not contain pytest without that repository dependency path.

## Required documentation and inventory updates

- Update the Windows access paragraph in `kb_creator/README.md` to include real reconstruction replay Stage 06 candidates, state the post-final-rename/pre-success ordering, and retain the reusable repair-helper instructions for sealed older candidates.
- Update `DOWNSTREAM_IMPLEMENTATION` as specified; no replay result, stage-manifest, provenance, audit, or promotion schema change is needed.
- After implementation and QA, only the main-chat orchestrator updates `plan.md`, `context.md`, and `PROJECT_STATUS.md`. This contributor must not edit them.

## Risks and assumptions

- The managed-tree wrapper resolves the final path strictly under `kb_creator/working`; isolated tests are expected to skip. Tests that need a normalized branch should inject the structured callback result rather than run real `icacls` on a temp tree.
- Readability depends on effective inherited ACEs, not ownership transfer. Acceptance must check inheritance and actual read/open behavior; changing owner is outside this fix.
- The callback must remain synchronous. Returning before `icacls` completes would violate the success guarantee.
- ACL repair is intentionally metadata-only. Any changed candidate byte, added receipt file, missing output, or closure drift remains a hard failure.
- The existing Number 7 Dream Stage 06 pair was produced by the pre-fix closure. It can be repaired and revalidated in place, but cannot truthfully become a new-code Stage 06 execution without a new run.

## Acceptance criteria and next action

Implementation is ready when all of the following are true:

1. Every new Stage 06 success path gates the exact final tree after output rename and before manifest/result success.
2. Managed Windows failure leaves no canonical new Stage 06 output/manifest pair and no `candidate_ready_for_reconstruction_qa` result.
3. Isolated/non-Windows skips are explicit and bounded; managed Windows output cannot silently skip.
4. Pre/post candidate inventories and SHA-256 identities are equal.
5. Fresh, failure, skip, mutation, rerun, and implementation-closure tests pass.
6. The existing candidate remains manifest-valid and byte-identical after helper repair, then bounded QA verifies ordinary-user/Codex opening separately.

Blockers: none for implementation. Next action: the orchestrator may implement the callback, quarantine completion, closure binding, tests, and README update; then dispatch bounded Windows QA. This receipt is an architecture recommendation, not implementation approval or a release decision.

## Supplemental recommendation: explicit desktop-principal read grant

- Supplemental timestamp: `2026-09-17T13:27:00+03:00`
- Triggering evidence: the orchestrator's live managed pytest tree had `AreAccessRulesProtected=False` after inheritance was enabled, but its immediate parent was also sandbox-restricted and supplied no ordinary-user read ACE. Therefore the inheritance-only recommendation above is insufficient as a general readability guarantee.
- Supplemental result: `REQUIRED`. On a managed Windows tree, successful normalization must both enable inheritance and explicitly grant the desktop principal recursive read/execute rights. All earlier ordering, inventory, quarantine, and ownership recommendations remain in force.

### Principal and least-privilege contract

1. Resolve the desktop account from both non-empty environment components `USERDOMAIN` and `USERNAME` as `USERDOMAIN\\USERNAME`. Reject missing, empty, control-character, separator-invalid, or unresolvable values with `PublicationAccessError`; do not fall back to `Users`, `Authenticated Users`, `Everyone`, the sandbox owner, or a guessed local account.
2. Prefer resolving that exact account to a SID and pass the numeric form to `icacls` as `*S-...`. This avoids localized account-name rendering and makes the grant identity explicit. A small injectable resolver is the preferred unit-test seam. Friendly-name invocation with argument-list subprocess execution is acceptable only if `icacls` itself is treated as the authoritative resolution check and every nonzero result fails closed.
3. Use additive `/grant`, not `/grant:r`. `/grant:r` can replace and unintentionally downgrade an existing explicit user grant. Add only read-and-execute (`RX`); do not grant write, modify, delete, change-permission, ownership, or full-control rights.
4. Keep ownership unchanged. A successful result is an explicit desktop-user allow ACE plus enabled inheritance, not ownership transfer from `CodexSandboxOnline`.
5. Run the explicit grant only after the existing inheritance-enabling pass. Both passes remain synchronous and precede the post-normalization byte-inventory comparison and Stage 06 manifest publication.

`RX` is the narrow practical Windows right for artifact review: it supplies file read and directory traverse/list behavior. Granting the exact desktop SID limits exposure to one user and is materially narrower than a broad local or authenticated-users group grant.

### Preserve the `.obsidian` exclusion

Do not issue one root-level recursive `(OI)(CI)(RX) /T` grant in the generic helper: that would also touch the deliberately excluded `.obsidian` subtree.

Use the existing top-level target partition instead:

- final artifact root: grant the desktop SID plain `(RX)` without inheritance flags or `/T`;
- each direct file except `.obsidian`: grant plain `(RX)`;
- each direct directory except `.obsidian`: grant `(OI)(CI)(RX)` with `/T`, so that directory and every existing descendant receive read/traverse rights and future descendants inside that included subtree inherit them;
- `.obsidian`: issue neither inheritance-normalization nor explicit-grant commands.

Stage 06 currently has no `.obsidian`, but the shared helper also serves publication/revision trees, so this boundary must remain generic and tested.

### Portability and residual risk

- Outside `kb_creator/working`, retain the declared `outside_managed_working_tree` skip before principal resolution. On non-Windows, retain the declared `non_windows_host` skip before reading Windows identity variables. These branches preserve portable test and non-Windows behavior.
- A successful additive allow grant can still be defeated by an applicable explicit deny ACE. `icacls` success proves the requested ACE was accepted, not full token-level effective access. The pipeline therefore requires both command success and the existing byte-inventory check; bounded live QA must additionally confirm the resolved SID's ACE and open/read behavior through an ordinary desktop process/Codex UI.
- Keep the desktop SID out of candidate contents, portable manifests, and artifact hashes. It is host-local access metadata. The normalizer's structured in-process result may report the resolved SID/principal for diagnostics, but must not create a file beneath Stage 06 or rewrite an existing sealed manifest.
- Byte identity remains stable: `/grant` and `/inheritance:e` mutate only DACL metadata. Recompute and compare the full deterministic inventory after both passes.

### Additional required tests

Extend `test_normalize_publication_access.py` and the Stage 06 integration tests with:

1. missing `USERDOMAIN` and missing `USERNAME` each fail closed for a managed Windows target;
2. invalid/unresolvable principal fails closed before Stage 06 success;
3. captured `icacls` calls use the exact resolved desktop SID/account and only `RX`, never `M`, `F`, `/grant:r`, or a broad group;
4. root receives non-recursive `RX`, included directories receive recursive `(OI)(CI)(RX)`, included files receive `RX`, and `.obsidian` receives no command;
5. injected grant failure quarantines a newly published Stage 06 output and publishes neither its manifest nor replay success result;
6. a successful inheritance-plus-grant pass preserves every candidate byte/inventory identity;
7. live managed-tree QA asserts `AreAccessRulesProtected=False`, a direct allow ACE for the resolved desktop SID with read/execute coverage on root and representative descendants, unchanged owner, unchanged SHA-256/inventory, and successful ordinary-user/Codex opening.

Revised acceptance condition: `AreAccessRulesProtected=False` alone is not sufficient. Managed Windows Stage 06 succeeds only after the exact desktop principal has explicit least-privilege read/execute access across the included final tree and all artifact identities remain unchanged.
