# KB Creator scenario pipeline reuse-preservation review — 2026-09-02

Status: `READY_FOR_PRESERVATION_IMPLEMENTATION`

This is an architecture/remediation specification, not a release decision and
not permission to mutate Candidate C, accepted reconstruction, source inputs,
or downstream publication stages.

## Contributor receipt

- `goal_id`: `20260830-kb-creator-next-scenario`
- `step_id`: `preservation-reuse-architecture`
- role: architect (`gpt-5.6-sol`, policy effort `high`)
- actual platform model/effort: unavailable
- orchestrator policy owner: `gpt-5.6-sol` / `medium`
- assignment state: `matched`
- scoped override: `none`
- scope: classify the accumulated Viral pipeline, trace dependencies and data
  contracts, identify misleading generic surfaces, specify a repository skill,
  and give an exact Git include/exclude boundary
- sole changed file:
  `kb_creator/docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md`
- forbidden and unchanged: scripts, tests, configs, contracts, source,
  reconstruction packages, Candidate C, plan/context/status/release files, Git
  index/history and all generated outputs
- result: reusable extraction/merge mechanics are separable now; Viral
  reconstruction and MASTER_EN code is valuable reference implementation but
  is not scenario-neutral under its current names or production profiles
- blockers: listed under `P0-P2 remediation`; they block the preservation
  commit, not this architecture handoff
- next action: Terra/medium implements only the accepted preservation allowlist
  and remediation, then bounded clean-checkout QA and independent review occur
- elapsed time: approximately 52 minutes
- token use: unavailable
- timestamp: `2026-09-02T11:35:46+03:00`

## Decision

Do **not** publish the current untracked tree as one commit. Preserve it in two
explicit layers:

1. a small scenario-independent reconstruction toolkit and repository skill;
2. a clearly named `Viral` reference layer containing its declarative contract,
   frozen publication policy, and scenario-bound enforcement/publication code.

Run-local source, MinerU runs, decisions, overlays, candidates, QA bundles,
scratch/staging roots, raw transcripts and the repetitive handoff corpus stay
out of Git.

The first preservation implementation may include the portable core and the
declarative Viral reference data. The current generic-looking Viral executables
must not enter that commit until they are renamed/moved or split as specified
below. Candidate C remains byte-frozen and is neither copied nor re-created.

## Assumptions and authority boundary

- The accepted architecture is the staged chain `source -> reconstruction ->
  MASTER_EN -> MASTER_RU -> HTML -> PDF -> production`; reconstruction fidelity
  and reader publication policy remain separate.
- `working/` is candidate/run state, not durable authority. A frozen config may
  be copied byte-for-byte to a reference path, but generated candidates and
  their source/reconstruction payloads are not thereby promoted.
- `contracts/viral.json` is declarative intake/topology data and is safe to
  preserve. It contains a relative locator hint, source identity, page roles,
  stage filenames and reviewed policies; it does not contain the source PDF.
- The 713,722-byte publication config is scenario policy/reference evidence,
  not reusable mechanics. Its current SHA-256 is
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Candidate C is still awaiting explicit user reading acceptance. This review
  neither changes nor accepts it.
- The repository has concurrent edits. In particular, a foreign `.gitignore`
  diff now admits `.agents/skills/**` and `kb_creator/contracts/**`. This review
  does not modify or claim ownership of that diff; implementation must inspect
  its final content rather than replaying it blindly.

## Dependency and branching trace

### Scenario-independent extraction and merge path

```text
immutable PDF
  -> prepare_mineru_three_view_inputs.py
  -> run_mineru_three_view.ps1 (external MinerU runtime)
  -> compare_mineru_three_views.py
  -> human/AI page decisions
  -> audit_mineru_ai_merge_fidelity.py
  -> materialize_mineru_ai_merge.py
  -> reconstruction candidate (run-local)
```

The first five scripts do not contain Viral/Innsmouth constants. Their matching
tests use temporary synthetic PDFs/JSON/assets and do not require the ignored
Viral working tree. They are the smallest useful reusable core.

Important data contracts:

