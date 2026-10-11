# Architect receipt: `kb_creator` pipeline automation review

## Contributor receipt

- `goal_id`: `20260913-kb-creator-pipeline-automation-review`
- `step_id`: `R2`
- role: architect / root-cause and pipeline architecture
- requested policy model and effort: `gpt-5.6-sol` / `high`
- actual platform model and effort: unavailable
- orchestrator policy owner: `gpt-5.6-sol` / `medium`
- assignment state: `platform-unverified`
- scoped override: `none`
- scope: read-only review of the published and local `kb_creator` pipeline,
  dependency/branch/data-contract trace, manual-transition analysis, and a
  remediation specification for a user-runnable one-command pipeline
- result: `REMEDIATION_SPEC_READY`; the product has strong stage-local safety
  controls and accepted artifact boundaries, but no product-level run contract,
  shared lifecycle implementation, or resumable orchestrator. The minimum safe
  target is one fixed stage graph driven by a scenario specification and run
  specification, with explicit machine manifests and hash-bound human gates.
- changed files: this receipt only
- forbidden and unchanged: canonical plan/context/status/release files, all
  existing scripts/tests/contracts, source PDFs, working/output/reports,
  accepted packages, Foundry, Git index/history/remotes
- verification: static/read-only inspection only; no source, PDF, build, test,
  QA, renderer, promotion, Git mutation, or network command was run
- blockers: implementation must not start in the current local checkout until
  the orchestrator resolves the `main...origin/main [ahead 1, behind 8]` dirty
  boundary. Formal release acceptance remains an independent critic decision
  and cannot be automated by the proposed runner.
- next action: orchestrator integrates this stage graph with the engineer and
  critic receipts, freezes a bounded implementation plan, and starts Wave 0 in
  a clean checkout rooted at `origin/main`
- elapsed time: approximately 55 minutes
- token use: unavailable
- timestamp: `2026-09-13T05:25:27+03:00`

## Executive finding

The current system is not missing extraction, validation, or publication code.
It is missing a product-level control plane.

There are three partly overlapping implementations:

1. the historical monolithic Innsmouth runner, which can prepare source and
   translation work but intentionally stops when an accepted RU master is
   absent;
2. the current accepted Innsmouth vertical slice, which is reproducible but
   requires a long sequence of scenario-specific build, preflight, promote and
   verify commands plus user decisions between them;
3. the Viral generalization path, which has reusable extraction mechanics and a
   sophisticated MASTER_EN build/verifier pair, but remains scenario-bound and
   stops before a generic MASTER_RU/HTML/PDF/production route.

The safe remediation is not another wrapper that invokes all current scripts
in order. That would preserve hard-coded paths, duplicated lifecycle logic and
implicit manual gates. The target must make lifecycle state first-class:

```text
ScenarioSpec + RunSpec
        |
        v
fixed trusted stage graph
        |
        +--> deterministic machine stages
        |
        +--> hash-bound review/acceptance checkpoints
        |
        v
run manifest + QA/evidence index + review queue + artifact package
```

One command must either reach the requested target or stop safely with a
self-contained review/input packet and a stable resume command. It must never
infer acceptance from prose, a model message, a passing test count, or the mere
presence of an output directory.

## Authority boundary and evidence snapshot

The published baseline, not the dirty local branch, is the current system of
record for this review:

- local `main`: `bc77068bdc75e63af1a3746d846be6d64c1bf197`
  (`2026-08-29`, `Document local Docling runtime`);
- published `origin/main`:
  `5248894a5a5e696b8eba31e1d345f9825b726364`
  (`2026-09-04`, `Save Viral MASTER_EN rebuild and remediation progress`);
- observed branch state: `main...origin/main [ahead 1, behind 8]`;
- local `kb_creator` status: 573 rows, consisting of 568 untracked paths and
  five tracked modifications. These are user work/experiments, not published
  product evidence.

Representative published commits traced:

- `5952a224` — accepted Innsmouth MASTER_EN pipeline;
- `a7b2b215` — strict Innsmouth MASTER_EN promotion path;
- `bd0da472` — accepted Innsmouth MASTER_RU;
- `c3eafb99` — Innsmouth HTML/PDF publication pipeline;
- `4d6033d4` — reusable three-view reconstruction tooling and scenario contract;
- `5248894a` — rebuilt Viral MASTER_EN review checkpoint.

Files inspected include:

