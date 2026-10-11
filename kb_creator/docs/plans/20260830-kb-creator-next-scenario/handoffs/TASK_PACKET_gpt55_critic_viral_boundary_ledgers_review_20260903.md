# Task packet: independent review of Viral boundary ledgers

## Role and independence

- Reviewer must be a real `nri-independent-critic` (`gpt-5.5`, high) child
  agent. The ledger authors and orchestrator must not substitute for it.
- Review only; do not implement, edit ledgers/config/code/tests/candidates, or
  stage/commit/push.

## Inputs

- committed user-review registry and accepted remediation architecture;
- frozen semantic candidate/review evidence;
- accepted reconstruction v4 and source PDF where necessary;
- the three ledgers and their author receipts:
  - `boundary_ledger_pages_001_040.json` expected SHA-256
    `44E2E8199768DEBCD0B41FF5294F33BFF0D2AC3181E3AE6A51A3B0643EDF31AF`;
  - `boundary_ledger_pages_041_068.json` expected SHA-256
    `92B40358A8B2294575526225290BE3766E529D5126ABADDC6CBBDAC719784A3B`;
  - `boundary_ledger_pages_069_122.json` expected SHA-256
    `9922B8A7A1B81D1961FE88E851C3BB9D78BA579F89C2459978A275936DACD813`.

## Required review

Independently prove or refute:

1. Exact union coverage of all 429 broad candidates, one disposition each,
   no duplicates/overlaps, no unresolved blocking rows, and pages 123--124
   excluded outside the reader ledger.
2. Every declared source segment resolves to exact v4 line bounds/text/hash;
   source ordering is monotonic and cross-range boundaries are closed.
3. Semantic fidelity to every blocking user defect/architecture row, including:
   full titles; 8 Appearance plus 5 Gear Carried bounded panels; 65 Keeper's
   Notes; all 9 Sight panels; Rumors/Signs/Lemon and all encounter/D10/infection
   tables with exact continuation/count; stream schedule 1--8; NPC headings;
   complete hospital hierarchy and run-ins; exact `DSS Incendiary Grenades (12)`
   card; global Encounters/New Rules/New Mythos/New Spell order; Devourer and
   Reliquae statblocks with PDF-backed `Cursed Plague Zombies` and invisible
   Infection anchor; Plots/Prologue art ownership; p106/107 full-page map and
   exactly six p111--122 pregen pairs.
4. No broad lexical false positive was materialized, no real repeated panel or
   table was rejected, and callout termination cannot swallow following prose.
5. OUT-008 and ENH-001 remain nonblocking deferrals; no Step 8A binary choice
   or post-MASTER_EN work is embedded.

The critic must inspect actual ledger records and source, not accept receipts at
face value. Findings must include exact file/unit/page/line evidence and priority.

## Owned output

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_boundary_ledgers_review_20260903.md`

Success token: `APPROVED_VIRAL_BOUNDARY_LEDGERS_FOR_V2_CONFIG` only if no P0/P1
or blocking coverage/semantic issue remains. Otherwise return
`CHANGES_REQUIRED_VIRAL_BOUNDARY_LEDGERS` with a bounded remediation list.
