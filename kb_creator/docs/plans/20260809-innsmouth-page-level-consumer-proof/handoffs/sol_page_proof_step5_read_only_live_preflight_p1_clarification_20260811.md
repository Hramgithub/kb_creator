# Immutable Sol Clarification Receipt — Step 5 Read-Only Live Preflight P1.1–P1.3

## Receipt

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `5-step5-read-only-live-preflight-p1-clarification`.
- Role: Sol architect.
- Requested model/effort: Sol, `high`.
- Actual platform model/effort: `unavailable`; repository role assignment is
  platform-unverified.
- Orchestrator policy owner: main-chat `gpt-5.5` at `medium`,
  `platform-unverified`. This receipt does not transfer orchestration ownership.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.
- Scope: clarification only for P1.1, P1.2, and P1.3 in the independent Terra
  architecture review of the Step 5 read-only live preflight specification.
- Result: **P1 CLARIFICATION SPECIFIED; LIVE EXECUTION REMAINS PROHIBITED**.
  Sections 1–3 close only the three reviewed contract gaps. They do not accept
  the architecture, authorize implementation, or resolve either previously
  declared Sol blocker.
- Base specification: `sol_page_proof_step5_read_only_live_preflight_spec_20260811.md`,
  SHA-256 `12DF1D960B94FA573FD98558CC744A9D36C4BB82CD9791C12B1623F31310F8E9`.
- Review being answered:
  `terra_page_proof_step5_read_only_live_preflight_architecture_review_20260811.md`,
  SHA-256 `5D9716CD3BC2F144C9E71FB9E34E19439F67A84AA2AF7DF906225AB44BACE4D5`.
- Timestamp: `2026-08-11T22:46:05.5557743+03:00`.

This receipt is an additive clarification to the base specification. All base
requirements remain normative unless this receipt gives the narrower exact
definition requested by P1.1–P1.3.

## Scope and forbidden scope

In scope are only:

1. the controller/adapter privilege split for sealed control records;
2. the prerequisite-QA evidence contract and its hash bindings; and
3. the reproducible selected-page queue identity and selection preimage.

Forbidden and unchanged:

- no adapter implementation or synthetic/live execution;
- no live Innsmouth PDF, EN source, RU source, KeeperBook, HTML, PDF output,
  output/build tree, scenario configuration, production root, public terminal
  result, Git, release, network, browser, OCR, cache, or existing render read;
- no code, test, canonical plan, context, project status, contract status, or
  release-file edit;
- no source reconstruction, repair admission, mutation, rebuild, production
  activation, release decision, or final acceptance;
- no selection of render Branch A or Branch B.

## Common canonical and binding rules

The new objects below use the already required reviewed canonical JSON
serializer. Every closed object rejects duplicate or unknown keys, floats,
non-canonical integer encodings, non-UTF-8 input, and a mismatched internal
`content_sha256`. A `content_sha256` is the SHA-256 of canonical UTF-8 JSON over
all preceding fields of that object. A file binding always has exactly:

```text
repo_relative_path, resolved_absolute_path, resolved_path_kind,
reparse_point, byte_length, file_sha256, content_sha256
```

`resolved_path_kind` must be `regular_file`; `reparse_point` must be `false`.
`file_sha256` seals the exact file bytes; `content_sha256` seals the decoded
closed object. A path string, internal content hash, or file hash alone is not
sufficient authority.

## 1. P1.1 — Closed control-record and OS privilege split

### 1.1 Normative choice: immutable record reads, not inline control JSON

The sealed control records are **immutable permitted reads**. They are not
expanded into inline JSON or key/value arguments. `exact_command_argv` is a
literal argv array and carries only the reviewed executable/adapter paths, the
literal option names, the exact absolute path to one phase-specific control
record, and the exact literal selected-PDF path already named by that record.
No shell command text, response file, environment substitution, stdin control
payload, glob, directory, or dynamically discovered path is permitted.

The only adapter control-record reads are:

