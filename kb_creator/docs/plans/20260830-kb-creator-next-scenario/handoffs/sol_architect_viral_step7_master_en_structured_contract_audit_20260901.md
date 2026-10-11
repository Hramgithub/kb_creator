# Viral Step 7 MASTER_EN structured-content executable-contract audit

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `7 / C2a structured-content executable contract`
- Timestamp: `2026-09-01T21:18:00+03:00`
- Role: NRI architecture/root-cause analysis
- Requested model / effort: `gpt-5.6-sol` / `high`
- Actual platform model / effort: `unavailable`
- Orchestrator policy owner: `/root`, NRI main-chat `gpt-5.6-sol` / repository-policy `medium`; ownership did not transfer
- Assignment state: `matched` to the architecture role; platform runtime remains `unavailable`
- Scoped override: `none`
- Result: `READY_FOR_BOUNDED_AMENDMENT`
- Elapsed time: approximately `00:38:00`
- Token use: `unavailable`

## Scope and result

This was the assigned read-only audit of all 29 `structured_content` rows against
the accepted Step 6 v4 Markdown, resolved assembly bindings, declared assets and
visual-review rows. No config, source/v4 package, builder, verifier, test,
candidate/output, plan/context/status, MinerU or Git surface was intentionally
modified. No candidate was created.

The current ledger is inventory/placement evidence, not an executable structure
contract. Only the `viral-structure-signs-and-portents` fact values are already
exact enough at the header/key level; even that row lacks executable region and
continuation selectors. The remaining semantic rows contain wrong, incomplete,
ambiguous or unsupported aliases. The six visual-form rows have correct owned
reader assets, but the exactly-once/no-semantic-duplicate rule is not enforced.

No accepted-v4 reconstruction defect requiring Step 6 reopening was found.
The observed lexical oddities are source-faithful and must be protected. The
smallest safe next step is a bounded publication-config amendment, followed by
a C2a-only Terra implementation in the existing builder and builder test.

## Pinned identity and read-only evidence

- Assignment: 5,045 bytes, SHA-256
  `D7271C67B669840B6CE2E3CA7CDD65E36BAAB8E1F7429F68BB04C4B6FD041455`.
- Accepted v4 package inventory: SHA-256
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Current builder: SHA-256
  `3D84DA82F31CCADAA8EFA831C21CB12DD7C35232A4B7F90E6B6BC215C8009CEE`.
- Baseline whole publication config before the concurrent xref correction:
  717,058 bytes, SHA-256
  `314058BEC330D16CC26B4D1D5E3DA07E3C98AFF8B3820AF5ECE2644648FE5D0E`.
- Completed xref-only successor publication config: 741,991 bytes, SHA-256
  `5391A55C2ABEB0835F3526BE6F6CD06334A9001DD3B00B168EDF4BB18A20A0BA`.
  Its xref correction receipt is 8,965 bytes, SHA-256
  `72145F9055E1CC042D0BBB56A3AE15B0531B577CE134055D57807988A50E6DEA`.
- Canonical `structured_content` subtree after that xref-only change: 135,802
  canonical bytes, SHA-256
  `84E740194388A568144FE97E4098855A2F868174D9865DBAAF5C1252E18AE5F2`.
  This exactly matches the assignment pin; the concurrent whole-config change
  did not alter the audited subtree.
- Existing declaration validation passed for all 29 structured rows, 123 assets
  and 91 visual-review rows. This proves current path/hash/count closure, not
  semantic executability.
- Existing strict binding resolution produced 219 locators and conservation
  `1935 total / 1862 owned / 73 generated / 0 unowned / 0 duplicate / 0
  unauthorized suppression`.
- The structured subtree contains 33 source-unit copies over 28 unique page
  files and embeds 111,158 characters of duplicated full-page Markdown. Five
  pages are duplicated twice (`021`, `055`, `059`, `066`, `067`).

## Per-row reconciliation matrix

