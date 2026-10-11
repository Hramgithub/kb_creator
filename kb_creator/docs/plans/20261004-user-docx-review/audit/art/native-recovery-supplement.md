# U3 bounded recovery supplement

This supplement records the user's later scope decision relayed by the orchestrator: use the existing reviewed DOCX, HTML, assets and exact original PDF to produce preserved-content successors. No OCR, translation, old master reconstruction or replay restoration is required for this bounded correction. Missing upstream data remains a provenance limitation, not a blocker for the authorized reader repair. This supersedes the dependency-checkpoint next action in immutable `handoffs/U3-architect-v01.md` for the bounded scope only.

## Frozen selection

`native-recovery-spec.json` SHA-256 `4653EB8E849B5F4CBEA4714BB5DB2CE4718E80BB87A3C0BCE0D8CE053F51C203` defines all23source-page selections, exact source object/xref, encoded and selected byte hashes, dimensions, source-page bbox and matrix, zero crop, HTML heading anchor, and verified unique Word bookmark/paragraph/text binding.

There are **21 unchanged native JPEG selections, one native JPEG2000 image decoded to lossless RGB PNG (page79), and one full-page render exception (page74)**. The source PDF identity and reviewed DOCX identity are frozen in the JSON. All22native objects were independently located by PDFium using exact encoded stream hash and pixel dimensions; their occurrence bounds were captured. Every Word heading bookmark is present exactly once in the current human-reviewed DOCX. All23candidate views were inspected against their original opening pages.

| Physical source page | Selected native xref or exception |
| --- | --- |
| 8 | 468 |
| 14 | 729 |
| 19 | 977 |
| 24 | 1430 |
| 29 | 1848 |
| 35 | 2279 |
| 41 | 2693 |
| 51 | 3252 |
| 57 | 3517 |
| 63 | 4133 |
| 69 | 4390 |
| 74 | Full physical page at144DPI, no crop; vector art exception |
| 79 | 5019, JPX to lossless RGB PNG |
| 86 | **5389**, not9245 |
| 92 | 5655 |
| 97 | 6100 |
| 103 | 6332 |
| 109 | 6612 |
| 119 | 7014 |
| 124 | 7415 |
| 135 | 8235 |
| 141 | 8597 |
| 147 | 8914 |

Two important selection corrections emerged from actual inspection. Page86's largest object9245 is blank paper texture; the scene is5389. Page74's largest raster is lettering/shadow, while the boat/sea scene is vector content. Thus the `dominant_native_candidate` entries in earlier `analysis.json` are explicitly exploratory candidates, superseded by this reviewed selection. Never implement a largest-image heuristic.

Page74's finite fallback keeps the complete source scene and its English title/byline/tags in a144DPI full-page facsimile. Preserve the existing translated text separately and disclose that fidelity exception; it is consistent with existing full-page opening facsimiles. Do not crop away the ship/sea or manufacture a text-free image. An optional exact vector-object composition can remove lettering later only with its own object-level evidence. This exception need not restart OCR or translation. Source124's native art has a small inherent `anomaly` label; preserve it as original graphic content.

## Implementation boundary and acceptance

The engineer should make an explicit, reusable asset-insertion revision from the current DOCX/HTML. The candidate directory must be new; original source and reviewed DOCX remain byte-identical. Use the exact scene selections and insert after each opener's existing translated heading/byline/tag group, before the next source-page body. The JSON's HTML anchor and unique Word bookmark identify the owner. Preserve source-page provenance independently of physical reader pagination. Use the existing opening-art sizing policy with proportional scaling and no crop; confirm actual placement after rendering.

Keep all original63image hashes and their ordered occurrences. With the23new scenes, the expected count for this concrete single-image-per-opener design is86. Preserve all existing body text, styles, links, comments/replies and their anchors except changes separately authorized by the user's comment decisions. A lossy DOCX-to-HTML-to-DOCX round trip is not an acceptable preservation strategy. Compare those invariants structurally; comments require OOXML checks because preview PDF does not display them reliably.

The reusable source-art coverage gate must take an independently declared required graphic domain, not derive it solely from the candidate master/HTML. For this revision, freeze all26opening identities plus the existing63asset identities and23explicit additions. Require one correct output occurrence for each of26openings, original63ordered occurrences conserved, source/hash/anchor agreement and no unexplained image removal. Maintain an extension point for the full meaningful-source-graphic ledger described in `report.md` without claiming that missing historical source/master lineage has been repaired.

Minimum negative checks: omission of any one declared opening fails even if actual image counts are self-consistent; wrong story anchor fails; page86paper texture substituted for5389 fails; JPEG2000 converted to blank/incorrect pixels fails; invalid source identity fails; lost user reply or changed body text fails; unapproved crop/duplicate art fails. Positive check: exact23selections inserted and existing63retained with26/26opener ownership passes structural coverage. Final candidate rendering must inspect every changed page and all23new pictures for clipping, scale, surrounding heading/byline/tag flow and page breaks. A separate independent critic reviews the frozen implementation/candidate.

## Supplemental handoff metadata

Goal/step: `20261004-user-docx-review` / U3 follow-up. Role policy: architect `gpt-6-astra/high`; actual runtime unavailable. Orchestrator policy owner remains `/root`, `gpt-6-sol/medium`; assignment `platform-unverified`; override none. Timestamp2026-10-04T20:46:00Z; additional elapsed approximately4minutes; tokens unavailable.

Checked: exact original object streams and26opening reference images,23candidate visuals, existing reviewed Word bookmarks, HTML anchors. Added only `native_spec.py`, `native-recovery-spec.json`, three `native-candidates-contact-*.jpg` previews and this immutable supplement under assigned audit/art. No source/book/production asset or implementation changed. Source/raw selection data were decoded in memory for inspection; the only saved images are diagnostic contact sheets, not production extractions.

Result: actionable finite23art recovery specification; no new translation/OCR needed. Blockers: none for bounded recovery under the declared page74facsimile exception. Historical upstream cause remains unresolved. Next: orchestrator dispatches scoped engineering/QA from this frozen selection and retains canonical state/release ownership. This architect does not provide the final release review of the repair it specified.