| Producer | Consumer | Contract | Portability consequence |
|---|---|---|---|
| input preparer | MinerU/comparator | `sample_pages.json` with ordered sample-to-source mapping and identities | durable script; generated manifest stays run-local |
| three MinerU views | comparator | exactly `original_hybrid`, `original_pipeline_ocr`, `raster_hybrid`; content-list/layout artifacts | external-runtime outputs, never Git inputs |
| comparator | audit/materializer | `kb_creator.mineru_three_view_comparison.v1`, exact page mapping, block and asset references | currently records runtime paths; treat as run-local |
| reviewed page decisions | audit/materializer | closed `kb_creator.mineru_ai_merge_decision.v1` pages, selected block identities, Markdown, assets, blockers and review | decisions are source-derived run evidence, not reusable code |
| audit | human gate | token recall/substitution report and optional exact allowlist | report is evidence only; threshold is not acceptance authority |
| materializer | finalization | `RECONSTRUCTED_EN.md`, per-page Markdown, decision copies, asset manifest, overlay selection and merge provenance | candidate remains unaccepted until scenario gates pass |

### Viral reconstruction reference path

```text
contracts/viral.json
  + retained Viral source identity
  + recovery manifests/evidence
  -> scenario_source_reconstruction.py
  -> reconstruct_scenario_source.py
  -> sealed reconstruction candidate and mutation evidence
```

`scenario_source_reconstruction.py` is **not shared infrastructure** despite
its name. The 1,648-line module pins:

- branch `codex/kb-creator-viral` and HEAD
  `54607bd3b9362adbb0c4bca64e8751482797f380` (lines 19-20);
- Viral-only recovery schema names (line 23);
- the retained Viral PDF path/hash/size, `contracts/viral.json`, recovery
  hashes, blocker IDs and candidate state (lines 346-357);
- a `viral-production` profile and worktree-derived production context
  (lines 357-359).

Its 1,183-line `test_scenario_source_reconstruction.py` is a valuable
Viral Step 6A adversarial/mutation suite (368 mutation cases per the accepted
goal evidence), but it is a test of that sealed profile, not proof that a third
scenario can use the public API. Preserve the suite as Viral reference evidence;
do not market it as generic coverage.

### Viral MASTER_EN reference path

```text
contracts/viral.json
  + accepted reconstruction v4 (ignored working input)
  + publication_config_v1.json
  + immutable source PDF
  -> build_scenario_master_en.py
  -> verify_scenario_master_en.py (independent verifier)
  -> build_master_en_visual_qa_bundle.py
  -> Candidate C and visual bundle (run-local)
```

The builder/verifier split is architecturally reusable, but the present
implementation is Viral-bound. Examples include a literal `# Viral` invariant,
168 anchors, fixed page domain 1..124, 41/42 xref counts, 39 handouts, 91 visual
review units, 1,935/1,862/73 conservation counts and `viral-*` anchor rules in
`build_scenario_master_en.py` (notably lines 821, 824, 877 and 881). The visual
QA bundle requires `scenario_id == viral`, fixed cover/handout anchors and
123/107/91/39 counts (`build_master_en_visual_qa_bundle.py`, lines 115,
132, 169-183 and 272-279). The verifier tests import the real builder and bind
the ignored source, reconstruction v4, publication config and candidate root.

## Classification