- `AGENTS.md` and `docs/governance/nri_goal_governance.md`;
- the assigned goal `plan.md` and `context.md`;
- published `kb_creator/README.md`, `PROJECT_STATUS.md`,
  `docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`,
  `docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md`;
- published next-scenario and direct-publication plan/context;
- `scenario_contract_architecture.md`, `contracts/viral.json`, its schema and
  the Viral reference README;
- all published script/test path inventories and representative source for
  extraction, reconstruction, MASTER_EN, acceptance, HTML, PDF and historical
  full-run flows;
- accepted Innsmouth EN/RU/HTML/PDF manifests and the Viral MASTER_EN
  verification report.

## Quantified current debt

All counts below are from `origin/main` unless explicitly marked local.

| Signal | Observed value | Architectural meaning |
|---|---:|---|
| Python scripts | 43 | many executable entrypoints, no single product CLI |
| PowerShell scripts | 1 | external MinerU adapter is separate from Python control flow |
| Python script LOC | 24,373 | implementation is large enough to require packages/interfaces, not more flat scripts |
| Scripts containing `Innsmouth` or `Viral` | 32/43 | scenario facts still dominate supposedly shared code |
| Python test/helper files | 47 | almost one top-level test module per script plus large historical proof suites |
| Python test LOC | 17,479 | test system is nearly three quarters of production script size |
| Schema-like `kb_creator.*` literals in scripts | 74 | stage contracts are fragmented and inconsistently enveloped |
| Plan-tree files | 695 | operational history is stored as many documents rather than generated run state |
| Handoff files | 669 total / 668 Markdown | contributor evidence has become an operational database |
| Handoffs in next-scenario goal | 564 | the second-scenario proof required hundreds of manual orchestration transitions |
| Next-scenario `plan.md` | 3,983 lines / about 239 KB | plan is a chronological ledger, not a compact executable plan |
| Next-scenario `context.md` | 3,375 lines / about 199 KB | context duplicates checkpoints and receipt identities |
| `PROJECT_STATUS.md` | 1,867 lines / about 97 KB | project rollup contains several historical/current narratives |
| `receipt SHA-256` occurrences in next plan+context | 165 | receipt linkage is manually repeated instead of indexed from manifests |
| Current Viral MASTER_EN review units | 441, priority sum 193 | a generated review queue is necessary; prose dispatch cannot scale |

Repeated mechanics are visible even before semantic comparison:

- `sha256_file` is redefined in 13 scripts and `sha256` in 11 more;
- `canonical_json` is redefined in 10 scripts;
- `write_json` is redefined in nine scripts;
- `acceptance_manifest` and `promote` are independently implemented four times;
- current accepted manifests use unrelated envelopes such as
  `InnsmouthAcceptedMasterEn.v1`, `InnsmouthAcceptedMasterRu.v1`,
  `kb_creator.innsmouth.accepted_html.v1` and
  `kb_creator.innsmouth.accepted_pdf.v1`.

The current schema is also narrower than its name suggests:
`scenario_contract.v1.schema.json` fixes `product_type=coc_scenario`, source
language `en`, publication languages `[en, ru]`, renderer profile
`viral_print`, and exact gate arrays. It is useful as the current two-scenario
proof, but it is not yet a general runtime contract.

## Actual current pipeline and branches

### Branch A: historical Innsmouth full runner

`scripts/build_innsmouth_source_to_artifacts.py` is a 2,781-line runner that:

```text
source identity checks
  -> render/normalize/source QA
  -> PyMuPDF text layer and cleanup
  -> column OCR reconstruction
  -> images/classification/contact sheet/approval preparation
  -> translation tasks and batches
  -> [stop if accepted RU master is absent]
  -> Keeper/HTML/PDF through legacy translator and Innsmouth helpers
  -> comparison report
```

It already demonstrates the correct high-level behavior of stopping before an
unavailable human-authored artifact. It is not the current production route:
the accepted Innsmouth chain later separated RECONSTRUCTED_EN, MASTER_EN,
MASTER_RU, HTML and PDF more strictly. It has run-local reports but no generic
cross-stage cache, resume graph, or acceptance state machine.

### Branch B: accepted Innsmouth production vertical slice

The published operational chain is:

```text
source PDF
  -> build_innsmouth_reconstructed_en.py
  -> build_innsmouth_master_en.py
  -> freeze_innsmouth_master_en_repo_input.py
  -> externally produced/accepted MASTER_RU candidate
  -> freeze_innsmouth_master_ru_repo_input.py
  -> build_innsmouth_html_from_master_ru.py
  -> freeze_innsmouth_html_repo_input.py
  -> build_innsmouth_pdf_from_accepted_html.py
  -> freeze_innsmouth_pdf_repo_output.py
```

