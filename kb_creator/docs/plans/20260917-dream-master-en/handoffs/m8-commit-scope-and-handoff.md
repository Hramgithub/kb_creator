# M8 receipt: canonical close and future commit scope

## Result

- Goal: `20260917-dream-master-en`; milestone: M8.
- Result: **PASS**. The accepted reconstruction has been promoted, a frozen
  Stage 10 candidate has passed bounded QA and independent implementation
  review, and the pipeline is stopped at the explicit MASTER_EN acceptance
  gate.
- Independent verdict: `APPROVE_IMPLEMENTATION`; no blocking finding.
- No commit or push was performed.

## Reusable implementation closure

The reported defect classes are represented by shared, scenario-neutral code
and tests, not by edits under generated output:

- typed semantic containers and compact line groups:
  `pipeline/semantic_structure.py`, reconstruction/audit/materializer/replay
  integrations, schemas, the reviewed-decision author, and their tests;
- readable Windows materialization:
  `scripts/normalize_publication_access.py`, pipeline integrations, and tests;
- promotion of structural replays:
  `pipeline/reconstruction_promotion.py` and
  `tests/test_reconstruction_promotion.py`, including validated semantic
  sidecar carriage and span-bound handout-caption evidence;
- scenario authority: declarative JSON under
  `inputs/number-7-dream/publication/v1` and the contract produced by the
  generic `author_scenario_publication_contract.py`; no scenario-specific
  Python exists.

The KB Creator README, pipeline summary, NRI layout rules, project status, and
canonical goal plans describe the same boundaries. A literal scan found no
Number 7 Dream scenario/title literal in reusable Python outside `working/**`.

## Test evidence and known debt

- Focused promotion: `19 passed, 1 skipped, 2 deselected`.
- Semantic/replay focused suites: `30 passed`.
- Publication-authority suites: `79 passed, 1 skipped, 255 subtests passed`.
- Combined affected suite: `428 passed, 3 skipped, 2 failed, 255 subtests
  passed`.
- Both combined-suite failures are the historical Dissociation replay-10
  live-fixture tests in `test_reconstruction_promotion.py`; they fail closed at
  `implementation_drift: producer_closure_changed: 01-prepare-inputs` because
  the immutable fixture predates current producer code. Independent review
  classifies this as nonblocking P2 historical-fixture debt. Do not claim a
  clean full affected suite until that fixture is rebaselined or given an
  explicit quarantine policy.
- `git diff --check` passes.

## Future explicit commit boundary

Final pre-commit working-tree audit after this receipt records 24 modified
tracked files and 95 visible untracked files. A future explicitly authorized
commit must include the complete reviewed closure:

- shared pipeline/scripts, schemas, and tests for reconstruction semantics,
  line flow, ACL normalization, replay, and promotion;
- Dream reconstruction and publication contracts plus declarative inputs and
  19 content-addressed reader assets;
- NRI/KB Creator rules, README/pipeline summary/status, and all completed
  canonical plans/receipts for the Dream reconstruction, ACL, structural,
  line-flow, and MASTER_EN goals.

It must exclude every generated replay, promotion, Stage 10 candidate, and
other file below `kb_creator/working/**`; the repository ignore rule continues
to cover that tree. Before an actual commit, inventory the Git index again and
review the staged diff. Push remains a separate explicit action.

## User gate

Candidate:
`kb_creator/working/number-7-dream/publication/20260918-publication-01/outputs/10-master-en-candidate/artifacts/MASTER_EN.md`.
SHA-256:
`4C154262D4BED6688BAB8BB3809DC33A4991AEF5DBD6B90575C5726A78E59945`.
It is verified but not accepted. Translation and all later publication stages
remain closed until the user explicitly accepts this MASTER_EN candidate.
