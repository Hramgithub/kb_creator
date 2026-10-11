# Dissociation full publication plan

Goal id: `20260914-dissociation-publication`

Goal state: `active`

Release state: `pending fresh independent review`

## Objective

Build a complete reproducible KB Creator package for `Dissociation` from the
immutable English source PDF: `RECONSTRUCTED_EN`, `MASTER_EN`, `MASTER_RU`,
ArtView/config evidence, HTML, DOCX, PDF, and a stable production package with
machine evidence, explicit user acceptance gates, and an independent release
decision.

## Role contract

- Governance: `docs/governance/nri_goal_governance.md`.
- Orchestrator policy owner: `gpt-5.6-sol`, medium; actual platform identity is
  unavailable, assignment state `platform-unverified`.
- Architect: `gpt-5.6-sol`, high; owns generic pipeline/control-plane boundary
  and remediation specifications.
- Engineer for this goal: `gpt-5.6-sol`, high; owns reusable implementation
  assistance under an explicit user-scoped override. A matching bounded
  contributor was assigned for the no-CUDA capability increment and closed
  after its receipt; actual platform model identity remains unavailable, so the
  assignment state is `user-overridden-platform-unverified`.
- Independent critic: `gpt-5.5`, medium; owns independent process,
  implementation, and mandatory final release review.
- Bounded executor: `gpt-5.6-luna`, medium.
- Bounded QA: `gpt-5.6-luna`, low.
- Scoped override: engineering role only, `gpt-5.6-sol` at `high`, requested by
  the user on `2026-09-14`. All other role assignments remain unchanged.

## Hard boundaries

- Treat the source PDF and any additional source images as immutable inputs.
- Do not reuse Innsmouth or Viral page ranges, counts, topology, publication
  policy, or accepted decisions as facts for Dissociation.
- Minimize manual processing. Put repeatable behavior in scenario-neutral
  package code, contracts, configuration, stage manifests, and tests.
- Do not create a `build_dissociation_*`, `freeze_dissociation_*`, or equivalent
  scenario-specific script family.
- Human decisions are limited to unresolved reconstruction semantics, reader
  editing, translation/proofreading, visual-art selection, and acceptance.
- A candidate, passing test, or agent report is not acceptance.
- Generated HTML and PDF are never edited directly.
- Publication order is fixed as accepted `MASTER_RU` plus accepted ArtView and
  effective configs -> HTML -> DOCX -> PDF. PDF generation directly from HTML
  is forbidden.
- ArtView, its accepted decision manifest, and every effective build/render
  configuration are mandatory production-package artifacts, not temporary QA.
- The exact shared CoC terminology authorities used by MASTER_RU must be
  hash-bound and retained in the production package.
- MinerU remains the reconstruction engine. Local CPU `pipeline/txt` and
  `pipeline/ocr` views are mandatory. GPU-backed local `hybrid`/`vlm` views are
  optional enrichment and only those views become `SKIPPED` when GPU capability
  is absent; absence of GPU must not skip the reconstruction run.
- All execution is limited to the current station. Remote execution, handoff,
  or another host is not a fallback.
- Git commit and push require explicit user authorization.

## Work plan

