# Terra evidence-only completion: Viral Step 6A QAV-D2

The QAV-D2 material implementation is frozen at the post-write identities below.
The first immutable receipt remains historical and unedited, but is not yet
integration-sufficient because several evidence fields required by its dispatch
are summarized rather than embedded. This completion task closes only that
engineering evidence gap. It does not authorize Luna to construct evidence.

## Frozen authority and material

- D2 amended dispatch:
  `DD7480844A3B3E7BA889485CB042D838DF9E596D6B0729EBE2FB1901AA18DB4F`.
- INV/QAV amendment / ACCEPT review:
  `779B641EBD2DC55F3A4725AA0345D5286CB41CE608A4465B8B5AE43DC9156606` /
  `12007AAFBA3838FE76EF0FFD54BBF2C4253197D08DFF41F8A63C4FD32A5A04EB`.
- Frozen library:
  `34943D5E0008A01A1F3AFC3AF2D49091F06049187AE9D0CB7DA02654663862D4`.
- Frozen focused tests:
  `D3FA871BBA3DED04ECD216544B7A9A7EEECB95D4769DDF45612B412990F9D192`.
- First D2 receipt:
  `96D6ACD0E6BA04C6DF87904AC09B259CB33187EE1ECE456901380C3A1E609509`.
- Reported four-row canonical stream: 534 UTF-8/LF bytes, SHA-256
  `2F58364620D69FBFC6EC19A43C3877E81FAAC9123D027EF945D8BDA813DC6EA0`.

Before any execution, confirm all identities above and that the completion
receipt below is absent. Material files and the first receipt are read-only.

## Sole write and forbidden scope

The only allowed write is absent-before:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_d2_audit_completion_20260901.md`

Do not modify code, tests, fixtures, candidate, source, plan, context, status,
prior receipts, governance, cache, Git, protected tests, or live state. Do not
clean any pre-existing residue. Run with `python -B` and pytest cache disabled;
prove that no new attributable residue appears.

## Required completion evidence

Rerun and report the three node groups separately, exactly as defined by the
accepted amendment section 10:

1. QAV-D2: four nodes = the three QAV-side INV aliases plus the independent
   `QAV-inventory-rule-wrong`; required `4 passed`.
2. INV-side aliases: three nodes; required `3 passed`.
3. SCH/QAV shape aliases: four nodes; required `4 passed`.

Their set union is exactly all ten members of the five alias pairs plus the one
independent rule node: eleven unique nodes. Do not compress this as an
ambiguous `8 passed` statement. Also rerun representative `3 passed`, BLD
`3 passed`, exact collection `371 tests collected`, and the retired-code search
with no `E_QA_INVENTORY_(ARRAY|COUNT|DIGEST)` match.

The completion receipt must embed, not merely assert:

- all four complete 16-field D2 audit objects in registry order;
- the exact four canonical six-field audit rows, byte length, and SHA-256;
- a separate five-row alias-pair table naming all ten members and recording
  non-secret within-process callable ordinals for both sides, with distinct
  identities proved for all ten;
- exact commands, native exit codes, and SHA-256 of captured stdout/stderr for
  each QAV-D2, INV-alias, shape-alias, representative, BLD, collect, and
  retired-code run;
- registry proof for INV `18`, QAV `90`, negatives `368`, unique ids `368`,
  unique callable objects `368`, focused `371`, and exactly five declared
  alias pairs;
- exact library/test/first-receipt pre/post hashes;
- exact pre/post inventory and SHA-256 for every existing `.pyc` plus the
  pre-existing root `.pytest_cache` state, showing equality and zero new
  attributable residue;
- exact sole changed path, elapsed time, and token use or `unavailable`.

All evidence must be derived by Terra from the frozen implementation and
prepared test/audit helpers. If the canonical audit stream differs from 534
bytes or the reported digest, or any other invariant fails, write a truthful
BLOCKED completion receipt and stop. No failure authorizes material repair,
cleanup, scope widening, live/protected execution, or delegation to Luna.

This evidence-only completion does not constitute independent QA, critic
acceptance, semantic acceptance, release, promotion, publication, commit, or
push.
