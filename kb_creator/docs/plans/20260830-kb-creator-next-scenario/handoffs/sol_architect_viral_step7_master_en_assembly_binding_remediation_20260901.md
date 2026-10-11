# Viral Step 7 MASTER_EN assembly-binding remediation

## Immutable architecture receipt

- Verdict: **`READY_FOR_BOUNDED_AMENDMENT`**.
- Goal / step: `20260830-kb-creator-next-scenario`, Step 7, deterministic `MASTER_EN` assembly binding.
- Assignment: `/root/viral_step7_master_en_assembly_binding_architecture`.
- Assignment state: `complete_as_architecture`; the bounded config amendment and Terra Phase C remain unstarted.
- Role / effort: NRI architecture and root-cause role, `gpt-5.6-sol` / `high`.
- Orchestrator and policy owner: `/root`, NRI orchestrator (`gpt-5.6-sol`, `medium`). Orchestration ownership did not transfer.
- Scoped override: this role could write only this receipt. Config, source, accepted reconstruction, code, tests, canonical plan/context/status, candidates, release artifacts, Git and every downstream surface remained read-only.
- Scope performed: audited all `168` hierarchy rows against all `124` accepted-v4 page Markdown files; reconciled hierarchy, source-disposition, xref, handout, structured-content and asset ownership declarations; inspected the current Phase A/B builder and verifier; specified the smallest closed binding amendment and Phase C acceptance contract.
- Result: the accepted v4 source is sufficient and no new OCR/reconstruction or user editorial decision is required. The current 13-top-level-key config is **not executable for semantic assembly as authored** because hierarchy rows do not bind target anchors to source insertion points/spans. A bounded content/config amendment must precede Terra Phase C.
- Files changed: only this receipt.
- Timestamp: `2026-09-01T20:03:44+03:00` (`Europe/Moscow`).
- Elapsed time: approximately 55 minutes.
- Token use: unavailable; exact role-level accounting was not exposed.
- Receipt identity: detached byte count and SHA-256 must be captured after the final write and reported to the orchestrator; the file cannot contain its own final whole-file digest.

## 1. Evidence and reproduced baseline

Pinned identities matched live read-only inspection:

- publication config: `630,533` bytes, SHA-256 `9B915863B058EA0DF73203E63FD338394159E9922AF4B21D5168FBE2E82DBADE`;
- accepted-v4 portable inventory: SHA-256 `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`;
- accepted-v4 page files: exactly `124`, `page-001.md` through `page-124.md`;
- current Phase B builder: SHA-256 `DAD518523ADAC39365E0D368966C4C7D112EC3EF3B3344146706F431EE96DD2F`;
- Phase B receipt: SHA-256 `8DBCCDA8E9B378BB6E2A9C53B1E36A8E03A2084C4A8A9F9EFAEB7786E007434A`.

The 124 pages contain `207` Markdown headings on `75` pages (`66` H1 and `141` H2). The sealed audit result reproduces exactly: `20/168` hierarchy titles have one case-sensitive exact Markdown-heading match on their declared pages; `148/168` have none. A global audit across all 124 pages finds `25` hierarchy rows with an exact Markdown-heading title somewhere; after assigning `viral-contents` to generated navigation and `viral-keeper-map-secret-underground` to its owned map unit, `23` are exact-heading bindings.

The zero-match population is not one defect class. It includes case-only changes (`Viral` / `VIRAL`, `Warning` / `WARNING`), reader labels that remove source qualifiers, source labels whose line also contains body text, plain non-Markdown labels, physical handout markers, page-owned visual units, generated containers and real source-page declaration drift. Therefore fuzzy title matching or placing all unmatched anchors at page start would be nondeterministic and would duplicate or reorder source content.

## 2. Complete 168-anchor binding classification

This is a mutually exclusive current-state partition. Counts sum to `168`.

