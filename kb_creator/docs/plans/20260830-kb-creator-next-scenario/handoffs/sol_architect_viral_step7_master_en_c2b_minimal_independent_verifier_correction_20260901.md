# Viral Step 7 MASTER_EN C2b minimal independent verifier correction

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `7 / C2b independent verifier and candidate sidecars`
- Timestamp: `2026-09-01 22:46:06 +03:00` (`Europe/Moscow`)
- Role: architecture/root-cause, repository policy `gpt-5.6-sol` / `high`
- Actual platform model/effort: unavailable
- Orchestrator policy owner: `/root`, repository-policy `gpt-5.6-sol` / `medium`; ownership did not transfer
- Assignment state: bounded architecture correction complete; current WIP remains unaccepted and no candidate execution is authorized
- Scoped override: the sole write is this immutable correction receipt; builder, verifier, tests, config, source, accepted reconstruction, candidate, plan/context/status, Git and release surfaces remained read-only
- Verdict: `READY_FOR_ENGINEERING`
- Elapsed time: approximately 43 minutes
- Token use: unavailable

## 1. Correction and precedence

This receipt corrects the disproportionate requirement in
`sol_architect_viral_step7_master_en_c2b_verifier_sidecar_contract_20260901.md`
(25,830 bytes / SHA-256
`F00428E34CC45C92A47F0D97643D89364946C7480D3F5C028E355CEDC134B14D`).
The original packet required the verifier to independently rebuild the complete
expected `MASTER_EN.md` and every sidecar. That would create a second publication
builder and duplicate the full reader planner. It is replaced by the bounded
package-verification design below.

The original CLI, absent-target atomic publication rule, closed topology,
canonical serialization, input/path/reparse rules, external-gate boundary and
role ownership remain in force except where this correction explicitly replaces
the provenance offset schema, verifier algorithm, error taxonomy, test set and
engineering definition of done. This is a simplification of implementation, not
a count-only or self-attestation verifier.

No user-owned decision is open. The accepted C2a reader and config semantics are
unchanged.

## 2. Current WIP evidence and exact gap

Read-only identities at architecture time:

| Surface | Bytes | SHA-256 |
| --- | ---: | --- |
| `build_scenario_master_en.py` | 68,003 | `4522168C7423EBB118F174B8240D4E1657B1991FC33250ECC6A2BDB122A62CEB` |
| `verify_scenario_master_en.py` | 5,251 | `37FB033F45815EB249BAD08B4E90EA71C0F3378A0B63A8682438901527829819` |
| `test_build_scenario_master_en.py` | 26,786 | `01BDFFFC6F32833E3EF5EF831A85F30775883C1E20B5E9B5B3C0687A58AD33DF` |
| `test_verify_scenario_master_en.py` | 1,319 | `E1482420EDEF0C1BBA760767FC62634E4B43A4A39F07226FE915768BE7F3C884` |

The compact baseline reproduces `44 passed in 9.00s`. The candidates directory
does not exist. The WIP already has a deterministic QA Markdown renderer and a
useful verifier topology scaffold. It is not complete because:

1. every unit's provenance `output_fragments` is empty;
2. source and structured offsets are Python string indices while the sidecar says
   only `utf8_bytes`;
3. the verifier trusts shallow counts (`168`, `107`, `123`) and does not close
   sidecar schemas or independently bind source semantics to candidate bytes;
4. builder metrics are presently literal values rather than derived ledgers;
5. normal publication contains a duplicate `stage.rename(destination)` path and
   has no candidate-level atomicity proof.

These are the only C2b correction targets. C2a assembly algorithms and scenario
config are not to be redesigned.

## 3. Minimal topology remains 130 files

The 130-file topology remains justified:

```text
MASTER_EN.md
MASTER_EN.provenance.json
SOURCE_DISPOSITION.json
ASSET_MANIFEST.json
MASTER_EN.qa.json
MASTER_EN.qa.md
INVENTORY.json
assets/<123 content-addressed files>
```

