# H5 independent release review receipt v01

- Goal ID: `20261011-model-handoff`; step ID: `H5`.
- Review kind: `release`.
- Role: independent critic; assigned profile `gpt-6-astra`, effort `high`.
- Independently verified runtime model/effort: unavailable; assignment state: `platform-unverified`.
- Participation declaration: I did not implement or materially design the candidate. I inspected evidence and wrote only this receipt; no candidate or implementation edits.
- Orchestrator policy owner: main chat `/root`, `gpt-6-sol` / `medium`. This review does not transfer orchestration ownership.
- Scoped override: none.
- Recommendation: **changes_required**.
- Assignment result: completed; two bounded P2 findings require correction and a new freeze/review. No P0/P1 finding.
- Timestamp: `2026-10-11T18:20:00Z` (UTC, approximate to the minute).
- Elapsed: approximately 3 minutes; exact token use: unavailable.

## Exact candidate and freeze

Candidate base recorded by the orchestrator: `91db0491f3fa0876ab0c44d45151f8006f812d5a`.
Freeze evidence: `../release.md`, frozen at `2026-10-11T18:17:02Z`.
Both file hashes matched the manifest at the start and again at the end of inspection:

| Candidate file | SHA-256 |
| --- | --- |
| `kb_creator/docs/handoff/MODEL_HANDOFF_SUMMARY.md` | `87B2B29BE33D3EB62D86D02C76C708F2C73A98463832256D020BC17D151DD5D1` |
| `kb_creator/docs/handoff/MODEL_HANDOFF_SPEC.md` | `29065236A5A8C29A89CA2170C1163356427C3EFF67B405789C1EE3D68AA247AA` |

Any candidate-byte mutation invalidates this receipt for the changed candidate. Preserve this receipt unchanged; record corrections in a new candidate freeze and successor review receipt.

## Findings and blockers

### R1 — P2: conditionally mutating integrity check labelled strictly read-only

`MODEL_HANDOFF_SPEC.md:393-400` introduces genuinely read-only checks and includes `git lfs fsck` at line 397. The installed command's own help (`git lfs fsck -h`) states: `Corrupted files are moved to ".git/lfs/bad".` Thus this command can mutate the local object store precisely when a fresh checkout has damaged LFS content. H4 v02 correctly closed the earlier `git lfs pull` issue, but the revised blanket read-only label remains inaccurate.

Required correction: separate this integrity/quarantine-capable operation from strictly read-only inspection, explicitly describe its conditional effect, and preserve the initial checkout inspection before materialization or repair. No integrity repair was run by this critic. A wording/block correction is sufficient; no implementation change is requested.

### R2 — P2: reconstruction profile map omits the supported CPU-first branch

`MODEL_HANDOFF_SPEC.md:112-115` presents `pipeline/reconstruction.py` with profile `mineru_three_view_v1` as the reconstruction control plane. That is the legacy run-v1 identity. The supported controller also handles `kb_creator.run_spec.v2`, `.v3`, and `.v4` with profile `mineru_cpu_first_three_view_v1` (`pipeline/mineru_cpu_first.py:13-17`). `reconstruction.py:581-603` requires CPU-first for contract revisions >= 2 and chooses run v4 for contract revision 3. The five-step intake supplies a revision-3 template (`five_step_intake.py:169`), while compatibility templates also remain available. This distinction was explicitly identified in H2 but did not reach the operational specification.

A new model could infer the wrong runtime/schema requirements from this map while preparing the proposed standalone hardening. The six semantic stages are correct and do not resolve the profile ambiguity.

Required correction: identify legacy v1 and CPU-first v2/v3/v4 separately; state that the actual contract/run schema selects the branch. Briefly identify the three required CPU pipeline views and optional CUDA hybrid/VLM views, whose absence needs the documented capability reason. Point to `mineru_cpu_first.py`; do not imply arbitrary fallback or acceptance from unavailable optional tools. This is correction of observed architecture, not a request to redesign it.

## Evidence reviewed and positive conclusions

