# Engineer receipt — MASTER_EN boundary cleanup and lining numerals

Date: 2026-09-16
Role: engineering, user override `gpt-5.6-sol/high`
Scope: reusable builder/verifier/renderer/tests only; no publication run, acceptance, canonical plan/status, or historical artifact was changed.

## Root causes

1. OCR normalization (`normalize_page_text(..., join_hyphenated_lines=True)`) is page-local. A standalone `<!-- source-page-NNN -->` marker therefore prevented both dehyphenation and ordinary lowercase prose continuation at a physical page boundary. Downstream HTML correctly rendered the two Markdown paragraphs/sections it received; joining there would have hidden an upstream MASTER_EN defect.
2. The production reader CSS declared the Georgia/Times font stack but no numeric OpenType policy. Computed-style evidence supplied from the current HTML showed `fontVariantNumeric=normal` and `fontFeatureSettings=normal` for body and statblock text, allowing oldstyle numerals. `lining-nums` is now explicit at `body` and inherited by prose/statblocks. `tabular-nums` was intentionally not enabled because equal-width figures would alter normal prose spacing.

## Design

- V3 MASTER_EN projection now performs a fail-closed cross-page continuation pass after configured page exclusion and before all derived counts/materialization.
- A join is allowed only for consecutive source pages, exact blank-line marker topology, two plain-prose paragraphs, a lowercase Unicode continuation, and a non-terminal alphabetic left edge. A trailing hyphen is removed for a word continuation; otherwise one space is inserted.
- Headings, lists, indented/fenced code, tables, Markdown images, hard-break statblocks, finished sentences, uppercase new paragraphs, and non-adjacent page markers are not joined.
- The page marker remains a standalone audit marker and is repositioned immediately after the completed reader paragraph. `MASTER_EN.provenance.json` records each transition (`from_page`, `to_page`, mode, and hashes of both boundary lines); `derived.page_boundary_joins` records the count.
- The independent verifier separately recomputes the normalized MASTER_EN and transition ledger; it does not import builder code.
- Production CSS adds `font-variant-numeric: lining-nums` to `body`, which covers body copy and statblocks through inheritance.

## Changed files and current SHA-256

- `kb_creator/scripts/build_scenario_master_en.py` — `C68148519F5C3AFAAAEB125BD83CFD2143045D21194750DE99F7F0DD26A1A5F1`
- `kb_creator/scripts/verify_scenario_master_en.py` — `5CE3511BFBDBF3BA88A6C90E6A528B86E650582D8567C5B159A05035DB1FB4A0`
- `translator/translator.py` — `F9CC50CB592C4921FE117B12E65CB8F159A30CE19D6128B90B708E7643FB4F3A`
- `kb_creator/tests/test_build_scenario_master_en.py` — `1971624CB8C276B13742DC621498BD25D9EB4058ABA394918AA023943C596366`
- `kb_creator/tests/test_publication_html_adapter.py` — `9099B77E5AFF1C4984B180786B3ACA7A155E883D2DB41552255BEF4FD4574A6B`

The HTML adapter test file and translator also contain earlier/concurrent statblock work already present in the shared dirty worktree; this packet added only the lining-numeral assertion/declaration there.

## Evidence

- `py_compile` for builder, verifier, and translator: pass.
- `pytest kb_creator/tests/test_build_scenario_master_en.py -k MasterEnV3NeutralTests -q`: `5 passed, 77 deselected, 8 subtests passed`.
- `pytest kb_creator/tests/test_publication_html_adapter.py -k compact_terminal_statblock -q`: `1 passed, 9 deselected`.
- `pytest kb_creator/tests/test_publication_html_adapter.py -q`: `10 passed`.
- Read-only run12 probe: exactly two transitions — page `003→004` `dehyphenated_word`, page `004→005` `continued_prose`; `malleability of the human body` and `end of the same day` are restored; marker count is unchanged.
- `git diff --check` on all five code/test files: pass.

Adjacent full-file command (`pytest test_build_scenario_master_en.py test_publication_html_adapter.py -q`) produced `29 passed, 63 failed, 8 subtests passed`. Every failure was in legacy Viral fixtures because this checkout lacks the declared Viral PDF/reconstruction package or has pre-existing frozen `publication_config_v1.json` identity drift; the V3 and HTML focused suites passed in the same environment.

## Risks / blockers

- Historical V3 candidates intentionally remain immutable. Because the closed V3 provenance now includes transition metadata and a derived count, re-verifying an old candidate with the new verifier will fail closed; a fresh candidate must be built through the governed workflow when authorized.
- The heuristic deliberately prefers false negatives over semantic over-joining. Ambiguous punctuation, styled inline starts, non-adjacent pages, or structural Markdown remain split for manual reconstruction review.
- No release/acceptance decision was made. Final independent critic and user reading acceptance remain outside this packet.
- Exact token telemetry for this contributor is unavailable.
