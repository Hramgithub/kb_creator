# Independent critic receipt - kb_creator pipeline automation process review

Goal id: `20260913-kb-creator-pipeline-automation-review`
Step: `R4`
Review kind: `process/concept`, not `release`
Role: independent critic (`gpt-5.5`, requested high)
Orchestrator policy owner: `gpt-5.6-sol`, medium
Assignment state: `platform-unverified`
Scoped override: none
Timestamp: 2026-09-13 (Europe/Moscow)

## Scope and result

Read-only process review of `kb_creator` governance, active plan/context,
project status, handoff patterns, test-as-evidence usage, authorization layers,
and commit-history shape. I did not modify implementation, canonical
`PROJECT_STATUS.md`, `plan.md`, `context.md`, release files, source/output
artifacts, Git state, Foundry content, or network state. The only write is this
receipt.

Recommendation: proceed with a lean one-command pipeline design, but treat the
first implementation wave as a governance reduction and evidence-indexing
product, not as another layer of agent-authored receipts. The current process
is strong at preventing unsafe promotion; it is weak at making the next safe
action obvious to a human or command runner.

## Severity-ranked findings

### P1 - Canonical state is too large and internally fragmented to be a safe run contract

Evidence:

- `kb_creator/docs/plans/20260913-kb-creator-pipeline-automation-review/plan.md`
  records the desired product goal: a one-command pipeline usable without an AI
  orchestrator, with packaging and deterministic evidence.
- The same plan records `457` plan-tree files, `438` handoff files, and a
  `1,612` line project status as the starting baseline.
- My read-only recount found `428` files directly under plan `handoffs/`
  folders in the current local tree. The dominant local buckets are
  `20260808-innsmouth-systemic-todo-execution` with `319` handoff Markdown
  files and `20260809-innsmouth-page-level-consumer-proof` with `79`.
- `kb_creator/PROJECT_STATUS.md` contains overlapping historical and current
  narratives: page-proof status at the top, v6 freeze, v7 rebuild proof, full
  dry-run proof, source-to-artifacts run, and later raw-PDF/page-proof
  checkpoints.
- Governance requires `PROJECT_STATUS.md` to be a concise rollup linking to
  goal details, while `plan.md` and `context.md` carry detailed state. That
  contract is no longer being met in practice.

Risk:

The next operator cannot reliably distinguish live blockers, stale blockers,
accepted evidence, rejected evidence, and historical explanation from one
canonical place. That makes the AI orchestrator itself the actual state
machine, which is exactly what the new one-command pipeline is supposed to
remove.

Recommendation:

Make the runner emit one canonical `run.json` plus `evidence/index.json` and
`review_queue.json`. `PROJECT_STATUS.md` should link to the current run id and
summarize only active blockers, accepted release boundary, and next human
decision. Plans should retain ownership and design intent; they should not be
the machine-readable pipeline ledger.

### P1 - Review receipts are being used as mechanical gates that scripts should own

Evidence:

- Across the two main historical handoff folders, a targeted read-only count
  found `360` files containing acceptance/rejection/blocker language and `719`
  lines repeating no-live/no-source/no-Git/no-release boundary prose.
- `kb_creator/PROJECT_STATUS.md` repeatedly records green test counts followed
  by independent review acceptance or rejection, for example `129 passed`,
  `147 passed`, `386 passed`, `649 passed`, `681 passed`, `1057 passed`, plus
  repeated "not a consumer switch" and "no rebuild authorized" statements.
- Several rejections are valuable but mechanical in nature: mutable registry
  pins, zero-length span entry, unrelated invalid synthetic topology before the
  target invariant, missing full matrix coverage, and manufacturing
  `accepted_no_mutation` without proof.
- The current engineer receipt independently observes the same pattern:
  mechanical evidence is repeatedly re-described in receipts instead of being
  emitted once by a runner, and routine stages should require zero prose
  handoffs.

Risk:

The process spends critic attention on facts a deterministic verifier can check
more completely and more cheaply. Worse, repeated prose gates create false
confidence when the prose says "no P0/P1" but the underlying invariant is not
encoded as an executable check.

Recommendation:

Move every repeated mechanical invariant into executable validators with stable
error codes. A critic should review new gate semantics, unresolved semantic or
visual decisions, and frozen release candidates. A critic should not be needed
to restate that a known file hash matched, that public routes fail closed, or
that source/output/Git boundaries remain prohibited when a run manifest can
prove those facts.

### P1 - Local branch divergence blocks trustworthy automation design unless integration is explicit

Evidence:

- Current branch state is `main...origin/main [ahead 1, behind 8]` with many
  unrelated tracked modifications/deletions and untracked `kb_creator` plan,
  script, test, and report files.
- The active context explicitly calls Git diverged and dirty, and says
  integration must remain surgical.
- Read-only commit inspection shows incoming `kb_creator` commits through
  `5248894a Save Viral MASTER_EN rebuild and remediation progress`, including
  generic scenario tooling and review checkpoint artifacts.
