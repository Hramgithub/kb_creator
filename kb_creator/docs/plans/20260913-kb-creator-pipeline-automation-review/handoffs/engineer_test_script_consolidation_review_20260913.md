# Engineer receipt — script and test consolidation review

Goal id: `20260913-kb-creator-pipeline-automation-review`
Step: `R3`
Role: reusable code/test engineering (`gpt-5.6-terra`, policy medium)
Orchestrator policy owner: `gpt-5.6-sol`, medium
Assignment state: `platform-unverified`
Scoped override: none
Timestamp: 2026-09-13 (Europe/Moscow)

## Scope and result

Read-only engineering review of `kb_creator` scripts, `pdf_raw`, tests,
contracts/manifests, the assigned goal context/plan, local Git history, and the
eight incoming commits on `origin/main`. No source PDF, build, output, live
pipeline, network, Foundry, deletion, or Git mutation was performed. The sole
write is this immutable receipt.

The problem is not a lack of automation. `origin/main` already contains a
promising generic scenario substrate (`scenario_contract.py`,
`scenario_source_reconstruction.py`, `reconstruct_scenario_source.py`,
`build_scenario_master_en.py`, `verify_scenario_master_en.py` and
`viral_publication_projection.py`). The problem is that it is surrounded by
scenario-specific entry points, duplicated test harnesses, and a workflow in
which mechanical evidence is repeatedly re-described in receipts instead of
being emitted once by the runner.

The target should therefore be a thin, product-level `kb_creator` CLI that
coordinates existing stage APIs from a declarative scenario contract and emits
one sealed run package. It must preserve the existing fail-closed checks, not
replace them with a permissive batch script.

## Baseline: committed versus local state

The local checkout is `main...origin/main [ahead 1, behind 8]`. Local working
tree material is substantially dirty and contains untracked Innsmouth
experiments; it is not a trustworthy implementation baseline. The relevant
committed baseline is `origin/main` at `5248894a` (2026-09-04), reached through
eight incoming commits beginning with `5952a224`.

| Surface | Local `HEAD` observed | `origin/main` committed baseline | Engineering meaning |
| --- | ---: | ---: | --- |
| `scripts/` Python/PowerShell entry points | 29 | 44 | The generic scenario work is mostly absent locally; do not design a replacement around old Innsmouth-only scripts. |
| `tests/` Python files | 46 including helpers | 47 including helpers | New reusable tests exist remotely, but historic fixture gates remain. |
| Plan-tree handoff Markdown files | 438 in current tree context | 669 committed | Receipt growth is itself a measurable workflow cost; 563 are under next-scenario work. |
| Generic scenario scripts | not a coherent local product command | 6 (`scenario_*`, `reconstruct_scenario_source.py`, master-EN build/verify) | This is the migration seed, not a greenfield rewrite. |

`PROJECT_STATUS.md` and the local `README.md` also describe a much older
fixture-heavy checkpoint. They must not be used to infer the remote reusable
pipeline's actual capability without first integrating or inspecting the
committed remote baseline.

## Test inventory and classification

The table below classifies 45 non-helper remote test files by primary intent.
`test definitions` counts source-level `def test_*`; parameterization and
`unittest` expansion make executed case counts larger, so it is a stable
consolidation sizing metric rather than a claimed pytest total.

| Class | Files | LOC | Test definitions | Keep/change recommendation |
| --- | ---: | ---: | ---: | --- |
| Reusable behavioral coverage | 5 | 3,423 | 161 | Keep and move shared fixtures/import seams into a test-support package. Includes `test_scenario_contract.py`, `test_scenario_source_reconstruction.py`, `test_build_scenario_master_en.py`, `test_verify_scenario_master_en.py`, `test_viral_publication_projection.py`. |
| Data-driven fixture/contract matrices | 20 | 9,523 | 235 | Retain security/fail-closed coverage, but consolidate into parameterized fixture families and declarative mutation catalogues. Includes raw-PDF Stage A, page-proof, and Step 5 non-live suites. |
| Generated/state assertions | 7 | 2,033 | 69 | Convert most to runner-produced manifest/verification assertions. Keep a small integration set. Includes `test_*freeze*`, `test_innsmouth_final_result.py`, `test_innsmouth_source_to_artifacts.py`. |
| One-off scenario evidence | 13 | 1,942 | 107 | Move scenario facts into contract/config fixtures and retain only explicit scenario acceptance tests. Includes Innsmouth builder/freeze tests and MinerU/Viral authoring helpers. |

The classification is intentionally not a deletion list. Fixture-only raw-PDF
and page-proof suites are valuable as component regression tests. They are not
appropriate as repeated per-run review gates once their acceptance facts are
already machine-verifiable in a sealed run manifest.

### Concrete duplication seams

