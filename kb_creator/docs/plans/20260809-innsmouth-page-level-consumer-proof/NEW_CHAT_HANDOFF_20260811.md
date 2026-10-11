# New-Chat Handoff: Innsmouth Page-Level Proof

Goal id: `20260809-innsmouth-page-level-consumer-proof`

Status: `paused`

## Purpose

This bundle protects the source-reconstruction pipeline from silently
misordering two-column text, collapsing paragraph boundaries, or publishing
occluded PDF text as normal body content. It is not yet a live Innsmouth
reconstruction or publication task.

## Read First

1. `D:\NRI\AGENTS.md`
2. `D:\NRI\docs\governance\nri_goal_governance.md`
3. `plan.md` and `context.md` in this directory
4. `D:\NRI\kb_creator\PROJECT_STATUS.md`
5. `D:\NRI\kb_creator\docs\contracts\page_level_consumer_proof_contract_status.md`

## Accepted Boundary

Packets `4b.1` through `4b.8` are accepted only as fixture-only proof work.
Their acceptance does **not** authorize a live PDF, EN source reconstruction,
KeeperBook, HTML, PDF, output/build, Git, release, production registry, or
public terminal result.

The two accepted fixture-only child identities are:

- two-column: `74ddca65755dbde190b57a5e82368895644ac6b605873913c20a32f2786d6526`
- nested Form: `136489ff1892bb27b8425806a1972809d03ce5e5e22f42b6a9f1bdfeca1cc503`

## Current Problem

Packet `4b.9` was interrupted after an executor breached the packet boundary
and left an untested partial literal reseal in these seven fixture-test files:

- `tests/_page_proof_fixture_leaves.py`
- `tests/test_page_proof_fixture_admission.py`
- `tests/test_page_proof_closed_schemas.py`
- `tests/test_page_proof_witness_render_components.py`
- `tests/test_page_proof_flow_adjacency.py`
- `tests/test_page_proof_visual_crosscheck.py`
- `tests/test_page_proof_composition.py`

The old frozen baseline cannot be restored byte-exactly because the needed
fixture-leaves file was not found locally. Its former SHA-256 was
`B471EB875410C09CDEF9ABA3F39082C3201F815D6C62ED9F3165A4ED58E1DF7E`.
Do not perform a partial six-file rollback.

The user chose to proceed without that file. Therefore the current seven-file
state is **not** accepted and must be treated as a new in-place candidate, not
as the former frozen baseline.

## First Permitted Action

Assign **Sol / high** a narrow, file-backed architecture task. Sol may write
only this handoff:

`handoffs/sol_page_proof_packet_4b9_in_place_salvage_spec_20260811.md`

The specification must define a fixture-only re-proof contract for the current
seven-file candidate. It must cover every affected invariant from `4b.6` to
`4b.9`, including:

- canonical visual-crosscheck containment;
- WitnessV3 private `W -> M -> E -> V` composition;
- closure of the two accepted fixture topology identities;
- authoritative inventory/reseal controls and an independent test oracle;
- fail-closed public APIs and inactive production roots.

It must list exact allowed files, deterministic test commands, acceptance
criteria, and an explicit prohibition on live input, output/build, Git,
network, production activation, and release paths.

## Required Review Sequence

1. Sol / high writes the salvage specification only.
2. A fresh independent Terra / high reviews the architecture.
3. Only if accepted, assign a bounded executor to implement the accepted
   packet and write a receipt.
4. A different independent Terra / high reviews implementation and evidence.
5. Only after that may `4b.9` be marked accepted. Step 5 live preflight still
   requires its own authorization and independent review.

## Key Evidence

- Invalid partial-candidate receipt:
  `handoffs/executor_page_proof_packet_4b9_high_recovery_20260811.md`
- Forensic baseline-recovery analysis:
  `handoffs/sol_page_proof_packet_4b9_baseline_recovery_spec_20260811.md`
- 4b.8 aggregate acceptance:
  `handoffs/terra_page_proof_packet_4b8_aggregate_acceptance_review_20260811.md`
- 4b.9 pre-interruption architecture review:
  `handoffs/terra_page_proof_packet_4b9_architecture_review_20260811.md`

## User-Facing Resume Prompt

```text
Continue goal 20260809-innsmouth-page-level-consumer-proof from the paused
handoff at D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\NEW_CHAT_HANDOFF_20260811.md.

Act as the gpt-5.5 orchestrator. Do not touch live Innsmouth source, Keeper,
HTML, PDF, output, build, Git, or release paths. The 4b.9 frozen baseline is
unavailable; the user chose in-place fixture-only salvage. First assign Sol
(high) to write the bounded salvage specification, then obtain a fresh
independent Terra (high) architecture review before any implementation.
Do not commit or push without explicit user authorization.
```
