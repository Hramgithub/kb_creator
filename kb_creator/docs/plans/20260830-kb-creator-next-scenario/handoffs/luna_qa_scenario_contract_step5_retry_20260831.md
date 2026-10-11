# Luna QA retry receipt — ScenarioContract.v1 Step 5 bounded QA

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `5-scenario-contract-bounded-qa-retry`
- Role: bounded QA
- Policy model / effort: `gpt-5.6-luna` / `low`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; policy role honored
- Scoped override: `none`
- UI-visible task: `Viral Step 5 QA retry`
- Task thread: `01a0548c-614e-7c22-8fb0-8db4b9c575ff`
- Candidate worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Candidate branch / HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Disposable QA probe: `D:\NRI\_scenario_contract_lf_probe_20260830_d`
- Timestamp: `2026-08-31T00:30:51+03:00` (`Europe/Moscow`)
- Elapsed time: approximately 25 minutes wall-clock; exact task timer unavailable
- Token use: `unavailable`; no precision invented
- Detached receipt SHA-256: compute after this immutable write; it cannot be embedded without changing its own bytes

## Result

`pass` for the bounded Step 5 QA retry.

The concrete prior probe blocker is resolved without changing the candidate:
the exact repository-owned `translator` tree was materialized from Git commit
`54607bd3b9362adbb0c4bca64e8751482797f380`, verified as tree object
`19df09963da89dc6a880b9f1783b7259f19cd644`, with exactly `193` files and
zero file-list or per-file blob mismatches. No working checkout supplied code
and `PYTHONPATH` was not changed.

The exact 13-file Innsmouth family then passed (`96 passed, 14 skipped`), all
five current verifier commands passed with real required arguments, focused
ScenarioContract execution and collect-only both returned `119`, targeted
shadow/source-resolution execution returned `10 passed`, schema/canonical/P2/LF
evidence passed, and no new failure class appeared.

The repository-wide suite remains explicitly non-green: it exits `2` during
collection with exactly the known `15` missing-`kb_creator.pdf_raw` errors.
This baseline was reproduced and is not concealed or reclassified as green.

No candidate material, source, accepted package, production package, original
worktree, plan/context/status/release file, Git index/history, commit, push, or
remote was changed. This receipt is the only active-worktree write by this QA
retry. Probe additions are only the prior authorized 34 fixtures plus the exact
193-file translator tree; 14 disposable outputs created by the regression run
were enumerated and removed before the final state snapshot.

## Reviewed immutable inputs and hashes

The applicable `AGENTS.md`, `docs/governance/nri_goal_governance.md`, current
`plan.md`, and current `context.md` were read before active work. Required
receipt identities all matched:

| Input | Verified SHA-256 |
|---|---|
| remediation amendment `sol_architect_scenario_contract_step5_remediation_20260830.md` | `211134E8BB2A642BC9E61B1670BD07894B68A2F2E134030A9058CC7395A8A58F` |
| independent accept `gpt55_critic_scenario_contract_step5_remediation_review_20260830.md` | `D81B5A277DB1CAA020A586ADD05605F2BEF4BF476D2508A998620A8A1EA923B8` |
| correction receipt `luna_executor_scenario_contract_step5_correction_20260830.md` | `F752E3996C4FBDFE1C4582F7FBD8E544AFF8E4C9A148A2A79BB40BFF447CE2C9` |
| blocked QA receipt `luna_qa_scenario_contract_step5_20260831.md` | `E264637B6444BDFF16EBE55E223645D6F0B1F5041AB10373EC403B13DE241ACE` |

## Translator Git-object provenance and verification

Preconditions:

- exact probe root resolved to `D:\NRI\_scenario_contract_lf_probe_20260830_d`;
- `probe\translator` was absent;
- `git ls-tree 54607bd3 translator` returned mode `040000`, type `tree`,
  object `19df09963da89dc6a880b9f1783b7259f19cd644`;
- recursive tree count was exactly `193`; every file mode was `100644`.

The requested initial `git archive` path was tested but rejected as final
evidence: Windows tar mangled one UTF-8 filename, while ZIP preserved names but
Git archive filters changed eight text-file blobs. Each failed extraction was
removed only at the exact validated `probe\translator` target before retry;
no other probe path was touched.

Final materialization used only Git plumbing from the exact commit/object:
`git ls-tree -r 54607bd3 translator` supplied each path/blob id and
`git cat-file blob <object-id>` supplied raw bytes directly into the probe.
Final audit against `git ls-tree -r`:

- expected files: `193`;
- actual files: `193`;
- missing: `0`;
- extra: `0`;
- per-file `git hash-object --no-filters` mismatches: `0`;
- verified tree provenance: `19df09963da89dc6a880b9f1783b7259f19cd644`.

No checkout-to-checkout copy, dependency installation, import-path change,
stage/commit, or overwrite of a pre-existing target occurred.

## Existing authorized fixtures

The blocked receipt's fixture identities were reverified before tests:

- MASTER_RU source and probe target: `195422` bytes, SHA-256
  `BAF53B8E20AA91D3124AE83C7D3A533F4D9D16B9F104AB47B93995B048C81FC9`;
- working HTML source and probe target: `226114` bytes, SHA-256
  `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`;
- working HTML assets: source `32`, target `32`, missing `0`, identity
  mismatches by relative path/bytes/SHA-256 `0`;
- production glossary source and existing probe target: `12594` bytes,
  SHA-256
  `93587612E9719FF209D2D092734A592BAA7DA20965444C0A3FA2F2EAE9247346`;
  it was not overwritten.

The existing fixture status delta remained exactly `34` paths: one MASTER_RU,
one HTML, and 32 assets. Together with the exact translator tree these are the
only retained additions made for this QA retry.

## Exact 13-file Innsmouth family

Selection expression: `^(test_(build|freeze)_innsmouth|test_innsmouth_)`.
It selected exactly:

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

Command from the probe:

`python -B -m pytest @innsmouthTests -q -p no:cacheprovider`

- exit: `0`;
- result: `96 passed, 14 skipped in 7.77s`;
- new failure: none.

The test run created exactly 14 disposable files in five probe-only test
directories: `test_source_structure_hazard_audit` (3),
`test_occluded_text_layer_content` (1), `test_clean_config` (1),
`test_translation_batches_contract` (7), and
`test_artifact_comparison_acceptance` (2). These outputs explained the full
temporary status increase from 1288 to 1302 lines and were removed from the
validated `kb_creator\working\test_*` targets. Final probe status returned
exactly to the authorized 1288-line state.

## Five verifier replays

All current CLIs were inspected with `--help`; only verify modes were used.

1. EN accepted MASTER:

   `python -B kb_creator/scripts/verify_innsmouth_master_en_repo_input.py --root D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\inputs\innsmouth\master_en\accepted_20260830_r6`

   Exit `0`; `INNSMOUTH_ACCEPTED_MASTER_EN_REPO_INPUT_OK`; 36 files, 33
   assets, 9,505,373 bytes, inventory
   `E1665ED05CE8C19443DB98D02D0FA9B2A957EA2C34114E438217DE95DB26CB8B`.
   Manifest: 1320 bytes /
   `AD9A6546EB7421F4387A4E6B547B2CD6B61346A3B326D25110A56028FC919B83`.

2. RU accepted MASTER:

   `python -B kb_creator/scripts/freeze_innsmouth_master_ru_repo_input.py --verify --glossary D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\docs\terminology\CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md --master-en-root D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\inputs\innsmouth\master_en\accepted_20260830_r6 --target D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\inputs\innsmouth\master_ru\accepted_20260830_r6`

   Exit `0`; `INNSMOUTH_ACCEPTED_MASTER_RU_REPO_INPUT_OK`; MASTER_RU
   189146 bytes /
   `B67CCE65F18984117204A12AD3ACB79E51D2E50622993268121458070B25E2BB`;
   32 assets, inventory
   `849C8238A9165EADC8A796B6A2501C84E9CD220F303CD70E46940FAF6C1E3019`;
   glossary identity matched. Manifest: 4075 bytes /
   `B87C34F312258FB349B6AE549A398637096CE3A29D9B623EEDA28D5ECF4EC384`.

3. HTML accepted input:

   `python -B kb_creator/scripts/freeze_innsmouth_html_repo_input.py --verify --master-ru-root D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\inputs\innsmouth\master_ru\accepted_20260830_r6 --target D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\inputs\innsmouth\html\accepted_20260830_r6`

   Exit `0`; `INNSMOUTH_ACCEPTED_HTML_REPO_INPUT_OK`; HTML 226114 bytes /
   `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`;
   32 assets, inventory
   `849C8238A9165EADC8A796B6A2501C84E9CD220F303CD70E46940FAF6C1E3019`;
   45 TOC heading targets. Manifest: 7208 bytes /
   `F3A6EC483858060B46EB266893FEE7D4AE4F63D3A9A0A26CCB899D5903B4375A`.

