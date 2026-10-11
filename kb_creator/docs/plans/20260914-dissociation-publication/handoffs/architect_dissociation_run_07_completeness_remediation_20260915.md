# Packet G — Dissociation run-07 completeness remediation

## Receipt

- **Timestamp:** 2026-09-15T03:03:07+03:00
- **Role / scoped override:** architecture and root-cause analysis, `gpt-5.6-sol` at `high`; read-only diagnosis except for this assigned handoff receipt.
- **Orchestrator policy owner:** main-chat `gpt-5.6-sol` at `medium`; ownership was not transferred.
- **Assignment state:** complete; bounded Packet G recovery after model-capacity failure.
- **Scope:** classify every failure in the immutable `20260915-cpu-first-07` source-visible completeness audit v2; specify closed decision remediation and separately identify audit-contract/implementation gaps.
- **Result:** the 28 reported errors contain **no true omitted narrative source text** and no selected-block ordering/duplication defect. Twenty-six are exact source units needing reviewed dispositions; two are valid Markdown text that the current proof construction cannot place. Decision-only remediation is **insufficient** because two code gaps remain. Run-07 is not to be mutated; it becomes implementation-stale only after the future audit code/contract change, at which point a fresh CPU-first run is required.
- **Files changed:** this receipt only.
- **Blocker:** Stage 05 cannot legitimately pass until engineering closes the two fail-closed audit gaps and reviewed allowlist rows/assertions are authored against the resulting fresh run authority.
- **Next action:** engineer implements the bounded audit correction and regression tests; independent critic reviews it; then execute a fresh CPU-first run and author fresh, byte-bound decisions/allowlist. Do not rerun or edit run-07 in place.
- **Elapsed time:** approximately 55 minutes across the initial investigation and this recovery turn.
- **Token use:** exact role token count unavailable.

## Immutable evidence identity

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `20260915-cpu-first-07/run.json` | 29,749 | `85534D85D0DAFDF7FA8A9FB95AB2CC769029066FCEF190E632C97D946BE17B5F` |
| `outputs/03-compare-views/comparison.json` | 449,244 | `08DD3F1C644997E579F679265E73D36E6BBFF84A9C656F03E5D240E42BCE3C95` |
| `outputs/04-visual-merge-bundle/visual/visual_manifest.json` | 14,568 | `A75B6D635BB6D83B84A7DC1A975BBFCF2DBFD77129B2FEAD679B3728A5FBC668` |
| `review/review_queue.json` | 5,232 | `8C623A1FF380270BD660228741DBBE68FC4F5F5964789B3D78592F48F2E35F38` |
| `20260915-cpu-first-07-decisions/decision_set.json` | 1,498 | `D13BBA3A196E8EFEA23527EF074E76DF56520BCEBE2F2A0C64F3DA72A71E7CBE` |
| `validation/source-visible-completeness-audit.json` | 251,917 | `B16618741A667C9EDE15377697DC8A6F42AD993C738338DAFB03B53EE3D13299` |

Audit result: `passed=false`; 26 `unaccounted` unit errors plus two page-level `Markdown contains omitted, reordered, or unproven reader text` errors. Page metrics were p1 `36/98`, p2 `12903/12924`, p3 `12204/12289`, p4 `12980/13001`, p5 `4392/4424`, p6 `5850/5891`; selected recall was `1.0` on every page. The low p1 completeness is cover text carried visually, not missing narrative.

## Closed classification and remediation table

Every unit action below is exact-unit scoped. An exclusion row must copy the audit unit tuple verbatim (`source_page`, `view_id`, `raw_index`, `block_type`, `bbox`, both text hashes, normalized count), bind the exact run-local triptych/render identity, and give a non-empty reviewer rationale. No wildcard or type/page-wide rule is permitted.