There are six sidecars and 123 assets, so the physical total is `1 + 6 + 123 =
130`. `INVENTORY.json` contains 129 rows because it cannot list itself. None of
the six sidecars is redundant:

- provenance binds source ranges, transformations and candidate ranges;
- disposition closes 124-page ownership policy;
- asset manifest binds origin, role and staged bytes;
- QA JSON is the machine-readable gate snapshot;
- QA Markdown is the deterministic human review projection required later;
- inventory closes physical bytes without a self-hash cycle.

The verifier enumerates physical nodes before reading inventory, rejects extra
or missing nodes, and applies the original traversal/symlink/junction/reparse and
canonical UTF-8/LF rules. No acceptance file, copied input, log, cache, temporary
render or staging directory may occur inside a candidate.

## 4. Corrected provenance contract

`MASTER_EN.provenance.json` keeps the original top-level purpose but replaces
the misleading single `offset_unit` with this exact object:

```json
{
  "char": "python_unicode_code_points",
  "byte": "utf8_bytes",
  "range": "zero_based_half_open"
}
```

The top key is `offset_contract`; `offset_unit` is forbidden. Python character
indices are internal navigation coordinates over decoded strings. Persisted byte
indices are independent coordinates over the exact UTF-8 bytes. Neither may be
derived by treating one as the other.

Each of the 168 unit rows retains the original exact keys
`anchor,binding_order,operations,source_fragments,output_fragments,asset_ids,xref_ids,structured_ids`.
For every non-empty source span that contributes reader text, `source_fragments`
has one exact row:

```text
fragment_id, page,
start_char, end_char, start_byte, end_byte,
sha256
```

The matching `output_fragments` row has exactly:

```text
fragment_id,
start_char, end_char, start_byte, end_byte,
sha256
```

`fragment_id` is deterministically `<anchor>/p<page-3d>/<span-ordinal-3d>` in
the source-span order for that owner. It is unique across the package. There is
exactly one output row for each listed source row and no orphan output row. An
empty source span is not serialized as emitted provenance; its disposition must
instead be accounted by the independently recomputed C1 generated ledger.

For a decoded string `text` and any persisted endpoint `(char, byte)`, the
verifier requires:

```text
0 <= char <= len(text)
byte == len(text[:char].encode("utf-8"))
```

It then requires the byte slice and character slice to encode identically and
requires `sha256` over those exact UTF-8 bytes. This check is applied separately
to every accepted page and to `MASTER_EN.md`; it detects non-ASCII offset drift.

Semantic `structured_units.fragments` replace each old `source_start/source_end`
and `emitted_start/emitted_end` with explicit `*_start_char`, `*_end_char`,
`*_start_byte`, `*_end_byte` fields. Attached-note evidence uses the same fields
plus its selector and occurrence. The 11 configured notes must therefore be
bound to both coordinate systems and exact hashes. Visual-form rows remain
range-free and retain exact asset/review/occurrence evidence. All provenance
objects remain closed; unknown or legacy offset keys fail.

## 5. Minimum sufficient independent verifier

The verifier is process-isolated. It may not import, execute, dynamically load,
monkeypatch or use a shared module from the builder. It independently parses the
contract, publication config, 124 accepted Markdown pages, source PDF identities,
candidate tree and all six sidecars. It may reproduce small deterministic
primitives (canonical JSON, hashing, exact locator resolution, UTF-8 offset
conversion and the fragment transformation interpreter below); it must not
contain a reader assembler, fragment emission planner or function that returns
an expected whole `MASTER_EN.md`.

Verification is ordered and fail-closed:

1. Validate CLI/input roots, exact live hashes and accepted-reconstruction
   inventory; apply traversal and reparse checks before resolution.
2. Enumerate the candidate physically. Require the exact 130 files, exact root
   names, exactly 123 regular content-addressed asset files and no extras.
3. Decode/canonicalize the six sidecars and validate their complete closed
   schemas. Independently enumerate the 129 inventory-scope files and recompute
   every row, count, byte size, hash and inventory digest.
