# Terra engineering receipt: Viral Step 6A REG

- Result: `COMPLETE_ENGINEERING_PENDING_INDEPENDENT_QA_AND_CRITIC`.
- Role: reusable code/test engineering, `gpt-5.6-terra` / `medium`. Luna performed no implementation, fixture, test, or audit construction.
- Orchestrator policy owner: root/main chat `gpt-5.6-sol` / `medium`; assignment state `platform-unverified`; token use `unavailable`; elapsed approximately 52 minutes.
- Scoped override: Luna/medium may only execute prepared bounded QA commands. Terra owns this engineering packet.

## Admission and material boundary

Admission was verified before the first write: dispatch `31A045116EF7D10F430764D974D0B84F734B7A45D5CB81C841058A255510D77B`, amendment `6E0C6280D7930D6994E461E32363C1FA15B0BBC39AFAE34CAF9EE8D84737341D`, ACCEPT review `FEB2C162524A1776729CBF236CF7419B118C97889B125AE623B08E471956C52B`, and absent receipt path. Frozen library/test hashes were `34943D5E0008A01A1F3AFC3AF2D49091F06049187AE9D0CB7DA02654663862D4` / `D3FA871BBA3DED04ECD216544B7A9A7EEECB95D4769DDF45612B412990F9D192`.

Exact delta: modified `kb_creator/tests/test_scenario_source_reconstruction.py`, then added this absent-before receipt. Library is unchanged at `34943D5E0008A01A1F3AFC3AF2D49091F06049187AE9D0CB7DA02654663862D4`; test post-hash is `FDFFAD49EF059C542F01A3E215E688B1A5DB9C7D16C88FAB73466546BAFCE6B9`. No candidate, source/recovery, protected, plan/context/status, prior receipt, Git, live, cache, cleanup, or library path was written.

## Result

The new fresh-fixture `REG-P1-stale-metadata` creates the approved synthetic state: v2 QA schema; manifest hash `C32CCA2A85F8123A2BE9E015FB39642943E31FCD723FA466FA436F454B344C3A`; removed recovery-evidence key; both blocker summaries 3; exactly sheet-001 through sheet-031 removed; 470 current fixture rows left in ordinal order; count/digest recomputed; canonical rule and candidate state preserved. One shared verifier call gives `E_SHAPE_QA` with `()`.

`REG-P1-missing-enforcement` is a distinct callable/fresh fixture which changes only `candidate/evidence/COMMANDS.json#/counts/pages` from 124 to 125, declares `(inventory, qa)`, and gives `E_COMMAND_COUNTS_PAGES`. It is exactly the sixth cross-family alias with `CMD-count-pages-wrong`; no test identity is supplied to the verifier.

Registry result: REG=2; negatives/unique IDs/unique callable objects=368/368/368; BLD=3; focused=371; retired `E_QA_SCHEMA` search is empty (expected rg exit 1). Current full declared 368-row UTF-8/LF audit stream is 51005 bytes with SHA-256 `8C5C2A0A69C212465D1429FA38B35A4802C9AFCDF52F9461A1747D5729671DD4`.

Six cross-family alias pairs, all distinct callables: SCH/QAV required-member; SCH/QAV extra-member; INV/QAV cardinality; INV/QAV digest; INV/QAV ordinary-row; CMD-count-pages-wrong/REG-P1-missing-enforcement. Their one-based ordinals are `81/272`, `104/295`, `117/359`, `122/360`, `111/361`, `236/363`. Stale metadata is not an alias.

## REG audit evidence

Both closed 16-field audit objects were materialized in fresh `TemporaryDirectory` fixtures: strict_verify_calls=1, outside_fixture_reads=0, undeclared_changes=[], residue=[], result PASS.

| Case | Selector | Reseal | Expected / observed |
|---|---|---|---|
| REG-P1-stale-metadata | candidate/RECONSTRUCTED_EN.qa.json# | () | E_SHAPE_QA / E_SHAPE_QA |
| REG-P1-missing-enforcement | candidate/evidence/COMMANDS.json#/counts/pages | inventory,qa | E_COMMAND_COUNTS_PAGES / E_COMMAND_COUNTS_PAGES |

The stale audit direct delta is the required ordered 38 selectors: schema, recovery-manifest hash, recovery-evidence hash, both blocker summaries, 31 `output_inventory/renders/contact_sheets/sheet-NNN.png` selectors for 001..031, output-inventory count, and output-inventory digest. Its independently recomputed fixture-local 470-row digest is `AB0FEF2085918E313E97BDADFE8AA6C20FDCE6AD8801F09E1948B27C501CC2DC`.

The exact two-row case stream is 224 UTF-8/LF bytes, SHA-256 `73A0B02AFC715AFA1EBC738FB2241329C76752342E67916A5376FC9659A43F4C`.

## Commands and residue

All Python invocations used `python -B`; pytest used `-p no:cacheprovider`. Native results: REG 2 passed in 5.87s; taxonomy 4 passed in 10.93s; all 12 alias members were rerun in three disjoint native 4-node subsets, each 4 passed (10.91s, 11.11s, 11.41s); BLD 3 passed, 368 deselected in 7.58s; collect-only 371 in 0.10s. One captured alias subset had exit 0, stdout SHA-256 `3877AC4E2D33538D292B023BF6B846F6A17FA7CF6294EC1DE76D275F3284FE88`, and empty stderr SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.

The three permitted pre-existing bytecode hashes are unchanged: `168C67BC8784F76DBA57F873A32B419112998AA359C9F1A21BF3E954D3BD13C4`, `9F4E03CC81C749C4C29FD0F97478D3EB1A2EF735D1B225DAD191B0D451FBEF54`, `DE4E516486951CE4EA9DA7621C54D7429489B0ABAB3CE1F58B28309457BDF0B9`; `.pytest_cache` is unchanged. Temporary fixtures were automatically removed. New attributable residue is zero.

## Downstream

No independent QA, critic implementation review, semantic work, candidate acceptance, or release decision is made here. Next action: prepared-script QA only, then a fresh independent GPT-5.5/high implementation/process critic.