Each freeze script has separate `preflight`, `promote`, and `verify` modes.
Following the published PIPELINE documents requires at least 16 distinct
command invocations for reconstruction, builds and the four stage promotions,
not counting translation, visual inspection, corrections, or release review.
The safety behavior is good: exact upstream identities, closed inventories,
staging, refusal to overwrite, and independent verify modes are all present.
The orchestration and generic lifecycle abstraction are absent.

Hard-coded accepted dates, directory revisions, hashes, filenames, counts and
scenario-specific correction rules appear directly in scripts. The next
accepted revision therefore tends to require another script/test edit even
when the lifecycle itself did not change.

### Branch C: Viral reusable-core and MASTER_EN proof

The published reusable extraction path is:

```text
immutable PDF
  -> prepare_mineru_three_view_inputs.py
  -> run_mineru_three_view.ps1
       -> original_hybrid
       -> original_pipeline_ocr
       -> raster_hybrid
  -> compare_mineru_three_views.py
  -> build_mineru_visual_merge_bundle.py
  -> reviewed per-page decision JSON
  -> audit_mineru_ai_merge_fidelity.py
  -> materialize_mineru_ai_merge.py
  -> finalize_mineru_reconstruction.py
```

The resulting accepted reconstruction then feeds the current Viral publication
proof:

```text
contract + accepted reconstruction + source PDF + review evidence
  -> propose_scenario_semantic_units.py
  -> boundary/semantic review evidence
  -> author_viral_master_en_v2_config.py
  -> build_scenario_master_en.py
  -> verify_scenario_master_en.py
  -> build_master_en_visual_qa_bundle.py
  -> user reading/visual acceptance (still pending)
```

This branch currently ends at a verified MASTER_EN review checkpoint. There is
no generic MASTER_RU, visual-finalization, HTML, PDF or production handler.
The supposedly generic builder is 1,931 lines with 139 `Viral` occurrences;
the independent verifier is 1,356 lines with 118 `Viral` occurrences; the v2
config author is 1,039 lines with 124 `Viral` occurrences and fixed working
paths. The older `scenario_source_reconstruction.py` is 1,648 lines and pins
source/profile facts and worktree authority.

`propose_scenario_semantic_units.py` also illustrates the danger of implicit
acceptance: it writes `confirm`, `adjusted_boundary`, and `reject` decisions
from heuristics while recording a caller-provided reviewer and a fixed
`USER_REVIEW...` provenance string. Generated proposals are valuable, but a
proposal generator must not author the final human decision manifest.

## Missing orchestration and manual transitions

The missing transitions are structural, not merely documentation gaps:

1. No command validates the complete toolchain before the first write.
   `kb_creator` has no project-level `pyproject.toml`, dependency lock,
   task-runner definition, or `doctor` command in the published tree.
2. No run manifest binds one execution to scenario contract, source, tools,
   stage configs, output roots and requested target.
3. No fixed state machine determines which stage may consume which accepted or
   candidate predecessor.
4. Review and acceptance live across prose, handoffs, user chat, bespoke JSON,
   hashes in plans, and directory naming. They are not one typed checkpoint.
5. Resume is local and inconsistent. Input preparation and visual-bundle code
   have `--resume`; many other builders require an absent root; none share a
   downstream invalidation rule.
6. Cacheability is implicit. Outputs may be hash-bound, but no stage key says
   whether a result is reusable under current source/config/code/tool versions.
7. Failure state is not uniform. Some commands return 1, comparison returns 2,
   some print success markers, and others raise exceptions. A caller cannot
   reliably distinguish `needs review`, `invalid input`, `tool missing`,
   `quality gate failed`, and `unsafe resume`.
8. The manual translation boundary is real but not modeled. A script cannot
   deterministically invent or accept MASTER_RU. It needs either a configured
   translation adapter plus review, or a typed `awaiting_input` package.
9. The independent release gate is governance, not a build step. The runner
   can freeze and verify a release candidate and export evidence; it cannot
   self-approve release.

## Target fixed stage graph

The graph is fixed in trusted code. Scenario data may select only named,
allowlisted strategy/profile identifiers; it may not provide arbitrary Python
imports, shell commands, or a custom DAG.

