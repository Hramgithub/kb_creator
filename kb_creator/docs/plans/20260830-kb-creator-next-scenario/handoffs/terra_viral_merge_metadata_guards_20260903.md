# Terra receipt — Viral merge metadata guards

- Goal id: `20260830-kb-creator-next-scenario`
- Step: bounded upstream repair `PROC-019` / `PROC-020`
- Role / requested effort: `nri-engineer` / Terra medium
- Orchestrator policy owner: root `gpt-5.6-sol` / medium
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-03` (Europe/Moscow)

## Scope and result

Implemented the assigned three-view metadata preservation and merge-materializer
guards. No reconstruction, raw comparison, candidate, v1, OCR/PDF, or Git data
was written.

The comparison adapter now preserves v1 `text_level` plus deterministic title
evidence from v2, middle, and Markdown. A v2/middle title is aligned only when
its exact text occurs once on the same source page; duplicate representations of
the same title/bbox are deduplicated. Markdown evidence requires an exact,
document-unique heading. Ambiguous repeated text remains non-title evidence.

`diff_blocks` now dereferences matches by `raw_index` rather than treating a
global raw index as a list offset. Image/heading overlap checks stay within the
same comparison side and source page.

The materializer now scopes unresolved comparison conflicts to the selected
view/block identities. It rejects an image block selected as body text and a
selected title that disappears from Markdown unless either its exact heading is
present or the reviewed notes contain the explicit line
`title override: <exact source title>`. It does not infer body prose from image
descriptions.

## Files changed

- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`

## Verification and evidence

```powershell
python -B -m pytest -q kb_creator/tests/test_mineru_three_view_tools.py kb_creator/tests/test_materialize_mineru_ai_merge.py
```

Result: `45 passed in 2.85s`.

Read-only actual-raw verification through `inspect_view` against
`20260901_step6a_mineru_three_view_full/runs/original_hybrid` reported:

- p25 `Santina Maria Salvatore`: `text_level=2`, `v2_title=true`,
  `middle_title=true`, `markdown_heading=true`;
- p25 `Padre Angelo`: same evidence;
- p39 `Hospital, Cellar`: same evidence.

`git diff --check` passed for the four owned code/test paths.

## Remaining limits, blockers, and next action

No implementation blocker. This prevents future silent metadata loss and
selected-block downgrades; it does not repair the immutable current Viral v4 or
claim `MASTER_EN` is fixed. Repeated same-page title text, non-exact OCR title
variants, and a title intended as a non-heading structure require an explicit
reviewed override rather than guessed alignment or representation.

Next action: root integrates the safeguards with the separate publication-author
work and performs the independently owned candidate/build verification.

- Elapsed time: approximately 24 minutes.
- Token use: unavailable.
