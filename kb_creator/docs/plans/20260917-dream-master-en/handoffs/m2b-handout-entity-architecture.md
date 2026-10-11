# M2b numbered-handout entity detector architecture receipt

## Receipt

- Goal: `20260917-dream-master-en`; milestone: `M2b`.
- Scope: scenario-neutral remediation of promotion's
  `numbered_player_handouts` closure check after the semantic-sidecar bridge
  exposed a valid caption form that the legacy detector cannot see.
- Result: `SPEC_READY`. The accepted Dream reconstruction is not defective;
  the promotion detector still assumes that every numbered handout is exposed
  by an ATX `Player Handout N` heading or a handout asset logical name.
- Files changed: only this assigned immutable receipt. No code, canonical
  status/plan, contract, source, candidate, or generated artifact was edited.
- Orchestrator policy owner: `gpt-5.6-sol`, medium.
- Assignment: architecture/root-cause analysis, `gpt-5.6-sol`, high;
  assignment state `completed`; orchestration ownership remains with the main
  chat.
- Scoped override: none.
- Timestamp: `2026-09-18T00:04:21+03:00`.
- Coordinate clarification amended: `2026-09-18T00:06:51+03:00` after an
  implementation checkpoint compared decision and Stage 06 page-file line
  numbers.
- Elapsed time: approximately 12 minutes.
- Token use: approximately 10k tokens including the coordinate recheck.

## Root cause and evidence

`pipeline/reconstruction_promotion.py` currently builds the numbered handout
set from only two sources:

1. combined-Markdown ATX headings containing `Player Handout N`;
2. assets already declared with `placement: handout` whose logical names
   contain `Player Handout N`.

It then requires exact equality with
`range(1, contract.scope.required_entities.numbered_player_handouts + 1)`.
The exact-range comparison is correct; the detector inputs are incomplete.

The accepted Dream candidate represents the handouts as visually reviewed
semantic containers. Their reader-visible labels are ordinary or blockquoted
caption lines such as:

- `Figure 1 Handout 1 - Number 7 Dream`;
- `> Handout 2 – Number 7 Dream`;
- `> Handout 5 - Number 7 Dream`.

The v2/v4 semantic authority contains eight `kind: handout` units across the
main text and appendix. Their hash-bound Markdown spans yield the exact unique
label set `{1, 2, 3, 4, 5}`. A read-only trial using the rules below found:

- page 9: `2`;
- page 10: `3`, `4`;
- page 14: `5`;
- page 19 appendix: `1`, `3`;
- the remaining typed handout spans contain no full-line label and contribute
  nothing;
- unique result: `{1, 2, 3, 4, 5}`.

By contrast, narrative references such as `give the investigator Handout 3`
are prose outside a typed handout span and must not satisfy entity closure.

### Authoritative coordinate system clarification

`markdown_span.start_line/end_line` are 1-based inclusive coordinates in the
page decision's effective Markdown, exactly as validated by
`semantic_structure.validate_semantic_structure`: it applies the declared
`block_boundaries` transform to `decision["markdown"]`, splits that result on
`\n`, and hashes/slices those lines. They are **not** coordinates in
`candidate/pages/page-NNN.md`.

Stage 06 page files prepend a source-page marker plus a blank line, so their
reader lines are offset by two. This caused an apparent contradiction during
the implementation checkpoint but does not justify an adjacency rule:

| Page/unit | Decision span | Caption in decision Markdown | Same caption in Stage 06 page file | Result |
|---|---:|---:|---:|---:|
| 9 `handout-2-body` | 3-17 | line 17 | line 19 | 2 |
| 10 `handout-3-body` | 1-13 | line 13 | line 15 | 3 |
| 10 `handout-4-body` | 15-23 | line 23 | line 25 | 4 |
| 14 `handout-5-body` | 9-23 | line 23 | line 25 | 5 |
| 19 `appendix-handout-1` | 3-13 | line 13 | line 15 | 1 |
| 19 `appendix-handout-3` | 15-29 | line 29 | line 31 | 3 |

Page 7's plain caption is genuinely outside its decision span (caption line
25 versus span 13-23) and contributes nothing; Handout 1 is independently
closed by the appendix page-19 typed span. Likewise, the page-19 Handout 5
duplicate has no label inside its span and contributes nothing; page 14 closes
that entity. The unique live result remains exactly `{1,2,3,4,5}`.

