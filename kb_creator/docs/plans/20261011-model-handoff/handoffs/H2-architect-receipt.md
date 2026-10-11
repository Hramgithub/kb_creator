# H2 architecture and dependency receipt

- Goal: `20261011-model-handoff`; step: `H2`.
- Role: architecture/dependency analyst; requested model/effort: `gpt-6-astra` / `high` (assigned profile). Independently verified runtime model/effort: unavailable.
- Orchestrator policy owner: main chat, `gpt-6-sol` / `medium`; ownership does not transfer.
- Assignment state: `platform-unverified`; scoped override: none.
- Scope: read-only architecture, contracts, continuation boundaries and standalone dependency inventory. Sole write: this immutable receipt. No release decision.
- Result: completed, with an experimentally confirmed standalone runtime gap and explicit document-state contradictions for H3 integration.
- Timestamp: `2026-10-11T18:06:00Z` (receipt drafting time, UTC; approximate to the minute).
- Elapsed: approximately 5 minutes; exact measurement unavailable. Token use: unavailable.

## Executive finding

KB Creator is a file-based, resumable source reconstruction, English-to-Russian translation/proofreading and editable Word production pipeline. Its durable API is sealed JSON plus immutable input/output trees, not a web service or autonomous translation daemon. Content work is issued to an external agent as tasks/submissions; Python and PowerShell perform mechanical stages and enforce lineage. Current ordinary production is `five_step_docx_v3`, DOCX only. The imported repository is a source/evidence snapshot, not a proven standalone executable distribution.

The latest correction goal is recorded completed on 5 October; those are historical NRI execution/review results. Six reviewed originals are present under `deliverables/latest`. The three corrected successors linked by that index are under excluded `working/`, which is absent here. Do not present their links as available deliverables, the old process history as a running job, or prior technical approval as user book acceptance.

## Control planes and branching

Paths below are relative to `C:/_Hobby/_work/kb_creator`, unless marked external.

| Control plane | Entry/modules | Contract and continuation boundary |
| --- | --- | --- |
| Ordinary PDF-to-DOCX | `kb_creator/__main__.py` `translate`; `pipeline/five_step.py`, `five_step_intake.py`, `five_step_language.py`, `five_step_docx.py` | Run/state v3, five semantic steps. Start requires produced source-graphics inventory and closed all-page review. Resume consumes explicit submissions; it can execute consecutive mechanical phases until the next content task. It never calls an LLM service itself. |
| Reconstruction | CLI `preflight`, `run`, `resume`; `pipeline/reconstruction.py`, `mineru_cpu_first.py` | Six stages: prepare inputs, MinerU views, compare views, visual merge bundle, fidelity audit, candidate materialization. Legacy run v1 and CPU-first v2/v3/v4 coexist; inspect the actual schema/profile, never infer behavior from the filename. |
| Replay/recovery/promotion | CLI `replay verify-source/run/resume`, `reconstruction-promotion`; `reconstruction_replay*.py`, `reconstruction_promotion.py`, `mineru_view_recovery*.py` | Reuse requires matching source, frozen implementation/input identities and explicit reconstruction decisions; promotion/materialization is distinct from acceptance. Presence of a saved artifact alone does not authorize continuing old processes. |
| Language/reader continuation | `scripts/continue_language.py`, `continue_review_source.py`, `continue_source_choices.py`, `continue_docx.py`; corresponding pipeline modules | Preserve verified upstream work, issue fresh output roots and rebind reviewed choices only where their source/context identities still match. Prefer this branch to restarting OCR when valid upstream data exist. |
| Preserved reviewed-DOCX repair | `scripts/revise_reviewed_docx.py`, `pipeline/reviewed_docx_revision.py`; `docs/reviewed-docx-revision.md` | `kb_creator.reviewed_docx_revision.v1`, provenance `reviewed_artifact_successor`. Hash-bound original DOCX/PDF, exact comment/paragraph or approved field anchors, source-image occurrences, finite operations. New root contains only `document.docx`; QA report is outside it. `validated_candidate`, `accepted: false`, no claim to replay lost masters. |
| Archived publication | `pipeline/publication.py`, `publication_adapters.py`, old revision helpers | Ten historical stages including ArtView, HTML, DOCX, PDF and offline package verification. Public writers/acceptance commands are retired before writes; read-only historical verification remains. Do not give old README examples as supported generation commands. |

