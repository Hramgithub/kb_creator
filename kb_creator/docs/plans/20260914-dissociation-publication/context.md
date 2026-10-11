# Dissociation full publication context

Goal id: `20260914-dissociation-publication`

State: `active`

## Objective

Create a complete, reproducible KB Creator publication package for
`Dissociation` while making required pipeline changes reusable and
scenario-neutral. The publication chain is `MASTER_RU + accepted ArtView and
configs -> HTML -> DOCX -> PDF`.

## Accepted intake

- title/id: `Dissociation` / `dissociation`;
- immutable external source:
  `C:\_Hobby\Yandex.Disk\НРИ\1_Зов Ктулху\temp\маленькие иголочки страха\Dissociation.PDF`;
- source byte count: `2159317`;
- source SHA-256:
  `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B`;
- source language: English;
- publication languages: English and Russian;
- requested outputs: `RECONSTRUCTED_EN`, `MASTER_EN`, `MASTER_RU`, ArtView and
  effective configs, HTML, DOCX, PDF, and a stable production package;
- old translation: none;
- terminology authority: the single shared Call of Cthulhu 7e system registry,
  `CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv`; current
  contract identity is `16003` bytes, SHA-256
  `EE84E121E63ECDA3F2165205E8335FD3C68E70CF1DEFE1D00CE6C3FF97EFF3AE`;
- user implementation constraint: minimize manual work and implement
  repeatable behavior as universal pipeline additions, not scenario-specific
  scripts.

## Accepted constraints

- Source inputs are immutable.
- No prior scenario topology, counts, or decisions are authority.
- The reconstruction skill owns only source reconstruction; publication and
  acceptance remain separate stages.
- Generic package/config/schema changes are preferred over bespoke scripts.
- PDF must be generated only from DOCX, which must be generated after HTML.
  Direct HTML-to-PDF generation is outside the accepted pipeline.
- HTML may be generated only after both `MASTER_RU` and ArtView decisions are
  accepted. ArtView, its accepted decision manifest, and all effective configs
  must be sealed into the production package.
- The exact shared CoC terminology authority used by MASTER_RU must be
  identity-bound and retained in the production package; a transient Stage 20
  copy is not sufficient evidence for offline reproduction.
- User acceptance and the independent release gate are not inferred.
- The unrelated local `.codex/config.toml` modification remains untouched.
- User-scoped role override: engineering implementation for this goal is
  assigned to `gpt-5.6-sol` at `high` instead of the default Terra/medium.
  Bounded engineering work is currently dispatched with that requested role;
  actual platform model identity remains unavailable, so the assignment stays
  `user-overridden-platform-unverified`.
- User environment constraint: install every tool/runtime under the repository
  `.tools/` tree; do not create tool environments under product/source folders.
- Accepted MinerU execution policy: keep MinerU as the reconstruction engine;
  run CPU `pipeline --method txt` and `pipeline --method ocr` locally, with a
  raster-input OCR pass as the third independent view. GPU-backed local
  `hybrid`/`vlm` is optional enrichment. If GPU is absent, only that enrichment
  is `SKIPPED`; the reconstruction continues. Remote execution is forbidden.

## Completed evidence

- Source path exists and was read successfully.
- Source identity recorded from the live file.
- Current branch is `main`, one commit ahead of `origin/main` after the explicit
  user-authorized checkpoint `2e6d0526`; `.codex/config.toml` remains an
  unrelated user modification.
- Current KB Creator README, project status, active/historical goal state,
  recent commits, pipeline automation review, scenario contract architecture,
  reconstruction skill, and NRI goal governance were reread.
- Full six-page read-only reconnaissance is complete. The source uses uniform
  MediaBox `595 x 841`, CropBox `595 x 770`, rotation `0`; page 1 is a visual
  cover and pages 2-6 are two-column scenario body. Page 5 contains a large
  embedded Alaska map/ad asset and page 6 contains a `HUMAN RESISTANCE`
  statblock. Numbered player handouts: `0`.
- The embedded text is viable but plain extraction interleaves columns. The
  source contains stale anthology outline/OpenAction residue and Poppler syntax
  warnings, so three-view comparison and rebuilt navigation are mandatory.
- Generic runner audit confirmed that the five reconstruction CLIs are mostly
  reusable; the missing layer is a contract-driven RunSpec/stage-manifest/
  review-queue/resume control plane.
