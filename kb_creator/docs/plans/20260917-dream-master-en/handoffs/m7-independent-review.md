# M7 independent implementation/process review receipt

- Goal: `20260917-dream-master-en`; milestone: `M7`.
- Review kind: `implementation` with process-boundary coverage.
- Recommendation: `APPROVE_IMPLEMENTATION`.
- Candidate reviewed: immutable Stage 10 run
  `kb_creator/working/number-7-dream/publication/20260918-publication-01`;
  this is not a release review.
- Implemented or materially designed candidate: no.
- Role: independent critic. Orchestrator policy owner remains
  `gpt-5.6-sol`, medium; assignment state `platform-unverified`; scoped
  override: none. Orchestration ownership did not transfer.
- Timestamp: `2026-09-18T00:38:32+03:00`.
- Elapsed time: approximately 45 minutes.
- Token use: unavailable for exact platform accounting; approx 27k local review
  tokens.

## Files checked

- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260917-dream-master-en/plan.md`
- `kb_creator/docs/plans/20260917-dream-master-en/context.md`
- all prior M1-M6 receipts under
  `kb_creator/docs/plans/20260917-dream-master-en/handoffs/`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/__main__.py`
- `kb_creator/scripts/author_scenario_publication_contract.py`
- `kb_creator/inputs/number-7-dream/publication/v1/**`
- `kb_creator/contracts/number-7-dream.publication.json`
- accepted reconstruction package
  `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-16/promotion/reconstruction-upstream-v1`
- Stage 10 run
  `kb_creator/working/number-7-dream/publication/20260918-publication-01`
- current Git status and ignore boundary for Dream plan/input/contract/working
  paths.

## Evidence

- User authority remains scoped to reconstruction acceptance only. `plan.md`
  and `context.md` both record the exact user decision
  `файл реконструкции принят` as authorization for replay-16/v27 acceptance,
  and explicitly exclude `MASTER_EN`, translation, ArtView, HTML, DOCX, PDF,
  release, commit, and push.
- Accepted reconstruction package is bound by inventory
  `FDE1E1C5FAC2746203909C518046DD46AB2895770E3A4EEAEDE4F9CDAAFA15DA` and
  acceptance receipt
  `BFEF49D286A4A25F61CDAD2E8F2A1E8D51660BE6327EFEADB4C797F8D1B4607B`.
  Acceptance evidence includes `content/SEMANTIC_STRUCTURE.json` while the
  public upstream role interface remains the four required roles.
- `reconstruction_promotion.py` selects structural mode from sealed
  decision-set v2 plus audit v4 authority, validates `SEMANTIC_STRUCTURE.json`
  against audit/submission/page-decision identities, copies it byte-for-byte as
  subordinate content, and revalidates it on package reopen. Legacy packages
  remain sidecar-free. This is generic and fail-closed; it does not add a fifth
  publication role.
- The numbered-handout detector preserves legacy heading and handout-asset
  evidence, and in structural mode adds only full-line caption extraction from
  already validated `kind: handout` spans after the shared block-boundary
  transform. It rejects invalid spans and ambiguous multi-number spans, and it
  does not scan arbitrary prose.
- Focused tests cover the sidecar bridge, span-bound captions, figure-number
  disambiguation, narrative rejection, ambiguity, compact-boundary coordinates,
  exact four-role publication preflight, and existing-package validation.
  Reported focused evidence: promotion suite excluding stale live-fixture
  checks `19 passed, 1 skipped`; semantic/replay suites `30 passed`;
  authority tests `79 passed, 1 skipped, 255 subtests passed`.
- The combined affected suite result `428 passed, 3 skipped, 2 failures` is
  not treated as a blocker for this candidate. The two failures are the real
  `test_reconstruction_promotion.py` Dissociation replay-10 live-fixture checks
  and fail at `implementation_drift: producer_closure_changed:
  01-prepare-inputs` after producer code changed. That is documented
  historical-fixture debt: it proves the immutable fixture needs rebaseline or
  quarantine policy, not that the new Dream promotion bridge or Stage 10
  candidate is unsound.
