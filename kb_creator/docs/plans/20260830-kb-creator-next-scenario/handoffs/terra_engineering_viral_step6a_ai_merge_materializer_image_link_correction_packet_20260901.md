# Terra correction packet — require reader-visible asset links

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Engineer: `gpt-5.6-terra`, medium  
Status: `AUTHORIZED_P1_CORRECTION`

## Reproduced defect

The first successful candidate contains 121 selected/copy-verified assets, but
38 non-reference assets on 25 range-A pages were written as bare
`{{asset:logical_name}}` placeholders. Substitution correctly produced stored
paths, but bare paths are not Markdown image links and therefore do not render.
Ranges B/C used the intended `![alt]({{asset:...}})` syntax.

The v1 decisions and v1 candidate are preserved as rejected evidence. A fresh
v2 decision root/candidate will be used after correction.

## Exclusive ownership

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- new receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_ai_merge_materializer_image_link_correction_20260901.md`

All previous receipts and every other file are read-only. You are not alone in
the worktree; do not revert or reformat others' work.

## Required correction

1. Every placeholder that appears in decision Markdown must be the exact target
   of Markdown image syntax `![nonempty alt]({{asset:<logical_name>}})`.
2. Every selected non-`reference_only` asset must have at least one such image
   use. Bare placeholders, empty/whitespace alt text, ordinary link-only uses,
   unknown names and malformed syntax fail before staging.
3. `reference_only` assets may remain absent from Markdown. If their placeholder
   is present, it must also use valid nonempty-alt image syntax.
4. Keep page/root path substitution, content-addressed storage, byte
   deduplication, original decision-byte preservation and page-context errors.
5. Add compact focused regressions for bare placeholder rejection, empty alt,
   valid image substitution in page/root, duplicate use and reference-only
   absence.

Run only the focused test and `py_compile`. Do not run real decisions/candidate,
MinerU, full suite, verifier, commit or push.

