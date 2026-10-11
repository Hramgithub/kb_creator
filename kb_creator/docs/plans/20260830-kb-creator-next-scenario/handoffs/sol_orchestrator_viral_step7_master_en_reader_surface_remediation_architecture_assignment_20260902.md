# Viral Step 7 MASTER_EN reader-surface remediation architecture assignment

- Role: Sol/high root-cause and remediation architecture.
- Trigger: independent GPT-5.5/high release review rejected frozen candidate A.
- Scope: define the smallest reusable config/builder/test remediation that
  closes the reader-surface defects exhaustively.
- Do not implement, edit the candidate, or reopen accepted reconstruction.

## Frozen evidence

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Rejected candidate A root:
  `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a`
- Candidate inventory identity:
  `37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421`
- `INVENTORY.json` SHA-256:
  `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8`
- `MASTER_EN.md` SHA-256:
  `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`
- Publication config SHA-256:
  `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- Accepted reconstruction inventory SHA-256:
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`
- Independent reject receipt SHA-256:
  `FBE15693C3CAD6FE5B5E7F01DF79E031C5B48180E563F24B63B585D1D5D42678`
- Full visual-QA resume receipt SHA-256:
  `1B076F39877310F425829F3E8B4CB0E554415B1D46112F5F4D18E0DCF9D8FD23`

The independent verifier passed mechanically, but the critic found:

1. P1 semantic ownership drift at Corrina, Ku Hyeon, Emily, Creating New
   Investigators, Beggar's Cove, Administrator's Office and Boiler Room;
2. P2 plain generated-looking image-description paragraphs and provenance-style
   `Scenario illustration owned by ...` alt labels;
3. P2 duplicate/global-level headings inside Keeper maps, pregens, merchandise
   and back cover.

The orchestrator independently confirmed every representative locus in
`MASTER_EN.md` and found that accepted reconstructed pages intentionally contain
cross-page continuation text; the publication binding currently assigns page
prefixes to the next semantic anchor.

## Required analysis

Read the full critic receipt and inspect current candidate, accepted v4 pages,
publication config, builder, focused builder/verifier tests and provenance.

### A. Exhaustive semantic seam audit

Do not stop at the seven examples. Audit all 168 publication units and every
multi-page/page-start continuation for reader-anchor ownership. Produce an exact
table for every confirmed misowned prefix/suffix with:

- current owner anchor and correct owner anchor;
- source page plus exact start/end selector text;
- current candidate line/range;
- required fragment split/order;
- affected xref, structured, note and asset bindings;
- whether config-only or builder support is needed.

Preserve every accepted source-visible word exactly once unless it is separately
classified as authorized technical reader noise. Accepted reconstruction v4,
source PDF and reconstruction decisions are immutable.

### B. Reader-noise and alt-text audit

Enumerate every plain image-description/provenance artifact in the complete
reader, not just four examples. Distinguish source-authored prose/captions from
AI/extraction descriptions. Define exact config-authored authorized suppression
or relocation for each noise block so conservation remains closed.

Audit all 107 reader-image alt labels. Specify deterministic descriptive alt text
from existing asset/page/owner semantics and forbid provenance phrases such as
`owned by`, generic `scenario illustration`, hashes, page numbers or tooling.

### C. Heading hierarchy audit

Enumerate every heading inside all 168 owner regions. Define a closed local
hierarchy contract: generated group/anchor headings retain their intended level;
source headings are preserved as subordinate headings or non-heading labels and
may not create duplicate/global H2 navigation. Include maps, pregens, merchandise,
back cover and any additional affected unit.

### D. Minimal reusable remediation

Specify exact config schema/data changes, builder behavior and focused tests.
Prefer existing generic fragment/transform machinery; add code only where the
current schema cannot express a closed rule. The remediation must fail closed on:

- misowned page-prefix or page-suffix fragments;
- unknown/open nested keys;
- missing/duplicate/out-of-order semantic content;
- reader-noise leakage;
- provenance-style or empty alt text;
- heading levels outside the owner-local contract.

Define content-aware tests that would have rejected candidate A and cover the
generic behavior with compact fixtures. Do not propose per-selector mutation
matrices or revive historical 371/119/490.

### E. Invalidation and rerun boundary

State exactly which prior gates become stale when config/builder changes, the
smallest compact test/review sequence, and the new absent candidate name. Preserve
candidate A/B as rejected evidence. Decide whether the existing 27/39/p80 visual
inspection may be carried forward by exact asset-manifest byte identity or must
be repeated, and justify the answer. Explicit user reading acceptance remains
pending and MASTER_RU remains closed.

## Allowed write

Write exactly one architecture receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md`

All other files, including source/reconstruction, config, code/tests, candidate,
bundles, plan/context, prior receipts, Git and downstream outputs are read-only.

## Verdict

Return one:

- `READY_FOR_BOUNDED_REMEDIATION` with exact tables/schema/tests/rerun order;
- `NEEDS_USER_DECISION` only for a genuine source-semantic ambiguity with exact
  alternatives and evidence;
- `BLOCKED` only when required current evidence is inaccessible.

No acceptance, implementation, build, MinerU, mutation matrix, Git mutation,
cleanup, MASTER_RU, HTML, PDF or production action is authorized.