- Independent architecture/process review rejected use of
  `ScenarioContract.v1` for a live Dissociation run because it hard-codes
  `viral_print` and an obsolete direct HTML-to-PDF authority. A neutral
  reconstruction-only versioned contract is the blocking remediation.

## Historical active-step snapshot (run11)

Fresh implementation-bound publication run `20260915-publication-11` is the
current authority, run identity SHA-256
`520D81F513B2152B7009DB8468E4088BA653142FBF4B800413ACCCDE1CE78AAE`.
It reproduced the exact accepted MASTER_EN and MASTER_RU binaries. Their fresh
acceptance receipt SHA-256 values are
`D859364BBB583413B445D3DF1410F258535A93F7C0D26C2322743DE04101E4CE`
and
`D53564DD4407B7E0057C6C784626E49B9F4E54FEF71CAF57E576015142276577`.

The user-accepted run07 ArtView JSON was strictly rebound only after complete
candidate-graph and selected-binary equivalence. The run11 accepted decisions
are 1,715 bytes, SHA-256
`BA3AB4BC30FDB8EF3C3ED482D922378886997EF716A837B21DBEBA683E3E28D0`;
validation passes 2/2, acceptance receipt SHA-256 is
`0F874129111578DE16F903BDDD24BF43087AE4E5A4DF07F08A1FFDCF6648CE09`,
and Stage 31 applied without modifying either master. Stage 40 generated
`Dissociation_RU.html` at 62,793 bytes, SHA-256
`1B243CBA730C64267305A7974E032C39DBD38AD4A2E89B699BC8DA6E203455DE`.
Automated QA passes with 21 headings, 6 source pages, 2 stage-local image refs,
0 missing refs and no direct PDF route. Full-page visual QA nevertheless found
that the final stat block renders its title twice and retains excessive line
spacing, matching the user's earlier formatting observation. Run11 HTML is not
acceptance-ready. A generic renderer/config fix and regression test are active;
HTML acceptance remains closed.

Runs08-10 remain historical evidence only. Run10 was created outside the
assigned review-only task and binds an older `scenario_artview.py` identity;
it must not be resumed.

## Blockers

- The CPU installation/execution profile, provider-local GPU skip policy,
  RunSpec v2/view pipeline, repository-local child home and retained diagnostics
  are implemented and independently closed. Two failed live attempts remain
  immutable: `-01` found the missing child home; `-02` produced two views but
  required manual descendant cleanup after inherited pipe handles blocked
  completion. The replacement Windows Job Object runner is independently
  closed with `224 passed, 1 skipped` and no P0/P1/P2. Run `-03` proves that
  fix live, but exposes a separate Stage 04 rendered-dimension normalization
  gap after three successful CPU views and comparison.
- The neutral publication-contract author is implemented and independently
  closed after remediation of a P1 Windows ADS output escape and P2
  whitespace-only semantic fields. Closure evidence is `53 passed, 13`
  environment/dependency skips plus direct attack and determinism selections;
  no P0/P1/P2 remains within the authoring scope.
- The shared terminology closure is implemented and independently accepted:
  actual CoC CSV/Markdown authorities parse as `80` merged terms and `85`
  authority bindings, checks are per applicable translation unit, and Stage 70
  retains exact terminology snapshots in package config inventory. Focused and
  expanded evidence is `12 passed` plus `6` subtests and `65 passed`, `2`
  host-conditional skips plus `4` subtests.
- An isolated ignored test dependency directory under
  `.tools/python-test-deps` provides pytest and PyMuPDF to the repository-local
  MinerU Python without installing task dependencies outside `.tools`.
- The bounded takeover completed the generic fixed graph, production adapters,
  synthetic E2E, neutral contract-driven visual roles, arbitrary uniform
  MediaBox handling, strict run/stage/queue/decision identity, decision-bound
  stage cache inputs, tool and local-binding revalidation, path containment,
  and partial-output quarantine. The focused suite currently passes `83`
  tests and `py_compile` is clean.
- Independent implementation review found one production-only P1: the fidelity
  adapter used the page subdirectory instead of the merge-index root. The
  adapter is corrected and has direct argv regression coverage. Review queue
  categories now also derive generically from contract, geometry, and
  comparison signals. The closure review independently passed all `83` focused
  tests and found no remaining P0/P1/P2 blocker.
