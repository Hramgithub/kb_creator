# Number 7 Dream HTML publication regression correction plan

Goal id: `20260918-dream-html-heading-toc`

Status: active — fresh run14 HTML candidate is built and awaits explicit
HTML acceptance; no Stage 50/DOCX/PDF work is authorized

## Objective

Correct three coupled regressions in the reusable publication pipeline:

1. restore the governed authors/frontmatter treatment and preserve the
   source-authored contents instead of replacing it with an unrelated generated
   heading dump;
2. restore the source-backed Appendix C character hierarchy and ordering so
   repeated leaf headings do not become peer TOC entries;
3. keep Appendix A stat blocks semantically structured and row-preserving
   without rendering them as quote/callout boxes, while preventing character
   names from joining the first statistics row.

Establish why previously fixed rules fell out of the active assembly path,
close the reconstruction/configuration/adapter/renderer contract gaps with
regression tests, create immutable reconstruction and publication successors,
and stop at every explicit acceptance gate. A fresh Stage 40 candidate can be
built only after the corrected upstream successors are explicitly accepted.

## Authority and boundary

The user's three screenshots reject run09 as a publication candidate and
authorize a systematic pipeline correction plus rebuild. The existing accepted
reconstruction, MASTER_EN, MASTER_RU, translations, and ArtView decisions remain
immutable historical authorities: none may be edited or relabelled. The audit
proved that Appendix C hierarchy and four Appendix A title/stat joins already
exist in those authorities, so a fully correct result requires a new
reconstruction successor and then new MASTER_EN/MASTER_RU/ArtView successors.
Run09 is not edited or accepted. No successor acceptance is inferred. Stage 50,
DOCX, PDF, release, commit, and push remain outside scope.

## Role contract

- Orchestrator: policy `gpt-5.6-sol`, medium; canonical state, source audit,
  integration, authority decisions, recovery, and user-facing synthesis.
- Architect: policy `gpt-5.6-sol`, high; independently identify the earliest
  justified correction layer and generic contract. No implementation ownership.
- Bounded QA: policy `gpt-5.6-luna`, low; verify the fresh candidate, regression
  suite, heading tree, TOC membership, and absence of downstream artifacts.
- Independent critic: policy `gpt-5.5`, medium; read-only release-gate review.
  The critic does not implement or design the change.

## Steps