ArtView is not mandatory in the five-step profile. In-memory HTML/DOM is still an internal transport into the Word builder; this does not mean a published HTML artifact is generated. `translator` remains an actual implementation dependency of this KB Creator snapshot even though it is not canonical governance or a Sourcefold compatibility contract.

## State and lineage contracts

The ordinary v3 progression is:

`source PDF + closed source-graphics review -> intake task -> reconstruction/review -> MASTER_EN -> documentary draft task -> proofread task -> MASTER_RU + projection -> reader_options + fidelity plan -> DOCX -> full text review -> all-page visual review -> ready_for_docx_review`.

`five_step.py:15-20,97-178,363-520` separate phase from state: `running`, `needs_agent_work`, `failed`, and final `ready_for_docx_review`. `_load` revalidates source/glossary/options/review identities, all evidence files, and step implementation inventories. New attempts get numbered directories. Legacy v1/v2 status is read-only and reports completeness as not assessed; it does not inherit v3 guarantees.

The DOCX package has another state layer: `built_pending_render` or `needs_visual_review`; `release_state` stays `not_reviewed`. `reader_fidelity.py:545-605` separately records mechanical closure with semantic state `needs_output_review`. None of these is user acceptance. Mechanical verification, all-page inspection, technical release review and user book acceptance must stay distinct in the handoff.

Important contracts and why they matter:

- `pipeline/identity.py` defines canonical JSON as UTF-8, sorted keys, compact separators, `ensure_ascii=False`; SHA-256 is uppercase. `manifests.py` signs/verifies the document excluding its digest field. Do not hand-edit/reseal a frozen receipt to bypass changed input/code checks.
- `contracts/run_spec.v1-v4.schema.json`, `stage_manifest.v1-v2.schema.json`, reconstruction identity/decision/upstream schemas bind the OCR views, reviewed decisions and downstream replay evidence.
- `contracts/source_graphics_inventory.v1.schema.json`, `source_graphics_review.v1.schema.json` bind the exact PDF, physical page, rendered PNG, reviewer and disposition of graphics. `source_graphics.build_inventory` deliberately marks machine discovery incomplete; an empty machine list cannot prove no art exists.
- `contracts/reader_fidelity_plan.v2.schema.json` binds inventory/review/PDF/MASTER_RU/projection/config/canonical CSV/book overlay. Closed domains identify book, section, entity, field and physical source page. Whole numeric operands and visible field labels must match; only accepted registry rows or explicit book-overlay rows authorize terminology changes. Unsupported primary/editorial authority remains `needs_decision` rather than silently passing.
- `DOCX_MANIFEST.json` and `READER_FIDELITY_VERIFICATION.json` bind actual DOCX bytes, retained image occurrences/order, reader projection, text/graphics observations, config, inventory and service render evidence. Identical image hashes do not merge distinct occurrences.
- Source masters and preserved user DOCX remain immutable. Reader adaptations belong to reviewed projection/operation data; a successor preserves originals, native comments/replies and all undeclared OOXML/media content.

## Technology/dependency map