| Binding class | Count | Deterministic interpretation |
|---|---:|---|
| `generated_container_or_toc` | 3 | `viral-contents`, `viral-pregenerated-investigators`, and `viral-appendix-new-mythos-tome`; emit structure/navigation from reviewed config and consume no free source span. |
| `exact_markdown_heading` | 23 | Bind to a page-qualified, occurrence-qualified exact Markdown heading. Five are exact globally but currently outside their declared pages and require data correction. |
| `normalized_or_explicit_source_locator` | 79 | Bind through an explicitly recorded source label/alias/prefix/structured selector, never runtime normalization. This class includes `26` hospital room prefixes whose source line also carries body text, the three structured locator roles (`Cold Spot`, `Taint Levels`, `Infection`), shortened/expanded location labels, character qualifiers and plain-text headings. |
| `page_or_section_start` | 1 | `viral-opening-message` starts at the first retained lexical block on p3 because the source has no heading label. |
| `physical_handout_deterministic` | 37 | A page-qualified physical label/title boundary already separates the unit. Marker position may be before or after the body and is declared, not guessed. |
| `owned_page_unit` | 21 | Front/back covers `2`, Keeper-map units `6`, pregen/template units `12`, and merchandise/QR `1`; content and assets are closed by the unit owner, with semantic text retained where declared. |
| `ambiguous_shared_handout_prefix` | 4 | `viral-handout-04`, `viral-handout-05`, `viral-handout-06`, `viral-handout-07` on two multi-handout pages require one explicit owner for the shared page heading. |

Physical handouts therefore total exactly `41 = 37 + 4`. The four pre-amendment ambiguous rows are a binding-ownership ambiguity, not a source-fact ambiguity:

- p74 has shared source heading `Marco's Emails` before the markers for Handouts 4 and 5;
- p75 has shared source heading `Maya's Emails (1 of 2)` before the markers for Handouts 6 and 7.

The bounded amendment resolves them without user choice: the shared p74 prefix is retained once under `viral-handout-04`, and the shared p75 prefix once under `viral-handout-06`; Handouts 5 and 7 begin at their own markers. Post-amendment unresolved ambiguous-row count must be `0`. Other multi-handout pages have explicit ordered title/marker boundaries: p78, p93, p100 and p101. Page 107 is not an orphan; it is an ordered continuation of the p106 map unit.

## 3. P0 / P1 / P2 findings

### P0

None. No candidate exists and no source/config/code mutation was performed by this role.

### P1-1 — missing executable source binding

The current hierarchy row is closed to:

`level / title / anchor / parent_anchor / source_pages / toc_entry / semantic_role`.

Neither it nor `source_disposition` declares the exact insertion point, replacement rule, continuation ownership or multi-unit boundary. Phase A validates page/anchor membership only. Phase B materializes assets only. Phase C cannot lawfully infer Viral-specific fuzzy selectors.

### P1-2 — declared-page evidence is not reliable as a locator

Global source-line inspection proves `25` target starts outside their current `hierarchy.source_pages` declaration:

- investigator/body boundaries: `viral-creating-new-investigators`, `viral-spektral-krew-gear`, `viral-history`, `viral-one-night-in-perla`, `viral-epilogue`, and the Peter, Ku Hyeon, Maya and Emily profile anchors;
- Keeper's Secrets children: `viral-isola-number-of-sessions`, `viral-isola-plots-and-schemes`;
- scenario locations/end transition: locations 3, 4 and 6 through 13, `viral-isola-hastalyk-awakens`, and `viral-epilogue-rewards`;
- appendix boundary: `viral-appendix-new-rules` and `viral-appendix-new-rules-the-sight`.

Examples: `Creating New Investigators` is declared on p14 but appears on p12; `One Night in Perla` is declared on p18-25 but begins on p17; location 13 and `Hastalÿk Awakens` are declared on p52 but begin on p49; `New Rules` and `The Sight` are declared from p61 but begin on p60. Adding selectors without correcting these rows would merely hide the existing data error. The amendment must reconcile each locator page with both `hierarchy.source_pages` and the corresponding `source_disposition.target_anchors` ownership.

