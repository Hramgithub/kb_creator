# Architect correction receipt - Stage 50 transient render semantics

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4P-neutral-publication-control-spec-correction`
- Role: architect
- Requested model: `gpt-5.6-sol`
- Requested reasoning effort: `high`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Assignment state: `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform
  identity unverified
- Scoped override: none for this architecture correction. The goal's recorded
  engineering-only override does not apply and does not transfer orchestration
  ownership.
- Scope: correct only the Stage 50 pre-acceptance render ambiguity identified
  as P1-1 by the independent critic, plus the directly dependent package,
  cache/resume, test, P0/P1, and acceptance-checklist wording. This receipt does
  not reopen or redesign any other part of the publication architecture.
- Supersedes:
  `architect_neutral_publication_control_spec_20260914.md` only where this
  receipt explicitly replaces Stage 50 preview semantics and their dependent
  invariants. Every other original architecture decision remains unchanged.
- Result: P1-1 is architecturally remediated. Stage 50 may use Word PDF export
  only as a private transient implementation bridge to PNG review evidence. No
  pre-acceptance PDF may survive successful Stage 50, enter an inventory/cache,
  become user evidence, reach Stage 60, or enter the package. The single
  retained PDF lineage remains accepted DOCX -> fresh Stage 60 Word export ->
  final PDF candidate.
- Timestamp: `2026-09-14T05:11:19+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:06:00`
- Token use: unavailable

## Files checked or changed

Checked:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_neutral_publication_architecture_review_20260914.md`

Changed:

- added this immutable correction receipt only:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_correction_20260914.md`

The original specification was not edited. No canonical plan, context, status,
source, contract, schema, code, test, generated/production artifact,
acceptance, release, `.codex`, or Git state was changed.

## Verification/evidence

- The critic receipt was read in full. It records no P0 or P2 finding and one
  P1: Stage 50's phrase "DOCX QA preview PDF" did not forbid retaining,
  inventorying, packaging, accepting, caching, or forwarding that PDF.
- The active plan/context require final PDF generation only from the exact
  accepted DOCX.
- The original specification already requires Stage 60 to accept the exact
  accepted DOCX and forbids HTML/browser PDF generation. This correction closes
  the remaining pre-acceptance PDF ambiguity without changing that design.
- This receipt was checked for governance metadata, explicit supersession
  scope, cleanup-failure behavior, cache/package exclusions, Stage 60 isolation,
  and required negative tests. No runtime test was performed because this is an
  architecture correction only.

## Corrected authoritative rule

There is exactly one retained or packageable PDF artifact in the neutral
publication pipeline:

```text
exact accepted DOCX receipt
  + Stage 60 word_com_docx_export_v1
  -> final PDF candidate
```

Stage 50 produces a DOCX candidate and PNG review evidence. Stage 50 produces
no retained PDF artifact. A temporary PDF may exist only inside one invocation's
private render directory as a bridge from Word COM to Poppler; it has no
artifact identity or authority and must be deleted before Stage 50 can succeed.

## Replacement for Stage 50 render semantics

Replace only the original Stage 50 paragraph beginning "Use Word COM to create
a stage-local DOCX QA preview PDF" with the following normative behavior.

### Stage 50 retained outputs

Stage 50's allowed retained output/evidence roles are:

- the DOCX candidate;
- OOXML/semantic QA JSON;
- page PNGs rendered from the DOCX candidate for human layout review;
- a PNG inventory and review index;
- process diagnostics that say whether the private bridge was used and cleaned,
  without recording or inventorying its bytes; and
- the successful Stage 50 manifest.

No retained Stage 50 path may have a `.pdf` suffix or PDF media type. The Stage
50 output schema/adapter validates this allowlist before atomic publication.

### Private transient bridge

When Word COM cannot render the DOCX directly to PNG, the Stage 50 adapter may:

1. create a unique invocation-owned private directory such as
   `<run-root>/.private/stage-50/<invocation-id>/`;
2. export the DOCX to `bridge.pdf` there using the fixed Word policy;
3. invoke repository-local Poppler on that private file to write PNGs into the
   Stage 50 staging output;
4. validate that the PNG sequence is complete and non-empty;
5. explicitly delete `bridge.pdf` and its private directory in `finally`;
6. verify after deletion that neither path exists; and only then
7. inventory/publish Stage 50 outputs and seal the successful manifest.

The private bridge PDF is:

- never a stage output or evidence artifact;
- outside `outputs/` and `evidence/`;
- excluded from every input, output, evidence, configuration, and package
  inventory;
