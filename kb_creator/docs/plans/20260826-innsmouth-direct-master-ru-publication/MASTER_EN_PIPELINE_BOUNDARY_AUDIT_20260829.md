# Innsmouth MASTER_EN pipeline boundary audit — 2026-08-29

## Decision

The existing English lineage cannot be relabeled as a clean two-stage pipeline.
It mixes source reconstruction with reader-publication decisions before the
accepted `MASTER_EN` boundary.

The repaired pipeline must remain simple and explicit:

`source PDF -> MinerU reading extraction -> RECONSTRUCTED_EN -> MASTER_EN`

- `RECONSTRUCTED_EN` owns faithful source recovery: all source pages, text,
  reading order, headings, tables, stat blocks, handouts, illustrations and
  captions, plus source-backed OCR/layout corrections.
- `MASTER_EN` owns reader/editorial operations: scenario-scope filtering,
  reader-art suppression/deduplication, navigation anchors, TOC links, internal
  page-reference links and other explicitly approved publication policy.
- Technical evidence belongs in QA/manifest sidecars or in the reconstruction
  layer. It must not leak into reader-facing `MASTER_EN`, `MASTER_RU`, HTML or
  PDF.

No translation-unit compiler, historical EN/RU bridge or sentence-alignment
platform is required.

## Frozen evidence identities

| Artifact | Bytes | SHA-256 | Pages | Images | Tables | Headings |
|---|---:|---|---:|---:|---:|---:|
| Source PDF, `The Innsmouth terror_origin.pdf` | 71,369,650 | `5850B26A077390ABFF4A321E754A3709D6148FA4AC7A9F4D63BDBEFF6949B1BB` | 46 | — | — | — |
| MinerU reading candidate | 139,408 | `1504A9C71CA995748E4125B7303C0D3064E588ABB226EBB5AB99A5F5763C993C` | 46 (`0..45`) | 132 | 53 | 121 |
| Practical mixed `MASTER_EN_candidate` | 133,428 | `B34959A3948ECF14D735FEE04C11B492053182B292F5FD997860A250B69C6B18` | 43 (`0..42`) | 124 | 51 | 155 |
| Packet 5b / U11b | 128,319 | `751DE433161C2EA3AD174C8B20E7803130F2462C02DA267E863A2A9EA0004D2F` | 43 (`0..42`) | 38 | 51 | 155 |
| User-accepted Packet 7 successor | 133,032 | `41E84FAA5A247434133D2A3B0A40245C4842C4F906E7D5D117B9353DE05C1D18` | 43 (`0..42`) | 38 | 51 | 155 |

The accepted repository package remains immutable while the replacement
pipeline is built and reviewed.

## What is already reproducible

The preserved historical producer
`build_innsmouth_master_en.py` pins the MinerU reading-candidate and source-PDF
identities and applies explicit source-backed corrections, including OCR fixes,
portrait/card structure recovery, a table title, stat-block line breaks and six
approved recovered assets.

The current main checkpoint additionally contains:

- a deterministic builder for the final Packet 7 user-review successor from
  the exact `_r2_` predecessor;
- an independent verifier for the accepted 41-file repository package.

## Where reconstruction and publication are mixed

| Existing stage | Reconstruction work | Publication work mixed into it |
|---|---|---|
| Practical `MASTER_EN_candidate` builder | OCR corrections, source headings, portrait/card semantics, recovered source art and stat-block fixes | drops source pages `43..45` before a reconstruction boundary exists |
| Packet 1 through Packet 5b | semantic structure recovery, paragraph joins, handout reading-order repair and source-backed text corrections | reduces scenario image links from `124` to `38` through ornament/nonsemantic-art suppression |
| Packet 5b | closest preserved source-text candidate | already lacks pages `43..45` and 86 scenario image references, so it is not a complete reconstruction |
| Packet 7 | stable target graph and exact internal-reference resolution | inserts reader navigation anchors, TOC links and internal page-reference links |
| User-review successor | corrects the accepted navigation defect | remains a reader-publication successor, not source reconstruction |

Therefore Packet 5b is useful evidence and a comparison oracle, but must not be
renamed or accepted as `RECONSTRUCTED_EN`.

## Clean stage contracts

### Stage A — source extraction input

Inputs are identity-pinned:

- source PDF above;
- MinerU Hybrid/high reading candidate above;
- required MinerU content-list/table-control data;
- approved recovered source assets with byte identities.

The source PDF remains immutable. Re-running MinerU is an explicit extraction
operation, not an editorial operation.

### Stage B — RECONSTRUCTED_EN

Required properties:

- all 46 source page markers `0..45` retained in order;
- no scenario/backmatter page suppression;
- source text and source-visible anomalies preserved unless corrected by
  explicit PDF/OCR evidence;
- source reading order, semantic headings, tables, stat blocks, handouts,
  illustrations and captions reconstructed;
- no TOC/navigation anchors or generated page-reference links;
- no reader-art suppression or duplicate-handout suppression;
- technical evidence recorded in a deterministic QA/manifest sidecar;
- a two-build identity check and a complete source-page/image/table inventory.

The base source-backed recovery is expected to add three missing/replacement
illustration references and promote source headings without suppressing input
content. Its R0 structural oracle is therefore `46` pages, `135` image links,
`53` tables and `169` headings; the raw reading extraction itself remains
`46/132/53/121`.

### Stage C — MASTER_EN

Consumes only an accepted `RECONSTRUCTED_EN` identity and applies an explicit,
auditable list of reader/editorial operations:

- select the approved scenario scope (`0..42`) while recording excluded source
  pages rather than losing them upstream;
- apply the approved reader-art suppression/deduplication policy;
- create stable content anchors, TOC navigation and internal page-reference
  links while preserving punctuation and visible handout numbers;
- omit reconstruction-only technical comments from the reader master;
- keep handout-body suppression as a separate future editorial feature unless
  the user explicitly reopens it for this release.

The resulting `MASTER_EN` is separately reviewable and requires explicit user
acceptance before the accepted RU translation is synchronized.

## First bounded implementation slice

1. Restore only the proven base producer behavior needed for source recovery;
   do not import the historical forest of packet/review scripts wholesale.
2. Split the old mixed builder so source-backed corrections can produce a
   full-page `RECONSTRUCTED_EN` candidate without excluding pages `43..45`.
3. Add focused tests proving the full source scope and rejecting page/art
   suppression in the reconstruction stage.
4. Classify and port the already accepted Packet 2–5b text/structure repairs
   into the reconstruction stage while keeping art/page suppression out.
5. Only after reconstruction QA passes, implement the explicit editorial
   projection to `MASTER_EN` and compare its reader content with the currently
   accepted Packet 7 successor.

## Stage B implementation evidence — 2026-08-29

The bounded slice is now implemented without importing the historical packet
script forest. `build_innsmouth_reconstructed_en.py` pins and consumes the
source reading candidate, source PDF, 132 reading assets and OCR recovery
assets; reconstructs all 46 pages; materializes all 135 final linked assets;
and records byte identities for all pages and assets.

Candidate identity and evidence:

- corrected `RECONSTRUCTED_EN.md`: `138388` bytes,
  `72CF965DF27C28D5D3927867E0A08C8655F5A7A117E108716FA84521649A8F13`;
- QA sidecar: `74886` bytes,
  `D8103F92052F86945BABA9E964AE805C435C42AFA19C47E4BD8C59E998DEC106`;
- final asset inventory:
  `421467CBDB51E96D6025EE733EB7E67CB61C6C6F15BA52C2F0DAE248801BE66A`;
- structural oracle: `46/135/53/169`, zero excluded pages and zero missing
  assets;
- focused real-input suite: `13 passed in 3.68s`;
- pages `1..42` match Packet 5b reader text after removal of only declared
  publication differences; page `0` retains the source-visible standalone
  title fragment.

This proves implementation readiness, not independent acceptance. Stage C must
still project and verify the reader master before the English boundary can be
closed.

The first generated `r1` candidate is rejected and must not be promoted: Stage
C retained-art inventory exposed that it still referenced the failed original
Karen crop. The corrected `r2` replaces it with the source-backed clean OCR
crop `497d...`, pins that asset identity, and retains the same structural
oracle. This is a source-reconstruction repair, not reader-art suppression.

