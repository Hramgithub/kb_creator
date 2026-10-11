# Explicit authored source continuation

This bridge finishes verification of an already authored review draft, then
optionally continues its reviewed structural successor through the existing
public APIs. It produces candidate evidence; source acceptance, language,
publication and release remain separate decisions.

The operator must first freeze and independently review the runtime and resolve
exclusive ownership of the old producer/coordinators and their descendants.
The wrapper neither examines nor stops them. An observation or authorization
record is a hash-bound external prerequisite, not a process lock or an automatic
permission to signal a PID. Preserve actual interrupted/natural outcomes in those
records without rewriting historical job results.

## Commands and runtime

Run a fresh interpreter with bytecode disabled and the accepted runtime's
`code` directory first on `PYTHONPATH`, from outside the live repository root:

```powershell
$env:PYTHONPATH = '<accepted-runtime>/code;<reviewed dependency paths>'
Set-Location '<operator workspace outside the live checkout>'
& '<pinned Python>' -B -m kb_creator.scripts.continue_review_source verify --request '<absolute verify request>'
& '<pinned Python>' -B -m kb_creator.scripts.continue_review_source structural --request '<absolute structural request>'
```

These are two independently invoked commands. Run structural only after inspecting
the successful verification receipt and sealing a new structural request against
its exact bytes. There is no automatic retry, old coordinator reuse or book name
inside the module. CLI failure returns 2; partial new outputs and `failure.json`
remain diagnostic evidence. Use another absent output root for a reviewed retry.

The runtime manifest retains the existing `files` inventory relative to
`<runtime>/code`. Every imported `kb_creator` module must have a matching declared
file there, including package `__init__.py`, the wrapper and CLI. The interpreter,
manifest and explicitly declared dependency files must match pinned bytes. The
wrapper does not dynamically insert runtime paths or reload live modules.
The operator's compatibility decision must enumerate external import/dependency
closure; the wrapper hashes the declared dependency identities but does not infer
package equivalence or attest a dependency omitted from that reviewed closure.

## Closed request

Use schema `kb_creator.review_source_continuation_request.v1`. JSON parsing rejects
duplicate keys and nonfinite numbers using the existing strict parser helpers.
All top-level paths and absolute identity paths are absolute. Identity records
have exactly `path`, `bytes`, `sha256`; the latter is uppercase SHA-256 of file
bytes. Canonical seals are separate from file identities.

| Common field | Required meaning |
| --- | --- |
| `operation` | `verify` or `structural` |
| `binding_root` | Existing root for portable input bindings and new outputs |
| `run_root`, `authored_root` | Preserved replay and completed predecessor authored tree |
| `input`, `evidence` | Exact absolute identity records; evidence must be `authored_root/review-draft-evidence.json` |
| `expected_pages` | Sorted, unique, explicit positive source page domain |
| `runtime` | Closed object: `root`, `manifest` identity, `executable` identity, `dependencies` identity list |
| `authority_files` | Named absolute records, including all names below; additional reviewed dependencies may be included |
| `authority_inventories` | List of `{root, files}` where `files` is `identity.deterministic_inventory(root)` |
| `output_root` | Absent directory below binding root, with existing parent and absent sibling `.name.staging` |
| `request_sha256` | Canonical seal from `manifests.sealed(..., digest_key='request_sha256')` after all prerequisites are filled |

Required authority names are `old_runtime_manifest`, `runtime_integration`,
`patch_evidence`, `implementation_review`, `compatibility_decision`,
`ownership_decision`, `old_job_observation`, `exit_observation`, `source`,
`renderer`. The last two are the actual source PDF and geometry-bound renderer,
not alternate copies. Runtime integration/review/compatibility and ownership
authority must describe the exact new runtime and actual old process outcome.
The wrapper binds their bytes; the operator/reviewer owns their substantive
approval and process truth.

Inventory the complete replay and predecessor authored trees in the request.
Also pin existing archive/replay authority closures, the source-choice ledger's
submission/queue and transitive predecessor masters/candidates, original runtime
review/integration records and any other external closure listed in N356. Use
specific immutable roots, not a broad book tree that will contain new outputs.
The wrapper additionally checks every input binding, unresolved disposition,
authored evidence identity, decision-set page and exact page domain before/after
verification and at structural handoffs. Its inventories do not replace the
public APIs' full archive, ledger, Stage05/Stage06, freshness and master validation.

