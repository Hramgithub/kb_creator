# Sol Architecture Review: Innsmouth Source to Artifacts

## Contributor receipt

| Field | Value |
| --- | --- |
| Goal id | `20260730-innsmouth-source-to-artifacts` |
| Step id | `2-3: capability audit and full-pipeline contract` |
| Role | Sol architecture/process analysis |
| Model | Exact deployment identifier unavailable in runtime metadata |
| Effort | high |
| Scope | Read-only dependency, branch, contract, risk, and remediation analysis for source PDF -> accepted EN -> accepted RU -> KeeperBook -> HTML -> PDF -> reference comparisons |
| Result | `architecture_ready; implementation_blocked` |
| Timestamp | `2026-07-30T20:18:47Z` |
| Elapsed time | `361 seconds` at receipt preparation |
| Token use | `192690` goal tokens at receipt preparation |

This is an architecture/process receipt, not a release review or production
acceptance decision.

## Verdict

No current runner satisfies the goal's clean source-to-artifacts boundary.

The reusable `translator` layer already supplies much of the deterministic
machinery: source intake, page rendering, extraction, conditional OCR, page
policy, Document IR primitives, translation task preparation, HTML/PDF
builders, and mechanical QA. The missing work is the controlled materialization
of accepted EN, fresh RU, and KeeperBook artifacts, plus lineage isolation and
comparison-only reference handling.

The newly present
`kb_creator/scripts/build_innsmouth_source_to_artifacts.py` is a useful blocked
probe, but it is not a clean-room runner:

- it deep-copies `translator/config/the_innsmouth_terror.package.json`
  (`:16`, `:144-155`), inheriting historical page policy, package decisions,
  and true acceptance gates;
- it sends the raw column-OCR candidate directly to translation preparation
  and removes its source-acceptance gate (`:188-194`);
- it removes production HTML/PDF gates (`:198-201`);
- reference availability/hash mismatches prevent generation from starting
  (`:246-253`), so the references are operational dependencies rather than
  comparison-only inputs;
- it has no translation execution, RU assembly/proofread acceptance,
  KeeperBook assembly, or HTML/PDF completion stage (`:292-301`);
- the path-string guard (`:216-225`) does not prove transitive lineage and
  cannot detect inherited acceptance state.

The older runners are explicitly unsuitable: the full dry run resolves scripts,
configs, and accepted EN under deleted `CoC/Working/.../The_Innsmouth_Terror`
paths, while the v7 rebuild loads the v6 manifest/config and calls the deleted
package-specific statblock projector.

## Scope decision required before implementation

`kb_creator/docs/architecture/kb_creator_scope.md:8-24` currently says that
OCR, translation, proofreading, and publishing are out of scope. This goal
requires all four.

Recommended resolution: make `kb_creator` the run-owning orchestration facade
for this goal, while keeping reusable transformation implementations in
`translator`. `kb_creator` owns the clean config, run directory, lineage,
stage receipts, final artifacts, and comparison reports; `translator` remains
the execution library. The orchestrator should record this as an explicit scope
or ADR decision before implementation. If that decision is rejected, the full
pipeline belongs under `translator`, and `kb_creator` may only consume its
accepted manifest.

## Required dependency graph and branches

```text
source PDF
  -> clean package/config + immutable intake
  -> page renders + native text extraction
  -> accepted page map / Document IR
      -> native-text branch where reliable
      -> selected OCR/column-reconstruction branch
      -> visual-only branch with render evidence, no invented text
  -> assembled Full EN candidate + strict source-block coverage
  -> HUMAN source acceptance
  -> translation units
      -> fresh LLM translation (required for this run)
      -> independently supplied accepted-RU substitution (not supplied)
  -> deterministic RU assembly + mechanical QA
  -> HUMAN proofreading/RU acceptance
  -> deterministic KeeperBook assembly from accepted RU + policy
  -> HUMAN KeeperBook acceptance
      -> art extraction/classification/approval/placement branch
  -> HTML build + statblock projection + semantic/mechanics/art QA
  -> two-column PDF build + print QA + rendered visual review
  -> isolated Keeper/PDF reference comparisons
  -> reproducibility candidate; production approval remains false
```