| Item | Classification | Preserve in first commit? | Reason / required treatment |
|---|---|---:|---|
| `scripts/prepare_mineru_three_view_inputs.py` | reusable core | yes | scenario-free input preparation; synthetic tests |
| `scripts/run_mineru_three_view.ps1` | reusable core | yes | runtime root is an argument; machine/runtime output remains local |
| `scripts/compare_mineru_three_views.py` | reusable core | yes | scenario-free normalization/comparison; emitted absolute/runtime locators make outputs run-local |
| `scripts/audit_mineru_ai_merge_fidelity.py` | reusable core | yes | scenario-free fail-closed decision audit |
| `scripts/materialize_mineru_ai_merge.py` | reusable core | yes | scenario-free closed decision materialization; output is only a candidate |
| their three matching test modules | reusable core QA | yes | temporary synthetic fixtures; no Viral working-tree dependency |
| `scripts/build_mineru_visual_merge_bundle.py` | Viral reference with reusable helpers | no, pending split | `ROLES` hardcodes all 124 Viral page ranges (lines 18-21), default page count is 124; extract contact-sheet/inventory helpers or supply roles from reviewed contract |
| `tests/test_mineru_visual_merge_bundle.py` | Viral reference QA | no, pending split | explicitly proves the 124-page Viral role partition and 31-sheet result |
| `scripts/finalize_mineru_reconstruction.py` | Viral reference with reusable finalization mechanics | no, pending split | `EXPECTED_HANDOUTS` hardcodes Viral labels and 1..39 closure (lines 21, 130-134) |
| `tests/test_finalize_mineru_reconstruction.py` | Viral reference QA | no, pending split | builds 124 pages and the exact Viral handout set |
| `scripts/scenario_contract.py` | CoC/Viral reference contract implementation | no, pending rename/split | validator fixes `coc_scenario`, EN/RU, a closed role taxonomy, exact gate lists, `viral_print`, and Innsmouth shadow hashes |
| `contracts/scenario_contract.v1.schema.json` | CoC/Viral reference schema | yes, clearly labelled | preserve with validator data, but do not claim universal scenario support |
| `contracts/viral.json` | declarative Viral reference | **yes at current path** | portable relative data; required to preserve admitted source identity/topology/policies; source PDF remains excluded |
| `contracts/innsmouth.json` | compatibility-shadow reference | yes with schema | required by current contract tests and documents the non-runtime compatibility boundary |
| `tests/test_scenario_contract.py` | CoC/Viral reference QA | no until validator is renamed/split | mixes generic schema negatives with exact Viral and Innsmouth assertions |
| `scripts/scenario_source_reconstruction.py` | sealed Viral executable reference | no under current name | branch/SHA/source/recovery/profile pinned; its production route will be stale after a new commit |
| `scripts/reconstruct_scenario_source.py` | Viral CLI facade | no with current dependency | imports the sealed Viral production context |
| `tests/test_scenario_source_reconstruction.py` | sealed Viral adversarial suite | preserve only in renamed reference layer | 368-case mutation value is high, but its authority/profile is Viral Step 6A |
| `scripts/build_scenario_master_en.py` | Viral MASTER_EN reference builder | no under current name | hard-coded Viral topology, counts and reader invariants |
| `scripts/verify_scenario_master_en.py` | Viral MASTER_EN reference verifier | no under current name | independent verifier is valuable, but schema/count/identity closure is Candidate C/Viral-specific |
| `scripts/build_master_en_visual_qa_bundle.py` | Viral Candidate C QA tool | no under current name | fixed Viral identities/counts and Babez/p80/cover checks |
| three matching MASTER_EN tests | Viral integration/reference QA | no in first commit | `test_build_scenario_master_en.py` and `test_verify_scenario_master_en.py` load ignored live fixtures at module scope; clean checkout is not self-contained |
| `working/viral/master_en/publication_config_v1.json` | frozen Viral publication policy | **yes, by byte-identical copy to reference path** | see dedicated decision below; do not stage the `working/` path |
| `working/viral/source/**` | immutable local source | no | original/source PDF is excluded by repository policy |
| `working/viral/source_reconstruction/**` | run-local/source-derived evidence and candidates | no | MinerU outputs, decisions, overlays, accepted-v4 package and assets are heavy/source-derived runtime state |
| `working/viral/master_en/candidates/**` | generated/rejected/frozen candidates | no | includes rejected A/B, frozen C, scratch builds and four stale `.c2b-unittest.staging.*` roots |
| visual QA bundles and transported originals | generated QA evidence | no | evidence is summarized by identities; bundles/images stay scratch-only |
| `docs/plans/.../plan.md`, `context.md`, `handoffs/**` | goal-local governance/evidence | no in the reusable-code commit | 321 receipts / 3,320,413 bytes plus 305 KB plan/context are repetitive operational history; orchestrator may preserve canonical state separately |
| `docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md` | durable architecture summary | yes | compact stage/state model and prior generalization boundary |
| `docs/plans/.../scenario_contract_architecture.md` | durable design reference | yes | accepted data/mechanics boundary and stop conditions |
| this review | durable architecture + contributor receipt | yes | exact classification and remediation boundary |

## Explicit decisions on the frozen configs

### `contracts/viral.json`

Preserve it in Git at its current portable destination:

`kb_creator/contracts/viral.json`

