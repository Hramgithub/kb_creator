# Stage A Page-Proof Topology Authorities

Goal id: `20260809-stage-a-page-proof-topology-authorities`

## Objective

Create and independently accept two new fixture-only Stage A authority
topologies required by the accepted page-proof contract:

- `stage_a_positive_two_column.v1`;
- `stage_a_positive_nested_form.v1`.

The output is raw authority evidence only. It must not consume live Innsmouth
files, reconstruct source text, use page-proof public APIs, modify source or
publication artifacts, or authorize a rebuild.

## Role Contract

- Orchestrator: `gpt-5.5`, `medium`, platform-unverified.
- Sol architecture: `high`.
- Terra engineering: `medium`; independent criticism: `high`.
- Executor: bounded fixture/test work only, `low`.

## Work Order

| Step | Owner | Effort | Status | Definition of Done | Evidence | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Specify two required Stage A topology authorities | Sol architect | high | completed | Exact fixture leaf topologies, literal seals, expected raw authority records, adversarial cases and no-live boundary are defined | `handoffs/sol_stage_a_page_proof_topology_authorities_spec_20260809.md`; SHA-256 `23eccf5e...74eab630` | Terra architecture review |
| 2. Independently review topology specification | Terra critic | high | completed | Terra accepted raw-provenance/paint-only scope, literal seals and non-promotion boundary | `handoffs/terra_stage_a_page_proof_topology_authorities_architecture_review_20260809.md` | Implement fixture-only authority additions |
| 3. Implement sealed fixture authorities and QA | Terra engineer / executor | medium/low | remediation required | First implementation pass made no code/test changes; baseline only is `369 passed, 1 skipped` | `handoffs/terra_engineer_stage_a_page_proof_topology_authorities_implementation_20260809.md` | Split into two bounded authorities; restart with two-column only |
| 3a. Implement two-column Stage A authority | Terra engineer | medium | remediation required | Raw topology is correct, but Terra rejected candidate-generated assertion identity and non-resealed negative tests | `handoffs/terra_stage_a_two_column_authority_implementation_review_20260809.md`; `11 passed` non-acceptance evidence | Add literal assertion leaf and fully resealed target-only replay matrix |
| 3a-r. Independently review two-column authority | Terra critic | high | completed: remediation required | Terra confirmed raw-only non-geometric topology and baseline preservation, but found two P1 proof gaps | `handoffs/terra_stage_a_two_column_authority_implementation_review_20260809.md` | Correct only literal assertion / replay-matrix P1s |
| 3a-p1. Correct two-column literal assertion and adversarial replay proof | Orchestrator, after bounded engineer restart failed | medium | completed | Literal assertion leaf/facts/content identities are pinned; a fully valid artifact rejects only the privately resealed mismatching assertion and passes again with the accepted row | `handoffs/terra_stage_a_two_column_authority_literal_rereview_20260809.md`; focused `13 passed`; wider `372 passed, 1 skipped` | Implement nested-Form authority |
| 3b. Implement nested-Form Stage A authority | Orchestrator, recovery takeover after two empty engineer handoffs | medium | completed | Add only nested-form fixture after the accepted two-column authority is stable | handoffs/terra_stage_a_nested_form_implementation_review_20260809.md; focused 15 passed, wider 386 passed, 1 skipped | Aggregate the two accepted authorities |
| 4. Accept topology authorities | Terra critic | high | completed | Both exact authority hashes and topology assertions are independently accepted | Two-column receipt plus nested-Form receipt; fixture ids/hashes are pinned in the registry | Return their inventory identities to page-proof bundle |

## Hard Boundaries

- No live Innsmouth PDF, source, EN, Keeper, HTML, PDF, config or output access.
- No changes to `page_proof.py` or its tests in this bundle.
- No page-proof candidate or ledger can be constructed here.
- The fixtures must be synthetic/test-only and be valid except for exactly one
  targeted adversarial defect per negative case.
