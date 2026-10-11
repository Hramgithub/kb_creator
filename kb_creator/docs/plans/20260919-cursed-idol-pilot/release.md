# Release decision: user DOCX review

Goal: 20260919-cursed-idol-pilot. State: completed. Date:2026-09-20 Europe/Moscow.

## Frozen candidate

Manifest: working/cursed-idol/reviewed/release-candidate-r07.json (relative kb_creator).
SHA256:74032963008D3180B69FB391B96875E8C2A530DDCEC940357462AD38FFBAE210.
Freeze:2026-09-19T22:26:14.962629+00:00.
571artifact/evidence entries and94codeentries matched at independent review.
DOCX: r07/docx-002/docx/document.docx, SHA2CE7E24C028E70497F5C5467DF15569F2C1516E9C524E57FB5E53873C31CC80F.
Editable delivery: working/cursed-idol/delivery/Проклятый идол Манко Капака/;85pages,74assets,75files verified.

## Independent decision

[Independent release receipt](handoffs/P6-independent-release-review.md): ready for user DOCX review, no blocker/high/medium. Requested critic gpt-5.5/medium; actual runtime identity unavailable. Reviewer declared no implementation/material design participation; only receipt edited. Main captured result and explicitly closed contributor.

Visual coverage85/85;880translated/proofreadunits,124changes; no mechanical findings. SourcePDF unchanged. Known LOW observations: p10hardlineflow,p56shadedfigureindent; future nested-list falsefail/invalidmargin validation. Intentional exclusions: user acceptance, publication/public PDF or HTML, mandatory ArtView, autonomous backend, unrelated repository changes. No commit/push.

This decision applies to the frozen candidate only. Changing candidate code or outputs invalidates this receipt for that changed candidate. The delivery copy is provided for user edits; its initial hash establishes the handoff baseline, not restrictions on user postproduction.

## Next owner

User reviews/edits the [delivery DOCX](handoff.md); PDF is an optional subsequent operation after those edits. Pipeline follow-ups and automation limits are recorded in automation-report.md. Orchestrator token accounting: runtime goal aggregate reported in final answer; separate per-role totals unavailable.
