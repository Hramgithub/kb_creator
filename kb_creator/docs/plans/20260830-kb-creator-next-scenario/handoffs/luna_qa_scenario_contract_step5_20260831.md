# Luna QA receipt — ScenarioContract.v1 Step 5 bounded QA

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `5-scenario-contract-bounded-qa`
- Role: bounded QA
- Policy model / effort: `gpt-5.6-luna` / `low`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; policy role honored
- Scoped override: `none`
- UI-visible task: `Viral Step 5 bounded QA`
- Task thread: `01a05484-23f9-7463-928e-9c33c8aa6e73`
- Candidate worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Candidate branch: `codex/kb-creator-viral`
- Candidate HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Disposable QA probe: `D:\NRI\_scenario_contract_lf_probe_20260830_d`
- Timestamp: `2026-08-31` (`Europe/Moscow`)
- Runtime-goal time at pre-receipt checkpoint: `310` seconds
- Runtime-goal token count at pre-receipt checkpoint: `188184`
- Detached receipt SHA-256: compute after this immutable write; it cannot be embedded without changing its own bytes

## Result

`blocked`

The corrected six-path ScenarioContract candidate itself replayed green:
focused execution and collect-only both returned the expected `119`, schema
parsing and canonical raw/frozen equality passed, shadow runtime profiles and
source resolution rejected fail-closed, the P2 scans were empty, and the full
suite reproduced exactly the known `15` missing-`kb_creator.pdf_raw`
collection-error baseline without a new error class.

The authorized ignored Innsmouth fixtures were materialized successfully and
matched their required identities. The prescribed 13-file Innsmouth family
then stopped during collection with two new errors because the retained probe
has no top-level `translator/` package:

- `test_build_innsmouth_html_from_master_ru.py` —
  `ModuleNotFoundError: No module named 'translator'`;
- `test_build_innsmouth_pdf_from_accepted_html.py` —
  `ModuleNotFoundError: No module named 'translator'`.

This is not the accepted 15-error full-suite baseline and is not one of the
previous missing-candidate/CRLF failures. Per the task's explicit “stop on new
failure” condition, no retry with another checkout on `PYTHONPATH`, no code
copy, no dependency installation, and none of the five verifier commands were
run after this failure. Step 5 QA therefore cannot be accepted from this
receipt.

No material candidate path, source, accepted package, production package,
translator file, test, script, plan/context/status/release file, Git index,
Git history, commit, or remote was changed. In the Viral worktree this receipt
is the only write. Probe writes are exactly the authorized QA fixtures recorded
below.

## Reviewed immutable inputs

The following were completely read before QA:

- `D:\NRI\AGENTS.md`;
- `docs/governance/nri_goal_governance.md`;
- active `plan.md` and `context.md`;
- remediation amendment
  `handoffs/sol_architect_scenario_contract_step5_remediation_20260830.md`:
  required and verified SHA-256
  `211134E8BB2A642BC9E61B1670BD07894B68A2F2E134030A9058CC7395A8A58F`;
- independent accept receipt
  `handoffs/gpt55_critic_scenario_contract_step5_remediation_review_20260830.md`:
  required and verified SHA-256
  `D81B5A277DB1CAA020A586ADD05605F2BEF4BF476D2508A998620A8A1EA923B8`;
- correction receipt
  `handoffs/luna_executor_scenario_contract_step5_correction_20260830.md`:
  required and verified SHA-256
  `F752E3996C4FBDFE1C4582F7FBD8E544AFF8E4C9A148A2A79BB40BFF447CE2C9`;
- all six current material files listed below.

## Six-path candidate identities