The Yandex KeeperBook and PDF cannot serve as the accepted-RU substitution.
No independent accepted RU input is in the task packet, so fresh translation
and proofreading are mandatory for this run.

## Stage classification and contract

| Stage | Required input -> output | Execution class | Stop/branch rule |
| --- | --- | --- | --- |
| 1. Clean init | source path/hash + explicit kb_creator roots -> neutral config | deterministic | Must not copy the historical Innsmouth config. All gates start false. |
| 2. Intake | source PDF -> identity report | deterministic | Require SHA-256 `CFD72D...61F`, 71,396,612 bytes, 46 unencrypted Letter pages. |
| 3. Render/extract | source PDF -> page renders + native text | deterministic with pinned tools | Extraction is evidence, not accepted reading order. |
| 4. Page policy | renders/text diagnostics -> page map and source-block manifests | mixed | Automated proposal is allowed; page type, columns, visual-only pages, tables, handouts, and statblocks require source-grounded acceptance. |
| 5. Reconstruction | selected native/OCR blocks -> Full EN candidate | deterministic assembly plus LLM/human repair | OCR only where selected. Preserve page/block IDs, structure, mechanics, and uncertainty markers. |
| 6. EN acceptance | candidate + renders + coverage reports -> hash-bound acceptance receipt | human | No blocked pages, unresolved mechanics, or unreviewed structural blocks. |
| 7. Translation prep | accepted EN -> stable translation units | deterministic | Each unit carries source block IDs and source hash. |
| 8. Translation | units -> RU unit candidates | LLM | Record model, prompt hash, source hash, unit ID, and output hash. No automatic acceptance. |
| 9. RU assembly/QA | exactly one accepted candidate per unit -> Full RU candidate | deterministic | Exact unit/order coverage, page-marker parity, mechanics/token checks, terminology and residual-English reports. |
| 10. RU acceptance | EN/RU/renders/QA -> hash-bound proofread receipt | human | Meaning, structure, tables, stats, handouts, and terminology accepted. |
| 11. Keeper assembly | accepted RU + reviewed assembly policy -> KeeperBook candidate | deterministic | Split creation from acceptance; never let a manual gate create the artifact. |
| 12. Keeper acceptance | RU/Keeper/structure reports -> hash-bound receipt | human | Reader structure and declared transformations accepted. |
| 13. Art | source PDF/renders -> candidate assets -> approved assets/placements | deterministic extraction; human classification/placement acceptance | Full-page visual material may use render evidence; no reference-art copying. |
| 14. HTML | accepted Keeper + accepted art policy -> HTML | deterministic | Include statblock projection as a declared reusable postprocessor, then run positive-content, CoC mechanics, page-structure, semantic-chain, coverage, and art-layout QA. |
| 15. PDF | final HTML hash + pinned two-column policy/engine -> PDF | deterministic build; human visual acceptance | Mechanical print QA is necessary but does not detect every overlap/clipping defect. |
| 16. Comparisons | generated Keeper/PDF + external references -> delta reports | deterministic, isolated read-only | Runs only after generated artifact hashes are frozen; comparison output cannot feed the same generation run. |

## Minimum universal stage receipt

Extend the existing `translator.pipeline_state` fingerprint/hash record rather
than replacing it. Each material stage needs an immutable
`kb_creator.stage_receipt.v1` with:

- `run_id`, `stage_id`, `attempt_id`, schema version, mode
  (`deterministic`, `llm`, `manual`, or `comparison_only`);
- dependency receipt IDs and the exact dependency output hashes consumed;
- path-bearing input/output records with symbolic role, normalized path,
  SHA-256, size, and provenance class;
- argv, exit code, implementation/script hash, stage-local config hash,
  tool/model versions, and relevant binary hashes;
- start/finish timestamps and duration;
- status from `pass`, `needs_review`, `blocked`, or `fail`;
- structured findings, warnings, and explicit intentional exclusions;
- for LLM stages: model/profile, prompt-pack hash, source-unit hash, sampling
  settings if exposed, and per-unit output hash;
- for manual gates: actor/role, decision, timestamp, acceptance scope,
  current input hashes, and reviewer evidence paths;