- `contracts/dissociation.reconstruction.json` is schema-valid and binds the
  exact source identity, six-page topology, page roles, zero handouts, page-5
  OCR/visual risk, and page-6 statblock. Canonical contract SHA-256:
  `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E`.
  Read-only source preflight passed and created no run root.
- MinerU installation/runtime scripts now default to `.tools/MinerU`; a first
  accidental partial install under `MinerU/` was stopped and moved to
  `.tools/quarantine/mineru-setup-20260914-0415`. This host has no detected
  NVIDIA device. The interrupted CUDA `torch`, `torchaudio`, and
  `triton-windows` packages were uninstalled, and both large incomplete pip
  unpack payloads were removed without touching source/model inputs.
- The generic MinerU setup now writes `.tools/MinerU/capability.json` before
  venv/pip work. No-CUDA setup and verification are explicit successful
  `SKIPPED` operations. The reconstruction control plane binds that receipt to
  run identity, emits only sealed skip evidence, records all dependent stage
  skips, creates no candidate/review/output, and forbids resume.
- Real Dissociation run `20260914-no-cuda-skip-01` is the current-host evidence:
  `run.json` plus `skip.json` only, run identity
  `72095696C9C0E304E3F8D8CED9B387C21272203592567ACAEF1D984AB63CF292`.
  Focused verification is `88 passed`; independent review found no P0/P1/P2
  issue. The matching engineering and critic agents were closed after receipts.
- Read-only full-scope publication reuse audit proved that current Viral and
  Innsmouth automatic PDF routes consume HTML directly. Reusable foundations
  are the HTML renderer, DOCX projector, ArtView decision validator and content
  inventory helpers; generic acceptance/control/DOCX-to-PDF/package layers are
  missing.
- The neutral publication architecture and its Stage 50 correction are recorded
  in goal handoffs. Its only retained PDF lineage is accepted DOCX -> fresh
  Stage 60 Word COM export -> final PDF. Stage 50 may retain only DOCX, PNG and
  JSON/manifest evidence; transient bridge cleanup is a success prerequisite.
  Independent architecture closure reports no remaining P0/P1/P2 and permits
  synthetic Packet A, not live publication or acceptance.
- Packet A implementation and remediation are complete. The first critic probe
  found and reproduced an unmanifested Stage 50 PDF escape and an incomplete
  packaged stage chain; both are now fail-closed. The closure review reran the
  adversarial probes and the full suite (`107 passed`) with no remaining P0/P1.
  Public production adapters remain unavailable by design. A non-blocking P2
  tracks schema/runtime strictness parity for package array cardinalities and
  uniqueness before real packaging.
- Packet B implements neutral MASTER_EN v3, MASTER_RU lifecycle and ArtView v3
  while preserving legacy v2 routes. Four independently reproduced P1s were
  remediated: output containment, closed MASTER_RU acceptance, exact asset
  source-graph membership and reachable exact-once ArtView decision binding.
  Closure finds no P0/P1/P2. Current focused evidence is `34 passed` plus `14`
  subtests, MASTER_EN v3 `3 passed`, and accessible ArtView v2 `9 passed`.
- Packet C completes the fixed ten-stage registry, public one-stage run/resume,
  exact accepted-input HTML, explicit DOCX, private transient Stage 50 render,
  accepted-DOCX-only Stage 60 Word export, all-page `.tools` Poppler QA, exact
  Stage 70 package assembly and isolated copied-verifier Stage 71. Independent
  implementation and schema/runtime parity closure report no P0/P1/P2.
  Focused evidence is `56 passed`, `2` host-conditional skips and `14` subtests;
  final schema/control/registry evidence is `40 passed`.
- Word exists at `C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE`,
  but COM activation from this Codex logon fails with `0x80070520`. This is a
  recorded environment limitation, not a successful export. Final Stage 50/60
  must run in an interactive Windows logon where COM activation succeeds.

## Historical next-action log

