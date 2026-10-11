# U9 independent release review — immutable receipt v02

- Goal/step: `20261004-user-docx-review` / repaired frozen release v02.
- **Review kind: release. Recommendation: approve within the exact frozen and
  declared scope below.** R1–R4 are CLOSED. No remaining release-blocking
  severity finding was reproduced in this finite recheck. Completed independent
  QA v05 has been consumed; this is no longer a recommendation pending QA.
- Independence: I did not implement or materially design the candidate or its
  remediation. I wrote only assigned diagnostic probes/evidence and receipts.
  Main `/root` retains orchestration, canonical integration and user-facing
  acceptance decisions. Human book acceptance is not inferred by this receipt.

## Candidate revision and freeze

Canonical release v02 freeze: `2026-10-04 23:14 UTC`. Prospective U8 v04 normal
DOCX policy/fidelity implementation is the exact43-file manifest
`audit/fidelity-engineering/U8-v04-implementation-hashes.json`, SHA-256
`9A948C1264D64A48E551221E5604FC6435F2641A9B50AAEE13079C5F657C8BEC`.
All42 predecessor entries remain, plus the versioned v2 normal plan schema.

The critic independently rehashed all43 actual file sizes/hashes at review
start and checkpoint: zero mismatches. Evidence:
`audit/release-critic-v02/freeze-v02.json` and
`audit/release-critic-v02/freeze-checkpoint-v02.json`, checkpoint clock
`2026-10-04T23:17:56.9539787Z`. Independent QA v05 separately confirms all43
identities still match after its completed full/focused runs. The exact manifest,
not a branch label or mutable path alone, defines this approved revision.

Unchanged reviewed-artifact repair API is independently approved under
`handoffs/U6-api-critic-v05.md`, its seven-file manifest in
`audit/critic-u6-recheck-v05/report-v05.md`; API SHA-256
`ECF14988614230151542B5EFE358A1FF1A8554A7B6718BCF00AFBE7AADBB5A90` was freshly
matched. U6 F1–F6 closure remains separate from normal-route R1–R4 closure.

The three actual corrected DOCX candidates, freshly rehashed by the critic and
also preserved through QA, are under `working/user-review-20261004/`:

| Candidate | SHA-256 |
| --- | --- |
| fear-reader-v01/document.docx | D79AB0EC131D2C6926D868EB037786093F615AEAF122895AA4487254616CF33E |
| leningrad-reader-v01/document.docx | CC3A1F96D82121C07938D860EF88186AA33A32199B578D4C7C2DE05F4C83AD23 |
| kremlin-reader-v01/document.docx | 5573888152F7EDAB32D483E4D652FD465694BFBF1764CC708C3EF7C042AA87D8 |

Predecessor release v01 rejection remains immutable and is not rewritten.
Approval here applies to v02's changed implementation and exact unchanged
book identities only; it does not retrospectively approve the rejected code.

## Independent findings disposition

Detailed finite recheck, inputs, exact commands and controls:
[recheck-report-v02](../audit/release-critic-v02/recheck-report-v02.md) and
[recheck_v02.py](../audit/release-critic-v02/recheck_v02.py).

| Finding | Prior severity | Disposition / evidence |
| --- | --- | --- |
| R1 numeric operand/field binding | P1 | CLOSED. WholeSTR13→65 and styled-label controls pass. Partial prefix/suffix, Luck misbound asSTR and unedited-exterior mutation reject; fragmented numeric operand fails closed; changed actual Word value rejects. |
| R2 source/occurrence domain | P1 | CLOSED. Page/story/book/entity/occurrence membership and source-render binding reject foreign/missing/stale values against a valid v2 reviewed domain. Reopened Word moved outside declared story rejects. |
| R3 accepted mapping authority | P1 | CLOSED. Actual accepted CSV and explicit book-overlay mappings pass projection/Word controls. Empty/unaccepted authority, invented target, wrong reference/context reject. Unbound primary/editorial dispositions stay typed unsupported_authority/needs_decision. |
| R4 same-paragraph graphic order | P2 | CLOSED. Valid before/after placements pass both directions; inverted order rejects both directions using actual Word. Resealed observation tampering and promotion to semantic approval reject offline. |

Thirty-eight independently exercised current-format cases:16 edition/domain,
9 terminology,7 graphic/offline,6 public-builder; nine expected valid accepts
and29 expected invalid rejects agree. All semantic negatives are honestly
resealed against current format-valid authorities. Closure does not rely on
an obsolete-schema rejection. Per-case evidence is in
`edition-retry-v02/results-v02.json`, `terms-retry-v02/results-v02.json`,
`graphics-retry-v02/results-v02.json`, and `public-v02/results-v02.json`
under the owned audit root.

The public normal builder successfully handles both source-visible in-master
art and reviewed art absent before the master. The latter is inserted only
into the reader DOCX; both masters remain byte-identical. Both packages reopen
as `verified_pending_visual_review`, not semantic approval. Partial operand,
foreign page, invented mapping and None authority reject before output root
creation. Synthetic source/plan/builder/offline checks are real; the upstream
language fixture uses its documented test-only verifier patch. This is not
evidence that a current real book was reconstructed through that fixture.

## Independent QA consumed

- `handoffs/U8-fidelity-qa-v05.md`, freshly matched SHA-256
  `54B42B3EE73C840D31FF224E0F27FCDACFC6BF122FF689B96C18E47C086D8A72`.
- `audit/fidelity-qa-v05/U8-normal-fidelity-qa-v05.md`, freshly matched SHA-256
  `D7C59CE3F1F66E4CFEE7BF2CF8B607907856F4F08CB709EC44AC9D070FE1A0C2`.
