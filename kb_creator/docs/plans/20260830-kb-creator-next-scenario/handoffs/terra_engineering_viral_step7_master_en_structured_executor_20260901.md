# Viral Step 7 MASTER_EN structured executor — engineering handoff

- Timestamp: `2026-09-01T22:01:30+03:00` (`Europe/Moscow`)
- Role: reusable code/test engineering, `gpt-5.6-terra` / `medium`
- Orchestrator policy owner: parent `/root`; ownership was not transferred.
- Assignment state: `PASS_STRUCTURED_EXECUTOR`; this is bounded implementation evidence, not a C2a/C2b or release decision.
- Scoped override: writes were limited to the builder, its focused test file, and this receipt. Config, accepted source/package, verifier, candidate, canonical plan/context/status, MinerU, historical matrices, Git, and release surfaces remained read-only.

## Scope and result

Implemented the remaining config-driven structured executor evidence path in `build_scenario_master_en.py`.

1. `fragment_emission_plan` retains the accepted root/child/root interleave: every declared source fragment is planned exactly once, and a direct descendant is interleaved only when all of its exact source spans lie strictly between consecutive parent spans. This preserves unrelated binding order.
2. Assembly now records an actual emitted-fragment ledger from final block offsets. Every entry carries the binding owner, source page/start/end, exact emitted character start/end, and the final emitted text.
3. `structured_resolver` derives each nonvisual region's `emitted_start`, `emitted_end`, and `emitted_sha256` from final reader text. It fails closed if the configured source region does not map to exactly one owner-local emitted fragment or if the expected transformed region is missing/ambiguous. The former source-body hash placeholder was removed.
4. Exact source-xref rewriting is shared by assembly and emitted-region resolution, so a legitimate configured link rewrite does not break source-to-reader correspondence.
5. Visual forms now require the staged asset SHA to equal the config asset SHA, both configured review IDs to exist with their closed pending external-QA status, and exactly one asset Markdown occurrence inside the exact `owner_anchor` block (anchor to next anchor), with zero occurrences in every other owner block.

No Viral-specific text, record numbers, or anchors were added to reusable builder logic. No semantic structure is regenerated or duplicated.

## Files changed

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- this receipt

Read-only input identity:

- `publication_config_v1.json`: `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`.

Builder/test identities before this final emitted-evidence pass:

- builder: `7924B1F7B39A434E353DE214E909983AE72B577347C33EEDC58F72AD839438E0`;
- tests: `7DBA16A0B5D1DE7F030BFACE5CD998BA678D3FAD8BBF5DCF7BC72D751396C9FC`.

Final identities:

- builder: `72579A69C8F52428808092AFDF8532B9504C468A9A2C4571AEA6D29EADA37672`;
- tests: `4C721410827EFB1E8CCA722D76E3A3F9911FEFF273BE3AFE8D221E1E53EA5F3F`.

## Verification and evidence

Focused command:

```text
python -B -m pytest -q -p no:cacheprovider kb_creator\tests\test_build_scenario_master_en.py
36 passed in 7.65s
```

The added compact tests cover actual emitted ranges/hashes for all 23 nonvisual rows; missing emitted ledger, owner crossing, and changed emitted fragment failures; visual wrong-owner, duplicate, and staged-SHA failures; and the existing generic plus real Outdoor root/child/root consumption/order checks.

Two fresh `TemporaryDirectory` reader builds from the same pinned inputs were byte-identical:

```text
358622 bytes
SHA-256 17528F1543738CA5FAE1A215237B6F7476A9483B015D1C41889213DFA140B010
```

Derived topology and retained invariants:

- `168` anchors; `256` emitted source fragments; `29` structured evidence rows;
- class split: `11` semantic tables / `10` semantic cards / `2` statblocks / `6` visual forms;
- `107` reader assets, with all six configured visual forms emitted exactly once in their owner blocks;
- `237` reader links, `237` executed xref IDs, `41` source-link segments;
- source conservation: `1935` total / `1862` owned / `73` generated / `0` unowned / `0` duplicate / `0` unauthorized suppression.

Representative actual nonvisual evidence is p20 Rumors: source `[2947,5061)` SHA `0E9F7533767E49C87D20E57209DB752ABEF2DD36B30F6D8AB9E22074B0BB1C49`, final reader range `[71175,73278)` SHA `4436E20E24F9909243133C0079F06E9C46CC64F665CBA31DE8123868BDF708F1`.

`git diff --check` reported no whitespace errors for the two implementation files. No candidate/output, MinerU operation, verifier edit, or historical `371/490` matrix was run.

## Blockers and next action

No blocker remains inside the assigned files. The orchestrator should independently inspect the actual temporary reader/evidence and obtain the required independent critic implementation review before authorizing candidate work or any acceptance decision.

Elapsed time: approximately 30 minutes across the original fragment emission and final emitted-evidence passes.

Token use: unavailable.
