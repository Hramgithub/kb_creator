# Engineer handoff — neutral publication Packet C checkpoint

Date: 2026-09-14  
Role: engineering, user-scoped `gpt-5.6-sol` / `high`  
Scope: synthetic implementation only; no Dissociation source, live run, acceptance, or release mutation

## Result

Packet C is **partially implemented and not production-enabled**. The reusable
HTML, DOCX, Word-export, render-QA, and offline-verification primitives below
are implemented with focused synthetic coverage. The public `publication run`
and `publication resume` commands deliberately remain fail-closed because the
fixed registry does not yet contain proven real adapters for all ten stages and
the real Stage 70 assembler is not implemented. No acceptance or release is
inferred by this checkpoint.

## Implemented semantics

- `production_docx.py` accepts an explicit, closed
  `kb_creator.production_docx_config.v1` document profile for page geometry,
  margins, fonts, sizes, spacing, all six heading styles, footer page numbers,
  and core metadata. Unknown or missing fields fail before output. The
  no-config Viral defaults and existing semantic projection remain available.
- `publication_adapters.py::build_html_candidate` validates the exact accepted
  MASTER_RU candidate plus sealed ArtView decisions, application, effective
  visual config, and source config under the run authority root before deriving
  a stage-local compatibility config. It invokes only
  `translator/translator.py build-production-html`, copies the Stage 31 asset
  tree into the isolated HTML artifact root, validates the renderer report and
  every local `src`/`href`, and records all authority identities. It has no PDF
  callable or PDF subcommand.
- `export_docx_to_pdf.ps1` accepts only contained existing `.docx` input and a
  contained absent `.pdf` target, uses a fresh hidden Word COM instance and the
  fixed all-page `ExportAsFixedFormat` arguments, writes through a unique temp
  file, records Word/input/output/export/cleanup identity for final export, and
  closes/releases Word in `finally`. Transient mode forbids a retained evidence
  receipt and does not disclose a bridge path or hash.
- `publication_render_qa.py` accepts only a repository-local
  `.tools/poppler/**/pdftoppm.exe`, renders every PDF page to stable numbered
  PNGs, and emits page count, dimensions, text/occupancy, near-blank/orphan
  signals, renderer identity, inventory, and a pending human-review index.
  DOCX QA uses the Word adapter only as a private transient bridge and removes
  the bridge/private root before returning success; retained evidence is PNG
  and JSON only.
- `verify_production_package.py` is Python-standard-library-only and can be
  copied into a frozen package. It rejects inventory drift, reparse content,
  missing/extra/duplicate stage and receipt identities, non-closed ArtView
  decisions, broken stage graph/seals/cache keys, run/config/tool/
  implementation/source discontinuity, stale acceptance input identities,
  incorrect acceptance producer/candidate identities, non-DOCX Stage 60
  lineage, and any package with other than one Stage 60 PDF. Success is only
  `candidate_for_release_review` with `release_state=not_reviewed`.
- Publication implementation identity now includes the Packet C adapter and
  scripts, so an older run cannot resume after these implementation changes.

## Files changed in this checkpoint

- `kb_creator/scripts/production_docx.py`
- `kb_creator/scripts/export_docx_to_pdf.ps1`
- `kb_creator/scripts/publication_render_qa.py`
- `kb_creator/scripts/verify_production_package.py`
- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/pipeline/publication.py` (implementation inventory only)
- `kb_creator/pipeline/__init__.py` (exports only)
- `kb_creator/tests/test_production_docx.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- `kb_creator/tests/test_publication_docx_adapter.py`
- `kb_creator/tests/test_publication_docx_to_pdf.py`
- `kb_creator/tests/test_publication_render_qa.py`
- `kb_creator/tests/test_production_package_verifier.py`

## Verification

Interpreter and test dependencies stayed below repository `.tools`:

```text
C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe
PYTHONPATH=C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI
```

Repository production renderer used by tests and recorded in render evidence:

```text
C:\_Hobby\_work\NRI\.tools\poppler\poppler-26.02.0\Library\bin\pdftoppm.exe
```

Focused Packet A/B/C/control and legacy DOCX command:

```text
python -m pytest -q \
  kb_creator/tests/test_publication_contracts.py \
  kb_creator/tests/test_publication_control_plane.py \
  kb_creator/tests/test_scenario_master_ru.py \
  kb_creator/tests/test_scenario_artview_v3.py \
  kb_creator/tests/test_publication_html_adapter.py \
  kb_creator/tests/test_publication_docx_adapter.py \
  kb_creator/tests/test_publication_docx_to_pdf.py \
  kb_creator/tests/test_publication_render_qa.py \
  kb_creator/tests/test_production_package_verifier.py \
  kb_creator/tests/test_production_docx.py
```

Result: **49 passed, 2 skipped, 14 subtests passed** in 106.65 s.

The two skips are host-conditional and explicit:

1. Windows did not permit creation of the reparse/symlink adversarial fixture;
   runtime reparse rejection remains covered by the verifier implementation and
   the existing control-plane tests.
2. Word is installed at
   `C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE`, but COM
   activation from this Codex logon fails with `0x80070520` (logon session not
   available). The smoke test reports that environment capability as a skip;
   the non-skippable DOCX-only, pre-existing-output, fixed-argument, and cleanup
   route tests pass.

Additional legacy ArtView run: **9 passed, 1 environment-bound failure**. The
failure is the pre-existing real Viral fixture test because
`kb_creator/inputs/viral/artview/review_checkpoint_20260909/candidate/candidate_manifest.json`
is absent; no Packet C code is on that v2 path.

Python `py_compile` passed for all changed Python implementation modules.
PowerShell AST parsing passed for `export_docx_to_pdf.ps1`. Scoped
`git diff --check` passed with no output.

## Exact remaining work before Packet C can be called complete

1. Implement and test real control-plane wrappers for the Packet B stages and
   the DOCX/PDF scripts, then construct the fixed ten-stage registry. The
   registry factory must bind the exact per-resume authority paths because the
   present `PublicationStageAdapter.invoke(staging, private)` signature does
   not itself receive authority records.
2. Implement the real Stage 70 stable package assembler: copy exact accepted
   candidates/receipts, all mandatory ArtView/config/code/schema/evidence roles,
   the exact eight upstream manifests, and the copied stdlib verifier into a
   new absent package root; then seal and validate the exact inventory.
3. Implement Stage 71 as execution of the **copied package verifier**, not an
   in-repository import, and retain only its JSON result.
4. Add actual DOCX and PDF adapter invocation-path tests (including injected
   Word failure cleanup) and a synthetic ten-stage E2E that stops at every
   explicit user gate.
5. Only after items 1–4 are green may `kb_creator.__main__` enable public
   `publication run/resume`. The current fail-closed message is intentional.

## Risks

- The HTML adapter's stage-local compatibility derivation is covered with an
  injected renderer and exact path/asset/report checks; a real translator CLI
  smoke still belongs with the complete registry/E2E because a scenario's
  complete legacy presentation config can exercise additional optional output
  fields.
- The Word COM implementation was parsed and route-tested but could not perform
  a successful live export in this host logon. This is an environment
  capability gap, not evidence of successful Word export.
- The standalone offline verifier passes a copied `python -I` synthetic package
  test, but production safety still depends on the unimplemented Stage 70
  assembler producing the exact stable inventory.
