# Viral user-review remediation architecture receipt

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `7-user-review-remediation-architecture`
- Contributor role: `nri-architect`
- Requested model / effort: repository profile `gpt-5.6-sol` / `high`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `matched`
- Scoped override: `none`
- Timestamp: `2026-09-02T23:41:37+03:00`
- Elapsed time: approximately `00:56:00`
- Token use: `unavailable`
- Result: `READY_FOR_REMEDIATION_IMPLEMENTATION`

## Scope and non-mutation statement

This receipt turns the completed Viral user-review registry into an executable
remediation contract for a successor `MASTER_EN`. It identifies the earliest
failing layer, separates current Step 7 work from later Step 8A binary choice,
defines exact implementation ownership, and supplies acceptance gates.

No code, test, config, source reconstruction, candidate, plan, context,
registry, Git index, commit or remote state was changed. This immutable receipt
is the only file written by this assignment. Orchestration ownership remains
with the main `gpt-5.6-sol` / `medium` orchestrator.

## Authoritative evidence checked

- Canonical goal state: `plan.md` and `context.md`.
- Assignment packet:
  `sol_orchestrator_viral_user_review_remediation_architecture_assignment_20260902.md`.
- Complete registry: `USER_REVIEW_TYPICAL_PROBLEMS_20260902.md`, including
  OUT-001 through OUT-026, PROC-001 through PROC-026, the final user decisions,
  the semantic-template hypothesis and Step 8A policy.
- Accepted reconstruction v4: all 124 pages remain frozen under
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/`;
  its accepted inventory SHA-256 is
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Frozen working and reference configs are byte-identical, each SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`:
  `kb_creator/working/viral/master_en/publication_config_v1.json` and
  `kb_creator/reference/viral/master_en/publication_config_v1.json`.
- Current reusable seams were inspected in the scenario builder, independent
  verifier, visual-QA generator, three-view comparison, merge materializer,
  reconstruction finalizer and their focused tests.

## Architectural decision

The successor is a new publication-contract version over immutable
reconstruction v4. It must not repair generated Markdown or rewrite accepted
evidence. The remediation has two compatible lanes:

1. **Current Viral publication lane.** A new, closed `v2` publication config
   declares confirmed semantic units, source-ordered events, reader exclusions,
   exact source-backed text recovery, visual ownership and provisional binaries.
   The reusable builder serializes those declarations into a new candidate.
2. **Reusable upstream prevention lane.** The three-view adapter preserves raw
   semantic evidence; the merge materializer rejects unresolved semantic
   duplication/downgrade; the reconstruction finalizer rejects malformed EOL.
   These guards prevent the same defects on later scenarios but do not mutate or
   rebuild Viral reconstruction v4.

The dependency chain is:

```text
frozen reconstruction v4 + immutable source PDF
  -> reviewed semantic-candidate evidence + publication_config_v2.json
  -> v2 preflight
  -> typed source-ordered publication graph
  -> canonical Markdown serializer + provisional reader assets
  -> absent-root atomic candidate build
  -> independent verifier
  -> full visual/structural QA
  -> fresh GPT-5.5/high review
  -> explicit user reading acceptance
  -> MASTER_RU
  -> Step 8A binary-quality decisions
```

### Publication v2 data contract

`kb_creator.master_en_publication.v2` must be accepted alongside the frozen v1
contract; v1 behavior remains regression-tested and byte-policy compatible.
The builder and verifier must not infer Viral cardinalities from constants.
Counts and expected metrics are derived from the closed v2 declaration and
recomputed from output.

The v2 contract adds or makes explicit the following concepts:

- `document.audit_scope`: source PDF and reconstruction pages `1..124`.
- `document.reader_scope`: pages `1..122`, with exact excluded rows `123` and
  `124` carrying disposition `excluded_advertising` and a user-decision reason.
- `hierarchy[].representation`: `heading`, `anchor_only`, or
  `inline_run_in`. Addressability no longer implies an outline heading.
