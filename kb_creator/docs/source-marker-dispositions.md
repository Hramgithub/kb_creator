# Source-marker disposition input

`source_marker_dispositions` is an optional, sealed input for a reviewed semantic spec. It closes a reviewer-selected candidate domain; it does not classify historical specifications that omit the binding.

The spec binding is a relative file descriptor:

```json
"source_marker_dispositions": {"path": "marker-dispositions.json", "bytes": 123, "sha256": "..."}
```

The bound JSON uses schema `kb_creator.source_marker_dispositions.v1`, with `candidates` and `dispositions`. Each candidate and its one disposition repeat the exact `source_page`, `view`, `raw_index`, `reader_preimage_sha256`, and rendered source-page `visual` identity. A disposition is either `unordered_list_item` or `non_list`, and always has a visual-review rationale.

Authoring validates this input after it creates semantic units. A list disposition needs exactly one unordered-list unit owning the same `(view, raw_index)`, with valid Markdown list syntax and its declared item count. A non-list disposition cannot have list ownership. The guard reads selected source blocks and semantic source selectors; it never derives a role from marker letters or reader wording. Canonical source identity remains distinct from rendered or replaced reader strings.