| Step | Owner | Dependency | Deliverable | Status |
|---|---|---|---|---|
| 0. Intake and immutable source identity | Orchestrator / medium | none | Source identity, output scope, language and terminology decisions | completed |
| 1. Read-only PDF reconnaissance | Architect / high + orchestrator | Step 0 | Page topology, text-layer/layout risks, required entities and candidate page roles | completed |
| 2. Neutral reconstruction contract boundary | Architect + engineer + critic | Step 1 | Versioned reconstruction-only schema that cannot inherit Viral publication policy | completed |
| 3. Generic runner gap closure | Engineer / high (user override) | Steps 1-2 | Minimal scenario-neutral Wave 0 runner, manifests, review queue and tests | completed |
| 3R. Independent implementation review | Independent critic / medium | Step 3 | P0/P1 closure before live source execution | completed |
| 3C. Dissociation reconstruction contract | Orchestrator / medium | Steps 2-3R | Schema-valid declarative contract with no copied scenario facts | completed |
| 4. Three-view source reconstruction | Executor / medium + QA / low | Step 3C | Run-local MinerU CPU views, optional capability-gated GPU enrichment, comparison, decisions, fidelity audit and candidate | completed in accepted CPU-free replay run `20260915-cpu-replay-10`; exact compact-boundary correction, no MinerU/CPU rerun |
| 4P. Neutral publication architecture | Architect / high + critic / medium | User pipeline mandate | Additive contracts and corrected accepted `MASTER_RU + ArtView/configs -> HTML -> DOCX -> PDF` design | completed; P1 correction independently closed |
| 4PA. Publication Packet A | Engineer / high (user override) + critic / medium | Step 4P | Neutral publication schemas, fixed gate/control skeleton and synthetic P0 tests | completed; P0/P1 remediation independently closed; schema parity closed in Packet C |
| 4PB. Publication Packet B | Engineer / high (user override) + critic / medium | Step 4PA | Neutral MASTER_EN, MASTER_RU and ArtView v3 adapters with synthetic parity and gate tests | completed; four P1 remediations independently closed |
| 4PC. Publication Packet C | Engineer / high (user override) + critic / medium | Step 4PB | Accepted-input HTML adapter, explicit DOCX, selectable Word COM/local LibreOffice DOCX-to-PDF, render QA, package/offline verifier and production wiring | completed; independently closed with no P0/P1/P2 |
| 4PD. Publication contract authoring | Engineer / high (user override) + critic / medium | Step 4PC | Closed blueprint-to-contract author with automatic file identities and no acceptance inference | completed; P1/P2 remediation independently closed |
| 4PE. Shared terminology closure | Engineer / high (user override) + critic / medium | Step 4PC | Single system-level CoC CSV term gate plus durable package snapshot | completed; later unified under goal `20260916-coc-unified-terminology` |
| 4PF. Reconstruction promotion bridge | Architect / high + engineer / high (user override) + critic / medium | Step 4 | Immutable reconstruction upstream package, separate explicit acceptance receipt and strict publication preflight | completed for legacy/direct-v2/replay-v2; live materialize validation remediation independently closed with no P0/P1/P2 |
| 5. RECONSTRUCTED_EN acceptance | Orchestrator + user | Step 4 | Verified immutable reconstruction package and explicit acceptance | completed for run10; receipt SHA-256 `E660EA6BBF24BAE683715F9C433C68134DC946D6BF9CFD1EF40B867DE0FBEE0B` |
| 6. MASTER_EN publication | Engineer + QA | Step 5 | Verified reader-English candidate and explicit user acceptance | completed in current run29; SHA-256 `2EB528C44A2B1A20C00D167AD255BA0C767B74653564A9FE9182D6A3FC51CABE` |
| 7. MASTER_RU publication | Orchestrator + QA | Step 6 | New Russian master using common CoC 7e terminology and explicit acceptance | completed in current run29 with unified terminology; SHA-256 `25537977DC1CAB80B9DDC04E603F95BB601F3C1EB29BAAFB6FFAD161A5F02E84` |
| 8. Visual asset finalization | Engineer + QA + user | Step 7 | Hash-bound ArtView, accepted decision manifest and effective visual configs | completed in current run29 by strict exact-equivalence rebind of the user-accepted 2/2 choices |
| 9. HTML publication | Executor + QA + user | Steps 7-8 | Generated HTML from accepted MASTER_RU plus accepted ArtView/configs; structural/visual QA and acceptance | completed in current run29; SHA-256 `09D3E0618F9922255AE12A916D283FB9B2F900E8FE877C1072A52A44D8016B97` |
| 10. DOCX publication | Executor + QA + user | Step 9 | Generated DOCX from accepted HTML with render/layout QA and acceptance | completed in current run29; SHA-256 `D40140D8AD7C347B137042072826B16786F54AF5CECDE778748A8A6B8383A9CA`, 9 pages, no footer/page-number structures |
| 11. PDF publication | Executor + QA + user | Step 10 | Generated PDF from accepted DOCX only, complete render QA and acceptance | completed in current run29; SHA-256 `983AECFEE9395BAB44396E7EF600E98D930D2D07F7DB5A86FC9F0F835126CEAA` |
| 12. Production package | Engineer + QA | Steps 6-11 | Stable package including ArtView/configs, manifests, evidence index and offline verifier | completed in run29; package manifest file SHA-256 `551AF24D7575CCCAF4DBB4661F03D4A4C27430DAFDA5F109BA8E16ED8BBF0F79` |
| 13. Independent release review | Independent critic / medium | Step 12 | Release receipt for the frozen candidate | pending for run29; the run24 receipt is historical and cannot approve changed bytes |
| 14. Save point | Orchestrator / medium | Step 13 | Status sync; commit/push only if explicitly authorized | status synchronized; commit and push remain unrequested |
| 15. User-facing package ACL closure | Orchestrator / medium, engineering policy user override retained | Reviewed-DOCX successor | Wire the generic inheritance normalizer into all publication/materialization paths, repair run29, remove obsolete wrapper-only run72 artifact, and verify ACL plus regression tests | completed; 18 focused passed; expanded 139 passed, 3 skipped; 321 package objects checked with 0 protected ACLs |

