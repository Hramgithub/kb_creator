# Reviewed DOCX successor

`python -X utf8 -m kb_creator.scripts.revise_reviewed_docx` creates one new
`document.docx` from a sealed, human-reviewed DOCX. The original PDF and
selected source images are immutable evidence. The command does not generate
HTML or a published PDF. It does not replay missing source or translation
masters, resolve review comments, or approve the candidate.

```powershell
python -X utf8 -m kb_creator.scripts.revise_reviewed_docx `
  --manifest kb_creator/docs/plans/20261004-user-docx-review/audit/fear-candidate/fear-docx-only-manifest-v01.json `
  --reviewed-docx kb_creator/deliverables/latest/fears-sharp-little-needles/document.docx `
  --source-pdf path/to/immutable/original.pdf `
  --output-root kb_creator/working/user-review-20261004/fear-reader-v01 `
  --report kb_creator/docs/plans/20261004-user-docx-review/audit/fear-candidate/revision-report-v01.json
```

The output root must be new and contains only `document.docx`. The report is a
separate QA artifact. A failed preflight does not create the candidate root.
The report marks a successful structural build `validated_candidate` with
`accepted: false`; page rendering and independent review remain separate.

The JSON manifest schema is `kb_creator.reviewed_docx_revision.v1` with
`provenance: reviewed_artifact_successor`. `inputs` seals the reviewed DOCX and
original PDF SHA-256, any supporting authority files (`path` and `sha256`),
and the complete ordered list of original Word drawing occurrences
(`sha256` and `drawing_id`). `stories` lists ordered `story_id` and unique
`word_bookmark` pairs. The first story can represent front matter; any image
before its bookmark fails as unowned artwork.

`source_graphic_ids` is the independently reviewed required source-art domain.
`source_graphics` has exactly one row for every ID. A required row has
`graphic_id`, `story_id`, physical `source_page`, `disposition: must_include`,
selected image `sha256` and zero-based `occurrence_ordinal` among identical
image binaries within that story. Retained rows may also seal the existing
`drawing_id` and original `legacy_descr`. Repeated occurrences are not merged
by hash. `reference_only` does not satisfy required coverage. A deliberate
exclusion requires `disposition: exclude`, `reviewed: true` and a specific
reason. For Fear, the reviewed domain is all 26 opening scenes: three existing
plus 23 restored.

Each unchanged issue has `kind: keep`, `disposition: keep`, `issue_id`,
`comment_id`, `story_id`, `word_bookmark`, a reason and an exact paragraph
selector. A text edit adds `kind: text`, `disposition: replace`, full
`expected_text`, its UTF-8 `expected_text_sha256`, `target_text` and
`replacement`. The paragraph selector is
`{"kind":"exact_paragraph","expected_matches":1,"ordinal":0}`; it is
mandatory even if the story bookmark is present. The selected paragraph must
carry the named native root comment range. The target must occur once within
one supported Word text node. Rich runs and comment markers are preserved;
fields, hidden text, mixed run constructs and ambiguous matches fail closed.

Artwork operations use `kind: art`, exact `graphic_id`, story bookmark,
physical source page, source image path/hash/pixel dimensions, positive Word
width and `insertion: after_exact_paragraph`. A mandatory `position` object
contains the full final opener-group paragraph text, its SHA-256 and exact
paragraph selector within that story. An absent selector or changed context
cannot fall back to the heading. The selected image's actual decoded format,
JPEG or PNG, controls the new internal media extension and content type;
the input filename extension is irrelevant. The image is embedded with
proportional dimensions and no crop.

The builder snapshots manifest, DOCX, PDF, supporting authority files and
selected images before editing. It verifies their hashes before build and
again before publishing. OOXML edits preserve the bytes of all existing parts
other than the required main document, relationship and content-type parts;
the old rows of those two metadata parts remain intact. Original drawings,
paragraphs, bookmarks, hyperlinks and native comment markers keep their
order and identity except declared text changes and additions. A staged DOCX
is reopened and rechecked before publication. The report records input and
output hashes, operation bindings, source physical pages, reader stories,
coverage and remaining lineage/layout limits.

## Optional exact source-bound Word fields

Unannotated stat fields do not masquerade as native comments. A separate
`source_bound_fields` object can be added to the same DOCX-only manifest:

```json
{
  "book_id": "shadows-of-leningrad-1938",
  "ledger": {"path": ".../approved-word-operations.json", "sha256": "..."},
  "choices": {"path": ".../accepted-choices-v01.json", "sha256": "..."},
  "conversion_spec": {"path": ".../conversion-spec.md", "sha256": "..."},
  "operation_ids": ["every approved operation ID for this book, in frozen order"],
  "expression_ids": ["every approved split-run expression ID, if any"]
}
```

The referenced operation ledger must have schema
`nri.u7_word_conversion_operations.v1`, state
`approved_source_bound_operations`, `source_qa_closed: true`, and
`orchestrator_approved: true`. The current U7 planning ledger does **not**
meet this gate and cannot author a successor. The manifest's IDs must close
the entire per-book approved ledger domain; selecting a convenient subset is
not allowed. Both original DOCX and source-PDF identities must match.

Every operation binds a source physical page and edition evidence, exact
entity-heading body index/text/hash/bookmarks, zero-based body/table/cell/run/
text-node path, full original text node and its SHA-256, field and exact
nonoverlapping span, approved rule or explicit user-decision ID, and reverse
text. Its node group also seals original and final full-node text **and XML**
hashes; `node_group_ids` must agree. The final approved ledger adds
`current_scale: old_edition` to numeric operations and `source_verified: true`
to every operation. Direct skill mappings also require a per-entity
`entity_collision_clear: true` QA finding. A protected Luck, SAN,
HP, MP, MOV, damage, age, attack or skill percentage cannot enter the numeric
characteristic allowlist. Bare values in tables must bind to their exact
column header. Direct skill-label mappings retain numbers and percentages.
User-approved contextual/prose labels require a matching choice ID. There is
no global regular-expression replacement or value-range inference.

All edits in a shared Word text node are planned against the original node,
checked for span overlap, and applied atomically. Up to eight edits in a
Kremlin node follow the same rule. A separate `expression_groups` ledger
section supports a contiguous two-to-four-node characteristic dice effect,
such as `1D6 СИЛ` → `5 × (1D6) СИЛ`, by exact first/last node edits while
retaining existing run formatting. Hidden runs, Word fields, tracked-change
nodes, unsupported rich target-run constructs, noncontiguous expressions and
stale XML hashes fail closed. Field edits cannot share a build with artwork
insertions because those change body-path indexes. The written DOCX is reopened
to verify final text/XML hashes, original paragraph and drawing order, and
unchanged original OOXML parts. This route does not generate HTML or PDF.

The U7 v01 operation ledger remains planning evidence and is never promoted
in place. The U5v04 adapter in `docs/plans/20261004-user-docx-review/audit/
two-book-candidates/prepare_candidates.py` verifies its frozen source, closure,
user-choice and independent 146-field source-QA authorities, then seals a new
197-operation ledger and two exact manifests. That ledger contains 146 stat-card
characteristics, 2 source-bound door Strength thresholds, 35 direct skill
labels, 1 contextual prose label, 8 user-approved Kremlin labels and 5 exact
two-table Persuasion consolidation edits. One separate expression group edits
the split-run Strength-drain expression. An already-current Natural History
label is verified as a no-op, not represented by a fabricated edit. This is a
bounded two-book pass, not a general 7e mechanics conversion engine.

`skill_consolidation` may clear only the exact duplicate Торг 40 label/value
cells for Leon and Colin after checking the accepted decision, adjacent cell
pair, per-entity original values and final single Убеждение 40 pair. Colin's
surviving 32 becomes 40 in place. Empty `w:t` nodes are verified across the
OOXML parse/write round trip. A plain, attribute-free line break may precede a
selected `w:t` in the same run; its order remains unchanged, while page breaks,
pictures, fields, hidden runs and tracked changes remain unsupported.

The explicit `art_scope: preserve_original_drawings_only` is available only
for a source-bound field manifest with an empty art ledger and no art
insertions/removals. It conserves the original ordered drawing occurrences
and embedded-media bytes but does **not** assess source-art completeness. It
must not be used for the Fear opener-art pass. The two-book candidates contain
DOCX only; original PDF inputs are read-only and no HTML or PDF successor is
generated. Old-edition Resistance Table prose, MP-drain details and Kremlin's
plain POW check remain source-preserved exceptions, not converted mechanics.

## U6 API hardening

The manifest is parsed from one captured byte snapshot. That same snapshot is
used for the input map and report identity, and the live file is checked for
drift after all input snapshots and again before publication. Other consumed
authorities are likewise read once into snapshots. An ordinary ×5 or high-EDU
numeric operation must preserve every nonnumeric character in its exact span;
the accepted `ХАР`→`НАР` crosswalk is the only narrowly bound label exception.
Field and expression targets use effective inherited visibility from the
actual DOCX styles/defaults plus paragraph and run properties, so hidden text
cannot be edited through a valid leaf hash. A split-run expression requires
adjacent, direct, one-text-leaf Word runs with no intervening hyperlink,
break, field or unsupported inline construct. The actual Katerina expression
passes this stricter rule. These controls do not alter previously authored
candidate bytes; their exact original inputs and output payloads were
revalidated read-only under `audit/api-remediation/readonly-preflight-v03.json`.

The U6v04 boundary adds two further exact checks. Each characteristic span
must contain its complete numeric operand: a resealed edit of only one digit
inside `13` cannot claim to convert `13` by changing `3` to `15`. For a
split-run expression, the first selected fragment must reach the end of its
text leaf, every middle fragment must fill its leaf, and the last fragment
must start at the beginning of its leaf. Unrelated prose before the first
fragment or after the last remains permitted; visible text between selected
fragments does not. These two rules reject the independent critic's partial-
operand and three hidden-gap probes while the frozen three real manifests and
unchanged DOCX payloads still pass read-only preflight. Evidence is under
`audit/api-remediation-v04/`.

U6v05 extends the numeric boundary across the complete visible inline
sequence of a Word paragraph. Adjacent text leaves, runs and hyperlinks are
considered together; supported zero-width markers do not split a number.
Consequently, a selected `3` next to visible `1` cannot be converted as if it
were a complete characteristic `3`. Tabs and line breaks are delimiters, and
an unsupported inline construct adjacent to the operand fails closed. A full
`13` next to `; Удача: 75` remains valid. The independent critic's frozen
adjacent-run inputs and the three unchanged candidate manifests are checked
read-only under `audit/api-remediation-v05/`.