- `hierarchy[].reader_title`, `navigation_label` and an optional closed
  `reviewed_title_transformation`. Without the latter, the normalized complete
  source heading must equal `reader_title`.
- A source-ordered event graph whose nodes are typed `heading`, `text_fragment`,
  `structured_unit`, `asset`, `anchor_only` or `generated_navigation`. Every
  source-derived event carries page, accepted fragment/range identity and a
  stable order key. Parent headings open immediately before their first emitted
  descendant; owner-end dumping is forbidden.
- `structured_content[].target_representation` and exact `contains[]` for
  `callout`, `ordered_list_callout`, `table`, `equipment_card`,
  `creature_statblock`, `inline_run_in`, `physical_page_pair` and
  `full_page_map`. Source scope and target representation are separate.
- `assets[].reader_value`, `assets[].placement`,
  `assets[].duplication_resolution` and `assets[].quality_stage`.
  Placement binds before/after an exact event or inside a physical unit, not
  merely to an owner. `platform_logo`, `promotional_badge`, typographic residue
  and child crops default to evidence-only.
- `source_recoveries[]` for the exceptional source-proven lexical recovery
  `Cursed Plague Zombies`. It must bind exact visible text to source page 66,
  a reviewed PDF region/native-text identity and the containing Reliquae card.
  It is emitted by the builder with provenance operation
  `source_backed_recovery`; it is not an editorial rename or hand patch.
- Typed serialization. EOL and spacing are normalized while serializing nodes,
  not by a final global regex. Pipe tables and blockquotes are serialized as
  atomic constructs; literal/fenced content is never whitespace-normalized.
- Generated TOC provenance operation
  `generated_navigation_replaces_source_toc`; the source TOC remains in the
  124-page audit layer but is not duplicated in the reader.

## Closure matrix: output and presentation records

