# Viral Step 7 — independent reader-surface implementation review

## Role and authority

- Reviewer: independent critic, `gpt-5.5`, high.
- Review is read-only except for one receipt named
  `gpt55_critic_viral_step7_reader_surface_implementation_review_20260902.md`.
- The critic must not implement, redesign, edit config/code/tests/candidates,
  build a candidate, stage/commit, or claim release/user acceptance.
- Orchestration and integration remain in the main chat.

## Frozen review inputs

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Config: `kb_creator/working/viral/master_en/publication_config_v1.json`,
  707368 bytes, SHA-256
  `EEE2B0BBE8EB0F8862F09C884818B1C20C8DC023FCC01B504E963AFD3346438E`.
- Builder: SHA-256
  `3832B1F218C7F658E98660ADB9757BCA365F15A2A5A9C0677764992329C34051`.
- Verifier: SHA-256
  `C0544CFEA3D24E6B5F4501D9FADAF7B9C8B3D4F8A41C9238C9FE7A71C2753335`.
- Builder tests: SHA-256
  `E33A39DA0F9C53DD38A4EB89289717E6C9D3A99422CB704BC060F86589C5F259`.
- Verifier tests: SHA-256
  `B7D6822A44B06A87457DBE6B37F9CE97CC60E33083B2387C04C665402771B04F`.
- Engineering PASS receipt: SHA-256
  `AF6F2CA945E89768D9FE833D6010669DB6A59936F8F22E2B2174398B491045A4`.
- Architecture and errata are the Sol reader-surface remediation receipt plus
  the asset-count, reader-alt-ordinal, suppression and hash/endpoint correction
  packets in this handoff directory. Later evidence supersedes the erroneous
  ordinal rule: accepted reader assets map rows 001-105 by placement, front
  cover row 106, back cover row 107.
- Accepted reconstruction v4 remains immutable; candidate C is absent.

## Confirmed pre-review evidence

- Main-chat rerun: `53 passed in 27.34s` for exactly the two focused modules.
- `py_compile` builder/verifier and scoped `git diff --check`: pass.
- Config audits: 25/25 semantic exact ranges and normal claims; 22/22 exact
  full suppression ranges; 41/41 source xrefs; 29 structured units and notes;
  107 architecture alts; 123 asset owners; 107 reader + 16 evidence; lexical
  conservation 1935 total / 1862 owned / 73 generated / zero open blocks.
- Candidate C remains absent. Passing implementation tests do not prove release.

## Required independent questions

Inspect the actual current config/code/tests and answer with code evidence, not
the engineering receipt alone:

1. Is the new top-level and nested `reader_surface` schema closed, including
   selector combinations, counts and unknown-key rejection?
2. Does the builder validate semantic rows over normal claims without using a
   second overlay/mutation engine?
3. Are suppression endpoints full-range and identical across validation,
   deletion, provenance, structured transforms and conservation?
4. Is owner-local heading normalization deterministic and correctly propagated
   through reader emission, structured evidence and sidecars?
5. Are reader alts bound by asset identity/validated policy, excluding
   evidence-only ordinals and preventing provenance/plain-description leakage?
6. Does the verifier recompute the public contract independently without
   importing or trusting builder internals/sidecar success?
7. Do sidecars provide enough source/emitted range/hash/owner/order evidence for
   the verifier and later full-reader QA?
8. Are the focused tests behavior-oriented and sufficient for the architecture's
   negative cases and Viral regressions, especially verifier rejection tests?
9. Did any change weaken accepted reconstruction identity, structured/xref
   closure, asset bytes, link targets, candidate topology or external gates?
10. Is it safe to authorize two scratch builds and then candidate C, or must code
    remediation occur first?

The critic may rerun only the two focused test modules, `py_compile`, scoped
diff checks, and read-only diagnostic scripts. Do not run MinerU, historical
371/119/490 suites, a candidate build, or downstream stages.

## Receipt format

Return exactly one verdict: `APPROVE_IMPLEMENTATION` or
`REJECT_IMPLEMENTATION`. Findings must be ordered P0-P3 with exact file/line or
contract loci, impact, and minimal remediation. Record commands/results, input
hashes, changed-file check, unresolved risks and whether candidate creation may
open. A critic approval is not release approval; a separate review follows the
frozen successor candidate.
