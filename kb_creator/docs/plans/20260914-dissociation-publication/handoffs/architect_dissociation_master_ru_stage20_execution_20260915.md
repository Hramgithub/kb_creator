# Architect receipt: Dissociation MASTER_RU Stage 20 execution packet

- Goal id: `20260914-dissociation-publication`
- Step id: `stage20-master-ru-read-only-execution-architecture`
- Role: architecture/root-cause analysis, `gpt-5.6-sol` / `high`
- Orchestrator policy owner: main-chat `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; bounded contributor only
- Scoped override: none for architecture; the goal's separate engineering
  `gpt-5.6-sol` / `high` override is not exercised here
- Timestamp: `2026-09-15T12:49:21+03:00`
- Elapsed time: unavailable
- Token use: unavailable

## Scope and result

Read-only specification for the future `MASTER_RU` packet/submission/candidate
sequence after explicit `MASTER_EN` acceptance. No acceptance was inferred or
recorded; no publication command, translation, external API, MinerU/CPU, live
stage, source/config/code/run-root, Git, plan/context/status, or release file
was changed.

**Overall decision: NO-GO for the real Stage 20 -> Stage 21 chain.** The
current Stage 10 candidate itself is suitable input, but three generic P1 gaps
must close first: there is no safe submission author, the structural validator
does not preserve Markdown hard breaks, and the contract's
`independent_translation_qa` requirement is neither produced independently nor
enforced at acceptance. Because the affected files are in the run's sealed
implementation inventory, remediation makes current run
`20260915-publication-01` non-resumable. Do not record its pending MASTER_EN
acceptance merely to run Stage 20; after reviewed remediation, create a fresh
publication run, reproduce Stage 10, independently verify it, and obtain a new
explicit user acceptance bound to that fresh producer stage.

There is no P0 finding. The three P1s below are scenario-neutral and block real
translation promotion, not just Dissociation.

## Current authority and stop condition

- Run: `kb_creator/working/dissociation/publication/20260915-publication-01`
- Portable run identity:
  `F291449833998F9F0A2CF52443D6951BBE63805B4164CFA9B93FAF5CC600C782`
- Sealed implementation inventory:
  `106FE3A697B00781DE261D58B64479ADB6E190EA4D558CA31112D7EF9EEC115D`
- Contract:
  `kb_creator/contracts/dissociation.publication.json`, SHA-256
  `7F1B02F3C18B6C4FE998D121328ACCDB5A449D12C850368732BA2ACAA6EE0367`
- Stage 10 candidate:
  `outputs/10-master-en-candidate/artifacts/MASTER_EN.md`, `20,863` bytes,
  SHA-256
  `2AD1E9175A3B53B7C85CCA5824B2FAA60D4A82C38928F487E6BB7700B5617CA6`.
- Independent Stage 10 process receipt reported by the orchestrator:
  `B315433E...16D5`; it is evidence only, not acceptance.
- Observed absent: `acceptance/master_en.acceptance.json`,
  `outputs/20-master-ru-packets`, and `outputs/21-master-ru-candidate`.

The sole current gate is explicit user acceptance of MASTER_EN. Stage 20
requires exactly one run-local authority, `master_en_acceptance`; Stage 21
requires exactly one run-local authority, `master_ru_submission`. Neither
`publication resume` invocation may carry an extra authority.

## Deterministic packet topology estimate

The estimate uses the current candidate with the production algorithms
`_source_units`, `expand_units_for_translation`, and `batch_units`, and the
bound `max_batch_chars: 3000`. It is exact for an identical fresh Stage 10
candidate/config, but it is not a generated Stage 20 authority.

- UTF-8 text characters: `20,755` (`20,863` encoded bytes).
- Original units: `87`; translation units: `87`.
- Long-unit splits: `0`; maximum unit size: `709` characters.
- Batches: `8`.
- Source assets referenced and later copied byte-for-byte: `2`.
- Parsed shared terms: `80` merged terms / `85` source bindings.
- Applicable terminology: `17` terms across `45` per-unit checks.
- Numeric/dice/mechanics tokens observed by the current signature: `76`.
- The last statblock body is `unit-00087`; it contains `10` accepted Markdown
  hard-break lines.

| Packet | Units | Chars | Unit range | Approx. source pages |
|---|---:|---:|---|---|
| `batch-0001` | 16 | 2,741 | `00001-00016` | 1-2 |
| `batch-0002` | 10 | 2,783 | `00017-00026` | 2-3 |
| `batch-0003` | 10 | 2,807 | `00027-00036` | 3 |
| `batch-0004` | 12 | 2,896 | `00037-00048` | 3-4 |
| `batch-0005` | 10 | 2,413 | `00049-00058` | 4 |
| `batch-0006` | 11 | 2,838 | `00059-00069` | 4-5 |
| `batch-0007` | 13 | 2,930 | `00070-00082` | 5-6 |
| `batch-0008` | 5 | 1,174 | `00083-00087` | 6 |

The exact output topology after successful Stage 20 is:

```text
outputs/20-master-ru-packets/
  artifacts/
    packet_manifest.json
    translation_tasks.json
    batches/batch-0001.en.json ... batch-0008.en.json
  evidence/
    terminology/authority-00.csv
    terminology/authority-01.md
