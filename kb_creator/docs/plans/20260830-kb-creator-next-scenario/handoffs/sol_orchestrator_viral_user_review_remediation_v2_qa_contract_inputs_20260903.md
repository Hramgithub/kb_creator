# Viral v2 QA contract-input completion

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-qa-contract-inputs`
- Owner: current `nri-engineer`, `gpt-5.6-terra` / `medium`
- Blocker receipt: `terra_engineering_viral_user_review_remediation_visual_qa_v2_20260903.md`
- Completion token: `READY_TO_RESUME_VISUAL_QA_V2`

## Objective and ownership

Add the three authoritative inputs required by Slice 4: per-page disposition,
dynamic visual-review declarations, and an external candidate-bound verifier
report. Candidate roots remain free of acceptance/verification sidecars.

Owned paths:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_qa_contract_inputs_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## V2 contract additions

### Source binding and page dispositions

Extend the closed v2 document object with source-PDF and accepted-reconstruction
inventory identities (`path`, `bytes`, `sha256`) and validate them against CLI
inputs without weakening v1.

Add required top-level `source_disposition` with exactly 124 ordered rows. Each
closed row contains:

- `page`, `audit_disposition`, `publication_disposition`,
  `publish_reader_content`, `decision_date`, `reason`, `page_markdown` identity.

Every row is `audit_disposition: reconstructed` and binds the immutable accepted
page Markdown. Pages 1--122 are `publication_disposition: reader` / true.
Pages 123--124 are exactly `excluded_advertising` / false with decision date
`2026-09-02` and nonempty reason. Reject missing/duplicate/out-of-order rows,
identity drift and any reader event/hierarchy/xref/recovery/asset on excluded
pages. Candidate `SOURCE_DISPOSITION.json` serializes these rows and summary,
not synthetic page lists.

### Dynamic visual-review declarations

Add required top-level `visual_review_units`. Each closed row contains:

- `review_id`, `kind`, `source_pages`, `event_ids`, `asset_ids`, `priority`,
  `contact_sheet_group`.

Use a closed kind enum covering heading/outline, callout, ordered-list-callout,
table, equipment-card, creature-statblock, inline-run-in, full-page-map,
physical-page-pair, xref/recovery and asset-placement review. Validate unique
ids, reader page/event/asset closure, nonempty coverage, boolean priority and
nonempty group. Counts are derived only from declarations.

### External verification report

Extend verifier CLI/API with an optional explicit absent `--report-path` outside
the candidate. After a successful full v2 candidate verification, atomically
write canonical JSON schema `kb_creator.master_en_verification.v2` containing:

- status/scenario/candidate root name;
- candidate inventory digest and inventory-file SHA-256;
- config, source PDF, reconstruction inventory and verifier-script SHA-256;
- independently recomputed metrics and exact visual-review count.

The report has no timestamp or absolute/device path and is not written inside
the candidate. Refuse existing/symlink/report-in-candidate paths. Preflight-only
never writes a report. Add a reusable report validator for later QA consumption
without importing builder code.

## Tests and evidence

Update synthetic fixtures and add positive/mutation tests for identities, all
124 rows, exact excluded pages, leakage, review-unit closure/dynamic counts,
report atomicity/path safety/tampering and candidate cleanliness. Retain all v1
and v2 gates and verifier independence.

Run both full test modules, both `py_compile`, real v1 builder/verifier
preflights, no-builder-import and diff check. Write the exact receipt and return
the token only when all inputs are available.

No visual-QA script, real config/evidence/source/reconstruction/candidate/Git/
Step 8A changes.
