# Engineer receipt — hierarchical production TOC

Date: 2026-09-16
Role: engineering, user override `gpt-5.6-sol/high`
Scope: generic HTML TOC renderer, Dissociation HTML configuration, HTML→DOCX TOC projection, and focused tests. No publication run, source/master, acceptance, canonical plan/status, README, or `.codex` configuration was changed.

## Outcome

- Added opt-in `generated_hierarchical` TOC mode driven only by heading anchor IDs. It never matches visible titles.
- The mode accepts ordered `top_level_anchor_ids` and optional `parent_children`. It fails closed on malformed, unknown, duplicate, cyclic/role-overlapping, unresolved, and (when `require_all_heading_ids=true`) omitted anchors.
- HTML uses an unnumbered nested `<ul>`. Each top-level `<li class="toc-group">` wraps its children and has `break-inside: avoid`; parents are bold, children are indented and normal weight.
- TOC columns/font/line height/gap remain generic config values. Dissociation is configured for two balanced columns, `12.5pt`, line-height `1.25`, and `7px` item gap.
- HTML nav exports generic DOCX metadata (`numbering=none`, hierarchical layout, point font size). The DOCX builder preserves legacy numbered/flat behavior unless those attributes are present.
- Hierarchical DOCX output omits ordinal prefixes, keeps source case, renders bold parents and indented normal children at the configured size, splits columns only between complete groups, and chains parent/children with Word `keep_with_next` where supported.

## Dissociation anchor policy

- Excluded: landing `dissotsiatsiya`; terminal statblock `soprotivlenie-lyudei-politseiskie-ispytuemye-zhiteli-aniaka`.
- Top level: `vvedenie`, `okruzhenie-pervoe`, `okruzhenie-vtoroe`, `okruzhenie-trete`, `vyzhivshie`, `nagrady-i-posledstviya`.
- Children exactly match the approved groups, including disambiguated duplicate anchors `rassledovanie-2` and `interlyudiya-v-mire-grez-2`.
- The existing generated heading text remains `Оглавление`; the unrelated latent `generated_fallback_title` behavior was not activated, preserving current release-QA expectations.

## Changed files and current SHA-256

- `translator/translator.py` — `CED40F6F85DB2BEDA813C0C9AFE27D9C264D2BC1F7D5D8F139CF8E466EC5CC9F`
- `translator/tests/test_recovery_support.py` — `C9B0CC27DE267CFC02D8D57D4B474B34D39D1F3FFAB86014018B055EB362C4C1`
- `kb_creator/scripts/production_docx.py` — `1D070D03879832407D1C6338AF7B3F3C56B4F7C0C4D12EFC0698C79E86B1741A`
- `kb_creator/tests/test_production_docx.py` — `FAEA0D006620BE40B33943E4FCFA835C94D9D926ACC3AD89BCC4296F7296063E`
- `kb_creator/inputs/dissociation/publication/v1/configs/html.json` — `7C27A41974AB01EEAE274DCD9BB6257547E929A017C7103F60D7D428FBCB7BDC`

`translator/translator.py` also contains earlier/concurrent work already present in the shared dirty worktree; this packet is limited to the hierarchical TOC renderer, metadata, and CSS there.

## Evidence

- `pytest translator/tests/test_recovery_support.py -k toc -q`: `23 passed, 45 deselected, 5 subtests passed`.
- `pytest kb_creator/tests/test_publication_html_adapter.py kb_creator/tests/test_production_docx.py kb_creator/tests/test_publication_docx_adapter.py -q`: `17 passed`.
- Full `translator/tests/test_recovery_support.py`: `67 passed`, with one unrelated existing failure in `test_reader_master_leading_anchor_preserves_following_markdown` caused by escaped duplicated leading anchors in the shared renderer changes outside this TOC packet.
- Dissociation read-only HTML probe: 6 top-level groups, 13 children, landing absent, statblock absent, balanced two-column metadata present, `12.5pt` present, no `<ol>`.
- Temporary actual-anchor HTML→DOCX probe: 19 linked entries, no numbering, group-safe column split `9/10`; column two begins with `Окружение второе`, so no parent/child group crosses the split.
- `py_compile` for `translator.py` and `production_docx.py`: pass.
- `json.tool` for the Dissociation HTML config: pass.
- `git diff --check` for all five code/config/test files: pass.

## Risks / blockers

- No live HTML/DOCX/PDF publication stages were run. Fresh governed artifacts still need to be built and visually reviewed by the orchestrator.
- Word pagination can override keep constraints in physically impossible layouts; the converter additionally prevents splitting a configured group between the two TOC table columns.
- The one unrelated full-suite renderer failure above remains outside this packet; focused TOC and all HTML/DOCX adapter suites used here pass.
- No acceptance or release decision was made. Exact contributor token telemetry is unavailable.
