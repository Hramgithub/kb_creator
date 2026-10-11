# H5 independent release recheck receipt v02

- Goal ID: `20261011-model-handoff`; step: `H5`; review_kind: `release`.
- Role: independent critic, assigned `gpt-6-astra` / `high`; independently verified runtime identity/effort: unavailable.
- Participation: I did not implement or materially design either candidate. This receipt is my sole write in this recheck.
- Orchestrator policy owner: main chat `/root`, `gpt-6-sol` / `medium`; ownership unchanged.
- Assignment state: `platform-unverified`; scoped override: none.
- Verdict: **changes_required**. R1 closed; R2 substantially corrected but one directly affected statement remains overbroad; freeze timestamp also needs correction.
- Timestamp: `2026-10-11T18:25:00Z`, approximate to the minute. Elapsed: approximately 2 minutes. Exact token use: unavailable.
- Assignment state/result: bounded review completed; await successor freeze for remaining corrections.

## Candidate identity and freeze evidence

Read `../release.md` v02 and independently computed both SHA-256 values. They matched:

| File | SHA-256 |
| --- | --- |
| `kb_creator/docs/handoff/MODEL_HANDOFF_SUMMARY.md` | `87B2B29BE33D3EB62D86D02C76C708F2C73A98463832256D020BC17D151DD5D1` |
| `kb_creator/docs/handoff/MODEL_HANDOFF_SPEC.md` | `1891ABF1307A4ABE7461673C4DC8501B94908C833E45934B720C2BD8BBE552F3` |

Recorded baseline remains `91db0491f3fa0876ab0c44d45151f8006f812d5a`; no fresh Git verification in this bounded recheck. The v02 release record claims freeze at `2026-10-11T18:54:00Z`. This is future-dated relative to both clock-tool `18:23:52 UTC` and live host `[DateTime]::UtcNow` `2026-10-11T18:24:08.9428578Z`. The release file's observed LastWriteTimeUtc was `18:23:34`. Candidate byte identity is verified, but the declared freeze chronology is inaccurate.

Any candidate mutation invalidates this receipt for changed bytes and requires a new freeze/review. Keep v01/v02 receipts immutable. The orchestrator indicated a v03 freeze will be created; this receipt does not apply to that future candidate.

## Findings and evidence

### R1 — CLOSED

The affected bootstrap section now places `git lfs pull` and `git lfs fsck` after the initial checkout/CLI inspection. It explicitly says pull writes working-tree content and fsck can move a corrupt object to `.git/lfs/bad`. Fresh `git lfs fsck -h` confirms that conditional move. The initial block no longer promises universal read-only behavior. No regression found in the directly adjacent `doctor` limitation or retired-writer guidance.

### R2 — P2, PARTIALLY CLOSED

Section 4.2 now correctly distinguishes legacy `kb_creator.run_spec.v1` / `mineru_three_view_v1` from CPU-first v2/v3/v4 / `mineru_cpu_first_three_view_v1`. The three required CPU views and optional CUDA hybrid/VLM views agree with `mineru_cpu_first.py:13-105`; supported unavailability reasons are bounded. `reconstruction.py:581-603` confirms revision >=2 requires CPU-first and revision3 chooses run schema v4. Six-stage sequencing remains accurate.

However, the new unqualified statement that current five-step intake creates contract revision3 should identify the revision3 template/selection. `prepare_intake` writes the compatibility `intake-submission.template.json` from a base contract without revision3 (`five_step_intake.py:147-164`) and additionally provides the revision3 template (`:165` onward). The handoff should not imply every current intake uses revision3. State that the revision3 template is available and selects CPU-first v4 when chosen; retain the actual contract/schema/profile selection rule already present. This is a bounded wording correction, not an implementation request.

### F1 — P2, freeze chronology metadata

Correct the future-dated v02 freeze timestamp, using actual recorded UTC time for the successor freeze. This observation is directly within the required freeze-evidence check. No candidate content change is required by F1 itself.

## Files checked and inherited evidence

- `kb_creator/docs/plans/20261011-model-handoff/{plan,context,release}.md`.
- Both `kb_creator/docs/handoff/MODEL_HANDOFF_*.md` by SHA-256; specification sections 4.2 and 12 plus neighboring text inspected directly.
- `kb_creator/docs/plans/20261011-model-handoff/handoffs/H5-release-critic-v01.md`, identity/findings and review boundaries.
- `kb_creator/pipeline/five_step_intake.py`, `prepare_intake` template creation.
- `kb_creator/pipeline/reconstruction.py`, contract-revision/profile/schema dispatch.
- `kb_creator/pipeline/mineru_cpu_first.py`, schemas/profile/view plan/unavailability reasons.
- Installed `git lfs fsck -h` output; live UTC clock and release-file metadata.

The broader factual review and QA references remain those captured in H5 v01: H2 architecture, H4 initial QA and H4 v02 recheck. They were not rerun or extended here. The summary hash is unchanged from v01. This assignment only rechecks prior findings and directly affected passages; no broad code audit, build, tests, rendering, runtime restoration, Git mutation, or model-availability check was performed.

## Scope, limitations, and next action

Declared exclusions remain runtime hardening, corrected-DOCX restoration, translator vendoring, supplying dependencies/registry, broad tests, starting/accepting books, commit, and push. This is a document handoff release decision only, not code production readiness or human book acceptance. Orchestrator should finalize the bounded wording/time corrections, freeze v03, and request a narrow successor check. No permission expansion or implementation ownership is implied.