The before and pre-receipt-after identities were byte-identical:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `.gitattributes` | 622 | `943503F18B58DF37D7E33A29C44A1364A86D6B187978D2964A303B2B4A5D9F9D` |
| `kb_creator/contracts/scenario_contract.v1.schema.json` | 13426 | `25BF02364D4CE16E7D7DA96BD3E6B41D0E36B3642224F0989589B2335C5C07F2` |
| `kb_creator/contracts/innsmouth.json` | 3137 | `56E3B89B474CC466EBF6C84B8797E3D9AC56E34AD2B2294235415A073C98AD60` |
| `kb_creator/contracts/viral.json` | 4582 | `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D` |
| `kb_creator/scripts/scenario_contract.py` | 23157 | `51DFFCF62D0DFD41716FCD0B1330E9C6FF82A3A81A0578FB57B49BC34708C6F3` |
| `kb_creator/tests/test_scenario_contract.py` | 18252 | `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3` |

`git diff --check` exited `0`; its only output was the existing warning that
Git may replace `.gitattributes` LF with CRLF when it next touches the file.
`git diff --name-only` returned only `.gitattributes`; direct identities above
cover the ignored/untracked candidate paths. The six-path diff stat remained
one insertion in `.gitattributes` only.

## Probe identity and authorized fixture pre-state

The probe path resolved exactly to
`D:\NRI\_scenario_contract_lf_probe_20260830_d`, and `git rev-parse
--show-toplevel` returned the same root. It is a non-bare Git repository with
`.git` in the root, branch label `master`, no commits/valid `HEAD`, no remote,
and only `.gitattributes` plus `kb_creator/` at top level. This retained probe
is therefore not a complete repository checkout: notably, it has no
top-level `translator/` directory.

Before fixture writes:

- probe porcelain `-uall`: `1061` lines, UTF-8 status-text SHA-256
  `899425AB94BD3E91F5047AF30425AAAE440981BE5558847EDDA514DD53218E15`;
- MASTER_RU target: absent;
- HTML target file/root/assets: absent;
- glossary target: already present at `12594` bytes / SHA-256
  `93587612E9719FF209D2D092734A592BAA7DA20965444C0A3FA2F2EAE9247346`,
  identical to its authorized production source, so it was not overwritten.

Every target was resolved with `Path.GetFullPath` and verified to begin with
the exact probe root plus a directory separator before any copy.

## Authorized disposable fixtures

### MASTER_RU working candidate

- read-only source:
  `D:\NRI\.worktrees\innsmouth-master-en-main\kb_creator\working\innsmouth_direct_master_ru\MASTER_RU.md`;
- probe target:
  `D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\working\innsmouth_direct_master_ru\MASTER_RU.md`;
- source and target: `195422` bytes;
- source and target SHA-256:
  `BAF53B8E20AA91D3124AE83C7D3A533F4D9D16B9F104AB47B93995B048C81FC9`.

### HTML working candidate

- immutable probe source root:
  `kb_creator/inputs/innsmouth/html/accepted_20260830_r6/`;
- probe target root:
  `kb_creator/working/innsmouth_direct_html/accepted_20260830_candidate_r11/`;
- copied HTML only:
  `The_Innsmouth_Terror_RU.html`, `226114` bytes, SHA-256
  `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`;
- copied asset directory only: exactly `32` files;
- post-copy asset mismatch count against source by name, bytes, and SHA-256:
  `0`;
- authoritative `HTML.acceptance.json` inventory SHA-256:
  `849C8238A9165EADC8A796B6A2501C84E9CD220F303CD70E46940FAF6C1E3019`.

### Production glossary

- immutable probe source:
  `kb_creator/inputs/innsmouth/production/pipeline/terminology/CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md`;
- probe target:
  `kb_creator/docs/terminology/CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md`;
- source and pre-existing target: `12594` bytes, SHA-256
  `93587612E9719FF209D2D092734A592BAA7DA20965444C0A3FA2F2EAE9247346`;
- action: identity verified; no overwrite performed.

After fixture materialization, probe porcelain `-uall` contained `1095` lines,
status-text SHA-256
`F8C27C10E6F2B66BE2E300B711C77954606195B661593303D0307975E16CCD0C`.
The increase is exactly `34` paths: one MASTER_RU, one HTML, and 32 assets.
The glossary already existed in pre-state. Targeted status enumerated only the
three authorized fixture locations.

## ScenarioContract focused QA

Command:

`python -B -m pytest kb_creator/tests/test_scenario_contract.py -q -p no:cacheprovider`

