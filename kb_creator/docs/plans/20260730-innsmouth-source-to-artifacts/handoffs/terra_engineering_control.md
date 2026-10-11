# Terra Engineering / Process-Control Receipt

- goal_id: `20260730-innsmouth-source-to-artifacts`
- step_id: `engineering_process_control_review`
- role: engineering/process-control reviewer
- model: Codex (gpt-5.6-terra role)
- effort: medium
- review kind: process and engineering control
- implementation or material design of candidate: no
- timestamp: `2026-07-30T23:13:46+03:00`

## Scope

Read-only review of the assigned goal plan/context, `kb_creator` Innsmouth
runners/configuration, and `translator` implementation evidence. No code,
canonical plan/context/status, legacy scenario folders, or reference artifacts
were changed or copied. This receipt is the sole write.

## Result

**Blocked for a source-PDF-to-artifacts claim.** The existing chain is a
v6-derived publishing reproducibility chain, not a clean-room full dry run.
The absence of `CoC/Working/Scenarios/The_Innsmouth_Terror` makes the first
failure explicit, but `CoC/Output/Scenarios/The_Innsmouth_Terror` still exists
in this checkout and remains an accidental-success input unless denied.

Concrete dependencies:

1. `build_innsmouth_full_dry_run.py` hard-codes the removed Working tree for
   three executable backends, baseline config, PyMuPDF output, QA reports, and
   accepted EN comparators. It imports the old reading-order/cleanup modules
   and clones the old `Recovery_v6` package config.
2. Its `accepted_cleaned_delta` applies nine hard-coded v6 editorial patches,
   then its publish gate requires normalized equality with old accepted raw and
   cleaned EN files. This is historical-content replay, not a comparison-only
   control.
3. `build_innsmouth_v7_rebuild.py` loads the freeze manifest and baseline v6
   config; retains accepted content inputs; calls the old statblock script;
   reads old art/integration manifests; writes to old CoC output paths; and
   compares output with frozen v6 HTML/PDF.
4. `build_innsmouth_final_result.py` requires the freeze and previous dry-run
   reports, invokes the v7 runner, and `copy2`s artifacts sourced from the old
   CoC output tree. Its frozen-path guard prevents overwrite, not content or
   provenance reuse.
5. `translator` is reusable engine evidence, but both Innsmouth package
   configs encode legacy Working/Output paths, accepted gates/receipts, and
   Innsmouth Guide references. Blindly cloning either config would preserve
   those dependencies. The Guide can be an explicitly recorded terminology or
   cross-check reference only, never an assembly input.

## Required Guard Contract Before Any Full Run

Implement a new `kb_creator`-owned package/config generator and a preflight
`dependency_control_report.json`; do not adapt the v6 config at runtime. The
config must declare only:

- immutable source-PDF path/hash and `kb_creator` run-owned working/output/QA
  roots;
- source reconstruction, RU, Keeper, HTML, PDF, and generated-art manifests;
- optional external reference paths in a dedicated **comparison-only** section.

Preflight must fail closed when executable/configured input paths, imported
local modules, subprocess scripts, symlink/junction targets, or artifact hashes
resolve under either `CoC/Working/Scenarios/The_Innsmouth_Terror` or
`CoC/Output/Scenarios/The_Innsmouth_Terror`. It must also reject any generation
stage that opens the external Keeper/PDF reference paths. Reference reads are
allowed only after generated Keeper/HTML/PDF hashes are sealed.

Required report fields: run id; canonicalized path and hash for every input,
output, imported script/module, subprocess command, and config; role
(`source`, `generated`, `comparison_reference`, `tool`); source stage; parent
artifact hashes; forbidden-path findings; reference-read event sequence; and a
final lineage DAG proving `PDF <- HTML <- generated Keeper <- generated RU <-
generated EN <- source PDF`.

## Guard Tests / Reports

1. **Static dependency test**: scan the new runner, generated config, and all
   transitively selected local scripts for forbidden legacy path fragments,
   `KeeperBook_v6`, `Recovery_v6`, freeze manifests, accepted receipts, and
   external reference paths in generation commands. Allow-list generic
   `translator/translator.py` only after its supplied config passes the same
   scan.
2. **Runtime file-access audit**: instrument file opens plus subprocess argv
   (or run in a deny-listed filesystem sandbox). The report must contain zero
   legacy/reference reads before `comparison_started_at`; otherwise status is
   `blocked`.
3. **Config provenance test**: construct the clean-room config from a minimal
   kb_creator template; assert no inherited true/manual gate, acceptance
   receipt, legacy output root, legacy QA report, art manifest, or baseline
   hash. All stage gates begin `false` and become true only from this run's
   reports.
4. **Negative fixtures**: inject (a) a legacy Keeper path, (b) a reference
   Keeper path in `production_html.source_markdown`, (c) a legacy art manifest,
   and (d) a reference hash copied into a generated target. Each must block
   preflight/promotion with precise finding codes.
5. **Anti-copy tests**: verify generated Keeper, HTML, and PDF have parents in
   the run manifest; reject `copy`, `copy2`, `shutil.copy*`, hard-link, and
   move promotion from forbidden/reference roots. Hash equality with a
   reference is reportable but never proof of provenance.
6. **Stage hand-off checks**: HTML report input hash must equal generated
   Keeper hash; PDF report input hash must equal generated HTML hash; final
   report must fail if either producer timestamp/hash predates its parent.
7. **Reference comparison report**: after sealing outputs, compare structure,
   text, page count, extracted PDF text, and rendered pages. Label every result
   `comparison_only`; it cannot set a generation gate or overwrite a generated
   artifact.

## Files Checked

- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/plan.md`
- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/context.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/scripts/build_innsmouth_full_dry_run.py`
- `kb_creator/scripts/build_innsmouth_v7_rebuild.py`
- `kb_creator/scripts/build_innsmouth_final_result.py`
- `kb_creator/scripts/freeze_innsmouth_v6.py`
- `kb_creator/working/the_innsmouth_terror.v7_rebuild.package.json`
- `translator/translator.py`
- `translator/config/the_innsmouth_terror.package.json`
- `translator/config/the_innsmouth_terror.recovery_v2.package.json`
- `translator/docs/plans/20260730-innsmouth-v6-kb-freeze/handoffs/terra_process_control_20260730.md`

## Files Changed

- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/terra_engineering_control.md` (this immutable receipt only)

## Verification / Evidence

- Assigned context's stated probe is consistent with static inspection: the
  full runner dereferences the absent legacy Working config before source work.
- Live path check: legacy Working tree `False`; legacy Output tree `True`.
- Static code evidence: full-runner legacy roots/constants and publish gate;
  v7 loader/art/statblock/baseline paths; final-runner legacy sources and
  `copy2`; translator configs' pervasive legacy paths and accepted gates.
- No execution of a build, reconstruction, comparison, or artifact promotion
  occurred in this review.

## Blockers

- No kb_creator-owned clean-room source-to-Keeper/RU contract/config exists.
- Current HTML/PDF runners use frozen v6 inputs and old CoC outputs, so they
  cannot satisfy the goal even if their rendering QA passes.

## Next Action

Orchestrator should specify and implement the clean-room package/config plus
the dependency-control preflight and negative fixtures first. Only then port
generic `translator` stages, with all paths rooted in the run workspace, and
run reference comparisons strictly after the generated artifact lineage is
sealed.

## Accounting

- elapsed time: approximately 14 minutes
- token use: unavailable
