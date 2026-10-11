# Terra correction packet — AI-merge materializer asset links

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Engineer: `gpt-5.6-terra`, medium  
Status: `AUTHORIZED_P1_CORRECTION`

## Finding

The accepted first materializer copies selected asset bytes to content-addressed
`assets/<sha>.<ext>` paths and records `logical_name` in `ASSET_MANIFEST.json`,
but it has no way for decision Markdown to reference those final stored paths.
The same raw Markdown is also used for both `pages/page-NNN.md` and root
`RECONSTRUCTED_EN.md`, which require different relative prefixes. A candidate
could therefore have closed asset inventory while its reader Markdown contains
no usable asset links.

## Exclusive correction ownership

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- new receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_ai_merge_materializer_asset_link_correction_20260901.md`

Preserve the first receipt. You are not alone in the worktree; do not revert or
format any other file.

## Required correction

1. Decision Markdown may reference a selected asset only through the literal
   placeholder `{{asset:<logical_name>}}`, normally inside Markdown image/link
   syntax. `logical_name` must exactly equal one asset row in that decision.
2. Reject unknown, malformed, duplicated-definition, traversal or absolute
   asset references. Do not interpret arbitrary templates or other braces.
3. Every selected asset whose placement is not `reference_only` must appear at
   least once as its exact placeholder in the decision Markdown. A
   `reference_only` asset may be absent from Markdown.
4. Replace placeholders only after validation:
   - page file: `../assets/<content-addressed stored filename>`;
   - root `RECONSTRUCTED_EN.md`: `assets/<content-addressed stored filename>`.
5. Preserve original decision JSON bytes unchanged under `decisions/` and keep
   the manifest mapping from logical name to stored path/hash.
6. Keep identical-byte deduplication. Multiple logical names may map to the same
   stored content-addressed file, but none may silently disappear from the
   manifest or placeholder substitution.
7. Keep empty-Markdown visual-page support only for `reference_only` assets.
   A `full_page`, `handout` or `map` selected asset now requires a Markdown
   placeholder so it is actually present in reader reconstruction.

Extend the compact focused tests for page/root relative links, unknown/missing
placeholder rejection, reference-only empty page, and same-byte/two-logical-name
deduplication. Run only this focused test and `py_compile`; no real candidate,
MinerU, full suite, commit or push.