| ID | Disposition | Earliest failing layer | Required closure and regression evidence |
| --- | --- | --- | --- |
| OUT-001 | Accepted review aid; not a reader defect | Review/handoff presentation | Keep `MASTER_EN.md` clean. Generate a non-candidate `MASTER_EN_REVIEW.md` or review HTML from provenance with visible page markers. Prove its master hash binding and that candidate inventory excludes it. |
| OUT-002 | `ACCEPTED_DESIGN` | Transformation provenance | Retain generated clickable navigation. Record `generated_navigation_replaces_source_toc`, source page 5 identity and zero reader duplication; do not restore authorial page numbers to the new TOC. |
| OUT-003 | Historical defect; Candidate C remains immutable and incomplete | Candidate lifecycle / retention | Never restore or delete inside Candidate C. Build only absent successor roots via private staging and atomic rename. Before every handoff, rerun verifier and check `exists + bytes + SHA-256 + inventory + asset closure`. Candidate deletion/damage invalidates its receipt. |
| OUT-004 | Process defect | User-facing handoff | A deliverable pointer may be issued only from the just-completed independent verifier result for that exact root/inventory. Record the verified inventory hash and timestamp in the handoff; a stale plan path is insufficient. |
| OUT-005 | Blocking Step 7 defect | Publication event/asset placement | Replace owner-end placement with exact source-event placement. Regress p3 logo before first prose and p31/p32 city then boat immediately before `Prologue`; cover before/between/after fragment, multi-image, section-tail, cross-page and reviewed-relocation cases. |
| OUT-006 | Blocking Step 7 defect; upstream prevention also required | Cross-view semantic conflict, then publication policy | Mark Summary crop evidence-only with resolution `text_wins_crop_evidence_only`; retain the ruined-hall hero. Add high-IoU image/heading conflict validation and reject simultaneous reader emission without an explicit resolution. |
| OUT-007 | Blocking Step 7 defect | Reader-value policy | Classify four platform marks as `platform_logo` and Patron image as `promotional_badge`, all `reader_value:false`; retain prose and reconstruction evidence. Regress that isolated marks are absent while an icon inside a confirmed physical handout remains part of that unit. |
| OUT-008 | Non-blocking future research | Composite-unit proposal | Do not delay successor Viral. Preserve a backlog/candidate-proposer test for the p7 whole web panel and the mutually exclusive parent-versus-children policy; do not synthesize it into the current candidate without review. |
| OUT-009 | Blocking formatting defect; table cases are structural | Reconstruction EOL admission and publication serializer | Future finalizer rejects lone CR/CRCRLF. Current builder reads frozen v4 through canonical typed serialization and emits LF with one ordinary inter-block blank line. Verifier scans raw bytes and Markdown AST; regress LF, CRLF input, malformed CRCRLF, literal preservation and zero broken table adjacency. |
| OUT-010 | Blocking content/structure defect | Publication title replacement policy | Restore all full authorial titles, including seven role qualifiers, two Italian names, Hastalÿk pronunciation, `Welcome to Perla`, and singular `New Spell`. Reject any lexical title drift without a typed reviewed transformation; compact navigation labels never replace reader headings. |
| OUT-011 | Blocking Step 7 defect | Document-level semantic-unit classification | Materialize confirmed character panels and all nine Sight panels as bounded blockquotes/callouts; run-in labels remain inline; true sections remain headings. Candidate-first evidence must cover every repeated label cluster and prove containment, quote closure, outline exclusion and parent-stream return. |
| OUT-012 | `MASTER_EN_ENHANCEMENT`, non-blocking | Missing native-PDF span-style channel | Do not hold successor acceptance on whole-document styling. Preserve ENH-001 as a separately reviewed `native_pdf_typography` pass. Current structural templates may encode only source-confirmed labels needed for table/card readability; no font-name-to-emphasis guess. |
| OUT-013 | Blocking Step 7 defect | Logical-table reconstruction and Markdown serialization | Emit one canonical table each for Rumors, Signs and Portents and Lemon Grove Results, with 10 rows each, one header and no orphan pipe rows. Parse the emitted Markdown and assert table/row/cell counts across page/column continuations. |
| OUT-014 | Blocking Step 7 defect; reusable upstream guard required | Comparison adapter semantic metadata loss | Add peer headings `Santina Maria Salvatore` and `Padre Angelo` under Perla NPCs, owning portrait/prose. Preserve `text_level`, v2/model title evidence and conflicts in comparison output; reject an unexplained title-to-text downgrade. |
| OUT-015 | Blocking Step 7 defect | Semantic-unit container materialization | Emit exactly one bounded callout containing ordered items 1–8; keep `Stream Schedule` and following `Maya` in parent prose. Regress the p27/p28 boundary and absence from outline. |
| OUT-016 | Blocking Step 7 defect; reusable upstream guard required | Heading metadata loss plus incomplete hierarchy | Materialize the complete Hospital floor/wing group family as source-ordered headings under Hospital Locations. Rooms bind to the correct group. Regression covers all peers, not only Cellar. |
| OUT-017 | Blocking Step 7 defect | Addressability/representation model | Emit 2E–2J as six single-paragraph run-in rows with technical anchors, label and xref together; `2I -> 1O`; none is in outline. Audit 2A–2D against the same rule rather than mass-promoting rooms. |
| OUT-018 | Blocking Step 7 defect | Structured contract materialization and scope | Emit one equipment card containing exact title, stat line and footnote only; terminate before `The Devourer is repelled...`. Title is internal to the card, not a free heading; regress exclusion of Keeper's Notes and following prose. |
| OUT-019 | Blocking Step 7 defect | Global source/subtree emission plan | Build one monotonic source-event graph. Assert Encounters -> Outdoor -> Hospital -> Catacomb -> New Rules; New Mythos Horrors immediately precedes its p65 child; singular New Spell precedes Control Reliquae; p68 advice is a bounded callout after the spell and before Player Handouts. |
| OUT-020 | Blocking Step 7 defect | Logical-table materialization | Emit exactly three encounter tables with 12/12/6 rows and one header each. `Cold Spot` is inline cell emphasis/optional anchor, never a heading. Provenance retains continuation pages. |
| OUT-021 | Blocking Step 7 defect | Logical-table materialization | Emit exactly two `D10 | Roll Result` tables with ten rows each; preserve result labels inline and no repeated header/orphan numbered paragraphs. |
| OUT-022 | Blocking Step 7 defect with exact lexical recovery | Statblock container serializer; subtitle absent from v4 | Emit exactly two bounded creature cards: Devourer and Reliquae. Preserve internal title/subtitle, compact characteristics, derived stats, attacks/abilities and nested infection tables. Reliquae spans p66/p67 and receives source-backed `Cursed Plague Zombies`; Plague Monk receives no stat grid. |
| OUT-023 | Blocking Step 7 defect | Addressability/heading conflation | Keep the stable Infection anchor before `Infected Flesh:` but emit no visible `Infection` heading. All three xref families resolve to that anchor and both tables remain inside Reliquae. |
| OUT-024 | Blocking semantic visual-unit defect in Step 7; binary choice in Step 8A | Physical-unit classification | Declare p106/p107 as one ordered two-page map unit and emit provisional deterministic full-page renders plus accessible Key A–V, legend and scale. Existing partial crops become evidence-only. Do not select the final XObject/render binary in Step 7. |
| OUT-025 | Blocking semantic visual-unit defect in Step 7; binary choice in Step 8A | Pregen back-page misclassification | Declare six exact front/back pairs 111/112 through 121/122. Emit a provisional full-page facsimile for each side in source order and separate accessible back text. Silhouette/diagram child crops become evidence-only. |
| OUT-026 | Accepted user scope decision, mandatory | Publication scope/disposition | Audit/reconstruction remains exactly 124 pages; reader scope is exactly 1–122. Pages 123–124 are `excluded_advertising` and contribute zero hierarchy nodes, fragments, xrefs, candidate assets, artview rows, HTML/PDF pages or production payload. |

