# Orchestrator receipt — second real CPU-first run attempt

- Goal: `20260914-dissociation-publication`
- Run id: `20260914-cpu-first-02`
- Run root: `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-02`
- Execution boundary: current local Windows station only
- Source mutation: none
- Result: intentionally aborted as non-reproducible during Stage 02
- Resume/promote status: forbidden

## Evidence identities

- `run.json`: `27972` bytes,
  SHA-256 `738716C08A7EC4725B061F5DBB1F604FA56DF41DA79C475B300510C75E9C422E`
- Stage 01 manifest: `6018` bytes,
  SHA-256 `54E3E5A656F42D0935CBC8E847062CD9D1B0BA4B992A1838CB96705EA1CB0580`
- Stage 02 failure receipt: `1430` bytes,
  SHA-256 `567FE30FE156832E7C8DFC1C24F383EC67CE7A2753C8AC4575D4CC4B238C43A4`,
  seal `A7E1BFCFAA01614222D1B8E2ED4D057EF157C6BA9C68010661BF718116A18DD8`
- sealed first-view receipt: `21006` bytes,
  SHA-256 `36A437B3D5C2EBD32EA0DC09A19895B653B49023B7894F10A215FC6AC82F63EC`

Stage 01 succeeded. The original-PDF `pipeline/txt` view produced ten files
(`8326323` bytes total) and was sealed. The original-PDF `pipeline/ocr` view
produced nine artifact files (`8326480` bytes total) but was not sealed before
the run was aborted. No raster OCR, comparison, review queue, candidate,
acceptance or publication artifact was created.

## Exact failure mode

The repository-local synthetic home remediation worked: both real MinerU views
ran and wrote complete-looking output. A second Windows process-control defect
then appeared. After each `mineru.exe` launcher exited, idle Python descendants
kept the anonymously redirected stdout/stderr handles open, so the wrapper
could not finish its asynchronous reads. The first view advanced only after the
orchestrator stopped the exact idle descendant pair. When the pattern repeated
after the second view, continuing by manual process cleanup would have made the
run non-reproducible. The orchestrator therefore terminated only that view's
exact wrapper/idle descendants. The control plane returned blocked and retained
the partial stage plus sealed `stage-failure.json` in quarantine.

No global process-name kill, source/model edit, GPU, remote host or external API
was used. Post-abort inspection found no remaining process from this run.

## Remediation boundary

Replace inherited anonymous-pipe capture with a deterministic Windows-safe
closed-process mechanism, and clean/verify only the exact process tree created
by the wrapper. Add a synthetic grandchild-holds-pipe regression test and bind
the helper identity into RunSpec. Close independent review before using a new
run id. Do not resume or rewrite this failed run.