| Phase | Adapter control record | Literal argv selector | Other live read |
| --- | --- | --- | --- |
| Step 5A | `selection.json` / `LivePagePreflightSelection.v1` | `--selection <exact-absolute-selection-json>` | the one selected PDF at the exact `--source` path |
| Step 5B | `authorization.json` / `LivePagePreflightAuthorization.v1` | `--authorization <exact-absolute-authorization-json>` | the same one selected PDF at the exact `--source` path |

The Step 5B adapter does not read `selection.json`, `source_identity.json`, an
identity-review file, a QA-output file, or any receipt as a second control
input. Everything required at adapter runtime is copied into and hash-bound by
`authorization.json` as defined in section 2. The selected PDF remains the only
live content input. This clarification opens no second PDF, raster, source, or
denied root.

### 1.2 Controller authority

The evidence-capture controller and the adapter are separate OS subjects. The
controller may launch exactly one reviewed adapter process but may not import,
call, or execute the adapter in-process.

For the active phase, the controller may read only:

- the exact phase control record and its file binding;
- the exact reviewed executable, controller, adapter, serializer/verifier,
  sandbox-policy implementation, and closed local-import manifest;
- for Step 5B only, the exact `source_identity.json` and accepted
  `terra_identity_review.md` named and hash-bound in `authorization.json`;
- the already permitted goal-local receipts whose exact path, length, and
  SHA-256 occur in the control record;
- the adapter's stdout and stderr through OS-owned in-memory capture pipes; and
- the OS policy/audit event stream for that one child process.

The controller may not open, hash, map, stat for content inference, or otherwise
read the selected PDF. It passes the already sealed literal path to the OS
policy and adapter. It may write only the base specification's phase-appropriate
create-new files beneath the one sealed run directory. It may not redirect
stdout/stderr to disk, create a temp file, bytecode/cache, or mutate an existing
file.

### 1.3 Adapter authority

For each phase the adapter may read exactly:

1. its one phase control-record file;
2. the one selected PDF at the exact literal path; and
3. the exact read-only runtime/code/import files in the hash-bound
   implementation manifest.

The adapter has an empty filesystem write allowlist, no inherited writable
handle, no network capability, no child-process capability, no plugin/dynamic
import authority, and no directory-enumeration authority. Stdout may contain at
most one canonical evidence or failure object; stderr must be empty on success.

Before any PDF open, the adapter must read the control record exactly once into
memory and verify, in this order:

1. regular-file and non-reparse identity;
2. exact resolved path;
3. exact byte length and file SHA-256 from the OS policy;
4. closed schema and canonical bytes;
5. internal `content_sha256`;
6. goal, step, run, source-path, page, implementation, runtime, prerequisite-QA,
   and policy bindings; and
7. literal argv equality to the record's `exact_command_argv`.

The adapter never reopens the control record. The controller records the same
record's length/SHA-256 immediately before launch and immediately after child
exit. Any difference is
`preflight_rejected_policy_mismatch_or_denied_access`, with no PDF open or
partial result.

### 1.4 Closed OS policy and audit preimage

Each phase's `filesystem_policy` has exactly these closed fields:

```text
schema, phase, run_id, controller_executable_binding,
adapter_executable_binding, adapter_control_record_binding,
selected_pdf_exact_path, runtime_import_file_bindings,
controller_read_allowlist, controller_create_new_allowlist,
adapter_read_allowlist, adapter_write_allowlist,
denied_root_literals, directory_enumeration, inherited_handles,
child_processes, network, stdout_capture, stderr_capture,
audit_schema, content_sha256
```

Required literal values are:

- `adapter_write_allowlist = []`;
- `directory_enumeration = forbidden`;
- `inherited_handles = capture_pipes_only`;
- `child_processes = controller_exactly_one_adapter_adapter_none`;
- `network = disabled`;
- `stdout_capture = controller_memory_only`;
- `stderr_capture = controller_memory_only`.

`adapter_read_allowlist` is the exact union of the one control-record binding,
the one selected-PDF literal path, and the runtime/import file bindings—nothing
else. The controller read/write lists are exactly those in section 1.2. The
policy hash is included in the control record and later evidence.

