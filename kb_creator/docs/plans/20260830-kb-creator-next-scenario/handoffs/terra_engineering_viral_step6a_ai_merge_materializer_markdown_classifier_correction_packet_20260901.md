# Terra correction packet — materializer Markdown path classifier

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Engineer: `gpt-5.6-terra`, medium  
Status: `AUTHORIZED_P1_CORRECTION`

## Reproduced defect

The first real materializer admission stopped before output publication with:

`ValueError: markdown contains a forbidden marker, path or HTML`

Read-only classification found 37 false positives. The current pattern treats
any slash-led fragment and many in-word drive-shaped fragments as an absolute
path. It rejects ordinary source text including:

- `Lighthouse/Radio`;
- `video editing/sound engineering`;
- `and/or`;
- Call of Cthulhu values such as `1/1D3` and `1D8/4D10`;
- `Ideology/Beliefs`;
- escaped source text `Damage:\*` through the in-word substring `e:\`.

Target root remains absent. Decisions are frozen and must not be changed.

## Exclusive ownership

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- new receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_ai_merge_materializer_markdown_classifier_correction_20260901.md`

Preserve both earlier Terra receipts. You are not alone in the worktree; do not
revert, reformat or edit any other file.

## Required correction

1. Continue rejecting generated source-page markers, actual HTML/script tags,
   device-specific Windows absolute paths, UNC paths and POSIX absolute paths.
2. Allow ordinary slash punctuation, dice/Sanity notation, URLs and escaped
   Markdown source text. At minimum the six examples above and
   `https://www.chaosium.com` must pass.
3. Path detection must require a real token/path boundary. It must still reject
   examples such as `C:\Users\name\file.png`, `D:/NRI/file.md`,
   `\\server\share\file`, `/etc/passwd`, and a Markdown target
   `](/absolute/file.png)`.
4. HTML detection must target actual tag syntax rather than arbitrary text
   between `<` and `>`; `<script>` remains categorically rejected.
5. When decision validation fails during full materialization, include the exact
   `page-NNN.json` identity in the raised error without hiding the original
   reason.

Add compact regression cases to the existing focused test file. Run only that
focused test and `py_compile`; do not run the real candidate, MinerU, verifier
suites, full tests, commit or push.

