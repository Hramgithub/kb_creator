# R2 authors/frontmatter and source-contents regression audit

## Receipt

- Goal / step: `20260918-dream-html-heading-toc` / `T1-R2-frontmatter-toc-audit`.
- Role: architecture and root-cause analysis; no implementation or release-review ownership.
- Policy role / model / effort: architect, `gpt-5.6-sol`, high.
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, medium; orchestration ownership was not transferred.
- Assignment state: `platform-unverified`.
- Scoped override: none.
- Scope: read-only trace of the recorded authors/frontmatter and source-contents rules into Number 7 Dream publication run09 Stage 40.
- Result: **ROOT_CAUSE_CONFIRMED / REMEDIATION_SPEC_READY**.
- Files changed: this immutable receipt only.
- Blockers: none for implementation planning. HTML acceptance and all downstream publication stages remain blocked by the rejected run09 candidate.
- Next action: orchestrator integrates this contract with the other two defect audits, then assigns a reusable config/adapter/renderer implementation and a fresh Stage 40 successor.
- Elapsed time: approximately 34 minutes.
- Token use: unavailable to contributor.
- Timestamp: `2026-09-18T10:43:18+03:00`.

## Executive finding

The reusable renderer still contains source-TOC and credits machinery. The
regression occurred because the active Number 7 Dream HTML config never carried
the inputs that activate it, and the strict publication adapter treated that
incomplete config as Stage-40-ready.

The exact originating decision is recorded in
`docs/plans/20260917-dream-master-en/handoffs/m3-publication-authority-architecture.md`:
the downstream `html.json` was deliberately authored as a future
template/placeholder while only Stage 10 was authorized. M3 explicitly said to
omit `toc_policy` until an accepted MASTER_RU existed and expected the neutral
adapter to use a generic generated TOC. That deferral was not wrong for a
Stage-10-only packet, but there was no later state transition, schema flag, or
Stage 40 precondition that required the placeholder to be completed.

M4 hash-bound the placeholder as the production HTML config. Run09 then copied
the same 569-byte config into Stage 40 unchanged. This is the regression
boundary: **a deliberately incomplete future-stage config crossed from
Stage-10 inventory into Stage-40 authority without a completeness gate**.

## Intended recorded rule

The active reusable rule is recorded in
`translator/docs/architecture/production_frontmatter_standard.md` and in Git
commits `5316752c` (`Enforce production frontmatter flow`) and `0470919f`
(`Freeze Innsmouth v6 frontmatter baseline`):

1. A source book that contains `Содержание` keeps that source-authored title and
   entry set as the production TOC; printed page-number decoration is removed,
   and every retained entry is linked to an accepted production heading.
2. Generated `Оглавление` is permitted only when no source contents page exists
   or the package explicitly opts into generated mode.
3. The source TOC page is typed `source_toc`, consumed into the linked TOC, and
   must not leak as ordinary body content.
4. Credits/authors pages are typed `credits` frontmatter and transformed under
   an explicit credits policy rather than rendered as ordinary paragraphs.
5. Frontmatter order is explicit. The generic standard requires cover/landing
   before TOC and allows a declared credits placement. For Number 7 Dream the
   immutable source and accepted MASTER_RU establish pages `001` cover/title,
   `002` authors/credits, `003` source contents, and body from `004`; the source
   order therefore needs an explicit `cover -> credits -> source_toc -> body`
   declaration rather than an inferred default.
6. Missing or unresolved source-TOC links, wrong TOC origin, duplicate visible
   source contents, and missing typed credits are blockers.

Number 7 Dream reconstruction evidence did preserve the source material:
`MASTER_RU.md` contains `# АВТОРЫ И СОЗДАТЕЛИ` on page 002 and
`## СОДЕРЖАНИЕ` plus the source entry set on page 003. The structural audit also
fixed the missing page-002 Credits heading. The content was not lost during
reconstruction or translation; its publication role was lost at Stage 40.