The mandatory audit is complete, not success-only. For every attempted open,
stat/map, write/create, directory enumeration, process creation, inherited
handle use, and network operation it records the subject (`controller` or
`adapter`), normalized exact path or capability, requested access, allow/deny,
matched policy entry, and monotonically increasing event ordinal. The evidence
contains the audit byte length/SHA-256, event count, allowed-access inventory,
denied-attempt inventory, and `policy_complete = true`; it contains no source
bytes or plaintext. A missing event range, unlisted allowed access, or denied
access attempt is fail-closed.

This split removes the prior contradiction: the adapter policy explicitly
permits the one immutable control-record read and separately permits the one
PDF read. The controller's evidence-write authority is not inherited by the
adapter and cannot be cited as adapter containment evidence.

## 2. P1.2 — Closed prerequisite-QA evidence and cross-gate binding

### 2.1 Logical record and placement

Define one closed `LivePagePreflightPrerequisiteQA.v1` logical record. It is
embedded verbatim in `selection.json`; it is not a new file and therefore does
not expand the base write allowlist. The byte-equivalent canonical object is
also embedded in `authorization.json`. Both parent records carry its exact
`content_sha256`. A mismatch between the two copies is a stop condition.

The prerequisite record must be completed successfully before `selection.json`
is sealed and before Step 5A may open the selected PDF. It contains no live
source data, extracted text, raster, PDF identity, repair inference, or output
artifact reference.

Closed root keys:

```text
schema, goal_id, step_id, run_id, cwd, runtime_identity,
implementation_manifest_sha256, environment_allowlist,
command_records, aggregate_result, receipt_bindings,
terminal_state, content_sha256
```

`terminal_state` must be
`prerequisite_qa_passed_no_live_input_no_production_activation`.

### 2.2 Exact command-record contract

`command_records` is a six-element array in this exact order:

1. `page_proof_py_compile`;
2. `page_proof_collect_159`;
3. `page_proof_execute_159`;
4. `stage_a_topology_execute_15`;
5. `stage_a_aggregate_execute_386_plus_1_skip`;
6. `inactive_root_public_poison_target`.

Each command record has exactly:

```text
command_id, exact_argv, cwd, environment_allowlist_sha256,
implementation_manifest_sha256, expected_result, actual_result,
exit_code, stdout_byte_length, stdout_sha256,
stderr_byte_length, stderr_sha256, output_parser_binding,
started_at, completed_at, terminal_state, content_sha256
```

`exact_argv` is a literal array beginning with the reviewed absolute Python
path and includes `-B`; pytest argv also includes `-q -p no:cacheprovider`.
There is no shell, alias, PATH lookup, redirection, glob, response file, or
placeholder. `cwd` is the exact reviewed `D:\NRI` root identity. The compile
and pytest target lists are exactly the literal lists in base specification
section 10.1. The collection command is the page-proof execution argv with
`--collect-only` added in the reviewed literal position.

Expected and required actual facts are:

| Command id | Expected and actual result |
| --- | --- |
| `page_proof_py_compile` | exit `0`; all eight named files compile; no failed file |
| `page_proof_collect_159` | exit `0`; `tests_collected = 159` |
| `page_proof_execute_159` | exit `0`; `passed = 159`, `failed = 0`, `skipped = 0` |
| `stage_a_topology_execute_15` | exit `0`; `passed = 15`, `failed = 0`, `skipped = 0` |
| `stage_a_aggregate_execute_386_plus_1_skip` | exit `0`; `passed = 386`, `failed = 0`, `skipped = 1`; the one skip identity/reason matches the accepted receipt |
| `inactive_root_public_poison_target` | exit `0`; `collected = 1`, `passed = 1`, `failed = 0`, `skipped = 0` |

The exact targeted node id is:

```text
kb_creator/tests/test_page_proof_private_authoritative_inventory_reseal.py::test_production_roots_remain_inactive_and_public_poison_is_coverage_first
```

Its command record additionally binds the exact test-file length/SHA-256 in the
implementation manifest and these expected claims:

```text
production_roots_inactive = true
public_poison_terminal = page_proof_stage_a_fixture_coverage_incomplete
caller_supplied_inputs_accessed = false
public_terminal_result_created = false
```

