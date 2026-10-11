# Source Integrity Warning Pages - Orchestrator Summary

Goal: classify `possible_cross_column_sentence_split` warnings from
`source_pdf_integrity_audit` for the Innsmouth EN PDF -> normalized EN source
stage.

Source audit:

`kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/source_pdf_integrity_audit.json`

Normalized source:

`kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Formatted/The_Innsmouth_Terror_Source_Text_Normalized_EN.md`

## Coverage

Assigned warning pages:

`005`, `006`, `007`, `009`, `010`, `012`, `013`, `016`, `019`, `020`,
`021`, `023`, `028`, `030`, `031`, `032`, `033`, `035`

Covered pages:

`005`, `006`, `007`, `009`, `010`, `012`, `013`, `016`, `019`, `020`,
`021`, `023`, `028`, `030`, `031`, `032`, `033`, `035`

Coverage status: complete.

## Classification

| Page | Status | Evidence summary | Action |
| --- | --- | --- | --- |
| 005 | real_issue | Lovecraft quote is split around `INTRODUCTION`; second half appears after body text. | Repair page 005 extraction so the full quote is one pre-body block. |
| 006 | real_issue | Right-column body and `Table 1` are interleaved; orphan table fragments remain at page end. | Add table/right-column policy for page 006; keep `Table 1` intact. |
| 007 | ok | Normal two-column page; warning triggered by layout/header residue. | No cross-column fix; optional header residue cleanup. |
| 009 | ok | Two independent biography entries, left Anna then right Christopher. | No source fix. |
| 010 | ok | Left Sammy/Crew, right `MINOR NPCS`; independent section start. | No source fix. |
| 012 | ok | Left Orne Library bullets, right `THE ARKHAM ADVERTISER`; no sentence split. | No cross-column fix; if revisited, inspect note/caption noise. |
| 013 | ok | Left Advertiser continuation, right `THE MISKATONIC PLAYHOUSE`; normal page flow. | No source fix. |
| 016 | ok | Left Gilman House, right Production Train Car; normal section split. | No source fix. |
| 019 | ok | Left trailer/handout block then right continuation; acceptable two-column flow. | No source fix. |
| 020 | ok | Main body left, Keeper note sidebox right; normalized order is preferable. | No source fix. |
| 021 | ok | Normal investigation page; left setup then right interaction text. | No source fix. |
| 023 | real_issue | `Table 2` row ranges/descriptions are interleaved into broken prose. | Add table-aware extraction or page-type override for Table 2. |
| 028 | ok | Normal section split; normalized source separates sections coherently. | No source fix. |
| 030 | ok | Full-width locomotive/statblock page; warning caused by header/statblock density. | No source fix. |
| 031 | needs_human_visual_review | Text layer and visible page evidence conflict around `What if they’re captured?`. | Human visual review before changing extraction policy. |
| 032 | ok | Normal epilogue/rewards two-column page. | No source fix. |
| 033 | ok | Statblock spread; warning caused by decorative header and concurrent statblocks. | No source fix. |
| 035 | ok | Statblock spread; left-then-right sequence remains readable. | No source fix. |

## Summary

- total warning pages reviewed: `18`;
- `ok`: `14`;
- `real_issue`: `3` (`005`, `006`, `023`);
- `needs_human_visual_review`: `1` (`031`);
- missing pages: none.

## Handoff Receipts

- `source_integrity_warning_pages_A1.md`: pages `005`, `006`, `007`;
- `source_integrity_warning_pages_A2.md`: pages `009`, `010`, `012`;
- `source_integrity_warning_pages_A3.md`: pages `013`, `016`;
- `source_integrity_warning_pages_B.md`: pages `019`, `020`, `021`,
  `023`, `028`, `030`, `031`, `032`, `033`, `035`.

## Next Actions

1. Implement reproducible source extraction fixes for pages `005`, `006`, and
   `023`.
2. Visually review page `031` before deciding whether it is a source-layer
   defect.
3. Re-run `source_pdf_integrity_audit` after fixes and require zero
   `real_issue` warning pages before continuing downstream.
