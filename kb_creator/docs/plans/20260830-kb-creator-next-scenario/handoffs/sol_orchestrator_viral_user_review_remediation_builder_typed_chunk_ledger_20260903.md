# Viral v2 builder typed-chunk emission ledger

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-builder-typed-chunk-ledger`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Prior receipt: `terra_engineering_viral_user_review_remediation_builder_event_provenance_20260903.md`
- Completion token: `READY_TO_RESUME_V2_VERIFIER_SEMANTIC_GATES`

## Objective and ownership

Implement the final event ledger by composing `MASTER_EN` from typed chunk
objects. Do not infer offsets by searching finished Markdown.

Owned paths:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_builder_typed_chunk_ledger_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required implementation algorithm

1. Refactor the v2 serializer to produce an ordered list of typed chunk objects,
   one per declared event, carrying event id/type/page/order/anchor/fragment,
   representation, canonical declared-content hash, optional structured
   `contains`, rendered text and emitted/suppressed state.
2. Represent each reader asset marker as its own chunk. Remove its original
   asset placeholder by event id and relocate the chunk by list operations:
   insert before/after the distinct target chunk; for `inside_structured_unit`,
   attach a child chunk at the declared structured container boundary while
   preserving the target's own base rendered slice.
3. Join emitted top-level chunks exactly once with `\n\n` and terminal `\n`.
   While joining, accumulate exact character and UTF-8 byte offsets from chunk
   lengths. Nested inside chunks receive their own exact offsets in the final
   combined structured chunk.
4. Emit provenance from this ledger only. Every reader-emitted event has exact
   final start/end char+byte and slice SHA-256. Suppressed asset events have an
   explicit non-emitted disposition and no fake range. Structured rows include
   exact ordered `contains`; all other rows omit it.
5. Fail closed for duplicate event ids, ambiguous/multiple placement, nested
   range overlap inconsistent with declared parent, or any final slice/hash
   mismatch. Output remains deterministic and root/time independent.

## Tests

Add focused tests for:

- plain and repeated-looking text events with monotonic unique ledger ranges;
- table/callout rendered range and `contains`;
- reader assets before, after and inside with relocated marker ranges;
- suppressed asset non-emission row;
- recomputed character/UTF-8 byte offsets and SHA-256 for every emitted row;
- two-root provenance byte equality;
- existing canonical blank-run and literal-content preservation.

Run full builder tests and `py_compile`. Write the exact receipt and return the
token only when the final ledger closes.

No verifier/config/evidence/source/real candidate/Git/Step 8A changes.
