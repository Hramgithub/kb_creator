# Task packet — independent Viral v2 B1c4 implementation rereview

## Governance and scope

- Goal id: `20260830-kb-creator-next-scenario`.
- Review kind: implementation rereview only; not architecture or release.
- Assigned role: fresh `nri-independent-critic`, canonical `gpt-5.5` / high.
- Main-chat `gpt-5.6-sol` / medium retains orchestration.
- The critic must not implement, repair, materially redesign, mutate Git, or
  edit plan/context/config/candidate/assets/downstream files.
- Only authorized write: immutable receipt
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_implementation_rereview_20260903.md`.

## Bound inputs

- Original implementation-review packet SHA-256:
  `C8CA9473BDD6C7C03E278381AC37999AA8D1CD9DDA5E197F0F7AC2086B070ACF`.
- Blocking review receipt SHA-256:
  `D20415E2B888A3370C00071991A16EE9919312F3F2659D80C0374D91ABBF85A1`.
- Approved architecture receipt SHA-256:
  `A68A643CEBCF11BFBC3F358A900F3677309C02A8D410AB29B4861D62DAEB6442`.
- Parent remediation packet SHA-256:
  `61C6AC7752618EFA510B25B84049D300E76C3919493C5FB84C8CF0F9EA27990D`.
- Continuation packet SHA-256:
  `4188992330DD0180FD744E047FF020EB7880792B6216FD9B34BF658CCBDC5E39`.
- Partial remediation receipt SHA-256:
  `25D4F0B8397F019FBCCCCE1B5FAA6D7C376B4FE264537DB8291DB998AEE70E06`.
- Continuation receipt SHA-256:
  `FD33C9F31C956FAA6A440C6EC7F636112E283B99A7902F718501C183A8DAEC7D`.
- Error-taxonomy addendum SHA-256:
  `92EA06C32F773B3ECBDAAB0B17BE38E8266E9619C7CEA5DFD32A17E1C3CF9097`.

Final scoped implementation/test hashes:

```text
author helper   FFE2202E0FC2CB2FCD36FCA802C8484057E714704B734027B6AD25B17F0C9249
author tests    A019999265B17005775D801E4D5DF8E83A540959F402F8837705069C58D7386F
builder         DB1CA64720E8A9525CA5F9483E4EB57444913FF83B6FAD7EAA12777752E2C367
builder tests   DE1CC0AC1A20EF20A47C55F5771BBEA68B8BC67DB1B770D51F6F1F86118941C6
verifier        B5EDA81F746501116F305952F173A05C64192FC15BD1E8CBCFC573FBFED203B2
verifier tests  C357DCB7EAD79F9BAFEE836514466150FFD11954F75C980D4106294AF6F5B7E6
```

Stop with a P1 identity finding if any bound input differs.

## Mandatory rereview

Reperform the original packet's review, concentrating on the two prior P1s and
the taxonomy addendum. Inspect code and immutable evidence; do not accept the
remediation receipts as proof.

1. Verify the public `provenance` declaration is a genuinely closed,
   discriminated union for exact Markdown references, visual regions,
   provisional full pages and exclusions.
2. Independently prove builder and verifier rederive every field from accepted
   v4 pages/manifest, three-view comparison and source-PDF metadata; test fake,
   missing, swapped, borrowed and internally self-consistent-but-source-wrong
   evidence.
3. Independently prove all 121 path-backed rows bind path/bytes/SHA/magic/
   decoded dimensions and exact manifest/comparison identity before review.
4. Prove the exact ordered 123-row migration table and exact ordered eight
   target/sixteen-child graph, including page/slot/physical-unit/owner/
   accessibility obligations and exact child order.
5. Re-run every original critic probe: binary SHA/missing, foreign child,
   child swap, forged target, same-page membership swap, exclusion membership
   swap; add omission, duplicate, order, decision/evidence substitution and
   reader/event leakage probes. Broad counts should be preserved where useful.
6. Confirm every mutation fails at a B1c4-specific public gate in both builder
   and verifier, not at visual review or generic migration taxonomy. Explicitly
   reproduce the prior `v2 migration count mismatch` case.
7. Confirm exact positive totals and partitions: 123 frozen outcomes
   `99/2/16/6`; provenance `16 Markdown / 100 visual / 9 provisional full page /
   6 excluded as applicable`; final `125 = 93 reader + 32 evidence`; exact
   eight targets and sixteen unique replacement children.
8. Confirm v1 compatibility, unmutated v2 exact next seams, independent
   builder/verifier implementations and absence of canonical/temp config,
   candidate/render/review/downstream outputs. Preserve the nine historical
   candidate/staging roots.

Minimum execution evidence: six-file py-compile; combined suite (orchestrator
reproduced `122/122` on these hashes); both frozen-v1 preflights; guarded public
v2 preflight pair; direct adversarial probes; scoped status/diff and no-output
sweep.

## Decision

Write exactly one terminal token:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION`, only with no
  unresolved P0/P1/P2; or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION`, with
  exact severity/evidence/bounded remediation.

Approval closes only B1c4 implementation. It does not authorize a canonical v2
config, Candidate D, MASTER_RU, Step 8A, HTML/PDF or release acceptance.