## Closure matrix: process and pipeline records

| ID | Disposition | Earliest failing layer | Reusable fix and proof |
| --- | --- | --- | --- |
| PROC-009 | Defect | Asset placement QA | Exact event-bound placement plus source-boundary-derived owner; verifier compares source order to emitted order. Tests cover six placement classes and reject internally consistent but source-wrong owners. |
| PROC-010 | Defect | Merge conflict model | Comparison emits image/text overlap conflicts; decision/materializer requires a closed resolution enum. High-IoU heading crop plus heading text cannot both become reader content without reviewed exception. |
| PROC-011 | Defect | Asset publication policy | Closed `reader_value` classification and default-deny publication. Extraction success alone never yields `representation: reader`. |
| PROC-012 | Open non-blocking research | Composite proposal | Keep outside current Terra acceptance. Future proposer records parent bbox, children and mutually exclusive publication choice; p7 is the seed fixture. |
| PROC-013 | Defect | Reconstruction serialization admission | Finalizer rejects malformed EOL for future packages; Step 7 typed serializer safely canonicalizes immutable v4 input. Both builder and verifier independently enforce LF and bounded blanks. |
| PROC-014 | Defect | `replace_heading` contract | Complete source-title fidelity is the default; typed transformation is mandatory for lexical change. Verify selector/source heading against emitted reader title, not only against config title. |
| PROC-015 | Defect | Page-local heading semantics | Document-level semantic candidate/review pass precedes assembly. Confirmed panels own explicit children and close by layout boundary; ambiguous candidates fail closed instead of entering outline. |
| PROC-016 | Non-blocking enhancement gap | Native-PDF typography | Defer ENH-001 to its own task/artifacts. When implemented, separate typography runs from semantic style spans and require exact offset/bbox alignment; p12 is the fixture. |
| PROC-017 | Defect | Logical layout-unit reconstruction | Table declarations carry stable id, ordered cells/rows, source regions and continuation edges. Geometry/content candidates are reviewed before materialization. |
| PROC-018 | Defect | Table serializer/verifier | Canonical serializer emits tables; independent CommonMark AST verification asserts count, rows, cells, adjacency and absence of orphan pipe rows/numbered fallbacks. |
| PROC-019 | Defect | Three-view adapter | Preserve v1 `text_level`, v2/model title evidence and Markdown-heading evidence as typed semantic evidence. Conflicts remain explicit. Regress p25 NPCs, p39 Hospital Cellar and p55 grenade title. |
| PROC-020 | Defect | Merge/finalization review | Selected raw title evidence may end as a heading/card label or reviewed override only. Outline closure compares confirmed candidates to reconstruction/master owners and prevents silent downgrade. |
| PROC-021 | Defect | Publication representation | Split owner, anchor and outline representation. Run-in rooms, table records and Infection use anchors without headings; structural conservation checks one source row to one reader row. |
| PROC-022 | Defect | Structured target representation | `semantic_card`/`semantic_statblock` must materialize or independently prove a bounded target container with exact title, contents and termination. Literal presence alone is insufficient. |
| PROC-023 | Defect | Fragment emission | Replace parent-span heuristic with one globally source-ordered typed event graph and validate monotonicity, contiguous subtrees and parent-heading proximity to first content. |
| PROC-024 | Defect | Physical-unit/art closure | Maps/forms declare exact page set and ordered full-page coverage; verifier checks dimensions/aspect, page closure, accessible legend/key and absence of reader child-crop duplication. |
| PROC-025 | Defect | Pregen classification | Pair detection/contract requires both full pages plus accessible back semantics. Semantic text cannot satisfy visual form closure. Six Viral pairs are exact regressions. |
| PROC-026 | Step 8A-only process improvement | Binary acquisition/finalization | Do not implement in this Step 7 Terra task. Step 8A compares current provisional binary, direct dominant XObject and page-render fallback, hash-binds the user decision and never changes semantic owner/role/page binding. |