## Definition of Done

- The complete requested artifact chain is reproducible from the immutable
  source and declared contract without scenario-specific executable code.
- All reusable additions have focused tests and preserve Innsmouth/Viral
  compatibility where relevant.
- Every stage emits identity-bound evidence and stops fail-closed on unresolved
  review items or stale inputs.
- The final PDF passes complete PNG render inspection with no layout defects.
- The final PDF is identity-bound to the accepted DOCX, and no direct
  HTML-to-PDF route exists in the accepted run.
- The production package has stable filenames, closed asset inventory, code and
  contract snapshots, ArtView/decision/config evidence, and a standalone
  verifier.
- The user accepts the required reader and visual stages.
- A fresh independent `gpt-5.5` release review approves the frozen candidate.

## Historical execution narrative

Repository-local `uv`, CPython 3.12.14, the CPU profile and both synthetic
MinerU methods are installed, receipted and verified on this station. The
provider receipt records `pipeline_cpu=ready`; `hybrid_cuda` and `vlm_cuda` are
locally unavailable because no NVIDIA device was detected. Packet B is
independently reviewed with no P0/P1 blocker. Real run
`20260914-cpu-first-01` failed closed before its first view because the cleared
MinerU child environment lacked a repository-local Windows home for
`modelscope`; generic home/cache isolation and retained failure diagnostics are
now independently closed. Real run `20260914-cpu-first-02` produced the first
two original-PDF views but was intentionally aborted after launcher descendants
retained anonymous output-pipe handles, making completion depend on manual
process termination. The reusable Windows Job Object runner now starts the
owned tree suspended, constrains handle inheritance, captures output to files,
and performs bounded owned-tree cleanup. Its P1 remediation is independently
closed with `224 passed, 1 skipped` and no P0/P1/P2. Fresh run
`20260914-cpu-first-03` then completed all three mandatory CPU views, recorded
both CUDA providers as skipped, and sealed Stage 03 comparison without manual
process intervention. Stage 04 failed closed because rendered view dimensions
differ and the generic triptych builder has no authority-defined canvas
normalization. Keep all three failed CPU runs immutable. The source-authoritative
MediaBox normalization architecture is independently accepted with no
P0/P1/P2. Its reusable implementation is independently closed with no P0/P1
and evidence of `28`, `82`, and `447 passed, 1 skipped`; two non-blocking P2s
track test-dependency discoverability and one unreachable duplicate `raise`.
Fresh run `20260914-cpu-first-04` then completed Stages 01-04 and reached the
intended `needs_review` boundary. Six visually reviewed page decisions pass the
production decision validator, full fidelity audit, and disposable materializer
as `candidate_ready_for_reconstruction_qa`. Exact production materialization
exposed a separate v2 authority gap: Stage 06 drops the sealed Stage 03
comparison path and the legacy loader looks for it under Stage 02. Because the
generic correction changes the implementation inventory, do not resume `-04`.
The explicit v2 Stage 03 comparison authority is independently closed with no
P0/P1 (`184 passed, 1 skipped`). Fresh `20260915-cpu-first-05` reached
`needs_review`; all six decisions revalidated against byte-identical packets.
Independent content review found two source-visible omissions that the selected-
block-only fidelity audit missed: the page 3-to-4 `malle-` continuation and the
page 5 Laboratory tunnel sentence. Both decisions are corrected and the
materialized candidate now validates, but the general audit class remains a P1.
Implement and independently close an all-source-text disposition/coverage gate
before Stage 05/06. The implementation changes the sealed inventory, so run
`-05` remains immutable and cannot be resumed. The source-visible completeness
gate is now independently closed with no P0/P1/P2 (`186 passed, 1 skipped`).
Start fresh run `20260915-cpu-first-06` and revalidate the corrected decisions
against its exact queue, comparison, packets, and visual identities.
After RECONSTRUCTED_EN is independently verified and explicitly accepted, the
reviewed neutral publication runner can begin Stage 10. Stage 50/60 must later
run in a Windows logon where Word COM activation succeeds; the current Codex
logon returns `0x80070520` and is not successful Word-export evidence.
The current execution policy and stop conditions are recorded in
`handoffs/orchestrator_mineru_local_execution_decision_20260914.md`.

## Publication Packet A checkpoint — 2026-09-14

Packet A now supplies additive publication schemas, a fixed ten-stage control
graph, explicit non-overwriting user acceptance receipts, run/config/tool/code
identity checks, and a synthetic one-stage-per-resume engine. Public production
`run` and `resume` remain deliberately unavailable until the real adapters are
implemented.

