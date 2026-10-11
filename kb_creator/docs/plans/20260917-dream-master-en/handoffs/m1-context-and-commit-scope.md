# M1 context and future commit-scope audit

- Goal / step: `20260917-dream-master-en` / `M1`
- Role: orchestrator
- Policy owner / effort: `gpt-5.6-sol`, medium; platform assignment unavailable
- Assignment state: `platform-unverified`; scoped override: none
- Timestamp: `2026-09-17T23:43:00+03:00`
- Token use: accounted by the parent goal; per-step split unavailable
- Result: PASS

## Live context read

Re-read the repository `AGENTS.md`, NRI goal governance, KB Creator README,
PROJECT_STATUS, completed Dream reconstruction/structural/line-flow plans and
contexts, the reconstruction scenario contract, the scenario reconstruction
skill, publication/reuse architecture, current CLI surfaces, and the latest 12
KB Creator commits. `main` is at `8a81ada0`, one commit ahead of `origin/main`;
no commit or push was performed.

The reconstruction skill explicitly ends at Stage 06. The live generic next
route is `reconstruction-promotion materialize`, then
`reconstruction-promotion record-acceptance`, then a publication preflight and
fresh Stage 10 run. `MASTER_EN` cannot repair reconstruction and remains a
separate acceptance gate.

## Git classification

Current working-tree inventory before this goal's publication inputs:

- 22 tracked modified files;
- 54 untracked but not ignored files;
- 9 untracked reusable code/contract/test files;
- 45 untracked canonical plan/evidence files.

All reusable Dream/ACL/semantic changes are either already tracked-modified or
untracked-but-not-ignored. Representative checks return `check-ignore` exit 1
for:

- `kb_creator/pipeline/semantic_structure.py`;
- `kb_creator/scripts/author_reviewed_semantic_decisions.py`;
- `kb_creator/tests/test_semantic_structure.py`;
- `kb_creator/contracts/number-7-dream.reconstruction.json`;
- this goal's canonical plan.

The exact generated Stage 06 candidate returns `check-ignore` exit 0 under the
repository-wide generated-output rule, as intended. No Python file exists
anywhere below `kb_creator/working/number-7-dream`, so reusable implementation
has not been hidden inside generated evidence. A literal scan found no Number
7 Dream title, character, or page-specific vocabulary in reusable pipeline,
script, or test Python.

## Later commit boundary

A later explicit commit must include the reusable/canonical closure as one
reviewed scope:

- shared reconstruction/replay/audit/materializer/ACL/semantic modules;
- their tests and schemas;
- the Dream reconstruction contract;
- NRI layout rule, KB Creator README/pipeline summary/status;
- completed Dream reconstruction, ACL, structural, line-flow, and this
  promotion goal's plans/receipts;
- declarative Dream publication blueprint/config/contract inputs created by
  M4.

It must exclude all `kb_creator/working/**` replay, promotion, publication, and
rendered candidate trees. Because those ignored artifacts carry immutable
execution evidence, the canonical receipts must record their identities and
commands before commit. Git index contents must be inventoried again before
any future commit. Push remains separately gated.

## Blockers / next action

None. Materialize the exact replay-16 promotion package and validate it before
recording the user's acceptance.
