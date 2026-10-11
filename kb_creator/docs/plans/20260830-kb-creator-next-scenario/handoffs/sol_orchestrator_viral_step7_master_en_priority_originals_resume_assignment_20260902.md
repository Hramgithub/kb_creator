# Viral Step 7 MASTER_EN priority-original visual-QA resume assignment

- Role: Luna/high bounded QA continuation.
- Scope: inspect only the 39 priority-original byte streams whose candidate
  paths were inaccessible in the first pass.
- Do not repeat the already completed 27 contact sheets or p80 inspection.

## Accepted preceding evidence

- First QA assignment SHA-256:
  `160C18B7E3BE63A0E33EC65E8C541A90017147B4B4DF032EC6155F456D68058D`
- First BLOCKED receipt SHA-256:
  `020F6AEB1CF9205125DF0D9E1C8B864DB7AA65E59074A2A4DD013230F9D9CF20`
- That receipt directly inspected 27/27 contact sheets and p80, found no open
  P0-P2 defect, visually confirmed `Hey Marco Babez`, and left only 39/39
  priority originals uninspected because candidate paths returned `os error 5`.
- Transport remediation receipt SHA-256:
  `E46884EDDF689AF6C8E0471FBF7A1E39CAF3444ECFCD6CDCC978E65265CA83F7`
- Current generator/test SHA-256:
  `801450DAC2B41A89607DC52786E3AC06D24231640E2066561961770260F162D0` /
  `A334BE7C35DD609F6D302848B8F4C46D7260ED8399C66EAECFC52C2265075574`
- V3 bundle root:
  `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-master-en-visual-qa-bundle-20260902-v3`
- V3 manifest SHA-256:
  `9F6875D66823D10777702C8CEBD30D7BBDB5FA71AD98B3B65000A7AAA5C08614`
- V3 contains exactly 39 files beneath `priority_originals/`; every file was
  independently proven byte/hash-identical to its recorded candidate asset.
- Orchestrator successfully opened the transported p1 file with
  `view_image(detail=original)` before this assignment.

Frozen candidate identities remain:

- `INVENTORY.json` SHA-256:
  `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8`
- `MASTER_EN.md` SHA-256:
  `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`

## Allowed write

Write exactly one new receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step7_master_en_priority_originals_resume_20260902.md`

Everything else is read-only. Do not modify the first BLOCKED receipt, candidate,
v2/v3 bundles, source/config/code/tests, plan/context, Git or release surfaces.

## Preflight

1. Match the preceding receipt, remediation receipt, generator, tests, v3
   manifest and candidate hashes above.
2. Require manifest counts `123/107/91/107/27/39/0`, exactly 39
   `priority_assets` rows and exactly 39 files under `priority_originals/`.
3. For every row, require `transported_identity.bytes/sha256` to equal
   `identity.bytes/sha256`, the transported path to resolve beneath v3, and the
   file's recomputed bytes/SHA-256/dimensions to match the row.
4. Fail BLOCKED before inspection if any identity or closure check fails.

## Direct inspection: exactly 39 images

Open each manifest-listed `priority_assets[].transported_path` with
`view_image(detail=original)`. These are byte-identical originals, not resized
tiles or proxies. For each row record asset id, source page, semantic role,
transported path and a concrete visual observation.

Check semantic completeness, orientation, crop, legibility and obvious source
mismatch for every cover, full-page, map and handout asset. Explicitly inspect:

- p1 `viral-render-cover-front` as the complete front cover;
- p124 `viral-render-cover-back` as the complete clean back cover;
- all remaining 37 priority originals.

Successful opening is not a visual verdict. Do not fix any finding.

## Receipt and combined verdict

The receipt must contain a 39-row inspection table, explicit p1/p124 findings,
all defects with severity, pre/post candidate hashes and one verdict:

- `PASS_FULL_VISUAL_QA_RESUMED` only if all 39/39 transported originals were
  directly inspected with no open P0, P1 or P2 defect, and the prior receipt's
  27/27 sheet plus p80 evidence remains identity-valid;
- `FAIL_FULL_VISUAL_QA` for a visual P0-P2 defect;
- `BLOCKED` for incomplete access or identity/coverage failure.

When passing, state clearly that the two receipts together close full visual QA;
they do not constitute GPT-5.5 release review, user reading acceptance or a
candidate acceptance sidecar.

## Forbidden execution

- No MinerU, build, verification script, pytest or mutation matrix.
- No new render/copy/proxy/screenshot/log artifact.
- No candidate, bundle, code/config/test, plan/context or prior-receipt edit.
- No acceptance, promotion, commit, stage, push, deletion or cleanup.