Line numbers refer to the exact accepted-v4 files under
`working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/`.
`Pipe` means an accepted Markdown pipe table. `Series` means accepted Markdown
whose source table is preserved as exact numbered records rather than rewritten
into a pipe table. All checks below preserve the selected region byte-for-byte
apart from the already declared heading/image cleanup; none re-author row text.

| # | id / class | logical owner; pages | exact accepted-v4 region and attached note | current fact status | representation and deterministic check |
|---:|---|---|---|---|---|
| 1 | `viral-structure-rumors` / table | `viral-one-night-in-perla-rumors`; 20-21 | Pipe: p20 L23-32, header `Roll / Rumor`, keys 1-6; repeated heading/header p21 L3-27, keys 7-10. Attached preface p20 L21 begins `Note that most of these aren't true` but is currently owned by the parent Exploring block. | **Wrong:** declares `Roll / Result`; keys are right; continuation and attached preface are undeclared. | Preserve both raw pipe fragments; require one repeated-header continuation, exact keys 1-10 and source-to-emitted region hashes. |
| 2 | `viral-structure-signs-and-portents` / table | `viral-one-night-in-perla-signs-and-portents`; 21-22 | Pipe: p21 L31-67, header `Roll / Result`, keys 1-7; repeated heading/header p22 L3-23, keys 8-10. | Header/keys exact but **non-executable/incomplete:** no exact regions or continuation rule. | Resolve two fragments inside the owner, require repeated header and ordered 1-10 exactly once. |
| 3 | `viral-structure-rowing-speed-results` / table | `viral-isola-location-02-beggars-cove`; 34 | Attached intro p34 L25; pipe p34 L27-33, header `STR Roll / Result`, keys `Fumble, Failure, Success, Hard Success, Extreme Success`. | **Wrong:** declares `STR Result`, six reversed/renamed keys and a nonexistent `Critical` row. | Exact pipe parser; five rows in printed order; intro retained; evidence crop stays evidence-only. |
| 4 | `viral-structure-lemon-grove-results` / table | `viral-isola-location-04-the-lemon-grove`; 36 | Pipe p36 L3-51, header `Roll / Result`, keys 1-10; exact post-note p36 L53 `Note: Unless otherwise indicated, each of the above options requires a Sanity check (0/1).` | Header/keys exact; **note is semantic and non-executable** (`preserve general SAN note`). | Exact pipe plus exact required after-note selector; no inferred “general SAN” alias. |
| 5 | `viral-structure-dss-incendiary-grenades` / card | `viral-epilogue-expanded-ending`; 55 | p55 L17-21: heading `DSS Incendiary Grenades (12)`; one exact statline with labels `Skill:`, `Damage:`, `Range:`, `Uses per Round:`, `Malfunction:`; following `*Delivers...` distance/damage line. | **Incomplete/non-executable:** `base_range`, `uses_per_round`, `statline` and `distance-damage note` are semantic aliases; source says `Range`, not `Base Range`. | Exact start/end and ordered literal label tokens; require the exact following asterisk note; preserve raw values. |
| 6 | `viral-structure-dss-throw-results` / table | `viral-epilogue-expanded-ending`; 55 | Attached intro p55 L33; pipe p55 L35-42, header `Throw Result / Range / Result`, keys `Fumble, Failure, Normal Success, Hard Success, Extreme Success, Critical Success`; fumble explanation p55 L44 and cumulative note L46. | **Wrong:** missing `Range` column, reversed/renamed keys; note is only a semantic description. | Exact three-column pipe in printed order plus exact adjacent explanation/note selectors. |
| 7 | `viral-structure-outdoor-encounters` / table | `viral-appendix-encounters-outdoor`; 58-59 | Series: heading p58 L13, header `Roll Phenomenon Encountered` L15, records 1-9 L17-33; headerless continuation records 10-12 p59 L3-7. General encounter guidance is p58 L7-11. | **Wrong/non-executable:** declares `D12 / Encounter`; accepted form is a numbered series. **Wrong-owner seam:** records 2-9 currently emit under descendant `...outdoor-cold-spot` (legitimate declared child), but records 10-12 emit under sibling `...hospital` (not legitimate). | After binding correction, parse exact numbered records across root/declared descendant fragments and one headerless p59 continuation; reject any sibling owner. |
| 8 | `viral-structure-hospital-encounters` / table | `viral-appendix-encounters-hospital`; 59 | Series p59 L9-35; header `Roll Phenomenon Encountered`; keys 1-12. | **Wrong/non-executable:** declares `D12 / Encounter`; owner also presently consumes outdoor rows 10-12 before its heading. | After binding correction, exact series begins only at `Hospital Encounters`; 1-12 once and in order. |
| 9 | `viral-structure-catacomb-encounters` / table | `viral-appendix-encounters-catacomb`; 60 | Series p60 L3-17; header `Roll Phenomenon Encountered`; keys 1-6. | **Wrong/non-executable:** declares `D6 / Encounter`. | Exact series within owner; ordered keys 1-6; stop before `New Rules`. |
| 10 | `viral-structure-taint-levels` / table | `viral-appendix-new-rules-the-taint-levels`; 62 | Pipe p62 L15-28; header `Level / Modifiers / Effect`; keys 1-10. Source-faithful preface p62 L9 contains `Hastaÿk's corruption`. | **Wrong/incomplete:** declares singular `Modifier`; lexical note is semantic rather than an exact protection. | Exact pipe and keys; protect literal `Hastaÿk's corruption`; source table crops remain evidence-only. |
| 11 | `viral-structure-insanity-bouts-of-madness` / table | `viral-appendix-new-rules-insanity-and-bouts-of-madness`; 63 | Series p63 L3-27; intro L5; header `D10 Roll Result` L7; keys 1-10. | **Wrong/non-executable:** declares `D10 / Bout`. | Exact series, intro retained, keys 1-10 once; stop before the page image. |
| 12 | `viral-structure-paranormal-phenomena` / table | `viral-appendix-new-rules-paranormal-phenomena`; 64 | Series p64 L19-43; intro L21; header `D10 Roll Result` L23; keys 1-10. | **Wrong/non-executable:** declares `D10 / Phenomenon`. | Exact series and ordered keys; stop before the image caption at L45. |
| 13 | `viral-structure-hastalyk-devourer` / statblock | `viral-appendix-new-mythos-horrors-hastalyk`; 65 | p65 L19-67: `The Devourer`, `Aspect of Hastalÿk`; labels `STR, CON, SIZ, POW, DEX, HP, Damage Bonus, Build, Magic Points, Move`; `* Starting Stats`; sections `ATTACKS`, `SPECIAL ABILITIES`; exact labels `Attacks per round, Grab, Grab (mnvr), Dodge, Armor, Spells, Sanity Loss, Devour, Swarm of Flies`. | Concepts are source-supported but **non-executable/incomplete**; `Characteristics` is not a source token and many exact labels are omitted. | Exact region, ordered literal labels/sections and derived source/emitted region hash; protect literal source oddity `avatar of Hasalÿk`. |
| 14 | `viral-structure-plague-monk` / card | `viral-appendix-new-mythos-horrors-plague-monk`; 66 | p66 L5-13: `The Plague Monk`, `Servant of Hastalÿk` and three narrative paragraphs. Exact source sentence: `The monk has no physical abilities`. | **Unsupported/wrong:** source contains no `ATTACKS`, `SPECIAL ABILITIES`, `attacks`, `armor`, `sanity_loss` or statline. The forbidden-invention intent is correct. | Replace invented expectations with exact narrative-region selectors and a forbidden-stat-token assertion; never manufacture stats. |
| 15 | `viral-structure-reliquae-and-infections` / statblock | `viral-appendix-new-mythos-horrors-reliquae`; 66-67 | p66 L17-41 base block (`The Reliquae`; STR, CON, SIZ, DEX, INT, APP, POW, HP, Damage Bonus, Build, Move); p67 L3-19 `ATTACKS`, combat labels, `SPECIAL ABILITIES`, `Infected Flesh`; two pipes p67 L21-31 `Roll / Infection, Serious` and L32-41 `Roll / Infection, Deadly`, keys 1-8 each. | **Wrong/incomplete:** no `Plague Zombie` section or `plague_zombie_d8` exists; generic fields are non-executable. Current p67 L3-46 emits under the Infection descendant, with the ATTACKS portion caused by a page-start locator. | Correct root/child binding seam, then exact base/attack/ability/two-table fragments; reject nonexistent Plague Zombie assertions. Preserve literal source cross-reference separately. |
| 16 | `viral-structure-iuramentum-corruptionis` / card | `viral-appendix-new-mythos-tome-iuramentum-corruptionis`; 67 | p67 L47-67: heading, three description paragraphs, labels `Sanity Loss`, `Cthulhu Mythos`, `Mythos Rating`, `Study`, `Skills Gained`, `Suggested Spells`, and `* New Spell`. Prose contains exact `written in Latin`. | **Wrong/incomplete:** `language` and `description` are semantic aliases; `Skills Gained` and footnote are omitted; declared section order is reversed from source (description precedes fields). | Exact region, literal prose token and ordered field labels; source order only. |
| 17 | `viral-structure-control-reliquae` / card | `viral-appendix-new-spells-control-reliquae`; 68 | p68 L5-13: heading; one line containing exact labels `Cost:` then `Casting Time:`; three rules paragraphs. Ends before `A Few Pointers on Running Viral from Bud` at L15. | **Unsupported/ambiguous:** `effect`, `range`, `resistance`, `failure` are not exact source fields; no separate resistance/failure field exists. | Exact region/start/exclusive-end and ordered literal labels; hash raw rules prose rather than inferring fields. |
| 18 | `viral-structure-pregen-marco-front` / visual form | `viral-pregen-marco-front`; 111 | p111 L3-5: one heading and one complete-form image. | Asset identity is exact; generic visual-field list is not independently tokenized. | Require the owned full-page reader asset below exactly once, both required review rows, and no semantic row for the same owner/page. |
| 19 | `viral-structure-pregen-corrina-front` / visual form | `viral-pregen-corrina-front`; 113 | p113 L3-5, one heading/image. | Same as row 18. | Same exact-asset/no-duplicate gate. |
| 20 | `viral-structure-pregen-enoch-front` / visual form | `viral-pregen-enoch-front`; 115 | p115 L3-5, one heading/image. | Same as row 18. | Same exact-asset/no-duplicate gate. |
| 21 | `viral-structure-pregen-peter-front` / visual form | `viral-pregen-peter-front`; 117 | p117 L3-5, one heading/image. | Same as row 18. | Same exact-asset/no-duplicate gate. |
| 22 | `viral-structure-pregen-ku-hyeon-front` / visual form | `viral-pregen-ku-hyeon-front`; 119 | p119 L3-5, one heading/image. | Same as row 18. | Same exact-asset/no-duplicate gate. |
| 23 | `viral-structure-pregen-blank-front` / visual form | `viral-pregen-blank-front`; 121 | p121 L3-5, one heading/image. | Same as row 18. | Same exact-asset/no-duplicate gate. |
| 24 | `viral-structure-pregen-marco-background` / card | `viral-pregen-marco-background`; 112 | p112 L3-59. Exact sections: `Background`, `Gear and Possessions`, `Cash and Assets`, `Quick Reference Rules`, `Marco's Responsibilities`; ten exact bold background field labels. | **Incomplete/non-executable:** `equipment` is not a source section, `Cash and Assets` is omitted, and `responsibilities` omits the exact name prefix. | Exact heading/section/field sequence plus source/emitted hash; reader silhouette retained, quick-reference image stays evidence-only. |
| 25 | `viral-structure-pregen-corrina-background` / card | `viral-pregen-corrina-background`; 114 | p114 L3-58; same common sections, final `Corrina's Responsibilities`; ten exact bold background field labels. | Same incompleteness as row 24. | Exact sequence/hash for Corrina; no alias inference. |
| 26 | `viral-structure-pregen-enoch-background` / card | `viral-pregen-enoch-background`; 116 | p116 L3-58; final `Enoch's Responsibilities`; same exact common sections/fields. | Same incompleteness as row 24. | Exact sequence/hash for Enoch. |
| 27 | `viral-structure-pregen-peter-background` / card | `viral-pregen-peter-background`; 118 | p118 L3-62; final `Peter's Responsibilities`; same exact common sections/fields. | Same incompleteness as row 24. | Exact sequence/hash for Peter. |
| 28 | `viral-structure-pregen-ku-hyeon-background` / card | `viral-pregen-ku-hyeon-background`; 120 | p120 L3-62; final `Hyeon's Responsibilities`; same exact common sections/fields. Exact oddity: `a significant portion is ties up in video and audio gear.` | Same incompleteness as row 24; lexical protection is correct but must be literal. | Exact sequence/hash and literal oddity protection. |
| 29 | `viral-structure-pregen-blank-background` / card | `viral-pregen-blank-background`; 122 | p122 L3-52. Sections: `Background`, `Gear and Possessions`, `Cash and Assets`, `Quick Reference Rules`, `Fellow Investigators`; ten blank bold fields and blank spending/cash/assets labels. | **Wrong/incomplete:** `responsibilities` is unsupported; actual final section is `Fellow Investigators`; `Cash and Assets` is omitted; `equipment` is an alias. | Exact blank-template sequence/hash, two reader assets once each, quick-reference image evidence-only. |