- exit: `0`;
- result: `119 passed in 0.18s`.

Collect-only command:

`python -B -m pytest kb_creator/tests/test_scenario_contract.py --collect-only -q -p no:cacheprovider`

- exit: `0`;
- result: `119 tests collected in 0.04s`.

The focused suite includes one successful source-resolution case, eight
negative observation/path/identity cases, and the shadow-first filesystem-probe
rejection case: all ten passed as part of the 119.

Independent direct evidence:

- schema JSON parse: `OK`;
- draft: `https://json-schema.org/draft/2020-12/schema`;
- Viral raw/frozen canonical SHA-256:
  `C2EF2DD143E304F59C8973E8DB82CF83B094BC35DDA37BB2299686E1FE6DA194` /
  same; bytes equal `true`; canonical bytes `4067`;
- Innsmouth raw/frozen canonical SHA-256:
  `46D10BE6B4D639AAE0C28CDF510E7CB96B3DB66CE1FB98190E2FCB95532B523E` /
  same; bytes equal `true`; canonical bytes `2490`;
- Innsmouth shadow under `intake`: rejected;
- Innsmouth shadow under `reconstruction_ready`: rejected;
- Innsmouth shadow source resolution: rejected before filesystem access.

## Full-suite baseline diagnostic

Command:

`python -B -m pytest kb_creator/tests -q -p no:cacheprovider`

- exit: `1`;
- result: interrupted during collection with exactly `15 errors in 1.20s`;
- missing classes: `kb_creator.pdf_raw.page_proof`,
  `kb_creator.pdf_raw.errors`, and
  `kb_creator.pdf_raw.raw_authority_projection`;
- comparison: exact known count and module-family baseline; no new class in
  this active-worktree diagnostic;
- disposition: full suite is not green and is not reported green.

## Collectable 13-file Innsmouth family

Selection expression:

`^(test_(build|freeze)_innsmouth|test_innsmouth_)`

Selected exactly 13 files:

1. `test_build_innsmouth_html_from_master_ru.py`
2. `test_build_innsmouth_master_en.py`
3. `test_build_innsmouth_pdf_from_accepted_html.py`
4. `test_build_innsmouth_production_package.py`
5. `test_build_innsmouth_reconstructed_en.py`
6. `test_freeze_innsmouth_html_repo_input.py`
7. `test_freeze_innsmouth_master_en_repo_input.py`
8. `test_freeze_innsmouth_master_ru_repo_input.py`
9. `test_freeze_innsmouth_pdf_repo_output.py`
10. `test_innsmouth_final_result.py`
11. `test_innsmouth_master_en_packet7_user_review_successor.py`
12. `test_innsmouth_master_en_repo_input.py`
13. `test_innsmouth_source_to_artifacts.py`

Execution command:

`python -B -m pytest @innsmouthTests -q -p no:cacheprovider`

- exit: `2`;
- collected/executed test count: `0` (collection interrupted);
- new collection errors: `2`;
- elapsed: `0.61s`;
- blocker: both importing build modules require `from translator import
  translator`, but this probe has no `translator` package.

No rerun or environment substitution was attempted because the task required a
stop on any new failure.

## Existing five verifiers

All five verifier runs were stopped and remain `NOT RUN` after the new
13-file collection failure. Therefore there are no current-task exit codes,
counts, manifest checks, or acceptance claims for these commands:

1. EN accepted MASTER verifier — `NOT RUN`;
2. RU accepted MASTER verifier with the probe glossary — `NOT RUN`;
3. HTML accepted-input verifier with probe MASTER_RU/HTML paths — `NOT RUN`;
4. PDF accepted-output verifier with real accepted HTML/PDF roots — `NOT RUN`;
5. production package verifier against the probe production root — `NOT RUN`.

Prior correction-receipt verifier results were reviewed as prerequisite
evidence but are not replayed or promoted as this QA task's results.

## LF, blob, and raw-byte evidence

For both:

- `kb_creator/inputs/innsmouth/html/accepted_20260830_r6/The_Innsmouth_Terror_RU.html`;
- `kb_creator/inputs/innsmouth/production/The_Innsmouth_Terror_RU.html`;

the probe reports:

- `git check-attr`: `text: set`, `eol: lf`;
- `git ls-files --eol`: `i/lf w/lf attr/text eol=lf`;
- index blob: `327c4f2a2d30468f8895213b295324e2457af67b`;
- `git hash-object`: `327c4f2a2d30468f8895213b295324e2457af67b`;
- raw bytes: `226114`;
- raw SHA-256:
  `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`.

## P2 scans

Scoped surface: only `kb_creator/scripts`, `kb_creator/contracts`, and
`kb_creator/tests`.

- `(build|freeze)_viral_.*\.py`: `rg` exit `1`, no match;
- `translator[\\/]config[\\/]viral\.package\.json|viral\.package\.json`:
  `rg` exit `1`, no match.

There is no copied Viral build/freeze script family and no executable/config
dependency on the legacy Viral package in the scoped implementation surface.

## Before/after state and no-mutation evidence

### Active Viral worktree

- pre-QA porcelain `-uall`: `15` lines, status-text SHA-256
  `5485D8E378EC47B240C2DE305A75C20A1E3E63F28150CAD870825408237553E0`;
- pre-receipt post-QA porcelain: same `15` lines and same status hash;
- active accepted/source targeted status: empty before receipt;
- all six material hashes: unchanged as listed above;
- HEAD before/after QA execution:
  `54607bd3b9362adbb0c4bca64e8751482797f380`;
- index listing SHA-256 at pre-receipt checkpoint:
  `58F66AD6A213C8924010C7E4D96759BF36D26F8803315BB494AE385B12ECF5BD`.

The only expected final status delta is this new untracked immutable receipt.

### Original Innsmouth worktree

- branch: `codex/innsmouth-master-en-main`, ahead of its remote by the existing
  three commits;
- pre-QA porcelain: `418` lines, status-text SHA-256
  `47E73CE29C9EBA27F137E5D985918EC250CCF895F5656B4B31FDAB53E5250EBD`;
- post-QA porcelain: same `418` lines and same status hash;
- HEAD before/after:
  `54607bd3b9362adbb0c4bca64e8751482797f380`;
- exact ignored MASTER_RU source after QA remains `195422` bytes / SHA-256
  `BAF53B8E20AA91D3124AE83C7D3A533F4D9D16B9F104AB47B93995B048C81FC9`.

No original-worktree byte or Git state changed.

### Disposable probe

- expected fixture delta only: `34` newly materialized paths (MASTER_RU,
  HTML, 32 assets);
- glossary was already present and unchanged;
- accepted HTML, production HTML, their index blobs, and immutable fixture
  sources were not changed;
- probe Git index/history was not changed and no commit exists.

## Blockers

1. The retained LF probe is not a complete checkout and lacks the top-level
   `translator/` package required by two of the selected Innsmouth test files.
   This produced two new collection errors and triggered the mandatory stop.
2. Because execution stopped, the 13-file family has no passing test count and
   all five current-task verifier replays remain absent.
3. Independently, the known full-suite baseline still contains exactly 15
   missing-`kb_creator.pdf_raw` collection errors; it remains visible and is
   not part of this QA fix.

## Forbidden work not performed

- no dependency installation;
- no `pdf_raw` module creation;
- no test/script/contract/material edit;
- no old Viral translation copy;
- no Viral PDF processing, source reconstruction, OCR, translation, render,
  build, freeze, or publication work;
- no accepted/production/source/translator mutation;
- no plan/context/status/release edit;
- no Git add/index/history mutation, commit, push, or remote operation.

## Next action

The main-chat orchestrator should treat this QA as blocked, capture this
receipt, and decide how to provide a complete disposable LF probe containing
the repository-owned `translator/` package without importing it ad hoc from a
different checkout. Then rerun the same bounded QA from a fresh/validated probe.
Only after the 13-file family and all five verifiers pass should Step 5 proceed
to fresh independent implementation review. Source reconstruction remains
blocked.