4. Resolve config locators against accepted pages using a verifier-owned compact
   resolver. Recompute the 124-page disposition projection, all block identities,
   one-owner/one-consumption and the exact conservation ledger `1935 = 1862 +
   73`, with `0` unowned, duplicate and unauthorized-suppression blocks. The
   sidecar summary is comparison data, never authority.
5. Parse `MASTER_EN.md` into owner blocks by exact anchor marker and immediately
   following heading. Require all 168 anchors once, in config order, with exact
   level/title and no undeclared anchor. This parser reads the produced package;
   it does not synthesize an expected reader.
6. Recompute every unit's source range, char/byte endpoints and hash from accepted
   pages. Independently transform each source fragment using Section 6 and compare
   the resulting bytes to the matching candidate output range. Require output
   ranges to lie inside the declared owner block, occur in source/placement order,
   be pairwise non-overlapping and have exact union with the package's complete
   set of source-derived emitted mappings. No source mapping may be owned or
   consumed twice.
7. Classify every remaining byte in each owner block as exactly one of: anchor
   marker, exact configured heading, configured generated-xref line, configured
   asset-reference line, source-derived output fragment, canonical `LF LF`
   separator, or the single terminal `LF`. Overlap and unclassified nonseparator
   bytes fail. This local layout grammar rejects resealed inserted/deleted/reordered
   prose without reconstructing the whole reader.
8. Recompute all 237 xref ids from config and candidate owner blocks. Require all
   196 generated rows in their exact owners, all 41 source rows/42 segments in the
   exact transformed fragments, each internal target among the 168 anchors, and
   the configured external-text segment unlinked. The union of provenance xref
   ids is exact and one-owner/one-consumption.
9. Resolve the 29 structures and 11 attached notes independently from accepted
   source/config. Semantic region/note candidate ranges must be contained by their
   owning source-output mapping and match exact transformed bytes/tokens/order;
   visual forms must point to their configured asset exactly once in their owner.
   The structured-id union is exact and unique.
10. Recompute the 41 physical handout ownership rows, 107 reader assets, 16
    evidence-only assets and all 123 manifest rows. Reader assets occur exactly
    once in their owner; evidence-only assets occur zero times. Accepted assets
    byte-equal their immutable reconstruction origins. The verifier privately
    rerenders only the two declared source-PDF assets (p1 and p124) with the pinned
    Poppler/Pillow rules when performing a real production verification and
    byte-compares them; temporary outputs stay outside the candidate and are
    normally removed. MinerU and `SELECTED_OVERLAY.pdf` are never used.
11. Independently derive QA metrics from the preceding ledgers: `124` pages,
    `168` anchors, `237` xrefs, `41/42` source xref rows/segments, `41` handouts,
    `29` structures, `11` notes, `107/123` reader/total assets, and the complete
    `1935/1862/73/0/0/0` conservation ledger. Compare all QA JSON values and gate
    states, require process/external gates pending, regenerate QA Markdown with a
    verifier-local small renderer, and compare its bytes.

A correctly resealed mutation therefore cannot pass merely because its new hash
appears in inventory: it must also satisfy independent source identity,
provenance/range/transform, local grammar, xref, structure, asset and QA facts.

## 6. Exact fragment transformation rules

For each resolved source span, the verifier applies only this ordered rule set,
derived afresh from config rather than trusted from provenance:

1. For each applicable exact source-xref row, locate its exact source line once;
   replace each declared segment in declared order with either
   `[reader_text](#target_anchor)` or unlinked `reader_text` when `emit_link` is
   false. No fuzzy or normalized match is allowed.
2. Apply locator actions inside the span: `replace_heading` and
   `consume_continuation_label` delete the exact locator line; and
   `replace_label_retain_remainder` deletes only the exact selector prefix.
3. Remove only a leading `<!-- source-page-NNN -->` line.
4. Remove only source image-Markdown lines matching the accepted C2a rule; assets
   are verified separately through the manifest and owner grammar.
