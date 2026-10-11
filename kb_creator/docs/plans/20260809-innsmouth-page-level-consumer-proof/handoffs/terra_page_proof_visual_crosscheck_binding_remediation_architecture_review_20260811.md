# Independent Terra Architecture Review — Packet 4b.6-r binding remediation

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.6-r-architecture-review`.
- Review kind: `architecture`; this is not an implementation or release review.
- Role: Terra independent critic; requested effort `high`.
- Actual model/effort: `platform-unverified`.
- Implemented or materially designed candidate: **no**.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`).
- Assignment state: `platform-unverified`.
- Scoped override: this review receipt only; no code, test, canonical plan/context/status, output, Git, parser, renderer, live/source, filesystem-leaf, browser, network, subprocess, or release work.

## Verdict

**Accepted — the Sol P/F remediation specification is architecture-sound.**

It removes both former full-binding back-edges without weakening the inactive public fail-closed boundary.  This accepts the *specification only*; implementation, the prescribed target-only matrix, bounded regression, and a fresh Terra implementation-remediation review remain required before Packet 4b.6 can be accepted.  It does not authorize production activation, Packet 4b.7, or release work.

## P0 / P1 / P2 findings

### P0

None.  `P` commits only stable identity, Stage-A/topology identity, and the exact render leaf pair.  `W` and `V` carry `P`, never `F`; `F` then commits `P` plus the exact final W/render/V leaf pairs.  A substituted W, render, or V cannot be admitted downstream under `F`, and neither W nor V needs the value that seals its own bytes.

### P1

None in the proposed architecture.  The required construction sequence is genuinely acyclic:

```text
identity + Stage-A/topology + render -> P
P -> W -> mechanics/flow E
P + E -> V
P + W/render/V leaf pairs -> F
F -> candidate/review/ledger projection
```

There is no edge from W, E, V, candidate, review, expected-output hashes, or F into P; no edge from F back to W or V; and expected-output hashes remain outside both seal payloads.  This directly eliminates the current `V -> F -> V` and `W -> F -> W` cycles documented by the two preceding Terra receipts.

### P2

None.  The one implementation-sensitive point is already explicit in the Sol Definition of Done: the eventual receipt must demonstrate the actual predicate vector, not infer reachability from the shared public error.  That evidence belongs in the future implementation review, not a scope expansion now.

## Admission and target-predicate review

The specified pre-normalizer contract is sufficient and non-circular for every positive, adversarial, and repaired case:

1. derive P once from immutable non-visual inputs;
2. make W and its content seal current, normalize mechanics/flow from that exact W/render pair, and build V with P and resulting E;
3. reseal only V's dependent closure, set exact W/render/V length-and-SHA pairs in the row, and derive F once;
4. prove `_fixture_pre_visual_binding_is_valid`, `_fixture_admission_is_valid`, and `_fixture_admission_row_matches_derive_leaves` before calling the visual normalizer;
5. directly assert the intended named visual predicate false with the applicable non-target predicates current; repair only the semantic target, reseal its dependent closure, and re-run the same admission proof.

This prevents both prior false-positive forms of evidence: a stale outer V leaf cannot pose as an internal visual failure, and an interim row cannot pose as a valid admission after the V root is rebound.  The separately required stale-row and stale-V envelope tests remain correctly outside the internal matrix.

The required fourth private boundary variant is necessary and sufficient: it supplies two ordered boundaries so reordering is a material negative rather than a vacuous one.

## Oracle and containment review

The oracle boundary is independent in the material sense required here.  Literal fixture leaves/P/F constants are one anchor; test-side explicit canonical JSON/SHA-256 field lists are a second; production recomputation is only compared against them, never used to create them.  The prescribed ban on production sealing/normalization calls in oracle construction, import-time derivation, loops, and post-root patches rules out the former circular test construction.

The executor scope is both sufficient and minimal.  It includes the sole production module and precisely the dependent row/root, leaf, closed-schema, mechanics/flow, topology-constructor, admission, and visual-matrix tests.  The current public coverage guard need only be run: public signatures and coverage-first failure behavior do not change.  Its existing import/call containment, together with the mandated focused AST assertions in an allowed affected test, is enough to establish that P helpers only use row fields, canonical JSON, SHA-256, and literal schema/domain strings.  No live/source/output/Git/network/parser/renderer dependency or consumer activation is authorized or needed.

## Implementation acceptance criteria

The future executor evidence is acceptable for a fresh Terra implementation-remediation review only if all of the following are true:

- `PageProofFixtureAdmission.v2`, WitnessV2, and CrossCheckV2 use the exact field sets, schemas, domain separators, and P/F formulas in the Sol handoff; closed W/V roots contain P and no final `binding_sha256` field.
- `_fixture_admission_is_valid` recomputes both P and F, and every internal positive/adversarial/repaired matrix call proves admission validity and exact W/render/V tuple matching before normalizer entry.
- Each internal negative reaches its named predicate with current dependent seals and an explicit predicate vector; the repair restores only its semantic mutation and reproduces the baseline normalized output.
- Literal P/F constants agree independently with both the stdlib-only oracle and production recomputation; no helper imports or calls production hash/normalizer code to manufacture expected values.
- The two outer-envelope failures remain distinct from the valid-admission internal matrix; the real multi-boundary reorder case exists.
- Production registries remain empty; public error precedence/signatures and no-output behavior remain unchanged; static containment confirms no prohibited dependency or F back-edge; only the Sol-allowed files and the executor receipt change.
- The seven named target suites pass in the bounded command, followed by a new independent Terra implementation-remediation review.  This architecture receipt alone is not that evidence.

## Files checked and review limits

- `AGENTS.md` and `docs/governance/nri_goal_governance.md`.
- Sol binding-remediation specification and both preceding Terra 4b.6 review receipts.
- `kb_creator/pdf_raw/page_proof.py`.
- `kb_creator/tests/test_page_proof_visual_crosscheck.py` and `kb_creator/tests/_page_proof_fixture_leaves.py`.
- Dependent admission, closed-schema, witness/render, flow, topology, coverage-guard, and Stage-A contract test references were statically searched to validate scope.

No tests, parser/renderer, browser/network, live materials, output, or Git operation were run.  No code or test was changed; this immutable receipt is the sole write.

## Blockers and next action

- Current blocker: implementation of the accepted bounded specification and its evidence; not an architecture blocker.
- Standing separate blocker: accepted `fixture_topology_acceptance` review-content hashes remain absent, so public admission/coverage must remain inactive.
- Next action: assign the bounded executor exactly to the Sol file scope, then request the specified fresh Terra implementation-remediation review.  Do not start Packet 4b.7 from this architecture acceptance alone.

- Timestamp: `2026-08-11T13:59:09+03:00`.
- Token use: `unavailable` at receipt authoring time.

This immutable architecture receipt does not transfer orchestration ownership and is not release acceptance or authorization to activate production coverage.
