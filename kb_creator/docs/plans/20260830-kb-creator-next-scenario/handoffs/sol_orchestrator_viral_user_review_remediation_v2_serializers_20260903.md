# Viral remediation v2 structured serializers continuation

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-structured-serializers`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Prior receipt: `terra_engineering_viral_user_review_remediation_v2_materializer_20260903.md`
- Completion token: `READY_FOR_V2_ASSET_CLOSURE`

## Objective

Replace opaque v2 `structured_unit` strings with typed, validated serializers
and strict termination/shape tests. Do not work on asset binary placement or the
independent verifier in this continuation.

You are not alone in the worktree. Preserve all prior changes and edit only the
three exclusive paths below.

## Exclusive ownership

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_serializers_20260903.md`

## Required behavior

Implement construct-specific v2 validation and canonical Markdown emission for:

- `table`: explicit header/cell matrix, exact declared row/cell counts, escaped
  pipes, one header and one delimiter, no orphan rows;
- `callout`: bounded blockquote body and return to parent stream;
- `ordered_list_callout`: one bounded blockquote with exact ordered items;
- `equipment_card`: internal title/stat/footnote/body membership and exact end;
- `creature_statblock`: internal title/subtitle, compact stats, attacks,
  abilities and nested tables with exact boundaries;
- `inline_run_in`: technical anchor plus label/xref in one paragraph, never
  outline;
- `full_page_map`: ordered page membership plus accessible key/legend/scale;
- `physical_page_pair`: ordered front/back facsimiles and separate accessible
  back semantics.

Containers must be data-driven, not Viral-title hard-coded. Event `contains[]`
must exactly match emitted child identities, reject missing/extra children and
prevent following parent prose from being absorbed. Preserve canonical LF and
the existing atomic candidate route.

Add focused success and mutation tests for row/cell mismatch, duplicate table
header, missing/extra child, early/late card end, outline leakage and closure of
content following every bounded construct. Retain all old/v1 tests.

## Forbidden

No verifier/config/evidence/source/reconstruction/candidate edits, real builds,
asset copying/Step 8A, Git operations, cleanup, deletion or unrelated files.

## Evidence

Run the builder test module and `py_compile`, then write the exact immutable
receipt. Return `READY_FOR_V2_ASSET_CLOSURE` only when all eight serializers and
their failure modes are implemented; otherwise identify the remaining
serializer-only gap.