Accordingly, no adjacent-line allowance is permitted. Do not subtract a fixed
offset from Stage 06 page-file line numbers and do not inspect lines before or
after a semantic span. The extractor must consume the same effective
decision-Markdown coordinate space as the semantic validator.

## Required detector contract

Implement one generic helper that returns an evidence-bearing set of numbered
handout entities. It must combine only these high-authority channels:

1. **Legacy heading evidence:** preserve the existing ATX `Player Handout N`
   behavior byte-for-byte for non-structural and structural candidates.
2. **Legacy asset evidence:** preserve the existing behavior for logical names
   of assets explicitly declared with `placement: handout`.
3. **Reviewed semantic-caption evidence:** only in the already validated
   structural v2/v4 mode, inspect the exact hash-bound Markdown span of page
   semantic units whose `kind` is `handout`. Extract a number only from a
   complete caption line inside that span.

Do not infer an entity number from a semantic unit `id` such as
`handout-5-body`; IDs are reviewer-local identifiers, not reader-visible source
evidence. Do not scan arbitrary prose for `Handout N`.

### Semantic caption grammar

For each line inside a validated `kind: handout` span:

1. start from the effective page-decision Markdown after applying the same
   declared `block_boundaries` transform used by semantic validation; never
   use `pages/page-NNN.md` as the span coordinate source;
2. remove only Markdown container prefixes proven by the representation:
   repeated blockquote markers and, if present, one ATX heading prefix;
3. trim whitespace and optionally unwrap one balanced whole-line emphasis
   pair;
4. match the entire remaining line, case-insensitively, against this closed
   semantic form:

```text
[optional "Figure" or "Fig." + decimal figure number]
[optional "Player"]
"Handout" + decimal handout number
[end of line OR one of -, en dash, em dash, : followed by a non-empty title]
```

The captured value is the number after `Handout`, never the optional figure
number. Arbitrary trailing prose without a caption separator is forbidden, so
`Handout 3 is in the wastepaper bin` does not match. A sentence containing the
token mid-line also does not match.

The helper must defensively require a valid integer span inside the current
decision Markdown. In the live route it must run only after structural-mode
selection and semantic sidecar/audit/submission/page-decision validation have
closed those spans. If semantic authority is absent, it must not examine
semantic fields or widen legacy behavior.

### Ambiguity and duplicates

- Zero matching captions in one typed handout span is allowed. A body may have
  a caption excluded from that span or be a continuation/duplicate; it
  contributes no entity number. An adjacent excluded caption is never pulled
  into the unit by promotion.
- Repetition of the same number across main text and appendix is allowed and
  collapses to one entity.
- Two different full-line handout numbers inside one semantic handout span are
  ambiguous and must fail closed rather than silently count both.
- Any parsed number less than 1, greater than the contract count, or outside
  the exact expected range causes the final set equality check to fail.
- The final authority remains the contract: detected unique numbers must equal
  exactly `{1..N}`. Matching `N` items with gaps or extras is not sufficient.

## Integration order and data contracts

The structural path should be ordered as follows:

```text
sealed decision-set v2 + audit v4 select structural mode
-> candidate decisions and sidecar are identity-validated
-> typed handout spans are eligible for caption extraction
-> union with unchanged legacy heading/asset evidence
-> exact contract range comparison
-> remaining asset/provenance/package closure
```

Move the required-entity comparison after semantic sidecar validation, or
otherwise pass only an already validated structural projection into the
helper. This prevents the entity gate from trusting unvalidated metadata.

No schema revision is required. The detector consumes existing fields:

- reconstruction contract
  `scope.required_entities.numbered_player_handouts`;
- validated page decision `markdown`;
- validated page semantic units `kind`, `representation`, and
  `markdown_span`;
- existing legacy heading and `placement: handout` asset evidence.

The semantic sidecar remains evidence that those page units were independently
audited; it is not itself a source of visible labels because its compact rows
do not carry Markdown line coordinates or text.

## Fail-closed boundaries and risks

- Do not broaden the global regex to every `Handout N` occurrence. That would
  let instructions, cross-references, contents pages, and narrative prose
  manufacture contract closure.
- Do not use only the count of typed `kind: handout` units. Dream legitimately
  repeats entities in the appendix, so unit cardinality is not entity
  cardinality.