## Visual-form identity and exactly-once closure

Each form page currently has one `reader` / `full_page` asset owned by the same
anchor as the structured row. The corresponding source Markdown has one image
reference. Each asset is used by both the ordinary pregen review row and the
structured review row; those are two evidence declarations, not permission to
emit the image twice.

| row | page | reader asset SHA-256 | bytes | dimensions |
|---|---:|---|---:|---:|
| Marco front | 111 | `74F6D8049985378C8C5CC3F846B06982DA3A39DE05975DC31880F024E649D7A6` | 475,565 | 1445x2043 |
| Corrina front | 113 | `00F35CB2535F45BFCE6B8CC61C4BBF9FD5A493F2F63995A5608F14EDFABFB782` | 469,069 | 1437x2007 |
| Enoch front | 115 | `EE6F908E8A15D1EE0F9F8A976427F1050CEEF9810642F5DDFE1D172A0189BC3C` | 476,311 | 1437x2023 |
| Peter front | 117 | `9407122D0650698A811B6096285828CF7FBE43EFE74D3476C51995EFEC9DCA01` | 468,278 | 1439x2004 |
| Ku Hyeon front | 119 | `36E2C03C86A9B35DAB62BAF48F2E1D2E4FC0F77811173CA7ACF8D7C44944D070` | 474,537 | 1439x2009 |
| Blank front | 121 | `4B6C6DC23113457BF08F7AACF67BB8F009AB2AA193FBCE921509695A6E261F5A` | 429,148 | 1434x2034 |

