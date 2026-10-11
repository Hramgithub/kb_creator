# Task packet: Viral v2 complete publication authoring

## Role

- Owner: `nri-architect` (`gpt-5.6-sol`, high).
- Orchestrator: main chat (`gpt-5.6-sol`, medium).
- Analysis/specification only. Do not edit code, tests, config, evidence,
  immutable inputs, candidates or Git.

## Goal

Specify the exact fail-closed algorithm and test contract for authoring a
complete Viral `publication_config_v2.json`. The approved boundary ledgers are
reviewed overlays, not a complete reader source.

## Observed defects in the blocked helper

- Ledgers cover 1,905 line-slots of 4,860 lines on pages 1--122 (39.2%).
- No gap/ordinary `text_fragment` events are emitted.
- Frozen v1 config is not consumed, so its full hierarchy, asset policy,
  suppressions, xrefs and accepted placements are not migrated.
- All ledger `asset_ownership` units become `reader_value:false`; current v1 has
  123 assets and accepted reader assets that must not disappear.
- Equipment/statblock serializers invent placeholder text such as
  `Source-backed ...` / `See source-backed entry.` rather than preserving exact
  source text.

## Inputs

- Frozen v1 config (SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`).
- Accepted immutable reconstruction v4, pages 1--124 and assets.
- Three approved ledgers (hashes recorded in plan/context) and independent
  approval receipt SHA-256
  `4992A0CC7BA402F999177988241A3D679A7E7B437AD1F9FD8AB0663783547FE3`.
- Candidate-first 429-row decisions and user-review registry.
- Current v2 builder/verifier schemas and tests.
- Original architecture receipt
  `sol_architect_viral_user_review_remediation_spec_20260902.md`.

## Required decisions

1. Canonical 100% partition of reader pages 1--122 into exact source spans:
   reviewed structured replacements, retained ordinary text/heading spans,
   explicit asset spans, generated navigation replacement and declared
   suppressions/recovery. Define treatment of blank lines without weakening
   lexical completeness.
2. Exact non-overlap/no-gap/no-duplicate invariants, source hash identities,
   monotonic ordering and provenance required in config and output.
3. Migration of all v1 hierarchy, reader/evidence asset policies, relative
   placements, xrefs and source dispositions into v2, including how reviewed
   ledger decisions override v1 while untouched content remains unchanged.
4. Exact source-preserving typed payloads for callouts, tables, equipment cards,
   creature statblocks, full-page map and pregen pairs. No placeholders or
   editorial invention.
5. Required builder/verifier/config-author tests and metrics proving ordinary
   prose, headings, all required assets and pages 1--122 survive while pages
   123--124 and rejected/evidence-only assets do not leak.
6. Minimal allowed implementation paths and sequencing after the separate
   reconstruction identity contract is green.

## Required negative tests

- one unclaimed nonblank source line;
- one duplicated/overlapping source span;
- reordered page/column event;
- structured payload not byte/lexically derived from its claimed spans;
- placeholder/invented payload;
- missing v1 reader asset, duplicate asset, wrong event placement or p123/p124
  asset leakage;
- heading lost/downgraded or inset label promoted to outline;
- wrong source recovery or unsealed title transformation;
- mutation of v1/reconstruction/ledgers.

## Output

Write only
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_v2_complete_publication_authoring_20260903.md`.
Include root cause, exact data/partition model, precedence rules, migration
algorithm, validation/test matrix, path ownership, sequencing and terminal token
`READY_FOR_V2_COMPLETE_PUBLICATION_AUTHORING_IMPLEMENTATION` or a precise blocker.
