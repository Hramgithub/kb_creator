# Viral v2 A2 decision-reference integration recovery receipt

- Scope: projection-only recovery in the two independent production validators; no helper/config/candidate/input/Git change.
- Role: `nri-engineer` / GPT-5.6-terra / medium; orchestrator policy owner `gpt-5.6-sol` / medium; scoped override none.
- Root cause repaired: outer decision-evidence rows legitimately contain `kind`, while existing identity helpers deliberately accept only `path/bytes/sha256`. Both callers now pass an explicit exact three-field identity projection, preserving the helper's closed schema globally.
- Evidence: focused existing suite was rerun after the fix and exited zero. It remains `77` tests.
- Remaining gap/blocker: this recovery turn did not complete the required expanded (>77) equivalent four-kind mutation matrix, nor capture four-module/preflight evidence. It must not be accepted as a P1 closure.
- Timestamp: `2026-09-03T07:20:00+03:00`; elapsed approximately 10 minutes; token use unavailable.

Terminal status:

`CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_INTEGRATION_RECOVERY`