1. **Duplicate v2 test construction.** Both
   `test_build_scenario_master_en.py` (955 LOC) and
   `test_verify_scenario_master_en.py` (755 LOC) implement overlapping
   `eol_profile`, `_v2_fixture_base`, `v2_fixture`, `bind_v2_inputs`,
   `bind_v2_decision_evidence`, and `refresh_v2_review_units` helpers. Extract
   these to `tests/support/master_en_v2_fixture.py`. Initial measurable target:
   remove at least six duplicate helper implementations and 350 source lines
   while preserving the distinct builder/verifier behavior tests.

2. **Dynamic script loading hides a package boundary.** At least 20 local and
   21 remote test modules use `importlib.util.spec_from_file_location` or
   mutate `sys.path` to load files from `scripts/`. The two generic master-EN
   suites dynamically load both builder and verifier (and authoring code). Move
   callable functions to `kb_creator.pipeline`/`kb_creator.stages`, keep
   `scripts/*.py` as two-to-five-line CLI adapters, and import the package in
   tests. Target: no dynamic loading in new generic tests; reduce the existing
   21 remote loaders to documented legacy adapters during migration.

3. **Repeated integrity primitives.** SHA-256, canonical JSON, relative-path
   containment, inventory sealing, regular-file/reparse checks, atomic/no-
   overwrite writes, and subprocess command records recur in
   `build_innsmouth_source_to_artifacts.py` (4,010 LOC),
   `build_scenario_master_en.py` (1,931),
   `verify_scenario_master_en.py` (1,356),
   `scenario_source_reconstruction.py` (1,648), freeze scripts, and tests.
   Extract one internal `pipeline_core` module: `paths`, `jsonio`, `identity`,
   `inventory`, `run_record`, and `errors`. Target: all new stages consume this
   API; no second implementation of inventory hashing or safe write semantics.

4. **Bespoke single-purpose stage scripts.** `audit_innsmouth_page_043_handout_structure.py`,
   `audit_innsmouth_pages_041_042_letter_handouts.py`,
   `audit_innsmouth_source_structure.py`,
   the running-header/fused-lead ledgers, exact-residue preflight/apply/QA, and
   historical build scripts encode stage configuration in Python. Their stable
   predicates should become named rules in the scenario contract or a
   `rules/*.json` policy pack; code becomes generic evaluators. Target: no new
   scenario-named executable for a rule that is expressible as data plus a
   shared evaluator.

5. **Source-text/AST review surrogates.** At least 29 remote test files inspect
   source text, AST, or scripts directly; particularly dense examples are
   `test_verify_scenario_master_en.py` (30 matches),
   `test_materialize_mineru_ai_merge.py` (24),
   `test_build_scenario_master_en.py` (14), and
   `test_step5_non_live_containment.py` (14). Keep AST tests only for explicit
   policy invariants that cannot be exercised through a public API (for example
   an enforced no-live-input boundary). Replace implementation-shape checks with
   behavioral negative tests and contract validation. Target: label every AST
   check `policy-static` or migrate it; cut non-policy source inspection by at
   least half.

6. **Review evidence is repeated in prose.** `origin/main` contains 669 plan
   handoffs: 563 under `20260830-kb-creator-next-scenario`, 106 critic-labelled,
   289 engineering-labelled, 102 execution/QA-labelled, and 150
   orchestration-labelled. This indicates repeated authorization/review of
   mechanical transitions. A runner must generate a compact evidence index;
   only semantic exceptions, visual adjudications, stage-design changes, and
   frozen-candidate release review require human receipts.

## Recommended automation architecture

```text
scenario contract + policy/rule packs + explicit source paths
                         |
                 kb_creator run
                         |
  preflight -> reconstruct -> normalize/project -> build -> verify -> package
       |             |               |             |         |          |
   input seal    recovery pkg    typed model   artifacts  QA report  run manifest
                         \______________ cache/resume keys ___________/
                         |
              review queue (only unresolved semantic/visual units)
```

### Public CLI contract

Use one stable command, for example:

```powershell
python -m kb_creator run --contract contracts/viral.json --source <PDF> --run-root <empty-run-dir> --profile full
```

Subcommands should be `preflight`, `run`, `verify`, `package`, and `review
queue`; they all consume the same resolved `RunSpec`, rather than chaining
scenario-specific scripts. Required behavior:

- Parse and strictly validate `scenario_contract.v1.schema.json`, then resolve
  all paths and input identities before any artifact write.
- Give each declared stage typed inputs, outputs, dependency hashes, tool
  versions, deterministic cache key, and a declared invalidation policy.
- Create a fresh sealed run root with a canonical `run.json`, stage receipts,
  artifact inventory, machine-readable verification report, human-readable
  summary, and a final package manifest. Resume only a stage whose full input
  identity matches; otherwise fail closed with a distinct exit code.
- Write visual/semantic candidates to `review_queue.json` with source pages,
  reasons, and contact-sheet references. User adjudication is a signed data
  file referenced by the next run; it is not a new bespoke script or prose
  handoff.