```text
00 doctor
   |
01 intake --------------------------------------------------+
   | source identity + contract validation                  |
02 extraction.prepare                                       |
   +--> 03a mineru.original_hybrid -----+                   |
   +--> 03b mineru.pipeline_ocr --------+--> 04 compare     |
   +--> 03c mineru.raster_hybrid -------+                   |
                                               |             |
05 reconstruction.review_bundle               |             |
   |                                           |             |
06 GATE reconstruction_decisions <------------+             |
   | decision manifest accepted                              |
07 reconstruction.materialize_and_verify                     |
   |                                                         |
08 GATE reconstructed_en_acceptance                          |
   |                                                         |
09 master_en.author_build_verify                             |
   |                                                         |
10 master_en.review_bundle                                   |
   |                                                         |
11 GATE master_en_acceptance                                 |
   |                                                         |
12 master_ru.acquire_or_translate                            |
   +--> configured adapter -> draft                          |
   +--> no adapter -> AWAITING_INPUT packet                  |
   |                                                         |
13 master_ru.verify                                          |
   |                                                         |
14 GATE master_ru_acceptance                                 |
   |                                                         |
15 visual_assets.finalize -> artview/review bundle           |
   |                                                         |
16 GATE visual_asset_acceptance                              |
   |                                                         |
17 html.build_verify                                         |
   |                                                         |
18 GATE html_acceptance                                      |
   |                                                         |
19 pdf.build_verify -> full render bundle                    |
   |                                                         |
20 GATE pdf_acceptance                                       |
   |                                                         |
21 production.build_verify                                   |
   |                                                         |
22 release_candidate.freeze + evidence export ---------------+
   |
23 EXTERNAL GATE independent release review
```

### Branching rules

- Stages 03a-c may execute in parallel, but stage 04 starts only when all three
  output manifests verify against stage 02.
- A quality failure never falls back silently from one extraction view to
  another. The comparison/review bundle records the alternatives.
- A missing translation adapter is not an error. Stage 12 returns
  `awaiting_input` and exports the exact MASTER_RU input contract.
- A configured translation adapter produces a draft only; stage 14 still needs
  a hash-bound user decision.
- Visual binary finalization remains after the RU master and before HTML, as
  accepted by the current Viral plan. Semantic asset identity/ownership is
  established upstream; binary choice is a separate gate.
- `--to` may stop at any public stage. Downstream stages cannot be selected if
  an upstream acceptance manifest is absent or invalid.
- Formal release remains external. `--to production` may produce a verified,
  frozen release candidate with state `pending_independent_release_review`,
  never `released`.

## Proposed command contract

Primary entrypoint:

```powershell
python -m kb_creator.pipeline run `
  --contract kb_creator/contracts/viral.v2.json `
  --source D:\path\Call_of_Cthulhu_Viral.pdf `
  --run-root D:\NRI-runs\viral\20260913T... `
  --to production
```

Required supporting commands:

```text
python -m kb_creator.pipeline doctor [--profile <name>]
python -m kb_creator.pipeline status --run-root <root>
python -m kb_creator.pipeline verify --run-root|--accepted-root|--package <path>
python -m kb_creator.pipeline review export --run-root <root> --stage <stage>
python -m kb_creator.pipeline review import --run-root <root> --decision <json>
python -m kb_creator.pipeline accept --run-root <root> --stage <stage> --decision <json>
python -m kb_creator.pipeline resume --run-root <root> [--to <stage>]
python -m kb_creator.pipeline promote --run-root <root> --stage <stage> --target <absent-root>
```

For a fresh scenario, `run --to production` is still the one operational
entrypoint. It runs until the first genuine human/input boundary, emits a
complete packet, and exits with `review required`. After the user supplies the
decision/input, `resume` continues without an AI orchestrator. If all required
decision manifests and accepted upstreams are already supplied, the original
`run` command can reach the package in one invocation.

No command defaults to `promote`, overwrites an accepted target, modifies a
source, commits, pushes, or claims release acceptance.

## Data contracts

### 1. `ScenarioSpec.v2`

Durable, reviewed scenario facts only:

- scenario id/title/product/languages;
- source identity and complete page topology;
- required entity classes and reader/excluded scope;
- named extraction/publication/translation/render profiles;
- artifact names and presentation policy;
- closed, scoped exceptions with selectors and expected match counts;
- required user/reviewer gates.

