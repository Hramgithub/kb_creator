# Step 5 executor packet: minimal scenario-contract implementation

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `5-minimal-reusable-implementation`
- Assigned role / effort: bounded executor, `gpt-5.6-luna` / `medium`
- Engineering contributor: `gpt-5.6-terra` / `medium`
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: policy roles matched; actual platform model/effort unavailable
- Scoped override: `none`

## Fixed review evidence and scope

Treat these as immutable reviewed inputs; do not edit or reinterpret them.

- Architecture candidate: `scenario_contract_architecture.md`, SHA-256
  `EF96C3B155EB749FBABDFEA5B86BD4C190854F3029D8693E7F09D051F4B9FDBE`.
- Independent architecture review: `handoffs/gpt55_critic_scenario_contract_architecture_review_20260830.md`, SHA-256
  `DC469CE5EC55EFB114B6E196149AB5C05C9462CCDF662BE056890083F783F733`.
- Binding resolution: `viral.json` uses exactly `Viral_RU.html` and
  `Viral_RU.pdf`; placeholders are forbidden.

The complete implementation allowlist is exact:

1. add `kb_creator/contracts/scenario_contract.v1.schema.json`;
2. add `kb_creator/contracts/innsmouth.json`;
3. add `kb_creator/contracts/viral.json`;
4. add `kb_creator/scripts/scenario_contract.py`;
5. add `kb_creator/tests/test_scenario_contract.py`;
6. modify only `.gitattributes`.

Do not change existing Innsmouth stage scripts, any accepted/production package
or manifest, source material, `translator/`, plan/context/status/release files,
Git index/history, or generated output. Do not commit or push. The shadow
contract is validation-only and must not be wired into any existing runtime.

## Evidence-derived facts and fact stop boundary

### Viral facts permitted in `viral.json`

Use only the following intake facts, recorded in the active context and
architecture:

- `schema`: `kb_creator.scenario_contract.v1`; revision `1`.
- scenario: id `viral`, title `Viral`, product type `coc_scenario`, source
  language `en`, publication languages `en`, `ru`.