The first Stage C projection slice consumed only the corrected Stage B
identity and applies the explicit `0..42` scope plus the accepted 38-asset
reader allowlist. The navigation-free base is `126388` bytes, SHA-256
`6551D2E6367551EB71C41725996C6E52D7C6D7AE67119C0CF5C62502B5B11CE4`,
with structural oracle `43/38/51/155`; normalized content equals Packet 5b and
the clean Karen crop is retained.

Stage C is now implementation-complete. The same bounded producer applies the
accepted navigation policy directly from explicit local constants: 34 leaf and
11 group TOC links, 33 internal `page N` token replacements, one visible
Handout-number link and 50 page-scoped anchor targets. It then strips technical
comments from the reader artifact, validates 79 fragments with zero broken
targets, and materializes the pinned 38-asset inventory.

Corrected strict-pipeline `r2` candidate evidence:

- `MASTER_EN.md`: `130028` bytes,
  `4A3DDE7AC0EA7A6815AE7FE3CAD38062CC828CF5880D549026E99D5496389A50`;
- `MASTER_EN.qa.json`: `14362` bytes,
  `CED340C73D98B889269C915359FEDE44866CA04ED9216474C366BAE8284149CF`;
- 38-asset inventory:
  `C1A9AB2F89650201C91FA74EAB809E16724D0C608534CFBFAA478AEEBA9CAE3A`;
- final structural oracle: `38` image links, `51` tables, `155` headings,
  `50` unique anchors, `79` fragments, zero broken fragments and zero
  technical comments;
- the Fire Station seed retains its closing parenthesis and the Handout 1-b
  reference retains the visible handout number;
- all `765` nonblank reader lines equal the user-accepted Packet 7 successor;
- Stage C verifies the exact Stage B Markdown and QA identities plus all 135
  Stage B assets before projection, then records only logical relative input
  identities; no device-specific path remains in the QA sidecar;
- the reader Markdown is byte-identical to `r1`;
- `freeze_innsmouth_master_en_repo_input.py` preflights explicit user-accepted
  hashes, stages the copy, writes a deterministic acceptance manifest,
  re-verifies the frozen package and refuses overwrite;
- combined real-input and temporary-promotion suite: `21 passed in 4.23s`.

At this checkpoint local implementation was complete but user promotion had
not yet occurred. The earlier independent review in
`CRITIC_EN_PIPELINE_REVIEW_20260829.md` applied only to `r1` and was invalidated
by the package-identity/freeze changes. The corrected `r2` therefore required
fresh review before its later promotion recorded below.

The first independent `r2` review in
`CRITIC_EN_PIPELINE_R2_REVIEW_20260829.md` found one P1: the freeze gate could
accept a caller-pinned but provenance-tampered QA sidecar. Remediation now
hard-compares the exact canonical Stage B Markdown, QA and 135-asset identities
inside `MASTER_EN.qa.json` before creating an acceptance manifest. A negative
test proves that a substituted Stage B inventory is rejected. The full
post-remediation suite is `23 passed in 4.12s`. Independent closure review
appended to the `r2` receipt is `APPROVE`, with no remaining P0/P1/P2 findings
and a canonical rerun at `23 passed in 4.14s`.

The user explicitly accepted `MASTER_EN r2` and authorized promotion, commit
and direct push to `origin/main`. The reviewed gate promoted it to
`inputs/innsmouth/master_en/accepted_20260829/` and immediately re-verified the
acceptance manifest. Repository identity: 41 files, 38 assets, `8085246` total
bytes, inventory SHA-256
`A71F591B39D3DEB6C1EFE60AF48A22B5B779D0CABEDA4FB71FB1EB6F32F7E584`.
Both promoted-package verifiers pass. The unified root-level EN release suite
is `33 passed in 4.47s` with no skips, including the historical Packet 7
compatibility tests.

The open `60% (307/12)` fidelity question is resolved without editorial
normalization: visual inspection of physical source-PDF page 40 (printed page
36) confirms that exact value is printed by the publisher. It remains an
explicit source-visible anomaly in the accepted master.

## Closed boundaries

- Do not mutate the accepted repository package.
- Do not use historical RU, cleaned EN v6 or the `unit_id/source_hash` bridge.
- Do not copy all historical one-off scripts into main.
- Do not call Packet 5b a reconstruction merely because it predates Packet 7.
- Do not start HTML or PDF until the accepted RU candidate is synchronized to
  the promoted MASTER_EN and frozen through its own acceptance gate.
