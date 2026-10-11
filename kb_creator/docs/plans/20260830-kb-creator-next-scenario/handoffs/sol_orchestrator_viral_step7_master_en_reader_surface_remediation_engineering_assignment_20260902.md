# Viral Step 7 MASTER_EN reader-surface remediation engineering assignment

- Role: Terra/medium engineering.
- Authoritative specification:
  `sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md`
  at SHA-256
  `BD537483C7BB3C78076DC2A6F7FC8937BF4040261B74E58312D3CBC6FEFC901D`.
- Goal: implement the complete closed reader-surface contract, not only critic
  examples.
- This pass does not create or accept a durable successor candidate.

## Frozen inputs and rejected evidence

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Accepted reconstruction v4 inventory SHA-256:
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`
- Source PDF SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`
- Rejected candidate A `INVENTORY.json` / `MASTER_EN.md` SHA-256:
  `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8` /
  `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`
- Independent reject receipt SHA-256:
  `FBE15693C3CAD6FE5B5E7F01DF79E031C5B48180E563F24B63B585D1D5D42678`
- Current config/builder/verifier/builder-test/verifier-test SHA-256:
  `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3` /
  `82C720B572A73B33DF9D2548BB3FD4CB8BAE81660AE21D4273DEB984C99EDA1C` /
  `C151967D435A31DACF706D2938C5FC157C8E7E01E10E90C1211844C620B174E5` /
  `01BDFFFC6F32833E3EF5EF831A85F30775883C1E20B5E9B5B3C0687A58AD33DF` /
  `B7D6822A44B06A87457DBE6B37F9CE97CC60E33083B2387C04C665402771B04F`.

Candidate A/B and every accepted input remain immutable. The successor target
`kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-c`
must remain absent throughout this engineering pass.

## Allowed writes

1. `kb_creator/working/viral/master_en/publication_config_v1.json`
2. `kb_creator/scripts/build_scenario_master_en.py`
3. `kb_creator/scripts/verify_scenario_master_en.py`
4. `kb_creator/tests/test_build_scenario_master_en.py`
5. `kb_creator/tests/test_verify_scenario_master_en.py`
6. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_reader_surface_remediation_20260902.md`

No other durable write is allowed. Accepted reconstruction, source, candidates,
visual bundles, plan/context, architecture/review receipts, other scripts/tests,
Git and downstream outputs are read-only. Temporary test directories may be
created and cleaned through normal test/`TemporaryDirectory` lifecycle only.

## Required complete implementation

Implement every architecture row and invariant:

1. Repair all 25 semantic fragment ownership seams using existing locator
   machinery, including every xref/structure/note dependency named by the
   architecture receipt.
2. Apply all 34 exact asset-owner corrections, including the one evidence-only
   representation; do not infer movement solely from page number.
3. Add the closed top-level `reader_surface` schema and all 25 semantic fragment,
   22 exact suppression, heading-policy and alt-policy records. Validate unknown
   nested keys and invalid selector combinations fail closed.
4. Suppress exactly the 22 non-authorial technical ranges and retain their raw
   hashes/text/dispositions in sidecar evidence and conservation accounting.
5. Install the exact 107-row descriptive alt ledger. Reject empty, generic,
   provenance/tooling/path/hash/page forms defined by the architecture.
6. Replace global source-heading increment with owner-local normalization,
   preserving relative depth, deterministic strong-label overflow/duplicates,
   and sidecar evidence for original/emitted forms.
7. Extend candidate sidecars so builder and verifier independently prove all
   new semantic/suppression/heading/alt outcomes. The verifier must not import or
   execute builder implementation.
8. Preserve accepted reconstruction bytes, all source-visible semantic text
   exactly once except the 22 authorized ranges, public anchor/link targets,
   asset bytes and unrelated publication behavior.

Do not narrow the architecture's exhaustive counts to representative cases.

## Focused verification only

- Compile the two scripts without retained bytecode.
- Run only:
  `python -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py`
- Execute the architecture's read-only full-config/static-contract audit through
  production preflight or an equivalent existing in-memory path. It must prove:
  168 units, 25 semantic fragments, 22 suppressions, 107 alts, 34 corrected
  asset owners, zero semantic mismatch/noise/alt/hierarchy error and closed
  source conservation.
- Use temporary synthetic/full-reader artifacts only where tests already own
  cleanup. Do not build candidate C or any other durable candidate.
- Run scoped `git diff --check` on the five owned implementation files.
- Do not run MinerU, reconstruction, visual QA or historical 371/119/490.

## Receipt

Write the receipt only after all focused verification passes. Include:

- exact before/after hashes of all five implementation files;
- config counts and schema closure;
- test command/count/time and static full-contract results;
- exact evidence for all 25/22/107/34 and heading outcomes;
- proof A/B and accepted input hashes are unchanged and candidate C absent;
- any residual risk and exact next action: independent GPT-5.5/high
  implementation review before successor build.

Verdict is `PASS_READER_SURFACE_REMEDIATION` or `BLOCKED`; do not claim release,
user acceptance, candidate freeze or downstream readiness.
