# Architect receipt: Dissociation Stage 10 MASTER_EN execution

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `stage10-master-en-execution-spec`
- Role: architect / dependency and remediation specification
- Policy role/model/effort: `gpt-5.6-sol`, `high`
- Actual platform model/effort: unavailable
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: none for architecture; the goal's engineering Sol/high override remains canonical
- Timestamp: `2026-09-15T12:01:07+03:00`
- Elapsed time: approximately 35 minutes
- Token use: unavailable
- Scope: Stage 10 `master_en_candidate` only, from the accepted run09 reconstruction package
- Result: execution contract and one generic blocker identified; no publication input, run root, candidate, acceptance, code, canonical state, source, or Git state was changed
- Files changed: this receipt only

## Decision

**GO** for the smallest declarative publication-config authoring packet and the
narrow generic Stage 10 verifier wiring below.

**NO-GO** for live Stage 10 until both are complete and independently reviewed.
The accepted reconstruction is ready, but the Dissociation publication contract
and all seven identity-bound source configs do not exist. In addition, the
production Stage 10 adapter currently invokes the v3 builder but not the already
implemented independent v3 verifier.

No later-stage execution, user acceptance, translation, ArtView decision,
rendering, packaging, or release is authorized by this receipt.

## Exact accepted upstream authority

Use only:

- package root:
  `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-09/promotion/reconstruction-upstream-v1`;
- inventory: `RECONSTRUCTION_INVENTORY.json` in that root;
- acceptance: `RECONSTRUCTION_ACCEPTANCE.json` in that root, receipt SHA-256
  `10F058EE1D6FE1691E59EEB4B02354AC6862417FE193A5BA7991C03450223D22`;
- accepted source candidate: `content/RECONSTRUCTED_EN.md`, 21,048 bytes,
  SHA-256 `2C8983B83C770AC60AA32993B84228E64983B46010121A9DBA393BD3107C646D`;
- reconstruction contract:
  `kb_creator/contracts/dissociation.reconstruction.json`, SHA-256
  `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E`.

The promotion package validator, not a copied standalone Markdown file, remains
the Stage 10 upstream authority.

## Current existence census

The accepted upstream package and both acceptance files above exist. The shared
terminology authorities also exist at their canonical project paths.

The following proposed publication authorities are absent and must be created
as one reviewed declarative packet:

```text
kb_creator/inputs/dissociation/publication/v1/
  publication-blueprint.json
  configs/
    master_en.json
    master_ru.json
    artview/profile.json
    artview/source-graph.json
    artview/assets/<identity-bound source images>
    html.json
    docx.json
    pdf.json
    package.json
  terminology/
    CoC_Terminology_Decisions.csv
    CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md

kb_creator/contracts/dissociation.publication.json
kb_creator/working/dissociation/publication/
kb_creator/working/dissociation/publication/20260915-publication-01/
```

The final path is the proposed whole-publication run root and must remain absent
through authoring and preflight. Its parent must exist before preflight because
the control plane rejects an absent run-root parent. No other Dissociation
publication or MASTER_EN run root was found.

The terminology files under the config root are exact snapshots, not edited
translations. Their bytes must equal the two accepted canonical authorities
recorded in goal context. This makes the contract author and later Stage 70
package able to bind and retain them without an escaping relative path.

## Full-contract prerequisite and Stage 10 boundary

`scenario_publication_blueprint.v1` requires exactly seven config path roles:

1. `master_en`
2. `master_ru`
3. `artview`
4. `html`
5. `docx`
6. `pdf`
7. `package`

The generic author resolves every referenced file and emits its bytes/SHA into
`scenario_publication_contract.v1`. `publication_preflight()` then revalidates
all seven identities and rejects a missing role before it creates a run root.
Therefore Stage 10 **cannot** be run before the later visual/render/package
configs exist and are frozen. Placeholder files are not acceptable: modifying
one later would invalidate the contract, `run.json`, effective config and Stage
10 chain, forcing a new run and duplicate MASTER_EN candidate.

