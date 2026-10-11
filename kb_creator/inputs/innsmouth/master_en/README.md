# Innsmouth accepted MASTER_EN input

The canonical English input for the Russian publication pipeline is:

`accepted_20260830_r2/MASTER_EN.md`

The user explicitly accepted and authorized promotion of strict-pipeline
candidate `r2` on `2026-08-29`. The accepted pipeline was then corrected for
the approved reader-handout policy: exact body duplicates of Handouts 1-a and
2 are suppressed, their eight narrative references link to the appendix, and
the Handout 2 Keeper note is conserved in the appendix. Five non-semantic
handout crops (three seals and two signatures) are excluded from the reader
package, while remaining available in `RECONSTRUCTED_EN`. The package was
created only through `freeze_innsmouth_master_en_repo_input.py`; it is
immutable input, not a working-output directory.

The `r2` successor additionally recovers the source cover at Stage B and
removes the complete `CONTENT WARNINGS` section at Stage C. Package identity:

- files: `36` (`MASTER_EN.md`, QA, acceptance manifest and `33` assets);
- total bytes: `9505083`;
- canonical repository inventory SHA-256:
  `D244FBE98E65119826A387F62B4A11ACB331935CB5D157D5656FF9B26A267241`;
- `MASTER_EN.md`: `127769` bytes, SHA-256
  `31F67A2865BF00A48F197333A162AD56AA0F56061068D3BFD6B564591F9AA3C2`;
- `MASTER_EN.qa.json`: `13155` bytes, SHA-256
  `3FD5FEA6D704B868447B0F3B431CE5D2F3CC13FB32E7B0CE342A8ED8CF1BFB08`;
- `MASTER_EN.acceptance.json`: `1320` bytes, SHA-256
  `971A9991E10652FFF482B1045EDBE963B929D84E0E23158E6DF80E3152C5AD9E`;
- accepted 33-asset reader inventory SHA-256:
  `15485C208825A08B8EFA97183606D18BACEBB060AA901DCA0EC3543F922923E2`.

The semantic-anchor correction aligns 16 previously misplaced `nri-h-*`
anchors to their existing section headings. The handout correction adds two
appendix targets, removes all five decorative handout crops, and consolidates
Handout 2 to one appendix block. The final structure is `33` image references, `51`
tables, `153` headings, `52` anchors and `86` resolved fragments, with zero
broken targets and zero technical comments.

Run both repository verifiers from `kb_creator`:

```powershell
python -B scripts/verify_innsmouth_master_en_repo_input.py
python -B scripts/freeze_innsmouth_master_en_repo_input.py `
  --verify `
  --target inputs/innsmouth/master_en/accepted_20260830_r2
```

`packet7_user_review_20260826/` remains unchanged as historical accepted
evidence and comparison authority. It is no longer the production input for a
new translation/render run.

See `PIPELINE.md` for the reproducible strict chain and the boundary for
`accepted MASTER_EN -> MASTER_RU -> HTML -> PDF`.
