# Number 7 Dream reconstruction context

## Objective and boundary

Reconstruct `Number 7 Dream` from the immutable user-supplied PDF through the neutral KB Creator reconstruction control plane. This goal ends at a fidelity-audited reconstruction candidate and user handoff. It does not infer acceptance or begin publication.

## Accepted decisions and constraints

- Source PDF remains outside the repository and read-only.
- Scenario ID is `number-7-dream`; title is `Number 7 Dream`.
- Source identity is `2915268` bytes, SHA-256 `C03AD05644C5B7438E4FAB750557EB8098E637492242D21969C5C4110FBF97D0`.
- The document has 26 US Letter pages, all unrotated with identical MediaBox and CropBox (`612 x 792` points).
- Scope covers every source page.
- Required numbered player handouts: 5. Pregenerated characters are a scenario topology fact captured in the page roles and goal DoD, while the v1 contract schema has no separate pregen-count field.
- Mandatory evidence views are MinerU text, MinerU OCR on the source PDF, and MinerU OCR on a raster derivative. Optional CUDA providers may be skipped only through their capability receipts.
- Comparison, decisions, audit evidence, and candidates are run-local. Visual-priority and AI merge decisions are not source truth or user acceptance.

## Completed evidence

- Read applicable repository governance, KB Creator README/status, reconstruction skill, PDF skill, reviewed scenario-contract architecture, and prior Dissociation execution context.
- Read-only source reconnaissance completed with bundled `pypdf`, `pdfplumber`, and Poppler rendering.
- Full-page contact-sheet inspection confirms cover (1), credits/contents (2-3), scenario body (4-17), character statistics (18), five numbered handouts (19-20), and six pregenerated player characters (21-26).
- Text-bearing source layer exists on all pages; pages with maps, portraits, full-page art, or handout facsimiles require visual preservation.

## Completed reconstruction state

Fresh replay root `20260917-cpu-replay-05` contains sealed Stages 01-06. Reviewed decision set v12 closes all 26 page decisions. Stage 05 passes with completeness `1.0` and no errors; Stage 06 materializes `RECONSTRUCTED_EN.md`, 26 per-page Markdown files, and 29 unique identity-checked assets with `acceptance_inferred=false`. Failed or superseded replay roots remain immutable diagnostic evidence.

## Blockers

None inside the reconstruction scope. The prior 302-character Poppler input-path failure, reviewed OCR-equivalence limitation, literal `sup`/`sub` normalization, and two visually confirmed title-to-text conflicts are closed by tested, independently reviewed, fail-closed changes. The Stage 01-04 `result.json` remains `needs_review` by schema; the separate replay-resume result is the authority for `candidate_ready_for_reconstruction_qa`.

## Next action

Present the audited candidate and QA receipt for user reconstruction review. Do not infer acceptance or start translation/publication without a new explicit instruction.
