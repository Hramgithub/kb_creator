# Independent architecture review receipt

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `4-independent-architecture-review`
- Review kind: `architecture`
- Role: independent critic
- Policy model: `gpt-5.5`
- Policy reasoning effort: `medium`
- Actual platform model/effort: `unavailable` (not exposed to this contributor)
- Orchestrator policy owner: main chat `gpt-5.6-sol`, `medium`
- Assignment state: `matched` by `nri-independent-critic`
- Scoped override: `none`
- Independence declaration: I did not implement or materially design the candidate under review.
- Implemented or materially designed candidate: no
- Timestamp: `2026-08-30T20:22:57+03:00`
- Elapsed time: approximately 4 minutes by Codex goal timer at pre-write checkpoint; approximately 30 minutes wall-clock including sandbox approval retries
- Token use: Codex goal counter reported `51752` tokens at pre-write checkpoint; final platform/role split unavailable

## Scope

Reviewed the assigned `ScenarioContract.v1` architecture candidate without
editing it. This is not a release review. I did not verify a frozen release
candidate, candidate revision manifest, QA references for release acceptance,
declared release exclusions, or release invalidation beyond checking that the
architecture defines those future requirements.

Owned write scope was exactly this receipt:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_scenario_contract_architecture_review_20260830.md`

Forbidden scope was honored: no implementation, material redesign, source
processing, Innsmouth/Sourcefold mutation, canonical plan/context/status/release
edit, Git mutation, commit, or push.

## Candidate Identity

- Candidate path:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md`
- Expected SHA-256:
  `EF96C3B155EB749FBABDFEA5B86BD4C190854F3029D8693E7F09D051F4B9FDBE`
- Verified SHA-256:
  `EF96C3B155EB749FBABDFEA5B86BD4C190854F3029D8693E7F09D051F4B9FDBE`
- Hash result: match
- Candidate status in document: architecture candidate only; no implementation
  authorized (`scenario_contract_architecture.md:7-8`).

## Files Checked

