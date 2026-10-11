# Critic receipt: Dissociation compact block-boundary replay10 QA

Timestamp: 2026-09-15T13:58:27+03:00

Review kind: implementation

Reviewer role: independent critic / bounded QA. I did not implement or materially design the candidate.

Orchestrator policy owner: main-chat orchestrator remains owner under `docs/governance/nri_goal_governance.md`; this receipt does not transfer orchestration ownership.

Assignment state: independent critic `gpt-5.5` / medium requested by task packet; actual platform identity unavailable, so assignment is platform-unverified.

Scoped override: none beyond the task packet. No implementation, run, acceptance, promotion, publication, source, plan/status, or config edits. No MinerU, CPU/GPU, network, commit, or push.

## Verdict

GO for explicit user acceptance of replay10 as the corrected reconstruction candidate.

No P0/P1/P2 findings.

This is not a release review and does not record acceptance.

## Scope checked

- Fresh candidate run: `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-10`
- Accepted baseline: `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-09`
- Engineer receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_compact_block_boundary_20260915.md`
- Implementation/tests, read-only:
  - `kb_creator/scripts/materialize_mineru_ai_merge.py`
  - `kb_creator/pipeline/reconstruction_promotion.py`
  - `kb_creator/tests/test_materialize_mineru_ai_merge.py`
  - `kb_creator/tests/test_reconstruction_promotion.py`
- Visual evidence: `outputs/04-visual-merge-bundle/visual/triptychs/page-006.png`

## Evidence

Run state and identity:

- `run.json`: 32207 bytes, SHA256 `A630DC354F96510031E545FF85B69FB8335553DB0E3A255276747743FBB4DF5B`
- run schema `kb_creator.run_spec.v2`
- replay10 portable identity `1C21F471B2B1092090963DD4DDA692884BC408C54219D6A1D169C1D9940279B2`
- `result.json`: 304 bytes, SHA256 `D91C75968B463DAE672660F746ACAE198C4E10B36C110A9439C7169CC56B64FC`
- result state `needs_review`, exit code `10`, acceptance_inferred `false`
- replay bridge SHA256 `1B05FC406A92B62E8BD5D9EF43C717136573ADAD1D56805A0A4EA37157D87756`

Replay/stage authority:

- `validate_replayed_prefix(run10)` passed read-only.
- `_validate_downstream_stage` passed for Stage05 and Stage06.
- Stage05 manifest file SHA256 `15B487D376B48C1914016E4A266BB1BECAD3FBD912573411345E8CFA7F6A173A`
  - sealed `manifest_sha256`: `83B026302F281C7AC4193D1358F9196BC2DC0175BF9D1D101968029448E36B6B`
  - output inventory SHA256 `9FDA0AD7F5B1DEFAAAB6C10F34E4C197BCD1F55C57C1D85212B12C07DD4E3E99`
- Stage06 manifest file SHA256 `302B06925D259E276FD4DC648C47D2EE566E0E3B7DC2463292DA164DDC9E4CDC`
  - sealed `manifest_sha256`: `6444AB78954C99090D64337FB461C75A68C79E7640A6463B0B895836155E6DE8`
  - output inventory SHA256 `6B738103ACEC43BF55A0FB44FEF7AF0AC1B7EEC9537134E04A0A0284BC452CA1`

Fidelity audit:

- `outputs/05-fidelity-audit/audit.json`: 531844 bytes, SHA256 `4DB336EF71F7F4E79DFACB0DF4A08C584399CA4D10567F6C23A926EFEB530084`
- schema `kb_creator.ai-merge-fidelity-audit/v3`
- passed `true`
- errors `[]`
- pages `1..6`
- completeness values `{1.0}`

Candidate comparison against accepted run09:

- run09 `RECONSTRUCTED_EN.md`: 21048 bytes, SHA256 `2C8983B83C770AC60AA32993B84228E64983B46010121A9DBA393BD3107C646D`
- run10 `RECONSTRUCTED_EN.md`: 21046 bytes, SHA256 `53B560862C3CC344C5C78676D988C3A4A479B5C0A0CBE4261B2E93080ED19993`
- Exact intended delta verified: the only text delta is removal of one empty separator line between:
  - `## HUMAN RESISTANCE (Police, Test Subjects, Residents of Aniak)`
  - `STR 50 CON 55 SIZ 50 INT 85 POW 60  `
- Unified diff reduced to:

```diff
 ## HUMAN RESISTANCE (Police, Test Subjects, Residents of Aniak)
-
 STR 50 CON 55 SIZ 50 INT 85 POW 60  
```

- Whitespace-normalized literal text/order equality with run09: true.
- Source page markers: `001`, `002`, `003`, `004`, `005`, `006`
- Headings: 21
- Pages 1-5 are byte-identical to run09:
  - page-001 SHA `71F2B69A6F4DBD30086B11096E735CB527CBC5CB76A2EE39146EFD11FC189329`
  - page-002 SHA `1594BF2BA2E1122E2E3B99E51AC15E72EA7D23637454ADC30DCC0135C8F8A84E`
  - page-003 SHA `531214200254F9AC0B71925880DA40767F9FCCA38D71E7C7AFDBBE5173F4C9BA`
  - page-004 SHA `AEC964F2EEBF3150FF3235E6C9B370B37CA52F3D06D83751E28272589CE7ABC8`
  - page-005 SHA `578252D5216F12EDB30EBAAE99223D33E2C45FCE93BC3EC3796B2C600BBD06E3`