5. Increase remaining Markdown heading depth by exactly one, capped at level 6.
6. Apply only trailing `rstrip()` to the complete transformed span.

The result must equal the candidate output fragment byte-for-byte. No general
Markdown normalization, punctuation cleanup, whitespace folding, OCR repair,
case-folding or editorial rewrite is permitted. Join separators, headings,
generated links and asset lines are verified by the local owner-block grammar,
not folded into this interpreter.

## 7. Reduced stable errors

Expected failures return exit `1`, empty stdout and one line `CODE: detail` on
stderr. Details are stable candidate-relative paths, ids or JSON pointers, never
device paths. First phase wins; items within a phase use ordinal paths or config
order.

| Order | Code | Boundary |
| ---: | --- | --- |
| 1 | `E_C2B_PATH` | CLI, wrong parent, traversal, absolute/drive/UNC/backslash, symlink/junction/reparse |
| 2 | `E_C2B_TOPOLOGY` | missing/extra/non-regular node, forbidden acceptance/staging content, 130-file closure |
| 3 | `E_C2B_SCHEMA` | encoding/canonical JSON, missing/unknown/type/enum/offset-shape error |
| 4 | `E_C2B_IDENTITY` | contract/config/PDF/reconstruction identity or accepted inventory mismatch |
| 5 | `E_C2B_INVENTORY` | physical 129-row/count/bytes/hash/digest mismatch |
| 6 | `E_C2B_PROVENANCE` | char/byte/hash, union, range, owner, overlap or transformation mismatch |
| 7 | `E_C2B_SEMANTIC` | anchor/heading/handout/order/local-grammar/noise/protected-text mismatch |
| 8 | `E_C2B_XREF` | 237-row owner/segment/link/target/external-text mismatch |
| 9 | `E_C2B_STRUCTURE` | 29 structures, 11 notes, tokens/order/visual occurrence mismatch |
| 10 | `E_C2B_ASSET` | 107/16/123 ownership/reference/source/rerender/type/dimension mismatch |
| 11 | `E_C2B_QA` | derived metrics, pending gate or deterministic Markdown mismatch |
| 12 | `E_C2B_ATOMIC` | builder-only occupied target, failed staging or non-atomic publication boundary |

These twelve risk-class codes replace the former sixteen implementation-phase
codes. They are not a selector permutation taxonomy.

## 8. Compact behavior-driven tests

Keep the 44 passing C2a/WIP tests. Add exactly these eight candidate-level test
methods; representative mutations may be subtests, but there is no per-row or
historical mutation matrix:

1. `test_candidate_build_closed_deterministic_130_129` — two fresh fixture
   targets produce byte-identical relative inventories, exact six sidecars,
   130/129 topology and no acceptance file.
2. `test_candidate_build_atomic_absent_target_and_preserved_failure` — occupied
   target is untouched; injected post-staging failure creates no target and
   reports/preserves only the private sibling staging directory; one rename occurs
   on success.
3. `test_verifier_isolated_positive_and_closed_schema` — verifier passes the
   fixture with builder import/execution disabled; one unknown sidecar key fails.
4. `test_verifier_path_topology_and_first_error_precedence` — one traversal or
   reparse case, one extra/acceptance file, and a two-fault topology-plus-bad-JSON
   case prove `PATH -> TOPOLOGY -> SCHEMA` precedence.
5. `test_verifier_identity_inventory_and_resealed_semantic_boundary` — raw reader
   mutation fails inventory; correctly resealed mutation crosses inventory and
   fails semantic/provenance rather than passing; one live input identity mismatch
   fails identity.
6. `test_verifier_provenance_char_byte_union_transform_and_xrefs` — a real
   non-ASCII endpoint is checked in both units; representative wrong byte offset,
   overlap/owner swap, transformed text mutation and xref target/external-link
   mutation fail the documented codes.
7. `test_verifier_structures_notes_assets_and_private_render` — one removed note,
   one structured token-order mutation, one asset-owner/reference mutation and
   one resealed render substitution fail; the renderer seam is invoked only for
   the two source-PDF rows.
