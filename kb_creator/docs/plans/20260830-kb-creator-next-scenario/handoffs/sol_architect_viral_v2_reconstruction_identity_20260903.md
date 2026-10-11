# Viral v2 reconstruction-package identity — architecture receipt

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `sol_architect_viral_v2_reconstruction_identity_20260903`
- Role: architecture/root-cause analysis, repository profile `gpt-5.6-sol` / high
- Orchestrator policy owner: main chat, `gpt-5.6-sol` / medium
- Assignment state: `platform-unverified`; scoped override: `none`
- Timestamp: `2026-09-03T03:59:06+03:00`

## Scope and result

- Scope: specify the smallest closed v2-only contract that binds the accepted,
  immutable Viral reconstruction v4 without inventing or adding an input
  `INVENTORY.json`.
- Result: the current v2 interface is wrong, not the accepted package. Replace
  the single-file `document.reconstruction_inventory` identity with the
  aggregate directory identity `document.reconstruction_package` defined below.
- V1 configuration, v1 execution, accepted v4 bytes, candidate-output inventory,
  ledgers, candidate roots and Git remain unchanged.
- Terminal result: `READY_FOR_V2_RECONSTRUCTION_IDENTITY_IMPLEMENTATION`.

## Evidence and root cause

The accepted v4 root is
`kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`.
It contains `377` regular files, `41,079,424` bytes and no root
`INVENTORY.json`. Replaying the accepted v1 aggregate algorithm produces
`68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
The three child directories are `assets`, `decisions` and `pages`; none is empty
or a reparse point.

The v1 config already binds these exact facts under `accepted_reconstruction`.
The v2 builder and independent verifier instead require
`document.reconstruction_inventory` to identify a physical file named exactly
`INVENTORY.json` whose parent is the CLI package. The author helper follows that
invalid interface and therefore fails before config output. Adding the missing
file would change the accepted aggregate identity and mutate an immutable input.

Checked identities:

- task packet:
  `FBC914A6EBF7A4C56A0F9FD4D17F8882E7175248696FE469FAA562C02DF66C09`;
- frozen `publication_config_v1.json`:
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`;
- current builder:
  `8A0639CD1BDA528DD090805A5F56F30D72BD88402AD64887F13584E4194D2020`;
- current independent verifier:
  `97CB0505CC5BE0D05A9D1E07A6D9E8235C4F7389449C6704FD70303F75D76F5B`;
- blocked author helper:
  `7F53462E27CE426D844BD80078D1AB55755391C32C751020FB13831E6BE4BFCC`;
- blocked engineering receipt:
  `3C99B1DAFFB423F60DC94C6A29649C1A5BDC8E6311CD20BEBCC46E0442A1AA42`.

## Decision: exact closed JSON contract

For schema `kb_creator.master_en_publication.v2`, the exact closed keys of
`document` become:

```json
{
  "audit_scope": [1, 2, 3],
  "reader_scope": [1, 2, 3],
  "generated_navigation": {
    "operation": "generated_navigation_replaces_source_toc",
    "source_identity": "..."
  },
  "source_pdf": {
    "path": "...",
    "bytes": 20718150,
    "sha256": "0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05"
  },
  "reconstruction_package": {
    "root": "kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4",
    "file_count": 377,
    "total_bytes": 41079424,
    "inventory_algorithm": "SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>",
    "inventory_sha256": "68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83"
  }
}
```

The abbreviated page arrays above illustrate placement only; their existing
exact `1..124` and `1..122` requirements do not change.

`reconstruction_package` is a closed object with exactly the five shown keys:

- `root`: non-empty, safe repository-relative POSIX path;
- `file_count`: positive integer, with booleans rejected;
- `total_bytes`: positive integer, with booleans rejected;
- `inventory_algorithm`: the exact constant shown above;
- `inventory_sha256`: exactly 64 uppercase hexadecimal characters.

No alias, fallback, optional legacy v2 key, physical input inventory path or
additional object key is admitted. In particular,
`document.reconstruction_inventory` becomes invalid for v2. This is safe because
v2 has no accepted publication config yet. V1 dispatch and its closed schema are
unchanged.