The first independent implementation review rejected two fail-closed gaps: a
Stage 50 adapter could retain an unmanifested PDF outside `artifacts/evidence`,
and a resealed package could list only the Stage 60 manifest. Remediation closes
the complete stage root, removes forbidden Stage 50 PDF/bridge residue before
quarantine, revalidates the prohibition on resume, and requires the exact
ordered eight-manifest Stage 10-60 chain plus six bound acceptance receipts.
The independent closure reran the attacks and the complete suite (`107 passed`):
no P0/P1 remains. One non-blocking P2 remains because several package-array
cardinalities are tighter in the runtime verifier than in the JSON Schema; it
must be closed before real package validation or release packaging.

## Publication Packet B checkpoint — 2026-09-14

Packet B adds scenario-neutral MASTER_EN v3, MASTER_RU packet/submission/
assembly, and ArtView v3 bundle/decision/application layers. It leaves the four
low-level translation primitives and all Viral/Innsmouth v2 routes unchanged.
The package schema P2 from Packet A is closed with exact cardinality and
uniqueness constraints.

The first implementation review found four P1 authority defects: outside-root
output targets, a non-closed MASTER_RU acceptance path, SHA-only rather than
exact source-graph membership, and unreachable/weak ArtView decision checks in
the package verifier. The engineer added authority-relative no-write paths,
closed receipt validation, exact `(path, bytes, sha256)` source membership and
reachable exact-once decision binding. Independent closure reproduced every
attack and found no remaining P0/P1/P2. Accessible evidence is `34 passed` plus
`14` subtests, MASTER_EN v3 `3 passed`, and ArtView v2 parity `9 passed` with one
unavailable generated Viral checkpoint test explicitly deselected.

## Publication Packet C checkpoint — 2026-09-14

Packet C completes the fixed ten-stage production registry and public
`publication run/resume` path. Stage 40 uses only the existing HTML renderer;
Stage 50 creates explicit DOCX plus complete PNG/JSON render evidence and
retains no PDF; Stage 60 freshly exports the exact accepted DOCX through Word
COM and renders every final PDF page with repository `.tools` Poppler. Stage 70
assembles the exact package with one PDF and mandatory ArtView/config/code/
schema evidence, and Stage 71 runs the copied standard-library verifier through
isolated Python without a release claim.

The implementation review and follow-up schema/runtime parity review are
closed with no remaining P0/P1/P2. Current focused evidence is `56 passed`,
`2` explicit host-conditional skips and `14` subtests; the final schema/control/
registry closure is `40 passed`. The current logon cannot activate installed
Word (`0x80070520`), so a successful live Word export remains future host/session
evidence rather than an inferred pass.

## Neutral publication architecture checkpoint — 2026-09-14

A full-scope reuse audit confirmed that existing Viral and Innsmouth automatic
PDF routes are direct HTML-to-PDF compatibility paths and that no generic
DOCX-to-PDF generator currently exists. The independently reviewed additive
architecture therefore keeps reconstruction separate and defines explicit,
hash-bound user gates from accepted reconstruction through MASTER_EN,
MASTER_RU, ArtView, HTML, DOCX, PDF and a package candidate.

The sole retained PDF lineage is exact accepted DOCX -> fresh Stage 60 Word COM
export -> final PDF. A critic rejected the first draft because Stage 50 could
retain a pre-acceptance preview PDF. The superseding correction restricts Stage
50 to DOCX, PNG and JSON/manifest evidence; any technical PDF bridge is private,
transient, uninventoried and must be absent before success. Independent closure
found no remaining P0/P1/P2 architecture issue and authorized synthetic Packet
A only.

## No-CUDA environment checkpoint — 2026-09-14

The current host has no detected NVIDIA device or working `nvidia-smi`.
Repository-local setup now probes this capability before creating a venv or
invoking pip. `setup.ps1` and `verify.ps1` return explicit `SKIPPED` with exit
code `0`; the CUDA packages from the interrupted attempt were uninstalled and
the two large pip unpack payloads were removed.

The real Dissociation preflight returned `state: skipped`. Run
`20260914-no-cuda-skip-01` then created only identity-bound `run.json` and
sealed `skip.json`, with all six stages explicitly skipped and no outputs,
review queue, candidate, or acceptance claim. Resume is rejected and a future
capability change requires a fresh run root. Focused verification and the
independent critic both pass `88` tests; the critic reports no P0/P1/P2 finding
for this bounded skip control. This is environment evidence, not Step 4
completion.

This whole-run skip policy is superseded by the user decision recorded on
2026-09-14. MinerU 3.4.4 supports pure-CPU `pipeline`; the correct capability
boundary skips only GPU-backed enrichment. The sealed run remains immutable
evidence of the old behavior and is not a template for the next run.