8. `test_verifier_qa_metrics_pending_gates_and_markdown` — a derived count mismatch,
   forged pending gate and QA Markdown drift fail `E_C2B_QA`.

The exact new C2b behavior set is eight methods. Test-count arithmetic is not an
acceptance substitute, but with the unchanged 44-method baseline the expected
collection is 52 passing tests. The real Poppler render is reserved for the
later frozen execution gate; unit tests use the existing deterministic renderer
seam. Do not run or recreate 371/119/490.

## 9. Terra WIP migration and allowed files

Next owner is Terra/medium reusable implementation. Exact permitted writes:

1. `kb_creator/scripts/build_scenario_master_en.py`
2. `kb_creator/scripts/verify_scenario_master_en.py`
3. `kb_creator/tests/test_build_scenario_master_en.py`
4. `kb_creator/tests/test_verify_scenario_master_en.py`
5. new immutable
   `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_c2b_minimal_independent_verifier_20260901.md`

Migration from the current WIP is deliberately local:

- Builder: retain accepted C2a resolver/reader/assets and the QA Markdown helper;
  populate provenance from the existing emitted ledger; convert every serialized
  source/output/structured endpoint into explicit char plus UTF-8 byte fields;
  derive metrics from live ledgers; remove the duplicate rename path; preserve
  same-parent staging and absent-target publication.
- Verifier: retain useful CLI/target/topology/inventory scaffold; replace shallow
  count checks with the independent phases above. Add only a compact exact locator
  resolver, fragment transformer, owner-block classifier and sidecar validators.
  Do not copy `assemble_reader`, `fragment_emission_plan`, `structured_resolver`
  wholesale or create a shared builder/verifier helper.
- Tests: retain the 44 baseline tests and add the exact eight methods in Section
  8. Fixture construction may call the builder subprocess; verifier assertions
  always run in a separate process with builder execution disabled after the
  fixture exists.

Required commands:

```powershell
python -B -m py_compile kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py
python -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py
git diff --check -- kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py
```

Terra must not execute the normal production candidate command. It may use only
temporary fixture targets. No config/source/reconstruction/plan/context/candidate,
dependency, Git or release write is authorized.

## 10. Reduced definition of done and next action

Engineering is `PASS_C2B_MINIMAL_VERIFIER` only when all of these are true:

1. the four implementation/test files and one receipt are the only writes;
2. the verifier has no builder import, execution, dynamic loading or shared helper;
3. candidate topology is exactly 130/129 and all six sidecars are closed/canonical;
4. all source-emitted mappings have nonempty one-to-one source/output provenance,
   valid char+byte ranges, exact hashes, complete union, exact ownership and no
   overlap;
5. the independent transformer plus owner-block grammar rejects a correctly
   resealed prose mutation without constructing expected whole-reader bytes;
6. independent ledgers reproduce `168` anchors, `237` xrefs, `29` structures,
   `11` notes, `41` handouts, `107/123` assets and
   `1935/1862/73/0/0/0` conservation;
7. the only verifier-side rendering is the two declared source-PDF assets;
8. the 44 baseline plus exact eight C2b tests pass, compile and diff checks pass,
   and no durable candidate exists.

After Terra, the next owner is independent GPT-5.5/high implementation review,
read-only except one review receipt. It must inspect for hidden whole-reader
reconstruction or builder trust and reproduce the positive fixture plus one
resealed provenance/semantic mutation, one asset mutation and one QA mutation.
This remains implementation review, not final release review.

Only after that review accepts may Luna/medium receive a frozen production
execution packet for two new candidate ids and separate-process verification.
Candidate creation, visual QA, promotion, release review, translation, HTML/PDF,
Git and user acceptance remain later gates.

## Files checked / changed

Checked read-only: canonical plan/context/NEXT_CHAT Step 7 state; original C2b
packet; accepted C2a baseline referenced by it; current builder, verifier and both
focused tests; current no-candidate boundary.

Changed: only this receipt. No candidate was created and no existing file was
modified.

