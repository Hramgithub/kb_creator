# U9 independent release review — immutable receipt v01

- Goal/step: `20261004-user-docx-review` / U9 frozen full-goal release review.
- **Review kind: release. Recommendation: reject this frozen release candidate.**
  Required baseline QA has now been consumed. Its passing tests do not close
  the four independently reproduced normal-pipeline contract defects below.
- Independence: I did not implement or materially design the candidate or its
  remediation. I wrote only assigned diagnostic probes/evidence and receipts.
  Expected fail-closed boundaries in the checkpoint are findings, not material
  implementation design. Main retains orchestration and repair decisions.

## Exact revision and freeze

Canonical release v01 records freeze `2026-10-04 22:46 UTC`. Prospective U8
production/test/contract/CLI/doc revision is the exact42-file manifest
`audit/fidelity-engineering/U8-v03-implementation-hashes.json`, SHA-256
`5572A5C0C3FB9E660563D4BC9DB5CDEA1E352892CA58C6BAF6B021036765BB1D`.

Independent actual-byte start/checkpoint verification found42/42 matching
size/hash pairs, zero mismatches. Evidence:
`audit/release-critic-v01/freeze-start-v01.json` and
`audit/release-critic-v01/freeze-checkpoint-v01.json`; critic checkpoint cutoff
`2026-10-04T22:51:28.7968623Z`. Completed U8 QA separately confirms post-suite
42/42 unchanged identities. No mutable branch name is substituted for this
manifest. Full file identities remain in those artifacts.

Reviewed-artifact repair API remains independently approved within U6 scope,
not implicated by these normal-route defects:
`pipeline/reviewed_docx_revision.py` SHA-256
`ECF14988614230151542B5EFE358A1FF1A8554A7B6718BCF00AFBE7AADBB5A90`;
seven-file manifest and F1–F6 closure are in
`audit/critic-u6-recheck-v05/report-v05.md` and `handoffs/U6-api-critic-v05.md`.

Three unchanged corrected DOCX candidates under `working/user-review-20261004/`:

| Candidate | SHA-256 |
| --- | --- |
| fear-reader-v01/document.docx | D79AB0EC131D2C6926D868EB037786093F615AEAF122895AA4487254616CF33E |
| leningrad-reader-v01/document.docx | CC3A1F96D82121C07938D860EF88186AA33A32199B578D4C7C2DE05F4C83AD23 |
| kremlin-reader-v01/document.docx | 5573888152F7EDAB32D483E4D652FD465694BFBF1764CC708C3EF7C042AA87D8 |

## Release-blocking findings

Exact finite inputs, reproduction commands, line locators, controls and expected
behavior: [immutable interim checkpoint](../audit/release-critic-v01/checkpoint-v01.md).

| ID | Severity | Reproduced defect | Exact result under audit/release-critic-v01 |
| --- | --- | --- | --- |
| R1 | P1 | Normal characteristic projection accepts a partial operand (`STR 13`, selected3→15 becomes `STR 115`) and field misbinding (declaredSTR edits `Luck 13`→`Luck 65`). Actual Word text observation accepts both. | edition-retry-v01/result-v01.json |
| R2 | P1 | Edition row accepts source_page9999 on a one-page PDF and a story outside the reviewed section domain; projection and actual Word observation also pass. | edition-retry-v01/result-v01.json |
| R3 | P1 | `accepted_direct_mapping` applies `Know`→`Выдуманный навык` although both correctly hashed accepted registry/overlay contain empty term lists; the claimed reference is not resolved to a mapping. | terms-retry-v01/result-v01.json |
| R4 | P2 | A drawing placed before the anchor text and paired bookmarks within the same paragraph passes an explicit after-anchor plan, actual drawing verification, sealed report and reopened report verification. | graphics-v01/graphic-results-v01.json |

No P0 finding. Findings concern the prospective normal builder's shared
validation/projection/observation seams. The diagnostic harness directly
exercised those exact callables; it did not claim every invalid plan was run
through the complete public CLI/builder. Integration locations are recorded
in the checkpoint. These are mechanically inconsistent but honestly resealed
authorities, not merely stale hashes. No actual-book corruption is demonstrated.

Positive/negative controls: wholeSTR13→65 passes; valid graphic passes; incorrect
extent and header graphic reject; resealed report-observation tampering and
semantic promotion to approved reject. The tested mechanical/visual pending
distinction remains honest, but does not waive R1–R4.

## Completed QA consumed

- `handoffs/U8-fidelity-qa-v04.md` and detailed
  `audit/fidelity-qa-v04/U8-normal-fidelity-qa-v04.md`: exact19-module prepared
  regression **219 passed,14 subtests passed,1 unrelated pre-existing Word COM
  skip,0 failures/errors**, runtime133.24s. Contract-schema isolated check1/1
  also passed. The19-module list and runner details are in the QA report.
