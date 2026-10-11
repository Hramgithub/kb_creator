# Terra engineering receipt — Viral Step 6A reconstruction finalizer remediation

## Scope and result

Bounded Terra/medium remediation of the generic finalizer only.  The first
finalizer receipt remains immutable.  The finalizer now fails closed before
publication, recognizes the frozen production Handout marker syntax
`*Handout #<label>*`, closes candidate assets/decisions/overlays, and writes a
portable deterministic candidate identity only after validation succeeds.

## Changed files

- `kb_creator/scripts/finalize_mineru_reconstruction.py`
  - SHA-256: `700758347227379B6B1E2F1670AEC7AB09450A82BCFCBF140E2C3752FFFAFB69`
- `kb_creator/tests/test_finalize_mineru_reconstruction.py`
  - SHA-256: `E6CCA4644642C406C30B45C0FE5C7B21BEE5B6BD5887849BFF57BF71BA4FBF8C`

First immutable receipt:

- `terra_engineering_viral_step6a_reconstruction_finalizer_20260901.md`
  - SHA-256: `6858D353306831E4D6C7EA6851874CAE4EDD26B7FBF705F26A68A61AC06ACE80`

## Finding closure

| Finding | Closure |
| --- | --- |
| Handout inventory | Exact italic marker, full-label closure, player-handout boundary, source-page provenance; `1,2a,2b,3a,3b,4..39`. |
| Assets | Exact declared/actual asset set, content hashes, candidate-relative Markdown image links, no absolute/escaping paths. |
| Portable provenance | Candidate count/bytes, candidate and asset root inventory hashes; ordinal UTF-8 LF inventory algorithm/version; overlay SHA-256/bytes. |
| Decision closure | Exact decision/provenance selected-block and unresolved agreement; frozen comparison page/view/reference resolution; duplicate rejection. |
| Overlays | Exact selection domain and known view; exactly one complete layout PDF per view; reopen and compare selected layout geometry/page order. |
| Fail-closed publication | Existing output refused; validation error leaves no output or temporary stage; success only reports `candidate_ready_for_reconstruction_review`. |
| Readability and gates | One-line implementation replaced by named functions; seven deterministic passing gates are emitted only after all validations pass. |

## Verification/evidence

Marker was **not repeated**. It had already succeeded exactly once in the first
receipt before any PDF-authoring test command for this task chain.

Commands, all exit code 0:

```powershell
python -B -m py_compile kb_creator/scripts/finalize_mineru_reconstruction.py kb_creator/tests/test_finalize_mineru_reconstruction.py
python -B -m pytest kb_creator/tests/test_finalize_mineru_reconstruction.py -q
# 21 passed in 7.54s
git diff --check -- kb_creator/scripts/finalize_mineru_reconstruction.py kb_creator/tests/test_finalize_mineru_reconstruction.py
```

The focused synthetic suite uses only pytest temporary roots and covers success
and deterministic provenance, exact/noncanonical Handout markers, missing or
duplicate page domains, decision/provenance/view/blocker failures, asset
closure, overlay selection/layout failures, role/source identity, output
refusal, and stage cleanup.  No real Viral candidate, raw v3, package, MinerU,
or full verifier suite was read, written, or run.

## Blockers and next action

No engineering blocker.  The orchestrator may arrange a separate bounded
execution/review of the frozen real candidate; this receipt is not a release or
candidate acceptance decision.

## Administration

- Timestamp: 2026-09-01 Europe/Moscow
- Elapsed time: approximately 25 minutes
- Token use: unavailable
- Orchestrator policy owner: main `/root` Sol/orchestrator
- Assignment state: completed, bounded remediation receipt captured
- Scoped override: parent correction message superseded the packet's obsolete
  `## Handout #...` heading with the frozen v2/v3 exact italic marker
  `*Handout #...*`; all other packet requirements remained in force.