Include the schema and Innsmouth compatibility shadow in the same reference-data
group:

- `kb_creator/contracts/scenario_contract.v1.schema.json`
- `kb_creator/contracts/innsmouth.json`

The current concurrent `.gitignore` change already proposes admitting
`kb_creator/contracts/**`; implementation must verify that final diff and stage
only the reviewed hunk. Do not include the source PDF.

### 713,722-byte `publication_config_v1.json`

Preserve it, because it is the only closed declarative record of the accepted
Viral MASTER_EN publication policy that produced Candidate C. Do **not** stage
it from `working/` and do not rewrite it for portability. Copy the exact bytes
to:

`kb_creator/reference/viral/master_en/publication_config_v1.json`

Required identity after the copy:

- bytes: `713722`
- SHA-256:
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`

Why this is acceptable: all inspected locators are repository-relative; no
device-local absolute path was found. Why it is still reference-only: it binds
the ignored accepted reconstruction v4, one review receipt and source-derived
asset identities. Therefore it is portable as a reviewed policy document, not
self-contained as a clean-checkout build input.

The active frozen config at `working/viral/master_en/publication_config_v1.json`
and Candidate C must remain unchanged. Current builder/verifier commands must
continue to use the frozen working path for Candidate C evidence. A future run
may use the reference copy only after byte identity is proved and a new run is
opened; no existing candidate manifest/provenance is re-sealed.

## Misleading generic names and target layout

The minimal safe layout is:

```text
kb_creator/scripts/
  prepare_mineru_three_view_inputs.py
  run_mineru_three_view.ps1
  compare_mineru_three_views.py
  audit_mineru_ai_merge_fidelity.py
  materialize_mineru_ai_merge.py

kb_creator/reference/viral/
  contracts/ or links to ../../contracts/viral.json
  reconstruction/
    viral_source_reconstruction.py
    reconstruct_viral_source.py
  master_en/
    publication_config_v1.json
    build_viral_master_en.py
    verify_viral_master_en.py
    build_viral_master_en_visual_qa_bundle.py
  README.md

kb_creator/tests/reference/viral/
  test_viral_source_reconstruction.py
  test_build_viral_master_en.py
  test_verify_viral_master_en.py
  test_build_viral_master_en_visual_qa_bundle.py