Stage 10 may run before later *artifacts, decisions and acceptances* exist. It
does not activate Word, PowerShell, Poppler, translation, ArtView, HTML, DOCX or
PDF. The fixed registry only resolves and hash-binds those tool executables.
Thus the recorded Word COM activation limitation does not block Stage 10 after
final configs exist; it blocks the future Stage 50/60 execution session.

## Smallest declarative config-authoring packet

One bounded content/config author owns only the new `v1` input tree and the
generated `dissociation.publication.json`. Do not add a scenario-specific
Python or PowerShell script.

### Blueprint

`publication-blueprint.json` must declare:

- scenario id `dissociation`, English title `Dissociation`, and an explicitly
  authored Russian title; do not silently infer the Russian title;
- source/target languages `en`/`ru`;
- the reconstruction-contract SHA above and the exact ordered roles
  `reconstructed_en`, `reconstruction_manifest`, `reconstruction_qa`,
  `source_identity`;
- stable artifact basenames `MASTER_EN.md`, `MASTER_RU.md` and explicitly
  selected HTML/DOCX/PDF basenames;
- the seven config paths above;
- MASTER_EN profile `neutral_v3`, MASTER_RU profile `neutral_v1`, packet policy
  `ordered_hash_bound_units_v1`, ArtView decisions v3, the fixed HTML/DOCX/PDF
  adapters, exact 22 package roles, repository tool root `.tools`, and only
  `powershell` plus `microsoft_word_com` as system tools;
- both terminology snapshot paths.

The blueprint contains policies and relative paths only. File sizes and SHA-256
values must be generated by `author_scenario_publication_contract.py`, never
typed manually.

### Stage configs

- `master_en.json`: closed `kb_creator.master_en_publication.v3`, scenario
  `dissociation`, source-template `inputs: {}`, output `MASTER_EN.md`,
  `excluded_source_pages: []`, policies `source_page_comment_v1`, `preserve_v1`
  and `copy_markdown_references_v1`; required QA must include accepted upstream
  identity, exact projection/source disposition, asset and inventory closure,
  and independent v3 verification.
- `master_ru.json`: closed `kb_creator.master_ru_adapter.v1`; use one explicit
  positive `max_batch_chars` value (the proven neutral fixture uses `3000`).
- `artview/profile.json`: v3 source template with scenario id, rows derived only
  from the accepted reconstruction/source graph, and declarative presentation
  defaults. The adapter replaces future MASTER_RU input identities at Stage 30;
  the source graph and row images must already be exact path/bytes/SHA/media/
  dimensions records. No user ArtView choices or acceptance belong here.
- `html.json`: final neutral translator HTML source config. It must not contain
  a direct HTML/browser PDF engine or acceptance claims; the adapter derives
  run-local input/output/evidence paths later.
- `docx.json`: closed `kb_creator.production_docx_config.v1`, with explicit page,
  margins, fonts, sizes, spacing, heading levels 1-6, footer and metadata.
- `pdf.json`: closed policy marker `kb_creator.pdf_adapter.v1`; no HTML input or
  browser engine.
- `package.json`: closed policy marker `kb_creator.package_adapter.v1`; no
  acceptance or release state.

Config review must validate each config with its existing parser/schema where
one exists, verify copied terminology/image identities, and run the generic
contract author plus publication preflight. Contract authoring alone proves
identity and outer policy, not every future adapter's config semantics.

## Generic Stage 10 blocker and narrow remediation

`publication_adapters._master_en_adapter()` calls
`build_v3_candidate()`, copies its self-produced `MASTER_EN.qa.json`, and returns.
It never calls `verify_scenario_master_en.verify_v3_candidate()`, although that
independent verifier is already in the publication implementation inventory and
the architecture requires independent recomputation before the user gate.

This is P1 for live Stage 10: a successful stage and subsequent acceptance can
currently bind only producer-authored machine QA. Do not work around it with a
manual report outside the run.

Minimal engineering ownership:

- `kb_creator/pipeline/publication_adapters.py`;
- `kb_creator/tests/test_publication_registry_e2e.py`;
- optionally the narrow Stage 10 cases in
  `kb_creator/tests/test_publication_control_plane.py` only if needed for
  quarantine/acceptance evidence coverage.