For the 23 semantic rows, a structured visual-review row may list a contextual
reader illustration or no asset at all. Such an asset is never semantic proof.
The builder must validate semantic rows from accepted Markdown regions. It must
reject an evidence-only crop or contextual reader illustration offered in place
of a parsed semantic structure.

## Exhaustive mismatch and ambiguity list

### P1 — must close before structured C2a acceptance

1. `accepted_v4_markdown` duplicates full pages inside all 33 source units.
   The builder already verifies the page path/hash and can read the accepted
   source directly; embedded authorial text is redundant and violates the
   no-whole-page-duplication boundary.
2. No class-specific closed schema exists for table/card/statblock/form facts.
   Current code checks only owner/page/hash/status closure and then reports the
   set size as `structured_units`; it never locates or validates a structure.
3. Ten of eleven table ledgers are wrong or non-executable. Six accepted tables
   are pipe tables; five are exact numbered series. Reusable code must support
   both without rewriting either representation.
4. Outdoor rows 10-12 are currently emitted under the Hospital sibling owner.
   This is a real wrong-owner binding, not a fact-ledger alias.
5. The Reliquae p67 ATTACKS region is currently assigned to the Infection child
   because that child owns page start. The child relationship is legitimate,
   but the boundary is semantically too broad and should be narrowed before
   the structure contract is sealed.
