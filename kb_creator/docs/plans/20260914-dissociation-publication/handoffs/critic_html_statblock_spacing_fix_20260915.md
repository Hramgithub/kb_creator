# Critic receipt: HTML statblock spacing and dedup fix

- Goal id: `20260914-dissociation-publication`
- Step id: `html_statblock_spacing_fix`
- Role: independent critic
- Model: `gpt-5`
- Effort: medium
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Assignment state: recovery review-only
- Scoped override: none
- Timestamp: `2026-09-15T22:18:00+03:00`
- Elapsed time: unavailable
- Token use: unavailable

## Scope

Recovery independent implementation review of the scenario-neutral HTML
statblock spacing/dedup fix. I reviewed these inputs and did not rely on the
interrupted prior critic state:

- `kb_creator/pipeline/publication_adapters.py`
- `translator/translator.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_html_statblock_spacing_fix_20260915.md`
- run11 Stage 40 evidence, read-only

I did not modify implementation, tests, plan, context, status, publication run
artifacts, or acceptance records. I did not create or resume publication runs,
open a browser/server, commit, or touch `.codex/config.toml`. The only write was
this critic receipt.

## Verdict

GO.

No P0, P1, or P2 findings.

The implementation is narrow and appropriate for the reported defect. The
adapter detects terminal compact statblock-shaped heading sections by structure
rather than scenario vocabulary; derives renderer-compatible heading ids;
merges detected ids into existing `statblock_section_policy` instead of
replacing it; records detected ids in the adapter receipt; and lets the existing
renderer wrap the body heading exactly once in `statblock-card` while excluding
that heading from the generated TOC. Markdown hard breaks are preserved as
`<br>` and statblock paragraph spacing is tightened locally.

## Review Notes

- False positives: acceptable. The detector requires immediate post-heading
  nonblank content, at least three body lines, at least one digit, hard breaks
  on all but possibly the last line, and terminality relative to the heading
  section. Synthetic probes confirm ordinary hard-broken prose and a parent
  section with a child subheading are not classified. A terminal numeric
  hard-broken block before a sibling heading or page marker is classified, which
  matches the intended terminal statblock shape.
- Terminal detector: pass. The terminality check rejects content followed by
  more same-section prose or a deeper heading, and permits a same/higher-level
  heading or source page marker as a section boundary.
- Heading/TOC dedup: pass. The adapter slug logic mirrors the renderer
  transliteration and duplicate-id sequence. The renderer wrap target is one
  body heading id, and the generated TOC omits configured statblock ids.
- Hard breaks: pass. `render_markdown_paragraph()` now converts CommonMark
  two-space line breaks to `<br>\n` and still joins ordinary wrapped paragraph
  lines with a space.
- Compact CSS: pass. `.statblock-card` uses `line-height: 1.12`, statblock
  paragraphs use `margin: .2em 0`, and card headings have tightened top margin
  without changing global paragraph spacing.
- Generic regressions: no evidence found. Focused adapter tests and adjacent
  publication registry/control-plane tests pass with the current implementation.

## Evidence

- Working tree scope:
  - Modified: `kb_creator/pipeline/publication_adapters.py`
  - Modified: `translator/translator.py`
  - Modified: `kb_creator/tests/test_publication_html_adapter.py`
  - Untracked input receipt: `engineer_html_statblock_spacing_fix_20260915.md`
  - Untracked output receipt: this file
- SHA-256 hashes under review:
  - `kb_creator/pipeline/publication_adapters.py`: `C21EBC8918CF32646D0BC7EB76D0C9B4D0C304C7549846C16E6AE768427812EB`
  - `translator/translator.py`: `9CF57E4CE194E05B7CA64488DD3AB5AA60A9F57A96BDEE80D96F6C93C71BF8D8`
  - `kb_creator/tests/test_publication_html_adapter.py`: `A9D11A8E366F5CC35FAB8EF8DA7D94174C6621578DBB3978053FF5B738A852C2`
  - `engineer_html_statblock_spacing_fix_20260915.md`: `AEB8F18B9F77C83F3BFED3C0DDBA443FC3C81C78195EE83C3B7152935EB23845`
- Read-only run11 probe:
  - Source: `kb_creator/working/dissociation/publication/20260915-publication-11/outputs/40-html-candidate/evidence/derived_html_source.md`
  - Detector result: `['soprotivlenie-lyudei-politseiskie-ispytuemye-zhiteli-aniaka']`
  - Existing run11 report before this fix: `counts.statblock_cards: 0`
  - Existing run11 adapter receipt before this fix: `compact_statblock_heading_ids: None`
  - Terminal block observed at derived source lines 173-184
- Run11 evidence hashes:
  - `derived_html_source.md`: `91C0947B55E03FFF57B68FF58A1B5E044034E6CABFF019D716626997457D8372`
  - `production_html_report.json`: `C95C2B35AE90CB9E387AEE64D73E53ACBEC3D614D9319C123893F6F1F5794A78`
  - `html_adapter_receipt.json`: `E29AB44DFB5067D0CBD8BBAD60CFA99EC264FC7F507E8D1380BA59D54D373550`
- Synthetic detector probes:
  - `ordinary_prose`: `[]`
  - `child_subheading`: `[]`
  - `sibling_terminal`: `['terminal-values']`
  - `page_marker_terminal`: `['terminal-values']`
- Focused tests:
  - Command: `.tools/python/cpython-3.12.14-windows-x86_64-none/python.exe -B -m pytest -p no:cacheprovider kb_creator/tests/test_publication_html_adapter.py`
  - Environment: `PYTHONPATH=.tools/python-test-deps;.tools/MinerU/.venv/Lib/site-packages`
  - Result: `10 passed in 1.74s`
- Extended adjacent tests:
  - Command: `.tools/python/cpython-3.12.14-windows-x86_64-none/python.exe -B -m pytest -p no:cacheprovider kb_creator/tests/test_publication_registry_e2e.py kb_creator/tests/test_publication_control_plane.py`
  - Environment: `PYTHONPATH=.tools/python-test-deps;.tools/MinerU/.venv/Lib/site-packages`
  - Result: `42 passed in 91.88s`
- Static checks:
  - `.tools/PortableGit/cmd/git.exe diff --check -- kb_creator/pipeline/publication_adapters.py translator/translator.py kb_creator/tests/test_publication_html_adapter.py`: pass
  - `.tools/python/cpython-3.12.14-windows-x86_64-none/python.exe -B -m py_compile kb_creator/pipeline/publication_adapters.py translator/translator.py kb_creator/tests/test_publication_html_adapter.py`: pass

## Blockers And Next Action

Blockers: none.

Next action: orchestrator may proceed to the governed HTML-stage rebuild and
visual review. This receipt is an implementation GO only; final publication
acceptance still depends on the rebuilt candidate and normal release gate.