| Step | Owner | Status | Evidence / next action |
|---|---|---|---|
| T1 Audit prior rules and the full three-defect class | orchestrator + architects | complete | R1/R2/R3 prove three separate boundaries: reconstruction structural incompleteness, deferred HTML policy accepted as ready, and semantic statblock coupled to quote presentation |
| T2 Specify the correct reusable layers | architects + orchestrator | complete | Canonical fix is upstream reconstruction completeness plus Stage-40 policy readiness and semantic presentation mapping; no heuristic or generated-output patch |
| T3 Implement generic reconstruction prevention | orchestrator | complete | `reviewed_role_outline_and_partitions_v2` enforces exact reviewed partitions plus character-statistics/pregenerated outline completeness in Stage 05/06; inheritance and OCR-correction paths are regression-tested |
| T4 Implement generic Stage-40 prevention | orchestrator | complete | Closed `deferred/stage40_ready` policy, one normalized source-TOC/credits flow, neutral typed statblock DOM, final output gates, Number 7 Dream ready policy, and regression tests are implemented |
| T5 Author and materialize a reconstruction successor | orchestrator + bounded QA | complete — rejected review evidence | Fresh CPU run `20260918-cpu-first-07` and replay18/v29 produced sealed Stage 05/06 and passed bounded QA, but user review correctly identified that all seven statblocks and their title headings still use visible `>` quote transport. Replay-18 is not accepted and must not be promoted |
| T5a Remove quote transport from semantic statblocks and rematerialize | orchestrator + engineering + bounded QA | complete — accepted | V2-only `semantic_span`, exact Stage-40 paired projection, neutral renderer, conflict-resolution support, documentation, and negative tests are implemented. Replay-21/v33 passed bounded QA; the user explicitly accepted its `RECONSTRUCTED_EN.md`. Promotion receipt SHA-256 is `A03FA27CD6569ED4F8304BB283E049942AD2DEEC9A772DFCBE28C77E8EDE0ADF` |
| T6 Rebuild publication successors through ArtView | orchestrator + user gates | complete | The user accepted MASTER_EN SHA-256 `C3B4F13E3E43B2422704F1A7BCF61A5CF1762191B474FAAE5C4C4243289367AA` and MASTER_RU SHA-256 `904133D5057172C404D28F3BCF2A5E4C578304A59382512D1B31FC56AE0FDAB2`. Fresh run14 reproduced both exact binaries, rebound 298/298 translations by exact source, rebound and validated 19/19 accepted ArtView decisions, and completed Stage 31 |
| T7 Build and verify a fresh Stage 40 successor | orchestrator + bounded QA | complete | Run11 first exposed a wrong global interpretation of page-local semantic spans. The generic v2 bridge now maps `semantic EN span -> accepted MASTER_EN -> Stage20 unit -> sealed RU payload -> MASTER_RU range`. Run12 then exposed ignored `frontmatter_order`; run13 exposed a non-nesting-aware page regex. Both defects are fixed generically and covered by regressions. Fresh run14 identity is `8E280A3F4919CBC76A50FA54FBD091FD050DC2CA6CB702027247EF5F81EF2863`; Stage 40 reached `awaiting_html_acceptance`, HTML SHA-256 `3F77B38C477D8E137CF22867BA9713EAF6AFD19C8168C07F1E8664E1790D1E21`. Bounded QA is PASS across 166 manifest-listed files; receipt SHA-256 `4B588F952161AC280976250836F02A32FA281D78A56CBA7FD80E4AFA02FEC123` |
| T8 Independent release-gate review | independent critic | complete — PASS | Independent gpt-5.5 release review found no blockers and confirmed implementation inventory closure, frontmatter order, 18-link source TOC, Appendix C hierarchy, seven neutral page-18 statblocks, and absence of Stage 50+. Receipt SHA-256 `6E50AA27263DE8565BA736DCC1E2BCAEFC7927E1CF6BB563B2DF57E04C02C84A` |
| T9 HTML acceptance gate | user + orchestrator | active | Present exact run14 candidate for explicit user acceptance; do not infer acceptance or continue downstream |

## Definition of Done

- The authors/frontmatter block follows the recorded publication rule and the
  source contents is preserved/linkable; no generated all-heading dump replaces
  it.
- Every pregenerated character on source pages 21–26 has the same justified
  semantic heading level; `Background` and `What You Know About Stanwick` are
  subordinate leaves, not peer top-level TOC entries.
- Appendix A stat blocks retain distinct name/stat/attack/skills rows without
  quote markers in `RECONSTRUCTED_EN`/MASTER, quote/callout decoration in HTML,
  or title/stat concatenation.
- The HTML navigation contains only the governed entries and levels, without a
  scenario-specific hard-coded output patch.
- Reconstruction rejects a visually titled statblock without exactly one
  reviewed title node and rejects incomplete `pregenerated_characters` outline
  coverage; reviewed intra-source-block partitions conserve every source byte.
- Stage 40 rejects a deferred/missing frontmatter contract, consumes one
  normalized policy, and verifies final manifest/DOM rather than vacuous counts.
- Semantic kind, Markdown transport, and publication presentation are separate:
  a typed statblock is a sidecar-bound neutral Markdown span and a neutral
  publication section/card, never a quote/callout by fallback. Standard
  blockquotes remain reserved for source quotations, handouts, and callouts.
- Reusable tests cover all three contracts, the seed defects, stale/ambiguous
  bindings, and neutral synthetic cases.
- A fresh successor chain passes the explicit reconstruction/MASTER/ArtView
  gates before Stage 40, then bounded QA and independent review, and stops
  before HTML acceptance/Stage 50.