6. Plague Monk expectations invent absent attacks/armor/Sanity/ability fields.
   Reliquae expectations invent a nonexistent Plague Zombie subsection/table.
7. Tome/spell/pregen fields use semantic aliases rather than literal accepted
   tokens. The blank template incorrectly expects Responsibilities instead of
   Fellow Investigators.
8. A semantic structured visual-review asset is not evidence that the table or
   card exists. Six full visual forms need a separate exact-asset path; all
   other rows need parsed Markdown evidence.
9. There is no exactly-once structure evidence row, no source-to-emitted region
   hash, no wrong-order/missing-fact failure and no visual-substitution gate.

### P2 — explicit preservation debt, not a Step 6 blocker

1. The source-faithful spellings `Hastaÿk's corruption` (p62), `avatar of
   Hasalÿk` (p65) and `a significant portion is ties up` (p120) must remain
   literal protections. Reusable code must not normalize them.
2. Source p48 literally says `see Plague Zombie`, while the appendix supplies
   Reliquae/Infected Flesh rather than a Plague Zombie block. The accepted xref
   contract already preserves the visible text and targets the Reliquae
   Infection anchor. This is a source-authorial inconsistency, not evidence for
   inventing `plague_zombie_d8` and not a reason to reopen v4.
3. Several owner blocks contain adjacent non-structure material. Exact region
   boundaries, not whole-owner equality, are therefore required.

