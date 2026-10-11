# Innsmouth accepted HTML and PDF pipeline

Run from `kb_creator/`.

## Preflight the accepted r7f candidate

```powershell
python -B scripts\freeze_innsmouth_html_repo_input.py --preflight `
  --candidate working\innsmouth_direct_html\accepted_20260830_candidate_r7f `
  --master-ru-root inputs\innsmouth\master_ru\accepted_20260830_r2
```

## Promote after explicit user acceptance

The target must not already exist.

```powershell
python -B scripts\freeze_innsmouth_html_repo_input.py --promote `
  --candidate working\innsmouth_direct_html\accepted_20260830_candidate_r7f `
  --master-ru-root inputs\innsmouth\master_ru\accepted_20260830_r2 `
  --target inputs\innsmouth\html\accepted_20260830_r2 `
  --accepted-on 2026-08-30
```

## Verify the frozen HTML package

```powershell
python -B scripts\freeze_innsmouth_html_repo_input.py --verify `
  --target inputs\innsmouth\html\accepted_20260830_r2 `
  --master-ru-root inputs\innsmouth\master_ru\accepted_20260830_r2
```

Success marker:

`INNSMOUTH_ACCEPTED_HTML_REPO_INPUT_OK`

The verifier is fail-closed on the exact accepted HTML and manifest identities,
accepted RU provenance, all 32 assets, structural counts and presentation
classes. No manual copy or HTML edit is part of this route.

## Build and freeze the final PDF

Run only after the frozen HTML verifier passes:

```powershell
python -B scripts\build_innsmouth_pdf_from_accepted_html.py
```

The builder re-verifies the permanent HTML package, creates a deterministic
print-only derivative, renders through Edge/Chromium with A4/background and
header/footer policy, runs structural and print QA, and renders every page
through Poppler. It does not modify accepted HTML or any upstream master.

Final working candidate:

`working/innsmouth_direct_pdf/accepted_20260830_candidate_r6/The_Innsmouth_Terror_RU.pdf`

It is `11566429` bytes, SHA-256
`8D79F72CB61626B05DE7EC000E140FA0C893C6B3D2DC693A64DF45AF756AE202`.
It has 46 A4 pages, 97421 text characters, 32 image XObjects, 88 internal
links, zero empty pages and zero structural findings. The physical front
matter is title page 1, introduction page 2, complete TOC page 3 and body start
page 4; warnings and credits are absent. All 46 final page renders are
pixel-identical to the accepted r7f preview render set.

The exact final PDF is promoted and verified through
`scripts/freeze_innsmouth_pdf_repo_output.py`; see `../pdf/PIPELINE.md`.

`accepted_20260830/` HTML and PDF r5 remain historical evidence only. They are
superseded by the r7f/r6 publication pair.
