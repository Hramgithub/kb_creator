# U6 API independent recheck — immutable receipt v04

- Goal/step: `20261004-user-docx-review`, finite U6 v04 implementation recheck.
- Review kind: `implementation`, not full-goal release. I did not implement
  or materially design the candidate/remediation. No implementation edits.
- Recommendation: `changes_required`. F1/F2/F3/F4/F5 CLOSED; F6 REOPENED P1:
  visible13 split adjacent Word runs permits selected3→15 yielding115 or
  selected1→5 yielding53. Same-leaf cases now reject. No demonstrated impact
  in the three actual candidates; no P0 finding.
- Evidence, exact input paths, locator and commands: [report-v04](../audit/critic-u6-recheck-v04/report-v04.md),
  [recheck_v04.py](../audit/critic-u6-recheck-v04/recheck_v04.py),
  `numeric-v04.json` plus `inputs-v02/adjacent_run_suffix/` and
  `inputs-v02/adjacent_run_prefix/` in that audit root. All inputs resealed.
- Checks:22/22 focused tests pass after authorized access-denial retry;
  10 previous probes,6 numeric boundary cases,6 EDU/CHR controls,2 drift
  probes and valid exterior-expression control. Exact structural restoration,
  197 operations plus expression,146 numeric source-QA records and all367 QA
  page hashes reverified. Existing visual-QA receipts and v05/v06 errata
  consumed; no claim of personally re-viewing367 pages or repaired API
  authoring historical candidates.
- API frozen `E09BC25ABE733B8D60E6CE8C3EBBD6F0A15482EF7CDA3A8AF6E95AA1526190EA`.
  Seven-file start/end manifest is in report. Candidate hashes remain Fear
  `D79AB0EC131D2C6926D868EB037786093F615AEAF122895AA4487254616CF33E`, Len
  `CC3A1F96D82121C07938D860EF88186AA33A32199B578D4C7C2DE05F4C83AD23`, Kremlin
  `5573888152F7EDAB32D483E4D652FD465694BFBF1764CC708C3EF7C042AA87D8`.
- Files checked: task/engineer v04 and critic v03 receipts/probes; frozen API,
  CLI, helpers, focused tests and docs; real candidate/original packages,
  manifests/reports/authorities and source-QA; all367 PNG identities and QA
  ledgers/indexes; Fear v04/v05/v06 and two-book v05 receipts; main scope
  clarification. Details and exact hashes in report and evidence-v04.json.
- Files changed: new harness, report, JSON results and synthetic fixture
  inputs only under `audit/critic-u6-recheck-v04/`, plus this new receipt.
  No code, book, source, older probe/receipt, canonical plan/context/status,
  release file, HTML/PDF or producer lineage edits. Sandbox-denied temporary
  remnants remain audit-local, outside commit scope.
- Scope: candidate conservation evidence remains usable; field-only art
  preservation is main's bounded implementation choice. No Leningrad/Kremlin
  source-art completeness or full7e reconstruction certification. U8 normal
  source/edition guards remain active/excluded; upstream194 output-policy
  tests are not reviewed as a final release gate here.
- Blocker/next action: finite F6 remediation then new frozen independent
  recheck; full release only after U8 closure/freeze. Any relevant code,
  dependency or candidate mutation requires a new receipt.
- Requested critic assignment: `gpt-6-astra` / `high`; platform identity and
  effort unavailable, assignment state `platform-unverified`, bounded review
  COMPLETE. Policy owner/orchestrator remains main `/root`, `gpt-6-sol` /
  `medium`; no orchestration transfer. Scoped role override: none.
- Start `2026-10-04T22:04:48.6347174Z`; receipt timestamp `2026-10-04T22:09:00Z`
  (minute-resolution drafting timestamp). Elapsed approximately4 minutes;
  exact platform elapsed/token accounting unavailable. Token use: unavailable.