## Architecture review checkpoint — 2026-09-14

Read-only PDF reconnaissance is complete for all six pages. The proposed
control-plane shape was independently reviewed. The critic accepted the fixed
graph, run-local identity/resume model, arbitrary uniform MediaBox policy, typed
review queue, and strict reconstruction/publication separation, but rejected
live Dissociation execution on `ScenarioContract.v1`: that schema hard-codes
`viral_print` and the obsolete `accepted_html -> pdf` authority. The blocking
P1 remediation is a narrow versioned reconstruction-only contract/schema.

The implementation packet must also prove that the legacy 124-page Viral role
fallback is unreachable from contract-driven runs and that every downstream
target is rejected before any filesystem write. Live MinerU remains closed
until implementation review passes and the Dissociation reconstruction
contract is validated.

## Wave 0 implementation checkpoint — 2026-09-14

The scenario-neutral control plane now exists as `python -m kb_creator` with a
fixed reconstruction-only graph, separate neutral contract/RunSpec/stage/
review/decision schemas, identity-safe resume, contract-driven page roles, and
full-MediaBox raster preparation for arbitrary uniform source geometry. The
runner records decision files in the fidelity/materialization cache identity,
revalidates source/contract/implementation/tool/local bindings before each
stage, rejects every downstream/publication target before writes, and
quarantines partial stage output.

Focused verification passes `83` tests, including synthetic run -> review ->
closed decisions -> fidelity audit -> materialization and negative cases for
stale data, tool drift, path escape, partial failure, non-Letter CropBox,
rotation and legacy Viral-role isolation. This is implementation evidence, not
independent acceptance. Step 3R remains the active gate.

The first Step 3R implementation review rejected live execution because the
production fidelity adapter passed `merge_packets/pages` where the auditor
requires the `merge_packets` root containing `merge_index.json`. That P1 is
patched and covered by a real production-adapter argv regression. The same
follow-up closes the critic's queue-routing P2 by deriving typed issue kinds
from contract strategies/traits, MediaBox-versus-CropBox evidence, and merge
comparison signals. Independent closure verification remains pending.

The closure review passed all `83` focused tests independently and found no
remaining P0/P1/P2 blocker. The validated Dissociation contract is
`contracts/dissociation.reconstruction.json`, canonical SHA-256
`99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E`.
Its read-only source preflight passed without creating a run root.

Per the user's environment policy, all installed tools and mutable runtime
state must live under `NRI/.tools`. MinerU setup/initialize/verify/run scripts
therefore separate the tracked `MinerU/` sources/models from the installed
`.tools/MinerU/.venv` and `.tools/MinerU/.runtime` trees.

## Reconstruction candidate and replay checkpoint — 2026-09-15

The three-view CPU extraction is frozen in immutable run
`20260915-cpu-first-07`. Downstream audit changes no longer require another
MinerU pass: the independently reviewed full-prefix replay path validates the
sealed source run, all nineteen Stage 01-04 producer-closure files, thirty-three
JSON artifact shapes, thirteen typed wrappers and seventy-one payload scans.
It then creates a fresh run with typed rebased authorities and explicit origin
provenance; decisions, acceptance and Stages 05-06 are never replayed.

Fresh run `20260915-cpu-replay-08` passed its dedicated Stage 05 audit v3 with
zero errors and completeness `1.0` on all six pages. Stage 06 materialized
`RECONSTRUCTED_EN.md` at SHA-256
`1FCC84CA50E24D57CFD5BFA906350EF24BC81BB93A7CC5C115415765DC71D28B`.
Independent content/fidelity QA reports no P0/P1 finding and authorizes only
presentation to the user. The active gate is explicit user reconstruction
acceptance. MASTER_EN promotion, Russian translation and publication Stages
10-71 remain closed.

## Accepted reconstruction and Stage 10 checkpoint — 2026-09-15

The user's page-6 statblock correction was applied through fresh replay run
`20260915-cpu-replay-09` without rerunning MinerU/CPU. The corrected
reconstruction was independently verified and explicitly accepted; its
acceptance receipt SHA-256 is
`10F058EE1D6FE1691E59EEB4B02354AC6862417FE193A5BA7991C03450223D22`.

