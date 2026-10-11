# Viral Step 7 MASTER_EN builder Phase B asset assignment

## Role and result boundary

- Owner: `gpt-5.6-terra` engineering, `medium`, accelerated service when exposed.
- Orchestration remains with `/root` (`gpt-5.6-sol`).
- Required result: implement and test the reusable deterministic asset layer for the MASTER_EN builder.
- This is not a candidate build, QA acceptance, release review, translation step, or Git action.

## Authoritative inputs

- Architecture: `sol_architect_viral_step7_master_en_publication_packet_20260901.md`.
- Production config: `kb_creator/working/viral/master_en/publication_config_v1.json`, 630533 bytes, SHA-256 `9B915863B058EA0DF73203E63FD338394159E9922AF4B21D5168FBE2E82DBADE`.
- Source PDF: `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`, SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Accepted reconstruction: `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`, inventory SHA-256 `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Phase A builder baseline: SHA-256 `43D338E4FC438F60FDD08B0FBCB16C73EDBD1D857FDE267048C1C426EDFCB9E0`.
- Phase A builder-test baseline: SHA-256 `F859314CB64AC81516832D75568F39FB6261C457E9A99E1839A481485F9D28C0`.
- Phase A receipt: SHA-256 `F0F8D626F8FEF6DEB3E15F20F67E2EFD1E9BFC13339BBF003C74AD476B31D5D1`.

## Write ownership

The contributor may edit only:

- `kb_creator/scripts/build_scenario_master_en.py`;
- `kb_creator/tests/test_build_scenario_master_en.py`;
- the new immutable receipt `handoffs/terra_engineering_viral_step7_master_en_builder_assets_20260901.md`.

All other code, tests, config, source, reconstruction, verifier, canonical plan/context, candidate/output roots, governance and Git state are read-only. Other work exists in this checkout; do not revert or absorb it.

## Required implementation

1. Preserve the accepted Phase A closed preflight behavior.
2. Add a reusable asset-materialization function used later by the full builder. It accepts an already validated config plus an explicit fresh staging root; it must not silently create or replace a real candidate.
3. Materialize the 121 accepted reconstruction assets byte-for-byte under content-addressed names `assets/<UPPER-or-lower-consistent-sha256>.<ext>`. Reject a source hash/size/type mismatch, basename/path escape, occupied output collision, undeclared output, or two declarations that violate the no-duplicate-binary invariant.
4. Render exactly the declared clean-source PDF pages 1 and 124 with `pdftoppm` 26.05.0 at 200 DPI from MediaBox. Never use `SELECTED_OVERLAY.pdf`. Select one page per invocation, then normalize with Pillow to upright RGB PNG, white background, no alpha, no embedded metadata, exactly 1700x2200. Use fixed PNG encoder settings so repeated runs in the pinned runtime are byte-identical.
5. Name each generated render by its computed content SHA-256 and return a deterministic manifest-ready record containing declared asset identity, output path, bytes, SHA-256, dimensions, media type, representation, owner, placement, source page/render declaration and pending visual-review status.
6. Return the complete 123-row asset ledger in config order. The asset layer must not write `MASTER_EN.md`, candidate sidecars, acceptance data or external-gate PASS claims.
7. Keep normal CLI build mode fail-closed with `implementation_phase_incomplete`; no real Viral target is authorized in Phase B.

## Focused verification

Use a compact representative suite, not selector-permutation expansion. Extend the current builder tests to cover the meaningful invariant classes:

- accepted asset byte identity and content-addressed output;
- clean-source page 1/page 124 render declarations and exact image properties;
- metadata/alpha stripping;
- deterministic two-run byte identity;
- wrong renderer/version, wrong source identity, occupied output/collision and overlay substitution refusal;
- 123-row ordering/ownership result and absence of candidate/acceptance/Markdown output;
- retained production preflight and fail-closed normal CLI behavior.

Target roughly 10-18 focused test nodes total. Do not recreate the historical 371/119/490 matrix. Synthetic temporary roots may be used and cleaned by their normal `TemporaryDirectory` lifecycle. A single real-source render probe may run only inside a fresh temporary root and must be reported separately; it is not a candidate.

Run at minimum:

```powershell
python -m py_compile kb_creator/scripts/build_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py
python -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_build_scenario_master_en.py
git diff --check -- kb_creator/scripts/build_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py
```

## Receipt

Write `terra_engineering_viral_step7_master_en_builder_assets_20260901.md` with `PASS_ASSET_LAYER`, `FAIL`, or `BLOCKED`; exact changed-file hashes; commands and results; test count; real-render evidence if executed; confirmed forbidden outputs absent; remaining Phase C work; elapsed time and token use if available. Do not claim candidate readiness.
