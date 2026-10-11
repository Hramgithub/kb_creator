# L2 architecture receipt: reviewed compact line groups

## Governance receipt

- Goal id: `20260917-dream-lineflow-fidelity`
- Step id: `L2`
- Role: architecture / root-cause analysis
- Model: unavailable; repository-policy role target is `gpt-5.6-sol`
- Effort: requested `high`; actual platform effort unavailable
- Orchestrator policy owner: `gpt-5.6-sol`, medium
- Assignment state: `platform-unverified`
- Scoped override: none
- Scope: inspect the shared semantic validator, reviewed-decision authoring
  helper, relevant schemas/tests, and replay-15 Dream pages 21-26; specify the
  smallest scenario-neutral fail-closed contract for visually reviewed compact
  line groups rendered with Markdown hard breaks. Pipeline code, schemas,
  tests, canonical plan/context/status, and generated replay artifacts were
  explicitly out of scope and were not changed.
- Result: root cause confirmed and the additive contract, authoring rule,
  compatibility boundary, implementation surface, risks, test matrix, and
  acceptance criteria below are specified.
- Files changed: this immutable receipt only.
- Blockers: none for implementation. A fresh absent decisions root and replay
  successor are required for authored Dream corrections; replay-15 and v26
  remain immutable evidence.
- Next action: L3 implements the shared validator/authoring support and focused
  tests exactly within this contract. L4 then authors all six reviewed groups
  into fresh decisions, and L5 proves the rebuilt Stage 05/06 successor.
- Elapsed time: approximately 28 minutes.
- Token use: unavailable.
- Timestamp: `2026-09-17T22:33:25+03:00`.

## Root cause and dependency trace

The defect is at the reviewed decision/semantic gate, not at rendering or
`MASTER_EN`:

```text
Stage 04 visual + packet blocks
  -> reviewed authoring spec
  -> page decision Markdown + semantic_structure
  -> Stage 05 v4 lexical audit + validate_semantic_structure
  -> Stage 06 _validate_decision + validate_semantic_structure
  -> page Markdown / RECONSTRUCTED_EN.md / SEMANTIC_STRUCTURE.json
```

The v4 lexical ledger intentionally normalizes away whitespace and Markdown
punctuation. The semantic validator currently recognizes blockquotes, lists,
tables/statblocks, and headings, but not a compact sequence of ordinary text
lines. Pages 21-26 therefore have a complete visual-review record with
`declared_unit_count=0`; the passing Stage 05 audit and Stage 06 sidecar cannot
distinguish blank-separated paragraphs from hard-broken lines.

The existing `block_boundaries: compact` transform is not the right contract:
it removes exactly one separator between an ATX heading and its first body
line. It neither groups ordinary lines nor proves a hard break between every
member. Extending it would combine unrelated boundary semantics and would not
bind the group to reviewed source blocks.

The authoring helper is the earliest reusable repair point. It already binds
unit definitions to ordered Stage 04 `raw_indices`, calculates effective spans
and hashes, and writes fresh decision identities. The same semantic validator
is already called by Stage 05 and Stage 06, so one new closed representation is
sufficient to make both gates fail closed.

## Replay-15 evidence and exact Dream mapping

The L1 full-scope audit found no other analogous group in pages 1-20. The six
reviewed character-field groups are:

| Page | Ordered `original_pipeline_txt` raw blocks | Source lines | Replay-15 state |
|---:|---|---:|---|
| 21 | `312,313,314,315,316,317,318` | 7 | false blank paragraphs |
| 22 | `327,328,329,330,331,332,333` | 7 | false blank paragraphs |
| 23 | `342,341,343,344,345,346,347` | 7 | false blank paragraphs and wrong first-two order |
| 24 | `356,357,358,359,360,361,362` | 7 | false blank paragraphs |
| 25 | `371` | 6 | already hard-broken |
| 26 | `381` | 7 | already hard-broken |

Page 23's order is deliberately geometry/review-derived: raw 342
(`STR ... SAN`, y=319-335) precedes raw 341 (`Luck`, y=334-349), followed by
343-347. Numeric raw-index order is not an ordering heuristic. Pages 25 and 26
prove that one source block may contribute several physical group lines.

## Minimal runtime data contract

Extend the existing exact semantic-unit vocabulary with one pair only:

```json
{
  "kind": "line_group",
  "representation": "hard_break_lines"
}
```

Keep the existing unit shape unchanged: `id`, `kind`, `representation`,
`source_blocks`, `markdown_span`, the three relation fields, `heading_level`,
and `item_count`. For `line_group`, both `heading_level` and `item_count` must
be `null`. Do not add page-decision keys, a transform field, counts, labels, or
scenario vocabulary. Expected line count and order are derived from the
already mandatory ordered `source_blocks`.

Do **not** reuse `item_count` for line groups. Its existing contract is a list
item count, and overloading it would weaken type meaning while adding no
authority: the line count is deterministically available from mapped source
text. Keeping it `null` preserves every v1 unit's exact key/type convention.

