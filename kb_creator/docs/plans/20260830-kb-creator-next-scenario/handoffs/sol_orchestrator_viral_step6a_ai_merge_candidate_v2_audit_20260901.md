# Orchestrator audit — Viral Step 6A AI merge candidate v2

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-ai-merge-candidate-v2-audit`
- Date: `2026-09-01`
- Owner: main-chat orchestrator (`gpt-5.6-sol`, policy effort `medium`)
- Scope: read-only post-materialization audit of the fresh v2 candidate
- Result: `PASS — candidate ready for reconstruction QA`
- Acceptance boundary: this receipt does not accept `RECONSTRUCTED_EN`, start
  `MASTER_EN`, promote a package or authorize Git/release work.

## Bound inputs and execution

- materializer SHA-256:
  `D632FD2203C1CB68AD01DBD369E7FD530146A5D423F786FDEB64848F0F331076`;
- focused-test file SHA-256:
  `F6917CC80C129527BDE95B15C85562921B7F9064221E63ED4839634C6D537DC3`;
- three-view visual QA receipt SHA-256:
  `5985CF1CF5C0EDA79C79D740793B1F2FA1F639DCCA08BF9B0AA46323A83F6157`;
- AI decision receipts SHA-256:
  `2E2BEF1C64AE9CB7AAF992932530465DE344E3F33E56A9E944986A3A9F1E4E07`,
  `36E4E208454D832734933DBB74CDC073379A049D4F6BFEB7FCB3D135FEEF6112`,
  `16CE8D5A5C52076D752604AA501C62B9959A978A86750125FEFB42355A84E115`;
- range-A reader-visible image correction receipt SHA-256:
  `08FE6FD49C83FFB4D7A042E4ABB4735AFEFEC2A84D7AF2C29802B67CD7A29386`;
- v2 decision set: `124` files / `589051` bytes; SHA-256 of the
  ordered concatenated per-file SHA-256 hex values:
  `AA13DF843FAC3473144D69678056BB30B7FFFFE53185408841D5672C38F47232`;
- Luna packet SHA-256:
  `0C210FCA3BA82AEDAAAE5C07531AB28426116C260CB468DE2BBAE5507B4CD35D`;
- Luna execution receipt SHA-256:
  `9ED721EFDFDFA9CD249835F836D6078B8857F556C2BF76E6EF171170472F29EC`;
- native execution count: `1`; exit `0`; stdout reported
  `candidate_ready_for_reconstruction_qa`, `124` pages, `121` assets and
  `121` unique asset bytes; stderr was empty.

## Candidate identity

Root:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v2`

- files: `373`;
- bytes: `13141502`;
- inventory SHA-256:
  `76C4C8599B9321FFCF0983C548A7A2A94D8B3BC259D93E3EF2343CB58DB471B1`.

The inventory digest is SHA-256 over UTF-8 without BOM, ordinal
forward-slash-relative `path<TAB>bytes<TAB>SHA256<LF>` rows, including the final
LF.

Root artifact identities:

- `RECONSTRUCTED_EN.md`: `346247` bytes, SHA-256
  `321B1D10006C9FCA679813AA11B5EC24924E73BEB473E3DD6F4EA73897C54735`;
- `MERGE_PROVENANCE.json`: SHA-256
  `CCEF71DF54A866FB751678D8874823A3D9B84D612166BAE559960DEE2101239F`;
- `ASSET_MANIFEST.json`: SHA-256
  `914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9`;
- `OVERLAY_SELECTION.json`: SHA-256
  `B17EF5E777FDDA7E51BADCD3E939B8BFBEC67AFB35FF016FB6AB1B7F7C07353D`.

## Independent read-only checks

- exact file-domain closure: `373/373`, no missing, extra or reparse entries;
- page Markdown: `124/124`, exact page names and exactly one matching source
  marker per page; root marker sequence is exactly `1..124`;
- decision copies: `124/124` byte identities, zero mismatch against v2 input;
- provenance: schema and status valid, `124` pages, exact page domain,
  `0` unresolved pages, all decision/packet hashes valid, selected-block sets
  match their decisions;
- assets: manifest `121`, physical files `121`, all hashes valid, unique logical
  and stored paths, `119` non-reference plus `2` `reference_only`;
- reader Markdown: exact `119/119` non-reference image-link set with nonempty
  alt text; page-local `../assets/...` links and root `assets/...` links all
  resolve; placeholders remaining: `0`;
- overlay selection: `124/124`, exact source-page domain and every preference
  matches its decision;
- candidate and predecessor v1 remained separate; no MinerU, 371/119/490,
  downstream stage, cleanup, Git, commit or push occurred.

## Remaining reconstruction gate

The candidate is mechanically complete but not yet an accepted reconstruction.
The next read-only/content QA must close the contract's seven
`reconstructed_en` gates: source identity, page coverage, role partition,
text/OCR provenance, all `39` numbered player handouts, asset closure and no
open blockers. Any content correction must produce a successor decision set and
fresh candidate; direct edits to this candidate are forbidden.
