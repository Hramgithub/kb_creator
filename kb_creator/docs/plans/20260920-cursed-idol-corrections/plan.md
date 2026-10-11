# Cursed Idol correction implementation

Goal20260920-cursed-idol-corrections. State complete for user-review handoff. Independent C6 release gate approved; publication acceptance pending. User authorized fixes, then a local commit and a complete review package: DOCX, MASTER_EN, MASTER_RU, reconstruction, metadata, assets, configs and QA. User proofreading remains pending. Preserve PDF, predecessors and editable user copy. No push authorized. ArtView optional; source-first TOC, numeric HP, normalized typography/text, clean asset extraction required.

Role contract:nri_goal_governance. Main sol/medium policy owns orchestration,canonicalstate,integration,bookdata and user synthesis; actualruntime unavailable/platform-unverified,override none. Terra medium engineering;Sol high architecture;Luna medium boundedexecution/low QA;5.5medium independentrelease. Critics must not implement/design reviewed candidate.

|Step|Owner|Dependencies|Done when|State|
|---|---|---|---|---|
|C1|Main+Sol high|Audit|Successor and source TOC/reader contracts bounded; identity baseline recorded|Complete|
|C2|Terra medium|Audit|Unified typography styles and native figure crop; meaningful tests|Complete; unified roles and theme override removal|
|C3|Luna medium + Main|Audit|Reusable PDF image extraction preserving alpha; selected clean assets|Complete; 8 selected from original PDF and visually checked|
|C4|Main + Terra medium|C1|Reviewed text normalization, source TOC mapping, crossrefs, HP presentation scripted|Complete; 77 TOC targets, six body references, numeric HP, verified reflow authority|
|C5|Main+QA low|C2–C4|New verified MASTER_RU/DOCX,allpages inspected,new delivery|Complete:81finalpages,76exacthashreuse+5freshviews; new delivery verified|
|C6|5.5mediumcritic+Main|C5|Frozenrelease review,docs,status,handoff|Complete; independent C6 approves user-review handoff|
|C7|Terra medium + Main|C5|Sealed complete artifact bundle, offline verification, scoped authorized commit|Complete:1335payloadfiles, offline verify pass; authorized local commit|

Evidence: C1 spec; C2 typography receipt; C3b PNG extraction; C4 successor-02; C5 text QA; C7 review bundle. Generic reader tests: 15 passed including correction binding; package/reader/extractor/bundle suite: 33 passed, 1 host symlink skip. True text amendments: 15 versus predecessor (12 spacing, 3 prose joins), not 15 versus original documentary draft. Earlier audit spacing counts included false positives on single-letter conjunctions; these ordinary headings remain unchanged. Text QA initially compared preimage hashes to new text; corrected receipt confirms all 15 old-text bindings.

Root inspected source pages29/39 and asset comparison sheets. Clean choices2/12/16/32/33/34/47; item48 remains original (candidate blank paper rejected). Word native crop reproduces visible Ghost and left photo fragment without raster modification. All original and selected assets retained in full bundle.

Baseline:r07/docx-002 SHA2CE7E24C028E70497F5C5467DF15569F2C1516E9C524E57FB5E53873C31CC80F. Audit../20260920-cursed-idol-quality-audit/audit-report.md. Avoid fullOCR/retranslation if compatible verified inputs can be explicitly reused by a successor operation. No manualsealedhashpatching. Everyseedclass scanned fullscope,regression/rebuild evidence required.

## Final bounded contributor packets

- C9 prisoner_asset_fix / Terra medium: clean source XObject for page28 stray paragraph; owns only prisoner-choice data and C9 receipt. No master/code/source edits.
- C7b bundle_selection_finish / Terra medium: complete portable selection and Russian package guide; owns selection/guide/receipt only.
- C6-final correction_final_release / independent5.5medium: reflow authority and frozen bundle review; owns finalrelease receipt only, no implementation.
- Visual QA Luna low completed29–56 and57–81, receipts captured and agents closed. Root inspected1–28, found stale abbreviated page refs and prisoner text bleed; correction gate remains open until final rebuild evidence.

## Final outcome

r09/docx-003 and curated review-02 frozen, ready_for_docx_review / awaiting_user_review. 81 pages,74 placements,82 preserved asset files,8clean replacements,77TOC+6bodylinks,16numericHPcards. Full source/master/reconstruction/MinerU/config/QA payload verified after relocation. C6-final independent5.5medium review approves user handoff and localcommit; no blocker/high/medium remains in that scope. Source/r07/oldusercopy unchanged. User proofreading/book acceptance pending; no push. Contributor receipts captured and completed agents explicitly closed.

Token accounting: runtime aggregate reported in final chat; exact main versus contributor split unavailable. Historical QA/review checkpoints remain explicitly superseded by C6-final and final freeze.json.