## Minimal executable config amendment

Use the existing `structured_content` list; do not add a second framework.

1. Remove `accepted_v4_markdown` from every `source_units` item. Keep the closed
   `page`, `path`, `sha256` identity only. The accepted page file is the single
   authorial-text authority.
2. Keep the `fact_expectations` key but replace its open semantic values with a
   closed classification-specific contract:

   - common `regions[]`: exact `page`, exact `binding_anchor`, exact start
     selector (`line_exact` only), exclusive end selector or deterministic
     record-count termination, and declared source format;
   - tables: `source_format` (`markdown_pipe_table` or
     `numbered_record_series`), exact header tokens/line, per-fragment ordered
     first-column keys, explicit continuation mode (`repeated_header` or
     `headerless`) and exact attached-note selectors;
   - cards/statblocks: exact ordered heading/section/field label tokens, exact
     region boundary, required literal substrings, literal lexical protections
     and literal forbidden tokens. Do not infer snake_case names;
   - visual forms: exact `asset_id`, `source_page`, `owner_anchor`, asset SHA,
     `representation=reader`, `semantic_role=full_page`, required ordinary and
     structured review ids, `emit_exactly_once=true`, and
     `semantic_duplicate_forbidden=true`.

3. Do not store row bodies or generated Markdown in config. At runtime derive a
   source-region SHA-256 from the hash-bound accepted page, emit the already
   accepted slice, and derive the emitted-region SHA-256 after only declared
   heading/image transformations.
4. Make `binding_anchor` exact per fragment. It must equal the logical owner or
   a declared hierarchy descendant; any sibling/unrelated owner is a hard
   failure.
5. Correct two binding seams in the same config amendment, then rerun the
   unchanged strict resolver:

   - add page 59 to `viral-appendix-encounters-outdoor.continuation_pages` and
     remove the page-start locator from
     `viral-appendix-encounters-hospital`, leaving its exact heading locator;
   - add page 67 to
     `viral-appendix-new-mythos-horrors-reliquae.continuation_pages` and remove
     the page-start locator from the Infection child, leaving its exact first
     infection-table locator.

   Expected result: outdoor p59 L2-8 belongs to Outdoor until the Hospital
   heading; Reliquae p67 L2-20 belongs to Reliquae until the Infection table;
   conservation remains zero-error.