Run `20260915-cpu-replay-09` is the accepted reconstruction authority. It
replayed only sealed Stages 01-04 from immutable CPU run
`20260915-cpu-first-07`; MinerU/CPU was not rerun. The user's sole correction
replaced paragraph separators inside the final `HUMAN RESISTANCE` statblock
with compact Markdown hard line breaks. Independent QA proved that all literal
text, ordering, pages 1-5, selected blocks and assets are otherwise unchanged.
The corrected `RECONSTRUCTED_EN.md` is 21,048 bytes with SHA-256
`2C8983B83C770AC60AA32993B84228E64983B46010121A9DBA393BD3107C646D`.
Audit v3 reports six pages, zero errors and completeness `1.0` throughout.

The generic reconstruction promotion bridge now dispatches legacy-v1,
direct-v2 and replay-v2 separately. Its replay package validation and
identity-safe post-publish rollback remediation passed independent closure
with `95 passed, 1` host-conditional skip and no P0/P1/P2. The fixed upstream
package validates at inventory seal
`7D6E05DA0E0F4CF71A5A89A2EEFC76C90D70EF001D5837DAEFF28BF59689C964`.
The user's explicit conditional acceptance is recorded at receipt SHA-256
`10F058EE1D6FE1691E59EEB4B02354AC6862417FE193A5BA7991C03450223D22`.

Publication contract `kb_creator/contracts/dissociation.publication.json`
(SHA-256
`7F1B02F3C18B6C4FE998D121328ACCDB5A449D12C850368732BA2ACAA6EE0367`)
binds the accepted reconstruction, all seven final declarative config roles,
the two exact art assets and both shared terminology snapshots. Its read-only
preflight passed before the publication run root was created.

Run `20260915-publication-01` completed only Stage 10 and stopped at
`awaiting_master_en_acceptance`. The independently verified `MASTER_EN.md` is
20,863 bytes, SHA-256
`2AD1E9175A3B53B7C85CCA5824B2FAA60D4A82C38928F487E6BB7700B5617CA6`.
It is the exact accepted reconstruction normalized from CRLF to LF: six page
markers, twenty-one headings, two exact assets, zero excluded pages and all ten
compact statblock hard breaks remain. No Stage 20+ output or MASTER_EN
acceptance exists.

The read-only Stage 20 audit projects 87 translation units in eight batches,
two exact assets and 45 applicable terminology checks. It also proves three
generic P1 gaps: no safe production submission author, no preservation of the
accepted Markdown hard-break topology, and no independently produced/enforced
MASTER_RU verification evidence. The remediation changes sealed implementation
identity, so run `20260915-publication-01` must not be accepted or resumed.

The generic Stage 20/21 remediation is independently closed: submission
authoring is atomic, Markdown hard-break topology is enforced, an independent
standard-library MASTER_RU verifier is required, and acceptance requires exact
producer plus verifier evidence. Fresh run `20260915-publication-02` reproduced
only Stage 10 and stopped at `awaiting_master_en_acceptance`; run identity is
`5CF1DC43273E4B5472AD6DA4D255A8E13B3070FA326976209B3E0D1DDD0224C3`.
Its `MASTER_EN.md` is byte-identical to run01 at 20,863 bytes and SHA-256
`2AD1E9175A3B53B7C85CCA5824B2FAA60D4A82C38928F487E6BB7700B5617CA6`.
Independent run02 QA found no P0/P1/P2; no Stage 20+ output or MASTER_EN
acceptance exists.

The immediate next action is explicit user acceptance or a bounded correction
request for the run02 `MASTER_EN`. Translation to MASTER_RU, ArtView, HTML,
DOCX, Word-exported PDF and the production package remain closed until their
preceding gates are explicitly satisfied. Keep final Word stages on an
interactive logon on this station where COM activation succeeds. Use
`handoffs/orchestrator_mineru_local_execution_decision_20260914.md` as the
current execution-policy authority.

## Current authority override — compact boundary correction

The previous paragraph is historical. Fresh CPU-free replay
`20260915-cpu-replay-10` is now the accepted reconstruction authority. It adds
the generic exact `block_boundaries: compact` transform and removes only the
single empty separator between the final `HUMAN RESISTANCE` heading and its
first `STR` row. The corrected reconstruction is 21,046 bytes, SHA-256
`53B560862C3CC344C5C78676D988C3A4A479B5C0A0CBE4261B2E93080ED19993`;
independent QA found no P0/P1/P2 and acceptance receipt SHA-256 is
`E660EA6BBF24BAE683715F9C433C68134DC946D6BF9CFD1EF40B867DE0FBEE0B`.