- transitive lineage result: `generation_lineage_clean=true|false`, forbidden
  path hits, and comparison-only input hits.

Current pipeline state already records stage/config fingerprints,
tool versions, timestamps, and input/output hashes
(`translator/pipeline_state.py:151-243`). Keep that state path-free for cache
safety and add the path-bearing audit receipt alongside it.

Manual gates must no longer be satisfied by a true config boolean alone.
`translator/pipeline_run.py:220-235` currently checks only booleans and then
records a manual stage as successful (`:395-410`). Wire
`translator/contract_v2_receipts.py` into the runner so acceptance is
hash-bound and becomes stale when any reviewed input changes.

## Required artifact data contracts

1. `clean_package.v1`: built from neutral `init-package` defaults and explicit
   kb_creator roots; no historical acceptance values or reference paths.
2. `source_block_manifest.v2` and `candidate_block_manifest.v2`: use the
   existing Document IR concepts—page/block IDs, order, type, bbox/region,
   render/evidence hash, review state, predecessor/successor, and source PDF
   hash. All 46 physical pages remain represented, including visual-only pages.
3. `translation_units.v1`: stable unit ID, ordered source block IDs, source
   text hash, required structure/mechanics tokens, and status.
4. `ru_unit_candidate.v1`: unit/source/prompt/model hashes, RU text, findings,
   and acceptance state.
5. `ru_assembly_manifest.v1`: exact unit coverage/order, Full RU hash, EN/RU
   structural fingerprint comparison, terminology/mechanics QA references.
6. `keeper_assembly_policy.v1` and `keeper_manifest.v1`: accepted RU hash,
   declared transformations, source-page marker policy, art/statblock anchor
   policy, Keeper hash, and structure counts.
7. `publication_manifest.v1`: Keeper hash -> HTML hash -> PDF hash, accepted
   art manifest hash, postprocessor hashes, PDF variant and engine identity.
8. `reference_comparison.v1`: generated/reference identities, algorithms,
   deltas, and `comparison_only=true`.

## Reference isolation rules

Allowed:

- verify the two reference hashes in the comparison stage;
- compare generated Keeper structure, normalized text, headings, tables,
  statblocks, source markers, art anchors, and declared transformations;
- compare PDF page count/media boxes, extracted-text coverage, headings and
  mechanics tokens, fonts/images, and rendered visual/perceptual deltas;
- use findings to open a new source-grounded remediation run.

Forbidden:

- reference paths or hashes in generation config, gates, cache keys, or stage
  dependencies;
- copying text, Markdown, art, CSS, HTML, or PDF pages from a reference;
- seeding page map, translation, Keeper assembly, art placement, expected
  counts, or acceptance thresholds from a reference;
- automatically patching the current candidate from a diff.

The reference PDF has 32 A4 pages while the source has 46 Letter pages.
Therefore page-number-to-page-number visual diff is not a valid universal
alignment strategy; align by headings/anchors/content windows and report
unmatched pages.

## Concrete remediation sequence

1. Record the scope/ADR decision described above.
2. Replace `BASE_CONFIG` cloning with neutral config generation. Add explicit
   kb_creator-owned page-policy and publication-policy files; initialize every
   acceptance gate to false.
3. Add a lineage firewall before execution and at every stage. Deny generation
   reads from both old CoC Innsmouth roots and both reference paths. References
   must be absent without blocking stages 1-15.
4. Add source IR/manifests and deterministic Full EN assembly. Use native text
   where supported, OCR only on selected pages, and require hash-bound source
   acceptance.
5. Add LLM translation execution, deterministic RU unit assembly, mechanical
   QA, and explicit proofreading acceptance. An independent accepted-RU import
   adapter may exist universally, but this run has no eligible import input.
6. Split `manual-keeperbook-assembly` into deterministic
   `assemble-keeperbook-candidate` and manual
   `accept-keeperbook-candidate`.
7. Port the statblock projection into reusable code or make it an explicit
   package postprocessor under current source control. Do not call the deleted
   CoC package script. HTML QA must run after projection.
8. Build PDF only from the recorded final HTML hash; pin browser/tool identity,
   run print QA, render all pages, and retain a focused human visual checklist.
