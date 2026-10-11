# T7 Stage 40 semantic-span root-cause and remediation specification

## Handoff receipt

- Scope: read-only architecture/root-cause analysis of the run11 Stage 40 failure `semantic statblock span crosses or escapes its declared page`; determine the scenario-neutral authority bridge from accepted reconstruction statblock spans to accepted translated `MASTER_RU`.
- Result: root cause confirmed; a fail-closed source-coordinate -> accepted `MASTER_EN` translation-unit -> accepted `MASTER_RU` projection is specified below. No manual HTML or master edit is valid.
- Files changed: this receipt only.
- Candidate/code/state changes: none.
- Blockers: implementation and a fresh publication run are still required. Run11 cannot be resumed after the implementation inventory changes.
- Next action: implement the closed lineage resolver and corrected Stage 40 projection, add the positive/negative tests below, independently verify them, then create a fresh publication successor and strictly rebind only byte-identical accepted authorities.
- Assignment state: complete.
- Orchestrator policy owner: `/root`, repository-policy orchestrator `gpt-5.6-sol` at medium. Architecture ownership remained bounded to this task; orchestration did not transfer.
- Scoped override: architecture/root-cause only; no edits to code, candidates, acceptance, plan, context, project status, or release artifacts.
- Timestamp: 2026-09-18T13:30:38+03:00.
- Elapsed time: approximately 30 minutes.
- Token use: exact subagent token counter unavailable.

## Executive finding

The failure is not a bad page-18 decision and not translation drift. Stage 40 uses the reconstruction span in the wrong coordinate system and then applies the wrong identity rule:

1. `markdown_span.start_line/end_line` are 1-based inclusive coordinates in one page decision's effective English Markdown. They are not global document lines.
2. `_semantic_html_projection()` applies those numbers directly to the global, translated `MASTER_RU` (`source_lines[start - 1:end]`) and checks the resulting global lines against the declared page.
3. It then compares the SHA-256 of Russian text to the English reconstruction span SHA-256. Even after adding the missing page offset, that comparison must fail for a real translation.

The current exception is therefore only the first visible failure. If the page check were removed, the following `semantic statblock span identity drift` check would still reject the valid Russian candidate.

The correct authority is not page-local line arithmetic alone. The promoted page file and decision prove the source-side span; accepted `MASTER_EN` and the sealed Stage 20 packet bind that span to translation unit identities; the sealed Stage 21 submission and `MASTER_RU.provenance.json` bind the same unit identities to Russian payloads and their deterministic ranges in accepted `MASTER_RU`.

## Concrete live evidence

### Coordinate contract

- `kb_creator/pipeline/semantic_structure.py:49-80` defines the effective page Markdown transformation.
- `kb_creator/pipeline/semantic_structure.py:417-447` validates a decision after applying that transformation.
- `kb_creator/docs/plans/20260917-dream-master-en/handoffs/m2b-handout-entity-architecture.md:62-69` explicitly states that the coordinates belong to the page decision's effective Markdown.
- `kb_creator/README.md:278-280` states that `semantic_span` seals exact first/last reader lines and their hash.

### Faulty consumer

`kb_creator/pipeline/publication_adapters.py:746-793`:

- splits the whole translated master into `source_lines`;
- reads page-local `start_line/end_line` from each reconstruction decision;
- treats them as global `MASTER_RU` indexes;
- hashes translated lines and compares that digest with the English span digest.

The synthetic positive fixture in `kb_creator/tests/test_publication_html_adapter.py:186-224` hides both defects. It calculates `start_line` from the full synthetic Russian master and makes the reconstruction span hash from those same Russian bytes. It does not model page-local reconstruction coordinates or the Stage 20/21 translation lineage.

### Accepted live authority chain

- Reconstruction: `reconstruction/20260918-cpu-replay-21/promotion/reconstruction-upstream-v1`.
- Run11 semantic authority copy: `publication/20260918-publication-11/outputs/10-master-en-candidate/evidence/master_en_authority/upstream`.
- Page decision: `evidence/review/pages/page-018.json`.
- Promoted page: `content/pages/page-018.md`, hash-bound by `RECONSTRUCTION_MANIFEST.json` as `pages/page-018.md`.
- Semantic summary: `content/SEMANTIC_STRUCTURE.json`.
- Accepted `MASTER_EN`: SHA-256 `C3B4F13E3E43B2422704F1A7BCF61A5CF1762191B474FAAE5C4C4243289367AA`.
- Accepted `MASTER_RU`: SHA-256 `904133D5057172C404D28F3BCF2A5E4C578304A59382512D1B31FC56AE0FDAB2`.
- Stage 20 packet: `outputs/20-master-ru-packets/artifacts/packet_manifest.json` and its sealed EN batches/tasks.
- Stage 21 lineage: `outputs/21-master-ru-candidate/artifacts/MASTER_RU.provenance.json`, accepted submission, and sealed RU batches.

