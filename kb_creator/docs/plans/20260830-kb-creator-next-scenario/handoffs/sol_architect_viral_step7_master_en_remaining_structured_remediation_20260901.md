# Step 7 remaining structured remediation receipt

- Timestamp: 2026-09-01 (Europe/Moscow)
- Role: `gpt-5.6-sol` architecture/remediation at high reasoning
- Orchestrator policy owner: parent `/root`; ownership not transferred
- Assignment state: bounded config amendment complete; one executor-owned blocker remains
- Scoped override: writes limited to current `publication_config_v1.json` and this receipt; builder/tests/source/v4/verifier/candidate/plan/context/Git/release surfaces remained read-only
- Result: `BLOCKED`

## Seven audited causes

1. `viral-structure-reliquae-and-infections`: the declared 20-token sequence is present exactly once and globally ordered across immutable p066+p067 (positions `1319,1707,1716,1725,1734,1743,1752,1761,1769,1776,1793,1803,2329,2338,2438,2490,2502,2716,2799,2818`). The unchanged executor instead validates the complete sequence independently against each of four region bodies, so p066 necessarily lacks p067 `ATTACKS` and raises `structured token order mismatch`. This is executor-owned; deleting/reducing tokens or folding regions would weaken order/ownership and was rejected.
2. Marco p112: exact heading exists, but `viral-pregen-marco-background` was `owned_page_unit`, which deliberately produces no `source_span_hashes`; structured resolution therefore saw zero eligible spans.
3. Corrina p114: same mismatch.
4. Enoch p116: same mismatch.
5. Peter p118: same mismatch.
6. Ku Hyeon p120: same mismatch.
7. Blank template p122: same mismatch.

## Config corrections

For each of the six hybrid background owners, changed only its assembly binding from `owned_page_unit` to `source_locator`, set `unit_ref` to null, and added one exact `markdown_heading_exact` / `replace_heading` locator using the already-declared structured start heading. Existing reader assets, ordinary/structured visual-review units, hierarchy order, source page, structured declaration, lexical protections, and source disposition remain unchanged.

Resolved exact spans:

- p112 `[26,2929)`, SHA-256 `BFFF09167630AD0543DC103DB2135BF7FFC38C29A77E3C90894262E8670124C5`
- p114 `[26,2802)`, SHA-256 `47EDF96D75303224B521775B70AA155DCE07144900C965A7E852AF3980D2DFBF`
- p116 `[26,2733)`, SHA-256 `6438100D1752E91A8112D782A20FF24D96B93FCEA34236E95D0878844CC13733`
- p118 `[26,2877)`, SHA-256 `7D5F62B4F5ED1BCF75717D80DC21339F2438356E89964F5194DF9C54220E7246`
- p120 `[26,2518)`, SHA-256 `941F688FEA11E1BCB47302FE2F9BD2D4F5E62F4EB0F728E421F426F89EB9A6AC`
- p122 `[26,1322)`, SHA-256 `3541D6D592A8236227641A6FE0E6ACA67EC494773D78528FBF7FC255CC7DB4B2`

## Identity and verification

- Config before this batch: 659,036 bytes; SHA-256 `6684DF90F19C200E1AABD511E23199973B3B6C1C567F20422788CAE35B42B652`
- Config after: 660,329 bytes; SHA-256 `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- Canonical structured subtree unchanged: 43,110 bytes; SHA-256 `465D65FD7AF94323CCBDCFC5E3C3B95CC6440C3A9340BC7EFC46E8DA98EBE5DA`
- Schema: all 29 declarations valid; classes remain 11 tables / 10 cards / 2 statblocks / 6 visual forms.
- Binding resolver: 223 exact locators; ledger unchanged at 1,935 total / 1,862 owned / 73 generated / 0 unowned / 0 duplicate / 0 unauthorized suppression.
- Xrefs: unchanged 41 exact rows / 42 ordered segments.
- Isolated structured execution: 28/29 pass; all six corrected pregen rows pass. The sole failure is the executor-owned multi-region Reliquae token validation above.
- Preserved inventory: 168 hierarchy anchors, 124 source dispositions, 237 xrefs, 123 assets, 91 visual-review units.

## Required next action

Next owner is bounded reusable-code engineering. In `structured_resolver`, retain exact per-region owner/start/termination/table validation and fragment hashes, but evaluate `ordered_literal_tokens` once against the concatenation of resolved region bodies in declaration order after the region loop. Do not normalize text, search outside owner spans, reorder regions, or relax missing/duplicate token failure. Acceptance: unchanged config yields 29/29 evidence, the Reliquae global positions above remain strictly ordered, and binding ledger plus 41/42 xrefs remain unchanged. No candidate or release decision is authorized here.

## Files and accounting

- Changed: `kb_creator/working/viral/master_en/publication_config_v1.json`
- Created: this receipt
- Checked read-only: fresh Plague Monk receipt, current builder resolver, seven structured declarations, immutable accepted pages 066/067/112/114/116/118/120/122, binding/xref/visual contracts
- Blocker: executor-local multi-region ordered-token validation only
- Elapsed time: approximately 19 minutes
- Token use: unavailable
