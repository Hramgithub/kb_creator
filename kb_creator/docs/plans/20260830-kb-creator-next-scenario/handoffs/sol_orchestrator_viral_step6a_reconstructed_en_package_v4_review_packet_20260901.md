# Viral Step 6A reconstructed English package v4 independent review packet

Date: 2026-09-01  
Required reviewer: independent `gpt-5.5` at `high`  
Review type: reconstruction acceptance, not product release  
Working directory: `D:\NRI\.worktrees\kb-creator-viral`

## Decision requested

Issue one fresh independent decision on whether the immutable Viral v4 package
may replace v3 as the accepted Step 6 reconstructed-English input for Step 7
MASTER_EN publication. Use one verdict:

- `accept_reconstruction_candidate`, or
- `reject_reconstruction_candidate`.

Classify every finding P0/P1/P2/P3. Acceptance requires no unresolved finding
that makes the reconstruction text, provenance, assets, overlay or package
identity unsafe as the publication input.

This is not a MASTER_EN acceptance, user reading acceptance, translation,
HTML/PDF acceptance, production promotion or final release decision.

## Why v4 exists

The previously accepted frozen v3 remains immutable historical evidence, but
Step 7 source reconnaissance proved that its AI decision Markdown altered
already selected correct raw evidence and omitted source facts. V4 is a minimal
successor: no MinerU/OCR rerun, no new extraction and no 371/119/490 matrix.

The 124 v4 decisions differ from v3 on exactly
`{20,34,42,44,45,49,50,55,62,65,66,67,69,74,75,80}`. The other 108 decisions
are byte-identical. Required closures include:

- p20 full systematic lowercase `l -> e` corruption repair and complete Rumors;
- p44 full systematic `H/h -> a` repair;
- p34/p55/p62 source tables;
- p65/p66 characteristics/statblocks and p67 infection tables;
- exact printed forms on p42/p45/p49/p50/p62/p65;
- dropped source titles on p69/p74/p75;
- exact source-visual p80 handwritten note ending `Babez` with source-intended
  stylized final `z`.

Source-authorial suspicious wording identified by the content audits must remain
unchanged. In particular, do not treat p75 `upshot of us` / `a millions`, p84
`Marcus`, p85 `SATANSIST`, p104 `It's specific/actual`, p120 `ties up`, p62
`Hastaÿk's corruption` or p65 `Hasalÿk` as defects merely because they look odd.

Page 124's clean full-page retained-visual back-cover asset is deliberately not
part of reconstruction v4. The accepted Step 7 architecture assigns its
deterministic render from the clean source PDF to the MASTER_EN builder. Confirm
that this known publication requirement does not get silently waived, but do
not reject reconstruction solely because v4 did not create that downstream
reader asset.

## Immutable authorities and identities

| Evidence | Identity |
|---|---|
| source PDF `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf` | 20,718,150 bytes; SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`; 124 pages |
| contract `kb_creator/contracts/viral.json` | 4,582 bytes; SHA-256 `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D` |
| Step 7 architecture packet | 43,067 bytes; SHA-256 `36B20416AEF0D7B7031859DAC119D65D99B61F0CA10C25CB44C34B0F23036117` |
| pages 001-068 content audit | 24,271 bytes; SHA-256 `BB2E623E02AC3941C9E7C14042C74415D7030A8767049416AF403F50FF243D20` |
| pages 069-124 content audit | 29,809 bytes; SHA-256 `DB030439C6B38DE192C3AE83647139FD4A7DBBBF7EBD1BB16409CAC37FD55242` |
| pages 001-068 v4 correction receipt | 9,947 bytes; SHA-256 `E04FD7310A4B30D901CDB648890E4AE3488ED2FBFE5E5EFF48BF7A3F9102D48D` |
| pages 069-124 v4 correction receipt | 7,620 bytes; SHA-256 `D783114736A20DD2589B52E4666B0CCB2377FD4E91D41DEF8B5C9A1D2134FDA2` |
| v4 decisions inventory | 124 JSON; 10,401 inventory bytes; SHA-256 `0213B2F046A76BE0BAF80F83FEF9D3AFC5180F61152DDCCEFCA8098E5F36C763` |
| reviewed fidelity allowlist | 417 bytes; SHA-256 `D84CB591732F2396DAE65E0B4A2C749E1E7E6EDC492E9144026013B8CEB649BF` |
| fidelity auditor | 10,560 bytes; SHA-256 `E5BDE87435D19EAD63FB4D5BAC2CCE1E4FE139B00B97FA6110CF5880EA5D0A08` |
| execution assignment | 6,195 bytes; SHA-256 `6835D8003C373B576E4372AB14C4D90330F1A92F61D14D2D36320D7795AE30F4` |
| Luna/high execution QA receipt | 9,335 bytes; SHA-256 `9718B8009A912E6FC6A033DAB119703A6905BA56F0EF646436B9A9F3A659F145` |

Candidate root:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v4`

