# Critic receipt: reconstruction promotion bridge implementation review

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PF-reconstruction-promotion-bridge-independent-review`
- Review kind: `implementation`
- Role: independent critic
- Requested policy role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed the candidate under review: no
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-14T11:57:29Z`
- Elapsed time: approximately 52 minutes
- Token use: unavailable in platform; active runtime goal reported `254323`
  orchestrator-side tokens after receipt write

## Scope

Reviewed the remediated reconstruction-promotion bridge as an independent
implementation critic. This is not reconstruction acceptance, not user
acceptance, not publication acceptance, and not a final release review. No
production code, tests, canonical plan/context/status, release file, live
Dissociation artifact, Git index, or acceptance artifact was edited. This
receipt is the only file written by this review.

## Files checked

- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/README.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_reconstruction_promotion_bridge_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_bridge_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/qa_reconstruction_promotion_bridge_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_path_remediation_20260914.md`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/__main__.py`
- `kb_creator/contracts/reconstruction_upstream_inventory.v1.schema.json`
- `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json`
- `kb_creator/contracts/reconstruction_source_identity.v1.schema.json`
- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/contracts/scenario_publication_blueprint.v1.schema.json`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_publication_control_plane.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_registry_e2e.py`
- `kb_creator/tests/test_author_scenario_publication_contract.py`
- `kb_creator/tests/test_scenario_contract.py`

## Verification evidence

- Combined targeted suite run with
  `PYTHONPATH=.tools/python-test-deps;<repo>` and repository-local
  `.tools/MinerU/.venv/Scripts/python.exe`:
  `275 passed, 2 skipped in 129.56s`.
  The run covered reconstruction promotion, the adversarial bridge matrix,
  reconstruction control plane, publication control plane, publication
  contracts, publication registry E2E, publication contract authoring, and
  scenario contract compatibility.
- `py_compile` passed for:
  `kb_creator/pipeline/reconstruction_promotion.py`,
  `kb_creator/pipeline/reconstruction.py`,
  `kb_creator/pipeline/publication.py`,
  `kb_creator/__main__.py`,
  `kb_creator/tests/test_reconstruction_promotion.py`, and
  `kb_creator/tests/test_reconstruction_promotion_adversarial.py`.
- `git diff --check` on the reviewed bridge, schemas, exact-four contract
  changes, and focused tests reported no whitespace errors.
- Real `jsonschema` is installed under `.tools/python-test-deps` and was used
  in the combined suite for publication blueprint/contract validation.
- Additional direct schema/runtime parity probe reproduced one non-blocking
  gap: `reconstruction_upstream_manifest.v1.schema.json` accepts a file record
  path `content//x.json` with `0` schema errors, while runtime
  `_safe_relative("content//x.json")` rejects it with
  `unsafe_promotion_path`.

## Findings

### P0

None found.

### P1

None found.

I did not reproduce the QA-reported lexical alias P1 after remediation:
`content//x.json`, `content///x.json`, `content/./x.json`, leading `./`,
terminal `/.`, trailing separators, ADS/colon, drive-relative, UNC/backslash,
reserved device names, trailing dot/space, traversal, and case-collision paths
are now covered by adversarial tests and fail closed through runtime path
validation. The remediated adversarial suite is included in the passing
combined run.

### P2

1. Schema/runtime path-pattern parity remains looser than runtime for the new
   reconstruction manifest schema.

   Evidence: the manifest schema `$defs.file.properties.path.pattern` at
   `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json`
   rejects absolute paths, `.`/`..`, colons, backslashes, and NUL, but it does
   not reject empty path components such as `content//x.json`. Runtime
   `_safe_relative` in `kb_creator/pipeline/reconstruction_promotion.py`
   rejects empty, `.`, and `..` components before path resolution. A direct
   jsonschema probe with `package_files: [{"path": "content//x.json", ...}]`
   produced `schema_errors 0`; the matching runtime call raised
   `unsafe_promotion_path`.

   Severity rationale: this is not a publication or acceptance bypass because
   package validation and publication preflight call the promotion runtime
   validator before accepting a package. It does weaken the architect's desired
   schema/runtime parity evidence for standalone schema consumers and should be
   closed before release packaging or before these schemas are treated as
   complete external contracts.