The neutral publication contract is
`kb_creator/contracts/dissociation.publication.json` at SHA-256
`7F1B02F3C18B6C4FE998D121328ACCDB5A449D12C850368732BA2ACAA6EE0367`.
Stage 10 run `20260915-publication-01` stopped at the intended
`awaiting_master_en_acceptance` gate. Its `MASTER_EN.md` is 20,863 bytes with
SHA-256 `2AD1E9175A3B53B7C85CCA5824B2FAA60D4A82C38928F487E6BB7700B5617CA6`.
Independent candidate QA found no P0/P1/P2: it is an exact LF-normalized
projection of the accepted reconstruction, including the compact statblock,
six page markers, twenty-one headings and two exact assets. No Stage 20+ output
or MASTER_EN acceptance exists. The active gate is explicit user acceptance of
this MASTER_EN candidate.

## Stage 20/21 pre-execution audit checkpoint — 2026-09-15

Read-only projection of the verified English candidate found 87 ordered
translation units in eight batches, zero long-unit splits, two exact assets,
and 45 applicable terminology checks. It also found three scenario-neutral P1
gaps before any translation was generated: no production submission author,
the current structure signature permits removal of all ten accepted statblock
hard breaks, and the contract-required independent translation QA is neither
produced nor enforced at MASTER_RU acceptance.

Run `20260915-publication-01` remains immutable historical Stage 10 evidence.
Its implementation identity cannot be resumed after the required generic
remediation. The active implementation packet adds a safe submission author,
line-topology preservation and a separate standard-library verifier. After
independent closure, create a fresh publication run, reproduce the same Stage
10 candidate, independently verify it and return to explicit MASTER_EN user
acceptance before Stage 20.

## Fresh Stage 10 after MASTER_RU pipeline closure — 2026-09-15

The generic Stage 20/21 remediation is independently closed with no P0/P1:
atomic submission authoring, hard-break-aware Markdown topology, a separate
standard-library MASTER_RU verifier, Stage 21 quarantine/evidence and exact
dual-evidence acceptance enforcement all passed the bounded regression matrix.

Fresh publication run `20260915-publication-02` reproduced only Stage 10 and
stopped at `awaiting_master_en_acceptance`. Its run identity is
`5CF1DC43273E4B5472AD6DA4D255A8E13B3070FA326976209B3E0D1DDD0224C3`.
The candidate remains byte-identical to run01: 20,863 bytes, SHA-256
`2AD1E9175A3B53B7C85CCA5824B2FAA60D4A82C38928F487E6BB7700B5617CA6`.
Independent run02 QA found no P0/P1/P2, confirmed eleven statblock rows with
ten hard breaks and no internal blank paragraphs, and found no Stage 20+ output
or MASTER_EN acceptance. Run02 is the current candidate authority; explicit
user MASTER_EN acceptance is the active gate.

## Compact boundary correction and Stage 20 execution — 2026-09-15

The remaining separator after the final statblock heading is now handled by a
generic `block_boundaries: compact` decision transform. The transform is exact
and fail-closed, changes no literal text, and retains all ten hard breaks.
Fresh replay run `20260915-cpu-replay-10` reused the sealed Stage 01-04 prefix
without invoking MinerU/CPU. Independent QA found no P0/P1/P2. The corrected
21,046-byte reconstruction has SHA-256
`53B560862C3CC344C5C78676D988C3A4A479B5C0A0CBE4261B2E93080ED19993`
and acceptance receipt
`E660EA6BBF24BAE683715F9C433C68134DC946D6BF9CFD1EF40B867DE0FBEE0B`.

Publication run `20260915-publication-07` remains the accepted-ArtView and
failed-HTML authority. Its Stage 10 and Stage 21 reproduce the exact accepted
content: `MASTER_EN.md` is 20,862 bytes, SHA-256
`571F96B077ACA59072C0399433E8372E997C9FC5D07428698D5580A2D5A1BED5`, and
`MASTER_RU.md` is 36,367 bytes, SHA-256
`A4BA09330C84490F4CB6018919A4BB25699770AF594CDC659749B1E9C3BC7BFE`.
The user explicitly accepted both ArtView rows in run07. The 1,715-byte
decision JSON has SHA-256
`2794971557014E2116AB5D9404E63B06F9F85341AE311C60B6579B6708F86151`,
strict validation passes `2/2`, and the ArtView acceptance receipt SHA-256 is
`0A384DCCC5282E0341DF99C0D9EED4E18E27A55E7AA0003942FB5CE818E964E2`.
Run07 Stage 40 exposed the escaping-asset defect and failed closed. The generic
stage-local asset fix is independently reviewed. Runs08-10 were created outside
the assigned review-only task and are historical evidence only; run10 also
binds an older `scenario_artview.py` identity and is not resumable. The generic
decision-rebind helper is independently reviewed GO with no P0/P1/P2; critic
receipt SHA-256 is
`7694366778CE20624188167023EA9B28CAFA0D551AF605EEB3AA06605C908650`.
Fresh implementation-bound publication run `20260915-publication-11` is now
the current authority. It reproduced the exact accepted MASTER_EN and MASTER_RU
hashes, strictly rebound the user-accepted run07 ArtView choices to the exact
equivalent candidate graph, passed 2/2 decision validation and applied Stage
31. Stage 40 generated `Dissociation_RU.html` at 62,793 bytes, SHA-256
`1B243CBA730C64267305A7974E032C39DBD38AD4A2E89B699BC8DA6E203455DE`.
Automated HTML QA passes with 21 headings, 6 source pages, 2 stage-local image
references, 0 missing references and no direct PDF route. The current gate is
blocked by full-page visual QA: the final stat block renders its title twice and
retains excessive line spacing. A generic renderer/config remediation with
regression coverage is active; HTML acceptance has not been requested or
inferred.