- source: `external_pdf`, locator hint `Call_of_Cthulhu_Viral.pdf`, SHA-256
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`,
  `20718150` bytes, `124` pages, page base `1`, media box `[612, 792]`,
  rotation `0`.
- scope: `all_source_pages`, `1..124`, with
  `numbered_player_handouts: 39`.
- approved artifact basenames: `RECONSTRUCTED_EN.md`, `MASTER_EN.md`,
  `MASTER_RU.md`, `Viral_RU.html`, `Viral_RU.pdf`, and
  `PRODUCTION_MANIFEST.json`.
- page role ranges proven by current reconnaissance: scenario body `6..68`,
  player handouts `69..103`, Keeper maps `104..110`, pregenerated
  investigators `111..123`, and back cover `124`.
- pages `1..5` have not received a reviewed primary-role partition. They must
  be represented under an allowed intake-only declaration with `content_mode`
  `unknown`, so `intake` passes but `reconstruction_ready` fails. Do not invent
  cover/credits/front-matter/contents page boundaries.
- historical EN/RU is reference-only. Do not put it in a stage input,
  translation lineage, merge input, or acceptance provenance.

Use no legacy Viral package field merely because it exists. In particular,
`translator/config/viral.package.json` is neither authority nor a runtime
dependency.

### Innsmouth shadow facts permitted in `innsmouth.json`

The fixture may use only facts directly visible in current accepted manifests
or existing script constants. Current production evidence establishes scenario
display package `The_Innsmouth_Terror`, final names `MASTER_EN.md`,
`MASTER_RU.md`, `The_Innsmouth_Terror_RU.html`,
`The_Innsmouth_Terror_RU.pdf`, and accepted roots
`master_en/accepted_20260830_r6`, `master_ru/accepted_20260830_r6`,
`html/accepted_20260830_r6`, and `pdf/accepted_20260830_r7`. The reconstruction
script supplies source-candidate SHA-256
`1504a9c71ca995748e4125b7303c0d3064e588abb226ebb5ab99a5f5763c993c` and
PDF-control SHA-256 `5850b26a077390abff4a321e754a3709d6148fa4ac7a9f4d63bdbeff6949b1bb`.

Before encoding every required source, page-role, policy, acceptance, or
exception field, the executor must point to its exact manifest key or script
constant. Stop rather than guess if any field necessary for a valid v1 shadow
fixture lacks that evidence, if the script and manifest conflict, or if the
source PDF byte count/page count/geometry cannot be established from the allowed
authorities. Do not derive missing source facts from historical output, legacy
translator configuration, filenames, or heuristics. Report the missing key and
the inspected paths to the orchestrator.

## Required implementation contract

### Closed JSON schema

Implement Draft 2020-12 (or the repository's stdlib-compatible structural
subset, with the Python semantic validator supplying the rest). Every object,
including nested policy/reference/exception/page-role objects, uses
`additionalProperties: false`. Required top-level fields are:

```text
schema, contract_revision, scenario, source, scope, page_roles,
artifacts, policies, acceptance, exceptions
```

Close the v1 enums exactly as architecture specifies:

- product/source/language: `coc_scenario`, `external_pdf`, source `en`,
  publication `en` and `ru`;
- primary roles: `cover`, `credits`, `front_matter`, `contents`,
  `scenario_body`, `player_handouts`, `keeper_maps`,
  `pregenerated_investigators`, `back_cover`;
- content modes: `text`, `mixed`, `visual`, `unknown`;
- traits: `multi_column`, `low_text`, `zero_text`, `table_heavy`, `statblock`,
  `form_like`;
- named extraction strategies: `embedded_text`, `reading_order`, `ocr_region`,
  `visual_preserve`;
- exceptions: `text_repair`, `reading_order`, `list_continuation`,
  `publication_suppression`, `semantic_link`, `asset_owner`,
  `render_placement`, `page_break`.

Reject executable or dependency-bearing configuration: commands, shell strings,
engine executables, arbitrary import/module paths, templates, custom stage DAGs,
or unknown policy keys. A contract must not contain mutable output hashes.
`source.locator_hint` is a basename only; absolute paths, drives, separators,
`..`, and URI-like durable locators fail. Artifact values are unique safe
relative basenames with no slash, drive, `..`, accepted/date/release suffix, or
placeholder; they include the two fixed Viral render names above.

### Semantic validator/API

`scenario_contract.py` is Python stdlib only and has no build, freeze, render,
translation, source-processing, or write operation. Provide a small public API
with explicit errors, sufficient for tests and later handlers:

```text
load_contract(path, profile="intake") -> immutable contract view
validate_contract(data, profile="intake") -> immutable contract view
canonical_contract_bytes(data) -> bytes
contract_sha256(data) -> uppercase SHA-256
resolve_source_path(contract, runtime_path) -> Path
```

The loader reads UTF-8 JSON, performs structural validation then semantic
validation, and never treats a runtime absolute source path as contract data or
digest input. Canonical bytes are deterministic JSON (UTF-8, stable key order,
compact separators) after validation; digesting the same semantic document must
not depend on a runtime source locator. Frozen structures must prevent accidental
post-validation mutation.

Semantic validation must enforce all cross-field rules: exact schema/revision;
safe scenario id `^[a-z0-9]+(?:-[a-z0-9]+)*$`; positive source identity and
geometry; source-page scope; a one-and-only-one primary-role partition over the
complete page interval; valid modes/traits/strategies; unique artifacts;
non-overlapping selectors; closed fixed acceptance stage keys for
`reconstructed_en`, `master_en`, `master_ru`, `html`, `pdf`, `production`;
reference-only historical sources; and stage-scoped, evidenced, approval-gated,
unique-id exceptions with positive exact match counts. Exceptions must never
weaken identity, all-pages coverage, provenance, accepted-upstream requirements,
the manual-generated-output ban, or the release gate.

Profile rules: `intake` may admit the explicitly declared `unknown` modes in
Viral; `reconstruction_ready` rejects every unknown mode and requires the full
role/policy closure. Both profiles reject unsafe/missing source identity and all
structural violations.

## Test matrix

Keep all tests in `test_scenario_contract.py`; they require no network and write
only pytest temporary space. Include tests for:

1. schema + semantic success for both contracts under their appropriate profile;
2. exact Viral identity, complete `1..124` partition, 39 handouts, all-pages
   scope, and exact `Viral_RU.html` / `Viral_RU.pdf` names;
3. Viral `intake` acceptance and `reconstruction_ready` rejection caused by the
   current pages `1..5`/unknown-mode prerequisite;
4. rejection of unknown keys, invalid identifiers/hashes/counts/geometry,
   absolute locators, unsafe/duplicate names, page gaps/overlaps, invalid
   roles/modes/traits/policies, executable fields, invalid exception kinds and
   zero/extra-match exceptions;
5. reference-only historical sources cannot be accepted as stage input or
   translation lineage;
6. canonical bytes/digest determinism and independence from a runtime absolute
   source path;
7. Innsmouth shadow facts selected from current manifest/script evidence and
   confirmation that loading it has no runtime wiring or output side effect.

Do not weaken a test merely to make the incomplete Viral topology
`reconstruction_ready`; the correct expected result is failure until reviewed
facts exist.

## Scoped LF prerequisite

Append exactly this narrow tracked-content rule to `.gitattributes`:

```gitattributes
kb_creator/inputs/**/*.html text eol=lf
```

It is narrower than a repository HTML rule and covers only manifest-bound input
HTML (accepted and production trees) below `kb_creator/inputs`. It overrides the
current `* text=auto` checkout behavior without touching PDFs or source files.
The current evidence before the change is `core.autocrlf=true`, `i/lf w/crlf`,
and the same index blob `327c4f2a2d30468f8895213b295324e2457af67b` for:

```text
kb_creator/inputs/innsmouth/html/accepted_20260830_r6/The_Innsmouth_Terror_RU.html
kb_creator/inputs/innsmouth/production/The_Innsmouth_Terror_RU.html
```

The expected raw identity for each is `226114` bytes and SHA-256
`B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`.
Do not normalize verifier input, re-freeze, re-manifest, edit either HTML file,
or update an accepted/production hash.

For a non-destructive fresh-checkout proof, use a newly created disposable probe
directory outside this worktree; do not run restore/reset/clean in the active
worktree. The probe may use a temporary clone and temporary index only; it must
not commit, push, or change the active index/history. In the probe, make the
same one-line `.gitattributes` change, stage it only in the probe's temporary
index so checkout attributes are applied, then force-checkout only the two known
HTML paths in that new probe. Capture raw bytes/hash, `check-attr`, `ls-files
--eol`, and `ls-files -s` before/after. The two target index blob IDs and all
active-worktree accepted/production manifest file hashes must be unchanged.
Leaving the probe for orchestrator inspection is preferable to deleting it.

## Exact acceptance commands

Run from the worktree root after implementation. Commands are deliberately
limited to the allowed implementation surface or specified Innsmouth evidence.

```powershell
python -B -m pytest kb_creator/tests/test_scenario_contract.py -q
python -B -m pytest kb_creator/tests -q