The seven page-18 semantic spans map exactly to the current Stage 20 source units:

| Semantic id | Decision-local lines | English span/source hash prefix | Translation unit | Accepted RU global lines |
|---|---:|---|---|---:|
| `stanwick-statblock` | 5-8 | `8A8B3DBF...` | `unit-00225` | 527-530 |
| `elsie-statblock` | 10-15 | `DC67DDB5...` | `unit-00226` | 532-537 |
| `regular-statblock` | 17-20 | `8C022E2A...` | `unit-00227` | 539-542 |
| `heavy-statblock` | 22-26 | `54EC5580...` | `unit-00228` | 544-548 |
| `migo-man-statblock` | 28-33 | `36FDDABE...` | `unit-00229` | 550-555 |
| `migo-statblock` | 35-44 | `3D1FC5E3...` | `unit-00230` | 557-566 |
| `hunting-horror-statblock` | 46-53 | `67DB289F...` | `unit-00231` | 568-575 |

All seven matches are unique in this packet and in declared page 18. Reassembling all 298 validated Russian unit payloads with the Stage 21 assembly rule (`"\n\n"` between units, one terminal LF) reproduces accepted `MASTER_RU` byte-for-byte. Thus the necessary binding already exists; Stage 40 currently ignores it.

## Authority decision: page file and translation provenance have different jobs

This is not an either/or choice.

- The promoted page file, page decision, sidecar, and reconstruction manifest are the authority for **what the English semantic span is**, its page-local position, representation, id, and source digest.
- Accepted `MASTER_EN`, the Stage 20 packet, the Stage 21 submission, and `MASTER_RU.provenance.json` are the authority for **which accepted Russian payload corresponds to that source span**.
- Page-local structural alignment may verify topology, but cannot prove cross-language identity by itself.
- An English digest must never be compared to Russian bytes.
- Heading text, translated vocabulary, fuzzy matching, stat-label recognition, and occurrence guessing are not authorities.

## Fail-closed projection algorithm

### 1. Close the accepted reconstruction source side

1. Resolve the reconstruction inventory, unique reconstruction manifest, semantic sidecar, review decision records, and candidate page records through exact path/bytes/SHA identities under the promoted authority root.
2. Verify manifest and sidecar seals/bindings exactly as the current consumer does.
3. For each top-level `kind=statblock, representation=semantic_span`:
   - apply `semantic_structure.apply_block_boundaries()` to the decision Markdown;
   - slice the declared 1-based inclusive page-local lines;
   - recompute and require the declared English span SHA-256;
   - require the summary sidecar row to agree on id, kind, representation, and span digest;
   - require the hash-bound promoted `pages/page-NNN.md` to contain the same span at the contractually defined page payload offset (currently the exact source-page marker plus blank separator).
4. Reject missing, stale, overlapping, quote-bearing, nested-as-top-level, or duplicate semantic ids before reading translation data.

The promoted page proves the materialized source page. It must not be used as a shortcut to copy its local line numbers into a translated document.

### 2. Close the accepted `MASTER_EN` / Stage 20 source-unit side

1. Resolve `MASTER_EN.provenance.json` and the exact accepted `MASTER_EN` named by the Stage 20 packet. Require its reconstruction inputs to bind the same promoted authority used in step 1.
2. Resolve and validate the packet manifest, `translation_tasks.json`, every EN batch, and their identities/seals.
3. Deterministically reassemble the packet source units and require byte equality with the accepted `MASTER_EN`.
4. Build a page-domain state machine from exact standalone source-page marker units. Reject repeated, decreasing, embedded, translated, or missing markers.
5. Map the page-local reconstruction span through the accepted `MASTER_EN` page segment into the exact minimal consecutive Stage 20 source-unit range. Require:
   - exact page equality;
   - exact source bytes and span digest;
   - complete unit boundaries (no partial translation unit);
   - no page marker inside the range;
   - exactly one possible range.

For run11 each statblock is exactly one unit. The algorithm may support multiple consecutive units only when joining their exact source payloads with the producer's declared separator reproduces the source span byte-for-byte. Ambiguous repeated text or a partial-unit span must fail; it must not be resolved by ordinal guessing.

