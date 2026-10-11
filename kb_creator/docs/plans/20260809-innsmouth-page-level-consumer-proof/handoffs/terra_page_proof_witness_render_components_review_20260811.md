# Immutable Independent Implementation Review Receipt — Packet 4b.4

- Goal id: `20260809-innsmouth-page-level-consumer-proof`
- Step id: `4b.4-review`
- Review kind: `implementation`; this is not a release review or freeze attestation.
- Candidate state: non-frozen, fixture-only Packet 4b.4 witness/render/component candidate.
- Role: Terra independent critic; requested effort `high`.
- Actual model/effort: `platform-unverified`.
- Implemented or materially designed candidate: **no**. This critic performed neither.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`); orchestration ownership remains with the main-chat orchestrator.
- Assignment state: `platform-unverified`.
- Scoped override: none.
- Scope: independent review of Packet 4b.4 only. No candidate implementation/test/plan/context/status/contract/artifact/Git mutation; no web/network/browser, live Innsmouth source, EN/Keeper, HTML/PDF, configuration, output, parser, OCR, or source-reconstruction access.

## Verdict

**Rejected — P1 remediation required.**

The positive witness/render leaves are literal `bytes` with separately written literal metadata, the production module remains pure/local, and public coverage-first no-output behavior is preserved. However, Packet 4b.4 does not meet its exact rational/canonical-decimal or fail-closed raw-PNG requirements. The passing suite does not exercise these holes.

## Files checked

- `AGENTS.md` and `docs/governance/nri_goal_governance.md`.
- Packet authority, section 5 / row 4b.4: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_proof_implementation_packetization_20260809.md`.
- Executor receipt and process disclosure: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/executor_page_proof_witness_render_components_20260811.md` — SHA-256 `33422C472B1428A0A8D0584EFBC971816B5FAECE127F3E8AD277F94B2EB01F47`.
- Prior 4b.3 independent review: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_proof_closed_schemas_review_20260811.md`.
- Candidate and fixture-only tests:
  - `kb_creator/pdf_raw/page_proof.py` — SHA-256 `B61263DE80C597E96F8ECF229F0FFE48B6BA9DD05E4FB22792DE65F77058FB55`.
  - `kb_creator/tests/_page_proof_fixture_leaves.py` — SHA-256 `9B839FD9FF9E3FCAB3F1A44CA488BC2A5DEA49995B588D358C279DFF2837BFE7`.
  - `kb_creator/tests/test_page_proof_witness_render_components.py` — SHA-256 `CF17DD6FA1E6E33CA074A637FAEE84C063E0A591F23BB1C53B852A561455BA91`.
  - `kb_creator/tests/test_page_proof_coverage_guard.py` — SHA-256 `CB2705B83C1C86FB8BCE4B5909206B53571410658FF302926AB115FF34CA03B9`.
  - `kb_creator/tests/test_page_proof_stage_a_topology_inventory.py` — SHA-256 `95835BA6123EAB7AFCD4F1BE0C1396E89BE33C2A6C09133EB3C94928A8FF9C94`.
  - `kb_creator/tests/test_page_proof_fixture_admission.py` — SHA-256 `93131CC97228A587D1F6964E19594B6E3D373BFBC7287685D49989F1FB0EF76D`.
  - `kb_creator/tests/test_page_proof_closed_schemas.py` — SHA-256 `34A92E5CBB82B0EE26E02C950E0393FFE0D30B16C797E52B77120763D8894B2C`.

## Test evidence

The only test suite run was the mandated fixture-only command:

```powershell
& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_page_proof_coverage_guard.py kb_creator/tests/test_page_proof_stage_a_topology_inventory.py kb_creator/tests/test_page_proof_fixture_admission.py kb_creator/tests/test_page_proof_closed_schemas.py kb_creator/tests/test_page_proof_witness_render_components.py
```

Result: `55 passed in 0.16s`.

Passing tests are regression evidence only; they do not invalidate the P1 findings below.

## Evidence and findings

### P0

None.

### P1