python -B kb_creator/scripts/verify_innsmouth_master_en_repo_input.py
python -B kb_creator/scripts/freeze_innsmouth_master_ru_repo_input.py --verify
python -B kb_creator/scripts/freeze_innsmouth_html_repo_input.py --verify
python -B kb_creator/scripts/freeze_innsmouth_pdf_repo_output.py --verify
python -B kb_creator/scripts/build_innsmouth_production_package.py --verify

git check-attr text eol -- kb_creator/inputs/innsmouth/html/accepted_20260830_r6/The_Innsmouth_Terror_RU.html kb_creator/inputs/innsmouth/production/The_Innsmouth_Terror_RU.html
git ls-files --eol -- kb_creator/inputs/innsmouth/html/accepted_20260830_r6/The_Innsmouth_Terror_RU.html kb_creator/inputs/innsmouth/production/The_Innsmouth_Terror_RU.html
git ls-files -s -- kb_creator/inputs/innsmouth/html/accepted_20260830_r6/The_Innsmouth_Terror_RU.html kb_creator/inputs/innsmouth/production/The_Innsmouth_Terror_RU.html
Get-FileHash -Algorithm SHA256 kb_creator/inputs/innsmouth/html/accepted_20260830_r6/The_Innsmouth_Terror_RU.html, kb_creator/inputs/innsmouth/production/The_Innsmouth_Terror_RU.html