6. Apply the row corrections in the matrix literally. In particular: Rumors
   uses `Rumor`; rowing has five printed keys; DSS throw has three columns in
   printed order; the five series tables use their exact one-line headers;
   Taint uses plural `Modifiers`; Plague Monk has no invented stat fields;
   Reliquae has two Infection tables and no Plague Zombie table; Iuramentum
   includes `Skills Gained`; Control Reliquae has only literal Cost/Casting
   Time labels; blank background ends with Fellow Investigators.

This is the smallest amendment because it changes only the existing config
schema/data and two existing binding declarations. It introduces no fuzzy
matching, no generic snake_case-to-source inference, no whole-page injection,
no duplicated crop and no scenario-specific code path.

## Builder-side algorithm

1. During declaration validation, enforce the closed per-class schema and
   source-unit shape. Reject unknown/missing keys, duplicate structure ids,
   duplicate placement indices, unsupported representation/class combinations,
   and any embedded `accepted_v4_markdown`.
2. Resolve ordinary assembly bindings first. Resolve each structure region only
   inside the exact emitted owner span named by its fragment. Validate logical
   owner/descendant relation; reject absent, duplicate or sibling owners.
3. Parse without rewriting:

   - pipe parser consumes the exact header, separator and configured key count,
     allowing only blank physical lines between accepted rows;
   - series parser consumes the exact header and exact `key + space` prefixes,
     with explicit repeated/headerless continuation behavior;
   - card/statblock parser validates ordered literal tokens and exact start/end
     boundaries while retaining the raw accepted text;
   - visual-form parser validates the owned reader asset and never treats an
     evidence/context image as semantic content.

4. Emit the already selected owner spans through the existing clean-span path.
   Do not construct replacement tables/cards/statblocks. Locate the emitted
   anchor block and prove the transformed region is present once, in the same
   order, with the expected deterministic source-to-emitted hash relationship.
5. For visual forms, strip the source Markdown image only through the existing
   generic image relocation, then require the ledger output path exactly once
   under the same owner. Reject a second semantic row or second emitted image.
6. Return a derived 29-row evidence list, not a constant count. Each row records
   id/class/logical owner, resolved fragment owner/page/start/end/source SHA,
   emitted occurrence/range/SHA, exact fact results, representation and asset
   identity/review ids where applicable. Fail if the set is not exactly the 29
   config ids.
7. Fail on absent, duplicate, wrong owner, wrong order, missing/extra key,
   header/field/section mismatch, missing attached note, source/emitted hash
   divergence, evidence-only visual substitution, wrong visual asset/review or
   duplicate form emission.

## Exact Terra implementation boundary

After a Sol/content owner applies and separately verifies the config amendment,
Terra/medium may modify only:

- `kb_creator/scripts/build_scenario_master_en.py`;
- `kb_creator/tests/test_build_scenario_master_en.py`;
- one immutable Terra implementation receipt assigned by the orchestrator.

The current `verify_scenario_master_en.py` and its tests remain C2b/later and
must not be opened by this C2a amendment. The temporary reader assembly may
return in-memory structured evidence; it may not create a durable MASTER_EN
candidate or sidecar in this step. Viral facts/tokens stay in config, never in
the reusable builder.

### Compact positive test classes

1. Current amended config: all 29 ids resolve once and evidence rows are derived
   from actual regions; exact class count is 11/10/2/6.
2. Pipe-table cases: single page, repeated-header continuation, attached note,
   three-column table, and two nested Reliquae infection tables.
3. Series cases: single page and headerless cross-page continuation.
4. Card/statblock cases: combined field line, literal empty/no-stat card,
   ordered sections/fields, source lexical protections and exclusive end.
