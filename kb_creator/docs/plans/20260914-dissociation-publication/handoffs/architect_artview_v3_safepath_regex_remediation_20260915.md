# Architect receipt: ArtView v3 `safePath` regex remediation

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `artview-v3-safepath-schema-remediation`
- Role: architect / micro architecture audit
- Policy role/model/effort: `gpt-5.6-sol`, `high`
- Actual platform model/effort: unavailable
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: none for architecture; the goal's engineering Sol/high override remains canonical
- Timestamp: `2026-09-15T12:18:13+03:00`
- Elapsed time: approximately 15 minutes
- Token use: unavailable
- Scope: ArtView v3 portable path grammar, schema compilation and matching runtime parity only
- Result: blocker reproduced and narrow remediation specified; no schema, parser, config, contract, run, canonical state, or Git state was changed
- Files changed: this receipt only

## Decision

**GO** for the bounded schema/runtime/test remediation below.

**NO-GO** for publication contract authoring, publication preflight, or live
Stage 10 until the corrected schema passes `Draft202012Validator.check_schema`,
the Dissociation profile passes instance validation, runtime parity tests pass,
and an independent implementation review closes the change.

## Root cause

Current JSON source in
`kb_creator/contracts/scenario_artview_profile.v3.schema.json` contains
`[/\\]`. JSON decoding reduces that to the regex fragment `[/\]`, where the
single backslash escapes the class terminator. Python `re` therefore reports
`missing ), unterminated subpattern at position 14`, and jsonschema cannot
compile the schema.

A literal compile-only repair would use `[/\\\\]` in JSON to produce
`[/\\]` after decoding. That would preserve the original apparent intent of
allowing both slash styles, but it would retain weaker and inconsistent path
semantics: the schema would still allow internal backslashes, ADS colons, dot
segments and duplicate separators while v3 output-root runtime rejects several
of those. The reviewed portable authority schemas use normalized forward-slash
paths and reject backslash, colon, dot/dotdot traversal and unsafe Windows
components. ArtView v3 should follow that contract.

## Exact portable `safePath` contract

Use this exact JSON string as `$defs.safePath.pattern`:

```json
"^(?!\\s)(?!.*\\s$)(?!/)(?!.*//)(?!.*(?:^|/)\\.\\.?(?:/|$))(?!.*[:\\\\\\x00-\\x1F])(?!.*(?:^|/)(?:[cC][oO][nN]|[pP][rR][nN]|[aA][uU][xX]|[nN][uU][lL]|[cC][oO][mM][1-9]|[lL][pP][tT][1-9])(?:\\.|/|$))(?!.*[ .](?:/|$))[^/]+(?:/[^/]+)*$"
```

After JSON decoding, the regex is:

```text
^(?!\s)(?!.*\s$)(?!/)(?!.*//)(?!.*(?:^|/)\.\.?(?:/|$))(?!.*[:\\\x00-\x1F])(?!.*(?:^|/)(?:[cC][oO][nN]|[pP][rR][nN]|[aA][uU][xX]|[nN][uU][lL]|[cC][oO][mM][1-9]|[lL][pP][tT][1-9])(?:\.|/|$))(?!.*[ .](?:/|$))[^/]+(?:/[^/]+)*$
```

Semantics are host-independent:

- nonempty, repository-portable relative path;
- `/` is the only serialized separator on both Windows and POSIX;
- no leading/trailing whitespace, absolute/UNC path, duplicate separator,
  `.` or `..` segment;
- no colon or backslash, hence no drive-qualified path, URI or NTFS ADS;
- no ASCII control character `U+0000` through `U+001F`;
- no Windows reserved device component, case-insensitively, including an
  extension (`CON`, `nul.txt`, `a/COM1.json`);
- no component ending in a space or dot;
- Unicode and internal spaces remain allowed.

This grammar applies equally to `output_root`, input file records and image
records. Filesystem containment, identity, reparse and existence checks remain
runtime responsibilities after lexical validation.

## Runtime parity

`scenario_artview._v3_output_root()` already rejects backslash, colon,
absolute paths and dot/dotdot components. `_v3_resolve()` currently calls the
legacy `safe_relative()`, which normalizes backslashes and is weaker for ADS,
dot components, duplicate slashes, controls, reserved devices and trailing
dot/space.