- Publication authority is declarative and contract-authored:
  `kb_creator/inputs/number-7-dream/publication/v1/**` plus
  `kb_creator/contracts/number-7-dream.publication.json`. No Number 7
  Dream-specific Python route was added. The contract binds seven config roles,
  the shared terminology authority, author metadata `James Killick`, four
  upstream roles, and the generated contract SHA-256
  `EB23016E8890EB9D31F6338D8D9F395E49E537EF6F1D0ECDC728711BDCA207B8`.
- ArtView source template includes exactly 19 reader-facing assets and excludes
  the ten page-18 `reference_only` stat-block crops. Stage 10 upstream evidence
  still carries the full accepted upstream package, so excluded crops are not
  lost as provenance.
- Stage 10 is correctly stopped before acceptance/translation. The run folder
  has exactly one output directory, `10-master-en-candidate`; no
  `20-master-ru-candidate`, no run-local `MASTER_EN_ACCEPTANCE.json`, and no
  Stage 20 output exists. `MASTER_EN.qa.json` reports `status: pass`,
  `candidate_state: awaiting_master_en_acceptance`, and `errors: []`.
  `MASTER_EN.verification.json` reports
  `verified_candidate_pending_process_and_external_gates`.
- Candidate inventory is `24` files with inventory SHA-256
  `908381E7CBB0DE93AACCB012D2235E467E36A3E483C8D7108C74A55AF2AD1C52`.
  `MASTER_EN.md` is 75,692 bytes with SHA-256
  `4C154262D4BED6688BAB8BB3809DC33A4991AEF5DBD6B90575C5726A78E59945`;
  it contains 26 source-page markers and 19 Markdown image references. Asset
  manifest and candidate assets both count 19.
- M6 QA covers the previously known quote/statblock/line-flow surfaces:
  Elsie's quoted letter/list on page 14, seven textual quoted statblocks on
  page 18, quoted callouts/handouts on pages 17 and 19, and page 21-26
  pregenerated-character stat-line flow including page 23 ordering.
- Git boundary is adequate for the next explicit commit gate:
  `kb_creator/contracts/number-7-dream.publication.json`,
  `kb_creator/inputs/number-7-dream/publication/v1/`, and this goal plan tree
  are Git-visible/untracked, while `kb_creator/working/number-7-dream/` is
  ignored. Current reusable changes remain visible outside `working/**`.

## Findings

- P2 process debt, nonblocking: the two combined-suite failures should be
  recorded before final goal close as historical Dissociation live-fixture
  drift caused by `producer_closure_changed: 01-prepare-inputs`. Do not claim a
  clean full affected suite until that fixture is rebaselined, quarantined with
  explicit policy, or otherwise repaired. This does not block the Dream Stage
  10 implementation/process approval because the focused generic suites and
  current Dream run evidence pass.
- P3 documentation hygiene: M5 execution evidence is currently represented
  through M6 and live run files rather than a separate M5 handoff. The evidence
  is sufficient for this review, but the orchestrator should update canonical
  plan/context/status with the exact run identity, hashes, test caveat, and
  next gate.

## Blockers

None for implementation/process approval.

This receipt does not accept `MASTER_EN`, does not authorize translation or
Stage 20, and is not a release decision. Because this is not a release review,
release-specific candidate revision/manifest, freeze-time, QA-reference,
declared-exclusion, and mutation-invalidation checks are not final acceptance
gates here. Mutation rule for this review: any change to the Stage 10 run,
publication contract/inputs, accepted upstream package, or reviewed reusable
implementation invalidates this receipt and requires a new M7 review.

## Next gate

Orchestrator may update canonical docs/status and present the Stage 10
`MASTER_EN` candidate for explicit user acceptance. Do not run translation,
ArtView, HTML, DOCX, PDF, package, commit, push, or release acceptance until
the corresponding explicit gates are opened.