```

Equivalent module/package naming is acceptable; retaining the current generic
filenames while only adding a disclaimer is not. The source-reconstruction
module should be split when practical:

- reusable filesystem containment, closed inventory, atomic publish, hash and
  mutation-audit mechanics in a scenario-neutral module;
- branch/head/source/recovery hashes, blocker list and schemas in an explicit
  immutable Viral authority manifest/profile;
- the 368-case suite split into reusable mechanism tests and Viral-profile
  mutation cases.

No profile may pin the repository to the pre-preservation HEAD and still be
advertised as a current public API. Either the reference profile stays
historical/non-executable or a reviewed runtime authority manifest supplies the
expected revision without changing the frozen Step 6 evidence.

## Smallest useful repository skill

Create one routing skill, with no copied Python/PowerShell implementation:

` .agents/skills/kb-creator-scenario-reconstruction/SKILL.md `

(The surrounding spaces above are presentation only; the real path has none.)

The skill should trigger for a new KB Creator scenario, MinerU three-view
reconstruction, merge-decision audit, or reconstruction-candidate
materialization. It should route to exactly:

1. `kb_creator/scripts/prepare_mineru_three_view_inputs.py`;
2. `kb_creator/scripts/run_mineru_three_view.ps1`;
3. `kb_creator/scripts/compare_mineru_three_views.py`;
4. `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`;
5. `kb_creator/scripts/materialize_mineru_ai_merge.py`;
6. tests:
   `test_mineru_three_view_tools.py`,
   `test_audit_mineru_ai_merge_fidelity.py`, and
   `test_materialize_mineru_ai_merge.py`.

The skill must state:

- source inputs are immutable and generated roots must be absent or explicitly
  resume-bound;
- comparison, decisions, audit output and candidates are run-local;
- visual priority scores and AI decisions are candidate signals, not truth or
  acceptance;
- the scenario contract supplies topology and required entities; the skill
  must not copy Viral page ranges/counts;
- promotion, user acceptance, downstream MASTER_EN/RU/HTML/PDF, Git and release
  review are outside this skill;
- `pypdf`, PyMuPDF, Pillow, ReportLab, Poppler and an existing MinerU runtime are
  discovered dependencies, not bundled assets.

The skill may link this review and `scenario_contract_architecture.md`. It must
not embed code, frozen hashes, commands with device-local paths, Candidate C
identities, or the 321-receipt history.

## P0-P2 remediation before preservation commit

### P0 — commit integrity

1. **Do not stage the current generic-named Viral executable surfaces.**
   `scenario_source_reconstruction.py` pins the old branch/HEAD and production
   authority; after the preservation commit, its public profile would reject
   the repository revision that contains it. Move/split it into the explicit
   Viral reference layer or mark the exact frozen profile historical and
   non-public before inclusion.
2. **Make the staged allowlist self-auditing.** The final staged set must be
   compared byte-for-byte with the allowlist below. No wildcard staging of
   `kb_creator/docs/plans`, `working`, `reports`, or the whole repository is
   permitted.
3. **Preserve frozen identities.** The publication config copy must be exactly
   713,722 bytes / `C16DFA...3B30`; Candidate C, its `INVENTORY.json`, source,
   accepted reconstruction v4 and current working config must show no change.

### P1 — portability and truthful naming

1. Move/rename or split the seven misleading generic surfaces:
   `build_mineru_visual_merge_bundle.py`,
   `finalize_mineru_reconstruction.py`, `scenario_contract.py`,
   `scenario_source_reconstruction.py`, `build_scenario_master_en.py`,
   `verify_scenario_master_en.py`, and
   `build_master_en_visual_qa_bundle.py`.
   A file may remain in shared scripts only when its scenario facts are passed
   through a closed reviewed contract/profile and a non-Viral fixture proves
   that path.
2. Split clean synthetic unit tests from live Viral integration tests. The
   current MASTER_EN builder/verifier tests bind ignored `working/viral`
   inputs at import/setup time; they cannot be part of a clean-checkout generic
   suite.
3. Admit `.agents/skills/**`, `kb_creator/contracts/**` and the chosen
   `kb_creator/reference/**` path through narrow `.gitignore` rules. Review and
   stage only the concurrent hunks that are still required; do not overwrite
   their owner.

### P2 — maintainability

1. Document dependency discovery and the Windows/Poppler/MinerU boundary in the
   skill; do not add machine paths.
2. Document that comparator/provenance paths are runtime locators and generated
   reports are not portable authority. A later schema revision may store paths
   relative to an explicit run root.
3. Prefer readable, formatted modules over the current dense one-line style in
   the 904-line builder and 320-line verifier when they are next materially
   changed. Formatting must be a separate reviewed change, not mixed into this
   preservation commit.
4. Keep the contract labeled CoC/Viral reference until at least one additional
   scenario proves any broader taxonomy/language/gate claims.

## Exact preservation commit boundary

### Allowlist for the first scoped preservation commit

The following paths, and no others, are recommended:

```text
.gitignore
.agents/skills/kb-creator-scenario-reconstruction/SKILL.md
kb_creator/contracts/innsmouth.json
kb_creator/contracts/scenario_contract.v1.schema.json
kb_creator/contracts/viral.json
kb_creator/reference/viral/master_en/publication_config_v1.json
kb_creator/reference/viral/README.md
kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md
kb_creator/docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md
kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md
kb_creator/scripts/audit_mineru_ai_merge_fidelity.py
kb_creator/scripts/compare_mineru_three_views.py
kb_creator/scripts/materialize_mineru_ai_merge.py
kb_creator/scripts/prepare_mineru_three_view_inputs.py
kb_creator/scripts/run_mineru_three_view.ps1
kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py
kb_creator/tests/test_materialize_mineru_ai_merge.py
kb_creator/tests/test_mineru_three_view_tools.py
```

`kb_creator/reference/viral/README.md` is limited to classification, frozen
config identity, upstream prerequisites and the explicit statement that the
reference is not a self-contained clean-checkout build. `.gitignore` is
included only for the exact narrow unignore rules required by these paths.

The Viral executable/reference layer is a **second commit after P0/P1**, with
its own exact moved/renamed file list and clean synthetic/reference test result.
It must not be silently added to the first allowlist.

### Explicit exclusions from this commit

```text
kb_creator/working/**
kb_creator/output/**
kb_creator/reports/**
kb_creator/**/*.pdf
kb_creator/**/*.PDF
kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md
kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md
kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/**
kb_creator/scripts/build_mineru_visual_merge_bundle.py
kb_creator/scripts/finalize_mineru_reconstruction.py
kb_creator/scripts/reconstruct_scenario_source.py
kb_creator/scripts/scenario_contract.py
kb_creator/scripts/scenario_source_reconstruction.py
kb_creator/scripts/build_scenario_master_en.py
kb_creator/scripts/verify_scenario_master_en.py
kb_creator/scripts/build_master_en_visual_qa_bundle.py
kb_creator/tests/test_mineru_visual_merge_bundle.py
kb_creator/tests/test_finalize_mineru_reconstruction.py
kb_creator/tests/test_scenario_contract.py
kb_creator/tests/test_scenario_source_reconstruction.py
kb_creator/tests/test_build_scenario_master_en.py
kb_creator/tests/test_verify_scenario_master_en.py
kb_creator/tests/test_build_master_en_visual_qa_bundle.py
**/*transcript*
**/__pycache__/**
**/.pytest_cache/**
**/*.pyc
```

Also exclude every unrelated current modification under `.codex/agents`,
`.codex/config.toml`, `AGENTS.md`, `CoC/AGENTS.md`, `Dune/AGENTS.md`,
`Sourcefold/AGENTS.md`, `CODEX_CONFIG_APPLIED.md`, `SETUP.md`,
`docs/governance/**` and `.gitattributes` unless the orchestrator authorizes a
separate configuration/governance commit. Do not stage deleted, ignored, or
foreign contributor files by directory wildcard.

## Acceptance criteria

Preservation implementation is accepted only when all of the following hold:

1. `git diff --cached --name-only` equals the first-commit allowlist exactly.
2. The tracked publication config copy has the exact frozen byte count/hash;
   the original working config and Candidate C identities are unchanged.
3. `git check-ignore -v` proves the skill, contracts and reference config are
   admitted by narrow rules, while the source PDF, working tree, candidates,
   overlays, bundles, reports, scratch and staging roots remain ignored or
   unstaged.
4. A clean/disposable checkout runs the three reusable test modules without
   `kb_creator/working/viral`, Candidate C or source PDF present.
5. Static scan of the five reusable scripts contains no `Viral`, `Innsmouth`,
   `124`, admitted source hash/path, frozen branch/HEAD or dated run root.
   Numeric algorithm parameters unrelated to scenario facts must be reviewed,
   not blindly rejected.
6. The skill contains routing and policy only; no Python/PowerShell code is
   duplicated.
7. The reference README states that `contracts/viral.json` and the frozen
   publication config are Viral-specific and that the latter is not a
   self-contained build input.
8. No test in the reusable suite reads a pre-existing ignored candidate or
   absolute device path.
9. No source, reconstruction package, candidate, generated reader, overlay,
   visual bundle, transported original, scratch/staging root, raw transcript or
   repetitive receipt is staged.
10. Independent implementation review finds no P0/P1 and confirms that this
    preservation commit makes no release/acceptance claim.

## Evidence checked

- applicable repository `AGENTS.md` and
  `docs/governance/nri_goal_governance.md`;
- assignment, current `plan.md`, `context.md`, scenario contract architecture,
  README, PROJECT_STATUS and pipeline summary;
- live Git status/diff/untracked/ignored inventories;
- `.gitignore` and `.gitattributes`, including the concurrent unignore diff;
- all 13 untracked Viral-era scripts and 10 matching tests;
- `contracts/viral.json`, schema and Innsmouth compatibility shadow;
- frozen publication config identity and locator scan;
- run-local directory inventory: 6,914 ignored files, source/reconstruction
  roots, rejected/frozen/scratch candidates and four stale test staging roots;
- handoff inventory: 321 files / 3,320,413 bytes.

No tests or build commands were run because this bounded architecture task had
a sole-write contract and test execution could create caches/staging output.
Existing accepted QA/review evidence was read as status evidence, not replayed
as a new release decision.

`READY_FOR_PRESERVATION_IMPLEMENTATION`
