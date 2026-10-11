# Task packet: Viral MASTER_EN v2 policy authoring

## Owner and role

- Owner: one fresh `nri-engineer` contributor (`gpt-5.6-terra`, medium).
- Orchestrator: main chat (`gpt-5.6-sol`, medium).
- This contributor owns only the paths named below and must not orchestrate,
  execute a candidate build, stage, commit, push, or modify immutable inputs.

## Goal

Author the real Viral `publication_config_v2.json` from the accepted v4
reconstruction, the committed user-review defect registry, the accepted
architecture specification, and the frozen semantic-audit evidence. Run only
config/builder/verifier preflight checks. Do not build Candidate D or either
scratch candidate.

## Read first

1. `USER_REVIEW_TYPICAL_PROBLEMS_20260902.md`
2. `sol_architect_viral_user_review_remediation_spec_20260902.md`
3. `terra_engineering_viral_user_review_remediation_semantic_audit_20260903.md`
4. `working/viral/master_en/review_evidence/20260902_user_review_remediation_v1/`
5. frozen v1 config and the current builder/verifier v2 schemas and tests
6. accepted reconstruction pages under
   `source_reconstruction/20260901_step6a_reconstructed_en_package_v4/`

The semantic audit is candidate-first evidence, not direct config. Coalesce
individual physical rows into logical structures and reject broad lexical false
positives by checking accepted source lines and the defect registry.

## Owned paths

- `kb_creator/working/viral/master_en/publication_config_v2.json`
- If and only if a reusable config-authoring helper is essential:
  `kb_creator/scripts/author_viral_master_en_v2_config.py`
- If such a helper is added, its tests only:
  `kb_creator/tests/test_author_viral_master_en_v2_config.py`
- Receipt only:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_config_authoring_20260903.md`

No other path may be changed. You are not alone in the codebase: preserve all
other edits and do not revert or normalize unrelated files.

## Immutable and forbidden

- Source PDF.
- Accepted reconstruction v4.
- Candidate C and retained scratch candidates.
- Frozen working/reference v1 configs (expected SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`).
- Builder, verifier, visual-QA scripts and their existing tests.
- Candidate D and scratch output roots: do not create them.
- MASTER_RU, Step 8A, HTML, PDF, production, Git staging/commit/push.

## Required policy result

- Bind exact source PDF/reconstruction/evidence identities.
- Preserve global source order and full source-title fidelity.
- Restore all user-reported heading, ownership, and run-in cases, including
  Welcome to Perla, Santina Maria Salvatore, Hospital/Cellar/Ground Floor,
  DSS Incendiary Grenades (12), New Mythos Horrors, and New Spell.
- Represent repeated Appearance, Keeper's Notes, Possible Vision from The Sight,
  the page-68 advice block, and related insert families as bounded structures,
  without swallowing following ordinary section prose.
- Restore all reported tables as logical multirow tables, including Rumors,
  Signs and Portents, Outdoor Encounters, D10 tables, Infection tables, and
  continued tables across columns/pages.
- Restore the stream schedule as an ordered structure.
- Restore The Devourer and The Reliquae as consistent creature statblocks/cards.
- Resolve Plots and Schemes/Prologue art ownership semantically.
- Restore reported grouped hospital room references and inline/run-in labels.
- Provide the source-backed `Cursed Plague Zombies` recovery required by the
  architecture spec.
- Model the Ground Floor & Basement map as a full-page handout plus translatable
  Key; model pages 111--122 as six physical two-page pregen pairs with complete
  provisional full-page assets and translatable reverse-side text. Do not make
  final binary art choices (Step 8A is later).
- Keep all 124 pages in audit disposition, exactly 122 reader pages, and exclude
  pages 123--124 as advertising with no text/event/asset leakage.
- Keep OUT-008 and ENH-001 as explicit nonblocking deferrals.
- Declare dynamic visual review units covering all emitted heading/structure/
  asset kinds required by the current v2 contract.

## Verification and receipt

- Validate JSON and both builder/verifier v2 preflight routes without creating a
  candidate root.
- Run only focused config-authoring tests if a helper is introduced.
- Prove v1 working/reference SHA-256 values unchanged.
- Record commands, exact counts, identities, unresolved items, and changed files
  in the receipt.
- Success token: `READY_FOR_VIRAL_V2_IMPLEMENTATION_REVIEW`.
- If any source-backed boundary or required recovery cannot be proven, stop with
  `BLOCKED_VIRAL_V2_CONFIG_AUTHORING` and list exact page/line evidence; do not
  guess or weaken the contract.