- excluded from cache keys and cache payloads;
- never copied, renamed into quarantine, uploaded, linked, or presented for
  user acceptance;
- never assigned a reusable SHA/file identity;
- never supplied to a later stage; and
- never a package file.

Command/process diagnostics must redact the private filename and may record only
`transient_bridge_used: true|false` and `transient_bridge_cleanup: pass|fail`.

### Cleanup is a success prerequisite

If deletion or post-deletion verification fails:

- Stage 50 returns blocked/failure;
- it does not atomically publish the DOCX/PNG staging directory;
- it writes no successful Stage 50 manifest;
- it exposes no cacheable result;
- Stage 50 acceptance and Stage 60 are unavailable; and
- the next resume is blocked while any private `.pdf` remains.

The adapter may retry cleanup only for the exact invocation-owned path. It must
not move a bridge PDF to quarantine because that would retain the forbidden
artifact. A process crash can leave private state, but the run cannot resume or
seal Stage 50 until an explicit, path-contained cleanup removes it and confirms
absence.

## Stage 60 isolation

Stage 60 remains unchanged except for these explicit negative boundaries:

- its sole document input is the exact DOCX bound by the accepted DOCX receipt;
- it always performs a fresh `word_com_docx_export_v1` invocation after that
  receipt is validated;
- it cannot accept a PDF path, PDF bytes, Stage 50 private path, Stage 50
  diagnostic, or Stage 50 PNG as a PDF-generation input;
- it cannot discover or reuse a prior Word export by filename, hash, cache, or
  directory scan;
- its final PDF and all-page PNG QA are generated anew under Stage 60; and
- Stage 50 PNGs may support DOCX acceptance only; they cannot satisfy Stage 60
  final-PDF render QA.

The Stage 60 manifest must bind the accepted DOCX receipt, DOCX bytes, fresh
Word export invocation/tool/config identity, final PDF bytes, and a fresh final
PDF render inventory.

## Cache and resume correction

The original cache-key formula remains, with these clarifications:

- no Stage 50 bridge path, bytes, hash, diagnostic path, or private-directory
  inventory enters the cache key;
- a reusable Stage 50 result contains only DOCX, OOXML/semantic QA, PNG review
  evidence, review index, and their successful manifest;
- Stage 50 cache validation recursively proves there is no `.pdf` file in its
  outputs/evidence and no remaining private Stage 50 directory;
- any declared Stage 50 PDF input/output/evidence makes the manifest invalid;
- any private bridge residue makes resume/cache reuse fail closed;
- Stage 60 has a distinct cache key and can reuse only its own verified output
  produced from the exact accepted DOCX receipt; and
- Stage 60 never inherits a Stage 50 render/export cache entry.

## Package and offline-verifier correction

The package topology remains as originally specified, with these additional P0
rules:

- the package contains exactly one `.pdf` file: the accepted final PDF at the
  contract-declared stable PDF path;
- no Stage 50 bridge PDF or alternate/preview PDF is a legal package role;
- Stage 50 evidence may contain PNGs and JSON/manifest files only;
- the package manifest rejects any Stage 50 file record with `.pdf` extension,
  PDF media type, or PDF artifact kind;
- the offline verifier rejects any additional `.pdf` anywhere in the package,
  even if it is otherwise inventoried; and
- the offline verifier confirms that the one retained PDF is bound to a Stage
  60 manifest whose sole document authority is the accepted DOCX receipt.

The production package does not contain `.private/`, transient-cleanup
directories, bridge diagnostics containing a path, or cache payloads.

## Packet C correction

Packet A and Packet B scopes remain unchanged. In Packet C:

- `publication_render_qa.py` owns a private Stage 50 bridge lifecycle helper
  that returns PNG evidence only;
- `export_docx_to_pdf.ps1` is used by Stage 60 for the retained final PDF and may
  be invoked by Stage 50 only with an explicit `-TransientBridge` mode that
  forbids evidence output, canonical naming, existing-output reuse, and a
  retained result;
- alternatively, Packet C may keep transient bridge handling private inside the
  Stage 50 adapter; it must not introduce a second generic PDF artifact API;
- `verify_production_package.py` enforces exactly one PDF and Stage 60 lineage;
  and
- the engineer must not expose a CLI command that preserves a Stage 50 PDF.

## Corrected P0 invariants

Add these P0 invariants to Section 11 of the original specification:

- [ ] A successful Stage 50 has no retained `.pdf` in outputs, evidence,
      private runtime state, cache payload, or package.
- [ ] Stage 50 cannot seal a manifest until private bridge deletion and
      post-deletion absence checks pass.
