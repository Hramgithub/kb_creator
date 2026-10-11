# Innsmouth strict English reconstruction and publication chain

## Result

The canonical repository authority is `accepted_20260830_r2/`. It is the strict
pipeline successor to the user-accepted `r2`, with the remaining decorative
letter-seal crop removed at the same reader-policy layer.

The promoted package contains `MASTER_EN.md`, its path-independent QA sidecar,
the acceptance manifest and exactly 33 assets. Both repository verifiers must
pass before downstream work consumes it.

## Replacement production flow

The repaired production chain is deliberately short:

`source PDF -> MinerU reading extraction -> RECONSTRUCTED_EN -> MASTER_EN`

- `RECONSTRUCTED_EN` retains all `46` source pages, source text/structure and
  all `136` linked source assets, including the source cover. It contains source-backed OCR/layout repairs
  but no reader page suppression, art allowlist or generated navigation.
- `MASTER_EN` applies the approved `0..42` scenario scope, 33-asset reader
  policy, TOC/internal links and 52 stable semantic anchors, then removes
  technical comments from the reader artifact. Exact body duplicates of
  Handouts 1-a and 2 are suppressed, all eight narrative mentions link to the
  appendix, the Handout 2 Keeper note is relocated to that appendix, and its
  two text copies are consolidated. Three seals and two signature crops remain
  in reconstruction evidence but are excluded from the reader master.
  Heading-class anchors must sit directly before their existing headings;
  only `The Innsmouth Terror` is an explicit body target because the source
  has no dedicated heading.
  Stage C also removes the complete `CONTENT WARNINGS` block; this reader
  editorial decision is not deferred to RU, HTML or PDF.
- `freeze/promote` is a separate acceptance operation. It verifies explicit
  user-accepted hashes and exact Stage B provenance, creates the acceptance
  manifest through a staging directory and refuses overwrite.

Historical RU, cleaned EN v6 and the `unit_id`/`source_hash` bridge are not
inputs to any of these stages.

## Rebuild commands

Use explicit paths discovered on the current device; do not write device paths
into tracked manifests.

Build the complete reconstruction package:

```powershell
python scripts/build_innsmouth_reconstructed_en.py `
  <mineru-reading-candidate.md> `
  <new-reconstructed-package>/RECONSTRUCTED_EN.md `
  <new-reconstructed-package>/RECONSTRUCTED_EN.qa.json `
  --reading-assets <mineru-reading-assets> `
  --ocr-assets <pinned-ocr-recovery-assets> `
  --control-pdf <source.pdf>
```

Build the reader master from the complete pinned reconstruction package:

```powershell
python scripts/build_innsmouth_master_en.py `
  --reconstructed-md <reconstructed-package>/RECONSTRUCTED_EN.md `
  --reconstructed-qa <reconstructed-package>/RECONSTRUCTED_EN.qa.json `
  --reconstructed-images <reconstructed-package>/images `
  --target <new-master-en-candidate>
```

The accepted candidate preflights with its two explicit root hashes:

```powershell
python scripts/freeze_innsmouth_master_en_repo_input.py `
  --preflight `
  --candidate <reviewed-master-en-candidate> `
  --expected-master-sha256 31F67A2865BF00A48F197333A162AD56AA0F56061068D3BFD6B564591F9AA3C2 `
  --expected-qa-sha256 3FD5FEA6D704B868447B0F3B431CE5D2F3CC13FB32E7B0CE342A8ED8CF1BFB08
```

Promotion is performed only after explicit user acceptance through the same
gate. The accepted target for this release is
`inputs/innsmouth/master_en/accepted_20260830_r2`:

```powershell
python scripts/freeze_innsmouth_master_en_repo_input.py `
  --promote `
  --candidate <reviewed-master-en-candidate> `
  --target inputs/innsmouth/master_en/accepted_20260830_r2 `
  --expected-master-sha256 31F67A2865BF00A48F197333A162AD56AA0F56061068D3BFD6B564591F9AA3C2 `
  --expected-qa-sha256 3FD5FEA6D704B868447B0F3B431CE5D2F3CC13FB32E7B0CE342A8ED8CF1BFB08 `
  --accepted-on 2026-08-30
```

Re-verify any promoted package using its own acceptance manifest:

```powershell
python scripts/freeze_innsmouth_master_en_repo_input.py `
  --verify `
  --target inputs/innsmouth/master_en/accepted_20260830_r2
```

## Historical accepted flow

The currently frozen Packet 7 package was produced through these historical
bounded successors:

1. MinerU Hybrid/high extraction and PyMuPDF/OCR evidence controls;
2. initial master/package projection;
3. Packet 1 art/caption projection;
4. Packet 2 semantic structure and graph recovery;
5. Packet 3 U02/U06-U12 semantic formatting;
6. U10 paragraph-boundary repair;
7. U11 ornament suppression;
8. Packet 6 residual nonsemantic-art and handout reflow;
9. Packet 6 stable-xref inventory and exact unresolved-row remediation;
10. Packet 7 stable-xref projection and one-shot publication;
11. the user-review successor that preserves punctuation, replaces only the
    printed `page N` token, keeps visible handout numbers and links all major
    TOC groups.

The nested `MASTER_EN.reconstruction.json` records that exact accepted
predecessor chain and operation ledgers. `MASTER_EN.qa.json` records the final
review-correction checks. Detailed architecture, implementation and release
receipts are under
`kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/`.

## Historical checkpoint scripts

The scoped checkpoint retains the two scripts required to verify the currently
accepted historical boundary:

- `scripts/build_innsmouth_master_en_packet7_user_review_successor.py` rebuilds
  the final user-review correction from the exact accepted Packet 7 `_r2_`
  predecessor;
- `scripts/verify_innsmouth_master_en_repo_input.py` independently verifies the
  complete repository package and its canonical inventory digest.

The complete accepted operation lineage is embedded in the nested
`MASTER_EN.reconstruction.json`; the human-readable stage order and the exact
release receipts are retained in this repository. Obsolete rejected script
variants and temporary execution state are deliberately not copied into this
main checkpoint.

The final user-review successor can be reproduced from the immutable Packet 7
`_r2_` predecessor with:

```powershell
python -B scripts/build_innsmouth_master_en_packet7_user_review_successor.py `
  --predecessor <accepted-packet7-r2-directory> `
  --publish `
  --target <new-empty-target>
```

The producer checks exact predecessor identities, builds twice in memory,
validates structural conservation, publishes through a same-parent stage and
refuses an occupied target. The repository copy is then verified independently
by `verify_innsmouth_master_en_repo_input.py`.

They remain evidence and verification tools; they are not the production route
for the strict successor described above.

## Translation boundary

The new delivery chain is strictly:

`promoted accepted MASTER_EN -> MASTER_RU -> accepted HTML -> accepted PDF`

Historical RU v6, old cleaned EN v6 and the old `unit_id`/`source_hash` bridge
are excluded from translation input and prose reuse. No old RU text is stored
in this accepted-input directory.