5. Visual forms: six exact owned full-page assets, ordinary + structured review
   closure, one emitted asset each and no semantic duplicate.
6. Scenario-neutral synthetic fixture with different ids/tokens proving that no
   Viral fact is embedded in reusable code.

### Compact negative mutation matrix

1. absent region and duplicate region;
2. sibling/wrong owner and undeclared descendant;
3. wrong header, missing/extra/reordered first-column key and broken
   repeated/headerless continuation;
4. missing attached note;
5. missing/reordered exact card/statblock section or field;
6. injected Plague Monk stat or Plague Zombie table;
7. normalized source oddity or changed accepted/emitted region body;
8. embedded full-page Markdown or reusable-code Viral literal;
9. visual form absent, duplicated, wrong owner/page/hash/review, evidence-only
   substitution or semantic duplicate;
10. evidence list with a constant/fabricated count, missing id or duplicate id.

## Acceptance criteria for the bounded amendment

`READY_FOR_BOUNDED_AMENDMENT` becomes C2a-acceptable only when all are true:

1. canonical structured schema/data matches the matrix and contains no embedded
   full-page Markdown;
2. corrected binding resolver remains 1,935-block zero-error conservation;
3. all 29 structures resolve exactly once in the correct owner/descendant block;
4. every table header/key/continuation/note, card/statblock literal token/order
   and source lexical protection passes;
5. all six forms bind the exact reader asset and emit exactly once with no
   semantic duplicate or evidence-only substitution;
6. 29 evidence rows are derived from the real emitted temporary reader, with
   source/emitted region hashes, and no count is hard-coded;
7. the positive and negative matrix passes; reusable code contains no Viral
   facts and performs no fuzzy or snake_case inference;
8. no durable candidate/sidecar, translation, HTML/PDF, production, Git or
   release action occurs.

## Files checked

- assigned plan, context, project status and NRI goal governance;
- assignment packet and completed concurrent xref correction receipt;
- `working/viral/master_en/publication_config_v1.json`;
- all 28 unique accepted-v4 page files referenced by the 29 rows;
- existing source renders for pages 62, 65 and 67 for lexical/source parity;
- all structured owner bindings through the existing resolver;
- all 123 asset declarations and 91 visual-review declarations through existing
  declaration validation;
- current builder, verifier and their focused tests (read-only inspection).

## Files changed and process note

Intended write:

- new immutable receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_structured_contract_audit_20260901.md`.

Accidental ignored artifact:

- a read-only builder import was initially run without `python -B` and created
  or refreshed exactly
  `kb_creator/scripts/__pycache__/build_scenario_master_en.cpython-313.pyc`,
  initially observed as 65,399 bytes, SHA-256
  `541C112BE2E52778DDFCF22C75FEC64EB75D39E45BCC2078B2C6D57E0CED5C9A`.
  A later final read-only check found that the shared ignored path had been
  concurrently recreated at `2026-09-01T18:15:40Z` as 68,144 bytes, SHA-256
  `3C7F8C4E3AA4374F8D7D1239B4C9DEFC7FF11EE1ADB2DEA50F4EFDF421783C72`;
  this later identity is not attributed to the audit because other contributors
  were active in the shared worktree.
  The orchestrator explicitly withheld deletion authority and directed that it
  remain for separate cleanup authorization. All subsequent Python reads used
  `-B`. No source/config/test file was affected.

## Blockers and next action

There is no Step 6/source blocker and no user decision is required for the
structured facts. C2a implementation is procedurally blocked until the
orchestrator integrates this receipt and a bounded Sol/content config owner
applies the exact schema/data plus two binding-seam corrections against whole
config SHA-256
`5391A55C2ABEB0835F3526BE6F6CD06334A9001DD3B00B168EDF4BB18A20A0BA`.
Then dispatch Terra/medium only within the two-file C2a boundary above. C2b,
durable candidate creation, translation and later publication gates remain
closed.
