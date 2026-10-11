# Immutable Terra Architecture Review Receipt — Packet 4b.9 In-Place Salvage

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.9-in-place-salvage-architecture-review`.
- Role: fresh independent Terra critic; requested effort: `high`.
- Actual platform model/effort: `unavailable`; repository role assignment is platform-unverified.
- Review kind: `architecture`; non-release.
- Implemented the candidate under review: **no**.
- Materially designed the candidate under review: **no**. This review evaluates the Sol specification; it does not amend or redesign it.
- Orchestrator policy owner: main-chat `gpt-5.5` at `medium` (`platform-unverified`). Orchestration ownership remains with the main chat.
- Assignment state: `platform-unverified role policy`.
- Scoped override: `none`.

## Scope and independence

This is an independent pre-implementation review of the proposed in-place, fixture-only salvage contract. I did not implement or materially design the candidate or this specification. No release decision is made and this receipt does not transfer orchestration ownership.

## Result

**REMEDIATION REQUIRED — one P1 is open; do not assign implementation.**

The proposed boundaries, graph, oracle coverage, fail-closed public contract, and two-review sequence are otherwise architecturally appropriate. However, the specification does not state a unique canonical JSON preimage for its private inventory/root seals, so the mandated independent stdlib-only oracle cannot recompute the two root literals solely from the supplied contract.

## Verification/evidence and checklist

1. Independence, architecture/non-release classification, policy owner, assignment state, and no scoped override are recorded above.
2. Confirmed: `S0` is an unaccepted current seven-file snapshot only. The unavailable old fixture-leaves baseline is not an input, must not be guessed or reconstructed, and partial rollback is prohibited.
3. Confirmed: section 3 is a bounded later write set. Existing candidate test files may change only for a demonstrated named invariant plus downstream identity reseals; the preferred success set is the new oracle and executor receipt. `page_proof.py`, Stage A, canonical plan/context/status/contract, production roots/public surface, and release files remain read-only.
4. Independently checked the two literal 4b.8 child records from the accepted aggregate receipt. Canonical compact UTF-8 JSON with sorted keys, omitting only each child `content_sha256`, recomputes respectively to `74ddca65755dbde190b57a5e82368895644ac6b605873913c20a32f2786d6526` and `136489ff1892bb27b8425806a1972809d03ce5e5e22f42b6a9f1bdfeca1cc503`. The documented entry-domain formula independently recomputes the two entry seals to `31a05f30ebd7919f27191f2986c679c32c6fb739724a5364bdaef1d3b8b04673` and `e7693b62761befda746fb405e1f6f5c89bca6ad91fea877110cd1e4a9d0844f6`. Root-seal reproduction is the P1 below.
5. The specified graph is acyclic: `C -> E -> I -> T -> P -> W -> M/E -> V -> F`. `P` excludes `W`, `V`, `F`, visual/final predicates, and both expected-output hashes; `F` is last and binds exact W/render/V identities. No cycle, fixed-point, retry, or fallback is authorized.
6. The required oracle/test mapping is concrete: 4b.6 is covered by oracle test 12 plus retained exact visual assertions (four positives, 46 named targets, two envelopes, target-only inverse repair); 4b.7 by tests 6, 8, 9, and 12 plus retained composition assertions; 4b.8 by tests 1-4 and 12; and 4b.9 by tests 5-11 and 12. The retained exact regressions are supplementary, not historical-hash-only acceptance evidence.
7. Subject to the P1 repair, the oracle design is independent: expected primitives, semantic baselines, target names, and source-structure facts are literal in the new module; seals are stdlib-only; production is SUT only; receipt/runtime derivation is forbidden; and named target-only mutations require inverse repair.
8. Confirmed mandatory exact containment/composition: visual calls/targets/adjacent contracts remain `98/46/96`; WitnessV3 remains same-witness private `W -> M -> E -> V`, with no separate or inferred flow route.
9. Confirmed: all production roots remain inactive and all three real public APIs may receive poison objects only, failing coverage-first before caller access. No candidate/review/replay/result/terminal object, activation, or expected-output-hash consumption is authorized.
10. The stated command roots and exact counts (`159 collected`, `159 passed`, upstream `15 passed`, and `386 passed, 1 skipped`) are deterministic. The rejection triggers, hard prohibitions, and required sequence of this architecture review followed by a different Terra/high implementation review are sufficient only after P1 is corrected.

## Severity findings

### P0

None.

### P1

**P1 — private inventory/root seal preimage is underspecified.** The salvage specification supplies the two child records, exact entry values, expected entry seals, and expected inventory/content seals, but does not declare the exact JSON object (field names and value shape) hashed for `inventory_sha256`. The inherited wording says only `{required_topology_ids, entry_count, ordered entry_sha256 values}`. Using that documented formula with canonical JSON and the explicitly named `entry_sha256s` field yields inventory `6b65dd4be5979e0a961b3dc41924318cb32c6981d90b683e8097c8c7f3698c28`, not the required `3d707193bfe883dbe510e1ccdc169ac21e28c7b3a8fda697446a126fae7cdfd6`; the resulting closed-root content seal is `9eabf52ab8106512f6ed4eb197d1ba28d5277891809e43d1b994567a992d0a9b`, not `4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4`.

This does not establish that either target literal is wrong. It establishes that the contract does not provide a uniquely reproducible preimage. An executor could otherwise obtain the answer only from existing implementation or candidate state, contrary to the independent-oracle rule. Sol must issue a new immutable clarification that states the exact inventory-hash payload and the exact root object used for content hashing; it must preserve all current no-live/no-production/no-public-result boundaries. A fresh Terra/high architecture review is then required.

### P2

None.

## Files checked

- `D:\NRI\AGENTS.md`
- `D:\NRI\docs\governance\nri_goal_governance.md`
- `D:\NRI\kb_creator\PROJECT_STATUS.md`
- `D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\NEW_CHAT_HANDOFF_20260811.md`
- `D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\plan.md`
- `D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\context.md`
- `D:\NRI\kb_creator\docs\contracts\page_level_consumer_proof_contract_status.md`
- `D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\handoffs\sol_page_proof_packet_4b9_in_place_salvage_spec_20260811.md`
- Relevant prior evidence only: the accepted 4b.8 aggregate receipt and the prior inventory/reseal specification/clarification needed to verify the stated child and seal formulas.

## Files changed

- `D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\handoffs\terra_page_proof_packet_4b9_in_place_salvage_architecture_review_20260811.md` — this immutable receipt only.

## Exclusions and blockers

No implementation, current candidate/test-source inspection, live Innsmouth PDF, EN source, KeeperBook, HTML, PDF, output/build, Git, network, browser, production activation, public terminal/result, release path, or partial rollback was performed. The open P1 blocks implementation; all live, production, and release paths remain blocked independently.

## Recommendation and next action

Recommendation: **remediation_required**. The main-chat orchestrator should request one bounded Sol clarification that supplies the exact independent inventory/root canonical-hash preimages, then assign a fresh independent Terra/high architecture review. Do not assign an executor before that review accepts with no P0/P1.

## Accounting

- Elapsed active review time: approximately `5 minutes`.
- Token use: `unavailable` (not exposed to this contributor).
- Timestamp: `2026-08-11T21:36:29+03:00`.

This receipt is immutable. Any correction or supersession must be a new handoff. It does not edit canonical state, accept implementation, authorize a release, or transfer orchestration ownership.