$allowed = @('.gitattributes','kb_creator/contracts/scenario_contract.v1.schema.json','kb_creator/contracts/innsmouth.json','kb_creator/contracts/viral.json','kb_creator/scripts/scenario_contract.py','kb_creator/tests/test_scenario_contract.py')
# Record `git status --porcelain` before implementation in the executor receipt.
# This worktree already has untracked goal documentation, so compare the post-run
# status with that recorded baseline.  The delta must be exactly $allowed.
git diff --name-only HEAD
git ls-files --others --exclude-standard

$surface = @('kb_creator/scripts','kb_creator/contracts','kb_creator/tests')
$viralFamily = rg --files $surface | rg '(^|[\\/])(build|freeze)_viral_[^\\/]*\.py$'; if ($LASTEXITCODE -eq 0) { throw "Copied Viral stage family: $viralFamily" } elseif ($LASTEXITCODE -ne 1) { throw 'Viral-family search failed' }
rg -n --glob '*.py' --glob '*.json' 'translator[\\/]config[\\/]viral\.package\.json' $surface; if ($LASTEXITCODE -eq 0) { throw 'Legacy Viral config runtime/config reference found' } elseif ($LASTEXITCODE -ne 1) { throw 'Legacy-reference search failed' }
```

The P2 scans intentionally exclude documentation and `translator/`: a filename
scan proves no copied runtime script family, while the constrained Python/JSON
scan proves no runtime/config dependency. Do not use a broad repository search
as an acceptance substitute.

## Executor stops, receipt, and safety

Stop and report to the orchestrator (without improvised substitutions) if:

- either reviewed hash differs;
- a required Innsmouth fixture fact is absent/conflicting;
- a schema/policy needs code, a command, a plugin/import path, or an unclosed
  enum to represent it;
- the LF rule changes a Git content blob, any accepted/production file, or a
  manifest identity rather than checkout serialization only;
- the fresh probe does not produce raw LF bytes and the existing verifier green;
- any existing Innsmouth test/verifier is red after the scoped change;
- any file outside the six-path allowlist would need modification; or
- work would start source copy/extraction/OCR/translation/rendering/publication.

The executor writes one immutable receipt under this goal's `handoffs/`, naming
the exact changed paths, architecture/review hashes, contract-test output,
P2 commands/results, before/after EOL/blob/raw-byte evidence, probe location,
all verifier outputs, stop/blocker state, next action, elapsed time, token use
or `unavailable`, timestamp, role/model/effort, orchestrator policy owner,
assignment state, and scoped override. It does not edit canonical plan/context.

## Engineering contributor receipt

- Role: engineering assistance, policy `gpt-5.6-terra` / `medium`.
- Actual model/effort: unavailable (not exposed by this surface).
- Scope/result: prepared this executable implementation packet only; no
  implementation or Git mutation.
- Files read: `AGENTS.md`; `docs/governance/nri_goal_governance.md`; active
  `plan.md`, `context.md`, architecture candidate and architect/critic receipts;
  `.gitattributes`; current Innsmouth reconstruction script/constants and
  accepted/production manifests; live Git EOL/blob status.
- Only file changed: this packet.
- Verification: candidate and critic SHA-256 values matched the assigned
  digests; live state confirmed `core.autocrlf=true`, `i/lf w/crlf`, and shared
  blob `327c4f2a2d30468f8895213b295324e2457af67b` for the two manifest-bound
  HTML paths; no implementation was run.
- Blockers: none for packet delivery; fact absence during shadow-fixture
  implementation is an explicit stop condition.
- Next action: orchestrator reviews this packet, then dispatches the bounded
  executor against the exact six-path allowlist.
- Elapsed time: approximately 30 minutes.
- Token use: unavailable.
- Timestamp: `2026-08-30T20:29:21+03:00`.