## Canonical aggregate algorithm

The builder and verifier must implement this algorithm independently; the
verifier must not import or execute builder code.

1. Resolve the checkout root from the publication-config location as today.
2. Validate `root` lexically before filesystem access. Reject an absolute path,
   empty segment, `.`, `..`, backslash, drive/colon syntax or any path whose
   strict resolution escapes the checkout.
3. Strictly resolve the configured directory and the CLI
   `--reconstruction-package`. Both must be directories and their resolved paths
   must be identical.
4. Before hashing, reject the configured root or any descendant that is a
   symlink, junction/reparse point, device or other non-regular/non-directory
   entry. Reject an empty directory because v1 does not encode directory rows;
   this prevents an unsealed topology change invisible to the aggregate.
5. Recursively enumerate every regular file under the root. Do not exclude any
   basename. In particular, an input file named `INVENTORY.json`, if introduced,
   is ordinary hash material and would invalidate the accepted v4 identity.
6. For each file, form a path relative to the package root using `/`, without
   `./`. Sort these path strings ordinally by Unicode code-point sequence, with
   no locale, case folding or normalization.
7. Read each file as raw bytes once. Its row is exactly
   `relative_path<TAB>decimal_byte_count<TAB>UPPER_SHA256<LF>`. File bytes and
   filenames receive no Unicode, EOL or content normalization.
8. Concatenate all row bytes encoded as UTF-8. The package inventory is the
   uppercase SHA-256 of this payload. `file_count` is the number of rows and
   `total_bytes` is the sum of their raw byte lengths.

On the stable accepted v4 this algorithm is output-compatible with the v1
algorithm and must reproduce the three fixed values above. Empty directories
are not assigned a new row format; they are rejected, preserving the accepted
v1 digest rather than defining a second digest dialect.

## Builder validation and first-error contract

V2 validation is fail-closed and must stop at the first failure in this order:

1. Validate the closed v2/document/package schemas and scalar types.
2. Validate the exact algorithm constant and uppercase digest syntax.
3. Validate safe repository-relative `root` syntax.
4. Strictly resolve the configured root and CLI package; require exact resolved
   equality and a directory.
5. Validate root and descendant topology.
6. Compute the aggregate once and compare `file_count`, then `total_bytes`, then
   `inventory_sha256`, stopping on the first mismatch.
7. Only after the aggregate passes, validate all 124 `page_markdown` identities
   and their exact `package/pages/page-NNN.md` bindings as today.

Builder errors should remain `ValueError` and use stable, unambiguous details:
`v2 reconstruction package closed schema mismatch`, `... algorithm mismatch`,
`... root must be safe repository-relative`, `... CLI/config path mismatch`,
`... topology mismatch`, `... file_count mismatch`, `... total_bytes mismatch`
and `... inventory_sha256 mismatch`. The v2 branch of `preflight()` must call
this binding; merely returning a freshly computed hash without comparing it to
the declaration is forbidden. Its existing result key
`reconstruction_inventory_sha256` may remain for compatibility, but its value
is the verified aggregate digest, never the hash of a supposed input file.

## Independent-verifier validation and first-error contract

The verifier independently repeats the same ordered checks and aggregate
construction. It may duplicate constants and small functions but may not import
builder helpers or trust builder provenance/output. Use these stable first-error
surfaces:

1. closed/type failure: `E_V2_SCHEMA: reconstruction-package`;
2. algorithm/digest syntax: `E_V2_IDENTITY: reconstruction-algorithm`;
3. unsafe configured root: `E_V2_IDENTITY: reconstruction-root`;
4. missing/not-directory/CLI mismatch: `E_V2_IDENTITY: reconstruction-package-cli`;
5. symlink/reparse/non-regular/empty-directory topology:
   `E_V2_IDENTITY: reconstruction-topology`;
6. aggregate comparisons, in order:
   `E_V2_IDENTITY: reconstruction-file-count`,
   `E_V2_IDENTITY: reconstruction-total-bytes`, then
   `E_V2_IDENTITY: reconstruction-inventory-sha256`;