## Current HTML authority after stat-block remediation — 2026-09-15

Run11 is immutable historical defect evidence. The scenario-neutral renderer
remediation detects only terminal numeric, densely hard-broken stat blocks,
binds the exact heading ID through the derived HTML config, preserves Markdown
hard breaks as `<br>`, and applies compact stat-block spacing. Independent
critic review is GO with no P0/P1/P2; receipt SHA-256 is
`69DAED4801B48C00AE619CECAA1233B03D987D4E0D59E948665E2E890C6DAA7A`.

Fresh publication run `20260915-publication-12` is the current authority, with
portable identity SHA-256
`A1BCCE994201F479057F97195894CD7E9455D5C1BD22507EE1E622679DFA00DA`.
It reproduced the exact accepted MASTER_EN and MASTER_RU artifacts, strictly
rebound the accepted ArtView decisions after complete equivalence, passed
decision validation `2/2`, and recorded ArtView acceptance receipt SHA-256
`052D8E3D518C4A2933C538C5DE2407C6F782331EB779B16E3E2CFAAF26208F90`.
Stage 40 generated the 62,801-byte `Dissociation_RU.html`, SHA-256
`4AED240DBA16BC99E5EFEFCEF6759DA0944CB340FEBFE8D747F456012E74299A`.
Automated QA passes with 21 headings, 6 source pages, 2 local image references,
0 missing references, 1 stat-block card, 0 findings and no direct PDF route.
Read-only browser QA confirmed one visible final stat-block title, one card,
10 `<br>` hard breaks, loaded natural image dimensions and no horizontal
overflow; its receipt SHA-256 is
`BED226343A9B6655D611224D85EAEB99E07BD4743F3095DD0048843EBD490F14`.
The current gate is explicit user acceptance or correction of this HTML
candidate; DOCX remains closed.

## Current HTML authority after page-boundary and numeral remediation — 2026-09-16

Run12 is immutable historical defect evidence: user review found two page-edge
paragraph splits inherited from MASTER_EN and Georgia old-style numerals. The
generic MASTER_EN v3 builder now joins only proved adjacent-page prose before
translation-unit derivation, records both transitions in provenance, and the
independent verifier recomputes them. The HTML renderer now applies
`font-variant-numeric: lining-nums` globally. Focused verification passes the
v3 builder and HTML suites; independent implementation criticism is GO with no
P0/P1.

The reusable `scenario_master_ru rebind-batches` command validates separate
old/new run authorities, carries exact source units, supports only those same
two proved page-boundary transforms, writes current-packet batches and a sealed
report, and fails closed for any other content edit. Its focused suite passes
`19 passed, 1 skipped, 23 subtests passed`.

Fresh publication run `20260916-publication-14` is the current authority,
portable identity SHA-256
`D201B1F1DD026385BF544774E68DDD95714B97F217E5AC414BC585BB69CA4760`.
Its accepted `MASTER_EN.md` is 20,858 bytes, SHA-256
`2EB528C44A2B1A20C00D167AD255BA0C767B74653564A9FE9182D6A3FC51CABE`,
with exactly two page-boundary transitions. The hash-bound translation rebind
carried 82 exact units and joined one dehyphenated word plus one continued
prose unit; its sealed report SHA-256 is
`727F3ED27BCD742BF39DFF7721A60A411349020A5969A4ED3813F6F770E6E744`.
The accepted `MASTER_RU.md` is 36,363 bytes, SHA-256
`E6975753BB3E8714269D9DDC01F97E6CE7F8EFA5810773949094BA03AAA5F9EA`,
with producer and independent QA both passing.