```

`packet_manifest.json` binds the accepted MASTER_EN receipt/candidate, both
terminology snapshots, tasks, ordered batch inputs/output basenames, counts and
seal. Stage 20 must stop at `awaiting_master_ru_submission`, exit `10`.

## Translation work decomposition

Use one exclusive owner per complete batch; no two translators edit the same
`.ru.json`. Eight batches are small enough that micro-splitting adds risk and
is unnecessary. A two-owner allocation may use odd/even batches; a four-owner
allocation may use consecutive pairs. In every case assign `batch-0008` to an
owner explicitly briefed to preserve the compact statblock and give it a
separate review pass. A distinct QA contributor reviews all `87` units after
batch owners finish; the QA contributor must not be the sole translator of all
batches.

Each translation result is a new run-local file under a submission work area,
for example:

```text
submissions/master_ru/batches/batch-0001.ru.json ... batch-0008.ru.json
submissions/master_ru/master_ru.submission.json
```

The `.en.json` Stage 20 artifacts remain immutable. A translated batch retains
the exact outer schema, `batch_id`, instructions, unit order, unit ids, page,
source hash, optional split metadata, and `source_text`; only `ru_text` is
filled. No unit may be summarized, omitted, joined, reordered, or copied with a
changed source field.

Reusable components that are safe in this topology:

- Stage 20 itself reuses `prepare_translation_batches.py::expand_units_for_translation`
  and `batch_units`.
- Stage 21 reuses `merge_translation_batches.py::validate_batch` as a low-level
  check, then applies stronger packet/submission/structure/terminology checks.

Do **not** use the standalone `merge_translation_batches.py` output: it emits
an Innsmouth-specific heading/provenance envelope. Do **not** use
`split_translation_batch_to_units.py` plus
`merge_micro_translation_batch.py` for this run: the merge emits
`kb_creator.translation_batch_ru.v1`, while Stage 21 requires
`kb_creator.translation_batch.v1`. This is an interoperability limitation, not
permission for a scenario-specific converter.

## Language, fidelity and asset contract

- The scenario/document title authority is exactly `Диссоциация`. Translate
  the leading `# DISSOCIATION` to `# Диссоциация`; do not derive a title from
  filenames or use an alternate Russian title. Lowercase/common-noun uses of
  “dissociation” remain contextual translation, not a blind title replacement.
- Preserve source-page comments, heading levels/order, links and targets,
  image targets, list/table syntax, anchors, paragraph order, inline Markdown,
  numbers, percentages and dice expressions. Russian prose may change text
  length, but not semantic content or mechanics.
- Preserve the exact two image references. Stage 21 must copy the corresponding
  accepted MASTER_EN assets byte-for-byte and emit a closed asset manifest; a
  translator never edits image paths or binaries.
- The final `HUMAN RESISTANCE` compact statblock remains compact. Its body must
  retain all ten two-space Markdown hard breaks; translation may change words,
  not convert the lines into paragraphs, one wrapped paragraph, a table, or a
  list. ArtView may style it later but MASTER_RU must not reinterpret it.
- The two bound glossary snapshots are normative and immutable. Current
  applicability includes `Keeper -> Хранитель`, `investigator -> сыщик`,
  `Sanity -> Рассудок`, characteristic abbreviations such as `POW -> МОЩ`,
  `DEX -> ЛВК`, `CON -> ВЫН`, stat terms including `ПЗ`, `Комплекция`,
  `бонус к урону`, and skill names including `Уклонение`,
  `Ближний бой (Драка)`, `Слух`, `Психология`, and `Внимание`. Accepted aliases
  apply only as declared; known bad variants are forbidden. Ordinary-language
  words that merely resemble a skill must still be translated by context, but
  every source-term match selected by the gate must contain one declared
  accepted Russian variant.

## Exact execution sequence after remediation

The following is the intended operator sequence, not authorization to run it
now. `<fresh-run>` must be a new absent run root because remediation changes
the implementation inventory. Use the exact tools already bound by the
contract/run environment.

1. Independently close the P1 remediation below. Run publication `preflight`
   against `<fresh-run>`, then `publication run` with the same accepted
   reconstruction/config/tool authorities to reproduce only Stage 10. Expected
   result: exit `10`, `awaiting_master_en_acceptance`; Stage 20 absent.