4. PDF accepted output:

   `python -B kb_creator/scripts/freeze_innsmouth_pdf_repo_output.py --verify --html-root D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\inputs\innsmouth\html\accepted_20260830_r6 --target D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\inputs\innsmouth\pdf\accepted_20260830_r7`

   Exit `0`; `INNSMOUTH_ACCEPTED_PDF_REPO_OUTPUT_OK`; PDF 11557577 bytes /
   `6883AE5D15FB498477239B98B3D278E458223EACA1691B3C73EB17F987D5E0E5`;
   36 pages, no empty pages, 89 internal links, 45/45 exact heading
   landings. Manifest: 7890 bytes /
   `5861569529394C8B04BD7903B1BD07C420812AD63DC1C669F7CA4E11E40E0154`.

5. Production package:

   `python -B kb_creator/scripts/build_innsmouth_production_package.py --verify --target D:\NRI\_scenario_contract_lf_probe_20260830_d\kb_creator\inputs\innsmouth\production`

   Exit `0`; `INNSMOUTH_PRODUCTION_PACKAGE_VERIFY_OK`; 70 files, 33
   assets; inventory
   `9A44C69454F243C8717C0A7B41FC34F99A8ABFE440653311090FDB1A084C5E71`;
   stable output hashes matched EN/RU/HTML/PDF. Manifest: 14435 bytes /
   `40DEB53603F1D4E14769C236663015B125C88EFA62F6F57CC61FBFC6FDBDF103`.

## ScenarioContract, schema, source resolution, and full-suite baseline

Focused command:

`python -B -m pytest kb_creator/tests/test_scenario_contract.py -q -p no:cacheprovider`

- exit `0`; `119 passed in 0.18s`.

Collect-only command:

`python -B -m pytest kb_creator/tests/test_scenario_contract.py --collect-only -q -p no:cacheprovider`

- exit `0`; `119 tests collected in 0.05s`.

Targeted command with `-k "source_resolution or shadow_rejection"`:

- exit `0`; `10 passed, 109 deselected in 0.08s`;
- includes positive resolution, all negative observation cases, and rejection
  of the shadow before filesystem access.

Direct evidence:

- schema JSON parse: `OK`;
- draft: `https://json-schema.org/draft/2020-12/schema`;
- Viral raw/frozen canonical SHA-256:
  `C2EF2DD143E304F59C8973E8DB82CF83B094BC35DDA37BB2299686E1FE6DA194`
  / same; equality `true`; canonical bytes `4067`;
- Innsmouth raw/frozen canonical SHA-256:
  `46D10BE6B4D639AAE0C28CDF510E7CB96B3DB66CE1FB98190E2FCB95532B523E`
  / same; equality `true`; canonical bytes `2490`;
- shadow `intake`: rejected;
- shadow `reconstruction_ready`: rejected;
- shadow source resolution: rejected before filesystem access.

Full-suite diagnostic:

`python -B -m pytest kb_creator/tests -q -p no:cacheprovider`

- pytest exit `2`;
- interrupted during collection with exactly `15 errors in 1.14s`;
- missing families: `kb_creator.pdf_raw.page_proof`,
  `kb_creator.pdf_raw.errors`, and
  `kb_creator.pdf_raw.raw_authority_projection`;
- comparison: exact known count and module-family baseline; no new class;
- disposition: full suite is not green and is not reported green.

No `pdf_raw` module, test, or script was created or modified.

## Six material identities and P2 scans

Before and final pre-receipt identities matched exactly:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `.gitattributes` | 622 | `943503F18B58DF37D7E33A29C44A1364A86D6B187978D2964A303B2B4A5D9F9D` |
| `kb_creator/contracts/scenario_contract.v1.schema.json` | 13426 | `25BF02364D4CE16E7D7DA96BD3E6B41D0E36B3642224F0989589B2335C5C07F2` |
| `kb_creator/contracts/innsmouth.json` | 3137 | `56E3B89B474CC466EBF6C84B8797E3D9AC56E34AD2B2294235415A073C98AD60` |
| `kb_creator/contracts/viral.json` | 4582 | `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D` |
| `kb_creator/scripts/scenario_contract.py` | 23157 | `51DFFCF62D0DFD41716FCD0B1330E9C6FF82A3A81A0578FB57B49BC34708C6F3` |
| `kb_creator/tests/test_scenario_contract.py` | 18252 | `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3` |