Add `"line_group": {"hard_break_lines"}` to the validator's closed
kind/representation map. Its additional invariants are:

1. The ordered mapped source blocks must each exist, be selected, and
   contribute non-empty text. Split each corrected source text on physical LF;
   the combined sequence must contain at least two non-blank lines.
2. Apply the existing closed reviewed text-correction ledger before comparing
   source and reader lines. Strip only MinerU `sup`/`sub` tags through the
   existing display normalization; do not infer groups from colons,
   capitalization, labels, or punctuation.
3. The inclusive Markdown span must contain exactly the derived number of
   physical lines, with no empty or whitespace-only line.
4. Reader lines must match the normalized source-line sequence one-for-one and
   in the declared `source_blocks` order. This is in addition to the existing
   span-level source-text and lexical-completeness checks.
5. Every non-final Markdown line must end with at least two literal ASCII
   spaces (` {2,}` immediately before LF). Tabs and a backslash break are not
   accepted by this representation. The final line must not carry a hard-break
   suffix.
6. The existing inclusive line bounds and SHA-256 bind the exact whitespace.
   Rehashing after replacing a hard break with a blank line still fails rules
   3-5, so this is a semantic gate rather than hash-only evidence.
7. Existing overlap, containment, relation, source-selection, visual-identity,
   and global-id invariants continue unchanged. A line group may have a
   semantic parent, but no parent or English field name is required.

The deterministic sidecar row remains the existing compact projection
`id/kind/representation/markdown_span_sha256`; no new sidecar envelope is
needed.

## Generic authoring rule

Do not add a second scenario-specific rule table. A reviewed spec unit whose
`kind` and `representation` are `line_group/hard_break_lines` is itself the
authoring instruction. Its ordered `raw_indices` are the sole grouping/order
authority; existing `start`/`end` selectors are checked against the resolved
first/last member and remain span selectors, not semantic inference.

Add one shared authoring helper and call it identically from `author()` and
`validate_spec()` after ordinary patches, structural review rules, and
post-patches, but before `apply_block_boundaries` and span hashing:

1. expand the ordered raw blocks into corrected physical source lines;
2. locate exactly one reader line for every expected line after removing only
   trailing spaces/tabs for matching; ambiguous, missing, duplicated, or stale
   matches fail;
3. require the smallest matched Markdown interval to contain only those member
   lines and blank separators—any unrelated non-blank line fails;
4. preserve each matched reader line's visible bytes, remove trailing
   whitespace, order the lines by the reviewed raw mapping, append exactly two
   ASCII spaces to every non-final line, and append none to the final line;
5. verify the declared first/last selectors exactly and then let the existing
   unit builder compute the final span/hash.

This makes pages 21-24 compact, keeps pages 25-26 semantically equivalent while
canonicalizing their existing three-space breaks to two, and corrects page
23's first-two field order from the reviewed mapping. It never manufactures or
edits field text. An already canonical group is idempotent.

The current helper has a minor branch divergence: `author()` computes spans on
`apply_block_boundaries(...)`, while `validate_spec()` currently computes them
on untransformed Markdown. L3 must route both through one effective-Markdown
function when adding the line-group helper; otherwise validate-only and author
can disagree.

## Compatibility decision

Use the existing `kb_creator.page_semantic_structure.v1` and decision-set v2
profile. This is the smallest compatible extension because the page unit's
exact key set, decision-set envelope, v4 audit envelope, and v1 sidecar envelope
do not change. The JSON schemas currently leave unit objects open to the
runtime closed validator, so no schema-shape addition is required.

- Existing decision-set v2 artifacts containing only the old pairs retain
  identical meaning and continue to validate under the new code.
- Decision-set v1 remains on its legacy v3 path and cannot claim this gate.
- New line-group decisions fail closed under old code as an unsupported
  kind/representation; they must be authored into a fresh replay whose
  implementation identity includes the updated validator/helper/tests.
- Replay-15, v26, its passing v4 audit, and its zero-unit page records remain
  immutable historical evidence; they are not relabelled as satisfying the
  new contract.
- No `block_boundaries` behavior changes. No `MASTER_EN`, promotion,
  acceptance, or release behavior is inferred.

If a future consumer requires schema-level enumeration rather than the current
runtime-enforced unit vocabulary, that is a separate schema-hardening goal; it
is not required to close this defect and must not be bundled into L3.

## Implementation surface

The bounded L3 change should touch only:

- `kb_creator/pipeline/semantic_structure.py`: add the closed pair and the
  per-line source/topology/hard-break validation;
- `kb_creator/scripts/author_reviewed_semantic_decisions.py`: add the shared
  mapping-driven canonical renderer and unify effective-Markdown ordering;
- `kb_creator/tests/test_semantic_structure.py`: unit-level contract tests;
- `kb_creator/tests/test_author_reviewed_semantic_decisions.py`: authoring and
  validate-only parity tests;