## Candidate-first semantic audit required for current Viral

The current registry contains confirmed instances, but full-scope closure still
requires a reproducible high-recall audit rather than manual patching. A reusable
proposer must read accepted page text, existing block coordinates/semantic
evidence and low-resolution PDF geometry, then emit candidates without changing
source or candidate content.

Required evidence root:

`kb_creator/working/viral/master_en/review_evidence/20260902_user_review_remediation_v1/`

Required artifacts:

- `semantic_unit_candidates.json`: ranked candidates with page, bbox/polygon,
  owner, label/template, child source refs, order keys and evidence signals;
- `semantic_unit_review.json`: closed decisions `confirm`, `reject` or adjusted
  boundary, with reviewer and source/config identities;
- `semantic_unit_review.html`: compact flagged crops with context before/after;
- `closure_report.json`: exact coverage of the registry fixtures/template
  families and zero unresolved blocking candidates.

High-confidence candidates combine known repeated label, local normalized gap,
consistent inset margins and background/frame continuity. Repetition alone does
not prove a panel. The minimum closed current families are character quick
references, appearance variants, Keeper's Notes, nine Sight panels, Stream
Schedule, hospital group/run-in rooms, p55 equipment card, p68 advice,
five table families, two creature statblocks, p106/p107 map and six pregen
pairs. OUT-008 p7 composite and PROC-016 typography remain explicitly
non-blocking and need not be confirmed for the successor.

## Exact Terra ownership and ordered implementation slices

One Terra/medium implementation task owns the following paths exclusively. No
parallel contributor may edit any of them until its immutable receipt is
captured. Terra does not build the real successor candidate and does not perform
independent QA or critic review.

### Slice 1 — upstream prevention guards

Owned existing paths:

- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/scripts/finalize_mineru_reconstruction.py`
- `kb_creator/tests/test_finalize_mineru_reconstruction.py`

Work: preserve semantic metadata/conflicts, require explicit duplicate/downgrade
resolution, and reject malformed EOL for future reconstruction. Viral v4 is
read-only and is not rerun.

### Slice 2 — semantic candidate proposer

Owned new paths:

- `kb_creator/scripts/propose_scenario_semantic_units.py`
- `kb_creator/tests/test_propose_scenario_semantic_units.py`

Work: deterministic candidate generation, closed review import and coverage
report. The script may write only an explicitly absent output root and must
never update the source/config/candidate in place.

### Slice 3 — v2 builder and independent verifier

Owned existing paths:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`

Work: dual v1/v2 schema routing, typed event graph, complete-title policy,
structured serializers, exact anchors, relative asset placement, canonical
serialization, dynamic declared metrics, excluded-page conservation and
independent AST/order verification. Builder and verifier must not share the
same parsing/verification implementation.

### Slice 4 — review bundle coverage

Owned existing paths:

- `kb_creator/scripts/build_master_en_visual_qa_bundle.py`
- `kb_creator/tests/test_build_master_en_visual_qa_bundle.py`

Work: remove Viral fixed asset/review/back-cover assumptions, derive counts from
the verified candidate/config, skip excluded pages, and add source-versus-reader
semantic rows for headings, callouts, tables, cards, map/pregen physical units
and asset placement. This is a disposable QA view, not Step 9 HTML publication.

### Slice 5 — Viral v2 policy/evidence

Owned new paths/root:

- `kb_creator/working/viral/master_en/publication_config_v2.json`
- `kb_creator/working/viral/master_en/review_evidence/20260902_user_review_remediation_v1/`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_20260902.md`

Work: derive v2 only from frozen v1, registry decisions, accepted v4 and source
evidence. Encode all blocking rows above; do not copy hidden changes back to v1.
The reference and working v1 files must retain their recorded SHA-256.

The slices are sequential because Slice 5 consumes schemas from Slices 1–4.
The Terra receipt must list exact changed paths, focused results and any
unresolved candidate. Candidate execution remains a later Luna/medium task.

## Successor artifact strategy

Protected immutable roots/files:

- Candidate C:
  `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-c/`;
- retained scratch packages
  `viral-master-en-scratch-20260902-1/` and
  `viral-master-en-scratch-20260902-2/`;
- both frozen `publication_config_v1.json` files;
- accepted reconstruction v4 and its assets/decisions/sidecars;
- immutable source PDF.

New roots/names:

- config: `kb_creator/working/viral/master_en/publication_config_v2.json`;
- semantic evidence:
  `kb_creator/working/viral/master_en/review_evidence/20260902_user_review_remediation_v1/`;
- deterministic scratch builds:
  `kb_creator/working/viral/master_en/candidates/viral-master-en-remediation-scratch-20260902-1/`
  and `...-2/`;
- final successor candidate:
  `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-d/`;
- full visual-QA bundle on this host:
  `C:/Users/BogdanD/.codex/visualizations/2026/08/30/01a05392-3683-7292-b5d5-20ddc8b54a80/viral-master-en-candidate-d-visual-qa-20260902-v1/`.

All roots must be absent before their owning command. Scratch packages are
retained until candidate D acceptance. Candidate D contains no acceptance
sidecar. Acceptance is a separate immutable receipt bound to its inventory.

## Pages 123–124: exact exclusion contract

The v2 `source_disposition` still contains exactly 124 hash-bound audit rows.
Rows 123 and 124 must state:

- `audit_disposition: reconstructed`;
- `publication_disposition: excluded_advertising`;
- `publish_reader_content: false`;
- user decision date `2026-09-02` and a nonempty reason;
- the immutable `page-123.md` / `page-124.md` identity and source-PDF identity;
- no target anchors, reader sub-units or candidate assets.

The reader hierarchy and event graph cover pages 1–122 only. Merchandise, back
cover, Zazzle QR, five p123 crops and the p124 render are absent from Candidate D
and every downstream publication/artview surface. QA reports three independent
counts: `source_pages_audited=124`, `reader_pages=122`,
`excluded_advertising_pages=2`. It is an error to report either excluded page as
missing, and also an error to publish any of its text or binaries.

## Step 7 versus Step 8A boundary

Step 7 owns semantic correctness:

- whether a visual is reader content;
- logical asset id, semantic role, owner, source page/region and exact position;
- map spread and pregen front/back membership/order;
- suppression of logos, typographic residue and duplicate child crops;
- provisional deterministic full-page binaries sufficient to prove physical
  closure in Candidate D.

Step 8A owns binary-quality choice only:

- direct dominant-XObject extraction, deterministic full-page render and any
  explicitly reviewed derived crop/stitched spread;
- image dimensions, colorspace, bytes, resampling/upscale and OCR contamination;
- the user's hash-bound `keep_current`, `replace_with_extracted`,
  `use_full_page`, `keep_both`, `suppress`, `needs_manual_work` or
  `reopen_masters` decision.

Step 8A must not change logical owner, role, placement, page-pair membership or
required/suppressed status. Any such change is `reopen_masters` and returns to
Step 7 followed by a new RU build. Pages 123–124 appear only as skipped audit
rows, never as choices. Direct PDF XObject extraction and final asset selection
are therefore expressly excluded from the Terra remediation task and Candidate
D acceptance.

## Focused test and execution plan

Run from the Viral worktree with the discovered Python on `PATH`. The historical
371/119/490 mutation matrix is not part of this remediation gate.

### Focused construction tests

```powershell
python -B -m pytest -q `
  kb_creator/tests/test_mineru_three_view_tools.py `
  kb_creator/tests/test_materialize_mineru_ai_merge.py `
  kb_creator/tests/test_finalize_mineru_reconstruction.py `
  kb_creator/tests/test_propose_scenario_semantic_units.py `
  kb_creator/tests/test_build_scenario_master_en.py `
  kb_creator/tests/test_verify_scenario_master_en.py `
  kb_creator/tests/test_build_master_en_visual_qa_bundle.py
```

