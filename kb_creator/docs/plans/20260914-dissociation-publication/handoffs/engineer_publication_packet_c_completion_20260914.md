# Engineer handoff — neutral publication Packet C completion

Date: 2026-09-14  
Role: engineering, user-scoped `gpt-5.6-sol` / `high`  
Scope: reusable neutral control plane and synthetic fixtures only; no live Dissociation run, acceptance, release, install, commit, or push

## Result

Packet C implementation is complete for independent implementation review. The
public control plane now exposes one fixed, closed ten-stage registry. Every
`run` or `resume` invocation can publish at most one stage, preserves all six
explicit user acceptance gates, and can reach only
`candidate_for_release_review` after the copied offline verifier succeeds.
Nothing in this packet records real user acceptance or claims release.

## Completed control semantics

- `PublicationStageInvocation` gives a reviewed adapter only the current
  run/contract/config/stage and already-validated authority paths. Dynamic
  plugins, config-provided callables, arbitrary shell commands, browser PDF,
  and HTML-to-PDF routes are absent.
- `fixed_publication_adapters()` is exact over the ordered stages 10, 20, 21,
  30, 31, 40, 50, 60, 70, and 71. Stages 10–31 call the Packet B MASTER_EN,
  MASTER_RU, ArtView bundle, and ArtView apply functions. Stage 31 supplies the
  exact Stage 30 candidate manifest as an explicit safe authority; it does not
  copy or link a second manifest.
- Stage 40 invokes only the existing translator HTML CLI adapter and binds the
  accepted MASTER_RU, ArtView decisions/application/effective configuration,
  assets, links, and renderer report.
- Stage 50 invokes the explicitly configured DOCX builder and private
  `TransientBridge` render QA. Its successful retained output contains DOCX,
  PNG, and JSON evidence but no PDF or private bridge residue.
- Stage 60 resolves exactly the accepted Stage 50 DOCX, rejects supplied or
  pre-existing PDF authority, performs a fresh fixed Word COM export, and
  renders every final page through repository `.tools` Poppler into a distinct
  final QA inventory.
- Stage 70 creates a new absent package root and copies exact stable names for
  all five accepted candidates, six acceptance receipts, the complete ArtView
  bundle/decision/application/effective config, source/effective/derived
  configs, source/upstream identities, exactly eight Stage 10–60 manifests,
  implementation and schema snapshots, README, and the stdlib-only verifier.
  The package contains exactly one PDF: the accepted Stage 60 candidate.
- Stage 71 runs the verifier copied inside the package with Python `-I`, checks
  its non-release result, and retains only `offline_verify.json`.
- Public `publication run` and `publication resume` use only the complete fixed
  registry and require explicit Python, Poppler, PowerShell, and Word paths.
  Missing resume authorities fail before the next stage target exists.
- Production tool records are no longer labelled `injected_test`. The exact
  repository Python and Poppler executables plus the allowed system PowerShell
  and Word executables are bound into the portable run identity using their
  SHA-256 identities. A non-injected Stage 60 also validates the closed Word
  export receipt, exact input/output bytes, fixed export arguments, cleanup,
  and actual COM executable path against that bound Word identity. Tool drift
  on resume fails before stage writes. Injected adapters retain the old
  explicit `injected_test` identity only in tests.

## Narrow Packet B integration correction

The real Stage 31 path exposed a mismatch between the run-local Stage 30
manifest and the historical profile-derived candidate location. The authorized
correction adds optional `candidate_manifest_path` authority to ArtView v3
validation/application and their CLIs. The explicit form rejects absolute,
drive-qualified, backslash, traversal, outside-root, and reparse paths; it
requires the exact candidate manifest/bundle identity and exact acceptance
candidate identity. Omitting it preserves the previous v3 profile-derived
behavior and v2 parity. A regression covers the exact Stage 30 path and stale
default mismatch without copy/link workarounds.

## Files completed or narrowly modified

- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/pipeline/__init__.py`
- `kb_creator/__main__.py`
- `kb_creator/scripts/production_docx.py`
- `kb_creator/scripts/export_docx_to_pdf.ps1`
- `kb_creator/scripts/publication_render_qa.py`
- `kb_creator/scripts/verify_production_package.py`
- `kb_creator/scripts/scenario_artview.py`
- `kb_creator/scripts/scenario_artview_apply.py`
- `kb_creator/tests/test_production_docx.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- `kb_creator/tests/test_publication_docx_adapter.py`
- `kb_creator/tests/test_publication_docx_to_pdf.py`
- `kb_creator/tests/test_publication_render_qa.py`
- `kb_creator/tests/test_production_package_verifier.py`
- `kb_creator/tests/test_publication_control_plane.py`
- `kb_creator/tests/test_publication_registry_e2e.py`
- `kb_creator/tests/test_scenario_artview_v3.py`

The earlier `engineer_publication_packet_c_20260914.md` remains a truthful
historical checkpoint; this receipt closes its five enumerated remaining items.

## Verification evidence

All Python tests used repository-local tooling:

```text
C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe
PYTHONPATH=C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI
Poppler=C:\_Hobby\_work\NRI\.tools\poppler\poppler-26.02.0\Library\bin\pdftoppm.exe
```

Focused Packet A/B/C/control, real-registry E2E, and legacy DOCX suite:

```text
56 passed, 2 skipped, 14 subtests passed in 136.71s
```

The two skips are host-conditional and explicit: Windows denied creation of a
symlink/reparse adversarial fixture, and Word COM activation from this Codex
logon remains unavailable with `0x80070520`. Word itself exists at
`C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE`. Non-skippable
DOCX-only lineage, fixed export arguments, cleanup on injected failure,
all-page Poppler render, and direct-route rejection tests pass.

Additional fixed-registry targeted evidence after tool-identity hardening:

```text
4 passed, 19 deselected in 20.96s
5 passed in 17.51s
7 passed, 1 host-conditional skip in 23.78s
```

The full synthetic ten-stage E2E uses actual Packet B functions, actual
publication adapter wrappers, actual Poppler rendering, actual package assembly,
and the copied isolated verifier. Only the legacy HTML renderer process and Word
COM export boundary are injected. It asserts every gate stop, absence of Stage
50 PDF, exactly one packaged Stage 60 PDF, all ten manifests, and no acceptance
or release inference. It also proves production tool drift blocks before the
next output.

Legacy ArtView v2 accessibility check:

```text
9 passed, 1 environment-bound failure in 0.86s
```

The single failure is the unchanged real Viral fixture test because
`kb_creator/inputs/viral/artview/review_checkpoint_20260909/candidate/candidate_manifest.json`
is absent. Packet C does not weaken or synthesize that historical input.

Static checks:

- Python `py_compile`: pass for publication control/adapters/CLI, ArtView v3
  integration, DOCX builder, render QA, and package verifier.
- PowerShell AST parse: pass for `export_docx_to_pdf.ps1`.
- Repository `git diff --check`: pass; only pre-existing LF/CRLF warnings were
  reported.

## Remaining review risks

- A successful live Word COM export cannot be claimed on this logon. The host
  smoke remains accurately skipped until Word can activate in an interactive
  user session. No fallback renderer or direct PDF route was introduced.
- The legacy real Viral ArtView fixture remains unavailable locally. Its nine
  environment-independent v2 tests pass; the missing immutable fixture must be
  restored separately if that historical integration test is required.
- This is implementation evidence, not the independent critic release review.
  Dissociation remains unrun and all real acceptance gates remain pending.
