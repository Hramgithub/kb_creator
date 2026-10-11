# M2 semantic-promotion implementation receipt

- Goal: `20260917-dream-master-en`; milestone: `M2`.
- Scope: only shared promotion bridge implementation and its focused regression
  coverage; no reconstruction source, Stage 01-06 output, schema, canonical
  plan/status, or publication artifact was changed.
- Result: `IMPLEMENTED_PENDING_FULL_SUITE`.
- Orchestrator policy owner: `gpt-5.6-sol`, medium.
- Assignment: engineering implementation, `gpt-5.6-terra`, medium; assignment
  state `completed`; orchestration ownership remains with the main chat.
- Scoped override: none.
- Timestamp: `2026-09-18T00:00:00+03:00`.
- Elapsed time: approximately 30 minutes.
- Token use: approximately 14k tokens.

## Result and changed files

- `kb_creator/pipeline/reconstruction_promotion.py`
  - derives structural mode exclusively from sealed decision-set v2 plus audit
    v4/profile authority, failing closed on a partial upgrade or downgrade;
  - validates the Stage 06 sidecar against the freshly sealed audit, submission,
    and each ordered decision identity;
  - permits/copies `SEMANTIC_STRUCTURE.json` only in structural mode, retaining
    the existing four publication roles;
  - reopens and validates the byte-identical packaged sidecar, including its
    candidate/content identity; and
  - adds the sidecar to acceptance evidence conditionally, plus all shared
    semantic modules/contracts that the bridge interprets to implementation
    inventory.
- `kb_creator/tests/test_reconstruction_promotion.py`
  - adds a compact synthetic v2/v4 sidecar regression: valid authority passes;
    reordered page identities and profile/audit disagreement fail closed.
- This receipt is the only additional authorized artifact.

## Verification/evidence

- `py_compile` passed for both changed Python files using the bundled Codex
  Python runtime.
- The same runtime passed a standalone semantic bridge smoke check using two
  synthetic decisions, an audit identity, and a sidecar.
- `git diff --check --` for both changed files passed; diff is two files,
  213 insertions and 7 deletions at the recorded checkpoint.
- The bundled runtime does not include `pytest`, and no system Python with
  pytest is installed, so the focused pytest file was not executable in this
  environment.
- Read-only Dream preflight advanced beyond the old candidate root-shape
  rejection and then correctly stopped at the pre-existing independent
  `contract-derived required-entity count mismatch` gate. No `promotion/`
  package or acceptance receipt was written.

## Blocker and next action

The accepted Dream candidate presently declares five numbered player handouts
in its reconstruction contract, while the Stage 06 combined Markdown and asset
logical names do not close that numbered domain. This newly visible gate is
independent of the semantic-sidecar promotion bridge and must be resolved by
the orchestrator under the relevant candidate/contract authority before a live
promotion retry. After that resolution, run the focused pytest suite in an
environment with pytest, rerun read-only promotion preflight, materialize, and
record the user-approved reconstruction acceptance.