- Do not use the optional `Figure N` value as the handout number.
- Do not interpret Stage 06 page-file offsets as semantic adjacency. Only the
  decision Markdown lines already covered by the audited inclusive span are
  eligible.
- Do not require every handout unit to contain a label; continuation and
  duplicate representations may omit it.
- Do not mutate accepted Markdown or semantic decisions to satisfy promotion.
  This is a reusable consumer fix and requires no MinerU/OCR or reconstruction
  replay.
- Keep the existing exact-range comparison, candidate inventory closure,
  atomic staging, and acceptance exclusivity unchanged.

## Regression specification

Add focused, committed tests for the helper and the promotion boundary:

1. **Caption variants:** plain, blockquoted, nested-blockquoted, optional ATX,
   `Player Handout N`, `Handout N`, and optional `Figure/Fig. M` prefixes;
   accept hyphen, en dash, em dash, colon, or end of line after the number.
2. **Figure disambiguation:** `Figure 2 Handout 1 - Title` yields `1`, not `2`.
3. **Dream-shaped positive fixture:** typed spans equivalent to pages 9, 10,
   14, and 19 yield exactly `{1,2,3,4,5}` even when an additional typed body
   has no label and appendix duplicates `3`.
4. **Coordinate regression:** prove that decision span 3-17 counts a caption
   on decision line 17 while the corresponding marker-prefixed Stage 06 page
   file exposes it on line 19; the extractor must use the former and must not
   scan either adjacent decision line 18 or page-file line 19 by offset math.
5. **Narrative rejection:** `give the investigator Handout 3`, contents lines,
   mid-sentence references, and `Handout 3 is ...` do not count when outside a
   handout unit; the sentence form also does not count inside one.
6. **Metadata rejection:** unit ID `handout-5-body` with no visible caption
   contributes nothing; an exact caption inside `kind: paragraph`, `callout`,
   or `statblock` contributes nothing.
7. **Ambiguity:** two different full-line captions in one handout span fail;
   duplicate identical captions and repeated same-number entities collapse.
8. **Contract closure:** missing number, extra number, zero/negative number,
   and a gap with the same total cardinality all fail exact equality.
9. **Backward compatibility:** existing synthetic legacy heading and
   `placement: handout` asset cases still pass without semantic authority;
   non-structural candidates do not gain plain-caption scanning.
10. **Authority ordering:** malformed/unvalidated span, stale sidecar, or
   v2/v4 disagreement fails before entity extraction can make a candidate
   promotable.
11. **Live read-only smoke:** Dream replay-16 promotion preflight reaches
    `promotion_preflight_passed` with candidate inventory unchanged before the
    orchestrator retries materialization.

## Acceptance criteria

- The detector recognizes the exact Dream handout entity set `{1..5}` from
  visible labels within reviewed semantic handout spans plus unchanged legacy
  evidence.
- A narrative-only `Handout N` reference cannot satisfy the contract in either
  structural or legacy mode.
- Existing valid legacy promotion fixtures and accepted non-structural packages
  remain valid.
- The implementation is scenario-neutral and located in reusable promotion
  code with focused tests; no Dream-specific literal, path, title, or count is
  embedded.
- Read-only Dream preflight passes without changing any Stage 01-06 byte, then
  the existing M2 materialization/acceptance sequence may resume.

## Files checked, verification, blockers, next action

Files checked:

- `kb_creator/docs/plans/20260917-dream-master-en/plan.md`
- `kb_creator/docs/plans/20260917-dream-master-en/context.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/pipeline/semantic_structure.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_semantic_structure.py`
- replay-16 `RECONSTRUCTED_EN.md` and all relevant typed handout page
  decisions (pages 7, 9, 10, 14, and 19; all 26 decision files were scanned
  for typed handout units).

Verification/evidence: static dependency trace plus a read-only PowerShell
trial of the closed caption grammar against every replay-16 semantic handout
span. The unique detected result was `1,2,3,4,5`. No production test was run
and no artifact was mutated in this architecture assignment.

Blockers: none for the bounded implementation. Promotion remains correctly
blocked until this consumer change and its regression tests pass.

Next action: implement the generic evidence extractor and ordering change in
`reconstruction_promotion.py`, add the focused tests above, run the promotion
and semantic suites, then rerun Dream promotion preflight before any materialize
or acceptance write.
