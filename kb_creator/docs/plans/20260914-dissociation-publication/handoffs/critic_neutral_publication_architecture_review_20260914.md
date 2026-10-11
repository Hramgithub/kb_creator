# Independent critic receipt - neutral publication architecture review

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PR-neutral-publication-architecture-process-review`
- Review kind: `architecture + process`
- Role: independent critic
- Requested model: `gpt-5.5`
- Requested reasoning effort: `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Participation declaration: I did not implement or materially design the
  neutral publication control-plane candidate under review.
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform
  identity unverified
- Assignment state: `platform-unverified`
- Scoped override: none. The recorded engineering override does not apply to
  this independent critic review and does not transfer orchestration ownership.
- Scope: read-only review of the proposed neutral publication architecture and
  process against the accepted Dissociation goal boundaries, active plan/context,
  explorer receipt, current code references, and governance requirements.
- Changed by this review: added this receipt only.
- Timestamp: `2026-09-14T05:09:37+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:22:00`
- Token use: unavailable

## Files checked

- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/explorer_publication_reuse_map_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_20260914.md`
- Current code references found with read-only search under `kb_creator/` and
  `translator/`, especially:
  - `kb_creator/contracts/scenario_contract.v1.schema.json`
  - `translator/translator.py`
  - `translator/page_policy.py`
  - `translator/pipeline_plan.py`
  - `kb_creator/scripts/build_viral_production.py`
  - `kb_creator/scripts/build_innsmouth_pdf_from_accepted_html.py`
  - `kb_creator/scripts/production_docx.py`
  - relevant existing tests named in the explorer/spec receipts

No tests or live publication commands were run; this assignment is an
architecture/process review, not implementation validation.

## Verdict

Reject as written for one narrow P1 architecture/process ambiguity before Packet
A/B/C are dispatched.

The overall shape is acceptable: the spec is additive, avoids mutating
`ScenarioContract.v1`, preserves the reconstruction boundary, contains legacy
direct HTML-to-PDF routes as compatibility-only, requires explicit user gates,
requires ArtView decisions/configs in the production package, keeps installed
pipeline tools under `.tools`, and does not infer release. However, the DOCX QA
stage currently authorizes a retained "DOCX QA preview PDF" before DOCX
acceptance, while the goal boundary says PDF generation is from the exact
accepted DOCX only. That ambiguity must be removed before implementation so the
new control plane cannot accidentally create a second PDF lineage or package an
unaccepted-DOCX PDF as evidence.

## Evidence

- Governance requires independent receipts, explicit assignment state, no
  transfer of orchestration ownership, and no release approval outside a frozen
  release review.
- The active plan/context fix the publication chain as accepted
  `MASTER_RU + accepted ArtView/configs -> HTML -> DOCX -> PDF`, forbid direct
  HTML-to-PDF, and require ArtView, accepted decisions, and effective configs as
  production-package artifacts.
- The explorer receipt confirms the current reusable foundations and legacy
  hazards: `ScenarioContract.v1` hard-codes `viral_print` and `accepted_html`
  PDF authority; `translator/translator.py`, Innsmouth, and Viral routes still
  contain direct HTML/browser PDF paths; `production_docx.py` is reusable but
  has implicit Viral metadata/layout defaults.
- The architecture spec correctly proposes separate additive publication
  contracts, a publication run spec, publication stage manifest, artifact
  acceptance receipts, ArtView v3 decision/profile envelopes, sealed effective
  config, and production package manifest rather than expanding reconstruction
  schemas.
- The spec's authoritative chain says "PDF generated from that exact accepted
  DOCX only" and Stage 60 requires `accepted_docx` as the sole PDF input through
  `word_com_docx_export_v1`.
- The same spec's Stage 50 says to "create a stage-local DOCX QA preview PDF"
  before stopping for `awaiting_docx_acceptance`. It asserts that this does not
  violate PDF authority because it is QA evidence only, but does not explicitly
  forbid retaining, inventorying, packaging, accepting, or using that PDF as a
  downstream input.
- The spec's direct-route containment is otherwise strong: it forbids neutral
  imports/invocations of `translator.build_production_pdf`,
  `build-production-pdf`, `build_innsmouth_pdf_from_accepted_html.py`, Viral
  browser PDF calls, and any publication PDF manifest/config naming HTML input.
- Packet A/B/C are appropriately bounded and additive. They do not require live
  Dissociation publication artifacts, stable package promotion, Git, release
  review, broad DAG machinery, browser PDF tooling, or Viral/Innsmouth
  migration.

## Findings

### P0

None.

### P1-1 - Stage 50 can create a retained pre-acceptance PDF artifact

Evidence:

- `architect_neutral_publication_control_spec_20260914.md` Stage 50 requires an
  accepted HTML receipt, creates a DOCX candidate, then says to create a
  stage-local DOCX QA preview PDF and render it before stopping for
  `awaiting_docx_acceptance`.
- The accepted goal boundary requires the PDF stage to be generated only from
  the exact accepted DOCX. A retained pre-acceptance PDF is close enough in name,
  bytes, and tool path to the final PDF artifact that it creates avoidable
  ambiguity in package inventory, cache identity, review evidence, and user
  acceptance.

Risk:

- Implementation could package or cache a PDF derived from an unaccepted DOCX,
  allow reviewers to confuse preview evidence with the final PDF, or weaken the
  "accepted DOCX -> final PDF" lineage tests.

Required remediation:

- Patch the architecture spec before implementation:
  1. Replace Stage 50's retained "DOCX QA preview PDF" with either a non-PDF
     DOCX inspection/render strategy, or a strictly transient Word-export
     intermediate that is deleted before stage success.
  2. If a transient PDF is used only as an implementation bridge to Poppler,
     state that it is never a stage output, never listed in the DOCX stage
     manifest output inventory, never copied to evidence or the package, never
     accepted by a user, never reused by cache/resume, and never supplied to
     Stage 60.
  3. Add a required test that a successful Stage 50 DOCX candidate package has
     no retained `.pdf` output/evidence/package file, and that Stage 60 refuses
     any PDF byte stream not generated in Stage 60 from the exact accepted DOCX
     receipt.
  4. Keep all final-PDF render QA under Stage 60 after DOCX acceptance.

Closure criterion:

- The spec unambiguously preserves a single retained PDF lineage:
  `accepted_docx` receipt + Stage 60 `word_com_docx_export_v1` -> final PDF
  candidate. No Stage 50 retained PDF may be part of the production package or
  downstream authority.

### P2

None.

## Recommendation

Do not dispatch Packet A/B/C from the spec as written. Apply the narrow P1
wording/process remediation above, then Packet A can proceed as a synthetic,
additive control-plane skeleton with no live Dissociation publication run and
no acceptance/release inference.

The review does not block the existing reconstruction Wave 0 boundary and does
not authorize live reconstruction, publication, package promotion, or release.

## Next action

Architect/orchestrator should patch the neutral publication spec to remove the
retained pre-acceptance PDF ambiguity, then request a short independent closure
check or dispatch Packet A only if the remediation is incorporated exactly.

## Closure review - P1-1 correction

- Closure step: `4PR-neutral-publication-architecture-process-closure`
- Timestamp: `2026-09-14T05:14:12+03:00` (`Europe/Moscow`)
- Reviewer role: independent critic
- Requested model/effort: `gpt-5.5` / `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Participation declaration: I did not implement or materially design the
  correction under review.
