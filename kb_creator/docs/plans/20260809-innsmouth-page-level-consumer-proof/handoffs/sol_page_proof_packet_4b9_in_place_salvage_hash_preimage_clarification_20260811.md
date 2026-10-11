# Immutable Sol Clarification Receipt — Packet 4b.9 Inventory/Root Hash Preimages

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.9-in-place-salvage-hash-preimage-clarification`.
- Role: Sol architect; requested reasoning effort: `high`.
- Actual platform model/effort: `unavailable`; the repository role assignment is platform-unverified.
- Scope: remediate only Terra's single P1 concerning the exact private `inventory_sha256` and root `content_sha256` preimages. This receipt is an architecture clarification, not implementation, implementation acceptance, or release review.
- Result: **clarified; both existing target root literals reproduce exactly from the closed contract below.**
- Orchestrator policy owner: main-chat `gpt-5.5` at `medium` (`platform-unverified`). Orchestration ownership remains with the main chat.
- Assignment state: `platform-unverified role policy`.
- Scoped override: `none`.

## Remediation decision and dependency boundary

This receipt clarifies only the `E -> I` edge in the existing acyclic
`C -> E -> I -> T -> P -> W -> M/E -> V -> F` graph. The two accepted entry
seals remain, in order:

1. `31a05f30ebd7919f27191f2986c679c32c6fb739724a5364bdaef1d3b8b04673`
2. `e7693b62761befda746fb405e1f6f5c89bca6ad91fea877110cd1e4a9d0844f6`

The first seal belongs only to `stage_a_positive_two_column.v1`; the second
belongs only to `stage_a_positive_nested_form.v1`. They may not be swapped,
duplicated, omitted, substituted, or derived from production/candidate state.

## Exact canonical JSON and byte contract

For both hashes, canonical JSON is exactly the byte result equivalent to:

```python
json.dumps(
    value,
    ensure_ascii=True,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
```

The fixed payloads contain only JSON objects, arrays, strings, and one integer,
so the remaining `json.dumps` defaults cannot alter these bytes. There is no
BOM, newline, trailing NUL, indentation, or insignificant whitespace. Object
keys are ordered by `sort_keys=True`; array order is preserved exactly. All
SHA-256 results are lower-case hexadecimal strings.

### `inventory_sha256`

The hash input is the ASCII domain separator
`page-proof.required-stage-a-topology-inventory.v1`, followed by exactly one
NUL byte `0x00`, followed immediately by the UTF-8 canonical JSON bytes below:

```json
{"entry_count":2,"ordered_entry_sha256":["31a05f30ebd7919f27191f2986c679c32c6fb739724a5364bdaef1d3b8b04673","e7693b62761befda746fb405e1f6f5c89bca6ad91fea877110cd1e4a9d0844f6"],"required_topology_ids":["stage_a_positive_two_column.v1","stage_a_positive_nested_form.v1"]}
```

The payload has exactly three fields:

- `entry_count`: JSON integer `2`;
- `ordered_entry_sha256`: a two-element JSON array of the exact entry-seal
  strings in the exact topology order above; the field name is singular
  `ordered_entry_sha256`, not `entry_sha256s` or any alias;
- `required_topology_ids`: a two-element JSON array in the same exact order.

The payload omits `schema`, full `entries`, `inventory_sha256`, and
`content_sha256`. Therefore:

```text
SHA256(
  UTF8("page-proof.required-stage-a-topology-inventory.v1") ||
  0x00 ||
  canonical_inventory_payload
) = 3d707193bfe883dbe510e1ccdc169ac21e28c7b3a8fda697446a126fae7cdfd6
```

### Root `content_sha256`

The content hash has **no domain separator**. Its complete preimage is exactly
the UTF-8 canonical JSON bytes of the closed root below:

```json
{"entries":[{"entry_sha256":"31a05f30ebd7919f27191f2986c679c32c6fb739724a5364bdaef1d3b8b04673","independent_stage_a_review_content_sha256":"74ddca65755dbde190b57a5e82368895644ac6b605873913c20a32f2786d6526","independent_stage_a_review_decision":"accept","independent_stage_a_review_kind":"fixture_topology_acceptance","positive_topology_assertion_sha256":"e681b6ffbed2705283b915039e1d7a6ac145f4988765fd772a68eb63803831c8","reviewed_authority_content_sha256":"890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef","stage_a_authority_content_sha256":"890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef","stage_a_authority_inventory_sha256":"3173d033fcf6228687388f020f0e5e6e7e9c1ce2a373bc1b2bca49823ab951c0","stage_a_authority_schema":"kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1","stage_a_fixture_binding_sha256":"c41ec7ae9eea7d5fc2f654eb825bf1bb1af954d00c754fd6140f134985af8880","stage_a_fixture_id":"stage-a.positive-two-column.v1","topology_id":"stage_a_positive_two_column.v1"},{"entry_sha256":"e7693b62761befda746fb405e1f6f5c89bca6ad91fea877110cd1e4a9d0844f6","independent_stage_a_review_content_sha256":"136489ff1892bb27b8425806a1972809d03ce5e5e22f42b6a9f1bdfeca1cc503","independent_stage_a_review_decision":"accept","independent_stage_a_review_kind":"fixture_topology_acceptance","positive_topology_assertion_sha256":"a82adc738fd89394e80a607df46f7775a1967f874267f3b0289e7e64829d3d0f","reviewed_authority_content_sha256":"8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7","stage_a_authority_content_sha256":"8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7","stage_a_authority_inventory_sha256":"f296a28a72e509f47fe294217492cc463375c30144f8deab57fd7b4c85678b21","stage_a_authority_schema":"kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1","stage_a_fixture_binding_sha256":"9b0f9f382e7926e3447072fa9340c38dd93531302e4294a14d8436eeacdf1d0a","stage_a_fixture_id":"stage-a.positive-nested-form.v1","topology_id":"stage_a_positive_nested_form.v1"}],"entry_count":2,"inventory_sha256":"3d707193bfe883dbe510e1ccdc169ac21e28c7b3a8fda697446a126fae7cdfd6","required_topology_ids":["stage_a_positive_two_column.v1","stage_a_positive_nested_form.v1"],"schema":"PageProofRequiredStageATopologyInventory.v1"}
```

The root preimage includes exactly five top-level fields: `entries` (the two
complete closed entry objects in topology order, including each
`entry_sha256`), `entry_count`, `inventory_sha256`,
`required_topology_ids`, and `schema`. It omits exactly one root field:
`content_sha256`. No entry field is omitted. Therefore:

```text
SHA256(canonical_closed_root_without_content_sha256)
= 4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4
```

## Independent-oracle acceptance criteria

A fresh Terra/high architecture critic can reproduce the targets using only
the two literal JSON preimages, the stated domain bytes, UTF-8, canonical JSON
settings, and a standard SHA-256 implementation. The critic must not import or
read production helpers, parse candidate state, derive expected values from a
receipt at test runtime, or select a different self-consistent root.

Acceptance of this clarification requires all of the following:

1. The inventory preimage reproduces exactly
   `3d707193bfe883dbe510e1ccdc169ac21e28c7b3a8fda697446a126fae7cdfd6`.
2. The closed-root preimage reproduces exactly
   `4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4`.
3. The critic confirms the exact field sets, value shapes, sorted object-key
   order, preserved array order, single inventory domain NUL, no content
   domain, and the stated inclusion/omission rules.
4. Any mismatch is a blocker. It may not be resolved by changing either target,
   inventing an alias, reading candidate literals, or widening the packet.

## Scope preservation, risks, and sequencing

This clarification does not change the `S0` decision, old-baseline
prohibition, no-partial-rollback rule, allowed write set, command counts
(`159 collected`, `159 passed`, `15 passed`, and `386 passed, 1 skipped`),
oracle/test mapping, no-live/no-production/no-public/no-Git/no-output/build/
no-release boundaries, or implementation prohibition. Production code and
roots remain read-only and inactive; no public result or terminal is
authorized.

The only remediated ambiguity is the singular field name
`ordered_entry_sha256` and the fully enumerated content-root preimage. Principal
rejection risks are pluralizing or aliasing that field, including `schema` or
full entries in the inventory payload, applying the inventory domain to the
content hash, omitting `entry_sha256` from a content entry, changing either
array order, or hashing the final `content_sha256` field into itself.

The two-review sequence remains mandatory: first, a fresh independent
Terra/high architecture review of this clarification; only after acceptance may
the orchestrator assign one bounded executor; a different fresh Terra/high
critic must then review implementation and evidence. Neither review is a
release review, and orchestration ownership does not transfer.

## Evidence and accounting

- Files checked: `D:\NRI\AGENTS.md`;
  `D:\NRI\docs\governance\nri_goal_governance.md`; assigned `plan.md`,
  `context.md`, and `NEW_CHAT_HANDOFF_20260811.md`;
  `docs/contracts/page_level_consumer_proof_contract_status.md`; the assigned
  Sol in-place-salvage specification; Terra's rejecting architecture receipt;
  the immutable 4b.8 aggregate acceptance, original packetization, post-4b.8
  inventory/reseal, literal-reseal, and 4b.1 remediation/review receipts; and
  read-only `kb_creator/pdf_raw/page_proof.py` solely to corroborate the
  previously omitted payload field name and canonical serializer settings.
- Files changed: only
  `D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\handoffs\sol_page_proof_packet_4b9_in_place_salvage_hash_preimage_clarification_20260811.md`.
- Verification/evidence: literal-only, in-memory .NET SHA-256 checks over the
  bytes printed in this receipt reproduced both accepted entry seals, then
  reproduced inventory
  `3d707193bfe883dbe510e1ccdc169ac21e28c7b3a8fda697446a126fae7cdfd6`
  and content
  `4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4`.
  No production module was imported or executed; no candidate test state,
  public API, live/source/output/build path, network, browser, Git, production
  activation, terminal result, implementation test, or release path was used.
- Blockers: none to a fresh independent Terra/high architecture review.
  Implementation and all live, production, public-result, and release paths
  remain blocked pending that acceptance and the unchanged later sequence.
- Next action: the main-chat orchestrator assigns a fresh independent
  Terra/high architecture review limited to the four acceptance criteria above.
  Do not assign implementation unless that review reports no P0/P1.
- Elapsed active time: approximately `18 minutes`.
- Token use: `unavailable` (not exposed to this contributor).
- Timestamp: `2026-08-11T21:45:39.9286453+03:00`.

This receipt is immutable. Any correction must be a new handoff that explicitly
supersedes this file. It does not edit canonical plan/context/status/contract,
transfer orchestration ownership, authorize implementation, accept a candidate,
or act as the final release reviewer.