Required files read:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_scenario_contract_20260830.md`
- `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`

Supporting evidence inspected read-only:

- `.gitattributes`
- Git `core.autocrlf`
- Git EOL attributes for accepted/production Innsmouth HTML
- Git index blob identity for accepted/production Innsmouth HTML
- `kb_creator/scripts/*innsmouth*.py` inventory
- `kb_creator/tests/*innsmouth*`, `*freeze*`, `*production_package*`,
  `*scenario_contract*`, and prior page-proof test inventory
- Innsmouth accepted-stage acceptance manifests and
  `kb_creator/inputs/innsmouth/production/PRODUCTION_MANIFEST.json`
- `translator/config/viral.package.json` as legacy evidence only
- Narrow memory registry and rollout summary for prior Innsmouth fixture-only
  proof constraints; used only to confirm non-authority and independence
  context, not as current product evidence

## Files Changed

Changed:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_scenario_contract_architecture_review_20260830.md`

Not changed:

- candidate architecture
- plan/context/status/release files
- implementation code
- contracts
- tests
- source files
- accepted or production packages
- Git index/history

## Verification And Evidence

- Candidate hash was verified before review and matched the assigned digest.
- Worktree status before receipt writing showed branch `codex/kb-creator-viral`
  with untracked goal documentation only:
  `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md` and
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/`.
- Governance confirms the critic must not implement or materially design the
  candidate and that contributor assignments never transfer orchestration
  ownership.
- The candidate fixes the stage graph in trusted reusable code
  (`scenario_contract_architecture.md:12-23`) and keeps scenario facts and
  reviewed policies in a non-executable contract
  (`scenario_contract_architecture.md:25-35`).
- The candidate explicitly rejects a configurable second graph
  (`scenario_contract_architecture.md:121-123`), arbitrary executable fields
  (`scenario_contract_architecture.md:291-294`), copied Viral stage scripts
  (`scenario_contract_architecture.md:625-627`), and legacy Viral config as
  runtime dependency (`scenario_contract_architecture.md:628-631`).
- The context verifies the current code reality: `23` Innsmouth-named scripts
  still pin paths, hashes, counts, and structural expectations
  (`context.md:47-56`; pipeline summary `:190-197`).
- `translator/config/viral.package.json` contains absolute local paths, tool
  paths, engine command arrays, old output paths, historical gates, and
  `production_approved: false`; the candidate correctly treats it as legacy
  evidence only, not authority.
- `rg` over current `kb_creator` found no implementation script family named
  `build_viral_` or `freeze_viral_`; current matches are only review docs.
  Existing translator scope files still reference `translator/config/viral.package.json`,
  so future acceptance evidence must scope the search to the implementation
  surface being reviewed.
- Current `.gitattributes` starts with `* text=auto` and has no scoped HTML LF
  rule. `git config --get core.autocrlf` returned `true`.
- `git ls-files --eol` reports accepted and production Innsmouth HTML as
  `i/lf w/crlf attr/text=auto`.
- Live production HTML SHA-256 was
  `BC66D5A2380288B23B8FBED9E85533EE120010A85E408C8DA5E3925A34DF2B49`, while
  `PRODUCTION_MANIFEST.json` binds `The_Innsmouth_Terror_RU.html` to `226114`
  bytes and SHA-256
  `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`.
- `python -B kb_creator/scripts/build_innsmouth_production_package.py --verify`
  failed read-only with `ValueError: production package file identity mismatch`,
  consistent with the documented CRLF checkout issue.
- `git ls-files -s` reports the same Git blob id
  `327c4f2a2d30468f8895213b295324e2457af67b` for both accepted and production
  Innsmouth HTML, supporting the candidate's claim that the prerequisite must
  preserve Git blob identities rather than re-manifest accepted artifacts.

## Findings

### P1 - First implementation slice still depends on unresolved concrete Viral artifact names

The architecture says exact stable Viral HTML/PDF filenames are not yet
user-approved and only proposes `Viral_RU.html` / `Viral_RU.pdf`
(`scenario_contract_architecture.md:127-129`). The illustrative contract keeps
`artifacts.html` and `artifacts.pdf` as `<review-required>`
(`scenario_contract_architecture.md:253-259`), while the invariant table says
artifact names must be safe, relative, unique basenames
(`scenario_contract_architecture.md:291`). The first implementation slice then
adds `kb_creator/contracts/viral.json` and requires schema/semantic validation
to pass for both reviewed contracts (`scenario_contract_architecture.md:643-654`,
`:674-680`).

Why this matters: if implementation begins as written, engineering must either
encode placeholders that violate the stated artifact-name invariant, silently
promote unapproved proposed names into authority, or weaken validation profiles
without an explicit architectural rule. That reopens architecture during the
first implementation slice and undermines the "closed declarative contract"
boundary.

Required remediation before material implementation: orchestrator must record
one explicit decision in canonical state and the candidate or implementation
packet must reflect it without changing scope:

- approve exact Viral HTML/PDF basenames before `viral.json` validation; or
- split `viral.json` into an intake-only contract whose render artifact names
  are absent under a declared profile and whose tests prove render/html/pdf
  stages are blocked until those names are supplied; or
- remove `viral.json` validation from the first slice and limit the slice to
  schema/loader plus Innsmouth shadow facts and Viral intake identity only.

Material implementation may not begin until this P1 is resolved by the
orchestrator.

### P2 - Acceptance evidence search for forbidden legacy imports needs exact scope

The candidate requires acceptance evidence that `rg` finds no
`build_viral_`/`freeze_viral_` family and no import of
`translator/config/viral.package.json` (`scenario_contract_architecture.md:699-706`).
In the live checkout, a broad search finds intended architecture-document
mentions and existing legacy translator scope files that reference the config.
That is not a policy violation, but a naive repository-wide command would be
ambiguous or noisy.

Required remediation: define the acceptance command scope precisely, for
example limiting the search to `kb_creator/scripts`, `kb_creator/contracts`,
and `kb_creator/tests`, and distinguish "no runtime import/dependency" from
"no textual mention in docs or legacy translator config".

## Non-Findings

- No P0 findings.
- No finding against the fixed stage graph. It matches the accepted Innsmouth
  lifecycle in the pipeline summary (`KB_CREATOR_PIPELINE_SUMMARY_20260830.md:14-28`)
  and keeps future alternate graphs outside v1.
- No finding against the data/mechanics split. The candidate keeps build,
  freeze/promote, verify, inventory, provenance validation, asset closure, and
  evidence freshness in reusable code (`scenario_contract_architecture.md:32-35`).
- No finding against page taxonomy or coverage. The candidate requires one
  primary role over every page with no gaps/overlaps
  (`scenario_contract_architecture.md:288-290`), separates content mode and
  traits, and blocks `reconstruction_ready` until pages 1-5 and unknown modes
  are closed (`scenario_contract_architecture.md:334-336`, `:674-676`).
- No finding against translation lineage. The candidate requires the current
  accepted `MASTER_EN` as the sole translation source and permits historical
  EN/RU only as reference evidence, matching the plan/context boundary.
- No finding against exception controls. The v1 exception kinds are closed,
  stage-scoped, evidenced, match-counted, and approval-gated; forbidden
  exceptions cannot bypass identity, coverage, provenance, manual-edit
  prohibition, or release review.
- No finding against asset closure or full-scope QA. The candidate requires
  inventoried assets, one semantic owner unless reviewed reuse is declared,
  closure for every source-required visual/page, and full-scope defect-class
  closure before promotion.
- No finding against the Innsmouth shadow-contract boundary. The first slice
  keeps it as a fixture assembled from current accepted manifests and script
  constants, not runtime authority, and stops if required facts are absent
  (`scenario_contract_architecture.md:669-672`).
- No finding against the scoped `.gitattributes` prerequisite. Live Git evidence
  supports the `core.autocrlf=true` / manifest-bound HTML issue, and the
  candidate correctly rejects verifier normalization and re-manifesting while
  requiring clean-checkout proof (`scenario_contract_architecture.md:609-612`,
  `:633-637`, `:694-704`, `:779-780`).
- No finding that copied `build_viral_*`/`freeze_viral_*` or legacy config
  authority has been introduced in the current candidate.

## Recommendation

`accept_with_conditions`

The architecture is sound enough to accept after orchestrator resolution of the
P1 artifact-name/profile conflict. Material implementation must not begin while
that P1 remains open. After resolution, the first slice should remain limited
to the six declared paths and include the scoped LF checkout proof plus the
precise forbidden-import search described in P2.

## Blockers

- P1 above blocks material implementation until resolved and recorded by the
  orchestrator.
- Release approval is not in scope and remains pending for a future frozen
  production candidate.

## Next Action

Main-chat orchestrator should resolve the Viral render artifact-name/profile
decision, record it in canonical plan/context state, and then dispatch the
minimal implementation slice only if no P0/P1 findings remain.
