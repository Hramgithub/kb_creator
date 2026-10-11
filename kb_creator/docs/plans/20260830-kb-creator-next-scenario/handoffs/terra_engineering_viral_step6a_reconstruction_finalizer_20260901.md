# Terra receipt — Viral Step 6A reconstruction finalizer

- Goal: `20260830-kb-creator-next-scenario`; role: `gpt-5.6-terra` engineering/medium.
- Orchestrator policy owner: `gpt-5.6-sol`; assignment: matched; override: none.
- Result: `READY_FOR_LUNA_EXECUTION`; no acceptance/publication claim.
- Timestamp: 2026-09-01; elapsed: approximately 24 minutes; token use: unavailable.

## Changed files

- `kb_creator/scripts/finalize_mineru_reconstruction.py` — SHA-256 `BA0B2BAA1516739A54F0B84511038394A118928F445685942A170B0AF3101F66`.
- `kb_creator/tests/test_finalize_mineru_reconstruction.py` — SHA-256 `5A9CC1F892C9AD6DC4122CE098C2C5CB6B06452EF306F79EBC39E98EB2F0CE0A`.

The generic CLI is `--contract --source --raw-root --candidate-root --output-root`. It rejects an existing output root, validates source/contract/pages/roles/blocks/assets/handouts, copies the candidate to same-parent staging, creates one selected overlay PDF, and emits the four reconstruction-boundary provenance/QA files. JSON is UTF-8 with two-space indentation and one trailing LF; inventory ordering is forward-slash/codepoint order.

## Marker and verification

The mandatory marker was run successfully exactly once before the first PDF-authoring test command (exit 0, no stdout):

```powershell
C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\plugins\openai-primary-runtime\plugins\pdf\skills\pdf\container_tools\mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 1 --output-format pdf
```

```powershell
python -B -m pytest kb_creator/tests/test_finalize_mineru_reconstruction.py -q
# exit 0: 4 passed in 4.22s
python -B -m py_compile kb_creator/scripts/finalize_mineru_reconstruction.py kb_creator/tests/test_finalize_mineru_reconstruction.py
# exit 0
git diff --check -- kb_creator/scripts/finalize_mineru_reconstruction.py kb_creator/tests/test_finalize_mineru_reconstruction.py
# exit 0
```

Only pytest temporary tiny PDFs were created. No real v3/candidate/package, MinerU, 371/119/490 suite, commit or push was touched. The later executor must not repeat the marker.

## Next command template

```powershell
python -B kb_creator/scripts/finalize_mineru_reconstruction.py --contract <contract.json> --source <retained-source.pdf> --raw-root <frozen-raw-root> --candidate-root <fresh-materialized-v3> --output-root <fresh-reconstruction-package>
```