Publication run `20260915-publication-05` is immutable historical evidence;
Stage 30 exposed a generic adapter defect because its copied asset manifest was
not accompanied by the exact relative assets. The reviewed fix validates the
complete manifest graph before copying it and materializes only the referenced
files. Run06 then exposed that the generic ArtView v3 HTML claimed to support
selection/export while presenting only static images. The independently
reviewed replacement adds safe per-row controls, explicit closure and canonical
SHA-256 export. Fresh publication run `20260915-publication-07` is the only resumable
publication authority. Its verified and conditionally accepted `MASTER_EN.md`
is 20,862 bytes, SHA-256
`571F96B077ACA59072C0399433E8372E997C9FC5D07428698D5580A2D5A1BED5`.
Stage 20 emitted 86 ordered translation units in eight batches. The sealed
Russian submission preserves all 86 unit identities. The generic terminology
gate now retains glossary domains and distinguishes required skill uses from
explicit occupation/profession uses; ambiguity fails closed and producer and
verifier implement the classifier independently. Stage 21 produced the
independently reviewed `MASTER_RU.md` at 36,367 bytes, SHA-256
`A4BA09330C84490F4CB6018919A4BB25699770AF594CDC659749B1E9C3BC7BFE`.
All producer, terminology, verifier and linguistic QA evidence passes with no
P0/P1/P2. The user explicitly accepted this exact Russian candidate on
2026-09-15; the fresh run07 receipt SHA-256 is
`FCFA128359A1AA380596C56F4189E728EB714F6A616E30F830822A246E9CCA39`.
Stage 30 produced two review rows: `dissociation-cover` at 100% centered and
`alaska-map` at 80% centered. Candidate QA passes all five gates and the review
tree ACL was normalized without changing artifact bytes. The user accepted
both current binaries with those defaults; strict decision validation passes
and Stage 31 application completed. Stage 40 exposed a generic escaping local
asset reference and stopped before publishing HTML. The next action is the
reviewed generic HTML asset-locality fix followed by a fresh publication run.
DOCX, PDF and packaging remain closed behind their later gates.

## Current authority override — accepted ArtView and HTML candidate

The preceding run07 next-action paragraph is historical. Run11 proved the
asset-locality fix but its full-page browser QA exposed duplicated visual
presentation and loose spacing in the final stat block. A scenario-neutral
renderer/config remediation now binds only the detected terminal numeric,
hard-broken stat-block heading, preserves its ten hard breaks, and uses compact
paragraph spacing. Independent critic review is GO with no P0/P1/P2; receipt
SHA-256 is
`69DAED4801B48C00AE619CECAA1233B03D987D4E0D59E948665E2E890C6DAA7A`.

Fresh publication run `20260915-publication-12` is the current implementation
authority, portable identity SHA-256
`A1BCCE994201F479057F97195894CD7E9455D5C1BD22507EE1E622679DFA00DA`.
It reproduced the exact accepted masters. The user's accepted run07 ArtView
JSON was strictly rebound only after exact candidate-graph and selected-binary
equivalence; validation passes `2/2`, Stage 31 is complete, and the run12
ArtView acceptance receipt SHA-256 is
`052D8E3D518C4A2933C538C5DE2407C6F782331EB779B16E3E2CFAAF26208F90`.
The current 62,801-byte HTML candidate has SHA-256
`4AED240DBA16BC99E5EFEFCEF6759DA0944CB340FEBFE8D747F456012E74299A`.
Automated QA reports `status=pass`, 21 headings, 6 source pages, 2 local images,
1 stat-block card, 0 missing references and 0 findings. Browser QA confirms one
visible final stat-block title/card, ten hard breaks, compact spacing, loaded
images and no horizontal overflow; receipt SHA-256 is
`BED226343A9B6655D611224D85EAEB99E07BD4743F3095DD0048843EBD490F14`.
Explicit HTML user acceptance is now the active gate. DOCX, PDF and packaging
remain closed.

## Current authority override — run14 page-boundary and numeral fixes