9. Move Keeper/PDF comparison into a separate command/stage that can run after
   generation success or report `comparison_blocked` without changing
   generation status.
10. Add tests for gate reset, forbidden transitive reads, missing references,
    run-ID collision/non-overwrite, receipt staleness, exact unit coverage,
    Keeper->HTML->PDF hash chaining, and comparison feedback isolation.

## Acceptance criteria for implementation

- The run succeeds through PDF when old Innsmouth Working/Output artifacts and
  both references are inaccessible; only comparison stages become blocked when
  references are unavailable.
- No generation receipt contains a forbidden path/hash, and the transitive
  lineage closure contains only the source PDF, kb_creator-owned state,
  declared reusable code/tools, and accepted current-run artifacts.
- The source identity matches the recorded hash/size and the source manifest
  covers all 46 pages with no unaccepted textual/structural blocks.
- Full EN is assembled from current-run source blocks and has a current
  hash-bound acceptance receipt.
- Full RU has exact translation-unit coverage, page/order and structural
  parity, preserved mechanics, passing terminology/residual checks, and a
  current proofreading acceptance receipt.
- KeeperBook is created by a deterministic command from the accepted Full RU
  hash and reviewed policy; it is not byte-copied from any reference and has a
  separate acceptance receipt.
- HTML records the generated Keeper hash as its direct content input; all
  required assets resolve; post-projection structure, positive-content, CoC
  mechanics, semantic-chain, coverage, and art-layout checks pass.
- PDF records the generated HTML hash as its direct input, uses the selected
  two-column variant, passes print QA, and has rendered visual evidence with no
  clipping, overlap, blank-body, or unreadable-glyph blockers.
- Keeper and PDF comparison reports include the required structural/text/art
  and page/render differences, but equality to the references is not required
  for generation success.
- `full_run_report.json` links every stage receipt and artifact hash, reports
  `production_approved=false`, and cannot report pass if any mandatory stage is
  `blocked`, `needs_review`, or `fail`.

## Evidence and live checks

- Source verified: 71,396,612 bytes; SHA-256
  `CFD72DD3B8702C07750DCBB9F721A704793D6D474167B288922E6F7EBEEA561F`;
  46 pages, unencrypted, 612 x 792 pt.
- Reference Keeper verified: 205,762 bytes; SHA-256
  `E1C889ADB5676798D7E296E4231040FA730029A7BA40AD515BF97059F5F78BA7`.
- Reference PDF verified: 65,261,806 bytes; SHA-256
  `D89BA390B296211692419D08F8E8F84CB0D393B54E94489531542BB5A0E08FC5`;
  32 pages, unencrypted, A4-sized.
- Old Working tree is absent. The old Output directory exists only as an empty
  directory; Git reports the historical scenario files as deleted. This still
  warrants a denylist because later checkout/recreation must not alter lineage.
- No scripts, canonical plans, context, project status, release files, source
  PDFs, references, or old scenario folders were changed.

## Files checked or changed

Checked:

- `docs/governance/nri_goal_governance.md`
- assigned `plan.md` and `context.md`
- `kb_creator/README.md`, `PROJECT_STATUS.md`,
  `docs/architecture/kb_creator_scope.md`
- all current Innsmouth kb_creator runners and their tests, including the
  concurrently added source-to-artifacts probe
- `translator/config/pipeline-stages.v1.json`,
  `artifact_registry.py`, `pipeline_run.py`, `pipeline_state.py`,
  `contract_v2_receipts.py`, `contract_v2_gates.py`, `document_ir.py`,
  `page_policy.py`, and relevant `translator.py` stage implementations
- source/reference file identities and PDF metadata

Changed:

- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/sol_architecture_review.md`

## Blockers and next action

Blockers are: unresolved kb_creator scope ownership; no clean neutral package;
no source-candidate acceptance chain; no translation execution/RU acceptance;
no deterministic Keeper assembly; package-specific statblock projection still
outside reusable code; no deep isolated reference comparators; and manual gates
not yet bound to current input hashes.

Next action: the orchestrator should accept or amend this specification, record
the scope decision, then assign bounded implementation beginning with neutral
config generation, lineage enforcement, and receipt-bound manual gates. Do not
run the current probe as evidence of a full pipeline.
