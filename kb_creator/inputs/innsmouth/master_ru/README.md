# Innsmouth accepted MASTER_RU input

Canonical Russian publication input:

`accepted_20260830_r2/MASTER_RU.md`

This package was created only by
`scripts/freeze_innsmouth_master_ru_repo_input.py`. It contains the user's
accepted direct Russian translation after the separately approved Hobby World
skill-terminology synchronization, the approved deterministic handout
projection, front-matter projection, the selected 32 reader assets from
canonical `MASTER_EN`, and a deterministic acceptance manifest. The
front-matter projection preserves the recovered source cover, removes the
authors/credits block and follows the Stage C content-warning suppression.

Identity:

- `MASTER_RU.md`: `189302` bytes, SHA-256
  `E9A0AF27BEFE56630E1DBF24CD63EB9C8768706FEAE4C4DB1836E3175D4DED8E`;
- `MASTER_RU.acceptance.json`: `3520` bytes, SHA-256
  `87B3B867895209D8444F5B7E940EE6E14BECE3C79D810F35C92BD5D4FA6ED412`;
- package: `34` files, `32` assets; asset inventory SHA-256
  `849C8238A9165EADC8A796B6A2501C84E9CD220F303CD70E46940FAF6C1E3019`.

The promotion pipeline reproduces the accepted semantic-anchor correction and
the reader-handout policy. It moves exactly 16 existing anchor lines to their
corresponding Russian headings, suppresses the exact body duplicates of
Handouts 1-a and 2, conserves the Handout 2 Keeper note in the appendix, and
links all eight narrative mentions to the appendix. It also excludes three seal
and two signature crops and consolidates Handout 2 to one text block. The
resulting structure is `32` images, `51` tables, `152` headings, `52` anchors and `86` resolved
fragments.

The permanent package must not be assembled or edited manually. Reproduce and
verify it with the commands in `PIPELINE.md`. Verification pins the acceptance
manifest itself and rejects missing, changed, or extra assets.

The downstream publication route is executable and direct:
`scripts/build_innsmouth_html_from_master_ru.py` creates r7f from this exact
frozen input, `freeze_innsmouth_html_repo_input.py` promotes it to
`inputs/innsmouth/html/accepted_20260830_r2/`, and
`build_innsmouth_pdf_from_accepted_html.py` plus
`freeze_innsmouth_pdf_repo_output.py` create and freeze the final PDF. Neither
generated HTML nor PDF is edited by hand.
