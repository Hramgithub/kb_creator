# Number 7 Dream MASTER_RU and ArtView plan

Goal id: `20260918-dream-master-ru-artview`

Status: completed

## Objective

Translate the sealed Stage 20 packet set from the accepted corrected
MASTER_EN lineage, materialize and independently verify a Stage 21
MASTER_RU candidate, then continue to the ArtView candidate only through the
explicit acceptance gates defined by the publication control plane. Do not
start HTML, DOCX, PDF, release, Git commit, or push.

## User authority and boundary

The user explicitly requested `собирай мастер ру и артвью`. This authorizes
translation authoring, Stage 21 candidate materialization, QA, and preparation
of the downstream ArtView candidate. It does not silently convert a candidate
into an accepted artifact: the MASTER_RU and ArtView acceptance receipts must
remain bound to explicit user decisions. If the control plane reaches an
acceptance gate before the next stage can run, stop there and present the
candidate for review.

## Role contract

- Orchestrator: policy `gpt-5.6-sol`, medium; canonical state, authority,
  integration, stop/ask decisions, and user-facing synthesis. Platform model
  and effort are unavailable; assignment state `platform-unverified`.
- Translation contributors: bounded executor role, policy `gpt-5.6-luna`,
  medium; disjoint packet ranges only. Assignment state
  `platform-unverified`; scoped override `none`.
- Bounded QA: policy `gpt-5.6-luna`, low; packet/submission and candidate
  integrity evidence. Assignment state `platform-unverified`; scoped override
  `none`.
- Independent critic: policy `gpt-5.5`, medium; implementation/process verdict
  after the frozen candidate. Assignment state `platform-unverified`; scoped
  override `none`.

## Steps

| Step | Owner | Status | Evidence / next action |
|---|---|---|---|
| R1 Reopen sealed Stage 20 authority and translation contract | orchestrator | completed | Run02 packet authority reopened: 27 batches, 298 units, exact closed schema |
| R2 Translate all 298 units in disjoint batch ranges | bounded executors | completed | Four compact payloads cover `101+81+59+57=298`; exact ordered IDs and no empty text |
| R3 Repair generic MASTER_RU validation/normalization blockers | engineering + orchestrator | completed | Producer/verifier parity v3; focused suite `45 passed, 1 skipped, 48 subtests`; receipts R3 v1-v3 |
| R4 Materialize Stage 21 MASTER_RU candidate | orchestrator | superseded | Run03 reached `awaiting_master_ru_acceptance`; SHA `D001BC19...AFB17`, but R5 found post-packet normalization corruption |
| R5 Independent MASTER_RU QA and review | bounded QA | needs_correction | `r5-master-ru-qa.md`: page/layout integrity passes; `Вождение автомобиля автомобиля` proves run03 is not acceptance-ready |
| R6 Polish translation and rebuild immutable successor | bounded executor + orchestrator | completed | 34 units polished; final validator v4; publication-04 Stage 21 SHA `A96BFEAF...A9230` |
| R7 Bounded QA for frozen run04 | bounded QA | completed | `r7-run04-master-ru-qa.md`: PASS; 27/298, all seed regressions closed, no Stage30 |
| R8 Independent implementation/process review | independent critic | completed | `PASS_WITH_LIMITATION`; exact run04 hash safe to present, not a release review |
| R9 MASTER_RU acceptance gate | user + orchestrator | completed | User replied `ну вроде ок`; accepted exact SHA `A96BFEAF...A9230`, reproduced byte-identically in run05 |
| A0 Repair resume path-coordinate defect and recover fresh authority | orchestrator | completed | Canonicalize `run_root` and authority paths before staging; regression plus ArtView/control-plane suite passes `55`, 255 subtests; run04 failed attempt remains quarantined |
| A1 Build and verify Stage 30 ArtView candidate | orchestrator + bounded QA | completed | Run05 producer/QA evidence passed but the live review exposed an interaction defect: `center + wrap` disabled explicit review. The generic UI now normalizes wrapping to right alignment (and table wrap to text wrap), with regressions. Fresh run06 Stage 30 has producer QA `pass`; R12 bounded QA is `PASS` over 19 rows, 18 source pages, 38 portable binaries and every manifest-listed file. |
| A2 ArtView decisions and acceptance gate | user + orchestrator + critic | completed | User completed/exported all 19 rows; strict accepted decisions and run06 ArtView acceptance are recorded, and Stage 31 materialized. Downstream HTML plus export-UX work moved to goal `20260918-dream-html-candidate-export-ux`. |

## Definition of Done

- Every sealed Stage 20 unit has a non-empty Russian translation and unchanged
  source identity, order, Markdown structure, mechanics, source markers, links,
  and image references.
- The run-local MASTER_RU submission passes generic authoring and independent
  verification; Stage 21 is materialized without manual patching of the final
  artifact.
- MASTER_RU QA covers terminology, mechanics, headings, quotes, lists,
  stat-block line flow, assets, and all source pages.
- ArtView is built only after an explicit MASTER_RU acceptance and accepted
  only after the user's 19/19 export; Stage 31 is complete. HTML and later work
  belongs to the separate successor goal.
- Reusable script/config changes, if any become necessary, receive tests and
  are documented; ignored `working/**` products remain outside Git commit
  scope. No commit or push is performed.
