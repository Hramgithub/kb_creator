# Number 7 Dream historical review evidence

This directory preserves byte-distinct user-reviewed files from superseded
publication runs. It is historical provenance, not the current publication
authority or a release. The current, offline-verified production candidate is
`../production/`.

`MANIFEST.json` records each archived file's original run-relative path,
byte count and SHA-256. The three ArtView decision files are the user's
original accepted exports from runs 06, 18 and 25. Run28 holds the first
human-edited DOCX revision; the later edited DOCX is already in the current
production package. Run29 holds an explicitly accepted PDF whose rendered
pages match run30, but whose bytes differ from the current accepted PDF.

The adjacent acceptance receipts are retained unchanged. They refer to their
original run-local stage evidence and are **not** a self-contained historical
verification graph after working-run cleanup. Do not rebind them to run30 or
present them as its release approval. The accepted run25 HTML itself is in
the current package byte-for-byte; only its old receipt is archived here.

PDF and DOCX payloads use Git LFS; all archived content bypasses Git text
normalization. Before removing source runs, verify every `MANIFEST.json` row
against both this archive and its still-existing source file.