- The existing engineer receipt reports that `origin/main` contains generic
  scenario substrate scripts absent or not coherent in the local baseline:
  `scenario_contract.py`, `scenario_source_reconstruction.py`,
  `reconstruct_scenario_source.py`, `build_scenario_master_en.py`,
  `verify_scenario_master_en.py`, and `viral_publication_projection.py`.

Risk:

A one-command pipeline plan based only on the dirty local checkout may
accidentally reimplement or contradict the incoming reusable scenario layer.
Conversely, pulling or committing without a surgical boundary risks mixing user
work, deleted historical scenario artifacts, and review artifacts.

Recommendation:

Before implementation, create a read-only integration inventory against
`origin/main` and the current dirty tree, then choose an implementation base.
Do not write the runner until the plan identifies which generic scenario APIs
are adopted, wrapped, or intentionally deferred. Keep Git integration as a
separate orchestrator step with explicit path scope.

### P2 - Authorization layers protect high-risk actions, but their taxonomy is too prose-heavy

Evidence:

- Governance correctly distinguishes bundled goals, contributor receipts,
  orchestrator-owned canonical state, recovery/watchdog, seed-defect closure,
  and independent release review.
- Page-proof and raw-PDF status entries repeatedly preserve critical
  boundaries: fixture-only acceptance is not live/source/output approval,
  architecture acceptance is not implementation authorization, implementation
  evidence is not release acceptance, and release remains separate.
- The previous Innsmouth memory baseline records that fixture packets `4b.1`
  through `4b.8` were evidence only, that `4b.9` had to be invalidated after
  prohibited dynamic-import/Git activity, and that production/live paths stayed
  closed until a salvage sequence completed.
- The current active plan is a planning/review goal, yet its Definition of Done
  includes a final commit and push. That is acceptable only as a later
  orchestrator action, but it is easy for contributor receipts to blur review,
  implementation, commit, and release verbs.

Risk:

The boundaries are conceptually right, but they are scattered through hundreds
of documents. A contributor can obey one packet and miss a later superseding
constraint, or a status reader can mistake "accepted architecture" for an open
implementation path.

Recommendation:

Use a compact `gate_state` enum in the run/goal evidence index:
`design_only`, `implementation_candidate`, `machine_verified`,
`human_review_blocked`, `release_candidate_frozen`, `release_accepted`,
`release_rejected`, `quarantined`. Pair it with `allowed_next_actions` and
`forbidden_surfaces`. Prose can explain exceptions; the machine state should
decide whether a command may proceed.

### P2 - Test counts are treated as evidence summaries, but not all green tests carry the same acceptance meaning

Evidence:

- `PROJECT_STATUS.md` includes many pass counts whose meanings differ: focused
  tests, collect-only tests, elevated raw suites, fixture-only suites,
  script-backed rebuilds, dry-run proofs, and production PDF checks.
- The same status file records cases where green tests were explicitly not
  accepted: `87 passed` with P1 evidence gaps, `16` plus `704` passed but not
  acceptance evidence, and `161 passed, 27 skipped` rejected for mutable
  authority/coverage gaps.
- The active plan asks tests to be classified as reusable behavioral tests,
  fixture/contract tests, generated state assertions, one-off evidence, or
  duplicated checks.

Risk:

Plain pass counts encourage cargo-cult gating. A future runner that says
`1057 passed` without classifying which stage, contract, live boundary, and
acceptance state it proves will preserve the current ambiguity in JSON form.

Recommendation:

Every test or verifier result in `evidence/index.json` should carry:
`evidence_class`, `stage_id`, `input_identity`, `accepted_scope`,
`non_authorized_scope`, `command`, `exit_code`, `result_hash`, and
`acceptance_effect`. Counts are display data, not gate state.

### P2 - Human decisions are needed, but the workflow currently models them as ad hoc prose or repeated visual receipts

Evidence:

- Current context says repeated manual reconstruction of information already in
  MinerU was challenged, and the manual all-reader B1c7 placement-ledger path
  was suspended in favor of existing OCR/MinerU/package evidence.
- Status and origin/main context preserve pending user visual acceptance and
  independent release review separately from build success.
- Existing artifacts already include machine-readable evidence candidates such
  as `verification_report.json`, `semantic_unit_review.json`,
  `closure_report.json`, `INVENTORY.json`, and asset manifests in the Viral
  review checkpoint.

Risk:

Human attention is being spent to compensate for missing review queues. The
process either over-asks for manual review on mechanical facts or under-specifies
the exact semantic/visual unit a human is approving.

Recommendation:

Represent human work as typed review units, not prose paragraphs:
`unit_id`, `page`, `source_span`, `artifact_path`, `candidate_decision`,
`why_machine_blocked`, `available_evidence`, `decision_options`,
`reviewer`, `timestamp`, and `decision_hash`. A changed unit invalidates only
dependent stages. Keep genuinely high-risk decisions manual: visual identity,
semantic ownership, translation/proofreading acceptance, source mutation
approval, destructive cleanup, Git publication, and release acceptance.