### P1-3 — four non-inferable shared-prefix rows

The p74/p75 shared headings cannot be assigned by nearest-marker heuristics without either dropping or duplicating lexical content. The explicit ownership decision in section 2 is binding.

### P2-1 — Phase C and independent candidate verification are absent

`build_scenario_master_en.py` still refuses normal mode with `implementation_phase_incomplete`; it has no Markdown assembly path. `verify_scenario_master_en.py` process-delegates Phase A preflight and deliberately has no candidate verifier. This is correct fail-closed behavior, but Phase C must not be dispatched until the amended config is frozen and preflight validates its new bindings.

## 4. Minimal closed schema amendment

The current 13 top-level keys remain unchanged. Add exactly one required closed member, `assembly_binding`, to every `hierarchy[]` row. Do not add a parallel selector matrix or a second top-level framework.

Exact row shape:

```json
{
  "level": 3,
  "title": "Example reader title",
  "anchor": "viral-example",
  "parent_anchor": "viral-parent",
  "source_pages": [42],
  "toc_entry": true,
  "semantic_role": "room",
  "assembly_binding": {
    "kind": "source_locator",
    "order": 73,
    "locators": [
      {
        "page": 42,
        "selector_kind": "line_prefix",
        "selector": "1N. East Corridor –",
        "occurrence": 1,
        "action": "replace_label_retain_remainder"
      }
    ],
    "continuation_pages": [],
    "unit_ref": null,
    "shared_prefix_owner": null
  }
}
```

Closed enums and invariants:

- `kind`: exactly `generated`, `source_locator`, `physical_unit`, or `owned_page_unit`;
- `order`: unique integer set `1..168`, representing reader/preorder assembly; hierarchy array order is not itself an assembly order;
- `selector_kind`: exactly `page_start`, `line_exact`, `line_prefix`, `markdown_heading_exact`, `markdown_heading_normalized`, `handout_marker`, or `structured_unit`;
- `action`: exactly `insert_before`, `replace_heading`, `replace_label_retain_remainder`, `retain_under_anchor`, or `consume_continuation_label`;
- `selector` is a string for all selectors except `page_start`, where it is `null`; `occurrence` is a positive integer and the page-qualified selector must match exactly once;
- `continuation_pages` is ordered, unique and disjoint from start locators; a continuation remains under the same anchor until the next declared start locator;
- `unit_ref` is `null` for generated/source locators and an exact existing handout/asset/structured owner identity for unit kinds;
- `shared_prefix_owner` is normally `null`; only the four p74/p75 rows may participate, with the owner values fixed in section 2;
- `generated` has no locators and consumes no source blocks; every non-generated row has at least one locator or a resolvable `unit_ref`;
- runtime case-folding, substring search, edit distance, fallback-to-page-start, and selector permutations are forbidden. `markdown_heading_normalized` records a reviewed exact source string plus its intended target label; it does not authorize generic normalization at runtime.

The bounded content amendment must also correct the 25 proven start-page mismatches and any affected page target ownership. It may not edit accepted-v4 Markdown or lexical content.

## 5. Assembly, continuation and conservation behavior