| # | Page / failing item | Exact evidence | Classification | Closed action under the v2 schema |
|---:|---|---|---|---|
| 1 | p1 `original_pipeline_txt:1` | `text`; bbox `[151,681,394,796]`; `H I D D E N E N E M Y SE NSORY CO N FUSIO N MI-GO`; original `190CB3C88448526497B20592955BC8F0108864CABFFF60DAA81D06D7AE1527F1`; normalized `C34441BC175B484D254EC36287ADD99E64E6F793BC7D57D28C4767FEC6CF96E6` | visual-only cover label | Add exact `source_text_exclusions` row classified `visual_only`, bound to selected logical asset `dissociation-cover.jpg` and p1 visual evidence. Allowed because the full-page cover asset is selected/materialized and preserves this non-reader cover label. |
| 2 | p1 `original_pipeline_ocr:1` | `text`; same bbox; `HIDDEN ENEMY SENSORY CONFUSION MI-GO`; original `EA700A10B71012C4A1BC039C14239F6D8A4ADA299D8BE7A9C47D910DC419909D`; normalized `C34441BC175B484D254EC36287ADD99E64E6F793BC7D57D28C4767FEC6CF96E6` | visual-only cover label, alternate view | Same exact `visual_only` disposition and asset binding; do not collapse it into row 1 because exclusions are unit identities. |
| 3 | p1 Markdown proof | Markdown starts `# DISSOCIATION`; the title is visible on the cover but absent from all required extracted text views | audit-proof false-positive, not a Markdown omission | Add a reviewed `visual_text_assertions` row for exact visible `DISSOCIATION`, exact reviewer-authored bbox and p1 visual identity. This row is schema-valid now, but acceptance awaits positional proof fix G1 below. |
| 4 | p2 `original_pipeline_txt:22` | `page_number`; bbox `[929,879,961,898]`; `113`; text hash `6C658EE83FB7E812482494F3E416A876F63F418A0B8A1F5E76D47EE4177035CB` | non-reader folio | Exact `non_reader` exclusion; `logical_asset=null`; visual proves a marginal folio, not reader body. |
| 5 | p2 `original_pipeline_ocr:22` | same type/bbox/text/hashes | non-reader folio duplicate | Exact `non_reader` exclusion, independently bound. |
| 6 | p2 `raster_pipeline_ocr:22` | `page_number`; bbox `[929,888,961,906]`; `113`; same hashes | non-reader folio duplicate | Exact `non_reader` exclusion, independently bound. |
| 7 | p2 `raster_pipeline_ocr:1` | `text`; bbox `[401,15,652,41]`; `DISSOCIATION`; original `7094C5102861BDC9EC2855F6270E680A24E613A81B1184EDBA0B4C0B29A01ED7`; normalized `CAA3522BEE6E08CFED41C444A5F651D2FDAA8CD5F535A265F5426D0387A7CE6A` | non-reader running header | Exact `non_reader` exclusion; visual proves repeated running furniture. |
| 8 | p2 Markdown proof | Markdown correctly restores initial drop-cap `T`; selected `original_pipeline_txt:3` begins `he mi-go...`; source glyph `T` is separately visible at PDF bbox approximately `[69.49,19.60,85.71,68.79]` | audit-proof false-positive, not a Markdown omission | Add exact visual assertion `T`, reviewer-confirmed bbox and p2 visual identity. Schema-valid, but must be interleaved before the selected paragraph by G1; appending it at page end is invalid. |
| 9 | p3 `original_pipeline_txt:45` | `page_number`; bbox `[38,879,68,898]`; `114`; hashes `9F1F9DCE319C4700EF28EC8C53BD3CC8E6ABE64C68385479AB89215806A5BDD6` | non-reader folio | Exact `non_reader` exclusion. |
| 10 | p3 `original_pipeline_ocr:45` | same type/bbox/text/hashes | non-reader folio duplicate | Exact `non_reader` exclusion. |
| 11 | p3 `raster_pipeline_ocr:46` | `page_number`; bbox `[38,889,70,907]`; `114`; same hashes | non-reader folio duplicate | Exact `non_reader` exclusion. |
| 12 | p3 `raster_pipeline_ocr:23` | `text`; bbox `[169,13,766,42]`; `FEAR'S SHARP LITTLE NEEDLES`; original `CB9C625BF78FCD1BDE9031139757E5FC7F5A7074B953AA0A3B47E481E894649F`; normalized `8D4312E1E64809C2B58FDDAB30CFA7E2869E361249982FCDC5E4ED804B7D46DE` | non-reader anthology running header | Exact `non_reader` exclusion; visual proves repeated top-margin furniture. |
| 13 | p3 `original_pipeline_ocr:36` | `text`; bbox `[478,93,865,119]`; `Examining Vessels (fow and Later)`; original `A0D2EE166000E2DEFC6159B18648F89FC6D503797D2E95E6C77A98B8F962766B`; normalized `7C4D6BA4E93465F05A0C870ABE750DC026C3391BB9C0C952F4A98F9F7B2A5727` | OCR-artifact alternate of reader heading | Exact `ocr_artifact` exclusion is allowed: p3 visual shows `Examining Vessels (Now and Later)`, and selected `original_pipeline_txt:36` contains that canonical text at the corresponding region. |
| 14 | p3 `raster_pipeline_ocr:37` | `text`; bbox `[478,171,865,195]`; `Examining Vessels (ow and Later)`; original `234F51829E4649ED744D15C61BF3DF69F0AB67342DB9442CDB79ED69CB230F88`; normalized `7CB87D5A1357BC521690EB3E937BAF461E91491D3B92D2F71C43CEEB61B48729` | OCR-artifact alternate of reader heading | Intended exact `ocr_artifact` exclusion, but current code blanket-rejects raster OCR artifacts. Accept only after G2 proves visual absence of `ow`, spatial correspondence, and coverage by selected canonical `original_pipeline_txt:36`. Never classify this reader heading as `non_reader`. |
| 15 | p4 `original_pipeline_txt:66` | `page_number`; bbox `[929,879,961,898]`; `115`; hashes `28DAE7C8BDE2F3CA608F86D0E16A214DEE74C74BEE011CDFDD46BC04B655BC14` | non-reader folio | Exact `non_reader` exclusion. |
| 16 | p4 `original_pipeline_ocr:66` | same type/bbox/text/hashes | non-reader folio duplicate | Exact `non_reader` exclusion. |
| 17 | p4 `raster_pipeline_ocr:69` | `page_number`; bbox `[929,889,961,907]`; `115`; same hashes | non-reader folio duplicate | Exact `non_reader` exclusion. |
| 18 | p4 `raster_pipeline_ocr:47` | `text`; bbox `[401,15,652,42]`; `DISSOCIATION`; hashes as row 7 | non-reader running header | Exact `non_reader` exclusion. |
| 19 | p5 `original_pipeline_txt:74` | `page_number`; bbox `[36,877,70,898]`; `116`; hashes `E5B861A6D8A966DFCA7E7341CD3EB6BE9901688D547A72EBED0B1F5E14F3D08D` | non-reader folio | Exact `non_reader` exclusion. |
| 20 | p5 `original_pipeline_ocr:74` | same type/bbox/text/hashes | non-reader folio duplicate | Exact `non_reader` exclusion. |
| 21 | p5 `raster_pipeline_ocr:80` | `page_number`; bbox `[38,889,70,907]`; `116`; same hashes | non-reader folio duplicate | Exact `non_reader` exclusion. |
| 22 | p5 `raster_pipeline_ocr:70` | `text`; bbox `[168,13,766,42]`; `FEAR'S SHARP LITTLE NFEDLES`; original `E798799101693DA744DAD57DCCF5076062AA0D440536AEB3FBD7085DD7D055AC`; normalized `B3DDD76A1F633D0605E09D3342455C8942F1B850B4213614D4FE11349D2D90BD` | non-reader running header with OCR typo | Exact `non_reader` exclusion. Its semantic role is visually proven running furniture; no generic typo suppression is allowed. |
| 23 | p6 `original_pipeline_txt:91` | `page_number`; bbox `[929,877,961,900]`; `117`; hashes `2AC878B0E2180616993B4B6AA71E61166FDC86C28D47E359D0EE537EB11D46D3` | non-reader folio | Exact `non_reader` exclusion. |
| 24 | p6 `original_pipeline_ocr:91` | same type/bbox/text/hashes | non-reader folio duplicate | Exact `non_reader` exclusion. |
| 25 | p6 `raster_pipeline_ocr:106` | `page_number`; bbox `[929,889,961,907]`; `117`; same hashes | non-reader folio duplicate | Exact `non_reader` exclusion. |
| 26 | p6 `raster_pipeline_ocr:103` | `text`; bbox `[401,15,652,42]`; `DISSOCIATION`; hashes as row 7 | non-reader running header | Exact `non_reader` exclusion. |
| 27 | p6 `raster_pipeline_ocr:104` | `text`; bbox `[126,884,373,910]`; `SENSORYCONFUSTON`; original `7E06894157E4CB9B9AE027297630C2D987B00ABD996368B8911C8E26D21D31B9`; normalized `C3F04DB1CC2BFC3D0632042F45E3BE4EE0430615D7023EC1EC7950CB489F7FC6` | decorative footer text | Exact `decorative` exclusion; visual proves bottom-margin series furniture. |
| 28 | p6 `raster_pipeline_ocr:105` | `text`; bbox `[484,892,561,909]`; `M1-GU`; original `ADA2C975C6E2F3765A7D976AF8CFF636CF31C1F35803515D016408B47EE9EE87`; normalized `32A36F498D21F5D90A0542FF389E37E82950F3E2B101EEC86B1C01725A6A1F52` | decorative footer text | Exact `decorative` exclusion; visual proves footer ornament/furniture. |

