# Architect receipt: reconstruction promotion bridge specification

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4-to-5-reconstruction-promotion-bridge-spec`
- Role: architect
- Policy role/model/effort: `gpt-5.6-sol`, `high`
- Actual platform model/effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Scope: read-only architecture of the scenario-neutral bridge from a completed
  six-stage reconstruction run to a reviewable upstream package, followed by a
  separately authorized reconstruction acceptance receipt.
- Result: specification complete; implementation, acceptance, publication,
  release review, and Git actions were not performed.
- Files changed: only this immutable handoff receipt.
- Timestamp: `2026-09-14T10:48:29Z`
- Elapsed time: approximately 35 minutes
- Token use: unavailable

## 1. Evidence and current-state finding

Files checked:

- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/__main__.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/pipeline/identity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/finalize_mineru_reconstruction.py`
- `kb_creator/scripts/build_scenario_master_en.py`
- reconstruction/publication/acceptance schemas and focused tests
- the sealed skipped-run evidence under
  `kb_creator/working/dissociation/reconstruction/20260914-no-cuda-skip-01/`

Confirmed contracts and gaps:

1. `resume_engine` revalidates the exact six-stage prefix and returns
   `candidate_ready_for_reconstruction_qa`; it does not claim QA completion,
   acceptance, or publication authority. Its fixed candidate is
   `outputs/06-materialize-candidate/candidate/`.
2. The stage graph is exactly:
   `01 prepare_inputs -> 02 mineru_three_view -> 03 compare_views ->
   04 visual_merge_bundle -> 05 fidelity_audit -> 06 materialize_candidate`.
   Each `stages/<id>/stage.json` binds the run identity, ordered upstream
   `reproducible_sha256` values, exact inputs, tool/code identities, and the
   deterministic inventory of `outputs/<id>/`.
3. The production materializer creates `RECONSTRUCTED_EN.md`, `pages/`,
   `decisions/`, `assets/`, `MERGE_PROVENANCE.json`, `ASSET_MANIFEST.json`, and
   `OVERLAY_SELECTION.json`. It does not create aggregate reconstruction QA,
   an upstream inventory, or an acceptance receipt.
4. The Stage 05 production adapter requires an audit report with `passed=true`,
   but publication cannot currently prove that the accepted upstream package
   contains this exact report or the complete six-stage lineage.
5. `publication._validate_reconstruction` currently accepts a sealed flat
   five-field inventory, validates only required role files, and then validates
   a generic `artifact_acceptance.v1` candidate record. It does not enforce the
   inventory schema value, exact role set, full package file closure, exact
   Stage 06 producer, exact QA/fidelity evidence, or a bridge manifest.
6. `artifact_acceptance.v1` already admits artifact kind `reconstructed_en`,
   but `record_artifact_acceptance` supports only publication-produced kinds.
   Reusing that generic publication command is therefore both impossible today
   and the wrong authority boundary for reconstruction.
7. The MASTER_EN v3 adapter copies the whole directory containing the upstream
   inventory, locates the unique `reconstructed_en` role, and later resolves
   Markdown assets under that copied package. The package therefore must freeze
   all referenced assets, not merely the Markdown file.
8. The production-package adapter later requires exactly one `source_identity`
   role and copies it as durable upstream evidence.
9. The reconstruction skill explicitly ends at a run-local candidate. It
   forbids promotion and acceptance. The bridge must therefore be a separate
   control boundary, not a seventh reconstruction stage and not an extension
   of the reconstruction skill.
10. The current Dissociation run is a sealed CUDA skip containing only
    `run.json` and `skip.json`; all six stages are skipped. It is not promotable
    and must never be resumed or used as bridge input.

The old `finalize_mineru_reconstruction.py` is not reusable for this bridge: it
contains Viral-specific handout identities/counts, requires a
`player_handouts` role, and generates an overlay PDF. It is evidence of useful
gate names only, not neutral implementation authority.

## 2. Architectural decision

Add a separate `reconstruction-promotion` control module and CLI namespace with
two commands and no combined path:

```text
completed, non-skipped six-stage run
  -> materialize immutable review package and sealed inventory
  -> STOP: awaiting explicit user reconstruction acceptance
  -> record one non-overwriting acceptance receipt
  -> publication preflight may consume the exact inventory + receipt
```

The first command never creates acceptance. The second command never rebuilds,
repairs, selects, or mutates candidate content. Neither command invokes a
publication stage. `publication run/resume` must not call either command.

## 3. Exact CLI

Add this isolated namespace to `python -m kb_creator`:

```powershell
python -m kb_creator reconstruction-promotion materialize `
  --run-root <canonical-completed-run-root> `
  --json
```

```powershell
python -m kb_creator reconstruction-promotion record-acceptance `
  --run-root <same-canonical-completed-run-root> `
  --user-decision-reference <non-empty-current-user-decision-reference> `
  --json
```

There are deliberately no `--source`, `--contract`, `--candidate`,
`--decision-set`, `--decisions-root`, `--evidence`, `--destination`,
`--inventory`, `--recorder-role`, `--decision`, or adapter arguments. Every
path except `run-root` is derived from the validated run. `recorder_role` and
decision are fixed respectively to `main_orchestrator` and `accepted`.

Successful materialization returns:

```json
{
  "schema": "kb_creator.reconstruction_promotion_result.v1",
  "state": "candidate_awaiting_reconstruction_acceptance",
  "exit_code": 0,
  "run_identity_sha256": "<SHA256>",
  "package_root": "<fixed-derived-path>",
  "inventory": "<fixed-derived-path>/RECONSTRUCTION_INVENTORY.json",
  "acceptance": null
}
```

Successful acceptance recording returns state
`accepted_reconstruction_upstream_ready` plus the fixed receipt path and its
identity. Errors use the existing fail-closed CLI `state=blocked`, exit `2`.

The command surface is an operational guard, not proof of user intent. NRI
governance requires the main orchestrator to invoke the second command only in
the turn containing a current, explicit user acceptance of that exact package.
A stored reference string alone does not authorize invocation.

## 4. Fixed roots and containment

The only accepted run topology is:

```text
<repo>/kb_creator/working/<scenario-id>/reconstruction/<safe-run-leaf>/
```

The resolved root must equal `run.json.local.run_root`; `<scenario-id>` must
equal the validated reconstruction contract scenario id; the leaf must be a
safe basename. Reject a lexical or resolved escape, `..`, drive-relative path,
UNC alternate root, symlink, junction, mount/reparse point, or any reparse
component. The bridge writes only below that validated run root.

The fixed package root is:

```text
<run-root>/promotion/reconstruction-upstream-v1/
```

It must be absent for `materialize`. The fixed acceptance destination is:

```text
<run-root>/promotion/reconstruction-upstream-v1/RECONSTRUCTION_ACCEPTANCE.json
```

It must be absent for `record-acceptance`. The sole allowed outside-repository
read is the source path already sealed in `run.json.local.source_path`; the
bridge takes no source argument and revalidates its bytes/hash. No outside-root
write is permitted.

Every portable record uses forward-slash relative paths. Reject backslashes,
colons, absolute paths, empty components, `.`/`..`, case-fold collisions,
reserved Windows device basenames, alternate data-stream syntax, symlinks, and
reparse points. Containment is checked both lexically and after resolution.

## 5. Required resume-authority snapshot

Promotion cannot safely recover the original DecisionSet from Stage 05/06
`path_hint` and hash alone. Before either resumed stage runs, `resume_engine`
must atomically snapshot the already validated submission to the fixed absent
root:

```text
<run-root>/review/validated-submission-v1/
  decision_set.json
  pages/page-NNN.json
  reviewed_allowlist.json       # only when present
  submission_inventory.json