- Reserve exit code `0` for a fully verified non-release run, `2` for bad
  invocation/contract, `3` for identity or preflight failure, `4` for blocked
  human review, and `5` for verification/package failure. A release decision
  remains an independent human critic gate outside the command.

### Reusable modules to extract before new features

1. `kb_creator.pipeline.core`: canonical JSON, hashing, safe paths, immutable
   writes, inventories, structured errors, subprocess/version capture.
2. `kb_creator.pipeline.contracts`: the existing `scenario_contract` loader,
   schema/profile validation, resolved `RunSpec`, policy/rule-pack schemas.
3. `kb_creator.pipeline.stages`: wrappers around reconstruction, source
   partition/projection, master build, verification, render, and package;
   each exposes `preflight(context)`, `execute(context)`, `verify(context)`.
4. `kb_creator.pipeline.evidence`: standard stage receipts, verification
   facts, review-queue units, and final manifest/index.
5. `tests/support`: source fixture factory, mutator catalogue, inventory
   resealer, v2 master fixture, and CLI test runner.

## Migration order and measurable acceptance

| Wave | Change | Acceptance evidence | Quantified target |
| --- | --- | --- | --- |
| 0 — establish baseline | Integrate/inspect `origin/main` in an isolated integration step; inventory old vs generic paths without changing production behavior. | Read-only comparison and selected current tests. | No adoption decision based on local untracked experiments. |
| 1 — package seams | Extract `pipeline.core`, `pipeline.contracts`, and test support; turn existing scripts into adapters without altering CLI behavior. | Unit tests plus current adapter smoke tests. | Remove six duplicated v2 helpers; no new dynamic script import. |
| 2 — one run model | Add `RunSpec`, stage protocol, run manifest, deterministic cache/resume and standard error codes. Wrap reconstruction + generic master build + verifier first. | Synthetic end-to-end run produces sealed inventory and verification report twice with identical identity. | One command replaces at least three manual generic invocations. |
| 3 — rule data | Move recurring Innsmouth/Viral predicates into versioned policy packs and generic evaluators; retain only irreducible code hooks. | Contract/rule schema validation and mutation catalogue matrix. | No newly added scenario-named audit script for data-expressible rules. |
| 4 — test portfolio | Consolidate test fixtures; separate unit, contract mutation, integration, and release smoke markers. | Marker-selected CI matrix and one full synthetic run. | Classify all 45 non-helper remote test files; reduce non-policy source/AST inspection by >=50%. |
| 5 — review reduction | Generate `evidence/index.json` and `review_queue.json`; make plans link to one run id instead of reproducing mechanical checks. | A single run package explains inputs, outputs, checks, blockers, and queue. | Routine stages require zero prose handoffs; retain human receipt for semantic exception and release gates. |

## Risks and safeguards

- Do not merge generic and legacy Innsmouth paths by copying behavior blindly:
  `pdf_raw`/page-proof suites are deliberately fail-closed fixture controls and
  need a separately approved adapter boundary.
- Do not make `review_queue.json` auto-approval. An unresolved or changed
  semantic/visual decision must block packaging/promotion.
- Avoid a monolithic replacement of the existing 1,000–4,000 LOC scripts.
  First introduce modules beneath current CLIs, prove parity with synthetic
  contracts, then retire adapters only after a controlled migration.
- A sealed run is reproducibility evidence, not an independent release
  decision. Preserve the independent critic release gate.

## Files checked

- Governance and goal state: `docs/governance/nri_goal_governance.md`,
  `kb_creator/README.md`, `kb_creator/PROJECT_STATUS.md`, and this goal's
  `context.md` / `plan.md`.
- Local scripts/tests/fixtures/contracts under `kb_creator/scripts`,
  `kb_creator/tests`, `kb_creator/pdf_raw`, `kb_creator/inputs`, and
  `kb_creator/docs/contracts`.
- Committed remote baseline: `origin/main` scripts/tests/contracts named above,
  the eight incoming `kb_creator` commits, and plan-tree handoff inventory.

## Verification/evidence

- Read-only inventory: local 29 scripts and 46 Python test files; remote 44
  scripts and 47 Python test files.
- Read-only remote test classification: 45 non-helper files, 16,921 LOC and
  572 source-level test definitions across the four categories above.
- Read-only remote handoff classification: 669 Markdown handoffs, with 563 in
  the next-scenario plan alone.
- No tests or project scripts were run, by assignment constraint. No files were
  changed other than this receipt.

## Blockers and next action

Blocker: `main` is behind `origin/main` by eight commits and dirty with unrelated
user work. This receipt deliberately makes no integration, reset, commit, or
push decision.

Next action for the orchestrator: combine this receipt with R2 and R4 into the
prioritized review report; make the first implementation packet an isolated
package/test-support extraction from the committed remote baseline, with a
synthetic-contract parity test. Keep Git integration and the user-requested
scoped push as a separate, surgical operation after the report is finalized.

Elapsed time: approximately 19 minutes.
Token use: unavailable (platform does not expose a reliable per-agent count).