## Positive closure checks

- Snapshot authority: `resume_engine` creates or revalidates
  `review/validated-submission-v1/` before Stage 05/06, then Stage 05/06 input
  identities are bound to the fixed snapshot rather than caller-supplied paths.
- Canonical run topology: promotion requires
  `kb_creator/working/<scenario-id>/reconstruction/<safe-run-leaf>/`, rejects
  skipped and injected runs, and revalidates source, contract, implementation,
  tool, and capability bindings before package or acceptance operations.
- Stage chain: package validation requires exactly six ordered reconstruction
  stage records, successful states, upstream continuity, Stage 05 fidelity, and
  Stage 06 candidate identity.
- Candidate closure: runtime validation covers source-page markers, page
  domain, contract-derived roles, required handout count, decision copies,
  selected-block provenance, asset manifest/tree/Markdown closure, overlay
  domain, and no unresolved findings.
- A/B separation: materialization returns
  `candidate_awaiting_reconstruction_acceptance` with no acceptance file;
  acceptance is a separate fixed command that recomputes candidate, producer,
  and evidence and uses exclusive create.
- Acceptance receipt: the fixed receipt uses
  `artifact_kind=reconstructed_en`, exact Stage 06 producer, the ordered five
  evidence identities, `decision=accepted`, `recorder_role=main_orchestrator`,
  and nonblank user-decision reference. There is no caller flag for candidate,
  evidence, decision, destination, or recorder on the reconstruction-promotion
  CLI.
- Publication preflight: `_validate_reconstruction` requires fixed inventory
  and acceptance basenames in one canonical package root, exact four upstream
  roles, complete runtime package validation, matching scenario and
  reconstruction contract identity, and `require_acceptance=True` before any
  publication run root is created.
- CLI boundary: `python -m kb_creator reconstruction-promotion` exposes only
  `materialize --run-root` and `record-acceptance --run-root
  --user-decision-reference`; unsupported override flags are rejected by the
  parser.
- Legacy/publication bypass: the publication acceptance command still handles
  only publication artifact kinds; reconstructed-en acceptance is routed
  through the dedicated bridge, and publication remains a strict consumer.

## Residual limitations

- Native symlink/reparse fixture creation is unavailable in this Windows
  session; the relevant symlink test is host-skipped. Runtime non-reparse checks
  are present in package and authority validation, and synthetic monkeypatch
  coverage exists in adjacent authoring tests, but native junction/mount race
  evidence remains host-limited.
- The architect's full adversarial list is broad. The focused suites cover the
  remediated lexical class, representative stage/decision/candidate/package
  mutations, skip/injected/source drift, no-overwrite and replay controls, and
  publication preflight. I did not manually enumerate every possible
  five-stage/extra-stage/candidate mutation beyond the implemented targeted
  tests and static review.

## Blockers

No P0/P1 blocker remains for starting a fresh GPU reconstruction run from the
reviewed checkout state.

The P2 schema/runtime parity gap is non-blocking for the fresh GPU run because
runtime promotion and publication validation remain fail-closed. It should be
closed before release packaging or before declaring the three new schemas fully
parity-complete.

## Recommendation

Approve the reconstruction-promotion bridge for a fresh GPU Dissociation
reconstruction run, with the following limits:

- do not treat this as reconstruction acceptance, publication acceptance, or
  release approval;
- do not resume the sealed no-CUDA run;
- after the fresh run, materialize the upstream package and stop for explicit
  user reconstruction acceptance before invoking the acceptance command;
- track the P2 schema path-pattern parity gap for closure before release or
  external schema-contract reliance.
