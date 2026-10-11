# Viral Step 7 — suppression edit-plan remediation resume

## Frozen checkpoint

- Config: 713722 bytes / SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Builder: `BD0830EEE6BBFCEB2B994F7F3614CD4DA019E53B6C4FE7C4632B2E7027C13C22`.
- Verifier: `45371835F45605CDFEF19B2ED136A1415467DAE6627CA4516D7B98D7DE528F59`.
- Builder tests: `E33A39DA0F9C53DD38A4EB89289717E6C9D3A99422CB704BC060F86589C5F259`.
- Verifier tests: `57B2B70193589C767FCEF9DD4F4CD6823E876CE978637E6BDFB84D1E38567D45`.
- Main-chat focused baseline: 54 passed; `py_compile` and scoped diff-check
  passed; Candidate C absent.
- Prior remediation receipt/checkpoints remain historical at SHA-256
  `4CEA557922C7ADA1033D99B57EBE91484112DF49D7515862DEF9FFE8F342DA96`.

The current code already contains verifier-local closed reader-surface parsing,
candidate semantic/suppression/alt evidence, recursive input identities and
exception-path staging cleanup. Preserve and test those changes.

## Ownership

Terra/medium may modify only builder, verifier, their two focused tests and one
new receipt named
`terra_engineering_viral_step7_suppression_edit_plan_resume_20260902.md`.
Config/source/accepted v4/candidates/prior receipts/plan/context/Git/downstream
and four existing dot-staging roots are read-only.

## Remaining implementation

Implement one deterministic source-span edit plan over original LF-normalized
coordinates:

1. Resolve source xrefs against their unique normal claim spans.
2. Resolve suppressions against `source_containment.claim_owner_anchor`, proving
   the declared normal or owned-page containment chain.
3. Keep semantic `owner_anchor` solely for replacement asset validation.
4. Reject overlap or ambiguous edits. Apply non-overlapping xref replacements
   and suppression deletions in reverse original-offset order so neither shifts
   the other's coordinates.
5. Count xrefs only when emitted; preserve exactly 237 links. Prove all 22
   suppressions applied once, reader occurrence zero and replacement occurrence
   one; specifically remove all four cross-owner technical descriptions.
6. Feed the exact same resolved ledger into structured/note transforms,
   candidate evidence and conservation.
7. Derive conservation metrics: 22 authorized rows, exact UTF-8 suppressed
   bytes, 17 normal, 5 owned-page, 4 cross-owner, zero generated/unproven,
   zero unauthorized. Verifier independently recomputes and compares them.
8. Keep the verifier independent; do not import builder internals or trust
   candidate assertions.

Add compact regressions for the lost-link case, the four cross-owner rows,
same-owner/owned-page positives, overlap/outside/broken-proof/generated failures,
evidence tampering and derived conservation values. Do not create a generated
mutation matrix.

Run only the two focused modules, `py_compile` and scoped `git diff --check`.
Return `PASS_EDIT_PLAN_REMEDIATION` only when all critic findings and this resume
are proven. No candidate or scratch build is authorized; a second independent
GPT-5.5/high implementation review follows.
