# A7 working specification: Dream structural successor decisions

Status: working specification; it is not a review receipt and does not imply a
passing Stage 05 audit, materialization, acceptance, or promotion.

## Immutable inputs and successor rule

- Baseline decisions: `20260917-cpu-replay-05-decisions-v12`.
- Baseline run: `20260917-cpu-replay-05`.
- Both baselines remain immutable.
- The successor is rebound to a fresh Stage 01-04 replay queue and uses the
  opt-in structural decision-set profile. Every one of the 26 page decisions
  receives a complete visual-review record, including pages with `units: []`.
- Raster table crops on page 18 remain provenance assets with
  `placement=reference_only`; reader Markdown carries the reviewed semantic
  stat blocks.

## Closed reviewed unit map

The raw references below use the `original_pipeline_txt` view unless another
view is stated. Marker-only changes do not change source wording.

| Page | Unit id | Kind / representation | Raw blocks | Required correction |
|---:|---|---|---|---|
| 1 | `dream-title` | heading / ATX 1 | 0, 1 | one `# Number 7 Dream` title; visually asserted missing `r 7` segment |
| 2 | `credits-heading` | heading / ATX 1 | 5 | `# CREDITS` |
| 4 | `glitches-list-part-1` | list / unordered | 30-32 | three list items; first half of cross-page list |
| 5 | `glitches-list-part-2` | list / unordered | 34-36 | three items, `continuation_of=glitches-list-part-1` |
| 5 | `dreams-heading` | heading / ATX 2 | 37 | parent heading |
| 5 | `dream-boardroom-heading` | heading / ATX 3 | 41 | child of `dreams-heading` |
| 5 | `dream-janitor-heading` | heading / ATX 3 | 43 | child of `dreams-heading` |
| 5 | `dream-monolith-heading` | heading / ATX 3 | 45 | child of `dreams-heading` |
| 5 | `dream-monster-heading` | heading / ATX 3 | 47 | child of `dreams-heading` |
| 5 | `dream-canisters-heading` | heading / ATX 3 | 49 | child of `dreams-heading` |
| 6 | `dramatis-heading` | heading / ATX 2 | 64 | parent heading |
| 6 | `stanwick-heading` | heading / ATX 3 | 65 | child of `dramatis-heading` |
| 7 | `elsie-heading` | heading / ATX 3 | 71 | child of `dramatis-heading` |
| 7 | `beginning-heading` | heading / ATX 2 | 75 | new major section |
| 7 | `handout-1-body` | handout / blockquote | 76-81 | enclose email and sign-off; add visually asserted caption |
| 7 | `email-heading` | heading / ATX 3 | 82 | child of `beginning-heading` |
| 8 | `bookshop-heading` | heading / ATX 2 | 86 | parent heading |
| 8 | `shopper-heading-p8` | heading / ATX 3 | 89 | child of `bookshop-heading` |
| 8 | `upstairs-heading` | heading / ATX 3 | 91 | child of `bookshop-heading` |
| 8 | `stanwick-knows-heading` | heading / ATX 3 | 94 | child of `bookshop-heading` |
| 9 | `handout-2-body` | handout / blockquote | 99-106 | enclose letter, sign-off, and caption |
| 9 | `leaving-bookshop-heading` | heading / ATX 2 | 108 | parent heading |
| 9 | `faceless-heading` | heading / ATX 3 | 109 | child of `leaving-bookshop-heading` |
| 9 | `shopper-heading-p9` | heading / ATX 3 | 111 | child of `leaving-bookshop-heading` |
| 9 | `elsies-flat-heading` | heading / ATX 3 | 113 | child of `leaving-bookshop-heading` |
| 9 | `elsies-diary-heading` | heading / ATX 3 | 116 | child of `leaving-bookshop-heading` |
| 10 | `handout-3-body` | handout / blockquote | 119-125 | enclose flyer and caption |
| 10 | `handout-4-body` | handout / blockquote | 126-130 | enclose journal summary and caption; raw 131 stays narration |
| 11 | `wellness-events-list` | list / unordered | 145-148 | four items, including first and last |
| 14 | `handout-5-body` | handout / blockquote | 187-194 | enclose letter, sign-off, and caption |
| 14 | `handout-5-list` | list / unordered | 188-191 | four nested items; parent `handout-5-body` |
| 15 | `keepers-note` | callout / blockquote | 201-202 | enclose note heading and body |
| 17 | `conference-opening-quote` | blockquote / blockquote | 241 | opening monologue only |
| 17 | `conference-revealed-quote` | blockquote / blockquote | 243 | revealed-location branch speech |
| 17 | `conference-unrevealed-quote` | blockquote / blockquote | 245 | unrevealed-location branch speech |
| 18 | `stanwick-statblock` | statblock / blockquote | 251-254 | semantic stat table, attacks, skills |
| 18 | `elsie-statblock` | statblock / blockquote | 255-257 | semantic name, stats, attacks, skills |
| 18 | `regular-statblock` | statblock / blockquote | 258-260 | semantic name, stats, attack, skills |
| 18 | `heavy-statblock` | statblock / blockquote | 261, 278, 262 | source reading order across the column break |
| 18 | `migo-man-statblock` | statblock / blockquote | 263-267 | semantic name, description, stats, attack, skills |
| 18 | `migo-statblock` | statblock / blockquote | 268-273 | semantic name, description, stats, combat, armor, skills |
| 18 | `hunting-horror-statblock` | statblock / blockquote | 274-276 | semantic name, stats, combat, armor, skills |
| 19 | `appendix-handout-1` | handout / blockquote | 280-285 | first boxed handout |
| 19 | `appendix-handout-3` | handout / blockquote | 286-292 | second boxed handout |
| 19 | `appendix-handout-5` | handout / blockquote | 293-299 | third boxed handout |
| 19 | `appendix-handout-5-list` | list / unordered | 294-297 | four nested items; parent `appendix-handout-5` |

Pages 3, 12, 13, 16, and 20-26 have a complete reviewed page contract with no
declared unit from the audited defect classes. Their existing Markdown remains
byte-identical except for the decision-side review metadata.

## Page 18 content source

Stage 03 must expose the exact v2 table caption and HTML cell text in each
matched table block while retaining its raster asset. That text is evidence,
not an inferred stat-block type. The page decision groups the reviewed blocks
into seven blockquotes and changes all ten table-crop assets to
`reference_only`. No table crop is rendered alongside the semantic reader
text.

The reviewed source visual establishes the intended seven boundaries and the
left-to-right continuation of the Enlightened Heavy block across the column
break. Any v2 cell omission remains a text-fidelity matter and must be closed
with exact reviewed visual evidence rather than invented by the structural
validator.

## Required verification

1. All 26 page contracts bind the exact fresh Stage 04 source visual.
2. All spans and hashes are recalculated after the effective Markdown transform.
3. The Stage 05 v4 audit reports all declared units validated and no legacy
   lexical gap.
4. Removing a quote marker, list marker, heading level, table delimiter,
   parent/continuation relation, or page-18 boundary makes validation fail.
5. Stage 06 emits the same semantic Markdown plus a hash-bound
   `SEMANTIC_STRUCTURE.json` and does not render reference-only table crops.