Structural requests require all common values except operation/output/seal to
equal the original verification request. Additional fields are:

| Structural field | Meaning |
| --- | --- |
| `verification_receipt` | Exact new successful `receipt.json` identity |
| `verification_request` | Original sealed verification request identity |
| `proposal`, `projection` | Reviewed structural proposal and page projection identities |
| `review_root` | Root for portable projection parents and original reviewed visual records |
| `excluded_owner_pages` | Explicit unique page list; proposal units may not replace these owners |

The proposal uses the existing N209 `normal_api_edit_sections` shape:
`schema`, `source_marker_dispositions_sidecar_proposal`, `structural_post_patches`,
`retained_owner_assertions`, `page_units`. The projection uses the existing N264
`parents` and `post_ledger_page_projections` shapes. All expected Markdown hashes
must match actual predecessor decisions over the complete configured page domain.
Marker candidates and dispositions must name selected nonasset raw keys; both
original and actual semantic visuals are identity checked. Only the existing
`ornament_removed` proposal annotation is stripped before passing runtime edits.
The prepare API validates source occurrences, retained owners and patch semantics.
This bridge does not infer structural decisions or perform new visual review.

## Operations and outputs

`verify_authored_source(request_path)` calls the actual
`verify_final_review_draft(run_root=..., authored_root=..., input_path=...,
evidence_path=..., binding_root=...)`. It neither preflights nor authors R1.
It writes the returned closed descriptor unchanged as `descriptor.json` only
after descriptor bindings and closing inventories match. A separate sealed
`receipt.json` is published atomically after all closing checks succeed.

The consumer checks the receipt seal, exact original request, runtime/recovery
bindings, matching before/after/current inventories and descriptor identities.
A caller-supplied `passed` flag is rejected. Seals are integrity checks, not
cryptographic signatures: provenance comes from the reviewed runtime invocation
and the operator's preserved execution evidence. Do not create receipts manually.

`continue_structural_source(request_path)` validates that receipt, then checks
projections, parents, raw keys, exclusions and visuals before creating output.
It runs unchanged public APIs in this order:

```text
prepare_review_draft_structural_successor
  -> validate_spec
  -> author_drafts(mode='review_draft')
  -> verify_final_review_draft
  -> materialize(review_draft_authority=descriptor)
  -> build_review_master_en (which calls verify_master_en)
```

The existing `source_choice_successor_spec-`/`source_choice_successor_page-`
bindings are preferred; compact supported preparations retain `input_`/`draft_`
bindings. Gates require sealed preparation, full page/zero-unbound-key preflight,
correct authored count, real closed verification descriptor, verified
materialization and verified review master result. Fresh authority checks remain
between stages. The materializer and master builder retain their own recomputation.

Structural output contains `marker-dispositions.json`, `edits.json`, `prepared/`,
`authored/`, `descriptor.json`, `materialized/`, `master/`, stage result JSONs
and the final receipt binding predecessor receipt, all output files, master and
asset manifest. Failed operations retain partial new artifacts and phase-specific
failure diagnostics; no success receipt is written. Publication uses atomic
exclusive hard links on the same filesystem; unsupported hard links fail closed.
Predecessor files and existing successor roots are never replaced.

## Focused evidence and limits

`tests/test_review_source_continuation.py` covers actual request/descriptor/seal
parsing, identity and inventory freshness, overwrite refusal, projection/key
rejection, API/CLI argument propagation and failure gating. Wrapper control tests
stub runtime selection and public operation results; they prove orchestration
and refusal behavior, not real book fidelity. The two-page structural test uses
the actual preparation API; subsequent gates are stubs.

The one-page integration test calls the actual verification API and renderer,
Stage05 audit and Stage06 validator. Its reused fixture stubs archive/queue
boundaries; runtime selection is also stubbed. It does not prove real archive
closure, runtime assembly or all-book fidelity. No Fear verification, original
R1 reauthoring, process mutation, OCR, package copy or release review is performed
by the implementation/test task. The orchestrator must integrate and independently
review the frozen runtime and request before authorizing an exclusive book run.
