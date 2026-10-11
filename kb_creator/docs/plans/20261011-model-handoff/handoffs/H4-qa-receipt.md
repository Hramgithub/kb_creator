# H4 bounded QA receipt

- Goal: `20261011-model-handoff`; step: `H4`.
- Role: bounded factual/coverage QA; assigned profile `gpt-6-luna` / `medium`. Actual runtime model/effort: unavailable.
- Orchestrator policy owner: main chat `gpt-6-sol` / `medium`; ownership unchanged.
- Assignment state: `platform-unverified`; scoped override: none.
- Scope: verify only the accepted H4 specification and listed files; no candidate/code repairs and no release decision.
- Result: **changes required before H4 passes**. One P1 finding affects command safety/accuracy; one P2 finding affects repository-count wording. No broad architecture issue found.
- Timestamp: `2026-10-11T18:14:24Z`.
- Elapsed: approximately 8 minutes. Token use: unavailable.

## Findings

### P1 — “read-only” command block mutates checkout

`kb_creator/docs/handoff/MODEL_HANDOFF_SPEC.md:391-400` labels the entire block “Минимальные read-only проверки” but includes `git lfs pull` at line 397. `git lfs pull` downloads/materializes LFS content in the working tree, so the block is not read-only and may change checkout files. Separate it into a clearly labeled fetch/materialization step and genuinely read-only checks, or remove it from the read-only block. This also matters because the bootstrap first asks the new model to verify that no unrelated changes exist (`:378`) before running the mutating command.

### P2 — import count terminology is ambiguous

`MODEL_HANDOFF_SUMMARY.md:73-75` says “3017 отслеживаемых объектов”; `MODEL_HANDOFF_SPEC.md:17` calls these “3017 Git-объектов”; and `MODEL_HANDOFF_SPEC.md:349-350` again says “3017 objects”. The H2/context evidence describes an imported-object count and separately references tracked paths. These terms are not interchangeable: Git objects include blobs/trees/commits, while tracked paths are index entries. Clarify the measured unit and evidence source consistently in both documents. The count 3017 was not independently recomputed in this QA because `git -C C:\_Hobby\_work\kb_creator ...` was denied access from the assigned environment; do not treat this as a disproven numeric value.

## Checks and evidence

- Read goal plan/context and H2 receipt first. H4 is active; orchestration belongs to main chat; H5 critic remains pending.
- Cross-checked candidate claims against `README.md`, the current top of `PROJECT_STATUS.md`, the completed `20261004-user-docx-review` plan/context/release, `deliverables/latest/README_RU.md`, CLI parser and requested pipeline modules.
- Verified the parser declares `translate run` (`__main__.py:88-105`), ordinary route has five steps and v3 schema (`pipeline/five_step.py:14-18`), reconstruction has four `run` plus two `resume` stages (`pipeline/reconstruction.py:43-50`), and legacy publication has ten stages and `reject_legacy_publication_writer()` (`pipeline/publication.py:46-60,167-169`). The handoff accurately distinguishes those routes and warns against legacy writers.
- Candidate internal Markdown links resolved successfully. The three corrected successor DOCX, top-level `translator/`, shared CoC CSV, `.tools`, and root dependency manifest are absent at the checked standalone paths, matching the documented portability gaps. The three corrected DOCX links in `deliverables/latest/README_RU.md:18-20` therefore remain unavailable, and both candidate docs state that.
- Candidate repository inventory: filesystem counts were 89 pipeline files, 97 scripts files, 92 contract files, 242 test-folder files including 224 `test_*.py`, 1214 docs files, 851 input files, 210 latest-deliverable files, 207 report files, 5 reference files, and 5 each under output/pdf_raw. Tracked-path counts could not be independently queried because Git denied access; filesystem counts are not substitutes for tracked-path counts. The spec's 242/224 test figures match observed file counts. The 1209 docs tracked-path figure is not contradicted by the 1214 filesystem-file count.
- Reviewed unsafe/misleading command guidance. Legacy publication commands are explicitly marked not to run as writers (`MODEL_HANDOFF_SPEC.md:406-416`); source code confirms the common reject guard. `git lfs pull` labeling is the sole actionable command issue found.
- Acceptance language consistently separates mechanical checks, visual review, technical release approval, and human book acceptance. Historical counts are identified as inherited/historical, and standalone tests/build are explicitly not claimed as run.
- Limitation: repository Git status/revision and tracked-path inventory were not verified here because the environment denied `git -C` access to the assigned repository. No tests were run; not required for this bounded document QA.

## Files checked

- `C:\_Hobby\_work\kb_creator\kb_creator\docs\handoff\MODEL_HANDOFF_SUMMARY.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\docs\handoff\MODEL_HANDOFF_SPEC.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\docs\plans\20261011-model-handoff\plan.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\docs\plans\20261011-model-handoff\context.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\docs\plans\20261011-model-handoff\handoffs\H2-architect-receipt.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\README.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\PROJECT_STATUS.md` (top current sections)
- `C:\_Hobby\_work\kb_creator\kb_creator\docs\plans\20261004-user-docx-review\plan.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\docs\plans\20261004-user-docx-review\context.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\docs\plans\20261004-user-docx-review\release.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\deliverables\latest\README_RU.md`
- `C:\_Hobby\_work\kb_creator\kb_creator\__main__.py`
- `C:\_Hobby\_work\kb_creator\kb_creator\pipeline\five_step.py`
- `C:\_Hobby\_work\kb_creator\kb_creator\pipeline\reconstruction.py`
- `C:\_Hobby\_work\kb_creator\kb_creator\pipeline\publication.py`
- `C:\_Hobby\_work\NRI\docs\governance\nri_goal_governance.md`

## Next action

Main orchestrator should correct only the two cited candidate passages, rerun the corresponding command/path/count checks, then freeze for H5 independent release review. H4 has no release authority.