Run12 is historical: it still contains two source-page paragraph splits and
default Georgia old-style numerals. The permanent correction is in the Python
pipeline, not in a generated document. MASTER_EN v3 now normalizes only proved
adjacent-page prose boundaries before translation units are created and seals
the transition ledger; HTML applies global lining numerals. A new generic,
fail-closed `scenario_master_ru rebind-batches` route transfers a previously
reviewed translation only through exact source matches or those same two page
joins, using separate old/new run authority roots.

Fresh run `20260916-publication-14` has portable identity
`D201B1F1DD026385BF544774E68DDD95714B97F217E5AC414BC585BB69CA4760`.
Accepted MASTER_EN SHA-256 is
`2EB528C44A2B1A20C00D167AD255BA0C767B74653564A9FE9182D6A3FC51CABE`;
accepted MASTER_RU SHA-256 is
`E6975753BB3E8714269D9DDC01F97E6CE7F8EFA5810773949094BA03AAA5F9EA`.
Translation rebind counts are 82 exact, 1 dehyphenated-word join and 1
continued-prose join. The accepted ArtView choices were strictly rebound to
decision SHA-256
`318F0FCD69458B732E3FD4578F0F8CBF6D421EC73EE2439C75D6DB67876E318B`.

The current HTML is
`working/dissociation/publication/20260916-publication-14/outputs/40-html-candidate/artifacts/Dissociation_RU.html`,
62,820 bytes, SHA-256
`1E0AF3ECD764DF5E1231F5E1228332C4B587F56A221C8580682D932F2B7790F7`.
Automated report status is `pass`, both formerly split sentences are single
paragraphs, and CSS contains `font-variant-numeric: lining-nums`. It is served
locally at `http://127.0.0.1:8767/Dissociation_RU.html`. The active gate is
explicit user HTML acceptance or correction; do not start DOCX yet.

## Current authority override — complete run24 candidate

The preceding run14 gate is historical. The reusable pipeline now includes
the accepted hierarchical TOC, 12.5 pt TOC type, page-boundary cleanup,
lining numerals, footer-free DOCX generation and a current-host LibreOffice
DOCX/PDF engine under `.tools`. PDF remains accepted-DOCX-only.

Run23 visually closed the nine-page DOCX/PDF layout but exposed a Stage 70
identity-path mismatch: packaging renamed accepted ArtView decisions while the
immutable acceptance preserved the original run-relative path. The universal
fix preserves that safe path and rejects traversal. Run23 was not resumed after
the implementation change.

The current authority is publication-only run
`20260916-publication-24`, identity
`1E3DA56F257C36FA12D024119A32DC236133E19437DC2B24FCD284BC689CCCB6`.
It reused the accepted reconstruction without MinerU/OCR. MASTER_EN,
MASTER_RU and HTML are byte-identical to the accepted prior candidates.
The final DOCX SHA-256 is
`C7D245D0AE49B5F5A1896B3600A17019454BDDE2F685B0F2D1D4A717A52CD537`;
the final PDF SHA-256 is
`70328A80606B5A56D13FBA4871DBE78207AD158D8994F16206A5ECD862A35603`.
Both render to the same reviewed nine pages, and the DOCX has no footer/page
number structures. Stage 70/71 completed; package manifest SHA-256 is
`170F8FC12CE63AC3AEFE64FE95DBF33A8F137216D9E4873E465644A8C1F94128`.
Offline state is `candidate_for_release_review`. Independent gpt-5.5 release
review is GO with no P0/P1; receipt SHA-256 is
`49AF4873A530ECDA5585ED78DDA31EFB995CEED1E36F8019AF17A5A9E8A49108`.
The immutable package continues to report `release_state: not_reviewed`; the
separate critic receipt is the release decision record.

## Current authority override — run29 unified CoC terminology

The preceding run24 release decision is historical. The system-level CoC
terminology consolidation changes successor MASTER_RU bytes, so it cannot
approve the current candidate.

Current authority is publication-only run
`20260916-publication-29`, portable identity
`DEB6A06C12BB987C5B825DAD55E849D7726000F595398474E3C08FAFE13B0E2A`.
It reused the accepted reconstruction and did not rerun MinerU/OCR. The run
binds the sole canonical CoC registry at `16003` bytes / SHA-256
`EE84E121E63ECDA3F2165205E8335FD3C68E70CF1DEFE1D00CE6C3FF97EFF3AE`.
Terminology QA passes with `18` deterministic replacements; `ТЕЛ`, `НАР`,
`МОЩ`, `РАС` and `СКО` are present in the final stat block, while `РАЗМ` and
`ВНЕШ` are absent.