- Read the complete two candidate documents and verified their exact frozen hashes twice.
- Read this goal's plan, context, release record, H2 architecture receipt, H4 initial QA receipt, and H4 v02 recheck. QA references exist and both earlier H4 findings are addressed as described; R1 above is a distinct remaining command effect.
- Cross-checked README/current status against the completed `20261004-user-docx-review` plan/context/release and latest deliverables index. The candidate correctly separates the completed October goal from superseded active checkpoints, preserves the 239/14/48/38 historical test counts and 367-page evidence as historical, and does not infer human book acceptance.
- Confirmed six DOCX paths exist under `deliverables/latest`; confirmed `kb_creator/working` is absent, so the three corrected successor links cannot be offered as present payloads. The candidate quotes the three historical hashes consistently with the October release record.
- Confirmed absence of top-level translator, the default shared CoC registry, `.tools`, NRI governance/layout files, and root `pyproject.toml`. Source imports confirm the `translator.translator` dependency. H2 supplies the fresh import-failure evidence; this review did not repeat interpreter execution.
- Inspected ordinary five-step v3 schema/stages and final `ready_for_docx_review`, reconstruction stage registry and schema dispatch, publication's ten-stage registry and writer-rejection guards, CLI parser and placeholder `doctor` response. DOCX-only current production, retained historical verification, and non-acceptance state language are otherwise accurately represented.
- Repository and technology maps provide a useful entry point. The bootstrap prompt directs the next model, including the named Claude consumer, to audit before implementation, avoid starting a book, preserve artifacts, and obtain commit/push authority. No claim about availability or capability of that external model is made or verified here.
- The proposed hardening acceptance gates adequately require explicit dependencies, clean-environment checks, immutable inputs, relevant tests, and exact-output text/visual review. They are future work, not completed evidence.

## Files checked

Repository-relative paths below are under `C:/_Hobby/_work/kb_creator`:

- `kb_creator/docs/handoff/MODEL_HANDOFF_SUMMARY.md` (complete).
- `kb_creator/docs/handoff/MODEL_HANDOFF_SPEC.md` (complete).
- `kb_creator/docs/plans/20261011-model-handoff/{plan,context,release}.md`.
- `kb_creator/docs/plans/20261011-model-handoff/handoffs/H2-architect-receipt.md`.
- `kb_creator/docs/plans/20261011-model-handoff/handoffs/H4-qa-receipt.md`.
- `kb_creator/docs/plans/20261011-model-handoff/handoffs/H4-qa-recheck-v02.md`.
- `kb_creator/README.md` (current and immediate historical sections).
- `kb_creator/PROJECT_STATUS.md` (current top/checkpoint).
- `kb_creator/docs/plans/20261004-user-docx-review/{plan,context,release}.md` (completion, exact freeze, QA, scope and invalidation sections).
- `kb_creator/deliverables/latest/README_RU.md` and six DOCX presence/size entries (no visual review of book contents).
- `kb_creator/docs/five-step-usage.md` (revision-3 template and runtime sections).
- `kb_creator/__main__.py` (parser, legacy guard dispatch, doctor).
- `kb_creator/pipeline/five_step.py` (schema, stage map, final state).
- `kb_creator/pipeline/five_step_intake.py` (contract revision template/dispatch).
- `kb_creator/pipeline/five_step_docx.py` (translator dependency).
- `kb_creator/pipeline/reconstruction.py` (stages and profile/schema dispatch).
- `kb_creator/pipeline/mineru_cpu_first.py` (run schemas, profile, view/capability definitions).
- `kb_creator/pipeline/publication.py` (stage registry and writer guards).
- `kb_creator/pipeline/coc_glossary.py` (default external authority path).
- `kb_creator/pipeline/identity.py` (canonical JSON and SHA implementation).
- External policy: `C:/_Hobby/_work/NRI/docs/governance/nri_goal_governance.md` (complete).
- External memory registry: `C:/Users/user/.codex/memories/MEMORY.md` (targeted conventions lookup only; current findings rely on live files/help).

## Declared exclusions and verification limits

The freeze explicitly excludes runtime hardening, restoring corrected DOCX, vendoring translator, supplying glossary/runtimes, broad test execution, starting or accepting a book, commits, and pushes. These exclusions are appropriate for a documentation handoff and were respected. No generated artifact, implementation, canonical plan/context/status/release, or Git state was changed by this critic.

Git identity/count checks using the discovered PATH Git returned `Permission denied` for the sibling standalone repository. Candidate identity was therefore independently verified by SHA-256 manifest; base revision, 3017 tracked-path count, LFS fsck and initial clean state are attributed to the orchestrator's recorded evidence, not a fresh critic Git verification. No permissions bypass was attempted for those optional checks. No broad tests, document rendering, network/model availability check, source-content audit, or independent secret scan was performed; none is represented as a pass.

## Handoff

Main-chat orchestrator should correct only R1/R2, recheck the affected passages against the cited command help/code, freeze the new bytes, and obtain a successor release review. All other inspected handoff boundaries are suitable for transfer. The present candidate is not approved until these two factual corrections are reviewed. Sole changed artifact: this immutable receipt.