The accepted test-file identity observed for this clarification is byte length
`39025`, SHA-256
`627BD77326E39F2EB06B8CC83F0496B3BD5B0646A6496AB1B7E23B50F17C5502`.
Execution must use the later adapter-implementation-review-accepted identity;
if it differs from this observed identity, the new exact identity and reason
must be independently reviewed before authorization. It may not be silently
refreshed.

Raw stdout and stderr bytes are captured in memory. Their exact byte lengths
and SHA-256 values are evidence, even when timing text makes them unequal to a
prior run. The closed `actual_result` is derived by the hash-bound
`output_parser_binding`; the original output bytes are not persisted. A parser
failure, nonempty success stderr, count drift, unrecognized skip, or mismatch
between expected and actual facts rejects the prerequisite record.

### 2.3 Receipt and hash bindings

`receipt_bindings` is a nonempty ordered array of closed records with exactly:

```text
role, review_kind, repo_relative_path, byte_length, sha256, decision
```

It must include exact accepted bindings for:

1. the accepted 4b.9 implementation and final Terra implementation re-review;
2. the base Step 5 specification;
3. this clarification;
4. the fresh Terra architecture re-review accepting the combined Step 5
   architecture; and
5. the later non-live adapter implementation receipt and fresh independent
   Terra implementation acceptance.

Missing, changed, non-accepted, self-authored critic, or ambiguous receipt
bindings reject the record before a live file is opened.

### 2.4 Required propagation and review

The following additions are mandatory closed bindings:

- `LivePagePreflightSelection.v1` embeds `prerequisite_qa` and adds
  `prerequisite_qa_sha256`;
- `LiveSourceIdentityCapture.v1` adds `prerequisite_qa_sha256`;
- `LivePagePreflightAuthorization.v1` embeds the byte-equivalent
  `prerequisite_qa` and adds `prerequisite_qa_sha256`;
- `LivePagePreflightEvidencePackage.v1` adds
  `prerequisite_qa_sha256` at the root; and
- `LivePagePreflightFailure.v1` records the hash when the prerequisite object
  was available and uses
  `preflight_rejected_prerequisite_or_review_missing` on any prerequisite
  defect.

The Step 5A controller and adapter verify the selection-embedded record before
the PDF open. The identity reviewer recomputes every command-record hash and
the aggregate prerequisite hash. The Step 5B controller and adapter verify the
authorization-embedded byte-equivalent record before the PDF open. The final
evidence reviewer recomputes it again, checks the hash equality across
selection/source identity/authorization/evidence, and verifies the exact argv,
expected/actual facts, output lengths/hashes, `159` collection count, targeted
node id/result, test identity, and receipt decisions. A zero adapter exit cannot
substitute for this review.

## 3. P1.3 — Reproducible selected-page queue identity

### 3.1 Queue snapshot is embedded and immutable

`LivePagePreflightSelection.v1` adds one closed
`queue_selection_proof` object. It is embedded in `selection.json`; it is not a
path to a mutable queue. The object contains the complete permitted-metadata
snapshot needed to replay selection and is sealed by both
`queue_snapshot_sha256` and the parent selection `content_sha256`.

Closed keys:

```text
schema, queue_authority_binding, snapshot_record_count,
snapshot_row_hash_inventory, snapshot_rows, queue_snapshot_sha256,
eligibility_filter, eligibility_results, eligibility_result_sha256,
ordering_rule, ordered_eligible_preimage, ordering_preimage_sha256,
selected_candidate_preimage, selection_replay_result, content_sha256
```

`queue_authority_binding` identifies exactly one permitted metadata artifact by
repo-relative path, byte length, file SHA-256, schema/version, and logical
content SHA-256. That artifact must be outside every denied source, EN/RU,
KeeperBook, HTML/PDF, output/build, Git, release, cache, and production root.
If no such canonical permitted-metadata authority exists, selection fails; the
controller may not inspect a denied root to construct one.

`snapshot_rows` contains every queue row, not only eligible rows. Each row has
exactly:

```text
queue_order, item_id, item_id_utf8_hex, item_row_sha256,
artifact_repo_relative_path_literal, selected_page_index,
status_literal, hypothesis_literal, metadata_source_row_ordinal
```

