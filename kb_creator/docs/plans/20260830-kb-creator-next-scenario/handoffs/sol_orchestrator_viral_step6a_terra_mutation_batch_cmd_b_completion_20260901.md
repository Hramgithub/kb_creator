# Terra evidence assignment: Viral Step 6A CMD-B completion

This narrowly scoped assignment resolves only the false CMD-B blocker caused by
classifying immutable pre-existing cache as residue created by the CMD-B run.
It does not weaken the zero-new-residue rule and authorizes no cleanup.

## Authority and baseline

- Accepted assignment review
  `gpt55_critic_viral_step6a_executable_enforcement_final_recovery_assignment_review_20260901.md`,
  SHA-256 `FEB102C7F2DA4B29EC34360C721CD52A37A2DACD6D6A6AE3E558CFC878E47269`,
  explicitly requires pre-existing `.pyc` residue to remain untouched because
  cleanup was not authorized, while requiring no new residue.
- Prior completed family receipts use the same scoped rule: preserve and report
  pre-existing cache, prove that the current run creates none.
- CMD-B material is read-only for this task:
  - library `231C976E57D6DC1051C326C479EC42D87525DDB8565741A0D64A0E96B37352C7`;
  - tests `59C148D64F5CAB7B6D50723A4C10D5AD292FC0449D839CDB963DFE6F2403F1EF`.
- Immutable blocked receipt:
  `terra_engineering_viral_step6a_mutation_batch_cmd_b_20260901.md`, SHA-256
  `AE658CBED70482120B7482EB4C44BCA3F95D5FBEB8339295DD7DA5824B49A65E`.

The observed cache baseline predates this CMD-B dispatch and must not be
modified:

- `kb_creator/scripts/__pycache__/scenario_contract.cpython-313.pyc`,
  SHA-256 `168C67BC8784F76DBA57F873A32B419112998AA359C9F1A21BF3E954D3BD13C4`;
- `kb_creator/tests/__pycache__/test_scenario_contract.cpython-313-pytest-9.0.2.pyc`,
  SHA-256 `9F4E03CC81C749C4C29FD0F97478D3EB1A2EF735D1B225DAD191B0D451FBEF54`;
- `kb_creator/tests/__pycache__/test_scenario_source_reconstruction.cpython-313-pytest-9.0.2.pyc`,
  SHA-256 `DE4E516486951CE4EA9DA7621C54D7429489B0ABAB3CE1F58B28309457BDF0B9`;
- pre-existing root `.pytest_cache` directory.

## Sole allowed write and evidence

Create only absent-before
`terra_engineering_viral_step6a_mutation_batch_cmd_b_completion_20260901.md`.
Do not edit code, tests, the blocked receipt, cache, candidate, source, recovery,
protected tests, Git state, or any other file.

Before creating the receipt, use Python `-B` and pytest `-p no:cacheprovider` to
rerun all 22 exact CMD-B cases in bounded chunks, the representative regression,
BLD 3, and collect 371. Re-materialize or mechanically revalidate all 22 full
Section-11 objects and recompute the packet-formula canonical bytes/digest.
Snapshot the four pre-existing cache targets before and after and prove their
identities unchanged; prove zero new cache, fixture, temp, marker, probe, log,
or bytecode path attributable to this dispatch.

The standalone immutable completion receipt must embed all 22 full objects,
canonical rows/bytes/digest, commands and native results, material before/after
hashes, cache-baseline before/after identities, exact changed-path list, and a
limited supersession statement: it supersedes only the blocked receipt's claim
that unchanged pre-existing cache makes CMD-B non-integrable. It must not claim
Step 6A, QA, release, candidate, semantic, or publication acceptance.