Required focused cases include every regression named in both closure matrices,
v1 compatibility, v2 dynamic counts, malformed inputs, excluded-page leakage,
CommonMark AST renderability and independent-verifier mutations for order,
container bounds, title drift, table rows, anchor-only representation and
asset placement.

### Preflight and two clean scratch builds

```powershell
python -B kb_creator/scripts/build_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v2.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target unused --preflight-only
python -B kb_creator/scripts/verify_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v2.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target unused --preflight-only
python -B kb_creator/scripts/build_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v2.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-remediation-scratch-20260902-1
python -B kb_creator/scripts/verify_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v2.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-remediation-scratch-20260902-1
python -B kb_creator/scripts/build_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v2.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-remediation-scratch-20260902-2
python -B kb_creator/scripts/verify_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v2.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-remediation-scratch-20260902-2
```

The two scratch inventories and every one of their non-inventory file identities
must match. A fresh independent GPT-5.5/high implementation review follows this
evidence and precedes the final build.

### Final real rebuild, verification and visual QA

```powershell
python -B kb_creator/scripts/build_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v2.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-d
python -B kb_creator/scripts/verify_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v2.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-d
python -B kb_creator/scripts/build_master_en_visual_qa_bundle.py --candidate-root kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-d --publication-config kb_creator/working/viral/master_en/publication_config_v2.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --output-root C:/Users/BogdanD/.codex/visualizations/2026/08/30/01a05392-3683-7292-b5d5-20ddc8b54a80/viral-master-en-candidate-d-visual-qa-20260902-v1
```