7. existing page bindings continue afterward under their current page identity
   error surface.

`v2_report_payload()` must stop reading `package/INVENTORY.json`. Its existing
`reconstruction_inventory_sha256` field is retained and receives the independently
computed, declaration-matched aggregate digest. The candidate report fields
`candidate_inventory_sha256` and `inventory_file_sha256` retain their current
meaning.

## Candidate `INVENTORY.json` boundary

The reconstruction input identity and candidate output inventory are different
contracts:

- input: declaration-only aggregate over **all** regular reconstruction files;
- output: materialized `INVENTORY.json` with schema
  `kb_creator.candidate_inventory.v1`, whose rows cover all regular candidate
  files **except** itself.

This remediation must not change candidate inventory filename, schema,
algorithm string, scope string, row format, counts, hashing, verifier rules or
report meaning. It must neither create an input inventory nor copy the output
inventory into v4.

## Required test matrix

All tests must exercise builder and independent verifier separately.

### Positive

1. Real v4 plus the exact declaration above passes both preflights and reports
   aggregate `68C17F...BA83` without creating any file.
2. A disposable synthetic reconstruction package with 124 page files and no
   `INVENTORY.json` passes after its five aggregate fields are independently
   computed.
3. Existing page identity/binding tests pass after fixture migration from a
   dummy input inventory to aggregate package identity.
4. A v2 candidate still emits one output `INVENTORY.json`; its existing closed
   schema and self-excluding rows are byte-for-byte/semantically unchanged and
   the independent candidate verifier accepts it.
5. Both real frozen v1 preflights pass unchanged, and
   `publication_config_v1.json` retains SHA-256 `C16DFA...3B30`.
6. The verifier source-level independence test continues to prove no builder
   import.

### Negative

1. Missing or extra `reconstruction_package` key; retained legacy
   `reconstruction_inventory` key.
2. Wrong type, boolean count, zero/negative count or bytes, lowercase/malformed
   digest and wrong algorithm string.
3. Unsafe roots: absolute, drive/colon, backslash, empty, `.`, `..`, doubled
   empty segment and a repository escape.
4. Configured root pointing to the wrong directory, a file, a missing path or a
   directory different from the CLI package.
5. Root or nested symlink/junction/reparse point, special file and an added empty
   directory.
6. Stale declaration with wrong `file_count`, then wrong `total_bytes`, then
   wrong `inventory_sha256`, proving the specified first-error order.
7. Immutable-package mutations against an unchanged declaration: add file,
   delete file, rename file and same-length byte replacement. All must fail;
   same-length replacement must reach the digest mismatch rather than pass on
   count/bytes.
8. A forged physical input `INVENTORY.json` added to a synthetic or copied tree
   must be counted as ordinary input material and cannot satisfy a stale
   declaration by its presence.
9. Existing wrong source-PDF and wrong page-markdown identity tests remain
   negative after aggregate binding succeeds.
10. Existing candidate-inventory mutation tests remain unchanged and failing
    under their candidate-specific errors.

## Migration sequence and dependencies

1. Implement the v2-only schema swap and independent aggregate helpers in the
   builder and verifier; leave their v1 branches untouched.
2. Make both v2 preflights execute the binding and comparisons before page
   identity checks. Update the verifier report to use the aggregate result.
3. Migrate only v2 test fixtures from dummy input `INVENTORY.json` creation to a
   computed aggregate declaration; add the matrix above.
4. Update the author helper to emit `reconstruction_package` with the exact
   accepted v4 values (or compute and assert those fixed values). Do not allow
   this step to write `publication_config_v2.json` yet.
5. Run focused builder/verifier tests and both real v1 preflights. Obtain fresh
   independent implementation review before reopening config authoring.
6. Only after this identity gate is accepted may the orchestrator separately
   resolve publication completeness and reassign config authoring.

## Downstream blocker independent of this contract

