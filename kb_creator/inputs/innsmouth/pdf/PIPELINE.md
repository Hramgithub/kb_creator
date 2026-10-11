# Innsmouth accepted PDF output pipeline

Run from `kb_creator/`.

## Build the final candidate

```powershell
python -B scripts\build_innsmouth_pdf_from_accepted_html.py
```

The default candidate is
`working/innsmouth_direct_pdf/accepted_20260830_candidate_r6/` and consumes
only `inputs/innsmouth/html/accepted_20260830_r2/`.

## Preflight

```powershell
python -B scripts\freeze_innsmouth_pdf_repo_output.py --preflight
```

## Promote after acceptance

The target must not already exist.

```powershell
python -B scripts\freeze_innsmouth_pdf_repo_output.py --promote
```

## Verify the permanent output

```powershell
python -B scripts\freeze_innsmouth_pdf_repo_output.py --verify
```

Success marker:

`INNSMOUTH_ACCEPTED_PDF_REPO_OUTPUT_OK`

The gate pins the exact PDF and QA identities, accepted HTML provenance,
structural/page counts, front-matter boundaries and the complete 46-page
Poppler render inventory. Promotion is staged and rejects an existing target;
verification rejects missing, changed or extra package files.
