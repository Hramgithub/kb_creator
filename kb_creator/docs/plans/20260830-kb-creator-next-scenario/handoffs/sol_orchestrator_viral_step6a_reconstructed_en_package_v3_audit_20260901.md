# Orchestrator audit — Viral Step 6A reconstructed package v3

## Result

- Goal: `20260830-kb-creator-next-scenario`.
- Owner: main-chat orchestrator (`gpt-5.6-sol`, policy effort `medium`).
- Date: `2026-09-01` Europe/Moscow.
- Result: `READY_FOR_INDEPENDENT_RECONSTRUCTION_REVIEW`.
- This receipt is not reconstruction acceptance, MASTER_EN promotion, user
  reading acceptance or release approval.

## Frozen inputs and implementation

- retained source: 20718150 bytes, 124 Letter pages, SHA-256
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
- v3 decisions: 124 JSON / 589384 bytes; ordered decision-set digest
  `0C44B3B7404CC2FD55B33146609E10A3622C8C45400CEA43E13940CE25F92D7A`;
- v3 content receipt SHA-256
  `179F289C1177F70B4049FF96306611087A6BE20498D9C35755B0A92B31E81E67`;
- materializer SHA-256
  `D632FD2203C1CB68AD01DBD369E7FD530146A5D423F786FDEB64848F0F331076`;
- finalizer SHA-256
  `E943D82F41651A6CBEDDAE7D199B0B755133EFB304D14DD2E2B1770FAF39C367`;
- finalizer focused tests: 22 passed; production-shape receipt SHA-256
  `5FD7C039BFB9B7BE6C903B98BC4FD7E57584CD68C122129B90E3C930BC3A44AE`.

No MinerU view was rerun. The optional 371/119/490 verifier matrix was not run
and is not a reconstruction-content gate.

## V3 successor correction audit

The v3 decisions differ from v2 on exactly 18 pages:

`16,69,70,71,72,73,74,75,76,77,78,79,80,81,83,84,85,86`.

All differences are confined to the `markdown` value; every other JSON key/value
is unchanged. Page 82 and pages 87-124 are byte-identical to v2. Page 16 contains
seven visually proven source-faithful corrections: `aospital` to `Hospital`, two
forms of the deity name to `Hastalÿk`, and four contextual `ae` OCR substitutions
to `He`. All before-forms are absent.

Handout identity is represented consistently as the exact italic line
`*Handout #<label>*`. There are 41 unique physical labels
`1,2a,2b,3a,3b,4..39`; unique numeric ordinals are exactly 1-39. The mapping for
labels 1-18 is pages 69, 70, 71, 72, 73, 74/74, 75/75, 76, 77, 78/78, 79, 80,
81, 83, 84, 85 and 86. Page 82 legitimately contains no numbered identity.

## Real execution

Luna/high ran exactly the frozen materializer and finalizer commands once each.
Execution receipt SHA-256:

`343A4B16236E63C2EBF40EED80CF02CD393C2D77DA13DDE273C98A155E48CD99`.

- materializer: exit 0, empty stderr, 124 pages, 121 assets and 121 unique asset
  bytes;
- finalizer: exit 0, empty stderr, 124 pages and 124 overlay pages;
- PDF create marker had already run successfully once before PDF-writing tests
  and was not repeated.

Fresh candidate:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v3`

- 373 files / 13142501 bytes;
- Python/codepoint ordinal trailing-LF inventory SHA-256
  `B0D74C6560648454DD3B12E02446969A11851BD722B41F0222FFA9DE32121EA1`;
- `RECONSTRUCTED_EN.md`: 346580 bytes, SHA-256
  `5D28F097708CB9D58A5A0D4C72CC93E9985FC7CDB00C22EFDB0A22C9931B79ED`;
- 124/124 decision copies are byte-identical to v3; 124 source markers; no
  unresolved records.

Fresh reconstruction package:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v3`

- 377 files / 41068701 bytes;
- Python/codepoint ordinal trailing-LF inventory SHA-256
  `46E61F5DB9853E795C636147C63230936221F056DE1A9C25B19A4C8DEAEA215E`;
- exactly the 373 candidate-derived paths are byte-identical;
- the only four additional paths are `SELECTED_OVERLAY.pdf`,
  `RECONSTRUCTION_PROVENANCE.json`, `RECONSTRUCTION_QA.json` and
  `RECONSTRUCTION_QA.md`;
- no stage residue, reparse point or extra top-level entry.

The package embeds the retained source identity and contract identity, keeps
the packet-bound fine-grained role and a unique contract role for every page,
retains normalized selected-block provenance, records exact Handout pages and
asset/candidate identities, and reports all seven reconstruction gates as pass
with empty error arrays. Reader-facing `pages/*.md` and `RECONSTRUCTED_EN.md`
contain no asset placeholder. Template placeholders remain only inside copied
decision JSON as expected provenance and are not reader-facing unresolved data.

## Overlay PDF and visual QA

`SELECTED_OVERLAY.pdf`:

- 27696569 bytes;
- SHA-256
  `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB`;
- 124 pages, media box `(0,0,612,792)`, rotation 0;
- selected-view distribution: original hybrid 116, original pipeline/OCR 7,
  raster hybrid 1.

Luna/high render-only visual QA receipt SHA-256:

`BEE706F229F43C7791856B417CCA32252C7D05C39D0BF0132C2B323C5C3CE2B0`.

Poppler rendered all 124 pages at 110 DPI. Every rendered page is an exact pixel
match to the already frozen selected-view PNG (`124/124`, mismatches none).
Direct inspection passed all 31 four-page contact sheets and 15 priority pages,
with no P0/P1/P2 render finding, blank/black/corrupt/clipped page, order defect
or mixed/partial assembly. Poppler emitted missing-display-font warnings for
`Symbol` and `ArialUnicode`, but exact pixel equality proves they introduced no
delta from the selected frozen view.

## Gate conclusion and next action

Machine and bounded visual evidence now close:

1. source identity;
2. 124-page coverage;
3. contract role partition while retaining fine roles;
4. selected-block text/OCR provenance;
5. exact Handout ordinal closure 1-39;
6. asset and reader-link closure;
7. no open blocker;
8. selected overlay page/domain/render integrity.

The package is frozen pending a fresh independent GPT-5.5/high reconstruction
review. Any mutation of decisions, candidate, package, code or bound receipts
invalidates this audit and requires a successor review boundary.