### P3 - Receipt immutability is good, but historical evidence needs an index and supersession graph

Evidence:

- Governance says correction receipts supersede prior receipts and do not
  rewrite them.
- Historical plan folders retain many rejected, superseded, restart, retry,
  addendum, rereview, and next-chat handoffs.
- Origin/main next-scenario context shows thousands of lines of accumulated
  task state and many active/remediation task references.

Risk:

Immutability without an index forces every recovery to reread too much history.
That increases token cost and raises the chance that stale instructions get
treated as current.

Recommendation:

Generate `handoffs/index.json` or fold this into `evidence/index.json` with
`receipt_id`, `kind`, `state`, `supersedes`, `superseded_by`,
`current_for_gate`, `paths_touched`, and `evidence_hashes`. Do not delete old
receipts during this goal; make them navigable.

## Blockers

- No release decision can be made from this review. This is process/concept
  review only; no frozen candidate, release manifest, or full release QA was
  reviewed.
- Implementation should not start from local `main` alone while it is dirty and
  behind `origin/main` by eight commits. First decide the integration base and
  protect unrelated user changes.
- I did not run tests or pipeline commands by assignment constraint. All
  evidence here is from read-only file, status, and Git-history inspection.
- The exact platform model/effort is not verifiable from this task. The receipt
  records the requested policy role, not a proven runtime identity.

## Lean gate model for a one-command pipeline

The target pipeline should have fewer gates, not weaker gates:

| Gate | Owner | Machine artifact | Human/critic involvement | Pass condition |
| --- | --- | --- | --- | --- |
| G0 input contract | CLI | `run.json`, input inventory, tool/version record | None unless paths or source authority are disputed | All declared inputs resolve, hash, and stay in allowed roots before writes. |
| G1 stage execution | CLI/stage library | per-stage receipt JSON with typed outputs and error code | None for known deterministic stages | Stage outputs match declared schema, dependency identities, and cache policy. |
| G2 mechanical QA | CLI/verifiers | `evidence/index.json` with test/verifier classes and acceptance effects | Critic only when a new gate/check is introduced or changed | All required checks pass; failures map to stable blocked states. |
| G3 review queue | User or assigned reviewer | `review_queue.json` and signed decision file | Required for unresolved semantic/visual/translation/source-mutation decisions | Every required unit has an allowed decision bound to source/artifact evidence. |
| G4 package freeze | CLI | package manifest, artifact inventory, reproducibility summary | Independent critic only if this is a release candidate | Candidate is immutable; any artifact mutation invalidates freeze. |
| G5 release | Independent `gpt-5.5`/high critic plus user acceptance where required | release receipt referencing frozen manifest | Mandatory for release only | No blocking findings against frozen package; intentional exclusions recorded. |

Routine architecture/implementation reviews should be replaced by G2 when the
change is a known mechanical variant covered by an existing validator. Keep
separate critic review for new validator semantics, new source mutation classes,
new visual/semantic acceptance policy, and frozen release.

## Files checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/docs/plans/20260913-kb-creator-pipeline-automation-review/plan.md`
- `kb_creator/docs/plans/20260913-kb-creator-pipeline-automation-review/context.md`
- `kb_creator/docs/plans/20260913-kb-creator-pipeline-automation-review/handoffs/engineer_test_script_consolidation_review_20260913.md`
- Historical `kb_creator/docs/plans/**/handoffs/*.md` inventory and targeted
  samples
- `kb_creator/scripts/*.py` inventory
- `kb_creator/tests/test*.py` inventory
- Read-only `git status`, `git log`, `git show`, `git ls-tree`, and `git grep`
  evidence for `kb_creator`
- Memory summary/registry excerpt for the prior Innsmouth page-proof salvage
  boundary

## Verification/evidence

- No tests were run and no live pipeline was executed.
- Read-only counts confirmed local handoff sprawl: `428` handoff Markdown
  files directly under plan `handoffs/` folders, with `319` in the systemic
  TODO plan and `79` in the page-proof plan.
- Read-only search found `360` historical handoff files with acceptance,
  rejection, or blocker language and `719` repeated no-live/no-source/no-Git
  boundary lines across the two dominant historical folders.
- Read-only local inventory observed `29` Python scripts and `43` top-level
  `test*.py` files.
- Read-only history showed incoming `kb_creator` work on `origin/main` through
  `5248894a`, including reusable scenario tooling that must be considered
  before implementation.

## Next action

Integrate this R4 receipt with R2/R3 into the final automation review. The
first implementation packet should be: choose integration base, introduce a
machine-readable run/gate evidence index around the existing generic scenario
tooling, and prove that routine known checks can advance without prose handoffs
while release review and genuine human semantic/visual decisions remain
separate hard gates.

Elapsed time: approximately 35 minutes.
Token use: unavailable from platform; this subtask used a bounded read-only
inspection plus one receipt write.
