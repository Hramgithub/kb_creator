# Independent architecture-amendment review receipt

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `5-scenario-contract-implementation-remediation-review`
- Review kind: `architecture`
- Reviewed candidate: `sol_architect_scenario_contract_step5_remediation_20260830.md`
- Role: independent critic
- Policy model: `gpt-5.5`
- Policy reasoning effort: `medium`
- Actual platform model/effort: `unavailable` (not exposed to this contributor)
- Orchestrator policy owner: main chat `gpt-5.6-sol`, `medium`
- Assignment state: `matched` by `nri-independent-critic`
- Scoped override: `none`
- Independence declaration: I did not implement or materially design this remediation amendment, the rejected Step 5 implementation, or the fixed ScenarioContract architecture.
- Implemented or materially designed candidate: no
- Timestamp: `2026-08-30T22:58:10+03:00`
- Elapsed time: approximately 3 minutes by Codex goal timer at pre-write checkpoint; approximately 25 minutes wall-clock including read-only evidence checks
- Token use: Codex goal counter reported `79276` tokens at pre-write checkpoint; final platform/role split unavailable
- Detached receipt SHA-256: computed after write; cannot be embedded in the hashed file without changing the hash

## Scope

This is a fresh independent review of the Step 5 remediation amendment as an
architecture amendment, not a release review. I did not verify a frozen release
candidate, release manifest, QA package for release acceptance, declared release
exclusions, or post-freeze invalidation beyond checking that the amendment does
not weaken those future release controls.

Owned write scope was exactly this receipt:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_scenario_contract_step5_remediation_review_20260830.md`

No implementation, material redesign, plan/context/status/release edit,
source/output/accepted/production/translator mutation, Git mutation, commit, or
push was performed.

## Candidate Identity

- Amendment path:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_scenario_contract_step5_remediation_20260830.md`
- Expected SHA-256:
  `211134E8BB2A642BC9E61B1670BD07894B68A2F2E134030A9058CC7395A8A58F`
- Verified SHA-256:
  `211134E8BB2A642BC9E61B1670BD07894B68A2F2E134030A9058CC7395A8A58F`
- Hash result: match

## Files Checked

Required files read:

- `D:\NRI\AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_scenario_contract_architecture_review_20260830.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_scenario_contract_implementation_packet_20260830.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_scenario_contract_implementation_20260830.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_scenario_contract_step5_remediation_20260830.md`

Supporting evidence inspected read-only:

- `.gitattributes`
- `kb_creator/contracts/scenario_contract.v1.schema.json`
- `kb_creator/contracts/innsmouth.json`
- `kb_creator/contracts/viral.json`
- `kb_creator/scripts/scenario_contract.py`
- `kb_creator/tests/test_scenario_contract.py`
- `kb_creator/scripts/build_innsmouth_reconstructed_en.py`
- `kb_creator/inputs/innsmouth/master_en/accepted_20260830_r6/MASTER_EN.acceptance.json`
- `kb_creator/inputs/innsmouth/production/PRODUCTION_MANIFEST.json`
- narrow memory context for prior Innsmouth fixture-only/non-authority constraints

## Files Changed

