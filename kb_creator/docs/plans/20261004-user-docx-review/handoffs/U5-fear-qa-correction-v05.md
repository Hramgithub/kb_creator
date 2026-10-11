# Immutable correction — U5 Fear visual QA hash label

- Goal/step: `20261004-user-docx-review`, correction to the U5 Fear visual QA v04 receipt.
- Timestamp: `2026-10-04T21:47:14Z`.
- Bounded QA role: `gpt-6-luna / medium`; actual runtime unverified. Orchestrator policy owner: `gpt-6-sol / medium`; scoped override: none.
- Assignment state: correction complete; orchestration and acceptance remain with `/root`.
- Elapsed time: unavailable. Token use: unavailable.

The v04 receipt's hash labeled `review_index.json` is incorrect. Fresh SHA-256 checks show `review_index.json` is `686FE24C9C5D398B0472A56689AC9946A570CA7EADF22D30FC86DC594C540430`; `render_inventory.json` is `F762E478AEDA0C7F4AB9A3BE768F82C70EFBBBC9346F813122C8F75428132418`. The old receipt/report/render were not rewritten. The owned page ledger already held per-page entries; all 279 PNGs were freshly rehashed against it, with 279 matches and zero mismatches. This is an evidence-label correction only; no visual finding changes.

Related receipt integrity note: historical `handoffs/U7-source-qa-v03.md` has an incomplete Kremlin DOCX hash in prose (`...FB3B81A0`). Its referenced JSON evidence is correct: the Kremlin input hash is `6c110ed5e62f29e3facf97ae3b2d8e515b0066cc1b9f48ccc4d45f09fb3b81a0`; JSON identity SHA-256 is `2790631A3F4C4514056AB565FEEC36CFCD7B37F97FC7A724B881B6B616FD1856`. This adjacent historical typo does not affect the new QA input checks.

Evidence: `audit/fear-candidate/visual-qa/errata-v05.json`; `audit/fear-candidate/visual-qa/page-ledger-v01.json`. No source, candidate DOCX, render, or previous receipt was modified.
