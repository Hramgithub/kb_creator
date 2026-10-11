# Number 7 Dream HTML candidate and ArtView export UX plan

Goal id: `20260918-dream-html-candidate-export-ux`

Status: completed — exact run09 HTML is awaiting explicit user acceptance

## Objective

Consume the user's explicit 19/19 ArtView export from run06, validate and bind
the accepted decisions, materialize Stage 31, improve the shared ArtView export
feedback without inventing a browser-hidden filesystem path, and build the next
fresh HTML candidate. Stop at explicit HTML acceptance; do not build DOCX/PDF,
record downstream acceptance, commit, or push.

## Authority and boundary

The user reported a completed accepted export and asked the pipeline to
continue. That authorizes ArtView acceptance, Stage 31, and an HTML candidate.
The later request to copy the export path authorizes a generic ArtView UX
change. A static browser page cannot discover the browser's real download
directory, so the implementation copies the exact exported filename and states
that the full path remains browser-controlled. This is not authority to infer
HTML acceptance or start DOCX/PDF.

## Role contract

- Orchestrator: policy `gpt-5.6-sol`, medium; canonical state, integration,
  authority decisions, recovery, and user-facing synthesis. Platform selection
  remains unverified.
- Bounded QA: policy `gpt-5.6-luna`, low; exact run07 Stage 40 and reusable UX
  verification only.
- Independent critic: policy `gpt-5.5`, medium; read-only implementation and
  process verdict. The critic does not implement or design the change.

## Steps

| Step | Owner | Status | Evidence / next action |
|---|---|---|---|
| H1 Capture and validate accepted ArtView decisions | orchestrator | completed | Exact 19/19 live choices captured; strict validation passes; run06 decision SHA `6A1326CA...F24` |
| H2 Record ArtView acceptance and materialize Stage 31 | orchestrator | completed | Run06 acceptance seal `F27DC9CE...647`; Stage 31 application SHA `E4288190...663A` |
| H3 Improve generic export locator feedback | orchestrator | completed | Export returns its exact filename, attempts clipboard copy, and explains that the browser does not expose the full path; focused suite `55 passed, 255 subtests passed` |
| H4 Recover fresh successor after implementation drift | orchestrator | completed | Fresh run07 portable identity `8CB72614...C1E3`; accepted masters and all 298 translations reproduced exactly; 19 ArtView decisions strictly rebound |
| H5 Build and inspect Stage 40 HTML | orchestrator | completed | Run09 Stage 40 awaits acceptance; HTML SHA `D338180E...3193`, 26 pages, 19/19 images, 7 semantic statblock cards, zero producer findings |
| H6 Bounded QA | bounded QA | completed | R17 `PASS`: all Stage-40 identities/inventories match; page 14 is one UL/four LI, page 18 is seven typed row-preserving cards, 19 assets close, and no downstream artifacts exist |
| H7 Correct generic HTML semantic projection and rebuild | architect + orchestrator | completed | Manifest-bound reconstruction semantics are projected only at Stage 40; loose lists, hard breaks, typed rows, exact count/order gates, QA accounting, regressions, and fresh run09 are complete |
| H8 Independent implementation/process review | independent critic | completed | R18 `PASS / READY_FOR_USER_HTML_ACCEPTANCE_GATE`; no blocking findings, one low-severity evidence-label clarity note |
| H9 HTML acceptance gate | user + orchestrator | awaiting_user | Exact run09 candidate is presented and open; no acceptance is inferred and Stage 50 remains absent |

## Definition of Done

- The accepted ArtView JSON is strictly validated and hash-bound before Stage
  31; no browser state alone is treated as production authority.
- The ArtView export UI provides a truthful, copyable locator and a safe
  fallback without claiming access to the browser's download directory.
- A fresh successor run absorbs the code change, rebinds only after exact
  source-graph and binary equivalence, and produces Stage 40 from accepted
  MASTER_RU plus accepted ArtView/configs.
- The corrected HTML candidate has complete local assets and passes bounded QA
  plus an independent implementation/process review; the failed run07 HTML is
  retained only as immutable defect evidence.
- The pipeline stops at `awaiting_html_acceptance`; HTML acceptance, Stage 50,
  DOCX, PDF, release, commit, and push remain absent.