It must not contain runtime paths, current run ids, candidate hashes, timestamps,
tool versions, stage status, executable import paths, or a custom graph.
The current `ScenarioContract.v1` should remain supported as a compatibility
input until both Innsmouth and Viral parity pass; it should not be silently
relabelled generic.

### 2. `RunSpec.v1`

One immutable input document created at run start:

- scenario contract identity;
- source locator plus verified identity;
- requested target stage;
- run root and cache root;
- named toolchain profile and resolved tool versions;
- execution options (`offline`, concurrency, render DPI, cache policy);
- external input/decision manifest locators;
- no secrets and no device-specific values copied back to ScenarioSpec.

### 3. `StageManifest.v1`

Every stage emits the same closed envelope:

```json
{
  "schema": "kb_creator.stage_manifest.v1",
  "run_id": "...",
  "scenario_id": "viral",
  "stage": "master_en",
  "attempt": 1,
  "state": "passed|awaiting_review|awaiting_input|failed|accepted",
  "inputs": [],
  "contract_sha256": "...",
  "config_sha256": "...",
  "implementation": {"id": "...", "sha256": "..."},
  "toolchain": [],
  "cache_key": "...",
  "artifacts": [],
  "inventory_sha256": "...",
  "metrics": {},
  "gates": [],
  "review_requirement": null,
  "diagnostics": [],
  "reproducible_payload_sha256": "..."
}
```

Timestamps and elapsed time live in the run event log or an unhashed metadata
section; they must not make deterministic stage payloads differ.

### 4. `DecisionManifest.v1`

A proposal and a decision are separate documents. The decision binds:

- review type and stage;
- exact candidate/stage-manifest identity;
- complete closed review-item domain;
- per-item decision and allowed adjustment payload;
- reviewer authority label and decision timestamp;
- referenced evidence identities;
- zero unhandled blocking items.

Generators may create proposals and pre-populated suggestions, but cannot set
the final authority or reuse a historical review label as proof of a new
decision.

### 5. `AcceptanceManifest.v1`

A common envelope for every promoted stage:

- accepted stage and scenario;
- exact candidate and upstream acceptance identities;
- ScenarioSpec and implementation identities;
- closed artifact inventory;
- passed gate summary;
- exact DecisionManifest identities;
- acceptance authority and date;
- explicit state `accepted`, not inferred from directory name.

Stage-specific metrics live under a typed payload keyed by stage schema. This
replaces four separately shaped promotion envelopes while keeping independent
stage validators.

### 6. `ProductionManifest.v1`

The final package contains stable artifacts, shared assets, the scenario and
run specifications, accepted-stage manifests, owning code/toolchain snapshot,
QA/evidence index, intentional exclusions, and a closed file inventory. It
does not contain the original PDF unless a scenario-specific distribution
policy explicitly permits it.

## Run-root and artifact layout

```text
<run-root>/
  RUN_SPEC.json
  RUN_STATE.json                 # derived current state, atomically replaced
  events.jsonl                   # append-only operational events
  stages/
    01-intake/attempt-001/
      stage.json
      artifacts/
    ...
  review_queue/
    index.html
    review_manifest.json
    items/
  reports/
    summary.json
    summary.md
    evidence_index.json
  candidate/
    reconstructed_en/
    master_en/
    master_ru/
    html/
    pdf/
  package/
    release_candidate/
```

`RUN_STATE.json` is a rebuildable index over immutable attempt manifests, not
an authority competing with them. Plan/context/status should link to a run
summary rather than copy every stage event or receipt hash.

## Cache and resume semantics

### Cache key

For each stage:

```text
SHA-256(
  stage-id + stage-contract-version + implementation digest
  + ordered input StageManifest/AcceptanceManifest digests
  + ScenarioSpec digest + stage-config digest
  + behavior-affecting tool versions/options
)
```

External engine output may be cached even if byte determinism is not promised,
but its manifest must say `reproducibility=engine-captured`, not
`deterministic`. A cache hit is accepted only after re-verifying the complete
artifact inventory. Paths, timestamps and machine names do not enter the
portable cache identity.

### Resume

- A fresh run root must be absent.
- `resume` first validates RunSpec, every completed StageManifest and every
  artifact inventory from the start of the chain.
- The first missing, invalid, or cache-key-mismatched stage is the resume point.
- A changed input/config/code/tool affecting a stage invalidates that stage and
  all downstream stages. Old attempts remain immutable evidence; the runner
  creates `attempt-N+1` rather than editing or deleting them.
- `awaiting_review` resumes only with a DecisionManifest bound to the exact
  candidate hash. Candidate mutation invalidates the decision.
