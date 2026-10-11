# Viral Step 7 MASTER_EN Phase C1 binding-executor assignment

## Role and scope

- Owner: `gpt-5.6-terra` engineering, `medium`, accelerated service when exposed.
- Orchestration remains with `/root`.
- Write only:
  - `kb_creator/scripts/build_scenario_master_en.py`;
  - `kb_creator/tests/test_build_scenario_master_en.py`;
  - new immutable receipt `handoffs/terra_engineering_viral_step7_master_en_binding_executor_20260901.md`.
- The verifier and its tests, config, source/reconstruction, plan/context, candidate/output, governance and Git state are read-only. Other edits exist; do not revert or absorb them.

## Pinned inputs

- Amended config: 710,922 bytes, SHA-256 `C15934BB4EA7619505EE076D94BE56DA90C08F0B4DC0350A69A8C399EC7DBCAC`.
- Config receipt: 5,501 bytes, SHA-256 `616AD288097AD78130E6328F0E33BE03E8154C187FEDF1515CE071465F4688B7`.
- Binding architecture receipt: 16,826 bytes, SHA-256 `C3CE8DC4E61A75BBE4AC6A2A7ED92FBC8F5275FD8AD3C03758FB4B266B3F861D`.
- Accepted-v4 inventory: SHA-256 `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Phase B builder baseline: SHA-256 `DAD518523ADAC39365E0D368966C4C7D112EC3EF3B3344146706F431EE96DD2F`.
- Read both binding receipts completely before editing. They define the exact schema and span/conservation semantics.

## Required implementation

1. Extend the closed Phase A parser/preflight to require and validate the new `assembly_binding` on all 168 hierarchy rows: exact keys/enums, unique order `1..168`, parent-before-child, locator shapes, page membership, exact handout/visual `unit_ref`, continuation and shared-prefix closure. The real amended config must preflight successfully; the prior unbound hierarchy shape must fail closed.
2. Add a reusable read-only binding resolver. It reads the pinned accepted-v4 page files without mutation, recognizes source-page comments as technical provenance, resolves every declared locator by exact page/selector/occurrence rules, and never uses fuzzy or fallback matching.
3. Return a deterministic 168-row resolved binding index in assembly order. Each row must identify anchor/kind/source pages, exact source locator offsets or unit owner, continuation pages, action, source-span hashes and shared-prefix ownership. Generated rows consume no source span.
4. Derive non-overlapping source spans from start locators and the next locator on the same page/EOF. Preserve the remainder of `line_prefix` rows byte-for-byte; physical/owned units resolve through their existing config owners; p106->107 stays one unit.
5. Produce an in-memory conservation ledger proving every accepted-v4 lexical/asset block is owned exactly once or classified by an already authorized technical/evidence-only policy. Report zero unowned, duplicate and unauthorized-suppression blocks. Do not yet perform reader formatting, xref wrapping or semantic table rendering.
6. Preserve the accepted Phase B asset layer unchanged and keep normal CLI mode fail-closed with `implementation_phase_incomplete`. No real candidate or sidecar may be written in C1.

## Compact verification

Use representative invariant-class tests, not selector permutations. Target approximately 14-22 focused nodes total across the existing builder test module. Cover:

- real amended config preflight and 168-row/189-locator resolution;
- missing/unknown binding keys, bad kind/action/selector enum, duplicate/missing order, bad unit_ref;
- zero/multiple locator match and explicit refusal of fuzzy/page-start fallback;
- corrected page ownership examples p12/p14, p17/p18, p49/p52 and p60/p61;
- p42 prefix replacement retains remainder exactly;
- continuation p20-22 and p106-107;
- shared-prefix ownership p74/p75 and multi-unit p93/p100/p101;
- generated rows consume nothing;
- conservation ledger has zero unowned/duplicate/unauthorized suppression;
- no target/MASTER_EN/acceptance/sidecar output;
- retained 123-row deterministic asset tests and fail-closed normal CLI.

Run at minimum:

```powershell
python -m py_compile kb_creator/scripts/build_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py
python -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py
git diff --check -- kb_creator/scripts/build_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py
```

Do not run MinerU or the historical 371/119/490 suites.

## Receipt

Return `PASS_BINDING_EXECUTOR`, `FAIL`, or `BLOCKED`; changed hashes; exact test count/commands; 168/189 resolver counts; conservation totals/errors; representative page evidence; forbidden-output absence; remaining C2 work; elapsed time and token use if available. This result never authorizes a real candidate.