The current author helper materializes only `186` reviewed ledger units covering
`1,905` of `4,860` line slots on pages 1--122 (about `39.2%`). The boundary
ledgers identify special structures; they are not a complete source partition.
Therefore successful reconstruction identity validation does **not** authorize
config output or candidate execution. A separately scoped fail-closed
completeness/partition gate must prove every in-scope source line is exactly
owned, deliberately suppressed with evidence, or generated by an approved
operation. This is the next independent blocker/risk and is deliberately not
designed or implemented by this identity assignment.

## Risks and controls

- **Config/package co-mutation:** an aggregate proves equality to the reviewed
  declaration, not historical truth if both are changed. Control: keep v4
  immutable and hash-bind/review `publication_config_v2.json` before execution.
- **Hash dialect drift:** locale sorting, backslashes, CRLF rows or excluding an
  `INVENTORY.json` would produce a different dialect. Control: exact algorithm
  constant, byte-level fixtures and real v4 known-answer test.
- **Hidden topology:** symlinks, reparse points, special files and empty
  directories are not safe portable hash material. Control: reject them before
  enumeration in both implementations.
- **TOCTOU during scan:** the package is expected immutable, but a concurrent
  mutation could produce an inconsistent snapshot. Control: read each file once
  for byte count and digest; any I/O/stat/topology change fails the preflight.
- **Candidate/input confusion:** reusing the candidate self-exclusion helper
  would silently omit an added input inventory. Control: separate function and
  tests; input scan excludes no basename.
- **V1 regression:** shared dispatch edits could alter accepted behavior.
  Control: branch strictly on v2 schema, do not modify v1 schema/functions/data,
  and run both real v1 preflights.

## Engineer changed-path allowance

The bounded identity implementation may change only:

- `kb_creator/scripts/build_scenario_master_en.py`;
- `kb_creator/scripts/verify_scenario_master_en.py`;
- `kb_creator/tests/test_build_scenario_master_en.py`;
- `kb_creator/tests/test_verify_scenario_master_en.py`;
- `kb_creator/scripts/author_viral_master_en_v2_config.py` only to emit/assert
  the new identity object without writing config;
- optional new
  `kb_creator/tests/test_author_viral_master_en_v2_config.py` for the helper's
  no-write/identity behavior;
- the engineer's specifically assigned immutable receipt.

Forbidden in this task: `publication_config_v1.json`, both v1 reference copies,
accepted reconstruction v4, source PDF, boundary ledgers, review evidence,
`publication_config_v2.json`, any candidate/scratch root, canonical plan/context,
Git staging/commit/push and all downstream MASTER_RU/asset/HTML/PDF paths.

## Acceptance criteria

- The exact closed v2 JSON shape above is implemented in both components.
- Real v4 known-answer values pass with no package mutation and no input
  `INVENTORY.json`.
- Every negative class above fails independently in builder and verifier at the
  specified first error.
- The verifier shares no builder implementation code.
- Both frozen v1 preflights and the existing full focused suites pass.
- Candidate output `INVENTORY.json` behavior is unchanged.
- No config or candidate is authored as a side effect.
- Fresh independent review finds no P0/P1 before config work resumes.

## Files checked or changed

- Checked: task packet, canonical plan/context, frozen v1 config, accepted v4
  topology and aggregate identity, current builder/verifier, blocked helper,
  blocked engineering receipt and existing builder/verifier v2 tests.
- Changed: only this architecture receipt.

## Verification, blockers and next action

- Verification: independently replayed the current accepted v1 aggregate helper
  on v4 and obtained `(377, 41079424, 68C17F...BA83)`; confirmed no root input
  inventory, no reparse points and no empty directories.
- Identity-contract blocker: none.
- Separate publication blocker: incomplete source partition in the current
  helper, as described above.
- Next action: assign the bounded changed-path allowance to Terra/medium; after
  tests, obtain fresh independent implementation review. Do not resume config
  output solely because the identity tests pass.

## Accounting

- Elapsed time: approximately 20 minutes.
- Token use: unavailable (platform contributor counter not exposed).

`READY_FOR_V2_RECONSTRUCTION_IDENTITY_IMPLEMENTATION`