Changed:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_scenario_contract_step5_remediation_review_20260830.md`

Not changed:

- remediation amendment
- fixed architecture candidate
- plan/context/status/release files
- implementation code
- contracts
- tests
- source files
- accepted or production packages
- translator files
- Git index/history

## Verification And Evidence

- The remediation amendment hash matched the assigned SHA-256 exactly before
  review.
- Current plan records the main-chat orchestrator as `gpt-5.6-sol`/medium and
  the independent critic as `gpt-5.5`/medium; orchestration ownership does not
  transfer to this review.
- Current context records the first Step 5 implementation as rejected because
  Innsmouth raw source PDF byte count/page count/geometry were unavailable and
  the executor used placeholders instead of stopping (`context.md:188-212`).
- The rejected `innsmouth.json` confirms the failure class: it used
  `source.kind: external_pdf`, the retained Markdown candidate SHA as
  `source.sha256`, and positive placeholder values for byte count, page count,
  scope, and geometry.
- `build_innsmouth_reconstructed_en.py` confirms the separate identities the
  amendment relies on: retained Markdown candidate SHA at line 98, control-PDF
  SHA at line 99, final asset inventory SHA at line 101, reconstructed page
  marker domain at lines 528 and 545-558, and source/control hashes written to
  QA at lines 643-644.
- `MASTER_EN.acceptance.json` confirms reconstructed Markdown, QA, and asset
  evidence values used by the amendment.
- `PRODUCTION_MANIFEST.json` confirms the accepted stage manifest map and stable
  production artifact names used by the amendment.
- The rejected `scenario_contract.py` confirms the amendment's gap analysis:
  no duplicate-key loader, Boolean-as-integer exposure through ordinary integer
  checks, source resolution returning a path without file/hash/page/geometry
  verification, and canonicalization that cannot accept its own frozen view.
- The rejected `test_scenario_contract.py` confirms the test matrix was much
  smaller than the architecture/engineering packet required.
- Current `.gitattributes` contains the scoped
  `kb_creator/inputs/**/*.html text eol=lf` rule, and the amendment preserves it
  without broad renormalization or accepted-file mutation.

## Explicit Review Decisions

1. `contract_role=compatibility_shadow`, required-null unavailable raw-PDF
   fields, closed `compatibility_evidence`, and categorical rejection by
   `intake`, `reconstruction_ready`, and source resolution are fail-closed. They
   preserve Innsmouth compatibility evidence without turning the shadow into
   raw-source authority.
2. Keeping `source.kind=external_pdf` inside the shadow is semantically
   coherent because it is paired with `identity_status: incomplete`, required
   null identity/geometry fields, `contract_role: compatibility_shadow`, and
   rejection before filesystem access. It describes the missing authority class;
   it does not assert a runtime source.
3. The source-resolution observation boundary is secure enough for this slice:
   the API must reject shadows before probing paths, verify regular-file
   bytes/hash against runtime contracts, and compare caller-supplied page count,
   media box, and rotation. The amendment correctly states that a trusted PDF
   inspector is a future dependency and that no runtime build may rely on this
   API until such a caller exists.
4. Exact policies, gates, authorities, schema branching, strict type checks,
   duplicate JSON handling, frozen canonicalization, artifact suffix rules, and
   the exception anti-bypass model are complete, minimal, and testable for this
   six-path correction.
5. The compatibility evidence values/classes are sufficiently grounded in the
   current script and manifests. The closed evidence object is finite and
   descriptive; it is not a second production manifest and must not be imported
   by Innsmouth runtime scripts.
6. The same-six-path correction allowlist, LF proof, P2 searches, full-suite
   baseline handling, and UI-visible executor boundary are consistent with
   governance and avoid scope expansion. The executor receipt is a handoff
   artifact, not a seventh material product path.
7. The amendment does not conflict with the fixed seven-stage Viral runtime
   graph, exact Viral identity/roles/names, translation reference-only
   boundary, no-copy rule, or future full 124-page outputs.

## Findings

No P0 findings.

No P1 findings.

No P2 findings.

## Recommendation

`accept`

Material correction may begin under a bounded executor packet because no P0/P1
architecture findings remain. The executor packet must carry the amendment's
six-path allowlist, runtime-shadow rejection rules, source-resolution
observation API, closed policy/acceptance/exception vocabularies, test matrix,
LF proof requirements, and stop conditions without reopening architecture.

## Blockers

- No blocker to accepting this architecture amendment.
- Release approval remains out of scope and pending for a future frozen
  production candidate.
- Full-suite green status remains separately blocked by the pre-existing
  missing `kb_creator.pdf_raw` module families; the correction may only compare
  against that baseline and must not conceal or expand into it.
- A real Innsmouth runtime contract remains blocked until the exact
  authoritative source PDF identity, bytes, page count, and geometry are found
  and reviewed; the accepted shadow must stay non-runtime.

## Next Action

Main-chat orchestrator should record this amendment review, then dispatch a
UI-visible bounded executor correction against only the six material paths plus
its immutable receipt. Source reconstruction and publication remain blocked
until Step 5 correction, QA, and implementation review are complete.