The previously accepted two-row ArtView decision set was strictly rebound to
the equivalent run14 graph; target decision SHA-256 is
`318F0FCD69458B732E3FD4578F0F8CBF6D421EC73EE2439C75D6DB67876E318B`.
Stage 40 generated the current 62,820-byte `Dissociation_RU.html`, SHA-256
`1E0AF3ECD764DF5E1231F5E1228332C4B587F56A221C8580682D932F2B7790F7`.
Automated QA passes with 21 headings, 6 source pages, 2 local images, 1 stat
block and zero findings. Both corrected Russian sentences are each contained
in one HTML paragraph, and the emitted CSS contains `lining-nums`. The active
gate is user visual acceptance or correction of run14 HTML; DOCX remains
closed.

## Final publication candidate — 2026-09-16

The HTML corrections, hierarchical unnumbered TOC, larger TOC type, local
LibreOffice DOCX/PDF fallback and footer-free DOCX policy are now represented
in reusable implementation/configuration. Run23 proved the final nine-page
layout. Its first package attempt correctly failed because Stage 70 flattened
the accepted ArtView decision JSON to a different path than the immutable
acceptance evidence.

The generic Stage 70 remediation preserves the safe run-relative ArtView
decision path and rejects escape paths. Engineering verification passed 5
focused tests and all 34 publication control-plane tests. Because the adapter
identity changed, run23 was not resumed. Fresh publication-only run
`20260916-publication-24` reused the accepted reconstruction without MinerU or
OCR and reproduced the accepted MASTER_EN, MASTER_RU and HTML bytes.

Run24 completed DOCX, PDF, production package and offline verification. The
DOCX contains no footer parts, `PAGE` fields or footer references. DOCX and PDF
each render to nine pages matching the reviewed run23 page images. Production
manifest SHA-256 is
`170F8FC12CE63AC3AEFE64FE95DBF33A8F137216D9E4873E465644A8C1F94128`;
the copied verifier and the repository verifier both report
`candidate_for_release_review`, `release_state: not_reviewed`, exactly one
PDF. Independent gpt-5.5 release review is GO with no P0/P1. Receipt SHA-256
is `49AF4873A530ECDA5585ED78DDA31EFB995CEED1E36F8019AF17A5A9E8A49108`.

## Unified-terminology successor candidate — 2026-09-16

Run24 remains historical release evidence. Consolidating all Call of Cthulhu
terminology into the single system authority changed MASTER_RU and therefore
invalidated that release decision for successor bytes.

Fresh publication-only run `20260916-publication-29`, portable identity
`DEB6A06C12BB987C5B825DAD55E849D7726000F595398474E3C08FAFE13B0E2A`,
reused the accepted reconstruction without MinerU/OCR. It binds only
`CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv` at `16003`
bytes / SHA-256
`EE84E121E63ECDA3F2165205E8335FD3C68E70CF1DEFE1D00CE6C3FF97EFF3AE`.
MASTER_EN remains byte-identical. MASTER_RU, HTML, DOCX and PDF hashes are
respectively `25537977DC1CAB80B9DDC04E603F95BB601F3C1EB29BAAFB6FFAD161A5F02E84`,
`09D3E0618F9922255AE12A916D283FB9B2F900E8FE877C1072A52A44D8016B97`,
`D40140D8AD7C347B137042072826B16786F54AF5CECDE778748A8A6B8383A9CA`
and `983AECFEE9395BAB44396E7EF600E98D930D2D07F7DB5A86FC9F0F835126CEAA`.
The final PDF has nine pages and comes only from the exact accepted DOCX; the
DOCX has no footer/page-number structures. Offline verification reports
`candidate_for_release_review` and `release_state: not_reviewed`. Fresh
independent release review is the only remaining publication gate.

## Reviewed-DOCX successor bundle — 2026-09-16

The user edited the DOCX link previously exposed from run29 Stage 50, removing
one unintended empty paragraph before the next laboratory paragraph. Exposing
that internal candidate instead of the package copy was an orchestration error;
the two files were initially byte-identical but should not both have been
presented as user-facing outputs.

The reusable remediation is `publication revise-docx`. It never rewrites the
completed production package: it embeds that verified package as immutable
provenance and emits a top-level reviewed DOCX, a fresh DOCX-only PDF, render
evidence, a sealed revision manifest and an offline verifier. The final
successor is `outputs/73-reviewed-docx-package`. DOCX SHA-256 is
`2AC1ACEFEF697B864B9D6DD33802083B72CCD2A4381430DE1C145008C5A7159A`;
PDF SHA-256 is
`89F2870D8FC76AF598A0F49A45C97D466B81C0E94F1BC5A0873A4478E290BAF6`.
All eight page PNGs were inspected at original resolution and pass. The final
revision seal is
`E32A4B537FD0640AA6CF3496BB01C5347A28C76E346DB514B8DD94AF7227C813`.
State remains `candidate_for_release_review`; fresh independent release review
is pending for these successor bytes.
