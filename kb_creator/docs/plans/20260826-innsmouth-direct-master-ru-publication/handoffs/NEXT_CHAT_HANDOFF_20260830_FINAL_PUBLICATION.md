# Innsmouth final publication handoff — 2026-08-30

## Outcome

The direct publication chain is complete and portable:

`source PDF -> RECONSTRUCTED_EN -> MASTER_EN -> MASTER_RU -> HTML -> PDF`

The user accepted HTML r7f and directed the project to treat successful final
PDF QA as acceptance. The scoped commit containing this handoff is pushed to
`origin/main`. A fresh independent `gpt-5.5` release verdict is still required
before calling the result formally release-approved under repository
governance; this does not invalidate the accepted artifacts or their pipeline.

## Canonical repository packages

1. `kb_creator/inputs/innsmouth/master_en/accepted_20260830_r2/`
   - `MASTER_EN.md`: `127769` bytes;
   - SHA-256:
     `31F67A2865BF00A48F197333A162AD56AA0F56061068D3BFD6B564591F9AA3C2`;
   - 33 assets.
2. `kb_creator/inputs/innsmouth/master_ru/accepted_20260830_r2/`
   - `MASTER_RU.md`: `189302` bytes;
   - SHA-256:
     `E9A0AF27BEFE56630E1DBF24CD63EB9C8768706FEAE4C4DB1836E3175D4DED8E`;
   - 32 assets.
3. `kb_creator/inputs/innsmouth/html/accepted_20260830_r2/`
   - `The_Innsmouth_Terror_RU.html`: `223459` bytes;
   - SHA-256:
     `040C7AF42A76241B3BC280350C0151096CF81E5F9A9194E6F5003B0388E4EF39`;
   - manifest SHA-256:
     `B0ADDD901CCD0DED10D84D331B3F168987070558641D374F13ABC30852E6D7E6`;
   - 32 assets.
4. `kb_creator/inputs/innsmouth/pdf/accepted_20260830_r2/`
   - `The_Innsmouth_Terror_RU.pdf`: `11566429` bytes;
   - SHA-256:
     `8D79F72CB61626B05DE7EC000E140FA0C893C6B3D2DC693A64DF45AF756AE202`;
   - `PDF.acceptance.json`: `1664` bytes, SHA-256
     `3477760E4C49892D54819CBB7D18A57F309533176217C4D43FAA5F6756950105`.

The PDF has 46 A4 pages, 97421 extracted text characters, 32 image XObjects,
88 internal links, zero empty pages and zero findings. Physical pages are:
title 1, introduction 2, TOC 3 and body start 4. Credits and content warnings
are absent. All 46 final page renders are pixel-identical to the accepted r7f
preview renders.

## Rebuild and verification entrypoints

Run from `kb_creator/`:

```powershell
python -B scripts\verify_innsmouth_master_en_repo_input.py `
  --root inputs\innsmouth\master_en\accepted_20260830_r2

python -B scripts\freeze_innsmouth_master_ru_repo_input.py --verify `
  --target inputs\innsmouth\master_ru\accepted_20260830_r2 `
  --glossary docs\terminology\CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md `
  --master-en-root inputs\innsmouth\master_en\accepted_20260830_r2

python -B scripts\freeze_innsmouth_html_repo_input.py --verify `
  --target inputs\innsmouth\html\accepted_20260830_r2 `
  --master-ru-root inputs\innsmouth\master_ru\accepted_20260830_r2

python -B scripts\freeze_innsmouth_pdf_repo_output.py --verify
```

Full commands and invariants are recorded beside each package in its
`README.md` and `PIPELINE.md`.

## Next-PC start

```powershell
git fetch origin
git switch main
git pull --ff-only origin main
```

Then run the four verifiers above. Do not copy from `working/` and do not edit
accepted packages in place.

## Boundaries

- `packet7_user_review_20260826/` is historical comparison evidence.
- Historical RU v6, cleaned EN v6 and the `unit_id/source_hash` bridge are not
  translation inputs.
- `accepted_20260829/` and non-r2 `accepted_20260830/` packages are historical
  predecessors, not current production authorities.
- The local source worktree contained unstaged mutations of old
  `accepted_20260829/` packages. They are deliberately excluded from the
  release commit; `origin/main` keeps those historical packages unchanged.
- Broad `kb_creator/tests` collection still encounters 15 archived
  page-proof/raw-authority tests importing modules absent from this branch.
  The scoped publication suites and all four package verifiers are the current
  applicable evidence.

The next logical task is a new, separately scoped formal release review or a
new publication goal. Do not reopen the completed direct translation chain
without a new user decision.