- Assets are byte-identical to run09:
  - `e30a388dc2a17e216a53a2a673ea583c3b71be6567fe97f9e35805de71e760ac.jpg`: 257805 bytes, SHA256 `E30A388DC2A17E216A53A2A673EA583C3B71BE6567FE97F9E35805DE71E760AC`
  - `f96ad0f20513f4737474915670fe2a1f361bf60c12fd6ae0f210cf2132127de4.jpg`: 236058 bytes, SHA256 `F96AD0F20513F4737474915670FE2A1F361BF60C12FD6AE0F210CF2132127DE4`

HUMAN RESISTANCE statblock:

- run10 heading line: 173
- Nonblank statblock rows: 11
- CommonMark hard-break rows: 10
- No blank paragraph separator between the H2 and first STR row.
- No blank paragraph inside the nonblank statblock row sequence.
- The first 10 of 11 statblock rows retain trailing double-space hard breaks; final `Spells: none.` remains without hard break.
- Visual page-006 triptych was inspected manually; it supports compact statblock rendering with no visible paragraph gap between the `HUMAN RESISTANCE` heading and stat rows.

Decision/submission evidence:

- replay10 review page-006 decision: 4672 bytes, SHA256 `39600DC220748C0E9C394D3011FC30D822D7E507F57920705BFDA669919FC231`
- materialized page-006 decision copy: 4672 bytes, SHA256 `39600DC220748C0E9C394D3011FC30D822D7E507F57920705BFDA669919FC231`
- Decision keys are the expected optional-extension shape: legacy decision keys plus `block_boundaries`.
- `block_boundaries` is exactly:

```json
[
  {
    "style": "compact",
    "heading_line": "## HUMAN RESISTANCE (Police, Test Subjects, Residents of Aniak)",
    "first_body_line": "STR 50 CON 55 SIZ 50 INT 85 POW 60  "
  }
]
```

- `review/validated-submission-v2/submission_inventory.json`: 3629 bytes, SHA256 `5C434A35FB529DEE54ADC108FF52030F731003D246F95D7F06DD16294F493DAD`
- Submission inventory binds the page-006 decision SHA above.

Implementation/test identities observed:

- `kb_creator/scripts/materialize_mineru_ai_merge.py`: 43215 bytes, SHA256 `B0BEBB66CF1AA83E81429C4820EFC1B1AB5ADC144AB7B1201F4D3CF66A639E3F`
- `kb_creator/pipeline/reconstruction_promotion.py`: 91604 bytes, SHA256 `F10CF250B7FA92A652ECA4BF0D6E6DD620E191596368301C1DC71D3B5847811B`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`: 18308 bytes, SHA256 `5A852975BD4E9EFEB422C8BFE78DDC032AA58FBAA5A2612BD4EA8C8E7B78E35E`
- `kb_creator/tests/test_reconstruction_promotion.py`: 29185 bytes, SHA256 `F22E5ACB8776CAA80E248103799DC6C37F83065895D09EF0B23F793ADE0DC6FD`

## Commands / tests

Read-only inspection and verification:

```powershell
Get-ChildItem -LiteralPath 'kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-10' -Force
Get-ChildItem -LiteralPath 'kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-10' -Recurse -File
Select-String -LiteralPath 'kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-10/outputs/06-materialize-candidate/RECONSTRUCTED_EN.md' -Pattern '<!--'
```

Python probes:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -c '<read-only run09/run10 SHA, exact diff, page/assets/statblock, decision/submission probe>'
& '.tools/MinerU/.venv/Scripts/python.exe' -B -c '<validate_replayed_prefix + _validate_downstream_stage probe>'
& '.tools/MinerU/.venv/Scripts/python.exe' -B -c '<audit completeness and marker probe>'
```

Focused tests:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m py_compile kb_creator/scripts/materialize_mineru_ai_merge.py kb_creator/pipeline/reconstruction_promotion.py kb_creator/tests/test_materialize_mineru_ai_merge.py kb_creator/tests/test_reconstruction_promotion.py
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q kb_creator/tests/test_materialize_mineru_ai_merge.py
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q -rs kb_creator/tests/test_reconstruction_promotion.py -k "legacy or compact or unknown or decision_authority_invalid"
```

Results:

- `py_compile`: pass
- `test_materialize_mineru_ai_merge.py`: `43 passed`
- focused promotion selector: `1 passed, 19 deselected`

Working-tree note:

- The implementation/test paths under review were already modified/untracked relative to Git during this QA (`materialize_mineru_ai_merge.py`, `test_materialize_mineru_ai_merge.py`, `reconstruction_promotion.py`, `test_reconstruction_promotion.py`). This QA did not alter them.

## Findings

P0: none.

P1: none.

P2: none.

The engineer-reported P2 about old live-run-dependent promotion fixtures remains an implementation-suite maintenance note, but it did not reproduce as a blocker for the self-contained compact-boundary and promotion-extension coverage used here.

## Blockers

None.

## Recommendation

Accept replay10 as the corrected reconstruction candidate after explicit user approval. The candidate is not accepted by this receipt. Promotion, publication, and release review remain separate gated stages.

Elapsed time: approx. 25 minutes active reviewer time.

Token use: exact platform token accounting unavailable inside this receipt.
