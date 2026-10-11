# Terra engineering assignment: Viral Step 6A BLD and full integration

All 368 negative registry members now have real mutation implementations. This
final Terra engineering batch closes the remaining OwnedTempRoot/build/finalizer
gaps and writes the one canonical full-integration receipt required by the
accepted parent architecture. Luna is not assigned: Luna may only execute the
prepared downstream QA commands after this engineering artifact is frozen.

## Admission authority and frozen baseline

- Parent architecture / independent review:
  `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A` /
  `B45198A548309258D08DE3CFBD4B0FA18F65580CBD94192E03044507E688E279`.
- Accepted SCH/QAV amendment/review:
  `0A692CD1A8F3067E551ACFB1581840BF9748FD2C308C6BBE79FD4B174FC75D2A` /
  `102383E2CD10EFE91DFBAD13A905DDCFB63DFE8ADF6BCC9B1D7937E40ADAA5DB`.
- Accepted INV/QAV amendment/review:
  `779B641EBD2DC55F3A4725AA0345D5286CB41CE608A4465B8B5AE43DC9156606` /
  `12007AAFBA3838FE76EF0FFD54BBF2C4253197D08DFF41F8A63C4FD32A5A04EB`.
- Accepted REG amendment/review:
  `6E0C6280D7930D6994E461E32363C1FA15B0BBC39AFAE34CAF9EE8D84737341D` /
  `FEB2C162524A1776729CBF236CF7419B118C97889B125AE623B08E471956C52B`.
- Final QAV-D2 evidence:
  `32A714D453F4A895866267A8F47879DE554A53581E272A7908C3F92D695FC268`.
- REG implementation receipt:
  `AC7655C76BE4C57614248EACFE9F7AD192265EDA21414667F2D86FA65233C422`.
- Current library/test baseline:
  `34943D5E0008A01A1F3AFC3AF2D49091F06049187AE9D0CB7DA02654663862D4` /
  `FDFFAD49EF059C542F01A3E215E688B1A5DB9C7D16C88FAB73466546BAFCE6B9`.
- Existing declared 368-row stream is 51,005 UTF-8/LF bytes with SHA-256
  `8C5C2A0A69C212465D1429FA38B35A4802C9AFCDF52F9461A1747D5729671DD4`;
  recompute it after this batch rather than trusting it.
- Integration receipt is absent before dispatch.

Any authority/baseline/receipt-absence mismatch is a pre-write stop.

## Exact three-path ownership

Terra may modify only:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. absent-before
   `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_bld_full_integration_20260901.md`.

Everything else is read-only. No candidate, source, recovery, CLI, contract
tests, protected 119, plan/context/status, prior receipt, governance, live
preflight/verify/build/remediate, Git, cache cleanup, semantic, promotion,
publication, or release mutation is authorized.

## Production build state machine

Implement accepted parent sections 9.2-9.4 exactly, with no reduced verifier:

1. Complete context/repository/path/source/sidecar/contract/recovery admission
   before any build write. Do not create parent/temp/marker first.
2. No-follow classify final and require missing; require admitted non-reparse
   same-parent/same-volume publication root.
3. Create the exclusive hidden same-parent temp and exclusive marker in the
   exact frozen `OwnedTempRoot` shape. The marker binds nonce, normalized
   temp/final, profile seal, and directory file id.
4. Write 500 non-QA files with create-new semantics; the sole shared finalizer
   writes COMMANDS then independently derives 501-row inventory and byte-stable
   QA, producing 502, and invokes the same strict verifier.
5. Before publish, reclassify final/temp/marker and revalidate containment,
   file id, nonce, profile, non-reparse state, and final absence.
6. `rename_no_replace` must be truly no-replace at the publication operation.
   On Windows use `MoveFileExW` without replace-existing or an equivalently
   proven primitive; a check-then-`os.rename` race is insufficient and
   `os.replace` is forbidden. Destination appearance yields
   `E_BUILD_PUBLISH_RACE` without mutation/deletion of that destination.
7. After publish, prove former temp file id at final, temp absent, marker still
   matching; run full strict verify again; only then delete the exact marker
   and prove it absent. A post-publish failure leaves final plus marker intact.
8. Provide `remove_owned_tree(OwnedTempRoot)` for pre-publish cleanup only. It
   must revalidate exact ownership and no-follow descendants and may remove only
   that temp and marker. No wildcard, computed/broad root, `shutil.rmtree`,
   followed-link traversal, final deletion, or retry loop. Any mismatch stops
   `E_BUILD_TEMP_OWNERSHIP` and preserves evidence.

## Exactly three real BLD nodes

Keep exactly three BLD tests, all using real production helpers:

- fresh-root success proves admission-before-write, owned sibling lifecycle,
  pre/post strict verify, atomic no-replace publication, exact 502/501/500,
  returned state, zero temp/marker and zero external/tool access;
- existing-target refusal snapshots kind/file-id/bytes/hash, proves exact
  `E_BUILD_OVERWRITE`, byte/type/id identity, and no sibling/marker creation;
- finalizer parity uses two independent inputs: real `_test_build` versus real
  `_write_non_qa_bundle` plus `_finalize_and_verify` in an owned staging root;
  assert every relative file, COMMANDS, QA, success payload, and 502/501/500
  manifest byte-identical, and record ownership/cleanup state transitions.

Counts stay 368 negatives + 3 BLD = focused 371. Toy bundles, arbitrary count
comparisons, test-only schemas, or static-only BLD assertions are forbidden.

## Registry closure and canonical evidence

Remove or make unreachable the generic proxy fallback: every one of the 368
case ids must resolve before collection to its own non-null, object-distinct,
descriptively named physical callable. Prove no case mutates a generic
`COMMANDS#/case/<id>` marker and no expected code is derived from observation.

Run the full focused file cache-disabled and require collect `371`, run
`371 passed`, exact family counts including REG2/QAV90/INV18, 368 unique ids,
368 unique callables/names, and exactly six declared alias pairs/twelve
distinct identities. Run targeted BLD 3 separately and the affected REG/QAV/
INV/SCH/CMD alias/taxonomy nodes as a regression.

The immutable integration receipt must embed literally:

- a machine-readable JSON array of all 368 complete closed 16-field
  `MutationAudit` objects in registry order;
- all 368 canonical six-field UTF-8/LF audit rows in registry order, exact byte
  length and recomputed SHA-256;
- the two complete REG objects and exact 38-selector synthetic delta;
- a separate three-row BLD state-transition table containing admitted/final/
  temp/marker states, non-secret file-id tokens, manifest identities, verifier
  call phases, and result;
- canonical profile serialization/seal, provider ids, public/test signatures,
  route table, full case-id list, family table, and exact six-pair table;
- literal commands, native exits, stdout/stderr SHA-256, collected/passed
  counts, material/cache pre/post identities, exact path diff, elapsed time,
  and token use or `unavailable`.

Run with `python -B` and pytest cache disabled; keep captures in memory or
automatically cleaned owned temporary roots. Preserve the three recorded
pre-existing `.pyc` and root `.pytest_cache` identities and prove zero new
attributable residue. Do not run protected 119, combined 490, or live commands;
those exact already-prepared QA commands belong to the later Luna execution
task.

Complete only when all requirements pass. Otherwise write a truthful BLOCKED
receipt and stop without cleanup, scope widening, weaker BLD tests, production
routing, or delegation of engineering evidence to Luna.
