# Task packet — Viral v2 B1c6 asset-provenance input binding engineering

## Role, ownership, and collaboration boundary

- Owner: `gpt-5.6-terra` reusable code/test engineering at medium reasoning.
- You are not alone in the codebase. Preserve all other edits and adjust only
  within the four assigned files plus one new immutable receipt.
- Orchestration ownership remains with main chat (`gpt-5.6-sol` / medium).
- This is an implementation checkpoint, not a release and not candidate
  materialization.

## Approved prerequisites

- Architecture receipt:
  `sol_architect_viral_v2_complete_authoring_phase_b1c6_asset_provenance_binding_20260903.md`,
  SHA-256 `B37F37EF54885AEC1CFC4CEF557D31D326E603D5EA70F9BEA919C42C18162E5C`.
- Independent architecture approval:
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c6_asset_provenance_architecture_review_20260903.md`,
  SHA-256 `F46457EB86DE9E5499C8272C6B72C23EAE0D80B42E24F591906B14589230B6E9`,
  terminal `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C6_ARCHITECTURE`, no
  P0/P1/P2.
- B1c4 and B1c5 approvals remain immutable prerequisites.

## Exact owned files and starting hashes

1. `kb_creator/scripts/build_scenario_master_en.py`
   - `8055F7B355EB711474398C84263521C4B8001D852B2B53987523D5CBE9C4D6DD`
2. `kb_creator/tests/test_build_scenario_master_en.py`
   - `CE38BA49E996C414166F345D3127FC6303DEFD4949C5678D966F414D340B8555`
3. `kb_creator/scripts/verify_scenario_master_en.py`
   - `2CFEE758C2EDBC5F445E864EDB46E366EB07E7E19D6E19FBD64D6A99E9FF2ED5`
4. `kb_creator/tests/test_verify_scenario_master_en.py`
   - `61566BD4C76344CE36ACE6DC97FE94DD4E65A68176AACD21E8C11C28BFD195FA`
5. One new immutable engineering receipt under this handoff directory.

The author helper and author tests are explicitly out of scope and must remain
at their B1c5 hashes. Do not edit scenario contracts, plan, context, status,
governance, source, accepted reconstruction, frozen v1 config or output code.

## Exact root cause to remediate

Both public input-binding paths send all 125 canonical B1c4 assets into a stale
A3 legacy loop requiring `source_span_ids`, `reader_value`, `page`, and
`placement`. Canonical assets instead have the approved closed row:

```text
{asset_id, disposition, source_page, binary, provenance, migration_outcome}
```

Their truthful provenance split is exactly 16 `markdown_image_reference`, 100
`visual_region`, and 9 `reviewed_provisional_full_page` (93 reader / 32
evidence-only). Architecture and critic independently bound all 125 with zero
evidence errors. The defect is validator routing/source binding, not authoring.

## Required implementation

Implement independent generic helpers in builder and verifier. Neither may
import author or the other public implementation, nor use the Viral B1c4
expected-row projection as its input oracle.

### Mode selection

- Determine mode by closed row shape, never `scenario_id`.
- All assets must be homogeneous canonical provenance rows or homogeneous
  legacy fixture rows; mixed mode fails closed.
- Canonical rows reject legacy aliases `page`, `reader_value`, and
  `source_span_ids`.
- Existing all-legacy synthetic fixture behavior remains compatible.

### Common binary binding

For Markdown and visual variants, require a safe repository/package-relative
regular file with no path escape or reparse-point ancestor. Recompute exact
path, bytes, SHA-256, magic MIME and decoded dimensions. Path plus digest is the
identity; digest-only lookup is forbidden. Provisional rows require
`binary == null`.

### Markdown-reference binding — exact 16

- Resolve the declared span uniquely in `source_partition`; require unique use,
  `owner_kind=asset`, `classification=asset_reference_source`, and matching
  `source_page`.
- Bind exact page identity and byte/character range; decode at UTF-8 boundaries;
  recompute marker digest.
- Parse exactly one complete Markdown image marker and resolve its target
  relative to the page file. It must equal the exact bound binary path.
- Do not require the logical source-ledger `owner_id` to equal the final
  content-addressed asset id.

### Visual-region binding — exact 100

- Bind `ASSET_MANIFEST.json` to the CLI reconstruction package and select one
  row by exact `stored_path + sha256`; recompute row hash.
- Bind the closed passing comparison evidence and its sibling companion input
  manifest by declared basename/hash and evidence-bundle topology, not by its
  device-specific absolute path.
- Require companion source identity to equal document and CLI PDF.
- Select exactly one block by `selected_view + raw_index + exact manifest
  source_path membership`; bind page, type, bbox and block hash.
- Cache manifest/comparison/companion parsing by resolved path and digest.

### Provisional full-page binding — exact 9

- Bind provenance PDF identity exactly to document and CLI source PDF.
- Require physical page, zero-based index, actual page existence, actual
  MediaBox and source rotation semantics.
- Validate the closed single-page render recipe and recompute expected output
  dimensions from geometry and DPI. Do not render or invent output hashes.

### Stop boundary

After canonical provenance succeeds, stop before placement. The unmodified
public-v2 pair must raise exactly:

- builder `v2 asset placement mismatch`;
- verifier `E_V2_ASSET: placement`.

There are exactly 93 reader assets without placement; first source-ordered id:
`viral-accepted-ed4012725c597dbcf6fca51e55faeb883a53f6f1d2c9ee7496c667460d37c860`.
Do not author or implement placement.

## Symmetric mandatory tests

Builder and verifier must each exercise positive real/synthetic bindings and
negative attacks in the B1c6 helper itself. At minimum cover:

- current real 125 rows and exact 16/100/9 result;
- mixed canonical/legacy mode and canonical legacy aliases;
- path escape and reparse-point file/ancestor;
- path borrowing, digest borrowing, donor binary pair, bytes/MIME/dimensions;
- Markdown donor/duplicate span, owner-kind/classification/page/ranges/UTF-8,
  marker digest, marker target and foreign path with borrowed digest text;
- manifest identity/row path/digest/row hash, duplicate/missing row;
- comparison identity/status/schema, companion hash/source identity, selected
  view/raw index/source reference, provenance-kind substitution, block
  type/page/bbox/hash, duplicate/missing block;
- provisional PDF path/digest/bytes/page/index/MediaBox/rotation/recipe/DPI/
  format/color/alpha/metadata/output MIME/dimensions and non-null binary;
- canonical `source_page` authority and rejection of canonical `page`;
- preserved B1c4 declaration-identity attacks and B1c5 exact-list attacks;
- frozen-v1 and existing legacy fixture positives;
- public unmodified v2 reaches only the placement seam and creates no target.

When earlier B1c4 Viral gates would intercept a mutation, add a closed generic
canonical synthetic fixture that reaches B1c6; do not weaken or bypass B1c4.

## Verification and exit gate

Run and record:

1. `python -m py_compile` over the four owned files (six-file compilation may
   also include unchanged author files).
2. Focused new B1c6 tests.
3. Exact current scoped regression:
   `python -m unittest -q kb_creator.tests.test_author_viral_master_en_v2_config kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en`.
4. Frozen-v1 builder and verifier preflight-only commands.
5. Guarded temporary public-v2 builder and verifier preflights proving the
   exact placement pair and cleanup.
6. Hash checks for the four final owned files and unchanged author/B1c5 files.
7. Absence of canonical `publication_config_v2.json`, `.phase-b1c*.json`,
   Candidate D, render/review, MASTER_EN/downstream output and changes to the
   nine protected historical roots.

Do not claim completion from a quiet command: record exit code and literal
`Ran ... OK` where applicable. Do not implement the placement seam.

## Deliverable

Write one immutable engineering receipt with role/ownership declaration,
starting/final hashes, exact code/test scope, commands/results, 16/100/9
binding evidence, mutation outcomes, exact next seam, no-output checks,
blockers/risks, and terminal:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C6_IMPLEMENTATION_REVIEW`, or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C6_ENGINEERING`.