| Dependency | Observed use | Standalone status |
| --- | --- | --- |
| Python and standard library | CLI, sealed JSON, deterministic hashes, subprocesses, ZIP/OOXML inspection, successor staging | No root `pyproject.toml` or `kb_creator/requirements.txt`; no Python found on PATH and `py -0p` found none. Bundled Codex Python 3.12.14 was usable for read-only checks. This is host evidence, not a declared supported version range. |
| `pypdf`, Pillow (`PIL`) | PDF page geometry/resources/image extraction; image identity/dimensions/render checks | Available in the tested bundled interpreter; no installation/version lock supplied by extraction. |
| `python-docx`, `lxml` | Editable Word creation, XML/HTML transport, exact OOXML validation, native comments and source field preservation | Available in tested interpreter. `scripts/production_docx.py:18-29` shows imports. |
| `translator.translator` | `markdown_to_review_html`, `unique_slug`, reader projection/duplicate analysis | Required by top-level imports in `five_step_docx.py:28`, `reader_projection.py:18`, `reader_duplicate_text.py:10`; top-level `translator/` is absent. Fresh import fails with `ModuleNotFoundError: No module named 'translator'`. |
| MinerU + model/provider installations | PDF extraction/OCR and independent view comparison | External runtime/source roots, provider receipts and PowerShell runner are required. CPU-first profile has mandatory CPU pipeline views; CUDA hybrid/VLM views are optional only under explicit supported availability reasons. No remote-host fallback is implied. |
| Poppler `pdftoppm` | Independent physical source-page rendering and service PNG generation | External executable with identity-bound rendering evidence; `.tools/` is absent in extraction. |
| PowerShell, Word COM / local LibreOffice export | DOCX layout rendering through a private PDF bridge, removed after PNG generation | External host/runtime capability. DOCX-only policy does not forbid service rendering; it forbids publishing a new HTML/PDF deliverable. A missing renderer cannot become a visual pass. |
| Shared CoC CSV + explicit book overlay | Canonical accepted terminology, conflict detection, edition/term authority | `pipeline/coc_glossary.py:15` defaults to absent top-level `CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv`; `--shared-registry` is an explicit supported binding. Do not fabricate authority from historical row counts. |
| Git LFS | Large DOCX/PDF/image artifact transport | Attributes/payloads belong to H1's inventory. An LFS pointer is not a usable book or source. H2 did not repeat LFS integrity checks. |
| pytest / existing tests | Regression and adversarial contract coverage | 228 files are present directly in `kb_creator/tests` (file count, not test count). pytest is absent from tested bundled interpreter; tests were not run by H2. |
| NRI governance/layout rules | Role ownership, immutable receipts, source/layout fidelity and review boundaries | Top-level `docs/governance/nri_goal_governance.md` and `NRI_OCR_LAYOUT_RULES.md` are absent here. NRI governance was read externally at the assigned workspace path; the handoff must identify this external policy boundary. |

## Repository map and current authority

- `kb_creator/__main__.py`: CLI; invoke from repository root, the parent of `kb_creator/`.
- `pipeline/`: reusable state machines, contract validators, replay, language and reader projections. `scripts/`: thin commands plus historical scenario-specific adapters; do not assume every old script is a supported current route.
- `contracts/`: versioned JSON schemas and scenario contracts. `reference/`: reusable reader defaults and preserved scenario reference config. Neither is a substitute for reviewed source-specific decisions.
- `inputs/`: preserved source/production material; currently four top-level scenario directories (Dissociation, Innsmouth, Number 7 Dream, Viral). `pdf_raw/`, `output/`, `reports/`: historical raw/output/checkpoint evidence, not automatically the newest authority.
- `deliverables/latest/`: six preserved reviewed DOCX and assets; exact identities in `MANIFEST.json`. This index is the useful reader entry point but its successor links are missing here.
- `docs/plans/20261004-user-docx-review/{plan,context}.md`: the 5 October completion checkpoint supersedes its own older active/rejected checkpoints. The first current sections of `PROJECT_STATUS.md` take priority over the long appended history.
- `docs/plans/20261011-model-handoff/`: current goal, owned by the orchestrator. `working/` is intentionally absent. `docs/debt.md` exists but does not replace debt/queues embedded in the historical goal packets.

## Contradictions and remediation specification for H3