The controller treats `artifact_repo_relative_path_literal` only as a string.
It must not resolve, stat, open, hash, or follow the referenced artifact.
`snapshot_record_count` must equal the number of rows, and
`snapshot_row_hash_inventory` must be the same-length ordered list of all
`item_row_sha256` values. Missing, duplicate, or unaccounted source rows reject
the snapshot.

### 3.2 Closed eligibility/filter result

`eligibility_filter` is literal data, not executable policy. It has exactly:

```text
required_status, allowed_hypotheses, required_fields,
page_index_minimum, forbidden_metadata_roots,
duplicate_item_policy, unknown_field_policy, content_sha256
```

Required values are:

```text
required_status = unresolved
allowed_hypotheses = [block_order_only_hypothesis,
                      paragraph_boundary_only_hypothesis]
page_index_minimum = 0
duplicate_item_policy = reject_snapshot
unknown_field_policy = reject_row
```

A row is eligible only when its row hash verifies, status is exactly
`unresolved`, all required fields are present, page index is an integer at
least zero, its hypothesis is exactly one allowed literal, its item id is
unique, and its metadata authority/path is not under a forbidden root. No PDF
feature, page count, extracted text, visual state, expected success, or denied
artifact may participate.

`eligibility_results` contains one result for every snapshot row in the same
order, with exactly:

```text
item_row_sha256, eligible, ordered_reason_codes
```

Reason codes are a closed enumeration. Eligible rows have exactly
`[eligible]`; ineligible rows list every failed predicate in the literal filter
order. `eligibility_result_sha256` seals the full all-row result, proving that
an earlier row was not silently omitted.

### 3.3 Closed ordering/tie-break preimage

The ordering algorithm is fixed ascending lexicographic comparison of this
four-field key:

```text
[queue_order, selected_page_index, item_id_utf8_hex,
 metadata_source_row_ordinal]
```

- `queue_order` is the canonical queue's integer order value;
- `selected_page_index` is the zero-based integer page index;
- `item_id_utf8_hex` is the lowercase hexadecimal encoding of the exact UTF-8
  item-id bytes, with no Unicode normalization or locale collation; and
- `metadata_source_row_ordinal` is the zero-based integer row ordinal and is
  the final total-order tie-break.

`ordered_eligible_preimage` is the complete sorted array of objects with
exactly:

```text
ordering_key, item_row_sha256, hypothesis_literal
```

It contains every and only eligible row. `ordering_preimage_sha256` seals that
array. `selected_candidate_preimage` must be byte-equivalent to element zero.
`selection_replay_result` has exactly:

```text
eligible_count, selected_array_index, selected_item_row_sha256,
selected_page_index, selected_item_id_utf8_hex,
selected_hypothesis_literal, replay_terminal
```

Required values include `selected_array_index = 0` and
`replay_terminal = first_eligible_selected_no_live_read`. Zero eligible rows is
`preflight_rejected_selection_invalid`; it does not permit fallback or a queue
refresh.

The parent selection adds these scalar cross-bindings:

```text
queue_snapshot_sha256, eligibility_result_sha256,
ordering_preimage_sha256, selected_item_row_sha256
```

They must equal the embedded proof values. `unresolved_item_row_sha256`,
`selected_page_index`, and `repair_class_hypothesis` in the parent selection
must equal `selected_candidate_preimage`. Any mismatch rejects before source
open.

### 3.4 Drift and independent replay

Immediately before sealing selection and again immediately before Step 5A
launch, the controller reads only the exact permitted queue metadata authority
and verifies its file/content binding against `queue_authority_binding`. If it
drifts, the run stops before the PDF is opened. There is no reinterpretation,
in-place refresh, or reselection.

The Step 5A adapter replays snapshot count, all row hashes, all eligibility
results, the total ordering, and element-zero selection from the embedded object
before it may open the PDF. The identity reviewer repeats the replay from
`selection.json` without reading the PDF or any denied root. Step 5B relies on
the accepted immutable `selection_sha256` and carries the three queue proof
hashes in authorization and evidence; it does not consult the mutable queue.

This proves deterministic selection from a complete immutable metadata
snapshot while keeping the live PDF and all denied roots outside the selection
preimage.

## 4. Preservation of the two existing fail-closed blockers

