# Viral Step 7 reader-surface code receipt

- Scope: bounded implementation attempt for the assigned reader-surface code only; no config, candidate, reconstruction, MinerU, plan/status/context, Git index/history, MASTER_RU, or downstream output was changed.
- Result: **BLOCKED_IMPLEMENTATION**. The frozen config cannot pass its first semantic-fragment raw-hash check under the architecture's stated selector/normalization contract.
- Orchestrator policy owner: root main-chat `gpt-5.6-sol` / medium; this receipt transfers no orchestration or release authority.
- Assignment state: blocked pending a corrected, independently auditable raw-range normalization definition or corrected frozen semantic-fragment hashes.
- Scoped override: Terra/medium engineering was explicitly assigned only the five-file code/test/receipt surface; only the builder and this receipt were changed during the stopped attempt.
- Timestamp: 2026-09-02T00:00:00+03:00 (written during the assigned contributor turn; exact telemetry timestamp unavailable).
- Elapsed time: approximately 35 minutes. Token use: unavailable.

## Files checked or changed

- Changed: `kb_creator/scripts/build_scenario_master_en.py` (partial reusable closed-schema validator, selector resolution, alt-policy validation, suppression/owner-local-heading plumbing; not accepted because the frozen-input invariant fails).
- Checked, unchanged: `kb_creator/scripts/verify_scenario_master_en.py`, `kb_creator/tests/test_build_scenario_master_en.py`, `kb_creator/tests/test_verify_scenario_master_en.py`.
- Receipt: this file.

## Evidence

- Assignment packet SHA-256 matched `709808AC6BC9C30CA368F55EC3507E6A70214F6731F5480342AB1293C3062C1F`.
- Config contains the required top-level `reader_surface` and reports 25 semantic fragments, 22 suppressions, and 107 reader assets.
- S01 resolves from page-008 content start (after source marker and surrounding blank lines) at character offset 26 through the start of `Corrina Trench (Investigator)` at offset 744. The direct UTF-8 SHA-256 is `C8F61FF8E835CD0E03ADFF455FD8D77BD47113E7B784E40083A38D166304725A`, not config `1C39F0DBE867C06AC8A8A957D62AD183B533BFB22D24C1BBDD838A3A71DC87F3`.
- Alternative no-appended-newline forms (`rstrip` and LF `splitlines` join) also do not yield the pinned value (`39736B22...` and `83E5A9CA...` respectively). Therefore this is not safely repairable by guessing an undocumented normalization rule.
- Authorized commands run: `python -m py_compile kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py` (pass); focused builder/verifier pytest invocation (fails before candidate build because S01 fails); focused builder rerun (same S01 invariant failure).

## Risks and next action

- Risk: accepting any guessed range normalization would turn the closed semantic contract into an unreviewable alternate mutation engine and could conceal additional S02-S25/suppression disagreements.
- Next action: Sol must provide a correction packet that either defines the exact preimage algorithm unambiguously with a worked S01 witness, or revises the frozen config hashes after a read-only authoritative audit. Then resume the same bounded implementation from this receipt; independently review before any candidate build or release decision.