- focused Stage 05/06 integration tests in the existing audit/materializer or
  replay-resume test files only where needed to prove both gates invoke the
  shared validator.

No comparison, Stage 04 packet, decision-set, audit-envelope, sidecar-envelope,
promotion, publication, or scenario-contract change is required.

## Test matrix

| Layer | Passing case | Required failing/mutation cases |
|---|---|---|
| semantic validator | seven lines from seven blocks; six lines from one block; two-or-more-space input compatibility | unknown pair; one-line group; blank internal line; missing hard break; tab/backslash break; hard break on final line; line-count mismatch; collapsed/split/reordered source line; stale span hash |
| authoring helper | blank-separated multi-block input becomes canonical; already hard-broken single-block input is idempotent; reviewed nonnumeric raw order is honored | absent/ambiguous member; duplicate source-line ambiguity; unrelated line inside interval; stale first/last selector; empty mapped source line; destination is not written on failure |
| Stage 05 | v4 audit passes a declared canonical group | lexically complete blank-separated group fails; updated hash cannot bypass syntax/source-line checks |
| Stage 06 | audited group rematerializes and sidecar records `line_group/hard_break_lines` | bypassed/tampered decision fails the repeated validator; audit structure hash mismatch fails before candidate output |
| compatibility | existing semantic fixtures, v2 pages without line groups, legacy v1/v3 path, and `block_boundaries` tests remain green | unknown page-decision fields and unknown representations still fail closed |
| Dream successor | exact assertions for all six page groups | deleting any one hard break, adding any internal blank line, or restoring page 23's `Luck`-first order fails QA |

## Acceptance criteria

L3 is complete only when:

1. reusable code and synthetic fixtures contain no Dream page numbers, field
   labels, scenario title, or punctuation-based grouping heuristic;
2. the new pair uses the unchanged semantic-unit shape and ordered selected
   source-block authority;
3. author and validate-only paths produce/validate identical effective
   Markdown, and Stage 05 and Stage 06 call the same runtime validator;
4. every mutation in the matrix fails before a Stage 05 pass or Stage 06
   candidate can be published, while all listed compatibility paths pass;
5. no existing replay or decision root is mutated.

L4/L5 closure additionally requires fresh decisions declaring exactly one
line-group unit on each of pages 21-26, exact raw mappings from the table above,
canonical hard breaks on all non-final fields, one ordinary paragraph boundary
between `Move` and `Skills`, page 23 ordered `STR...SAN` then `Luck`, a passing
fresh v4 audit, a matching Stage 06 sidecar, and exact visual/text assertions
across all 26 pages. This remains reconstruction QA only; it does not accept or
promote `RECONSTRUCTED_EN`.

## Risks and controls

- Trailing spaces are visually subtle and editors may trim them. Control: exact
  span hashes plus explicit runtime syntax checks at both stages.
- `_normalized` erases whitespace and punctuation. Control: the new validator
  compares the per-line sequence and Markdown endings in addition to the
  existing lexical ledger.
- One MinerU block may contain many lines, while many blocks may form one
  group. Control: derive a flattened physical-line sequence from ordered
  source mappings; never equate block count with line count.
- Raw indices do not always encode visual order. Control: the reviewed ordered
  mapping is authoritative; page 23 is the concrete counterexample.
- A broad formatter could damage unrelated prose. Control: replace only the
  exact minimal member interval and fail on any nonmember line.
- Expanding schemas/profile versions would multiply dispatch and compatibility
  branches without adding evidence for this defect. Control: the additive pair
  is code-identity-bound to a fresh replay, while old artifacts remain sealed.

## Files checked and verification evidence

Governance and state:

- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/README.md`, `kb_creator/PROJECT_STATUS.md`
- this goal's `plan.md`, `context.md`, and L1 QA receipt
- `kb_creator/contracts/number-7-dream.reconstruction.json`

Implementation, schemas, and tests:

- `kb_creator/pipeline/semantic_structure.py`
- `kb_creator/scripts/author_reviewed_semantic_decisions.py`
- Stage 05 v4 composition in `audit_mineru_ai_merge_fidelity.py`
- Stage 06 repeated validation/materialization in
  `materialize_mineru_ai_merge.py`
- decision-set validation in `pipeline/reconstruction.py`
- `page_semantic_structure.v1.schema.json`,
  `reconstruction_decision_set.v2.schema.json`,
  `reconstruction_semantic_structure.v1.schema.json`, and v4 audit schema
- `test_semantic_structure.py`,
  `test_author_reviewed_semantic_decisions.py`, and focused materializer tests

Live immutable evidence:

- replay-15 Stage 04 page visuals and merge packets for pages 21-26
- v26 page decisions and the original pages-21-26 authoring spec
- replay-15 Stage 05 `audit.json`, Stage 06 page Markdown, and
  `SEMANTIC_STRUCTURE.json`

Verification was read-only apart from this receipt. All six Stage 04 visuals
were inspected at original resolution. No tests were run because this step is
an architecture specification and makes no executable change.