Current artifact hashes are:

- MASTER_EN: `2EB528C44A2B1A20C00D167AD255BA0C767B74653564A9FE9182D6A3FC51CABE`;
- MASTER_RU: `25537977DC1CAB80B9DDC04E603F95BB601F3C1EB29BAAFB6FFAD161A5F02E84`;
- HTML: `09D3E0618F9922255AE12A916D283FB9B2F900E8FE877C1072A52A44D8016B97`;
- DOCX: `D40140D8AD7C347B137042072826B16786F54AF5CECDE778748A8A6B8383A9CA`;
- PDF: `983AECFEE9395BAB44396E7EF600E98D930D2D07F7DB5A86FC9F0F835126CEAA`.

DOCX and PDF both render to nine pages. OOXML inspection reports zero footer
parts, footer references and `PAGE` fields. The PDF is a fresh export of the
exact accepted DOCX. Stage 70/71 completed; the package manifest file SHA-256
is `551AF24D7575CCCAF4DBB4661F03D4A4C27430DAFDA5F109BA8E16ED8BBF0F79`,
and the offline verifier reports `candidate_for_release_review` with exactly
one PDF. The remaining gate is a fresh independent release review of run29.

## Current authority override — reviewed DOCX successor

The user clarified that the corrected file is run29's Stage 50 DOCX, which was
the internal path previously supplied in chat. Its sole content change against
the packaged run29 DOCX is removal of one empty paragraph before the paragraph
beginning `Рядом находятся другие стандартные сенсорные устройства`.

The current reader authority is the separate successor bundle
`working/dissociation/publication/20260916-publication-29/outputs/73-reviewed-docx-package`.
It embeds the verified Stage 70 package unchanged under `base_package/` for
provenance and exposes one complete product tree at the root: HTML with its
two local assets, masters, ArtView/configs, acceptance/evidence, DOCX and PDF.
The DOCX is `538565` bytes,
SHA-256
`2AC1ACEFEF697B864B9D6DD33802083B72CCD2A4381430DE1C145008C5A7159A`.
The fresh PDF SHA-256 is
`89F2870D8FC76AF598A0F49A45C97D466B81C0E94F1BC5A0873A4478E290BAF6`.
It renders to eight pages; all eight images are byte-identical across two
independent fresh export attempts and were inspected at original resolution.
No clipping, overlap, missing glyphs, blank pages, footer, or broken stat block
was found. Revision verification passes at seal
`60153D751A1FA1A07AF0D43D572C2CC9F0CF42618FBB9211DA34D2AC01521866`,
state `candidate_for_release_review`, release state `not_reviewed`.

## Completed access-normalization closure

The run29 reviewed-DOCX successor exposed the same Windows access-prompt class
previously seen in Obsidian: its sandbox-created root retained a protected DACL
instead of inheriting from `outputs`. The generic normalizer existed but was
not connected to the publication engine or reviewed-DOCX materializers. It is
now wired into every publication stage and both reviewed-DOCX materializers,
preserves the `.obsidian` exclusion, and skips only isolated trees outside
`kb_creator/working`. The existing successor was repaired in place: all 321
objects report unprotected inherited ACLs, and the complete file-tree digest
remained `824A4D96F5DBB8C0A447D9EAC2104878C60A80FB207E47703B12CD60F8009E`.
Revision verification still reports seal
`60153D751A1FA1A07AF0D43D572C2CC9F0CF42618FBB9211DA34D2AC01521866`
and `candidate_for_release_review`. Focused evidence is `18 passed`, including
quarantine on an injected post-publish ACL failure; the
expanded relevant matrix is `139 passed, 3 skipped`. The broader matrix's
historical Viral-only fixture remains independently stale/missing and outside
this change. No subagent was assigned; current platform model/effort remain
unavailable and the recorded engineering-policy override remains
`gpt-5.6-sol` at high.

The obsolete wrapper-only `outputs/72-reviewed-docx-package` was deleted after
the complete `outputs/73-reviewed-docx-package` passed verification and ACL
checks. The generated publication trees remain ignored working artifacts; the
reusable pipeline, verification, documentation and regression changes are the
Git commit scope.