Luna/high visual QA must compare full pages/reader surfaces for p3, p6–7,
p10–12, p20–22, p25, p27–28, p31–32, p36, p39–45, p55, p58–60, p63–68,
p106–107 and p111–122. It must also inspect the complete outline, all generated
tables/cards/callouts, every reader asset placement, all 39 handouts, absence of
p123/p124 content and the prior p80 handwritten-note risk. It records an
immutable receipt and does not modify Candidate D.

A fresh GPT-5.5/high candidate review then binds the exact Candidate D inventory,
v2 config, verifier output, scratch determinism and visual-QA receipt. Only a
review with no unresolved P0/P1/P2 may return the candidate to the user for
explicit reading acceptance. This architecture receipt is not that release
review.

## Acceptance criteria

Implementation is acceptable only when all of the following are true:

1. Frozen v1 configs retain SHA-256
   `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`;
   Candidate C, retained scratch roots, v4 reconstruction and source PDF are
   unchanged.
2. Every blocking OUT/PROC row above has a v2 config declaration, reusable
   implementation control and focused regression. OUT-001/002/008/012 and
   PROC-012/016 are treated exactly as accepted/deferred, not falsely closed as
   defects. PROC-026 remains Step 8A-only.
3. The final reader is source ordered; full source headings are preserved;
   insets/cards/statblocks/tables are bounded typed units; anchor-only items do
   not pollute outline; no malformed EOL, excessive ordinary blank runs or
   invalid/orphan table syntax remains.
4. All analogous Viral instances found by the candidate-first audit are closed,
   with zero unresolved blocking semantic candidate and no isolated manual
   output edit.
5. Audit evidence proves 124 reconstructed pages while the reader and every
   downstream publication surface contain only pages 1–122. Pages 123–124 have
   the exact `excluded_advertising` disposition and zero leakage.
6. P106/p107 and all six pregen pairs have correct semantic full-page closure;
   partial child crops are not reader duplicates. Their final binary quality is
   explicitly still pending Step 8A.
7. Both scratch builds and Candidate D pass the independent verifier; scratch
   outputs are deterministic; candidate build is atomic into an absent root;
   no acceptance sidecar is written by builder/config.
8. Full visual/structural QA passes, then fresh independent GPT-5.5/high review
   has no unresolved P0/P1/P2. User reading acceptance remains a separate final
   Step 7 gate.

## Risks and controls

- **Schema/count drift:** current scripts hard-code 168/123/107/91 and a
  p124 back cover. v2 derives metrics while preserving a separate strict v1
  route; mutation tests cover both.
- **False semantic grouping:** candidate proposals never materialize without a
  closed review decision. Geometry, repetition and typography are evidence,
  not unilateral truth.
- **Lexical invention:** only the exact p66 source-backed subtitle recovery is
  admitted; all other title changes must preserve source or carry a reviewed
  transformation. Config strings alone are not evidence.
- **Whitespace repair damaging structures:** typed AST serialization precedes
  whitespace policy; tables, blockquotes and literals have construct-specific
  rules.
- **Order proof circularity:** the independent verifier reconstructs expected
  source events from config + frozen pages and does not import builder code.
- **Step 8A leakage:** Step 7 may create provisional full-page renders but may
  not extract/select final XObjects. Stable logical ids isolate later binary
  choice from accepted semantic masters.
- **Stale handoff path:** a fresh verifier result immediately before user-facing
  delivery is mandatory; plan text or an old receipt cannot substitute.

## Blockers and next action

Blockers to architecture completion: none. The non-blocking p7 composite and
native-PDF typography work are intentionally deferred, and final binary image
selection is intentionally assigned to Step 8A.

Next action: the main orchestrator integrates this immutable receipt, creates a
bounded Terra/medium assignment using the exact sequential ownership above, and
keeps candidate execution, independent QA, GPT-5.5/high review and user
acceptance as separate gates.

Completion token: `READY_FOR_REMEDIATION_IMPLEMENTATION`
