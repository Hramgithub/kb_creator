# Number 7 Dream structural fidelity audit context

## Objective and boundary

Perform a full-scope visual/semantic audit of the 26-page Number 7 Dream
reconstruction candidate, diagnose the shared pipeline gap, implement a
scenario-neutral structural gate, and rebuild immutable successor Stage 05-06
artifacts. The seed defects are the flattened Handout 5 letter on source page
14 and the rasterized/fragmented character stat blocks on source page 18.

## Accepted evidence

- Immutable source PDF SHA-256:
  `C03AD05644C5B7438E4FAB750557EB8098E637492242D21969C5C4110FBF97D0`.
- Candidate root:
  `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-05/outputs/06-materialize-candidate`.
- Source visual root:
  `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-05/outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages`.
- Layout rule: semantic Markdown must preserve visible boundaries before later
  HTML/DOCX/PDF styling.
- Current candidate contains zero Markdown blockquote lines across all 26
  per-page files; page 14 contains one escaped list marker.
- The generic MASTER_EN v3 profile is an exact projection from an accepted
  RECONSTRUCTED_EN and explicitly does not consume the source PDF. It cannot be
  the first layer that discovers source callout/stat-block boundaries.
- Stage 06 currently validates text/asset identity and selected-unit coverage,
  but its decision contract has no typed semantic-container inventory. The v3
  fidelity audit proves lexical/spatial coverage, not preservation of visual
  container semantics.

## Current state

Systemic implementation, sealed replay-15/v26 rebuild, independent QA, and
independent implementation review are complete. Do not infer reconstruction
acceptance or promote to `MASTER_EN` without the downstream acceptance gate.

## Completed evidence

- A1/A2/A3 inspected all `26/26` source/candidate page pairs.
- Integrated result: `30` confirmed structural units on `15` pages, recorded in
  `structural-audit.md`.
- Defect classes: `7` title/heading, `9` handout/callout boundaries, `4` lists,
  `3` quoted speeches, and `7` stat blocks.
- Direct inspection of page 14 source artifacts confirms MinerU exposes the
  letter as ordinary `paragraph`/`text` blocks; no quote/container property is
  carried into the merge packet.
- A5 confirmed that Stage 03 normalization drops most v2/middle list and table
  signals before Stage 04, while the source metadata does not reliably type
  quote, callout, handout, or stat-block containers. The accepted remediation
  is an opt-in decision-set v2 with page-complete visually reviewed structure,
  a v4 Stage 05 audit, and a hash-bound Stage 06 semantic sidecar.
- A6 implemented that opt-in path and deterministic v2 table caption/cell-text
  preservation. The integrated structural/audit/materializer/replay/bundle test
  set passes `276` tests with `1` unrelated skip.
- Fresh run `20260917-cpu-first-06` rebuilt Stages 01-04 from the immutable
  source instead of rebasing stale Stage 03 evidence. It ended at
  `needs_review` with all 26 queue items; all 11 table blocks in each of the
  three required views carry closed caption/cell text and no path/HTML/type
  leakage. Queue SHA-256:
  `4FB392E4CD9198E10D11D8B735BA590F6660D745E2E0149A05BB05F5FA2DFAAF`.
- Fresh replay successor `20260917-cpu-replay-07` is sealed through Stage 04
  and ended at `needs_review`; bridge SHA-256 is
  `6EF1C72433B3D6A01147EA0B57F7C6DABD20565CB17773A12274162549480190`.
  Creating it exposed and closed a replay-contract lag: replay now accepts only
  the closed positive `v2_table_text=true` evidence field and the two declared
  semantic-conflict shapes, while continuing to reject unknown keys or false
  table evidence. Focused replay tests pass `118` tests with `1` skip.
- Full authoring against the fresh Stage 04 evidence now contains `53` typed
  semantic units across all `26` pages plus `6` position-bound visual text
  assertions. The reusable authoring helper supports disjoint fragments,
  exact review-note supersession/appending, selected-purpose overrides,
  reference-only assets, visual-only exclusions, and nested semantic units.
- The materializer now distinguishes title evidence from `v2_table_text`,
  validates ATX headings nested in blockquotes, permits a visually reviewed
  exact blockquote downgrade for false title signals, and resolves
  image/heading conflicts only through an exact selected semantic or visible
  asset role. Focused regressions pass `278` tests with `1` unrelated skip.
- QA of replay-13 exposed four source-confirmed OCR artifacts in the quoted
  handouts. Replay-14 then correctly failed at Stage 05 because the semantic
  validator and the older OCR-equivalence mapping did not yet share reviewed
  corrections. The generic correction ledger now binds one exact source form,
  one reader form, and a visual-review reason while preserving immutable source
  unit identities; both validators consume it. Replay-14 remains failed
  diagnostic evidence and was not resumed or rewritten.
- Fresh replay `20260917-cpu-replay-15` is sealed through Stage 06. Bridge
  SHA-256: `8FF5DD3BCC6C61F17C597DA20B3E16F3C21D756ED5922FB5A19686D25B544EF5`.
  Decision-set v26 SHA-256:
  `89CA64762ECB1049B75BE8B5477591D3B89A225B95CACB19EBE55EB579F1A0E0`.
  Stage 05 v4 audit has `26/26` pages, `53/53` semantic units and zero errors;
  audit SHA-256:
  `20AC37EC5ECDAC589B68C1824921B853BDB6397D57C03771F1713A2B2FA06109`.
  Stage 06 state is `candidate_ready_for_reconstruction_qa`; its
  `RECONSTRUCTED_EN.md` SHA-256 is
  `9A06EB41FD26B80168356335F948E9F41DEEC594771F479296FECB2DD36A9957`
  and its semantic sidecar SHA-256 is
  `1D6DA0B73CAC481F064AEB39C7A9B6DAABB60801058A550511740346A1231515`.
- Orchestrator candidate assertions pass: 26 page files/markers; page 14 one
  blockquote with four nested list items and no visible escaped dash; page 17
  three quote groups; page 18 exactly seven stat-block quote groups, zero
  reader table images, and all four missing-field assertions; page 19 three
  handout groups with four nested items; page 20 one reader handout image. The
  source-confirmed forms `Don't`, `experiments`, `don't`, `hypnotise`,
  `SN13 6PG -`, and `I am` are present and the OCR artifacts are absent.
  Final integrated suite passes `314` tests with `1` unrelated skip.
- Independent A8 QA passes replay-15/v26, all focused page assertions and the
  sealed replay-05/v12 identity check; receipt:
  `handoffs/a8-final-candidate-qa.md`.
- Independent A9 verdict is `APPROVE_IMPLEMENTATION` with no high/medium
  findings. It explicitly does not accept the reconstruction or authorize
  `MASTER_EN`; receipt: `handoffs/a9-independent-implementation-review.md`.

## Blockers

None.

## Next action

If the user accepts this reconstruction candidate, run the separate acceptance
and downstream `MASTER_EN` promotion gates. Otherwise retain replay-15/v26 as
the QA-ready candidate and replay14 as failed diagnostic evidence.