2. Independently verify the fresh MASTER_EN. Present it to the user. Only after
   an explicit acceptance, record the fresh run-local acceptance:

```powershell
.tools/MinerU/profiles/pipeline-cpu-v1/.venv/Scripts/python.exe -B -m kb_creator publication record-acceptance `
  --run-root <fresh-run> `
  --artifact-kind master_en `
  --evidence <fresh-run>/outputs/10-master-en-candidate/evidence/MASTER_EN.qa.json `
  --evidence <fresh-run>/outputs/10-master-en-candidate/evidence/MASTER_EN.verification.json `
  --destination <fresh-run>/acceptance/master_en.acceptance.json `
  --user-decision-reference "<verbatim explicit user decision>" `
  --json
```

3. Generate Stage 20 only:

```powershell
.tools/MinerU/profiles/pipeline-cpu-v1/.venv/Scripts/python.exe -B -m kb_creator publication resume `
  --run-root <fresh-run> `
  --authority master_en_acceptance=<fresh-run>/acceptance/master_en.acceptance.json `
  --python .tools/MinerU/profiles/pipeline-cpu-v1/.venv/Scripts/python.exe `
  --powershell C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe `
  --pdftoppm .tools/poppler/poppler-26.02.0/Library/bin/pdftoppm.exe `
  --word "C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE" `
  --json
```

   Expected: exit `10`, `awaiting_master_ru_submission`, exactly eight packet
   files and no Stage 21. Word/Poppler are identity inputs here; neither render
   path is invoked by Stage 20.
4. Translate the eight owned batches and run the new generic submission author
   (specified below). The author must atomically emit a sealed, schema-valid,
   run-local submission only after all eight batches pass.
5. Validate the submission read-only with
   `scenario_master_ru validate-submission`. Expected status: `pass`, no
   findings. Then resume exactly once with only:

```powershell
.tools/MinerU/profiles/pipeline-cpu-v1/.venv/Scripts/python.exe -B -m kb_creator publication resume `
  --run-root <fresh-run> `
  --authority master_ru_submission=<fresh-run>/submissions/master_ru/master_ru.submission.json `
  --python .tools/MinerU/profiles/pipeline-cpu-v1/.venv/Scripts/python.exe `
  --powershell C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe `
  --pdftoppm .tools/poppler/poppler-26.02.0/Library/bin/pdftoppm.exe `
  --word "C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE" `
  --json
