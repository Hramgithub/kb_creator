# Viral v2 A3 public-matrix isolation remediation receipt

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `viral-v2-complete-authoring-phase-a3-public-matrix-isolation-remediation`.
- Role: `nri-engineer` / requested `gpt-5.6-terra` / medium.
- Orchestrator policy owner: main chat / `gpt-5.6-sol` / medium.
- Assignment state: completed; ready for independent A3 rereview, not a release decision.
- Scoped override: none.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Timestamp: `2026-09-03T11:40:00+03:00` (Europe/Moscow; completion timestamp).
- Elapsed time: approximately 35 minutes.
- Token use: unavailable.

## Scope and result

Only the two focused test modules and this immutable receipt were changed.
Production validators, plans/context/status, scratch/config/candidates, immutable
inputs, Git, `MASTER_RU`, Step 8A, downstream HTML/PDF and generated output were
not edited.

The initially observed four-module failure was reproduced exactly: `104` tests
in `66.388s`, with `39` failures and `26` errors. It was a test-fixture
isolation defect, not a production defect. The builder helper created an asset
event whose source span was incorrectly event-owned; that invalid baseline
preempted unrelated positives. The verifier's public helper also left newly
materialized migration targets unsealed, used manual `setUp()` calls inside
subtests, and asserted broader/wrong first-error alternatives.

The focused fixture helpers now construct correct fresh source ownership for
asset events, reseal public migration targets, keep structured `contains`
source-bound after helper construction, and reset every public typed case to a
fresh fixture. Legacy serializer inputs now use the closed current typed
schemas. Verifier public negatives assert the legitimate first seam: closed
schema omission, unbound extra leaf, and map/pair missing reader-asset seam.

## Files checked or changed

- Changed: `kb_creator/tests/test_build_scenario_master_en.py` — SHA-256
  `EE0F021497A15879A878A83703427DC42DB5AD7D364D87829669A41606BCA376`.
- Changed: `kb_creator/tests/test_verify_scenario_master_en.py` — SHA-256
  `1828EE86ED5C994D9C33C1A9AEBC5315E45861B750076EE1E31477F9FB4C8417`.
- Added: this receipt.
- Checked unchanged: `kb_creator/scripts/build_scenario_master_en.py` —
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`.
- Checked unchanged: `kb_creator/scripts/verify_scenario_master_en.py` —
  `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.

## Verification and evidence

- `python -B -m py_compile` over both validators and both focused tests: exit 0.
- Builder alone twice: `67` tests, `34.387s` and `33.342s`, both OK.
- Verifier alone twice: `37` tests, `44.203s` and `44.218s`, both OK.
- Builder then verifier twice: `104` tests, `77.186s` and `77.317s`, both OK.
- Verifier then builder twice: `104` tests, `77.043s` and `78.394s`, both OK.
- Normal four-module order twice: `104` tests, `77.321s` and `77.468s`, both OK.
- Reverse four-module order twice: `104` tests, `77.617s` and `78.154s`, both OK.
- Frozen-v1 builder preflight-only: `preflight_passed`; contract
  `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`,
  reconstruction inventory
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`,
  source `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Frozen-v1 verifier preflight-only: `preflight_passed`; publication config
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Scoped `git diff --check` passed. Forbidden v2 config/candidate/synthetic
  roots required by the packet were absent after all runs.
- After the final exact builder-seam assertion tightening, the four public
  builder matrix tests passed again (`4` tests, `12.343s`); py-compile and the
  scoped diff check passed again. The prior full fresh-process order matrix
  passed on the same fixture behavior before that assertion-only tightening.

## Blockers and next action

No production defect was reproduced and no engineering blocker remains. Route
the two test-only changes and this receipt to a fresh independent A3 critic
rereview. This receipt does not authorize a release decision or Phase B work.

`READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A3_REREVIEW`