- `awaiting_input` resumes only when the supplied artifact satisfies the
  exported input contract and is copied into a new staged attempt.
- Accepted/published packages are never invalidated in place. A new run creates
  a new acceptance revision.

### Atomicity and failure quarantine

- All writes occur in a same-parent staging directory.
- Success atomically renames the stage attempt into place.
- On failure, partial output moves to an explicit failed/quarantine attempt or
  is retained in the staging root with a machine record; it is never consumed
  as a successful predecessor.
- A target that already exists is an error unless it is the exact validated run
  root supplied to `resume`.
- Windows reparse points/symlinks and paths escaping the declared run root are
  rejected.

## Exit-code contract

| Code | Meaning | Required artifact |
|---:|---|---|
| 0 | requested target reached and verified | final `stage.json` and summary |
| 10 | human review required | review packet + stable resume command |
| 11 | external input required | typed input packet + stable resume command |
| 20 | invalid ScenarioSpec/RunSpec/config | diagnostic report, no stage output |
| 21 | missing/incompatible toolchain | doctor report, no mutating stage started |
| 22 | source/upstream identity mismatch | failed stage manifest |
| 23 | deterministic/quality gate failure | failed stage manifest + findings |
| 24 | unsafe resume/cache/provenance mismatch | mismatch report, downstream untouched |
| 25 | occupied or escaping target | diagnostic report, target untouched |
| 30 | external engine/renderer failure | captured command record + quarantined attempt |
| 40 | unexpected internal error | redacted diagnostic + quarantined attempt |

Human-readable success markers may remain for compatibility, but automation
must depend on exit code plus manifest state, not stdout text.

## Proposed module boundaries

```text
kb_creator/pipeline/
  __main__.py                    # CLI only
  graph.py                       # fixed stages and legal transitions
  runner.py                      # scheduling, stop/resume, invalidation
  models.py                      # ScenarioSpec/RunSpec/manifest models
  lifecycle.py                   # stage attempt, atomic publish, quarantine
  identity.py                    # hashing, canonical JSON, inventory
  process.py                     # external command capture/redaction
  cache.py                       # content-addressed lookup/validation
  review.py                      # review export/import/acceptance binding
  evidence.py                    # summary and evidence index generation
  doctor.py                      # Python/MinerU/Poppler/browser/fonts checks
  stages/
    intake.py
    extraction.py
    reconstruction.py
    master_en.py
    master_ru.py
    visual_assets.py
    html.py
    pdf.py
    production.py
  adapters/
    mineru.py
    translation.py
    html_renderer.py
    pdf_renderer.py
```

Named adapters are selected from a trusted registry. Scenario config supplies
data and allowlisted profile ids, never import paths or shell fragments.

The first implementation should wrap proven scripts through adapters rather
than rewrite algorithms immediately. Shared lifecycle/identity code must be
used by the new runner from the first slice. Current accepted scripts remain
frozen reference implementations until parity is demonstrated.

Independent verification is retained at high-risk boundaries, but it must be
contract-level independence, not a second copy of every helper:

- builder and verifier must not share semantic projection logic;
- they may share canonical JSON, hashing, inventory parsing and closed schema
  models;
- ordinary unit validation runs once in the stage;
- acceptance verification rechecks identities and externally observable
  invariants, not the builder's entire internal algorithm.

## Prioritized migration plan

### Wave 0 — establish a safe baseline and executable contracts (P0)

1. Start from a clean checkout/worktree at `origin/main`; do not merge the 573
   local `kb_creator` status rows into this work.
2. Freeze parity fixtures from the accepted Innsmouth packages and the Viral
   MASTER_EN review checkpoint. Reference them by manifest identity, not by
   ignored working paths.
3. Introduce the package skeleton, `doctor`, fixed graph, RunSpec,
   StageManifest, identity/inventory helpers and uniform exit codes.
4. Add read-only `status` and `verify` before any build adapter.
5. Define generated `summary.json`, `summary.md`, and evidence index.

Exit criterion: a no-op fixture run can be created, inspected, resumed and
rejected on source/config/code mutation without touching existing outputs.

### Wave 1 — automate intake through reconstruction review (P0/P1)

1. Wrap the five currently reusable MinerU three-view scripts.
2. Add a toolchain profile for MinerU, Poppler and Python discovery.
3. Run three views under one stage group with captured versions/commands.
4. Generate comparison and visual review queue automatically.
5. Split proposal from decision; import exact page decisions through the common
   DecisionManifest.
