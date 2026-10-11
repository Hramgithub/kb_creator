# Task packet — independent Viral v2 B1c4 exact asset-identity rereview

## Governance

- Goal id: `20260830-kb-creator-next-scenario`.
- Review kind: implementation rereview only, not architecture or release.
- Assigned role: fresh `nri-independent-critic`, canonical `gpt-5.5` / high.
- Main chat retains orchestration.
- Do not implement, repair, redesign, mutate Git, or edit plan/context/config/
  candidate/assets/downstream files.
- Only write the immutable receipt
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_asset_identity_rereview_20260903.md`.

## Bound state

- Blocking prior rereview receipt SHA-256:
  `D6E741AF31FE81CD5307E370D589CC442A9456149CDFE556C12E58C44499323A`.
- Approved architecture receipt SHA-256:
  `A68A643CEBCF11BFBC3F358A900F3677309C02A8D410AB29B4861D62DAEB6442`.
- Exact remediation packet SHA-256:
  `BC89A0CE0B47169281545E9332583C02219927613643219A5CE2E37E43A3D0BD`.
- Engineering receipt SHA-256:
  `FB497EAB9AD911B9E6DBD59B4527F2BD29D642179696146FAA6C61C9743F46D5`.
- Final scoped hashes:

```text
author helper   FFE2202E0FC2CB2FCD36FCA802C8484057E714704B734027B6AD25B17F0C9249
author tests    A019999265B17005775D801E4D5DF8E83A540959F402F8837705069C58D7386F
builder         E36775C33A430A3F7D21743D5DCD9EBA185E16F247CD5DF42FECA6B9080A1DF9
builder tests   236E56016E687B26F772967A8475E4BF4E797E954D0CCB359AAB0CC1337BA1C2
verifier        F2C0C79FBA69F6C82ABD0A86BBF88B69B0987ACE89C618FA45837F71E16B544B
verifier tests  D240A5BEE52759C03E82928CCE968C2509F8FFFF569BBB3168A04D8E973F9EFB
```

Stop with P1 identity drift if any bound byte differs.

## Required adversarial rereview

Read the prior rereview finding and independently inspect whether builder and
verifier each reconstruct an expected declaration table per logical asset id
from frozen v1, accepted-v4 package/manifest, three-view comparison, Markdown
spans and source-PDF metadata without importing author or each other.

At minimum:

1. Reproduce the exact original borrowed-pair attack: asset
   `viral-accepted-e1e2aa6964b45037691d92e4faf91dba6bbd411e409dc49c237f6b0e71e6ce85`
   borrows both valid binary and valid provenance from
   `viral-accepted-a1d83a711a4b7962110b1ba158b2d610043f1fa836e06458e675373094acd6c1`.
2. Reverse that pair and try additional same-page/same-outcome visual-region
   pairs, a Markdown-reference pair and a provisional-full-page recipe pair.
3. Try borrowing binary only, provenance only, binary plus adjusted provenance,
   manifest identity plus comparison block, and source-page-preserving swaps.
4. Verify all fail before visual review at builder
   `v2 B1c4 asset declaration identity mismatch` and verifier
   `E_V2_ASSET: declaration-identity` or equally specific B1c4 gates.
5. Verify the positive 123/125/93/32, provenance, eight-target/sixteen-child and
   migration partitions still hold and all previous critic mutation classes
   still fail early.
6. Inspect independence: no shared validation implementation, no author import,
   no self-reported asset-id trust and no comparison by only broad page/outcome.
7. Run six-file py-compile, combined suite (orchestrator reproduced 124/124),
   both frozen-v1 preflights, guarded unmutated v2 preflight pair and no-output
   sweep. Preserve the nine historical candidate/staging roots.

## Decision

Terminal token must be exactly one of:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION`, only with no
  unresolved P0/P1/P2; or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION`, with
  exact evidence and bounded remediation.

Approval closes only B1c4 implementation and authorizes no canonical config,
Candidate D, MASTER_RU, Step 8A, HTML/PDF or release claim.