If a future `MASTER_EN` transform changes a semantic page/span, it needs an explicit hash-bound Stage 10 transition mapping. The current `page_boundary_transitions` ledger is empty and must not be stretched into a general heuristic.

### 3. Close the accepted Stage 21 target side

1. Resolve `MASTER_RU.provenance.json` only if it is hash-bound in the accepted Stage 21 producer manifest/output inventory.
2. Validate the provenance seal and closed shape. Require exact identities for accepted `MASTER_EN`, packet manifest, submission, unit order, and accepted `MASTER_RU`.
3. Resolve the submission and every submitted RU batch through the sealed packet/submission identities. Run the existing submission validation so source hashes, Russian payload hashes, ordering, mechanics, Markdown line classes, hard breaks, links, and page markers are re-proved.
4. Reassemble all validated Russian payloads using the Stage 21 assembly rule and require byte-for-byte equality with accepted `MASTER_RU`.
5. Replace each source-unit range from step 2 with the same ordered unit ids' Russian payloads. Compute target global line/byte ranges from the deterministic assembly ledger, not by searching translated text and not by reusing the page-local numbers.
6. Require all target units to stay in the same declared page domain, preserve their validated line topology, contain no reserved semantic transport, and produce non-overlapping ranges. A unit/range may be claimed by only one top-level statblock.

### 4. Derive HTML transport without mutating authority

1. Keep accepted `MASTER_RU` immutable.
2. Project ArtView assets to a derived source as today, but explicitly prove that the rewrite preserves line count and all source-page marker positions. Differences must be exactly those listed in the asset-rebase ledger.
3. Insert paired `semantic-span-start/end` markers around the target Russian ranges computed in step 3. The markers are derived evidence only.
4. Record a new `kb_creator.html_semantic_projection.v2` evidence document containing, per statblock:
   - semantic id and declared page;
   - decision/page-file/sidecar identities;
   - source local lines and English span SHA;
   - Stage 20 unit ids and source hashes;
   - Stage 21 Russian payload hashes;
   - accepted `MASTER_RU` global target lines/bytes;
   - derived container SHA.
5. Continue the existing neutral DOM gates: exact card count/order/id/page, `section|div.statblock-card`, no `blockquote.statblock-card`, no `review-callout statblock-card`.

If the derived asset projection changes a line inside a semantic statblock, accept it only when the exact rewrite is present in the asset ledger and line count is unchanged; otherwise fail. The live seven spans contain no such rewrite.

## Required implementation surfaces

### `kb_creator/pipeline/publication_adapters.py`

- Replace the global-line/source-hash logic in `_semantic_html_projection`.
- Pass both the immutable accepted `MASTER_RU` and the ArtView-derived Markdown to the projection; do not make the derived source masquerade as the accepted master.
- Resolve the Stage 21 producer/provenance graph from the exact accepted receipt and run root.
- Emit semantic projection evidence v2 with source and target identities.
- Preserve all existing neutral-renderer output gates.

### `kb_creator/scripts/scenario_master_ru.py`

Preferred reusable boundary: expose a read-only, fail-closed lineage resolver that returns validated ordered rows (`unit_id`, page domain, source text/hash, Russian text/hash, source and target assembly ranges) after verifying packet, submission, provenance, and exact master reconstruction. Stage 40 should consume that result rather than duplicate Stage 21 parsing/normalization rules.

The resolver must not edit batches or produce a new translation. If adding this public helper would create an undesirable producer dependency, put the pure shared validation in a small neutral pipeline module and call it from both Stage 21 verification and Stage 40.

### Tests

- `kb_creator/tests/test_publication_html_adapter.py`: replace the invalid same-language/global-coordinate semantic fixture with a real-shaped page-local English reconstruction plus distinct Russian Stage 20/21 lineage.
- `kb_creator/tests/test_scenario_master_ru.py` (or a new narrowly named lineage test module): cover the shared lineage resolver if extracted.
- `kb_creator/tests/test_publication_registry_e2e.py`: add/update a Stage 40 fixture with the required semantic sidecar and translation provenance so the real registry path exercises the contract.

No scenario-specific names, page 18 constants, or hard-coded unit ids belong in production code.

## Required regression matrix

Positive:

1. A two-page fixture whose statblock span is page-local, whose Russian payload differs lexically, and whose final global target lines differ from the local coordinates.
2. The live-shaped seven-statblock case maps in declared order and produces seven neutral cards.
3. An image before a statblock is rebased without moving the mapped range or page marker.
4. A statblock spanning multiple whole consecutive translation units succeeds only when exact source reconstruction and target unit order are proven.

