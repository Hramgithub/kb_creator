# U2 bounded QA receipt v01

- Goal / step: `20261004-user-docx-review` / `U2`.
- Role: bounded QA, assigned `gpt-6-luna` / `medium`; runtime identity/effort unverified.
- Orchestrator policy owner: `gpt-6-sol` / `medium`.
- Assignment state: `platform-unverified`.
- Scoped override: none.
- Scope: read-only review of the six latest DOCX packages' complete native Word comment metadata/reply graphs and tracked changes; Leningrad skill inventory, current CoC glossary provenance/freshness, and supplied original source/package availability. No implementation, repairs, terminology acceptance, release decision, or canonical plan/context/status/release writes.
- Result: bounded inventory complete. Exact replies, anchor evidence, package hashes, durable IDs and disposition text are recorded in the audit files below. Findings support orchestration/integration only; unresolved terminology remains explicit.

## Files checked

- `kb_creator/deliverables/latest/cursed-idol/document.docx`
- `kb_creator/deliverables/latest/dissociation/document.docx`
- `kb_creator/deliverables/latest/fears-sharp-little-needles/document.docx`
- `kb_creator/deliverables/latest/number-7-dream/document.docx`
- `kb_creator/deliverables/latest/secrets-of-the-kremlin-1931/document.docx`
- `kb_creator/deliverables/latest/shadows-of-leningrad-1938/document.docx`
- `kb_creator/deliverables/latest/MANIFEST.json`, Leningrad latest HTML, and supplied duplicate package at `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\temp\1938 Тени Ленинграда\shadows-of-leningrad-1938\`.
- Current authority `CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv`, its `README.md`, relevant 20260920 goal plan/context, `kb_creator/README.md`, and `docs/governance/nri_goal_governance.md`.
- Supplied source PDF: `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\temp\1938 Тени Ленинграда\5_Shadows of Leningrad, 1938.pdf`.

## Verification and evidence

- Six-package inventory: 46 comments total (Fear 33; Leningrad 13); 18 OOXML top-level comments and 28 parent-linked replies; 15 empty comments. The other four packages have zero native comments.
- Fear: all 11 NRI issue roots have one nonempty user reply and one empty companion. Leningrad: five NRI issue roots; four have nonempty user decision text, and `LEN-HANDOUT-RUSSIAN` has no nonempty response. Two additional user comments are top-level in OOXML but match the Yuri and Albion issue anchors and paragraph text exactly; the report labels these issue links as inferred. Empty comments are not treated as decisions. The five Leningrad NRI roots and explicit replies have Word `done=0` flags.
- No `w:ins`, `w:del`, `w:moveFrom`, or `w:moveTo` elements were found in any `word/*.xml` member. Body paragraph text is unchanged from the Git HEAD LFS package for both reviewed documents (zero changed paragraphs); this check does not claim all non-text package bytes are identical.
- Leningrad source PDF SHA-256 `E8C21B6D0BFBED034E6577C7BE01EE305EBFE480C93F87225B07C12AAFD3F10A`, 2,800,661 bytes, 49 pages. Visual checks of PDF p.6 / printed p.5 confirm the source explicitly says fifth edition. PDF p.41 / printed p.40 and latest HTML source page 041 provide a concrete 15-skill Albion card comparison with scores preserved.
- Current registry has 426 rows (94 accepted, 332 review-required), SHA-256 `8F6A41A64CA5A90621F6B8C2F3B40B4FE3658D7DE88B0D0A82BF95C1F82E6800`. Its bytes match `origin/main` commit `c981f2be45d07d718548cf3e0200f1a3688e68c7`; last path commit is 2026-09-28. The README's N132 count of 403 is stale. Registry has no explicit version field.
- Existing book-scoped review-required terms for `Move Quietly`, `Hide in Cover`, `Conceal`, `Sneak`, and `Natural History` preserve source-edition distinctions. The current book-bound effective glossary snapshot/provenance is not in either transferred reader package. Exact rows, current Russian labels, source-card scores, accepted field/status and bounded candidate mappings are in the terminology audit. No mapping was applied.
- The supplied adjacent Leningrad package contains DOCX/HTML/PDF/assets only; its DOCX is byte-identical to latest (SHA-256 `3E2172AB1CC9C045F9F5F472BF6F664337A06969FEDC786BEB2D8D40459007C8`). The original input/replay directory is absent from this checkout; the supplied PDF is source evidence, not proof that an executable replay/build is available.
- All JSON artifacts parse and focused count/hash assertions passed using bundled Codex Python with `-X utf8`. No system/repository Python, LibreOffice, tests, renders/rebuilds, or DOCX writes were used. Generated PDF page images were temporary QA evidence, outside project deliverables.

## Artifacts

- `audit/comments/comments_inventory.json`
- `audit/comments/comments_report.md`
- `audit/terminology/leningrad_inventory.json`
- `audit/terminology/leningrad_inventory.md`

## Blockers and next action

- `LEN-HANDOUT-RUSSIAN` remains unanswered in the reviewed package; do not infer approval from empty comments.
- Exact current-registry rows for `Hide` and `Bargain` are absent. Keep them unresolved pending an explicit scoped terminology decision. `Conceal`, `Sneak`, `Move Quietly`, `Hide in Cover`, and `Natural History` have book-scoped `review_required` rows; don't collapse them into modern skills by assumption. Accepted 7e forms and proposed card corrections are identified in the terminology report; scores remain intact.
- Current shared registry freshness is verified against `origin/main`, but the exact effective glossary snapshot used to build the reviewed DOCX is unavailable. README's stale N132 count can be handled separately if the orchestrator chooses; no registry mutation is required for this audit.
- Next: orchestrator integrates the captured user wording and decides which accepted-form spelling corrections to authorize, while routing `Hide`/`Bargain` and the unanswered handout issue as scoped open decisions. Replay/build feasibility remains unverified; do not claim the source PDF alone closes it.
- No acceptance or release decision is made by this receipt.

## Accounting

- Elapsed time: approximately 30 minutes wall time.
- Token use: unavailable.
- Timestamp: 2026-10-04 20:44 UTC.