## Current active path

The run09 path is:

```text
accepted MASTER_RU (pages 001-026, including pages 002/003)
  -> Stage 40 adapter copies hash-bound configs/html.json
  -> adapter adds runtime paths/gate booleans and statblock projection only
  -> derived_html_config.json
  -> translator build-production-html
  -> run09 HTML + frontmatter_manifest.json
```

Observed config/evidence state:

- `inputs/number-7-dream/publication/v1/configs/html.json` contains typography
  and five presentation booleans only. It has no schema/version, `page_map`,
  `frontmatter`, `toc_policy`, `credits_policy`, or body-start declaration.
- `effective_publication_config.json` identity-binds that file but does not
  inspect its semantic completeness.
- `publication_adapters.build_html_candidate` deep-copies the config and adds
  runtime source/output/report paths, gates, ArtView asset projection, and
  semantic statblock projection. It neither supplies nor validates
  frontmatter/TOC/credits policy.
- `derived_html_config.json` therefore retains the same omission.
- The renderer's early source-capture branch reads
  `production_html.toc_policy.mode`, defaulting a missing value to `generated`.
  It consequently never calls `source_toc_from_markdown` for page 003.
- `page_map` is empty, so pages 002 and 003 receive no `page-type-credits` or
  `page-type-source-toc` annotation. Credits transformation and source-TOC page
  replacement each receive an empty target set.
- Only later does `build_production_toc` merge `DEFAULT_TOC_POLICY`, whose mode
  is `preserve_and_link`; by then `source_toc` is already `None`. This is a
  split-default defect: source capture defaults to `generated`, while the TOC
  builder advertises a `preserve_and_link` default that cannot recover the
  skipped source capture.

Run09 evidence proves the branch outcome:

- `frontmatter_manifest.json`: `toc.mode=generated`, `origin=generated`,
  `source_page=null`, `credits.pages=[]`, `body.starts_at=null`.
- Flow: `page-001 -> toc:generated -> page-002 -> page-003 -> page-004 ...`.
- Producer counts: `page_type_annotations=0`,
  `removed_source_toc_pages=0`, `source_toc_entries=0`, and
  `transformed_credit_tables=0`.
- Nevertheless the producer status is `pass` with zero findings.

## Precise regression boundary and dependency trace

### Earliest failing layer

The earliest failing layer is the **publication authority/config lifecycle**,
not accepted source content and not CSS:

1. M3 authored a downstream placeholder and explicitly deferred TOC policy.
2. The publication contract schema bound the file by identity but has no HTML
   source-config schema or `deferred` versus `stage40_ready` state.
3. M4 created a valid identity-bound contract from that incomplete file.
4. Later runs reused the exact contract after MASTER_RU and ArtView acceptance;
   no stage required finalization/re-authoring of the deferred HTML policy.
5. The Stage 40 adapter accepts any object with or without `production_html`,
   silently creates the object if missing, and invokes the renderer.
6. Renderer defaults and QA are conditional on the very metadata that is
   absent, so they certify the fallback path rather than the source contract.

### Why the prior fix “fell out”

The previous frontmatter/source-TOC work lives in the reusable Translator
renderer and in complete legacy scenario configs. KB Creator's neutral
publication contract imported the renderer but did not import its required
frontmatter data contract or its positive-content gates. The reusable function
was therefore present but unreachable from Number 7 Dream's active config.

This is a boundary-integration regression: capability reuse occurred without
contract reuse.

## Test-coverage gap

Existing tests cover the feature in isolation but not the active dependency
chain:

1. `translator/tests/test_recovery_support.py` proves that the old package
   initializer emits `preserve_and_link`, that source TOC parsing/linking works
   when `page_map`/policy is supplied, and that typed credits transform when a
   credits page is supplied.
2. Those tests do not prove that a KB Creator Stage 40 source config contains
   those declarations. The Number 7 Dream config is not produced by the old
   initializer.