Required behavior:

1. After building the run-local v3 candidate and before moving it into stage
   artifacts, call `verify_v3_candidate()` with the same copied contract,
   upstream package, derived runtime config and authority-relative candidate.
2. Require status `verified_candidate_pending_process_and_external_gates` and
   exact scenario/candidate inventory/MASTER_EN/config identities.
3. Write the canonical result as run-local
   `evidence/MASTER_EN.verification.json`; include it in the stage evidence
   inventory and user acceptance evidence set.
4. A verifier error must fail Stage 10, quarantine the partial staging tree,
   create no successful Stage 10 manifest, and leave no candidate acceptance.
5. Do not change the v3 builder/verifier semantics or legacy v1/v2 routes.

Exact tests:

- production-registry Stage 10 succeeds only with a present verification
  report whose identities match the candidate and derived config;
- a test builder producing a post-build altered MASTER_EN is rejected by the
  independent verifier, with no successful manifest/acceptance and quarantined
  partial output;
- the report is sealed into Stage 10 evidence and is accepted as run-local
  evidence by the separate acceptance recorder;
- direct v3 and legacy tests remain green;
- a CRLF accepted reconstruction fixture with Markdown hard breaks proves the
  only permitted textual change is LF serialization and that trailing two-space
  hard breaks and compact statblock line adjacency survive exactly.

No new schema is required unless engineering chooses to seal a new report
schema. If a new schema is proposed, stop for a versioned contract decision
rather than adding an ad hoc Stage 10-only shape.

## Exact execution commands

All commands run from repository root. First author the contract into its
absent target:

```powershell
& ".\.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe" -B `
  kb_creator\scripts\author_scenario_publication_contract.py `
  --blueprint kb_creator\inputs\dissociation\publication\v1\publication-blueprint.json `
  --config-root kb_creator\inputs\dissociation\publication\v1 `
  --output kb_creator\contracts\dissociation.publication.json
```

Create only the parent `kb_creator/working/dissociation/publication` before the
read-only preflight; keep the run root itself absent. Then:

```powershell
& ".\.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe" -B -m kb_creator `
  publication preflight `
  --contract kb_creator\contracts\dissociation.publication.json `
  --upstream-inventory kb_creator\working\dissociation\reconstruction\20260915-cpu-replay-09\promotion\reconstruction-upstream-v1\RECONSTRUCTION_INVENTORY.json `
  --reconstruction-acceptance kb_creator\working\dissociation\reconstruction\20260915-cpu-replay-09\promotion\reconstruction-upstream-v1\RECONSTRUCTION_ACCEPTANCE.json `
  --config-root kb_creator\inputs\dissociation\publication\v1 `
  --run-root kb_creator\working\dissociation\publication\20260915-publication-01 `
  --tools-root .tools `
  --json
```

Preflight must return `state: ready`, exit `0`, both accepted reconstruction
seals, and create no run root. Only after config review, verifier remediation
and independent implementation closure, run Stage 10:

```powershell
& ".\.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe" -B -m kb_creator `
  publication run `
  --contract kb_creator\contracts\dissociation.publication.json `
  --upstream-inventory kb_creator\working\dissociation\reconstruction\20260915-cpu-replay-09\promotion\reconstruction-upstream-v1\RECONSTRUCTION_INVENTORY.json `
  --reconstruction-acceptance kb_creator\working\dissociation\reconstruction\20260915-cpu-replay-09\promotion\reconstruction-upstream-v1\RECONSTRUCTION_ACCEPTANCE.json `
  --config-root kb_creator\inputs\dissociation\publication\v1 `
  --run-root kb_creator\working\dissociation\publication\20260915-publication-01 `
  --tools-root .tools `
  --python .tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe `
  --powershell C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe `
  --pdftoppm .tools\poppler\poppler-26.02.0\Library\bin\pdftoppm.exe `
  --word "C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE" `
  --run-id 20260915-publication-01 `
  --json
