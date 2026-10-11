# Reviewed reader successor

> Historical dual-output contract. The `revise_reviewed_reader` writer is retired
> because it creates HTML beside DOCX. It now fails before output creation. For a
> current reviewed Word successor use
> `python -m kb_creator.scripts.revise_reviewed_docx`; keep this page for reading
> earlier manifests and reports only.

`revise_reviewed_reader` makes a new DOCX, HTML and asset package from an exact
human-reviewed reader. It is an artifact successor. It does not reconstruct the
source master, rerun OCR, translate text or approve a book.

The caller freezes a versioned JSON manifest after reviewing issue decisions and
source graphics. The tool checks every input hash and every source graphic row
before creating an output root. It then edits the Word OOXML directly: unchanged
parts, image binaries, comments, replies, styles, links and bookmarks remain in
place. It inserts a new image relationship, media part and uncropped inline
drawing for each approved art operation. HTML gets the matching figure and a
copy of every original asset. Existing Word paragraphs and image occurrences
retain their order.

## Command

Use the Codex bundled Python selected for the workspace and UTF-8 mode:

```powershell
python -X utf8 -m kb_creator.scripts.revise_reviewed_reader `
  --manifest decisions-v01.json `
  --docx reviewed/document.docx `
  --html reviewed/document.html `
  --assets reviewed/assets `
  --source-pdf original.pdf `
  --output-root successor-v01
```

The output root must be new and disjoint from every input. It contains
`document.docx`, `document.html`, `assets/` and `revision-report.json`. A failed
preflight creates no output root. A failed staged build removes its staging
directory. The report says `validated_candidate` and `accepted: false`; it
records exact input/output SHA-256 values, operations, physical source pages,
reader stories, graphic coverage, preservation checks and limitations.

## Manifest contract

Use schema `kb_creator.reviewed_reader_revision.v1` and provenance
`reviewed_artifact_successor`. `inputs` supplies `docx_sha256`, `html_sha256`,
`source_pdf_sha256` and `existing_assets`, an exhaustive mapping from safe
`assets/...` paths to hashes. `stories` is an ordered list of `story_id`, exact
`word_bookmark` names and exact `html_anchor` IDs. The next story start closes
the previous story's placement region. Both formats must have the same story
order.

`source_graphic_ids` is the independently reviewed source-art domain, not a
list derived from the current HTML or Word images. `source_graphics` has exactly
one row for each ID. A required row records `graphic_id`, `story_id`, physical
`source_page`, `disposition: must_include`, selected image `sha256` and
zero-based `occurrence_ordinal` among same-binary images in that story. This
ordinal keeps repeated artwork occurrences distinct. A deliberately omitted
row uses `disposition: exclude`, `reviewed: true` and a specific `reason`.
`reference_only` cannot satisfy required reader coverage. The reviewed domain
must include retained openings, newly recovered scenes and any other meaningful
graphics in the agreed scope. For Fear, the frozen art specification identifies
26 source opening scenes, 23 missing from the current reader; the caller must
freeze those 26 IDs before running a successor. A matching HTML/Word count by
itself is insufficient.

Every operation has a unique issue or graphic ID. An unchanged issue uses
`kind: keep`, `disposition: keep`, and a reason; a blank or deleted comment is
not a decision. A text operation uses `kind: text`, `disposition: replace`,
`story_id`, the story's Word/HTML anchors, `expected_text`, exact `target_text`
and `replacement`. For ordinary paragraphs or table cells without their own
IDs, include `expected_text_sha256` plus a `selector`: Word
`kind: exact_paragraph`, `expected_matches`, `ordinal`; HTML
`kind: exact_element`, `tag` (`p`, `td`, `th` or `li`), `expected_matches`,
`ordinal`. Each selected paragraph must equal the full expected text. The target
must occur once within one plain Word text node and one HTML text node. Text
crossing Word runs, fields, drawings, controls or hidden topology is rejected;
unrelated bold/italic runs and comment markers remain intact. Without a
selector, the operation addresses the anchored story paragraph itself.

An art operation uses `kind: art`, `graphic_id`, `story_id`, the story's anchors,
physical `source_page`, `source_image`, exact selected-byte `sha256`, pixel
`dimensions`, a new safe `asset_path`, and `insertion`. The source image is
read-only; the original PDF is separately hash-bound. The caller must record
the inspected PDF object or full-page exception and the selection evidence in
its frozen decision artifact. PNG and JPEG are supported. Word width defaults
to 5.5 inches and can be reduced with `word_width_inches`; height is calculated
from native dimensions, with no crop. `after_anchor` is suitable only when the
story heading itself is the approved insertion point.

For a story opener whose byline and tags must precede the artwork, use
`insertion: after_exact_text` with a `position` object. It has matching
`word_expected_text` and `html_expected_text`, their respective SHA-256 values,
and the same exact selectors described above. This names the final paragraph
or cell of the opener group within the story. The selected Word and HTML text
must agree; changed or ambiguous context fails. Physical source page and reader
position are reported separately.

## Validation and limits

Preflight rejects changed DOCX, HTML, source PDF, original asset or selected
image hashes; unsafe paths; aliases and occupied output roots; missing or
ambiguous anchors; unsupported text topology; unreviewed exclusions; and
missing or misplaced Word/HTML artwork. Post-write checks inspect the written
OOXML and HTML, source-art coverage, uncropped dimensions, original media and
comment/thread part bytes, bookmark/hyperlink/comment markers, original artwork
occurrence order, and every unchanged paragraph in order. A failed check never
labels a package accepted.

The report is structural evidence, not layout approval. Render the successor
with the bundled document renderer and visually inspect every changed page,
including each new picture and the surrounding translated opener group. Native
comments require structural checks because headless PDF rendering may omit
them. Independent QA and critic review remain separate. When prior masters or
replay inputs are unavailable, this route cannot establish their historical
lineage or repair an upstream selection defect.
