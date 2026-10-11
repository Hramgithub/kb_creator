# T5 interim Git and future commit-scope audit

## Result

The systemic changes are repository-visible rather than confined to the
ignored reconstruction run. No file is staged, no commit was created, and no
push was performed. The branch is `main...origin/main [ahead 1]`; the existing
tip `8a81ada0 Complete Dissociation release package materialization` predates
this goal and must not be described as a Number 7 Dream commit.

Current porcelain inventory contains 36 modified tracked files and 22
untracked path entries, with zero staged entries. This is a cumulative dirty
tree spanning the prior accepted Number 7 Dream goals as well as the active
goal, so a future commit must be assembled as one dependency-consistent series
and reviewed from the index. It is not safe to stage every dirty file blindly.

## Direct active-goal implementation closure

The direct reusable implementation and verification surfaces for
`20260918-dream-html-heading-toc` are:

- reconstruction semantics and enforcement:
  `kb_creator/pipeline/semantic_structure.py`,
  `kb_creator/pipeline/reconstruction.py`,
  `kb_creator/pipeline/reconstruction_promotion.py`,
  `kb_creator/pipeline/reconstruction_replay_resume.py`,
  `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`, and
  `kb_creator/scripts/author_reviewed_semantic_decisions.py`;
- schemas required by that implementation:
  `kb_creator/contracts/ai_merge_fidelity_audit.v4.schema.json`,
  `kb_creator/contracts/page_semantic_structure.v2.schema.json`, and
  `kb_creator/contracts/reconstruction_semantic_structure.v1.schema.json`;
- reconstruction regression coverage:
  `kb_creator/tests/test_semantic_structure.py` and
  `kb_creator/tests/test_author_reviewed_semantic_decisions.py`, together with
  the touched dependent audit/materialization/replay/promotion tests recorded
  by the combined affected-suite run;
- Stage-40 contract and projection:
  `kb_creator/pipeline/publication.py`,
  `kb_creator/pipeline/publication_adapters.py`, and
  `kb_creator/tests/test_publication_html_adapter.py`;
- renderer and renderer coverage:
  `translator/translator.py` and
  `translator/tests/test_recovery_support.py`;
- the live declarative Stage-40-ready policy:
  `kb_creator/inputs/number-7-dream/publication/v1/configs/html.json`;
- durable rules and documentation:
  `NRI_OCR_LAYOUT_RULES.md`, `kb_creator/README.md`,
  `kb_creator/PROJECT_STATUS.md`,
  `translator/docs/architecture/production_frontmatter_standard.md`, and the
  complete active-goal plan/receipt tree, including the reviewed T5 spec and
  QA/critic receipts.

These paths must not be committed as an isolated fragment if doing so would
omit their already-uncommitted schema, reconstruction, publication-contract,
or Number 7 Dream input dependencies. Prior commit-scope receipts under
`20260917-dream-master-en` and `20260918-dream-master-en-corrections` define
that cumulative dependency closure.

## Required exclusions

- Exclude all generated runs and candidates below `kb_creator/working/**`.
  `git check-ignore -v` confirms the exact replay-18 `RECONSTRUCTED_EN.md` is
  ignored by the repository-wide working-output rule.
- Exclude temporary logs, caches, browser data, OCR overlays, rendered
  intermediates, source-PDF copies, and any unrelated dirty files.
- Do not stage acceptance as data that has not occurred. Replay-18 remains an
  unaccepted reconstruction candidate.

## Verification and next boundary

- `git diff --check` passes.
- Candidate SHA-256 remains
  `4F37530D6655AE4786BB9A008E000510B0A32A638864B53663DEC1DD350337E5`.
- Before an explicitly authorized commit, repeat the porcelain inventory,
  stage only the dependency-consistent reviewed closure, inspect
  `git diff --cached --check` and `--stat`, and verify ignored/generated output
  is absent from the index.
- This receipt is interim: rebuild through MASTER_EN, MASTER_RU, ArtView, and
  Stage 40 may add further reusable or durable files after their explicit
  gates. The final commit manifest must therefore be refreshed after the fresh
  HTML candidate is verified.