```

   Expected: exit `10`, `awaiting_master_ru_acceptance`, Stage 21 only.
6. Independently review the Stage 21 candidate and its verification evidence.
   Present `MASTER_RU.md` plus QA findings to the user. Do not record acceptance
   until the user explicitly accepts it. Corrections must update the affected
   `.ru.json` batch(es), regenerate the sealed submission, and rebuild in a
   fresh compatible run/stage path; never edit generated `MASTER_RU.md`.

## P1 remediation specification

### P1.1 - No generic submission author

Production code validates a sealed `kb_creator.master_ru_submission.v1`, but
only tests construct one. Real use therefore requires manual/ad hoc canonical
JSON hashing, per-unit payload hashing and batch identity assembly.

Add `scenario_master_ru author-submission` with `--packet-root`,
`--batch-root`, `--destination`, and `--authority-root`. It must fail before
write unless the destination is absent/run-local/non-reparse, the batch root
contains exactly the expected ordered `.ru.json` names, every batch is a closed
copy of its source shape with only nonempty `ru_text` changed, all unit/source
fields and order match, every declared hash/identity is recomputed, review is
closed with no unresolved findings, and the draft passes the same complete
submission validator. Write atomically and canonically; never accept supplied
hashes or a caller-supplied scenario id/authority identity.

### P1.2 - Accepted compact hard breaks are not enforced

`_structure_signature` ignores plain line topology and trailing two-space hard
breaks. A read-only probe on real `unit-00087` removed all ten hard breaks while
preserving every currently measured signature field; the before/after
signatures compared equal. Such a translation can pass today and undo the
user-accepted compact statblock correction.

Extend the generic signature with Markdown line topology sufficient to retain
hard breaks, explicit `<br>` if present, fenced-code boundaries, and emphasis
delimiter balance without binding translatable prose. At minimum, retain the
ordered per-line structural class and exact hard-break boolean. A source line
ending in two spaces must map to one Russian line ending in two spaces at the
same structural position. The final statblock attack above must fail with a
stable `markdown_or_mechanics_drift` finding.

### P1.3 - `independent_translation_qa` is declarative only

The contract requires seven MASTER_RU QA roles including
`independent_translation_qa`. Stage 21 invokes `assemble`, which calls the same
module's validator and self-emits `MASTER_RU.qa.json`; there is no independent
MASTER_RU verifier. The acceptance recorder merely checks that supplied files
are inside stage evidence, so it can record MASTER_RU acceptance using only the
self-produced QA and never enforces the contract's required QA list.

Add a separate standard-library-only `verify_scenario_master_ru.py` that does
not import producer validation helpers. It must independently rederive packet
and submission seals/identities/order, batch/source/Russian hashes, exact
candidate assembly, Markdown/hard-break/mechanics topology, all applicable
terminology checks, the two copied asset identities, provenance, QA and
candidate inventory. It emits `MASTER_RU.verification.json` with exact
candidate/submission/packet/contract identities, the contract's seven required
QA labels, zero findings, and a non-accepting state. Stage 21 calls it and
retains the receipt under stage evidence. `record_artifact_acceptance` must
fail closed for `master_ru` unless both producer QA and the exact passing
independent verification for that candidate are included; extra unrelated
files cannot substitute for either.

## Minimal engineer ownership

- `kb_creator/scripts/scenario_master_ru.py`: submission author and stronger
  structural signature/validation.
- `kb_creator/scripts/verify_scenario_master_ru.py`: new independent verifier.
- `kb_creator/pipeline/publication_adapters.py`: run the verifier and retain its
  receipt in Stage 21 evidence.
- `kb_creator/pipeline/publication.py`: include the verifier in implementation
  inventory and enforce MASTER_RU acceptance evidence.
- `kb_creator/tests/test_scenario_master_ru.py`: author determinism, containment,
  exact topology, stale/tampered batch and hard-break attacks.
- `kb_creator/tests/test_verify_scenario_master_ru.py`: independent positive and
  adversarial verification.
- `kb_creator/tests/test_publication_registry_e2e.py`: real registry Stage
  20/21 evidence and acceptance enforcement.

No contract/config/glossary/source/run-root change is required. Do not mutate
`master_ru_submission.v1.schema.json` unless implementation proves an actual
schema/runtime parity defect; the missing operation is safe authoring and
verification, not a new scenario contract.

## Acceptance criteria

- Fresh synthetic registry run stops at every existing gate and carries the
  new verifier in its sealed implementation/stage evidence.
- Submission author output is byte-deterministic for identical inputs and
  passes both JSON Schema and runtime validation.
- Missing/extra/reordered/renamed batch; duplicate/reordered unit; changed
  source text/hash; empty RU; changed number/die/percent; changed page marker,
  heading level, link/image target, list/table/anchor; removed/added hard break;
  stale acceptance/packet; terminology omission/bad variant; asset drift;
  altered candidate/provenance/inventory; path escape/reparse; and resealed
  extra-field inputs all fail before accepted output.
- Exact compact ten-hard-break statblock translation passes; the same payload
  with zero hard breaks fails.
- MASTER_RU acceptance with producer QA only fails; verification only fails;
  stale or non-pass verification fails; both exact passing records succeed only
  after an explicit user decision.
- Legacy translation helpers/routes remain unchanged and no Innsmouth/Viral or
  Dissociation constants enter reusable implementation.
- Independent implementation review reports no P0/P1 before any fresh live
  publication run.

## Files checked / changed / evidence

Checked: repository `AGENTS.md`; governance role/receipt rules; KB Creator
README; active `plan.md`, `context.md`, and `PROJECT_STATUS.md`; neutral
publication architecture and Packet B/C plus shared-terminology handoffs;
publication contract/run/config; Stage 10 candidate QA/verification;
`publication.py`, `publication_adapters.py`, `scenario_master_ru.py`, all four
low-level batch/micro helpers, submission/acceptance schemas, MASTER_RU and
registry E2E tests, and both glossary snapshots.

Changed: this receipt only.

Verification was read-only: current authority/absence checks; deterministic
unit/batch/terminology projection; real statblock signature attack proving
`10 -> 0` hard breaks still yields `signature_equal: True`; source/code search
confirming that submission authoring exists only in tests and no independent
MASTER_RU verifier exists. No tests or production command were run because the
task forbids implementation and live publication mutation.

## Blocker and next action

Blocker: P1.1-P1.3, plus the unavoidable stale implementation identity of the
current run after their correction.

Next action: assign the seven-file generic remediation packet above to the
goal's engineering owner, obtain independent implementation closure, then use
a fresh absent publication run root to reproduce Stage 10 and return to the
explicit MASTER_EN user gate. Only after that acceptance may the exact Stage 20
sequence and eight-batch translation decomposition in this receipt execute.

This receipt does not transfer orchestration ownership and is not publication,
user, or release acceptance.