Closed totals: 2 `visual_only`, 20 `non_reader`, 2 `decorative`, 2 exact `ocr_artifact`, and 2 visual assertions blocked by positional proof. There are zero true narrative omissions, zero selected ordering defects, and zero selected duplication defects.

## Audit gaps requiring code change

### G1 — visual assertions lose their source position

`kb_creator/scripts/audit_mineru_ai_merge_fidelity.py:336-337` builds `authoritative_stream = joined_anchors + ''.join(assertions)`. Every assertion is appended at page end. Consequently a visually proven cover title before the author (p1) and a drop cap inside the first paragraph (p2) necessarily fail even when Markdown is correct.

Minimal universal remediation: preserve the existing exact assertion contract (page, text hashes, bbox, visual identity), match each assertion to one unique Markdown span, derive its source-order relation from page geometry and adjacent selected units, then merge assertion and selected spans into one monotonic source/Markdown mapping. Fail on ambiguous placement, overlap, reused span, geometry/order contradiction, missing text, or more than one match. Do not weaken the final exact normalized-stream proof.

### G2 — raster OCR artifacts are rejected categorically

`audit_mineru_ai_merge_fidelity.py:309` recognizes only exact normalized containment/concatenation as `included_equivalent`; it does not implement the architecture contract's bounded local one-for-one OCR alternative. At `:320`, every `raster_pipeline_ocr` unit classified `ocr_artifact` is rejected, even when exact visual evidence shows the OCR string is absent and another required view supplies the correct selected text for the same source region. This blocks p3 row 14.

