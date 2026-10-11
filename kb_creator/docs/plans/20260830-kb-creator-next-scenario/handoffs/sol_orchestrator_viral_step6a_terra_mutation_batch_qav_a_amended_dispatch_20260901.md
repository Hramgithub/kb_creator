# Amended Terra dispatch: Viral Step 6A QAV-A

This dispatch binds the accepted SCH/QAV taxonomy amendment and supersedes only
the expected-code literals in the held pre-write QAV-A assignment. All other
scope, mutation, audit, count, cache, live, protected, and Git constraints stay
binding.

## Admission authority

- Parent packet: `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`.
- Taxonomy amendment: `0A692CD1A8F3067E551ACFB1581840BF9748FD2C308C6BBE79FD4B174FC75D2A`.
- Fresh independent GPT-5.5/high ACCEPT review:
  `102383E2CD10EFE91DFBAD13A905DDCFB63DFE8ADF6BCC9B1D7937E40ADAA5DB`;
  findings P0/P1/P2: none.
- Held original QAV-A assignment:
  `5582B039B2B8D8E88B92821D1AAAF537AEBBDEA6CE5D6CD8EFF191BC06908144`.
- Library baseline:
  `2309CD5015B89908A5B751916F46B4C601AFB8E121EB338FC6450B7BAAE49FAC`.
- Test baseline:
  `7B9AEC1EF0BA2870E2021544912538FE3234DAF92D0E38E34F16285118649DCF`.
- QAV-A implementation receipt is absent before dispatch.

## Binding amended matrix

Keep the 25 descriptive QAV-A case ids and physical selectors from the original
assignment. Expected codes are now:

- every one of the 23 `QAV-top-<field>-missing` cases:
  `E_SHAPE_QA` at canonical phase 5;
- `QAV-top-extra`: `E_SHAPE_QA` at canonical phase 5;
- `QAV-state-promoted`: `E_QA_STATE` at canonical phase 9 after the valid
  document passes phase-5 root shape and earlier QA semantic checks.

Exactly two cross-family aliases are allowed and no others:

- `SCH-QA-required-top-member-missing` and
  `QAV-top-asset_count-missing` share physical selector `#/asset_count`;
- `SCH-qa-unexpected-top-member` and `QAV-top-extra` share physical selector
  `#/unexpected`.

Each alias remains a separately named callable object, pytest node, fixture run,
16-field audit row and exact-code assertion. Both feed the same production
shape branch and return `E_SHAPE_QA`; case id or family is never passed to the
verifier. Rerun both SCH alias nodes on the current post-CMD baseline alongside
all 25 QAV-A nodes. Existing SCH evidence remains historical and valid.

Counts remain exact: SCH 33, QAV 90, negative 368, BLD 3, focused 371. Literal
reseal for all 25 QAV-A root-QA mutations is `()`.

## Write scope and completion

Terra may modify only the shared verifier file, focused test file, and create
the absent `terra_engineering_viral_step6a_mutation_batch_qav_a_20260901.md`.
No other write, cleanup, live command, protected test, Git mutation, QAV-B/C/D,
REG, release or acceptance claim is authorized.

Completion requires 25/25 full executable audit objects and canonical digest,
the two current-baseline SCH alias reruns, representative CMD/clean path, BLD 3,
collect 371, unchanged pre-existing cache identities, zero new residue, exact
material pre/post hashes, and a complete immutable receipt. Luna has no role in
implementation or evidence construction.