- [ ] Cleanup failure or bridge residue blocks Stage 50 success, acceptance,
      cache reuse, resume, and Stage 60.
- [ ] The package contains exactly one PDF, produced by Stage 60 from the exact
      accepted DOCX receipt.
- [ ] Stage 60 rejects all supplied/pre-existing PDF bytes and always performs
      its own fresh Word export.

The original P0 DOCX-only lineage and no-HTML/browser-route invariants remain in
force.

## Corrected P1 wording

Replace the original P1 item:

> DOCX preview and final PDF render every page through `.tools` Poppler and emit
> complete visual-review inventories.

with:

- [ ] Stage 50 emits complete PNG review evidence from the DOCX candidate; if
      a PDF bridge is technically necessary, it is private, transient, absent
      before manifest sealing, and never an artifact/cache/package input.
- [ ] Stage 60 freshly exports the exact accepted DOCX, renders every final PDF
      page through `.tools` Poppler, and emits a distinct complete final-PDF
      visual-review inventory.

## Required negative tests

Add these mandatory tests to Packet A synthetic control-plane tests and Packet
C real-adapter/package tests:

1. Successful injected Stage 50 recursively contains no `.pdf` under
   `outputs/`, `evidence/`, cache payloads, or candidate package.
2. Stage 50 manifest validation rejects a `.pdf` input, output, evidence record,
   media type, or artifact kind.
3. A Stage 50 adapter attempting to copy, rename, quarantine, or publish its
   bridge PDF fails closed.
4. Simulated bridge deletion failure prevents atomic output publication,
   successful manifest creation, acceptance recording, cache reuse, and Stage
   60 dispatch.
5. A leftover private bridge from a simulated crash blocks resume until exact
   contained cleanup succeeds; cleanup cannot target outside the invocation's
   owned private directory.
6. After successful Stage 50, the private bridge file and directory are both
   absent while all expected PNGs remain.
7. Stage 60 rejects a supplied PDF path/bytes and rejects any attempt to use a
   Stage 50 private file, diagnostic, PNG, or cache entry as PDF authority.
8. Stage 60 invokes the Word exporter even when a same-named or same-content
   PDF already exists elsewhere, and it binds the fresh result to the accepted
   DOCX receipt.
9. Stage 60 final-PDF QA cannot reuse Stage 50 PNG hashes or review inventory.
10. Package assembly and offline verification reject a second PDF anywhere,
    including an inventoried preview/bridge file.
11. The sole packaged PDF record traces to Stage 60 and its exact accepted DOCX
    receipt; changing either receipt or DOCX bytes invalidates the chain.
12. Process diagnostics do not expose or inventory the bridge path/hash.

## Corrected architecture acceptance checklist

The original Section 14 checklist remains, with these additional closure rows:

- [ ] The critic can identify exactly one retained PDF lineage:
      accepted DOCX -> fresh Stage 60 Word export -> final PDF.
- [ ] Stage 50's retained surface is restricted to DOCX, PNG, JSON, and manifest
      evidence; PDF is prohibited.
- [ ] Any transient bridge is outside outputs/evidence/cache/package and is
      absent before successful manifest sealing.
- [ ] Cleanup failure is a stage blocker, not a warning or quarantined success.
- [ ] Stage 60 and the package verifier reject bridge reuse and every additional
      PDF.
- [ ] The negative tests above are represented in Packet A/C acceptance
      criteria before implementation dispatch.

## Assumptions and risks

- Assumption: Word COM PDF export is the available Windows bridge for rendering
  DOCX layout. This correction does not require retaining that intermediate.
- Risk: Windows file handles or antivirus inspection can delay deletion. The
  correct result is a blocked Stage 50, never a successful stage with residue.
- Risk: crash residue exists outside inventories. Resume must detect and block
  it; no later stage may ignore it.
- Risk: a developer may try to reuse Stage 50 PNGs for Stage 60 QA. Separate
  stage identities and the negative test forbid that shortcut.

## Blockers and next action

Blockers:

- No architecture blocker remains for P1-1 after this exact superseding rule.
- Implementation and Packet A/B/C dispatch remain subject to orchestrator
  integration and the critic's requested closure check.
- Live Dissociation publication remains gated on accepted upstream artifacts;
  this correction does not alter that state.

Next action:

1. Have the independent critic perform a short closure review against this
   correction and the original specification together.
2. If P1-1 is closed with no new P0/P1 finding, dispatch Packet A with the
   corrected P0 tests included.
3. Keep publication acceptance, stable promotion, and release pending.