```

`submission_inventory.json` is closed and sealed as
`kb_creator.validated_reconstruction_submission.v1`; it binds run, queue,
contract, source, the exact DecisionSet, exact ordered decision file domain,
and optional allowlist. Its `files` identities are the inputs passed to both
Stage 05 and Stage 06 manifests. Copy by bytes into a sibling staging directory,
reopen and hash every copy, then rename without replacement. No external
decision path is retained as portable authority.

If the fixed snapshot already exists, resume does not update or merge it. It
must validate it byte-for-byte against the supplied submission before using it;
otherwise it stops as stale/conflicting authority. Promotion requires this
snapshot and never accepts a later caller-supplied decision path.

This is the only necessary change inside the reconstruction resume boundary.
It does not add a stage, change a decision, or perform promotion.

## 6. Package layout and artifact roles

Materialize this exact portable shape:

```text
reconstruction-upstream-v1/
  content/
    RECONSTRUCTED_EN.md
    pages/page-NNN.md
    assets/**
    ASSET_MANIFEST.json
    OVERLAY_SELECTION.json
  evidence/
    run/run.portable.json
    stages/01-prepare-inputs.stage.json
    stages/02-mineru-three-view.stage.json
    stages/03-compare-views.stage.json
    stages/04-visual-merge-bundle.stage.json
    stages/05-fidelity-audit.stage.json
    stages/06-materialize-candidate.stage.json
    review/review_queue.json
    review/decision_set.json
    review/pages/page-NNN.json
    review/reviewed_allowlist.json       # optional, exact when declared
    review/submission_inventory.json
    review/MERGE_PROVENANCE.portable.json
    fidelity/audit.json
  SOURCE_IDENTITY.json
  RECONSTRUCTION_QA.json
  RECONSTRUCTION_MANIFEST.json
  RECONSTRUCTION_INVENTORY.json
  RECONSTRUCTION_ACCEPTANCE.json         # absent after A; created only by B
```

Do not copy the original `MERGE_PROVENANCE.json` verbatim because its current
production shape contains absolute raw/packet paths. Generate the portable
copy only from the validated Stage 04 packets, validated submission, and Stage
06 candidate; it contains package-relative paths plus bytes/hash identities.
Do not copy raw MinerU payloads, source PDF bytes, overlays, or tool runtimes.
Do not create a preview PDF.

The inventory exposes exactly the four roles expected by neutral publication:

| Role | Exact relative path | Meaning |
| --- | --- | --- |
| `reconstructed_en` | `content/RECONSTRUCTED_EN.md` | exact reader input candidate |
| `reconstruction_manifest` | `RECONSTRUCTION_MANIFEST.json` | complete portable lineage/package closure |
| `reconstruction_qa` | `RECONSTRUCTION_QA.json` | machine QA, all required checks pass |
| `source_identity` | `SOURCE_IDENTITY.json` | portable source/contract/run identity, no local source path |

Tighten both the publication-contract schema and runtime validation so
`upstream.required_artifact_roles` is this exact four-role set, not an arbitrary
subset. Legacy Viral/Innsmouth compatibility routes remain untouched.

## 7. Data contracts

### 7.1 `reconstruction_upstream_inventory.v1`

Add `kb_creator/contracts/reconstruction_upstream_inventory.v1.schema.json`.
Keep the existing publication-facing field names to minimize adapter change:

```text
schema = kb_creator.reconstruction_upstream_inventory.v1
scenario_id
reconstruction_contract_sha256
artifacts = exact four unique role records {role,path,bytes,sha256}
inventory_sha256
```

The seal is canonical SHA-256 over all fields except `inventory_sha256`.
Runtime must enforce the schema constant and exact role-to-path map.

### 7.2 `reconstruction_upstream_manifest.v1`

Add `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json`.
It is closed and self-sealed with `manifest_sha256`, and contains:

- `package_state = candidate_awaiting_reconstruction_acceptance`;
- scenario id/title;
- run id and portable run identity;
- reconstruction contract identity and revision;
- source identity-file record;
- queue, validated-submission, DecisionSet, decision-domain, and optional
  allowlist identities;
- exact ordered six-stage records, each binding stage id/name, copied manifest
  identity, and its `reproducible_sha256`;
- exact original Stage 06 candidate inventory and its digest;
- exact portable content inventory and its digest;
- exact Stage 05 fidelity audit identity;
- exact QA identity;
- implementation identity of the bridge and validators;
- `package_files`: the complete deterministic inventory of every regular file
  in the A package except `RECONSTRUCTION_MANIFEST.json` and
  `RECONSTRUCTION_INVENTORY.json`;
- `manifest_sha256`.

After B, exactly one additional unlisted file is allowed:
`RECONSTRUCTION_ACCEPTANCE.json`. Any other missing or extra file blocks.

### 7.3 `reconstruction_source_identity.v1`

Add `kb_creator/contracts/reconstruction_source_identity.v1.schema.json` for
the durable `SOURCE_IDENTITY.json` authority. It is closed and sealed and binds
scenario id, run identity, contract basename/bytes/hash/revision, source
basename/bytes/hash/page count/MediaBox/rotation, and
`source_identity_sha256`. It never records an absolute source path.

### 7.4 Reconstruction QA

Do not add a schema per QA report. `RECONSTRUCTION_QA.json` is a closed runtime
document, sealed by `qa_sha256` and then bound by the manifest, inventory, and
acceptance. Its state is exactly
`candidate_ready_for_user_reconstruction_review`; it contains the scenario,
run/contract/source identities, candidate and Stage 06 producer identities,
fidelity identity, decision authority identity, findings (empty), and these
exact pass-only gates:

1. `source_identity`
2. `complete_stage_chain`
3. `closed_decision_authority`
4. `fidelity_audit`
5. `page_and_role_coverage`
6. `text_ocr_provenance`
7. `required_entity_closure`
8. `asset_closure`
9. `no_open_blockers`

A missing gate, non-`pass` status, non-empty gate errors, or non-empty findings
blocks package creation and later acceptance/publication validation.

### 7.5 Acceptance receipt

Do not create `artifact_acceptance.v2`. Reuse
`kb_creator.artifact_acceptance.v1` with reconstruction-specific runtime
constraints:

- `artifact_kind = reconstructed_en`;
- candidate is exactly the inventory's `reconstructed_en` record;
- producer stage is exactly the copied
  `evidence/stages/06-materialize-candidate.stage.json`;
- evidence is the exact ordered identities of
  `RECONSTRUCTION_INVENTORY.json`, `RECONSTRUCTION_MANIFEST.json`,
  `RECONSTRUCTION_QA.json`, `SOURCE_IDENTITY.json`, and
  `evidence/fidelity/audit.json`;
- decision is fixed `accepted`;
- recorder role is fixed `main_orchestrator`;
- timestamp and non-empty user-decision reference are required;
- `receipt_sha256` seals the document.

The inventory deliberately contains no acceptance state. Acceptance is the
separate receipt; adding it does not rewrite the inventory or manifest.

## 8. Materialization validation algorithm (A)

Perform all checks before the first package write:

1. Validate canonical root topology and all existing components as non-reparse.
2. Load and fully validate `run.json`; require target/profile v1, exact local
   binding, and capability state exactly `available`. Reject `injected` and
   `unavailable`. Require `skip.json` absent.
3. Revalidate current source bytes/hash, contract canonical hash, implementation
   inventory, capability receipt, and every tool binding. This preserves the
   reconstruction engine's existing drift policy.
4. Load the fixed validated-submission snapshot; revalidate its seal, queue
   binding, full ordered page coverage, every decision identity, closed
   `unresolved=[]`, `visual_reviewed=true`, and optional allowlist identity.
5. Reconstruct the exact Stage 05/06 decision input list from that snapshot and
   call the same complete-prefix validation used by resume. Require exactly six
   stage directories, exact upstream chain, successful states, and unchanged
   output inventories. Extras or omissions fail.
6. Validate Stage 05 `audit.json`: exact supported schema, `passed=true`,
   `errors=[]`, exact ordered source-page domain, and every page row passed.
   Its bytes must be in the Stage 05 output inventory.
7. Validate the Stage 06 production candidate, not merely a file with the same
   name: exact required root files/directories; exact page and decision domains;
   source-page markers exactly once and in order; decision copies equal the
   validated submission; roles equal the contract partition; selected-block
   provenance is exact; no unresolved records; required-entity count is exact
   and derived from the contract rather than a scenario list; asset manifest,
   actual asset tree, and every Markdown reference are mutually closed.
8. Require the materializer provenance status
   `candidate_ready_for_reconstruction_qa`, then independently compute the nine
   QA gates above. That status alone is never a pass.
9. Create a staging package at a fixed absent run-local path. Copy only the
   portable layout in Section 6, using byte copies, then reopen/hash every file.
10. Generate source identity, QA, manifest, then inventory in that order.
    Recompute the complete staged inventory and all seals. Revalidate the live
    source/run bindings one final time immediately before publish.
11. Atomically rename the staging directory to the fixed absent destination
    with a no-replace primitive. Never use replacement semantics.
12. Reopen the published package and run the same package validator. Return
    success only after exact inventory/seal equality. Verify that the acceptance
    file is absent.

If a caught error occurs, remove only the just-created private staging
directory after proving it is the fixed child of the run-local staging root. A
process-crash residue is not resumed automatically; its presence is a stop
state requiring explicit quarantine/cleanup by the orchestrator.

## 9. Acceptance algorithm (B)

1. Require a current explicit user decision operationally and a non-blank
   decision reference syntactically.
2. Repeat root, run, source, contract, implementation, tool, capability,
   submission, six-stage, fidelity, and package validation. This prevents
   source or authority drift between package review and acceptance.
3. Require the fixed package to have no acceptance receipt and no unlisted file.
4. Recompute candidate, producer, and exact evidence identities from the package;
   never accept caller-supplied records.
5. Construct the v1 receipt in memory and validate it against JSON Schema and
   the stricter reconstruction rules.
6. Create the fixed receipt with exclusive-create semantics (`xb` or equivalent),
   flush/fsync, close, reopen, and verify seal/identity. A pre-existing path,
   including an identical receipt, is a hard no-overwrite stop.
7. Revalidate the full accepted package allowing exactly that one receipt, then
   return success.

No negative or ambiguous user response is converted to an acceptance file. A
rejected candidate remains immutable evidence. Corrections require a fresh
reconstruction run identity; A and B provide no in-place edit or retry route.

## 10. Publication-side enforcement

Strengthen `_validate_reconstruction` without teaching publication how to build
or accept reconstruction:

- inventory and receipt must have fixed basenames and the same non-reparse
  package root;
- package root must match the canonical bridge topology under repository
  `kb_creator/working`;
- inventory schema and exact four roles must validate;
- manifest, source identity, QA, all package files, seals, and no-extra rule
  must validate;
- manifest scenario/contract identities must match the publication contract;
- QA must be all-pass, fidelity exact and passing, and the stage chain exactly
  01 through 06;
- acceptance candidate, exact Stage 06 producer, exact evidence set, recorder,
  user reference, and seal must validate;
- absent acceptance always blocks publication preflight;
- publication remains read-only and creates no run root on any failure.

The MASTER_EN adapter then consumes only the exact `reconstructed_en` role and
its package-relative assets. It must not accept source PDF, original run-local
paths, or raw MinerU directories.

## 11. Atomicity and immutable-state rules

- A package root, validated submission root, inventory, manifest, QA, and
  acceptance receipt are create-once artifacts.
- Do not use `Path.replace`, overwrite mode, `copytree(..., dirs_exist_ok=True)`,
  or merge semantics at any public boundary.
- Only a fully validated staged tree may receive the final directory name.
- No failed/partial tree may contain a success manifest, inventory, or receipt.
- A succeeds with acceptance absent; B adds only the receipt. Neither rewrites
  content or prior evidence.
- Any change to source, contract, decision set, stage output, candidate, QA,
  manifest, inventory, implementation, capability, or tool binding invalidates
  the path to acceptance. Start a fresh run rather than resealing mutated data.

## 12. Stop states

| Condition | Required result |
| --- | --- |
| capability unavailable / `skip.json` present | `run_not_promotable_skipped`; fresh run required |
| injected test run | `run_not_production_authority` |
| missing/extra/failed/tampered stage | `reconstruction_stage_chain_invalid` |
| missing/stale decision snapshot | `decision_authority_invalid`; no fallback search |
| source/contract/code/tool/capability drift | corresponding `*_drift`; no write |
| fidelity missing/non-pass/incomplete | `fidelity_not_closed` |
| QA gate missing/non-pass | `reconstruction_qa_not_closed` |
| candidate/page/entity/asset/provenance mismatch | `candidate_not_promotable` |
| escape/reparse/absolute portable path | `unsafe_promotion_path` |
| A destination or staging residue exists | `promotion_path_exists`; no resume/overwrite |
| A succeeds | `candidate_awaiting_reconstruction_acceptance`; stop |
| no current explicit user acceptance | do not invoke B; remain awaiting decision |
| B destination exists | `acceptance_receipt_exists`; no overwrite |
| rejected/ambiguous decision | no receipt; fresh run for any corrected candidate |
| accepted package missing/stale at publication preflight | `invalid_or_unaccepted_reconstruction`; no publication run root |

Error strings may add detail, but stable reason codes should be machine-testable.

## 13. Required implementation scope

Narrow reusable changes only:

- add `kb_creator/pipeline/reconstruction_promotion.py`;
- minimally update `kb_creator/pipeline/reconstruction.py` for the fixed
  validated-submission snapshot;
- add the isolated CLI routes in `kb_creator/__main__.py`;
- add the three schemas in Section 7;
- strengthen `kb_creator/pipeline/publication.py` and the publication-contract
  schema for the exact bridge authority;
- add focused neutral tests in
  `kb_creator/tests/test_reconstruction_promotion.py` and targeted publication
  contract/control-plane tests.

Do not modify reconstruction stage enums, the reconstruction skill, legacy
Viral/Innsmouth builders, scenario content/contracts, publication adapters
beyond necessary read-side validation compatibility, live Dissociation
artifacts, canonical plan/context/status, acceptance artifacts, or release/Git
state. Do not add a `dissociation_*` executable.

Because `reconstruction.py` and `__main__.py` are included in run implementation
identity, implement and independently review this bridge before starting the
fresh CUDA-capable Dissociation run. Applying it after a completed run would
correctly make that run stale under current identity rules.

## 14. Required tests

Positive tests:

1. A production-shaped neutral synthetic run with capability `available`, exact
   six-stage chain, closed decisions, passing fidelity, zero and nonzero
   contract-derived entity cases, and closed assets materializes the fixed
   package.
2. A returns the awaiting state, exact four-role inventory, complete package
   closure, and no acceptance file.
3. B, called separately with a non-empty decision reference, creates one valid
   v1 receipt whose candidate, Stage 06 producer, evidence set, and seal are exact.
4. Strengthened publication preflight accepts that exact A+B pair read-only and
   creates no run root.
5. The package is portable: no drive/UNC/absolute local path occurs in any
   portable path field or generated provenance authority.

Adversarial tests must cover at least:

- current no-CUDA skipped shape, `skip.json`, and injected adapter runs;
- five-stage prefix, extra stage directory, failed state, changed stage seal,
  wrong upstream order, output inventory drift, and wrong Stage 06 producer;
- absent/false/errorful/partial fidelity report and wrong page domain;
- absent snapshot, stale queue/contract/source binding, missing/extra decision,
  changed decision bytes, open unresolved item, unreviewed page, and stale
  allowlist;
- missing/non-pass QA gate and resealed fake QA;
- source/contract/implementation/tool/capability drift before A and between A/B;
- candidate marker gap/order/duplicate, role mismatch, required-entity mismatch,
  broken/extra/escaping asset, manifest mismatch, and content extra file;
- absolute, traversal, alternate-drive, UNC, ADS, case-collision, symlink,
  junction, and reparse attacks at run, snapshot, staging, package, and
  inventory paths;
- package root outside canonical repository working root;
- unrecognized arbitrary path flags on both CLI commands;
- destination pre-created before A, rename race, partial staging residue,
  receipt pre-created before B, and a second identical B call;
- hand-authored flat inventory, wrong inventory schema, subset/duplicate roles,
  missing/extra package file, acceptance absent, candidate mismatch, evidence
  omission, fake recorder, blank reference, and resealed stale acceptance;
- mutation immediately before final publish/reopen validation, proving no
  successful result or acceptance residue;
- JSON-Schema/runtime parity for all new schemas and the reconstruction-specific
  use of `artifact_acceptance.v1`.

Public tests must not expose a flag that admits injected adapters or outside-root
paths. Test-only fixtures may call private validators directly.

## 15. Acceptance criteria for the remediation

- [ ] The fresh reconstruction run captures a fixed validated decision snapshot
      before Stage 05 and binds the copied identities into Stage 05/06.
- [ ] A accepts only a current, complete, non-skipped production run under the
      canonical repository working root.
- [ ] A independently closes stage, decision, fidelity, QA, page/role/entity,
      provenance, and asset checks.
- [ ] A atomically creates the fixed portable package with exact inventory and
      four publication roles, while creating no acceptance artifact or claim.
- [ ] No portable authority contains an external absolute path; the external
      source is read only through the run's pre-bound local path.
- [ ] B has no content/path/evidence/recorder overrides and can write only the
      fixed receipt after an explicit current user decision.
- [ ] B is exclusive-create and cannot overwrite or silently replay.
- [ ] Publication preflight rejects every absent, stale, incomplete, hand-made,
      outside-root, reparse, or unaccepted upstream before any write.
- [ ] The skipped Dissociation run is demonstrably unpromotable and unresumable.
- [ ] Focused positive, adversarial, race/no-overwrite, and schema/runtime parity
      tests pass.
- [ ] A separate independent implementation review finds no P0/P1 before any
      fresh live Dissociation run or user acceptance.

## 16. Risks and assumptions

- Assumption: the bridge is implemented before the fresh GPU run. Otherwise the
  existing implementation-identity policy intentionally invalidates that run.
- Assumption: accepted reconstruction remains in its immutable run-local bridge
  root; no separate stable-copy promotion is needed before publication.
- Assumption: `numbered_player_handouts` remains the only required entity type
  in reconstruction contract v1. Its closure must be derived generically from
  the target English Markdown/decision evidence; no Viral label list is allowed.
- Risk: a user decision reference is audit evidence, not cryptographic proof of
  consent. Governance and main-orchestrator ownership remain mandatory.
- Risk: source drift after B cannot be prevented without copying the immutable
  source, which is intentionally excluded. B revalidates immediately before
  acceptance; downstream authority is then the frozen package source identity.
- Risk: Windows no-replace and fsync behavior requires explicit race tests.
- Risk: copying every raw MinerU output would make the package large and expose
  local paths. The chosen bridge instead copies the exact portable evidence and
  binds the validated original candidate/stage inventories at A time.

## 17. Verification performed for this receipt

Read-only static trace completed across reconstruction final state, six-stage
manifest/output logic, decision validation, materializer/fidelity outputs,
publication upstream validation and adapters, acceptance schema/recorder,
skill boundary, current goal state, and the real sealed skipped-run layout.
The assigned receipt path was confirmed absent before creation. No runtime test,
live reconstruction, package materialization, acceptance, publication run,
source mutation, or Git action was performed.

## 18. Blockers and next action

Blockers:

- The bridge and validated-submission snapshot do not yet exist.
- The current host's sealed no-CUDA Dissociation run is not eligible input.
- User reconstruction acceptance does not exist and must not be inferred.

Next action: the orchestrator may assign a bounded scenario-neutral engineering
packet implementing Sections 3-13, followed by bounded QA and a fresh independent
implementation review. Only after that closure should Dissociation start a new
GPU-capable reconstruction run. After A returns the awaiting state, stop and
show the exact candidate/QA/inventory to the user; invoke B only on the user's
explicit acceptance of that exact identity.