- Bundled Python with existing local pytest9.0.2 was used; no installation or
  alternate interpreter. Initial sandbox scratch cleanup hit actual access
  denial; permitted same-suite elevated retry passed. Critic synthetic probes
  likewise used the permitted backend after confirmed audit renderer-stage
  access denial. Scratch artifacts are not commit scope.
- QA rehashed six original reviewed latest DOCX, three corrected candidates
  and canonical glossary before/after its run, and confirmed all nine retired
  format paths remain absent. Glossary SHA-256 remains
  `8F6A41A64CA5A90621F6B8C2F3B40B4FE3658D7DE88B0D0A82BF95C1F82E6800`.
  These completed QA checks are consumed, not claimed as freshly repeated by
  the critic after the instruction to stop additional inspection.
- Prior exact book/source/visual evidence remains applicable by unchanged
  identities: `U5-fear-qa-v04.md`, immutable Fear correctionsv05/v06,
  `U5-two-book-qa-v05.md`, `U7-source-qa-v03.md`, and U6 criticv05. They bind
  all367 individual page inspections (279/64/24),146 numeric source records,
  197 operations plus the separate effect,26 Fear opening placements and
  original media/comment conservation. This critic previously rehashed those
  page identities, but does not claim personally re-viewing all367 pages.
- QA explicitly leaves R1–R4 open; prepared passing regressions are not
  evidence that these independent adversarial cases reject.

## Intentional exclusions retained

This is limited skill-name/characteristic-number adaptation, not full7e
mechanics or skill-pool reconstruction. Resistance/MP/HP/unknown plainPOW and
missing Number7 source exceptions remain explicit. Global glossary CSV/status
has not been changed. Current books are preserved reviewed-artifact successors,
not normal-v3 replay or restored lost-master lineage; repaired code does not
retroactively claim authorship of historical candidate bytes.

Fear restores23 scenes and retains3 across26 openings while preserving old
drawings. Leningrad/Kremlin art is conserved, not certified source-art complete.
Field-only treatment is main's bounded technical decision, not a user-named
technical override. Source paint discovery is incomplete; exact all-page human
source review remains mandatory. XML mechanical observations do not establish
rendered visibility or semantic approval. V1/v2 archives remain read-only and
not assessed for source completeness.

DOCX is the only deliverable. No published HTML/PDF was generated by this
review; synthetic PDF inputs are diagnostic fixtures, not deliverables. Exactly
nine approved outdated latest files were previously recycled; QA confirms their
absence, not new deletion by this critic. Original source PDFs/assets and all
six reviewed original DOCX remain preserved. No commit, push or Foundry action
is authorized or performed. Human book acceptance is not inferred.

## Handoff and administrative record

- Files checked: canonical task/release/context and governance; U8 engineer
  v03 receipt/report/42-file freeze; source-graphics, edition-projection,
  reader-fidelity and affected normal public-seam code; prepared fixture/tests;
  previous U6/book/source/visual evidence; completed U8 QA receipt/report.
  Detailed exact probe inputs are linked from the checkpoint.
- Files changed: `audit/release-critic-v01/review_v01.py`, start/checkpoint JSON
  hashes, synthetic probe inputs/results, immutable checkpoint, and this new
  immutable handoff. No code/tests/contracts, books/sources, old evidence,
  canonical plan/context/status/release or unrelated files edited.
- Blocker/next action: main assigns bounded R1–R4 remediation, captures new
  code/evidence freeze, runs affected regression/adversarial QA, then requests
  fresh independent release review. Do not treat this rejection as requiring
  actual book reauthoring without evidence of candidate impact.
- Mutation invalidation: any relevant implementation/dependency/authority or
  candidate change invalidates this receipt for the changed revision. Prior
  rejected baseline evidence stays immutable; no acceptance carries forward.
- Critic role/model/effort requested: `gpt-6-astra` / `high`; actual platform
  identity/effort unavailable. Assignment state `platform-unverified`; this
  bounded release review is COMPLETE with **reject** recommendation.
- Orchestrator policy owner remains main `/root`, `gpt-6-sol` / `medium`.
  Scoped role override: none. No orchestration ownership transfer.
- Receipt timestamp: `2026-10-04T22:56:54Z`, using actual clock at QA consumption.
  QA prose labels its timestamp23:01UTC; exact execution times are not inferred
  from that drafting label. The test/freeze counts and consumed file contents
  above are the evidence, not that timestamp label.
- Elapsed: approximately11 minutes wall time since release assignment,
  including waiting for required QA. Exact platform elapsed/token accounting
  unavailable. Token use: unavailable.
