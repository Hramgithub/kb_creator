# Terra engineering receipt — Viral Step 7 visual-QA priority transport remediation

- Goal id: `20260830-kb-creator-next-scenario`
- Step: `7 / visual-QA priority-original transport remediation`
- Timestamp: `2026-09-02T00:39:48+03:00` (`Europe/Moscow`)
- Role: reusable code/test engineering; repository policy `gpt-5.6-terra` / `medium`
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `complete_engineering_pass`; no visual inspection, candidate acceptance, release decision, or orchestration ownership transfer
- Scoped override: only the assigned generator, focused test module, this receipt, and the exact permitted absent v3 scratch root were written. Candidate A, v2 bundle, source/reconstruction, config, canonical plan/context/status/release state, Git, and production surfaces remained read-only.

## Scope and result

Implemented the narrow UI-access transport remediation. The generator now copies
exactly the selected 39 priority original byte streams into
`priority_originals/`, using a stable collision-free filename derived from each
candidate-relative source path. It does not decode/re-encode, resize, crop,
convert, annotate, or otherwise modify the transported images. The manifest
preserves `original_candidate_path` and adds a bundle-relative transported path,
independently recomputed bytes/SHA-256/dimensions, and closed count evidence.

## Files changed or checked

- Changed: `kb_creator/scripts/build_master_en_visual_qa_bundle.py`
  - SHA-256: `801450DAC2B41A89607DC52786E3AC06D24231640E2066561961770260F162D0`
- Changed: `kb_creator/tests/test_build_master_en_visual_qa_bundle.py`
  - SHA-256: `A334BE7C35DD609F6D302848B8F4C46D7260ED8399C66EAECFC52C2265075574`
- Changed: this receipt.
- Checked read-only: Candidate A inventory and MASTER_EN identities, publication
  config, source PDF, v3 JSON manifest, and all transported file hashes.

## Verification and evidence

From `D:\NRI\.worktrees\kb-creator-viral`:

```text
python -B -m py_compile kb_creator/scripts/build_master_en_visual_qa_bundle.py kb_creator/tests/test_build_master_en_visual_qa_bundle.py
python -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_build_master_en_visual_qa_bundle.py
# 6 passed in 5.87s
git diff --check -- kb_creator/scripts/build_master_en_visual_qa_bundle.py kb_creator/tests/test_build_master_en_visual_qa_bundle.py
```

Focused coverage now includes exact priority transported bytes/hashes, 39-path
closure, corrupt-copy rejection, source candidate non-mutation, and two-run
determinism, as well as the existing visual-bundle count, p80 and Babez checks.
No historical or unrelated suite and no MinerU workflow was run.

The required real scratch-only v3 run passed at:

`C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-master-en-visual-qa-bundle-20260902-v3`

Its manifest SHA-256 is
`9F6875D66823D10777702C8CEBD30D7BBDB5FA71AD98B3B65000A7AAA5C08614`.

JSON/hash-only audit result:

```text
candidate_assets: 123
reader_assets: 107
visual_review_units: 91
tiles: 107
contact_sheets: 27
priority_originals: 39
open_generation_errors: 0
transported priority originals: 39/39 exact source bytes and SHA-256 equality
```

Candidate A remained immutable:

```text
INVENTORY.json SHA-256: EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8
MASTER_EN.md SHA-256: 44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62
```

No image was opened and this receipt makes no visual-QA, content, acceptance,
or release claim.

## Blockers, risks, and next action

- Blockers: none for this engineering remediation.
- Risk: byte-identical transport only makes files readable to the visual QA
  surface; it is not a substitute for the required human/direct visual review.
- Next action: Luna/high reopens only the 39 v3 `priority_originals` files at
  original detail and appends a new QA receipt.

## Time and token record

- Elapsed time: approximately 25 minutes.
- Token use: unavailable in this contributor surface.
