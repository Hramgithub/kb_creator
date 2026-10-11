# Engineer receipt: reconstruction compact block boundary

Date: 2026-09-15  
Scope: generic decision-driven reconstruction formatting only  
Result: implemented; no live run was materialized or mutated

## Result

- Page decisions using `kb_creator.mineru_ai_page_decision.v1` may optionally declare `block_boundaries`.
- The only supported row is the closed object `{style, heading_line, first_body_line}` with `style: compact`.
- Materialization requires one exact ATX heading occurrence and exactly the sequence `heading_line`, one empty line, `first_body_line`. It removes only that empty separator. Missing, ambiguous, already-compact, multi-empty, malformed, duplicated, unsupported, or unknown declarations fail before publication of the output root.
- The original decision JSON is still copied byte-for-byte. Literal heading/body text, ordering, assets, and existing CommonMark hard breaks are unchanged.
- Legacy decisions retain their exact nine-key shape. Promotion accepts either that exact shape or the exact shape plus `block_boundaries`; every other page-decision key remains rejected.

For Dissociation page 006, the fresh decision should add:

```json
"block_boundaries": [
  {
    "style": "compact",
    "heading_line": "## HUMAN RESISTANCE (Police, Test Subjects, Residents of Aniak)",
    "first_body_line": "STR 50 CON 55 SIZ 50 INT 85 POW 60\u0020\u0020"
  }
]
```

Exact rendered Markdown delta:

```diff
 ## HUMAN RESISTANCE (Police, Test Subjects, Residents of Aniak)
-
 STR 50 CON 55 SIZ 50 INT 85 POW 60  
```

Read-only application of the implementation to the accepted run09 page-006 payload proved: one logical LF removed, old boundary count `1 -> 0`, compact boundary count `0 -> 1`, and the 10 hard breaks across the first 10 of 11 stat lines remain `10`. The equality check against the same Markdown with only that separator removed was true.

## Files and identities

- `kb_creator/scripts/materialize_mineru_ai_merge.py`: 43,215 bytes; SHA-256 `B0BEBB66CF1AA83E81429C4820EFC1B1AB5ADC144AB7B1201F4D3CF66A639E3F`
- `kb_creator/pipeline/reconstruction_promotion.py`: 91,604 bytes; SHA-256 `F10CF250B7FA92A652ECA4BF0D6E6DD620E191596368301C1DC71D3B5847811B`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`: 18,308 bytes; SHA-256 `5A852975BD4E9EFEB422C8BFE78DDC032AA58FBAA5A2612BD4EA8C8E7B78E35E`
- `kb_creator/tests/test_reconstruction_promotion.py`: 29,185 bytes; SHA-256 `F22E5ACB8776CAA80E248103799DC6C37F83065895D09EF0B23F793ADE0DC6FD`

Immutable/read-only reference identities after verification:

- run09 page-006 decision: 4,452 bytes; SHA-256 `C7199F23D8302229B66A2F1E17F0D266446C10D648EB2B1039ABBF8B70E08B26`
- run09 `RECONSTRUCTED_EN.md`: 21,048 bytes; SHA-256 `2C8983B83C770AC60AA32993B84228E64983B46010121A9DBA393BD3107C646D`
- publication-01 Stage10 `MASTER_EN.md`: 20,863 bytes; SHA-256 `2AD1E9175A3B53B7C85CCA5824B2FAA60D4A82C38928F487E6BB7700B5617CA6`

If all other content and newline conventions remain identical, the predicted corrected reconstruction Markdown is 21,046 bytes, SHA-256 `53B560862C3CC344C5C78676D988C3A4A479B5C0A0CBE4261B2E93080ED19993`; the predicted corrected Stage10 Markdown is 20,862 bytes, SHA-256 `571F96B077ACA59072C0399433E8372E997C9FC5D07428698D5580A2D5A1BED5`. These are pre-rebuild predictions, not replacement authority identities.

## Verification

- `py_compile` for both implementations and both test modules: pass.
- `pytest -q kb_creator/tests/test_materialize_mineru_ai_merge.py`: `43 passed`.
- focused materializer and promotion matrix: `10 passed, 53 deselected`.
- promotion legacy plus optional-extension happy paths: `3 passed, 17 deselected`.
- Full promotion file: `16 passed, 1 skipped, 3 failed`; all three failures are live-fixture drift outside this patch: run09 now has acceptance while two older tests require no acceptance, and run09 Stage05 correctly reports producer-closure drift after the materializer implementation changed. Self-contained legacy and extension cases pass.
- `git diff --check` on owned implementation/test paths: pass.

No MinerU, CPU, GPU, network, acceptance, live publication, commit, or push command was run.

## Recommended replay

At inspection time `20260915-cpu-replay-10` was absent. Re-check it immediately before use, then replay the immutable run07 Stage01-04 prefix into a fresh run10 root; author and identity-bind all six fresh decisions, adding only the declaration above to page 006; run the canonical v3 audit and replay resume for Stage05-06; verify the exact boundary/hard-break counts; materialize a fresh promotion package; then perform new explicit reconstruction and Stage10 acceptance through the existing gates. Do not reuse or mutate run09 or its accepted package.

## Findings

- P0/P1: none.
- P2: live-run-dependent promotion tests encode the earlier pre-acceptance/producer-closure state of run09 and are no longer stable regression fixtures. This does not block the fresh replay; future cleanup should replace those cases with immutable synthetic fixtures.
- Blockers: none.
