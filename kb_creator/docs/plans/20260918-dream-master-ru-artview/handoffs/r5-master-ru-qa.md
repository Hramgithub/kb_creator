# R5 MASTER_RU bounded QA receipt

- Goal / step: `20260918-dream-master-ru-artview` / `R5-master-ru-qa`.
- Result: `NEEDS_CORRECTION`; the candidate is not acceptance-ready.
- QA role policy: `gpt-5.6-luna`, low. Platform-selected model and effort are unverified.
- Orchestrator policy owner: `gpt-5.6-sol`, medium. Assignment state: platform-unverified. Scoped override: none.
- Scope: read-only audit of frozen run `20260918-publication-03`; no payload, candidate, implementation, acceptance, plan, context, status, or source changes. This receipt is the only file written by this assignment.

## Files checked

- Plan/context: `kb_creator/docs/plans/20260918-dream-master-ru-artview/{plan,context}.md`.
- Run identity: `kb_creator/working/number-7-dream/publication/20260918-publication-03/run.json`.
- Stage 20 packet manifest, translation tasks, all 27 `.ru.json` batches, and Stage 20 manifest under `outputs/20-master-ru-packets` and `submissions/master-ru-01/batches`.
- Sealed submission: `submissions/master-ru-01/master_ru.submission.json`.
- Stage 21 manifest, `MASTER_RU.md`, `MASTER_RU.qa.json`, `MASTER_RU.verification.json`, `MASTER_RU.provenance.json`, `TERMINOLOGY.qa.json`, asset manifest and packaged assets under `outputs/21-master-ru-candidate`.
- Accepted English source and evidence under `outputs/10-master-en-candidate`; terminology authority `outputs/20-master-ru-packets/evidence/terminology/authority-00.csv`.

## Evidence

- Run ID and Stage 21 run identity both resolve to `20260918-publication-03` / `D72DDD52799A53EB5E5AF5EC483A85C36C9E46DFAA29A1FEDAE9D57C6734B48C`.
- Stage 20 inventory contains 27 batches and 298 ordered units. All 298 submitted `ru_text` values are non-empty. The 34 source-identical payloads are only the 26 page markers and 8 image references; no prose unit remained identical to its English source.
- Producer `MASTER_RU.qa.json` reports `pass`, with structural, mechanics, ordered-unit, terminology and anchor/link/image checks true. The independent verifier reports `verified_candidate_pending_user_acceptance`, no generated findings, and all declared checks true. Stage 21 manifest state is `succeeded`, with diagnostic state `awaiting_master_ru_acceptance`.
- Material defect found by comparing sealed batch payload to the assembled artifact: `submissions/master-ru-01/batches/batch-0025.ru.json`, `unit-00266`, correctly translates source `Drive Auto 75%` as `Вождение автомобиля 75%`; `outputs/21-master-ru-candidate/artifacts/MASTER_RU.md:695` instead contains `Вождение автомобиля автомобиля 75%`. The extra word is introduced between the Stage 20 translation payload and Stage 21 Markdown. A PCRE2 adjacent-word scan finds this as the only repeated Russian word of 3+ letters in `MASTER_RU.md`; the same scan over Stage 20 batch payloads finds none. Severity: major; generated text does not faithfully materialize its sealed translation unit.
- The page 14 letter is present as a Markdown blockquote, including its four list items and closing “Удачи!” / “Элси Уэбб” (`MASTER_RU.md:398-410`).
- Page 18 contains seven distinct character-stat entries (beginnings at lines 527, 532, 538, 542, 547, 554 and 565). Their blockquote structure is retained. Mechanical labels and proper names remain in some lines, as allowed by this check’s scope.
- Pages 21-26 retain compact stat fields with hard line breaks (for example lines 641-649, 665-673, 687-695, 711-719, 735-742 and 760-768). All 26 page markers are present and unique. No run of two or more empty lines was found. Previously problematic concatenated English headings are represented as separated Russian headings at lines 298 and 302.
- The Latin-word scan found no untranslated English prose; matches are source-image alt text or stat/mechanical labels and proper names. The 386 terminology QA checks have zero `bad_present` results. The authority currently maps `Credit Rating` to `Средства`, which appears repeatedly in the character skill lines; it is aligned with the configured authority and was not adjudicated by this bounded QA, but merits human terminology review.
- Only three stage manifests exist (10, 20, 21); no Stage 30 output was present. No MASTER_RU acceptance receipt was present; the run remains at its expected explicit acceptance gate.
- Governance-state discrepancy: the read plan/context still identify publication run `20260918-publication-02` and say R1 is active, whereas this assignment and the frozen evidence are for run `20260918-publication-03`. The run03 manifest is internally consistent, but the canonical plan/context need orchestrator reconciliation before the next gate.

## Blocker and next action

Do not record MASTER_RU acceptance or start ArtView from this candidate. Have the orchestrator trace and correct the Stage 21 materialization path that adds the duplicate word, rebuild Stage 21 from the unchanged sealed Stage 20 submission, update the canonical plan/context to run03, then repeat bounded QA on the rebuilt candidate. Recheck this line and scan for other assembly-only mutations.

## Accounting

- Elapsed time: approximately 6 minutes.
- Token use: unavailable.
- Timestamp: 2026-09-17 23:20 UTC.
