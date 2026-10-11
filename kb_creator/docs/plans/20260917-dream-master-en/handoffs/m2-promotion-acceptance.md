# M2 promotion and reconstruction acceptance receipt

- Goal: `20260917-dream-master-en`; milestone: `M2`.
- Result: `ACCEPTED_RECONSTRUCTION_UPSTREAM_READY`.
- User authority: current Codex task, 2026-09-17, exact decision
  `файл реконструкции принят`.
- Source reconstruction: replay-16 / decisions-v27; Stage 01-06 remained
  immutable during promotion.

## Shared remediation completed before promotion

The first materialization attempt failed closed because the promotion bridge
predated structural Stage 06 products. Two generic consumer gaps were fixed:

1. `reconstruction_promotion.py` now validates, copies, inventories, reopens,
   and conditionally accepts the sealed v2/v4 `SEMANTIC_STRUCTURE.json`, while
   retaining exactly four public upstream artifact roles.
2. Numbered handout closure now recognizes full-line captions only inside
   validated semantic `kind: handout` spans, after the shared compact-boundary
   transform. Legacy heading/handout-asset evidence remains unchanged;
   arbitrary prose and unit IDs never satisfy the contract.

Reusable implementation and regression tests are Git-visible outside
`working/**`. No Dream-specific Python or hard-coded scenario literal was
added.

## Verification

- Focused promotion suite, excluding two historical Dissociation live-fixture
  tests whose Stage 01 producer closure has independently drifted:
  `19 passed, 1 skipped, 2 deselected`.
- Semantic-structure plus replay-resume suites: `30 passed`.
- Live read-only promotion preflight: `promotion_preflight_passed`.
- Run identity:
  `D80F35D17285D77E319A5E4B16A4F1207CE5415608ED95D56CE050B729A1BA98`.
- Stage 06 candidate inventory:
  `609657AA11554918A67A9955C7D5DCD3554A5E4B65A4E2305C556F3851D4D9A3`.
- Accepted reconstruction inventory:
  `FDE1E1C5FAC2746203909C518046DD46AB2895770E3A4EEAEDE4F9CDAAFA15DA`.
- Acceptance receipt:
  `BFEF49D286A4A25F61CDAD2E8F2A1E8D51660BE6327EFEADB4C797F8D1B4607B`.
- Acceptance evidence includes fixed path
  `content/SEMANTIC_STRUCTURE.json` in addition to the historical evidence
  set. The public inventory still exposes only `reconstructed_en`,
  `reconstruction_manifest`, `reconstruction_qa`, and `source_identity`.

Reopened package validation with `require_acceptance=True` passed. Original
Stage 06 identities remained:

- `RECONSTRUCTED_EN.md`: 76,478 bytes;
  `4DEE0DFBC694F1B9A48357A05F47EB34C2F6B1C5E107CC42475CE76444A9EAC9`.
- `SEMANTIC_STRUCTURE.json`: 28,528 bytes;
  `5EE164971DB442D2AEE650593FBAC8529511AC3F02E1F422B9738E41BAB073FE`.
- Stage 06 manifest:
  `B29B791F128CF0C259EA5E6BAB57DACC256B9AD0F07760F99F1F0EC126767337`.

## Scope boundary and next action

This receipt accepts only the reconstruction upstream. It does not accept a
future `MASTER_EN`, translation, ArtView, HTML, DOCX, PDF, release, commit, or
push. M3 must author the Dream publication authority through the generic
blueprint/contract author before a fresh Stage 10 run.