Negative/fail-closed:

1. Treating local line 5 as global line 5 must not produce a binding.
2. Missing/stale promoted page, decision, sidecar, or reconstruction binding.
3. English span SHA/body mismatch.
4. Missing, stale, or unbound `MASTER_EN` provenance/packet/task/EN batch.
5. Span not aligned to complete translation-unit boundaries.
6. Zero or multiple possible unit ranges, including repeated identical payloads.
7. Unit range belongs to another source page or crosses a page marker.
8. Missing/stale Stage 21 producer output binding, `MASTER_RU.provenance`, submission, or RU batch.
9. Source hash, RU payload hash, unit order, mechanics, structure signature, or reconstructed `MASTER_RU` drift.
10. Two semantic ids claim an overlapping target range.
11. Translated target contains quote syntax or reserved semantic markers.
12. ArtView rebase changes line count/page markers or changes a semantic-range line without exact ledger evidence.
13. Renderer returns correct count but wrong semantic id, order, page, or obsolete blockquote/callout container.

## Acceptance criteria

Implementation is ready for a fresh run only when:

- the corrected fixture proves page-local EN -> accepted RU projection with genuinely different languages;
- all negative cases above fail before renderer invocation;
- run11's seven spans resolve to `unit-00225..unit-00231` and accepted RU lines `527-575` with the gaps shown in the evidence table;
- all 298 validated RU payloads reassemble the accepted `MASTER_RU` exactly;
- semantic projection evidence v2 binds both English source and Russian target identities;
- the renderer emits exactly seven neutral statblock sections on source page 18 and no quote/callout statblock;
- frontmatter/source-TOC and Appendix C gates remain unchanged and pass;
- focused adapter, MASTER_RU lineage, renderer, and publication-control tests pass;
- no Stage 50, DOCX, PDF, package, commit, or push occurs.

## Migration and run implications

- Keep run11 and its quarantined Stage 40 attempt as immutable diagnostic evidence.
- Any code/test implementation changes the publication implementation inventory, so run11 must not be resumed.
- Create a fresh publication run under the same accepted replay-21 reconstruction and publication-v2 contract only after implementation/QA closure.
- Reproduce `MASTER_EN` and `MASTER_RU`; carry earlier user acceptance only through the existing strict exact-hash/authority rebind. If bytes or bound authorities differ, return to the corresponding explicit user gate.
- Strictly rebind the 19 ArtView decisions only after complete candidate graph, binary identities, and presentation choices are equivalent; otherwise reopen ArtView review.
- Build Stage 40 once under the fresh implementation identity, perform bounded QA and independent review, and stop at the new HTML acceptance gate.

## Risks and containment

- **False binding by repeated text:** contain with page domain, exact coordinate projection, complete-unit coverage, and unique range requirement.
- **Implicit reliance on equal line counts:** derive target ranges from validated unit assembly; use line topology only as a required invariant, never as sole identity.
- **Producer/verifier circularity:** keep lineage validation pure/read-only and independently assert final evidence in adapter tests and candidate QA.
- **Stage 10 transform drift:** accept only explicitly ledgered transitions; otherwise fail and require a richer upstream mapping artifact.
- **Asset rewrite interference:** require exact rebase ledger and invariant marker/line topology before semantic marker insertion.
- **Historical compatibility:** v1 blockquote statblocks remain readable historical data but are not eligible for this v2 neutral projection.

## Files checked

- `kb_creator/docs/plans/20260918-dream-html-heading-toc/plan.md`
- `kb_creator/docs/plans/20260918-dream-html-heading-toc/context.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/README.md`
- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/pipeline/semantic_structure.py`
- `kb_creator/scripts/scenario_master_ru.py`
- `kb_creator/scripts/verify_scenario_master_ru.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- run11 `run.json`, acceptance receipts, Stage 10/20/21/30/31 artifacts and provenance, submitted EN/RU batches, quarantined Stage 40 derived source
- replay-21 promoted reconstruction inventory, manifest, sidecar, page-018 decision, and page-018 materialized page

## Verification performed

- Recomputed the seven decision span-to-source-unit matches.
- Derived their accepted Russian global ranges from ordered submitted payloads.
- Reassembled all 298 Russian payloads and confirmed exact byte equality with accepted `MASTER_RU`.
- Confirmed the current synthetic adapter fixture uses global same-language coordinates and therefore cannot catch the defect.
- Confirmed no code, candidate, acceptance, canonical state, or release artifact was edited.