1. Parse each pinned page into ordered lexical/asset blocks after recognizing the source-page comment as technical provenance, not reader content.
2. Validate all locators before creating a target. A zero-match, multi-match, wrong-page, overlapping-owner, unowned-block or duplicate-block result is fatal.
3. Sort by `assembly_binding.order`. Source locators establish boundaries; a span ends immediately before the next start locator on that page, or at page EOF. Continuation pages append in listed order. Continuation labels may be consumed structurally, but their body remains byte/lexeme conserved.
4. Parent containers may own only the introductory blocks before the first child locator. They must not reconsume child spans. Generated parents consume nothing.
5. A source heading/label may be replaced by the reviewed reader heading and explicit anchor. When a room label shares a line with prose, only the declared prefix is replaced and the remainder is retained exactly.
6. Physical handouts are emitted in source order `1,2a,2b,3a,3b,4..39`. Multi-unit pages use explicit boundaries; no whole-page copy is permitted for more than one unit. Shared p74/p75 headings appear once under the fixed owner.
7. p106 then p107 is one map unit with placement indices 1 then 2. It is not two headings or two owners.
8. Every accepted-v4 lexical block must have exactly one disposition: visible under one anchor, transformed by an already authorized structural operation, or classified as technical/evidence-only by the existing closed policies. With current exceptions, source-content suppression remains zero.
9. Body lexical values, table cells, statblock facts, authorial oddities and asset bytes are never silently edited. Heading normalization, generated navigation, link wrapping and relocation are recorded in provenance; source text is not recovered from the PDF as a fallback.

## 6. Compact Phase C tests and real-candidate evidence

Do not restore the historical 371/119/490 selector-permutation matrix. Use one or a few representative tests per invariant class:

1. closed schema: missing/unknown binding keys, bad enums, duplicate/missing order, unresolved `unit_ref`;
2. selector exactness: zero/multiple match and forbidden fuzzy/page-start fallback;
3. declared-page reconciliation: fixtures for p12/p14, p17/p18, p49/p52 and p60/p61 drift;
4. prefix retention: p42 `1N`/`1O` label replacement retains the prose after the dash byte-for-byte;
5. continuation: Rumors/Signs pages 20-22 and map pages 106-107;
6. multi-unit pages: p74/p75 shared-prefix ownership, marker-last p87-93, and p93/p100/p101 multiple units;
7. generated containers: no source consumption or duplicate body;
8. conservation ledger: every accepted lexical/asset unit accounted exactly once, zero unauthorized suppression, zero body lexical delta;
9. hierarchy/navigation: one H1, 168 unique bound anchors, generated TOC and all internal links resolve;
10. independent verifier: it must parse candidate outputs without importing/calling builder implementation and reject an acceptance file, extra output, modified sidecar or forged pass.

After implementation is independently accepted, the real Viral candidate gate requires two fresh builds from the same pinned inputs into two new empty targets. Their closed inventories and every file byte must match; the independent verifier must pass both; counts must remain 168 anchors, 124 source pages, 41 physical handouts, six map units covering seven pages, 12 pregen/template units, 29 structured units and 123 assets; source lexical suppression and unowned/duplicate blocks must be zero. Full visual QA, independent `gpt-5.5` release review and explicit user reading acceptance remain separate pending gates. This receipt does **not** authorize a real candidate build.

## 7. Next owner and exact write scope

The immediate next owner is a bounded `gpt-5.6-sol` / `high` content-config pass under `/root` orchestration. Its write scope is only:

1. `kb_creator/working/viral/master_en/publication_config_v1.json` — add the 168 closed bindings, correct the proven source-page/target ownership data, and make no other policy/content change;
2. one new immutable amendment receipt assigned by the orchestrator.

All source, accepted v4, code/tests, candidate/output, canonical plan/context/status, release and Git surfaces remain read-only for that pass. Acceptance criteria are exact 168-row classification/order closure, zero locator ambiguity, zero locator/page/ownership mismatch, zero unowned or duplicate source block in a read-only binding audit, and a new config byte/SHA identity.

Only after that immutable amendment is captured may Terra/medium receive a separate Phase C engineering assignment limited to the existing builder, independent verifier, focused tests and its receipt. Candidate execution remains a later separately authorized bounded step.

## 8. Assumptions and blockers

- Accepted v4 and its 124 page files remain immutable and are the sole lexical source.
- Existing handout, structured-content and asset owner identities remain authoritative except for the binding/page corrections explicitly required above.
- The p74/p75 shared-prefix decision is structural ownership, not an editorial rewrite.
- No material user decision is required.

Blocker to Terra Phase C: the config amendment is not yet written or frozen. There is no blocker to performing that bounded amendment.
