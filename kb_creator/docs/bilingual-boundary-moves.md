# Reviewed bilingual boundary moves

`python -m kb_creator.scripts.move_bilingual_page_spans` creates a fresh preliminary bilingual successor from exact reviewed RU span moves. It is transport automation: it does not translate text, infer unit ownership, validate source binding, or accept a book.

The command needs `--pages`, `--manifest`, `--plan`, and an absent `--output`. It rejects invalid input before creating the output directory.

## Plan v1

The JSON document has exactly these fields:

```json
{
  "schema": "kb_creator.bilingual_boundary_moves.v1",
  "predecessor": {"manifest": {"path": "MANIFEST.json", "bytes": 1, "sha256": "..."}, "pages": [{"path": "page-001.json", "bytes": 1, "sha256": "..."}]},
  "page_count": 200,
  "moves": [],
  "whitespace_edits": []
}
```

`predecessor.pages` covers every `page-NNN.json` exactly once. Rows must use the five-field bilingual page shape and have the matching English SHA-256. A move contains `source_page`, `target_page`, `source_span` (`start_byte`, `end_byte`), exact `source_text` and SHA-256, `target_insert_byte`, whitespace-only `target_suffix`, and a nonempty rationale. Coordinates are UTF-8 bytes in the immutable predecessor RU field.

`whitespace_edits` are optional, explicit `{page, span, replacement, rationale}` entries. Both the replaced span and replacement must be whitespace only. The helper rejects path escape, stale identities, noncharacter UTF-8 boundaries, same-page moves, overlapping source edits, and conflicting insertions.

The successor contains copied byte-identical unaffected pages, changed page JSON, an archived reviewed plan, and a manifest with predecessor/output identities and span-level conservation evidence. Its state is always `preliminary_boundary_successor_pending_source_binding`; a later exact source binding and reviewer-authored page map remain required.

The manifest proves construction at two levels: each moved source span has its exact successor destination byte span and SHA-256, while every inherited untouched byte fragment records its predecessor and successor span, hash, and order. A separate non-whitespace character-multiset check catches loss or duplication across the transport; it does not claim semantic equivalence or translation validation.

The helper may operate on a reviewed preliminary page set before final R1 exists. That successor remains preliminary. When R1 arrives, its English changes still require review and the eventual binder input must be bound to final R1 identities; this helper cannot transfer that authority.

The helper parses and checks each input from captured bytes, then uses that same
snapshot for composition and reported input identities. The archived plan is the
exact parsed byte sequence. A later external path change does not substitute a
new version into an already validated operation.
