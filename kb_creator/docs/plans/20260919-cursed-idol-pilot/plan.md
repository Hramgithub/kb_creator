# The Cursed Idol of Manco Capác: supervised pipeline pilot

Goal id: 20260919-cursed-idol-pilot. State: completed. Release: ready for user DOCX review; user acceptance pending.

## Objective and authority

User supplied the 52-page PDF and explicitly authorized starting. Produce reviewed Russian DOCX + assets through five_step_docx_v1, documentary translation and separate literary proofreading. Correct reusable scripts with targeted tests when defects arise; source-specific content belongs in contracts, decisions, glossary and configs. No standalone book builder, hidden artifact patches, mandatory ArtView, public HTML/PDF, commit or push. Original source is immutable. User edits a delivered copy of DOCX after handoff.

## Role ownership

Canonical contract: docs/governance/nri_goal_governance.md. Main chat owns orchestration, integration, plan/context/status, decisions and synthesis; policy sol/medium, actual model/effort unavailable, assignment platform-unverified, override none. Architecture sol/high; engineering terra/medium; bounded execution luna/medium; QA luna/low; independent release critic 5.5/medium. Delegated contributors own only explicit packets/receipts, never canonical state. Requested model/effort recorded per dispatch; independent critic does not implement/design reviewed candidate.

## Plan

| Step | Owner | Depends on | Definition of done | State |
| --- | --- | --- | --- | --- |
| P1 | Main + bounded intake/glossary contributors | — | Source copied with identity, all 52 page roles inspected, source-specific contract/glossary/config, baseline hashes | Complete: P1 receipts and P2D correction; 14 handouts, 12 statblocks, 4 pregens; 76 terms |
| P2 | Main + reconstruction contributors | P1 | MinerU three views, all page decisions closed, fidelity audit, verified MASTER_EN + source semantics/assets | Complete: r07 reconstruction and MASTER_EN accepted;52pages16characterHP verified |
| P3 | Translation contributors + main | P2 | All documentary units translated and mechanically checked | Complete:880draftunits accepted r07;879 exact reusable rows plus1fresh corrected logo |
| P4 | Separate proofreading + main | P3 | EN/RU comparison, literary ledger, all units reviewed, independently verified MASTER_RU | Complete: r07 verified MASTER_RU;880reviewed,124changes/756unchanged. P4E/F28tests andP4G review; P5J corrected logo separate proofreading |
| P5 | Main + QA | P4 | Generic DOCX build, all-page visual QA, assets, editable delivery copy, upstream unchanged | Complete: r07/docx-002;85pages covered (83exact-PNG prior reviews,2fresh);74assets;ready_for_docx_review;editable delivery copied and hashed |
| P6 | Independent critic + main | P5 | Frozen release review, automation/change report, durable status and user handoff | Complete: P6 independent5.5medium release review ready for user DOCX review; no blocker/high/medium |

## Evidence and limits

Prior implementation freeze/review: ../20260919-five-step-implementation/release.md; 240 relevant tests passed, 5 skipped, 54 subtests. Prior real source was one page only; this is first full book on the profile. Full historical suite has preexisting import/fixture failures. Content tasks are performed by Codex; no autonomous model backend is claimed.

Next: user reviews and edits delivery DOCX; optional PDF build follows user postproduction. Pilot implementation and handoff complete. All generic defects are recorded in changes.md with failing layer, fix, regression evidence and rebuild scope.