3. `kb_creator/tests/test_publication_html_adapter.py` uses a deliberately
   minimal config containing typography only. Its mock renderer writes a
   passing HTML/report, and the positive adapter test expects success. Thus the
   test currently codifies acceptance of the exact omission that caused run09.
4. Adapter coverage asserts identity binding, ArtView asset rebasing,
   statblock projection, local-reference closure, and no PDF route. It has no
   assertions for page roles, frontmatter order, TOC origin, source-entry
   conservation, credits transformation, or `frontmatter_manifest`.
5. Renderer semantic QA loops only over configured `source_toc` and `credits`
   pages. With an empty `page_map`, both loops are vacuous. The generated TOC
   count/title checks then pass because one generated `Оглавление` exists.
6. R17/R18 run09 QA reviewed the then-known page-14/statblock defects and
   authority hashes. It relied on the producer's zero-findings result and did
   not compare frontmatter evidence against source pages 002/003. This was a QA
   scope gap, not evidence that frontmatter was correct.
7. There is no negative test that a source `СОДЕРЖАНИЕ` or authors page plus
   missing publication policy must fail before rendering.

## Reusable remediation contract

### 1. Versioned, closed Stage-40 HTML source config

Introduce a versioned KB Creator HTML source-config contract validated both
when the publication contract is authored and again immediately before Stage
40. It must distinguish:

- `policy_state: deferred` — legal only while downstream HTML is not runnable;
- `policy_state: stage40_ready` — required by the HTML adapter.

The closed semantic portion must contain:

- ordered page roles or a validated `page_map`;
- authoritative frontmatter order and body start;
- cover/title declaration;
- credits pages and presentation policy;
- TOC mode (`preserve_and_link`, explicit generated mode, or disabled), source
  page/title, and link-resolution authority;
- generated-mode justification when the accepted source has a contents page;
- expected frontmatter-manifest invariants.

Runtime paths, output paths, acceptance booleans, and temporary evidence roots
remain adapter-derived and must not enter the source config.

### 2. One normalized policy, one default decision

The adapter must compile the closed source config into one resolved
frontmatter policy. All renderer phases—source capture, page annotation,
replacement, ordering, manifest authoring, and QA—must consume that same
resolved object. Remove the current split where source capture defaults to
`generated` but TOC rendering later merges a `preserve_and_link` default.

For the strict KB Creator publication path, absence is not a default: it is an
error. Generated TOC remains available only through an explicit config choice.

### 3. Authority-backed completeness check

Before invoking the renderer, Stage 40 must compare the resolved policy to the
accepted source graph:

- every declared frontmatter page exists exactly once in accepted MASTER_RU;
- typed page roles are unique and ordered;
- a source contents page is not paired with implicit/generated mode;
- configured source entries resolve or have an explicit reviewed mapping;
- configured credits pages are present and have a declared rendering mode;
- `policy_state=deferred` fails before any Stage 40 artifact write.

Page roles should come from reviewed reconstruction/publication metadata, not
from scenario-specific Python or Russian-heading heuristics. A lexical scan may
be a defensive contradiction check, not the authority source.

### 4. Output closure gate

The adapter must independently validate `frontmatter_manifest.json` and final
HTML before reporting pass. For Number 7 Dream-shaped source order, acceptance
criteria are:

- one source-origin `<nav>` titled `Содержание`;
- page 003 removed from ordinary body flow;
- source entries conserved in order and each link resolved;
- no second exhaustive generated heading dump;
- page 002 rendered as the declared credits/authors frontmatter treatment;
- exact declared flow `cover -> credits -> source_toc -> body`;
- body begins on page 004;
- zero wrong-origin, duplicate-source-page, unresolved-link, missing-credits,
  or flow findings.

### 5. Required regression matrix

Add all of the following:

1. Production-shaped neutral adapter integration: accepted four-page Markdown
   containing cover, credits, source contents and body plus a complete generic
   config; assert exact derived policy, manifest flow and HTML roles.
2. Negative: source-contents authority plus missing/deferred TOC policy fails
   before renderer invocation.
3. Negative: declared/known credits page plus missing credits role/policy fails
   before renderer invocation.
4. Negative: unresolved source entry, duplicate visible source contents, wrong
   frontmatter order, or generated origin under preserve mode fails.
5. Compatibility: complete legacy `page_map` +
   `production_html.toc_policy/credits_policy` normalizes to the same resolved
   policy and passes.
6. Explicit generated mode: a source without contents, and a source with a
   separately recorded reviewed replacement decision, each exercise the legal
   generated branches.
7. Number 7 Dream regression fixture: pages 002/003 from the accepted master or
   a minimal semantic equivalent; assert authors are typed frontmatter and the
   21 source TOC rows, title and order survive as linked navigation rather than
   becoming the generated heading set.

## Migration and compatibility notes

- Do not mutate run09; retain it as immutable defect evidence.
- Updating Number 7 Dream `html.json` changes a bound config identity. Re-author
  the publication contract and create a fresh successor run. Rebind the
  byte-identical accepted MASTER_EN, MASTER_RU, 298 translations and 19 accepted
  ArtView decisions through existing strict successor commands.
- Complete legacy configs that already declare `page_map`, TOC policy and
  credits policy can be normalized by an explicit compatibility adapter. Do
  not preserve the missing-field fallback in the strict publication path.
- Dissociation already explicitly declares `generated_hierarchical`; it should
  remain valid after normalization, subject to the same `stage40_ready` and
  manifest gates.
- The canonical `frontmatter` object should become the source of truth.
  `production_html.toc_policy` may remain a generated compatibility projection,
  but two independently editable copies would recreate drift.
- This remediation does not authorize editing accepted masters. It is a
  publication-policy correction and fresh projection from unchanged accepted
  authorities.

## Forbidden shortcuts

- No hand edit of run09 HTML, source/derived config evidence, or manifests.
- No mutation or re-acceptance-by-implication of accepted MASTER_EN/MASTER_RU.
- No Number 7 Dream page numbers, Russian titles, or entry strings hard-coded
  in reusable Python.
- No inference of authoritative page roles solely from localized heading text.
- No silent fallback from missing/deferred policy to generated TOC.
- No relabeling the generated exhaustive heading list as preserved source
  contents.
- No source-page suppression unless source-entry conservation and link closure
  pass.
- No borrowing another scenario's page topology or TOC rows; only the schema,
  resolver and gates are reusable.
- No in-place config change behind an existing contract/run identity.
- No Stage 50, DOCX, PDF, acceptance, release, commit, or push in this task.

## Files and evidence checked

- Governance/status: `AGENTS.md`, `docs/governance/nri_goal_governance.md`,
  `kb_creator/README.md`, `kb_creator/PROJECT_STATUS.md`, active plan/context.
- Prior authority decisions: Number 7 Dream M3 architecture and M4
  implementation receipts; structural-fidelity audit and page-002 decision.
- Recorded reusable rule: Translator frontmatter standard, README/status,
  commits `5316752c`, `0470919f`, and relevant renderer tests.
- Active data: accepted run09 MASTER_RU; Number 7 Dream base `html.json`,
  contract/effective config; derived HTML config/source; HTML; producer report,
  adapter receipt and frontmatter manifest.
- Active code/tests: `kb_creator/pipeline/publication_adapters.py`,
  `translator/translator.py`, `kb_creator/tests/test_publication_html_adapter.py`,
  `translator/tests/test_recovery_support.py`, publication contract schemas and
  author/control-plane validation.
- Comparison only: complete Viral and Dissociation HTML configs. Their scenario
  topology was not treated as Number 7 Dream authority.

No code, config, generated output, canonical plan/context/status, acceptance,
or Git state was changed.