- 373 files / 13,152,378 bytes;
- portable ordinal inventory SHA-256
  `EBC5135C61EA0D795D1A879B74B7B6E6127AFDE6406BC520059F997FB316A2E6`;
- `RECONSTRUCTED_EN.md` 348,578 bytes / SHA-256
  `243D7258599F038B2C512B675619B1312461EA4CEC97BC2B3E30A5C95C1917BE`;
- 124 pages, 124 decisions and 121 closed assets.

Package root:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`

- 377 files / 41,079,424 bytes;
- portable ordinal inventory SHA-256
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`;
- 373/373 candidate paths byte-identical and exactly four finalizer outputs;
- `RECONSTRUCTION_PROVENANCE.json` 229,628 bytes / SHA-256
  `0B958506A76A1CB152A0D935A4A78DF0326AE24C5BFEDDC8B59D5434BB9A8460`;
- `RECONSTRUCTION_QA.json` 643 bytes / SHA-256
  `F88E0474D19982B0634AE66DB7A10F865EA3EDB1DB491AF55E6E3CC5F03EDCC0`;
- `RECONSTRUCTION_QA.md` 206 bytes / SHA-256
  `162039F13D25D3E25B7D2C60B20845F615425AAE95CF1A8F869025C586195851`;
- `SELECTED_OVERLAY.pdf` 27,696,569 bytes / SHA-256
  `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB`.

The orchestrator independently reproduced both portable ordinal inventory
hashes, the QA receipt hash, exact repaired strings, overlay identity and the
seven `status: pass` / empty-error gates after Luna's PASS. Focused tests were
`62 passed in 9.87s`; focused fidelity was 124 pages, zero errors, pass.

## Required independent checks

1. Recheck every authority/input/output identity above before relying on it.
2. Confirm exact v3-to-v4 changed set 16 and 108 byte-identical decisions.
3. Trace every changed page to selected/frozen raw blocks, direct source visual
   evidence or exact content-audit fact ledger; confirm no silent copyediting.
4. Specifically inspect source visuals/raw evidence for p20, p44 and stylized
   p80 `Babez`; inspect p62 `Hastalÿk`/`Hastaÿk`, p65 `Hasalÿk`, and the three
   admitted source titles.
5. Recheck complete source facts for p34, p55, p62, p65, p66 and p67 rather than
   merely searching for table headings.
6. Confirm 124 page markers/order, decision identity, selected-ref resolution,
   provenance roles, 41 physical handout identities and ordinal 1..39 closure,
   asset closure, unresolved/placeholder absence and all seven QA gates.
7. Confirm candidate/package inheritance, closed package-only inventory and
   overlay source/geometry/hash identity. Overlay remains evidence, not a future
   reader asset.
8. Reassess the sole reviewed p62 `ý -> ÿ` count-7 fidelity allowlist for exact
   scope and source evidence; reject any broader or unused exception.
9. Confirm the v4 acceptance boundary leaves the exact p124 clean-source render,
   semantic navigation, handout placement, table presentation and reader-noise
   transformations for Step 7 without hiding a reconstruction defect.
10. Report exact findings and residual risks. Do not infer release acceptance
    from green automated checks.

## Write scope and forbidden actions

Only this new review receipt may be written:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstructed_en_package_v4_review_20260901.md`

All source, contract, three-view/bundle roots, decisions, allowlist, v1-v4
candidates/packages, code/tests, plan/context, accepted/production artifacts and
Git are read-only. No build, materializer/finalizer, MinerU/OCR, test suite,
cleanup, mutation, p124 render, MASTER_EN work, commit or push is authorized.

The receipt must record reviewer role/effort, exact inspected identities,
method, evidence per finding, P0/P1/P2/P3 summary, verdict, remaining Step 7
requirements, files changed and detached bytes/SHA-256.

