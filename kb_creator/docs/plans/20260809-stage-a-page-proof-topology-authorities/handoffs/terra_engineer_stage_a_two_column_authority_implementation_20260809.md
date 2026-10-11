# Immutable Engineering Handoff Receipt — Stage A Two-Column Authority

- Goal id: `20260809-stage-a-page-proof-topology-authorities`
- Step id: `3a`
- Assignment state: `implemented; limited to the synthetic two-column authority`
- Role/effort: Terra engineer / medium
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified)
- Scoped override: nested Form and any page-proof work are explicitly out of scope.
- Timestamp: `2026-08-09T21:20:26.6830112+03:00`
- Elapsed active time: approximately 23 minutes
- Token use: unavailable

## Scope and result

Implemented only `stage-a.positive-two-column.v1` with internal topology id
`stage_a_positive_two_column.v1`. Its literal synthetic PDF has page
`/Contents [5 0 R 6 0 R]`; root streams `5:0` and `6:0` emit `A,B` and
`C,D`, respectively. Stage A asserts only the distinct raw root
stream/frame identities and `B -> C` paint transition. It retains
`geometry`, `visibility`, and `semantic_role` as `unavailable_stage_a` for
every atom.

The assertion boundary explicitly says geometry, visibility, semantic blocks,
and reading order are not proved. It does not assert actual columns.

## Paths changed

- `kb_creator/pdf_raw/raw_authority_projection.py`
- `kb_creator/tests/test_raw_authority_projection_stage_a_topology_authorities.py`
- `kb_creator/tests/test_raw_authority_projection_stage_a_contract.py`
- this receipt

## Literal evidence

- fixture SHA-256: `f5416c3c080c127b9cd24d54201558f08f3760673c90c114d5038ef9eb17fede`
- fixture binding SHA-256: `c41ec7ae9eea7d5fc2f654eb825bf1bb1af954d00c754fd6140f134985af8880`
- authority inventory SHA-256: `3173d033fcf6228687388f020f0e5e6e7e9c1ce2a373bc1b2bca49823ab951c0`
- authority content SHA-256: `890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef`
- canonical topology assertion SHA-256: `5f81d370d69d6976fd0dcb5ab0e1b08ce3f1b73fe3830b9350b9f4a385561420`

## Verification

Executed with no bytecode and no pytest cache:

```text
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_raw_authority_projection_stage_a_topology_authorities.py kb_creator/tests/test_raw_authority_projection_stage_a_contract.py kb_creator/tests/test_raw_authority_projection_stage_a_replay.py
```

Result: `12 passed in 0.13s`.

```text
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_raw_authority_projection_stage_a_adversarial.py kb_creator/tests/test_raw_authority_projection_stage_a_boundaries.py kb_creator/tests/test_raw_authority_projection_stage_a_containment.py
```

Result: `365 passed, 1 skipped in 5.31s`.

Focused tests cover positive projection/replay, one-atom left/right
insufficiency, reversed stream order, incorrect transition endpoint,
membership duplication/drop, claim-boundary smuggling detection, and a
fully rehashed registry cross-pair rejected before `RawPdfDocument.open`.
The legacy raw-interpreter authority remains exactly two rows; the existing
adversarial matrix remains bound to the two baseline Stage A rows.

## Blockers and next action

No technical blocker for this narrow implementation. Public acceptance of
*all* topology authorities remains unavailable: only the two-column authority
exists in this substep, and nested Form was intentionally not created.
Next action is independent review of this two-column authority, followed by a
separate bounded nested-Form task if the orchestrator assigns it. No release
decision is made here.
