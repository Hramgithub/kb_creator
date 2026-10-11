# Engineer receipt: reconstruction promotion bridge

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4-to-5-reconstruction-promotion-bridge-implementation`
- Role: engineering contributor
- Requested policy role/model/effort: `gpt-5.6-sol`, `high` (user-scoped override)
- Actual platform model/effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Assignment state: `user-overridden-platform-unverified`
- Scoped override: engineering implementation for this goal uses
  `gpt-5.6-sol` at `high`
- Timestamp: `2026-09-14T11:37:50Z`
- Elapsed time: approximately 75 minutes
- Token use: unavailable

## Scope and result

Implemented a scenario-neutral, fail-closed bridge between a completed
six-stage reconstruction run and publication preflight. The implementation is
split into two create-once operations:

1. materialize a fixed portable upstream package in state
   `candidate_awaiting_reconstruction_acceptance`;
2. record a separate exclusive-create `artifact_acceptance.v1` receipt only
   through the dedicated acceptance command.

The materialization operation creates no acceptance file or acceptance claim.
Publication consumes only the exact four-role bridge inventory plus the exact
accepted receipt and performs no reconstruction write.

No live Dissociation run, candidate, acceptance, publication output, canonical
plan/context/status, README, `.codex`, Git index, commit, or release state was
changed.

## Files changed in this packet

- `kb_creator/pipeline/reconstruction_promotion.py` (new)
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/__main__.py`
- `kb_creator/contracts/reconstruction_upstream_inventory.v1.schema.json` (new)
- `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json` (new)
- `kb_creator/contracts/reconstruction_source_identity.v1.schema.json` (new)
- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/contracts/scenario_publication_blueprint.v1.schema.json`
- `kb_creator/tests/test_reconstruction_promotion.py` (new)
- `kb_creator/tests/test_publication_control_plane.py`

This receipt is the only handoff artifact changed by the contributor.

## Implemented controls

- `resume_engine` snapshots the already validated DecisionSet, exact page
  decisions, and optional allowlist to the fixed absent
  `review/validated-submission-v1/` boundary before Stage 05/06. Existing
  snapshots are revalidated against the supplied submission and never merged
  or overwritten.
- Stage 05 and Stage 06 manifests bind only snapshot identities; promotion has
  no fallback search or caller-supplied decision authority.
- `reconstruction-promotion materialize` and `record-acceptance` expose only
  the fixed CLI arguments from the architecture. There are no source,
  candidate, destination, evidence, decision, recorder, or adapter overrides.
- Materialization requires canonical repository topology, non-reparse paths,
  capability `available`, no skip evidence, non-injected production authority,
  current source/contract/implementation/tool/capability bindings, exact six
  stages and outputs, a closed submission snapshot, passing full-domain
  fidelity, materializer-shaped candidate closure, exact page/role/entity,
  selected-block provenance, assets, markers, and nine all-pass QA gates.
- The fixed package copies only portable content and evidence, uses exact four
  publication roles, seals source/QA/manifest/inventory records, binds the
  exact Stage 06 original candidate inventory, and excludes source PDF bytes,
  raw MinerU outputs, overlays, runtimes, acceptance, and preview PDF.
- Package publication uses staging then no-replace rename and validates the
  reopened tree. Destination and staging residue are stop states.
- Acceptance recomputes candidate, exact Stage 06 producer, and the ordered
  five-file evidence set. It fixes decision=`accepted` and
  recorder=`main_orchestrator`, uses exclusive create plus flush/fsync, rejects
  replay/pre-existing receipt, and removes only its own just-created receipt
  if post-write validation fails.
- Publication preflight requires fixed basenames in one canonical package,
  exact four contract roles, complete sealed package/file/directory closure,
  exact six-stage chain, all-pass QA/fidelity, exact acceptance candidate,
  producer, evidence, recorder and nonblank user reference before a publication
  run root can be created.
- Reconstruction and publication implementation identities now include the
  bridge and its schemas, so code drift invalidates a pre-bridge or stale run.

## Verification evidence

- Final bridge suite: `15 passed, 1 skipped` in `20.14s`.
  The skip is host-conditional: this Windows host did not permit creation of an
  unprivileged symlink fixture. Runtime reparse checks remain active.
- Final combined reconstruction/bridge/publication-positive run before the
  final tree-closure hardening: `32 passed, 1 skipped` in `22.60s`.
- Reconstruction control plane: `16 passed`.
- Reconstruction plus publication contracts/authoring: `69 passed, 13 skipped`;
  the skips are existing optional/schema-host conditions.
- Publication contract/authoring focused suite: `51 passed, 13 skipped`.
- Publication registry E2E: `3 passed`.
- All 32 `test_publication_control_plane.py` cases passed in bounded groups:
  positive/preflight/gates (`7`), registry/CLI (`12`), package-chain attacks
  (`7`), ArtView package attacks (`3`), Stage 60/config drift (`2`), and real
  Stage 70/71 synthetic package (`1`).
- `py_compile` passed for the two reconstruction modules, publication module,
  CLI, and changed focused tests.
- `git diff --check` reported no whitespace errors in this packet; only
  pre-existing line-ending warnings in unrelated/parallel files were printed.
- Positive coverage includes zero and nonzero contract-derived entity cases,
  A without acceptance, separate B, exact acceptance evidence, read-only
  publication preflight, portable path-field scan, schema/runtime top-level
  parity, and no acceptance/publication residue.
- Adversarial coverage includes skip, injected authority, outside root,
  missing snapshot, stage/output drift, source drift between A/B, pre-created A
  destination, simulated rename race, pre-created/second B, post-write B
  validation failure cleanup, resealed false QA, extra package file, legacy
  flat inventory schema, absent acceptance, subset publication roles, and
  unsupported CLI path/authority flags.

## Test-residue cleanup

An interrupted long pytest process left 31 directories with literal prefix
`kb_creator/working/sample/reconstruction/pytest-publication-`. After explicit
user authorization, every target was individually checked as a resolved direct
directory child of the exact sample reconstruction parent and removed with a
literal path. Result: `removed=31`, `remaining=0`. The fixture now uses
`TemporaryDirectory`; follow-up checks report residue `0`. No Dissociation or
other sample path was touched.

## Deferred exhaustive criteria and blockers

The bounded implementation packet is coherent and fail-closed, but the full
architecture acceptance checklist is not claimed complete. The following
exhaustive matrix remains for bounded QA/independent implementation review:

- explicit junction/mount/reparse attacks at every run, snapshot, staging,
  package and inventory component on a host that permits creating them;
- every lexical Windows path variant (alternate drive, UNC, ADS, trailing-dot,
  reserved-device and case-collision) at every portable record boundary;
- the complete stale allowlist/queue/decision mutation matrix, including all
  five-stage/extra-stage/upstream-order/producer variants as bridge-specific
  tests rather than relying partly on reconstruction-control coverage;
- the full candidate marker/role/entity/asset/provenance mutation matrix named
  in architecture Section 14;
- a real JSON Schema engine pass for every new document. The current repository
  test runtime has no `jsonschema` package; tests verify parseability, closed
  top-level parity and exact role constants, while runtime performs independent
  closed validation without an optional dependency;
- a native Windows concurrent no-replace race test in addition to the injected
  deterministic race test;
- independent `gpt-5.5` implementation review. Until that review closes all
  P0/P1 findings, a fresh live Dissociation reconstruction run and user
  acceptance remain blocked by governance.

## Next action

Assign bounded QA for the deferred attack matrix, then an independent
`gpt-5.5` implementation review. Do not start a fresh live Dissociation run,
materialize a live package, record user acceptance, or begin publication until
those gates are closed.
