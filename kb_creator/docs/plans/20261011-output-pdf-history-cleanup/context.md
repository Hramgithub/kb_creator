# Context: generated PDF history cleanup

- Goal ID: `20261011-output-pdf-history-cleanup`
- State: `completed`
- Repository: `https://github.com/Hramgithub/kb_creator.git`
- Old remote baseline: `91db0491f3fa0876ab0c44d45151f8006f812d5a`
- Clean root baseline: `141758c2d7e67acde0f4a9f28b2822379e3f5a18`
- Remote branch: `main`

## Evidence

- The two targets are ordinary Git blobs of 65,261,797 and 64,314,373 bytes.
- They were historical generated results from July/August Innsmouth work.
- Reports and manifests refer to them as historical run evidence; current tests
  do not consume their exact repository paths as binary fixtures.
- A later accepted Innsmouth PDF remains under
  `kb_creator/inputs/innsmouth/pdf/accepted_20260830_r2/`.
- `.gitignore` already excludes these output paths through the default-deny
  allowlist and also contains generic PDF rules; the obsolete files remained
  only because they were already tracked in the source repository.

## Protected scope

- no mutation of `C:\_Hobby\_work\NRI`;
- no removal of reports, manifests, HTML, Markdown, accepted inputs, LFS
  payloads, source code, scripts, tests, or deliverables;
- no remote mutation before QA and independent release review;
- no plain `--force`; publication must use an exact `--force-with-lease` guard.

## Completed

- only the two approved files were removed;
- the one-commit import baseline was rebuilt as `141758c`;
- the cleaned root contains 3015 tracked paths;
- `kb_creator/output/` now contains three tracked non-PDF historical artifacts;
- `pdf_raw/` remains unchanged at five tracked paths.

## Completed result

- independent critic approved exact candidate `ed52f92`;
- fresh fetch confirmed the old remote lease was still `91db049`;
- guarded `--force-with-lease` publication replaced GitHub `main` with the
  cleaned history;
- fresh remote verification confirmed `main` at `ed52f92` before integration
  of this administrative receipt/status delta;
- frozen handoff bytes were not changed after independent approval.
