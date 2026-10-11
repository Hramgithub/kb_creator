# Terra engineering receipt — Viral v2 Phase B1b source graph

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `7-v2-complete-publication-authoring / B1b-source-graph`.
- Contributor role: `nri-engineer` / GPT-5.6-terra / medium.
- Orchestrator policy owner: main chat, `gpt-5.6-sol` / medium.
- Assignment state: `partial`; B1b graph materialization is complete and B1c serialization remains fail-closed.
- Scoped override: changed only the author helper, focused author tests, and this receipt. Canonical config, candidates, builder/verifier, other tests, inputs, scratch, Git, downstream and production remain forbidden.
- Timestamp: `2026-09-03T00:00:00+03:00` (Europe/Moscow; session time).
- Elapsed time: approximately 35 minutes.
- Token use: unavailable.

## Scope and result

Implemented a deterministic real-input B1b source graph. It reads all three hash-bound approved ledgers, supports their two approved schema identifiers, and partitions pages 001--122 at every reviewed boundary. Every non-overlay interval is retained as ordinary `text_fragment` evidence with exact raw-byte and decoded-character slices.

The graph has 122 audited pages, 410 contiguous nonzero raw spans totaling 346,793 bytes, 186 ledger units, monotonic retained/overlay events, a 168-row frozen-v1 hierarchy projection without p123/124 coordinates, typed-unit inventory for every required family, and sealed recoveries for `Cursed Plague Zombies` and `New Mythos Tome`.

`author_to()` remains no-output and now fails at `E_V2_AUTHOR_ASSET_XREF_MATERIALIZATION_REQUIRED`; the graph is not represented as a full v2 config.

Terminal state: `PARTIAL_V2_COMPLETE_AUTHORING_PHASE_B1B`.

## Files checked or changed

- Changed: `kb_creator/scripts/author_viral_master_en_v2_config.py`.
- Changed: `kb_creator/tests/test_author_viral_master_en_v2_config.py`.
- Added: this receipt.
- Checked read-only: B1/B1b/parent packets, B1 receipt, architecture, A3 approval, frozen v1, reconstruction, all approved ledgers and A3 schema validators.
- Pre-edit bound hashes matched: B1 receipt `23611C725DA8D3CC2ADD3199B42DE0D0E0942014D1CC65B7DE8C57649E213A9D`; helper `C96EFC5787ECFD3EE72D7F007F1B05591F5991D3BAB35719AF30CBFB030992F3`; tests `8CA23E77954698AE7186DE9D5B5D4EDA96B4D0A533A58782B10E5350A5F08F83`.

## Verification and evidence

```text
python -m unittest kb_creator.tests.test_author_viral_master_en_v2_config -q
Ran 7 tests in 1.639s — OK

python -m py_compile kb_creator/scripts/author_viral_master_en_v2_config.py kb_creator/tests/test_author_viral_master_en_v2_config.py
exit 0

git diff --check -- kb_creator/scripts/author_viral_master_en_v2_config.py kb_creator/tests/test_author_viral_master_en_v2_config.py
exit 0

Test-Path kb_creator/working/viral/master_en/publication_config_v2.json
False
```

Focused tests cover deterministic graph bytes, raw-byte conservation and contiguity, retained ordinary prose, hierarchy/title/parent closure, p123/124 exclusion, typed-family inventory, sealed recoveries, migration baseline, atomic absent-only output behavior and the explicit no-output seam.

## Blockers and next action

No source-identity or ledger-boundary blocker remains within B1b. B1c must construct closed A3 typed payload schemas and bindings from this graph, materialize asset ownership/placements and xref targets, and only then serialize a config. Do not weaken the fail-closed seam or create the canonical config first.