This clarification does not resolve, weaken, or redesign either base
specification section 3 blocker:

1. **No accepted live adapter.** `LivePagePreflightAdapter.v1` and the identity
   capture adapter remain unimplemented and independently unaccepted. The
   schemas above are not implementation authority and do not make a live path
   readable.
2. **Visual proof versus no-render/one-PDF conflict.** No render branch is
   selected. Branch A remains unaccepted; Branch B remains blocked for Step 5B.
   No raster, renderer, second input, or reinterpretation is authorized.

Either blocker independently prohibits its affected execution. Closure of
P1.1–P1.3 cannot be used to bypass them.

## 5. Acceptance criteria for this clarification

A fresh independent Terra/high architecture critic may accept the combined base
specification and this clarification only if all of these are true:

1. control records are immutable permitted file reads, never inline control
   JSON, stdin, environment, response files, or dynamic discovery;
2. Step 5A reads only `selection.json`, the one PDF, and the reviewed
   runtime/import closure; Step 5B analogously reads only
   `authorization.json`, the same PDF, and that closure;
3. controller write authority is separate from the adapter's empty write
   authority, and the controller never reads the selected PDF;
4. the closed OS policy includes the exact control-record read and the audit
   proves all allowed and denied attempts for the separate OS subjects;
5. the adapter verifies its single control record completely before source open
   and record pre/post identity is unchanged;
6. `LivePagePreflightPrerequisiteQA.v1` contains the six exact command records,
   expected/actual results, output hashes/lengths, exact `159` collection count,
   exact inactive-root/public-poison node evidence, and accepted receipt hashes;
7. the prerequisite record is embedded and hash-equal across selection and
   authorization and its digest propagates through source identity, evidence,
   failure, identity review, and evidence review;
8. queue selection embeds the complete metadata-only snapshot, every-row
   eligibility result, closed total-order preimage, and element-zero selection;
9. independent replay can prove no earlier eligible row was omitted without
   opening the live PDF, a referenced artifact, or any denied root;
10. queue, prerequisite, control-record, source, runtime/code, policy, or audit
    drift fails before source use with no fallback or refresh-in-place;
11. both pre-existing Sol blockers remain explicit, independently fail-closed,
    and unresolved; no Branch A/B choice is made; and
12. this assignment changed only this immutable clarification and performed no
    implementation, live read, test execution, Git, build, release, network,
    browser, production activation, or public-result action.

## 6. Evidence and handoff

- Files checked:
  - `D:\NRI\AGENTS.md`;
  - `D:\NRI\docs\governance\nri_goal_governance.md`;
  - `D:\NRI\kb_creator\PROJECT_STATUS.md`;
  - assigned `plan.md` and `context.md`;
  - `D:\NRI\kb_creator\docs\contracts\page_level_consumer_proof_contract_status.md`;
  - the base Sol Step 5 specification;
  - the independent Terra Step 5 architecture review; and
  - read-only test-node inventory in
    `kb_creator/tests/test_page_proof_private_authoritative_inventory_reseal.py`.
- Files changed: only
  `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_proof_step5_read_only_live_preflight_p1_clarification_20260811.md`.
- Verification/evidence: the target handoff was absent before creation; the
  base Sol and Terra receipts were re-hashed to their recorded SHA-256 values;
  the targeted inactive-root/public-poison node exists at the exact node id
  specified above; no tests were run because this packet is clarification-only.
- Blockers: unchanged—(1) no independently accepted live adapter; (2) unresolved
  visual-proof versus no-render/one-PDF conflict. This clarification itself
  remains unaccepted pending fresh independent architecture review.
- Next action: the main-chat orchestrator requests a fresh independent
  Terra/high architecture re-review of the base specification plus this
  clarification. No adapter implementation, render-branch amendment, Step 5A,
  or Step 5B assignment is authorized by this receipt.
- Elapsed active time: approximately `4 minutes`.
- Token use: `unavailable` (not exposed to this contributor).

This receipt is immutable. Any correction must be a new handoff that names this
file and the base specification. It does not edit canonical plan, context,
project status, contract status, or release state; it does not act as final
release review; and it does not transfer orchestration ownership.
