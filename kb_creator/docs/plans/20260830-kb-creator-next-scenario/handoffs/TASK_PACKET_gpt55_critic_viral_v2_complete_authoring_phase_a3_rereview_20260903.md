# Task packet — independent Viral v2 Phase A3 rereview

## Role and scope

- Role: `nri-independent-critic` / GPT-5.5 / high.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Independent implementation rereview, not implementation and not release.
- Write only:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_a3_rereview_20260903.md`.
- Do not edit code/tests/plan/context/config/candidate/scratch/Git/downstream.

## Bound final identities

- Architecture receipt:
  `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- Original A3 changes-required receipt:
  `67BB38E33B7191D4061A6380A252ED9119A1931DFEF4273426D82616E520C6B7`.
- First xref public-defect receipt:
  `1C0A0A84C42B686C778D595A445995D78E5DEDEB15A30F46F11A4BA6C576188B`.
- Xref/hierarchy remediation receipt:
  `BBDD39B0DC37CA452D2A7C6DD6A2E1A78CE0CB0EDC70EFFD2280C8C33355DCD6`.
- Final isolation remediation receipt:
  `1C644CB33096F94934C093BD47FDAA58255977E4794CC3BCC88E83D81BB5054B`.
- Builder:
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`.
- Verifier:
  `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.
- Builder tests:
  `EE0F021497A15879A878A83703427DC42DB5AD7D364D87829669A41606BCA376`.
- Verifier tests:
  `1828EE86ED5C994D9C33C1A9AEBC5315E45861B750076EE1E31477F9FB4C8417`.
- Orchestrator final-byte reproduction: py-compile passed; exact normal
  four-module baseline ran 104 tests in 77.813 seconds, `OK`.

Refuse on hash drift.

## Required adversarial rereview

Read the architecture, original changes-required receipt and all remediation
receipts. Independently inspect builder and verifier; verifier must not import
builder validation helpers. Do not infer coverage from test names.

Re-run the original critic probes against both public paths and prove:

1. Full A3 xrefs pass top-level; legacy shape, source/text/target drift and
   exact migration mismatch/other-real-target/wrong-domain/unknown target fail.
   Audit exact `hierarchy:<anchor>` binding too.
2. Every event type accepts only legal source operations; heading+suppress and
   all other illegal pairs fail.
3. `contains` closes to real owned spans/child events and rejects unknown,
   duplicate, incomplete, cross-owner/page/kind and reorder.
4. Assets require exact asset-owned image-reference spans, unique non-reuse and
   valid placement/reader policy; event text/foreign/reused spans fail.
5. All eight typed schemas require complete source-bound shapes. Title-only
   equipment/creature and map/pair without reader assets fail. Probe omissions,
   extras/invented leaves, bindings, order/count/membership, creature nested
   tables and pair back semantics.
6. Builder rejection leaves no destination; tests are isolated and deterministic
   in builder/verifier/focused/four-module normal and reverse orders.

Use temporary probes outside the repo and remove them. Run py-compile, focused
and four-module normal/reverse baselines, both frozen-v1 preflights, scoped diff,
hash and forbidden-output checks. Confirm no new scratch and classify but do
not mutate the six pre-existing `.v2-inputs-*` roots.

Phase B may open only with no P0/P1. Report P0/P1/P2 and end exactly:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_A3`, or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A3`.