- Scope: P1-1 closure only. I did not reopen unrelated architecture and did not
  inspect or edit implementation.
- Files checked:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_correction_20260914.md`
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_20260914.md`
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_neutral_publication_architecture_review_20260914.md`
- Tests run: none; this is a closure review of architecture/process wording and
  required test coverage, not implementation validation.

### Closure verdict

P1-1 is closed by
`architect_neutral_publication_control_spec_correction_20260914.md`.

The correction supplies the missing normative boundary:

- exactly one retained/packageable PDF lineage remains:
  `accepted DOCX -> fresh Stage 60 word_com_docx_export_v1 -> final PDF`;
- Stage 50 retained outputs are limited to DOCX, PNG, JSON/process diagnostics,
  review index, and manifest evidence;
- no successful Stage 50 retained path may have a `.pdf` suffix or PDF media
  type;
- any Stage 50 Word-export PDF is a private transient bridge only, outside
  outputs/evidence/cache/package, with no reusable SHA/path authority;
- bridge deletion and post-deletion absence checks are required before Stage 50
  can seal a successful manifest;
- cleanup failure or crash residue blocks Stage 50 success, acceptance, cache
  reuse, resume, and Stage 60;
- Stage 60 must perform a fresh export from the exact accepted DOCX receipt and
  rejects PDF paths/bytes, Stage 50 private files, diagnostics, PNGs, or cache
  entries as PDF authority;
- the package/offline verifier must accept exactly one PDF and prove Stage 60
  accepted-DOCX lineage; and
- Packet A/C required tests now cover Stage 50 no-PDF retention, cleanup
  failure, bridge residue, Stage 60 fresh export/isolation, non-reuse of Stage
  50 PNGs, exactly-one-PDF package verification, and tampered DOCX/receipt
  invalidation.

### Remaining findings after closure

- P0: none.
- P1: none.
- P2: none.

### Closure recommendation

Packet A may proceed under the corrected architecture, provided the dispatch
includes the correction receipt as authoritative over the original Stage 50
preview wording and includes the added P0/negative tests. This closure does not
authorize live Dissociation publication, generated publication candidates,
acceptance recording, stable promotion, Git operations, or release review.
