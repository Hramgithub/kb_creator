# Viral Step 7 MASTER_EN builder phase A: preflight foundation

Date: 2026-09-01  
Owner: fresh bounded `gpt-5.6-terra` engineer at `medium`  
Working directory: `D:\NRI\.worktrees\kb-creator-viral`

## Scope

Replace the failed scaffold's configuration/preflight/inventory foundation only.
Do not attempt render, semantic assembly, candidate generation or final verifier
acceptance in this phase. A successful result is `PASS_FOUNDATION`, never a
conforming builder or authorization to build Viral.

Read the accepted architecture, original engineering assignment, both failed
engineering receipts, and the accepted production config/receipt completely.
Authoritative config:

`kb_creator/working/viral/master_en/publication_config_v1.json`

- 630,533 bytes;
- SHA-256 `9B915863B058EA0DF73203E63FD338394159E9922AF4B21D5168FBE2E82DBADE`;
- exact rows 168/124/237/41/29/123/91/9 as recorded in its receipt SHA-256
  `3AE6CA2930837D265BD7895078F9AB819F5CE4B6BB4253FB1276B37051A411E8`.

## Ownership

You are not alone. Do not revert other changes. You may modify only:

- `kb_creator/scripts/build_scenario_master_en.py`;
- `kb_creator/scripts/verify_scenario_master_en.py`;
- `kb_creator/tests/test_build_scenario_master_en.py`;
- `kb_creator/tests/test_verify_scenario_master_en.py`;
- new receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_builder_foundation_20260901.md`.

Everything else is read-only. Do not create any target, render, asset, config,
cache, dependency, root-checkout file or Git change. The old FAIL receipts are
immutable. Do not run the PDF marker.

## Required foundation

1. Replace fixture-only config parsing with exact closed production nested
   schemas for all 13 top-level keys and both allowed asset row variants. Validate
   types, required keys, enums, counts derived from document/config, uniqueness,
   ordering and referential closure. No `viral`/page-number behavior in code.

2. Resolve every repository-relative path from the discovered checkout root,
   require it remain inside the checkout, and require the CLI paths match pinned
   config paths. Reject absolute paths, parent traversal, symlink escape and the
   source/overlay as undeclared fallback.

3. Verify before target creation:

   - contract/source bytes and SHA;
   - accepted reconstruction root, file count/bytes and exact ordinal portable
     inventory algorithm `relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>`;
   - nested MD/QA/provenance/asset-manifest identities;
   - external repository-relative acceptance receipt identity;
   - each source page file/hash as required by source/structured rows;
   - all 121 accepted asset byte/hash/path identities;
   - reconstruction QA status/gates and no reconstruction blocker.

4. Validate semantic declarations without generating output:

   - hierarchy anchors unique ASCII scenario-prefixed, one H1, valid levels,
     parent closure and root anchor;
   - source pages exact first..last once, correct source paths, zero unauthorized
     suppression, every target/sub-unit/asset resolved;
   - xref IDs unique, classification/link-policy closure, all internal targets
     resolved, external rows targetless;
   - handout labels/ordinals/anchors/pages/assets/provenance/narrative closure and
     no contextual p82 fabrication;
   - structured unit IDs/owners/pages/source hashes/embedded accepted Markdown/
     fact-expectation schemas and zero editorial lexical delta;
   - 121 accepted plus declared render assets unique, reader/evidence ownership,
     accepted manifest closure, safe alt text and exact render declaration shape;
   - visual unit and reader-noise row closure;
   - authorial protection rows and three external gates required/pending/not
     assertable; acceptance file forbidden.

5. Provide a builder CLI `--preflight-only` path that accepts the original five
   required CLI arguments, performs all checks and emits deterministic JSON
   `status: preflight_passed` without creating `--target`. Without
   `--preflight-only`, fail closed with an explicit
   `implementation_phase_incomplete` before target creation. Keep the final CLI
   signature ready for later phases.

6. Implement the same preflight independently in verifier code without importing
   builder. It may share no builder functions/constants by import. It should
   expose a verifier `--preflight-only` mode before candidate work exists.

## Focused tests

Use exact production-shaped nested fixture rows, not the old flat fixture. One
or a few nodes per class, approximately 15-30 total:

- real production config read-only preflight passes in both scripts and creates
  no target;
- actual accepted package ordinal inventory/external receipt validation;
- closed top/nested schema unknown/missing/type/enums;
- path absolute/parent/symlink escape and CLI/config mismatch;
- contract/source/sidecar/source-page/asset/receipt hash or byte mismatch;
- package file-count/bytes/inventory mismatch;
- hierarchy/page/xref/handout/structured/asset/visual/noise closure failures;
- forged reconstruction/external gates, editorial delta, acceptance policy;
- actual-build mode refuses before target creation;
- verifier source does not import builder.

Use in-memory mutation of one compact production-shaped fixture rather than
hundreds of physical copies. Run only the two owned focused tests with
`python -B -m pytest -q -p no:cacheprovider`, `py_compile`, owned-file
`git diff --check`, plus one read-only real production preflight in each script.
No real build/render and no 371/119/490 suite.

## Receipt

Report exact file identities, collected/passed node count, production preflight
stdout/exits for builder and verifier, negative-class coverage, paths checked,
and blockers. Result wording must be `PASS_FOUNDATION`, `FAIL` or `BLOCKED`.
Explicitly state render/assembly/candidate verification remain unimplemented and
that no real candidate is authorized.