| Finding | Required handoff treatment | Acceptance criterion |
| --- | --- | --- |
| README current section says candidates still undergoing checks; correction plan/context say completed 5 October | State the latest goal checkpoint and clearly label older prose as stale | No suggestion that the old correction task or old process PID is currently active |
| Latest index describes three corrected successors, but every link targets excluded `working/` | Distinguish six available reviewed originals from historically produced, presently unavailable successors | All three missing paths explicitly labelled absent; no replacement with older originals under corrected labels |
| Latest manifest book states still contain `correction_goal_active` | Treat manifest as byte inventory, not current orchestration authority | Completion/state claims cite latest goal checkpoint; manifest states identified as stale metadata |
| Old HTML/ArtView/PDF commands and historical v1 docstrings remain in code/docs | Classify supported DOCX v3, archived verification and retired writers separately | Examples do not direct a new model to invoke retired generators or mutate legacy run state |
| Extraction is called standalone but lacks `translator`, registry, runtimes, governance and working state | Explain source snapshot versus executable closure; record concrete failing import | No claim of successful standalone build, replay or broad regression suite |
| Historical 239 tests/14 subtests, focused 48, 38 critic cases and 367-page review are recorded | Attribute them to frozen historical NRI execution, with no fresh-run or imported-asset coverage claim | Preserve approval scope and separate current snapshot verification from inherited evidence |
| Final v3 state is generic DOCX but fidelity contract names target edition 7e | Document this actual CoC-oriented contract (`nonapplicable_reviewed` exists) | Do not promise automatic generic rule-system conversion or whole-system 7e redesign |

Recommended next safe action: H3 drafts the two handoff documents using these boundaries, then H4 checks their paths, commands and current-vs-historical claims. No book build or recovery process should start as part of this handoff goal. A later execution-readiness task should select a supported route and explicitly provide the frozen renderer dependency, canonical registry/overlay, runtime capabilities and complete source set; then perform imports, CLI checks and the route's existing tests in a fresh output root. Do not solve these gaps by copying arbitrary old artifacts or changing accepted hashes.

Future readiness acceptance should require: the selected route imports under a documented interpreter without accidental NRI `PYTHONPATH`; all external dependency bytes/versions and source authorities are identified; missing inputs fail before output creation; meaningful source-art/edition/term guards and retired-writer tests pass; an actual build preserves source/DOCX originals and produces no published HTML/PDF; text and every rendered page receive exact-artifact review. Any release decision remains with an independent critic, outside H2.

## Evidence, files checked and limitations

Read the assigned handoff plan/context, external NRI governance, current README/status, correction plan/context, latest README/manifest, five-step and reviewed-DOCX usage docs; inspected the CLI, control planes and modules/contracts named above, import statements, stage registries, tests directory and input/reference roots. Targeted source excerpts were used rather than rereading the full historical log. No release file was edited or treated as a fresh H2 approval.

Live read-only verification: repository-root `python -B -m kb_creator --help` succeeded under discovered bundled Python. Module checks found pypdf/PIL/docx/lxml present, pytest/translator absent; importing `kb_creator.pipeline.five_step_docx` failed at its translator import. Explicit `Test-Path` checks confirmed absence of translator, default shared CSV, top-level governance/layout rules, `.tools`, `working`, pyproject and requirements file. No dependency installation, build, OCR, rendering, test run, Git mutation, commit or push occurred. A PATH `git status` call returned `must be run in a work tree`; H1 owns Git identity/cleanliness verification, so no Git conclusions are drawn from that failed check.

Blockers: none to documenting the handoff. Standalone execution is blocked at least by the confirmed renderer import and omitted authorities/runtimes; exact replay/returning the three corrected files is blocked by missing working data. Full dependency transitive closure and runtime capabilities were not audited. Sole changed file: this receipt. Memory was consulted only for prior project conventions (live-state precedence and reusable fixes); architecture/current facts above were checked against the assigned snapshot.
