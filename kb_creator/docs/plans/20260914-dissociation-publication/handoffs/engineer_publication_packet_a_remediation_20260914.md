# Engineering remediation receipt - publication Packet A

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PA-remediation-stage50-and-package-chain`
- Role / requested model / effort: engineering / `gpt-5.6-sol` / `high`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `user-overridden-platform-unverified`
- Scoped override: engineering for this goal only, `gpt-5.6-sol` at `high`
- Timestamp: `2026-09-14T05:54:11+03:00`
- Token use: unavailable

## Result

The two findings in
`critic_publication_packet_a_implementation_review_20260914.md` are remediated
in the synthetic Packet A control plane. No Packet B/C adapter, live
Dissociation artifact, acceptance, package promotion, release decision, or Git
operation was added.

## Root cause and exact changes

### P0 - Stage 50 retained-PDF escape

Root cause: the success check covered only `staging/artifacts` and
`staging/evidence`, while atomic publication promoted the entire staging root.
Completed-stage validation also inventoried only those two subtrees.

- Every stage now has a closed output root containing exactly the two
  directories `artifacts/` and `evidence/` before promotion and during resume
  validation.
- Stage 50 recursively scans the entire staging/published stage root plus its
  private and both supported cache scopes. The scan rejects case-insensitive
  `.pdf` files and JSON-declared PDF media/artifacts or bridge path/hash
  diagnostics.
- The identical Stage 50 scan runs again from `_validate_stage`, so a stale or
  tampered completed Stage 50 cannot authorize resume.
- On Stage 50 failure, forbidden PDF files, PDF-declaring JSON, private bridge
  residue, and stage-local cache residue are removed before safe partial
  DOCX/PNG/JSON evidence is quarantined. No forbidden PDF survives as output,
  evidence, cache, quarantine, or package authority.
- The adversarial regression writes uppercase `staging/stray.PDF` outside both
  approved subtrees. It proves failure before output/manifest publication,
  preservation of safe partial evidence, absence of retained PDF, impossible
  DOCX acceptance, and no Stage 60 dispatch.

### P1 - incomplete packaged stage authority

Root cause: the verifier authenticated every listed stage record but only
required that one of them be Stage 60. A resealed package could therefore list
only Stage 60 while raw upstream evidence files remained in inventory.

- The package schema now requires both `minItems: 8` and `maxItems: 8` for
  `stage_manifests`.
- The verifier requires the exact ordered upstream set present when Stage 70
  is assembled: stages `10`, `20`, `21`, `30`, `31`, `40`, `50`, and `60`.
  Stage 70 and Stage 71 are deliberately excluded because neither exists when
  the Stage 70 package is constructed.
- Missing, extra, duplicate, reordered, substituted, wrong-id, or wrong-name
  records fail closed. Each record must have the expected stage/version/state,
  exact accumulated upstream chain, run identity, adapter identity, input-kind
  set, valid cache key, and continuous adapter-script/effective-config/tool/
  implementation identities.
- The six acceptance manifest records must exactly match the package role
  receipt identities for MASTER_EN, MASTER_RU, ArtView, HTML, DOCX, and PDF.
  Each sealed receipt must bind the corresponding packaged candidate and exact
  producer-stage identity. Packaged stage acceptance inputs are also checked
  against those receipt identities.
- The effective config packaged role must match the authority used by all
  eight stage manifests.
- Negative regressions cover a resealed Stage60-only manifest, missing, extra,
  duplicate, reordered/substituted stage lists, and a missing acceptance record
  while its raw receipt file remains in package inventory.

## Files changed in this remediation

- `kb_creator/pipeline/publication.py`
- `kb_creator/contracts/production_package_manifest.v1.schema.json`
- `kb_creator/tests/test_publication_control_plane.py`
- `kb_creator/tests/test_publication_contracts.py`
- this receipt

The package schema file was added to the remediation ownership explicitly by
the orchestrator after the initial narrow assignment.

## Verification

- Focused publication suite: `19 passed in 27.10s`.
- Full accepted eight-file control-plane suite: `107 passed in 36.40s`.
- `py_compile`: PASS for the publication module and both publication test
  modules.
- `git diff --check`: PASS for tracked changes. Packet A files are currently
  untracked in the shared working tree, so the command cannot inspect their
  whitespace until they are staged; they were additionally parsed/compiled by
  the tests and Python compiler.

## Remaining risks and boundaries

- Packet A still exposes only injected synthetic adapters. CLI production
  `run`/`resume` remains deliberately unavailable until Packet B/C adapters are
  implemented and reviewed.
- A self-contained package proves internal hash and graph consistency, not an
  external signature or release approval. Its result remains strictly
  `candidate_for_release_review / not_reviewed`.
- Safe incomplete Stage 50 DOCX/PNG/JSON evidence can remain only in
  quarantine after a failed attempt. Quarantine blocks automatic retry and is
  never package authority.
- Independent critic re-review is still required before Packet A becomes
  authority for downstream work.