```

Expected exit is intentionally `10`, with state
`awaiting_master_en_acceptance`; it is a successful user gate, not a failure.
Do not run `resume` or `record-acceptance` in the same execution packet.

## Stage 10 output and QA contract

The absent run root is created with `run.json`,
`effective_publication_config.json`, then exactly one successful stage:

```text
outputs/10-master-en-candidate/artifacts/
  MASTER_EN.md
  MASTER_EN.provenance.json
  SOURCE_DISPOSITION.json
  ASSET_MANIFEST.json
  MASTER_EN.qa.json
  INVENTORY.json
  assets/<two referenced accepted binaries>
outputs/10-master-en-candidate/evidence/
  MASTER_EN.qa.json
  MASTER_EN.verification.json
  master_en_authority/<copied contract, upstream package, runtime config>
evidence/stages/10-master-en-candidate.manifest.json
```

Machine gates: accepted package/receipt identity, scenario and contract match,
six ordered source markers, zero excluded pages, exact source projection, unique
anchors, two referenced assets copied by identity, closed asset/disposition/
provenance/candidate inventories, independent verifier pass, and successful
stage manifest seal. Current read-only source census is six markers, 21
headings, zero explicit anchor tags and two image references.

The accepted file uses CRLF. V3 intentionally reads text and writes canonical
LF. With `excluded_source_pages: []`, the expected MASTER_EN text is 20,863
bytes and SHA-256
`2AD1E9175A3B53B7C85CCA5824B2FAA60D4A82C38928F487E6BB7700B5617CA6`.
This is line-ending normalization only. All ten Markdown hard-break lines retain
their trailing two spaces. The final `HUMAN RESISTANCE` statblock remains the
accepted compact consecutive-line form; no paragraph separators, reflow or
content edits are permitted.

The user gate is a review of the immutable Stage 10 candidate plus both machine
QA reports. The orchestrator may record `master_en` acceptance only after an
explicit user decision, using evidence already inside the Stage 10 evidence
root. Exit `10`, a passing QA file, or prior reconstruction acceptance must not
be interpreted as MASTER_EN acceptance.

## Findings

### P0

None.

### P1

1. No Dissociation publication blueprint, seven-config authority, publication
   contract or publication run parent exists, while v1 eagerly requires them
   all before Stage 10.
2. The production Stage 10 adapter does not invoke the existing independent v3
   verifier; a live user gate would otherwise rely on producer-authored QA.

### P2

1. The full-contract eager config seal makes an early independent Stage 10
   iteration expensive: any later config correction invalidates the entire run.
   Do not weaken v1 now. A future version may introduce stage-scoped config
   identities while preserving the final package's complete seven-role seal.

## Verification/evidence and next action

Read: repository instructions/governance, KB Creator README/status, active
plan/context, neutral publication Packet B/C/D authoring and independent-review
receipts, publication CLI/control/adapters, contract author, MASTER_EN builder
and verifier, publication/blueprint/run/stage/ArtView schemas, focused tests,
and the accepted run09 package read-only.

Read-only evidence confirmed the exact upstream/acceptance hashes, missing
publication paths, available repository-local Python and Poppler plus system
PowerShell/Word paths, and the source line-ending/marker/heading/asset/hard-break
census. No publication command or test suite was executed.

Blockers: declarative config/contract authoring, Stage 10 verifier wiring, and
independent implementation review.

Next action: dispatch the two non-overlapping owners above; run config validators
and the exact read-only publication preflight; obtain independent review; then
the orchestrator may execute only Stage 10 and stop at the MASTER_EN user gate.

## Final GO / NO-GO

- Declarative seven-config + blueprint/contract authoring: **GO**.
- Narrow independent-verifier adapter/test remediation: **GO**.
- Read-only preflight after those artifacts exist: **GO**.
- Live Stage 10 now: **NO-GO**.
- Live Stage 10 after both closures: **GO**, then stop at exit `10`.
- MASTER_EN acceptance, Stage 20+, ArtView decisions, rendering, package or
  release inference: **NO-GO**.