6. Wrap audit/materialize/finalize and emit one reconstruction StageManifest.

Exit criterion: one command reaches `awaiting_review`; after a fixture decision
import, `resume` creates and verifies RECONSTRUCTED_EN. No agent or hand-written
handoff is needed for the happy path.

### Wave 2 — generalize MASTER_EN without rewriting accepted logic (P1)

1. Move Viral facts and fixed paths out of the 1,039/1,931/1,356-line
   author/builder/verifier surfaces into typed scenario/profile data.
2. Keep the builder/verifier semantic separation; eliminate duplicated
   lifecycle, path and identity code.
3. Replace boundary-ledger prose routing with generated proposal/review
   manifests and a closed migration ledger.
4. Build the visual QA bundle as a standard review stage.
5. Prove both Viral checkpoint parity and Innsmouth compatibility; do not claim
   generic support from Viral-only fixtures.

Exit criterion: `run --to master_en` works for two scenario fixtures and either
returns a verified candidate or a complete hash-bound review packet.

### Wave 3 — generic accepted-stage lifecycle and downstream publication (P1)

1. Extract the common preflight/promote/verify machinery from the four
   Innsmouth freeze scripts.
2. Introduce MASTER_RU `acquire_or_translate` with explicit external-input
   behavior and terminology/structure verification.
3. Generalize HTML and PDF handlers behind named renderer profiles.
4. Keep user reading, visual-navigation and print gates explicit.
5. Add post-RU visual binary finalization and `artview.html` generation.

Exit criterion: accepted Innsmouth artifacts can be reproduced byte-for-byte
or explained by an explicitly approved renderer/toolchain delta; Viral can
advance through the same interfaces without copied `build_viral_*` scripts.

### Wave 4 — production package and offline verification (P1/P2)

1. Build stable unversioned package names from accepted stage manifests.
2. Include contract/config/code/toolchain snapshots and a closed evidence
   index.
3. Add `verify --package` that works on a clean machine without working roots,
   source PDF, chat history, or plan/handoff corpus.
4. Export one release-review packet; do not create machine release approval.

Exit criterion: the user can run one command plus explicit review/resume steps
and obtain a self-contained verified package and release-candidate evidence.

### Wave 5 — deprecate legacy surfaces after parity (P2)

1. Mark historical runners and scenario-specific scripts as reference-only.
2. Remove no files until two-scenario parity, clean-checkout QA and release
   review approve the new route.
3. Stop adding handoffs for successful machine stages. Keep one run summary;
   retain contributor receipts only for material design/implementation/release
   work required by governance.
4. Reduce PROJECT_STATUS to active goal links and last accepted package; keep
   history in immutable manifests and Git.

Exit criterion: no supported scenario requires manual invocation of a legacy
stage script, and operational state is reconstructible from run/package
manifests rather than prose chronology.

## Risks and controls

| Risk | Control |
|---|---|
| Automation silently claims human acceptance | candidate proposal and DecisionManifest are different schemas; exact candidate binding; exit 10/11 |
| Refactor invalidates accepted Innsmouth evidence | strangler/wrapper migration; existing scripts immutable until parity; golden manifest tests |
| MinerU/browser output varies by machine | capture toolchain/settings; distinguish deterministic from captured-engine cache; require downstream visual gates |
| Cache reuses stale or tampered output | full cache-key inputs plus inventory re-verification; downstream invalidation |
| Scenario contract becomes executable code | fixed graph and allowlisted adapters/profiles; no import path or command fields |
| Shared verifier reproduces builder bugs | share only identity/schema primitives; keep semantic verifier independently implemented |
| Duplicate independent reviews remain | one architecture review per material design, one implementation review per frozen slice, one final release review; machine gates are not reviews |
| Translation is treated as deterministic script output | stage 12 is adapter-or-awaiting-input; user reading gate is mandatory |
| Accepted packages are overwritten on resume | absent-target promotion, immutable attempts, new acceptance revision |
| Windows staging/reparse behavior breaks containment | same-parent atomic stage, reparse-point rejection, tested interruption recovery |
| Source-derived/copyrighted data leaks into Git/package | source distribution policy is explicit; default production manifest excludes source PDF and run-local OCR/review payloads |
| Cache and evidence roots grow without bound | pin accepted/release-linked entries; separate explicit `gc --dry-run` policy later; never treat ignored as disposable |
| Current dirty/diverged tree contaminates implementation | clean `origin/main` worktree and exact path-scoped commits |