Do not change the shared legacy `safe_relative()` and do not alter ArtView v2.
Add one v3-only lexical validator/compiled constant with the decoded pattern
above, and call it from both `_v3_resolve()` and `_v3_output_root()` before any
`Path` construction or filesystem access. It returns the unchanged normalized
forward-slash string; it must not convert a rejected Windows spelling into an
accepted path.

Minimal implementation ownership:

- `kb_creator/contracts/scenario_artview_profile.v3.schema.json`;
- `kb_creator/scripts/scenario_artview.py`;
- `kb_creator/tests/test_scenario_artview_v3.py`.

No publication-control, contract-author, config, decision, acceptance,
reconstruction or legacy schema file is required.

## Exact verification matrix

Add an unconditional test that JSON-loads the schema, runs
`re.compile(schema["$defs"]["safePath"]["pattern"])`, and asserts the exact
decoded regex string. When `jsonschema` is available, also require
`Draft202012Validator.check_schema(schema)` and validate the real authored
Dissociation profile.

Schema and v3 runtime must both accept:

- `profile.json`
- `assets/map-01.jpg`
- `кисти/карта 01.webp`
- `a.b/c-d_1.png`

Both must reject before filesystem lookup/write:

- empty string;
- `/abs`, `\\abs`, `C:/x`, `C:\\x`, `//server/share`, `\\\\server\\share`;
- `../x`, `a/../x`, `./x`, `a/./x`;
- `a//b`, `a/`, `a\\b`;
- `a.json:stream`, `https://host/x`;
- leading/trailing whitespace and `a/trail.`, `a/trail `;
- `CON`, `nul.txt`, `a/COM1.json`;
- embedded NUL, tab, newline and another representative `U+0001` control.

Test every unsafe value against all three schema use sites (`output_root`, one
input `path`, one image `path`) and direct v3 runtime helpers. Retain the
existing absolute-output/no-write, containment, reparse, exact source-graph and
ArtView v2 regression tests.

Acceptance criteria:

1. schema parse, Python regex compile, Draft 2020-12 `check_schema`, and real
   Dissociation profile validation all pass;
2. schema/runtime outcomes are identical for the complete matrix;
3. rejection occurs before output creation or source file lookup;
4. current Dissociation profile bytes are unchanged and all its paths pass;
5. focused ArtView v3, publication schema/registry and contract-author tests
   pass, followed by independent implementation review.

## Identity impact

Current defective schema SHA-256 is
`382AC7494813F65FD6E3CF5F93F5512A1EED783EF2CBCB8A768BB40AEEBB841F`.
The corrected schema necessarily has a new SHA.

`publication._implementation()` includes this schema, so a persisted
`kb_creator.publication_run_spec.v1` would become stale and must never be
resumed after the change. Read-only census found no publication RunSpec v1
instance: the only matches are the schema's own `$id`/`const`. The Dissociation
publication contract and publication run root are still absent, so no current
contract/run is invalidated.

The authored Dissociation `configs/artview/profile.json` contains only portable
forward-slash paths conforming to the stronger grammar. It does not embed the
ArtView schema file hash and need not be mutated. The future publication
contract will bind the profile's unchanged file identity; the future run will
bind the corrected implementation/schema inventory. Prior test receipts are
historical evidence and require focused rerun, not mutation.

## Findings and next action

- P0: none.
- P1: the malformed JSON escaping makes the ArtView v3 schema uncompilable and
  blocks the required config gate.
- P2: a compile-only slash escape would leave schema/runtime portable-path
  parity open; the v3-only common grammar above closes it without legacy drift.

Files checked: repository instructions/governance, active plan/context, config
author receipt, ArtView v3 schema/parser/tests, publication schema tests, and
the reviewed portable-path schemas. A read-only in-memory probe compiled the
proposed decoded regex, passed Draft 2020-12 `check_schema`, accepted all four
safe cases and rejected the full unsafe sample set. No repository test suite or
publication action was run.

Next action: bounded engineer applies the three-file remediation, runs the
matrix and focused regressions, then an independent critic reviews it. Only
after closure may the config author resume schema validation, generic contract
authoring and read-only publication preflight.

## Final GO / NO-GO

- Three-file v3 remediation and tests: **GO**.
- Compile-only escaping fix without runtime parity: **NO-GO**.
- Contract authoring/preflight before independent closure: **NO-GO**.
- Config mutation, live Stage 10, acceptance, later publication, commit/push:
  **NO-GO**.