Minimal universal remediation: permit an exact raster `ocr_artifact` disposition only if all of these fail-closed predicates hold: exact unit identity and run-local visual binding; reviewer rationale; the OCR string is visually absent; exactly one overlapping/corresponding required-view unit supplies the visually correct text; that canonical unit is selected or already uniquely proven equivalent in Markdown; and no source-visible characters are lost. Fail on missing/ambiguous counterpart, bbox/page mismatch, unmatched canonical text, or a merely preferable spelling. Keep the current rejection as the default. This is a bounded implementation of the already documented local OCR-equivalence rule, not a bypass.

## Forbidden shortcuts

- Do not relabel either p3 reader heading OCR variant as `non_reader` or `decorative`.
- Do not move p1 title or p2 drop-cap to page end, delete them from Markdown, or change canonical Markdown to OCR corruption.
- Do not add regex, raw-index range, page/type wildcard, threshold, `max_count`, or unused allowlist suppressions.
- Do not blanket-enable raster `ocr_artifact`; the exact visual/counterpart/coverage predicates above are mandatory.
- Do not skip Stage 05, soften `completeness == 1.0`, mutate/reseal run-07, or copy its decisions after authority hashes change.
- Do not treat repeated headers/folios as automatically excluded; every disposition remains an exact reviewed unit.

## Regression and acceptance specification

1. **G1 prefix assertion:** fixture with a visual-only title before a selected author line passes with a unique bbox/order-bound assertion; moving the title after the author fails.
2. **G1 inline assertion:** drop-cap `T` plus selected `he ...` reconstructs `The ...`; appending `T` at page end, overlapping it, or providing two possible Markdown matches fails.
3. **G2 positive:** corrupted raster heading `(... ow and Later)` may be excluded only when the triptych proves `Now`, an exact overlapping required-view canonical unit exists, and that canonical unit is selected/proven once.
4. **G2 negatives:** fail for absent visual binding, wrong page/bbox, two possible counterparts, canonical text absent from Markdown, or use of `ocr_artifact` to discard source-visible reader text.
5. **Exact exclusions:** page folio/running-header/footer fixtures pass only with exact unit identity and matching visual SHA/bytes/path; stale, duplicate, unused, or wildcard-like rows fail.
6. **Dissociation closure:** on the fresh authority, all six pages report `unaccounted_unit_count=0`, `completeness=1.0`, no page/global errors, and `passed=true`; selected recall and precision remain `1.0` where currently `1.0`.
7. **Schema and authority:** audit and reviewed-allowlist schema validation pass; any changed run, comparison, queue, source, contract, visual, decision, or implementation-inventory identity fails closed.
8. **Pipeline consequence:** after code/test closure, a fresh CPU-first run is mandatory because the audit script participates in implementation inventory. Run-07 remains immutable historical evidence and must not be called current under the new implementation.

## Files checked

- Canonical reconstruction plan/status/context and NRI goal governance previously read for this assignment.
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`.
- Run-07 `run.json`, Stage 03 comparison, Stage 04 visual manifest/contact sheets/triptychs and page merge packets, review queue.
- Run-07 decision set and page decisions, especially p1 cover, p2 drop cap, and p3 selected canonical heading.
- `20260915-cpu-first-07-decisions/validation/source-visible-completeness-audit.json`.
- `kb_creator/contracts/ai_merge_fidelity_reviewed_allowlist.v2.schema.json` and `ai_merge_fidelity_audit.v2.schema.json`.
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`, especially lines 309, 320, and 336-337.
- Architecture completeness contract receipt `architect_source_visible_text_completeness_audit_20260915.md`.

## Verdict

**Decision-only remediation is not sufficient.** The source/Markdown content is substantively complete, but G1 and G2 prevent a truthful fail-closed v2 proof. **A fresh CPU run is not needed before the code correction; it is required after that correction** because the implementation inventory changes. Final acceptance remains pending engineering, bounded QA, and independent critic release review.