## Acceptance criteria for the target pipeline

### Functional

1. `run --contract --source --run-root --to production` is the only required
   build entrypoint for an already fully authorized run.
2. On a fresh scenario it reaches the first genuine review/input boundary and
   emits a complete review/input packet, summary and exact resume command.
3. After importing a valid decision/input, `resume` continues without editing
   scripts, plans, paths or hashes by hand.
4. The final candidate package includes MASTER_EN, MASTER_RU, HTML, PDF,
   required assets, QA reports, accepted-stage manifests, owning config/code
   snapshot and a closed ProductionManifest.
5. A clean-machine `verify --package` needs neither working directories,
   original chat/history nor hundreds of receipts.

### Safety and provenance

6. Source is opened read-only and verified by bytes/hash/page facts before any
   mutating stage.
7. Every stage consumes only verified predecessor manifests and emits one
   common StageManifest envelope plus a typed payload.
8. Candidate, accepted and released states are distinct; a directory name or
   passing tests cannot promote state.
9. Every human decision is bound to an exact candidate and full review-item
   domain. Candidate mutation rejects the decision.
10. All writes are contained, staged atomically, fail closed, and never
    overwrite an accepted target.
11. A failed/aborted run cannot leave an output that a later stage recognizes
    as passed.
12. Formal release remains pending until an independent critic receipt is
    attached to the unchanged frozen candidate.

### Resume and reproducibility

13. Re-running the same deterministic fixture with identical inputs, configs,
    implementation and toolchain produces identical artifact and inventory
    hashes; timestamps do not affect the hashed payload.
14. Source/config/implementation/toolchain mutation invalidates exactly the
    affected stage and its descendants while preserving old attempts.
15. A valid cache hit is accepted only after inventory verification and is
    visible in events/summary.
16. Interruption at every mutating stage has a tested resume or quarantine
    outcome.

### Maintainability

17. New generic stage handlers contain no `Innsmouth`, `Viral`, dated accepted
    directory, scenario hash or device-local path literals.
18. Hashing, canonical JSON, inventory, stage lifecycle, process capture and
    promotion have one shared implementation each.
19. Scenario-specific facts are covered through contract/profile fixtures; a
    new scenario does not require copying or renaming stage scripts.
20. Tests are organized by reusable behavior, contract/profile matrix and a
    small number of end-to-end golden scenarios; clean-checkout tests do not
    depend on ignored `working/` artifacts.
21. A successful machine-only run creates zero contributor handoffs. Material
    architecture/implementation/release receipts remain governance artifacts,
    not operational stage state.
22. PROJECT_STATUS links the active goal and latest accepted package/run
    summary instead of reproducing the full event ledger.

### Required parity gates before legacy deprecation

23. Innsmouth accepted EN/RU/HTML/PDF inventories remain verifiable and the new
    route reproduces them or records an explicitly reviewed deterministic
    migration delta.
24. Viral MASTER_EN fixture reproduces the published candidate inventory
    `44BA578421ACFD95884E635DE89CB13D57C4A9259A9E0E63D96699106F802268`
    and its current 185 hierarchy / 1,216 event / 155 typed-structure / 93
    reader-asset expectations before downstream generalization is accepted.
25. Both scenarios pass from a clean checkout with source/run roots supplied
    externally and no pre-existing ignored candidate.

## Architectural non-goals

- Do not automate or waive user reading/visual/print acceptance.
- Do not automate the independent release verdict.
- Do not put a configurable arbitrary DAG or executable commands in scenario
  JSON.
- Do not generalize beyond the proven CoC scenario, EN-source, RU-publication
  domain in the first implementation.
- Do not rewrite extraction/publication algorithms merely to introduce the
  runner.
- Do not delete or rewrite historical receipts, tests, plans or accepted
  packages in this goal.
- Do not make Git commit/push part of the artifact runner.

## Final architectural recommendation

Build the control plane first, then migrate stages behind it. The initial
deliverable should be small: `doctor`, fixed graph, run/stage manifests,
content-addressed identity, uniform failure states, and one wrapped path from
intake to reconstruction review. That slice immediately lets the user launch a
safe run and receive a complete actionable packet without an AI orchestrator.

Do not begin by genericizing the 1,931-line Viral builder or by adding another
top-level orchestration script. Without the lifecycle contracts, that work
would repeat the current pattern at a larger scale.

`REMEDIATION_SPEC_READY`