- Full exact19-module prepared suite: **239 passed,14 subtests passed,1
  pre-existing unrelated Word COM skip,0 failures/errors**,140.07s. Focused
  four-module R1–R4 suite: **48 passed,0 skips/failures/errors**,11.18s. Exact
  module argv, runner identity and persistent output logs are referenced by
  QA's `pytest-run-manifest-v01.json`; these were QA executions, not falsely
  claimed as a second critic full-regression run.
- Bundled Python with appended existing local pytest9.0.2 library; no package
  install or interpreter substitution. Actual sandbox temporary-directory
  access denial justified the same bounded suites/probes on the permitted
  elevated backend. New scratch roots were not reused or cleaned broadly.
- QA confirmed43/43 pre/post hashes, six original reviewed DOCX and three
  corrected DOCX unchanged, canonical glossary unchanged, and9/9 specifically
  retired HTML/PDF paths absent. These are consumed independent QA checks;
  no fresh unchecked preservation claims or new deletion are implied.

## Actual-book evidence and approved limits

Critic's `books-v02/results-v02.json` freshly rechecks all three actual
manifest/original/source/authority preflights,146 numeric source-QA bindings,
197 approved operations plus the separate effect, exact reverse restoration
of canonical original Word XML and conservation of original media/comments/
other package content. It freshly rehashes all367 bound QA page PNGs:
279 Fear,64 Leningrad,24 Kremlin. Fear26 opening coverage comprises23 restored
source scenes and3 retained, with original63 drawings preserved.

Consumed current-book receipts: `U5-fear-qa-v04.md`, immutable correctionsv05/v06,
`U5-two-book-qa-v05.md`, `U7-source-qa-v03.md`, and U6 criticv05. The full-page
visual inspections are those bounded QA contributors' recorded work; this
critic does not claim personally repeating367 page views. Fear index/inventory
metadata correction remains verified; historical typo-attribution clarification
does not alter source/candidate bytes.

The approval explicitly retains these boundaries from canonical release v02:

1. Current books are preserved reviewed-artifact successors, not normal-v3
   replay or restoration of missing masters. New API/normal code does not
   retroactively claim authorship of historical candidate bytes. No actual
   book was shown to contain the rejected normal-route R1–R4 defects.
2. Adaptation is limited to approved names/numbers, not a full7e mechanics or
   skill-pool rebuild. Resistance/MP/HP/unknown plainPOW exceptions and absent
   Number7 source remain explicit. Already-percentile values are not guessed
   or reconverted. The other three reviewed books remain original versions.
3. Leningrad/Kremlin original art is conserved; full source-art completeness
   is not assessed. Field-only treatment is main's bounded implementation
   decision, not a user-named technical override. Fear's specific26-opening
   restoration evidence is not broadened into an unsupported global claim.
4. Prospective source paint discovery remains incomplete. Exact all-page
   human source review and future exact-output rendered Word review remain
   mandatory. XML mechanical closure cannot certify rendered visibility or
   semantic correctness; `needs_output_review`/`verified_pending_visual_review`
   states stay honest. Approval of this guard does not pre-approve future books.
5. Normal plans use v2; older plans do not silently upgrade. Unbound
   primary-rule/editorial normal-route exceptions are unsupported/pending
   until separately authorized by a resolvable contract. That limitation
   does not revoke existing authorized U6 artifact-repair exceptions.
6. DOCX is the only deliverable. Historical v1/v2 archives remain read-only/
   source-completeness-not-assessed. Separate PDF utility's environmental test
   skip does not substitute for existing native Word visual evidence.
   Synthetic/service/source PDF inputs are not published PDF output.
7. Global glossary CSV/status remains unchanged; QA confirms SHA-256
   `8F6A41A64CA5A90621F6B8C2F3B40B4FE3658D7DE88B0D0A82BF95C1F82E6800`.
   Exactly nine approved outdated latest format files were previously
   recycled; sources/assets/six original DOCX preserved. No commit/push,
   Foundry action or user acceptance is authorized/inferred here.

## Administrative handoff

- Files checked: current U9 task/release freeze, U8 engineer v04 receipt/report/
  final regression log/43-file manifest; exact changed edition/reader-fidelity
  and current test-authority seams; valid-format independent probe inputs;
  current book/source/visual/conservation evidence and completed QA v05
  receipt/report. Prior U6 and rejected U9 receipts remain immutable.
- Files changed: only new harness, diagnostic fixtures/results, freeze JSON
  and evidence report in `audit/release-critic-v02/`, plus this new immutable
  receipt. No implementation/test/schema/book/source, prior evidence or
  canonical plan/context/status/release file edited. Scratch/log/source
  fixtures and unrelated dirty files are outside potential commit scope.
- Blockers: none within this exact approved release scope. Human book
  acceptance and future-run source/output reviews remain outside this gate.
  Next action: main may integrate this independent decision into canonical
  state and present the scoped result to the user, without implying broader
  source completeness, full7e adaptation or future semantic approval.
- Invalidation: any relevant implementation/dependency/authority/candidate
  mutation invalidates this receipt for that revision and requires a new
  applicable freeze/review. Approval cannot be carried to altered bytes.
- Requested critic model/effort: `gpt-6-astra` / `high`; actual platform
  identity/effort unavailable. Assignment state `platform-unverified`, bounded
  release review COMPLETE. Orchestrator policy owner remains main `/root`,
  `gpt-6-sol` / `medium`; no ownership transfer. Scoped role override: none.
- Time: review start `2026-10-04T23:14:44.8128674Z`; final QA consumption and
  receipt timestamp `2026-10-04T23:22:27.7541742Z`. Approximately7m43s wall time,
  including waiting for QA. Exact platform usage unavailable. Token use:
  unavailable.