- scoped `(build|freeze)_viral_.*\.py` scan: `rg` exit `1`, no match;
- scoped `translator[\\/]config[\\/]viral\.package\.json|viral\.package\.json`
  scan: `rg` exit `1`, no match;
- `git diff --check`: exit `0`; only the existing CRLF checkout warning for
  `.gitattributes`, no whitespace error;
- `git diff --name-only`: only `.gitattributes`; ignored/untracked material
  paths were verified by direct hashes above.

## LF, blob, and raw-byte evidence

For both:

- `kb_creator/inputs/innsmouth/html/accepted_20260830_r6/The_Innsmouth_Terror_RU.html`;
- `kb_creator/inputs/innsmouth/production/The_Innsmouth_Terror_RU.html`;

the final probe reports:

- `git check-attr`: `text: set`, `eol: lf`;
- `git ls-files --eol`: `i/lf w/lf attr/text eol=lf`;
- index blob: `327c4f2a2d30468f8895213b295324e2457af67b`;
- `git hash-object --no-filters`: same blob;
- raw bytes: `226114`;
- raw SHA-256:
  `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`.

## Before/after state and mutation audit

Status hashes below are SHA-256 over UTF-8 porcelain-v1 `-uall` lines joined
with LF and no final newline, using the same method before and after.

### Active Viral worktree

- pre-QA: HEAD `54607bd3b9362adbb0c4bca64e8751482797f380`, 16 status
  lines, status hash
  `A11201BFC38C1705A73417D5739A063741FE79B9CE879CCF87E8C6815F8471C3`;
- final pre-receipt: identical HEAD, line count, and status hash;
- targeted `kb_creator/inputs/innsmouth` status: empty;
- index: 12860 entries, before/final hash
  `01503B9F49A1EE1CD7B6E905837E78D3DEE96F7A22A5CB0890C6291421FC4C68`;
- all six material hashes unchanged as listed above;
- expected post-write delta: only this new untracked immutable receipt.

### Original Innsmouth worktree

- pre-QA: HEAD `54607bd3b9362adbb0c4bca64e8751482797f380`, 418
  status lines, status hash
  `8E08EB4E8FF63E322AD4DAED33A07B894EB839018B53A8053CC64545C70A4BEB`;
- final: identical HEAD, line count, and status hash;
- ignored MASTER_RU source remained 195422 bytes /
  `BAF53B8E20AA91D3124AE83C7D3A533F4D9D16B9F104AB47B93995B048C81FC9`.

No original-worktree byte or Git state changed.

### Disposable probe

- pre-translator retained state: no valid HEAD; 1095 status lines;
- after exact translator materialization: 1288 status lines, status hash
  `78CEBCD35D676A8AF9BF4FF2C076A8AAF2ADE9DEC5BC015069C693951A195890`;
- temporary test-output peak: 1302 lines, explained exactly by 14 files;
- final after bounded cleanup: 1288 lines and the same
  `78CEBCD35D676A8AF9BF4FF2C076A8AAF2ADE9DEC5BC015069C693951A195890`;
- retained additions: prior 34 fixtures plus exact 193-file translator tree;
- translator final audit: expected 193, actual 193, blob mismatches 0;
- probe index/history was not changed; the probe still has no valid HEAD,
  commit, or remote operation.

## Blockers, forbidden work, and next action

No new blocker was found for bounded Step 5 QA acceptance. The known 15-error
missing-`pdf_raw` repository baseline remains a separate blocker to a
repository-wide green claim and was not modified or concealed. This receipt is
not a release decision.

Forbidden work not performed:

- no dependency installation or `PYTHONPATH` modification;
- no `pdf_raw` module creation;
- no test/script/contract/material edit;
- no Viral source processing, reconstruction, OCR, translation, render,
  build, freeze, accepted promotion, or publication;
- no historical translation copy;
- no accepted/production/source mutation;
- no plan/context/status/release edit;
- no Git add/index/history mutation, commit, push, or remote operation.

Recommended next action: main-chat orchestration verifies this receipt and its
detached SHA-256, captures the bounded QA pass, archives this completed
UI-visible QA retry task, and dispatches the fresh independent implementation
review required by the current plan. Source reconstruction remains blocked
until Step 5 integration and independent review are accepted.