- **Canonical fractional decimals are not implemented.** `page_proof.py` declares `_DECIMAL = re.compile(r"-?(0|[1-9][0-9]*)(\\.[0-9]+)?")`. In a raw regex this double backslash matches a literal backslash before an arbitrary character, rather than the decimal point. Consequently canonical fractional values required by the rational affine contract (for example `"0.5"` and `"-1.25"`) are rejected; only integral coefficients used by the three positives are covered. `test_affine_decimal_and_bbox_target_only_failures_repair_positive` proves that noncanonical `"1.0"` fails but supplies no valid fractional affine positive. Correct the pattern to match a literal dot, add at least one valid fractional-affine fixture/replay assertion plus target-only canonical/noncanonical cases, and preserve exact no-float arithmetic.

- **The raw PNG/zlib boundary is not closed after a valid terminal.** `_decode_png_rgba8()` sets `seen_iend=True` and breaks on `IEND` without requiring the parse offset to equal `len(raw)`, so bytes after `IEND` are silently accepted. `_inflate_zlib_uncompressed()` similarly reaches the final stored block but does not require its `offset` to consume the zlib payload before the Adler-32 trailer (and does not reject non-zero stored-block alignment padding). These are malformed, fully re-sealable byte streams that should fail the stated closed raw PNG decoder. The current tests cover signature, chunk-name, filter, and dimensions, but no trailing-after-IEND, trailing-zlib-payload, or stored-block-padding negative/repair cases. Require exact stream exhaustion and zero padding as applicable, then add targeted negative/repair coverage.

### P2

- **Process deviation, recorded; not the rejection basis.** The executor receipt discloses one attempted read of a non-existent local review-receipt path and local one-off Python computations used to derive/check literal fixture bytes before they were checked in. It also explicitly states that no web/network/browser/external research was used. The failed local path did not broaden to live material; the final helper contains literal bytes and separately written metadata with no imports or runtime generators. Record this as a P2 scope/process observation only. The P1 technical defects above independently require remediation.

## Additional confirmed properties

- `_page_proof_fixture_leaves.py` contains the three accepted PNG and witness leaves as literal byte constants with literal `RENDER_MECHANICS_V1_LENGTHS` and `RENDER_MECHANICS_V1_SHA256`; target-only derivatives are test-local JSON/bytearray helpers.
- Static containment in `page_proof.py` permits only `dataclasses`, `hashlib`, `json`, `re`, `RawPdfError`, and the exact `RawAtomProvenanceAuthorityV1` class import. There is no filesystem/environment/network/subprocess/dynamic-import/PIL/renderer/PDF/source-reconstruction/page-capable/Stage-A-constructor-or-replay dependency.
- The normalizer uses exact closed JSON objects, exact schema/key/type/enum/hash checks, RGBA8/non-interlaced IHDR constraints, chunk CRC checks, manual uncompressed-zlib/filter replay, canonical base64/RLE mask replay, 4-connected alpha components, exact component order/content, rational affine projection, geometry ordinal/row-id matching, and complete unique component ownership. It enforces one geometry row per supplied authority atom; targeted tests cover missing/malformed rows and ownership/order failures. The test helper should remain aware that it constructs its private authority atom list from the positive witness rows, so it is not independent positive Stage-A topology evidence.
- Production topology inventory and fixture-admission roots remain empty. `derive_fixture_page_block_ledger_v1`, `review_fixture_page_block_ledger_v1`, and `replay_fixture_page_block_ledger_v1` call `_require_complete_stage_a_fixture_coverage()` first and raise `page_proof_stage_a_fixture_coverage_incomplete` before touching caller values. No public proof-like object, ledger, text, wrapper, or terminal is returned.

## Blocker and next action

- Remediation blocker: close the decimal grammar and PNG/zlib terminal-consumption checks, add focused valid-fractional and malformed-tail/padding target-only tests, then request a new independent Packet 4b.4 remediation review. Do not start Packet 4b.5 from this rejected implementation evidence.
- Separate standing blocker: the independent `fixture_topology_acceptance` review-content hashes are absent, so production coverage/admission remains inactive and public proof routes remain unavailable.

## Timing and immutability

- Files changed: none. The only filesystem write by this review is this required immutable receipt.
- Elapsed active time: `108 seconds` at evidence capture.
- Token use: `41,153` reported by the platform runtime goal at evidence capture.
- Timestamp: `2026-08-11T12:41:05.8379999+03:00`.

This is an immutable point-in-time implementation-review receipt. It does not transfer orchestration ownership and is not a release decision, freeze attestation, or authorization to activate production coverage.
