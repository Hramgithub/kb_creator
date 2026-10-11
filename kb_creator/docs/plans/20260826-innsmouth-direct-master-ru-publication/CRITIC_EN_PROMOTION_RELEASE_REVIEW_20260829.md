# Innsmouth EN Promotion Release Review - 2026-08-29

## Immutable Handoff Receipt

- review_kind: release
- candidate_state: promoted non-frozen repository candidate in dirty worktree
- verdict: APPROVE
- reviewer_role: independent critic
- implemented_or_materially_designed_candidate: no
- orchestration_ownership_transfer: no
- timestamp: 2026-08-29 02:33:33 +03:00
- elapsed_time: 270 seconds active goal time at receipt drafting
- token_use: 114502 at receipt drafting
- orchestrator_policy_owner: gpt-5.6-sol medium
- assignment_state: platform-unverified
- scoped_override: only write allowed was this immutable receipt; no implementation, canonical plan, context, project status, release file, commit, push, RU, HTML or PDF edit

## Scope Reviewed

Assigned worktree:

`D:\NRI\.worktrees\innsmouth-master-en-main`

Reviewed candidate:

`kb_creator/inputs/innsmouth/master_en/accepted_20260829`

Release scope is limited to the accepted MASTER_EN save-point and the exact
current EN changes in the dirty worktree. This does not approve RU, HTML, PDF,
Foundry, publication activation, or any future mutation of the candidate.

## Files Checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/plan.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/context.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/MASTER_EN_PIPELINE_BOUNDARY_AUDIT_20260829.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/CRITIC_EN_PIPELINE_REVIEW_20260829.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/CRITIC_EN_PIPELINE_R2_REVIEW_20260829.md`
- `kb_creator/inputs/innsmouth/master_en/README.md`
- `kb_creator/inputs/innsmouth/master_en/PIPELINE.md`
- `kb_creator/inputs/innsmouth/master_en/accepted_20260829/MASTER_EN.md`
- `kb_creator/inputs/innsmouth/master_en/accepted_20260829/MASTER_EN.qa.json`
- `kb_creator/inputs/innsmouth/master_en/accepted_20260829/MASTER_EN.acceptance.json`
- `kb_creator/scripts/build_innsmouth_reconstructed_en.py`
- `kb_creator/scripts/build_innsmouth_master_en.py`
- `kb_creator/scripts/freeze_innsmouth_master_en_repo_input.py`
- `kb_creator/scripts/verify_innsmouth_master_en_repo_input.py`
- `kb_creator/scripts/build_innsmouth_master_en_packet7_user_review_successor.py`
- `kb_creator/tests/test_build_innsmouth_reconstructed_en.py`
- `kb_creator/tests/test_build_innsmouth_master_en.py`
- `kb_creator/tests/test_freeze_innsmouth_master_en_repo_input.py`
- `kb_creator/tests/test_innsmouth_master_en_repo_input.py`
- `kb_creator/tests/test_innsmouth_master_en_packet7_user_review_successor.py`
- historical Packet7 receipt:
  `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/critic_innsmouth_master_en_packet7_user_review_successor_release_review_20260826.md`

## Git Scope Evidence

`git status --short --branch --untracked-files=all` shows the current dirty
scope is limited to:

- canonical status/context/plan documentation already modified before this review;
- MASTER_EN README/PIPELINE documentation;
- EN verifier and Packet7/repository verifier tests;
- prior EN pipeline audit and critic receipts;
- accepted MASTER_EN package root plus exactly its 38 assets;
- Stage B, Stage C and freeze scripts plus their tests;
- this release-review receipt after it is written.

No unrelated project, temp log, raw transcript, browser profile, secret store,
Foundry path, RU accepted package, HTML or PDF output appeared in the checked
status scope.

## Candidate And Freeze Evidence

The promoted package exists at
`kb_creator/inputs/innsmouth/master_en/accepted_20260829` and verifies as:

- file_count: 41
- asset_count: 38
- total_bytes: 8085246
- canonical repository inventory SHA-256:
  `A71F591B39D3DEB6C1EFE60AF48A22B5B779D0CABEDA4FB71FB1EB6F32F7E584`
- `MASTER_EN.md`: 130028 bytes,
  `4A3DDE7AC0EA7A6815AE7FE3CAD38062CC828CF5880D549026E99D5496389A50`
- `MASTER_EN.qa.json`: 14362 bytes,
  `CED340C73D98B889269C915359FEDE44866CA04ED9216474C366BAE8284149CF`
- `MASTER_EN.acceptance.json`: 1320 bytes,
  `E9DB9E5511C0A9F8DBB1CD126009329320BBF03BFA6D9FCB289E2EC757734E1B`
- accepted 38-asset inventory SHA-256:
  `C1A9AB2F89650201C91FA74EAB809E16724D0C608534CFBFAA478AEEBA9CAE3A`

`MASTER_EN.acceptance.json` records:

- schema: `InnsmouthAcceptedMasterEn.v1`
- state: `ACCEPTED_MASTER_EN_REPO_INPUT`
- accepted_on: `2026-08-29`
- acceptance_authority: `explicit_user_promotion_in_main_chat`
- manual copy forbidden
- historical RU or EN bridge forbidden
- generated HTML or PDF manual edit forbidden

Stage B provenance is exact in both QA and acceptance manifest:

- `RECONSTRUCTED_EN.md`: 138388 bytes,
  `72CF965DF27C28D5D3927867E0A08C8655F5A7A117E108716FA84521649A8F13`
- `RECONSTRUCTED_EN.qa.json`: 74886 bytes,
  `D8103F92052F86945BABA9E964AE805C435C42AFA19C47E4BD8C59E998DEC106`
- Stage B asset inventory: 135 assets,
  `421467CBDB51E96D6025EE733EB7E67CB61C6C6F15BA52C2F0DAE248801BE66A`

`freeze_innsmouth_master_en_repo_input.py` now hard-compares the candidate QA
`input` object to these canonical Stage B identities before accepting or
manifesting the package. Mutation of these identities invalidates this receipt.

## Verification Commands And Results

Promoted repository verifier:

```powershell
python -B kb_creator\scripts\verify_innsmouth_master_en_repo_input.py --inventory
```

Result:

```text
INNSMOUTH_ACCEPTED_MASTER_EN_REPO_INPUT_OK
file_count=41 asset_count=38 total_bytes=8085246
inventory_sha256=A71F591B39D3DEB6C1EFE60AF48A22B5B779D0CABEDA4FB71FB1EB6F32F7E584
```

Freeze verifier:

```powershell
python -B kb_creator\scripts\freeze_innsmouth_master_en_repo_input.py --verify --target kb_creator\inputs\innsmouth\master_en\accepted_20260829
```

Result:

```text
ACCEPTED_MASTER_EN_REPO_INPUT_VERIFIED
INNSMOUTH_ACCEPTED_MASTER_EN_REPO_INPUT_OK
```

Focused root-level EN release suite, with bytecode and pytest cache disabled:

```powershell
python -B -m pytest `
  kb_creator\tests\test_build_innsmouth_reconstructed_en.py `
  kb_creator\tests\test_build_innsmouth_master_en.py `
  kb_creator\tests\test_freeze_innsmouth_master_en_repo_input.py `
  kb_creator\tests\test_innsmouth_master_en_repo_input.py `
  kb_creator\tests\test_innsmouth_master_en_packet7_user_review_successor.py `
  -q -rs -p no:cacheprovider
```

with required environment variables including `NRI_INNSMOUTH_PACKET7_R2` set.

Result:

```text
33 passed in 4.47s
```

Reviewer note: an earlier run of the same focused suite without
`NRI_INNSMOUTH_PACKET7_R2` produced `25 passed, 8 skipped`; that run is not used
as acceptance evidence. The corrected no-skip run above is the release evidence.

Broad `kb_creator/tests` collection was checked only to classify known
out-of-scope tests:

```powershell
python -B -m pytest kb_creator\tests --collect-only -q -p no:cacheprovider
```

Result:

```text
207 tests collected, 15 errors in 0.28s
```

All 15 collection errors are archived `page_proof` or
`raw_authority_projection` imports from modules absent on this branch. They are
outside the EN promotion scope and were not repaired or used to block this
release review.

## Content And Exclusion Checks

Accepted package absolute-path scan:

```powershell
rg -n "[A-Za-z]:[\\/]|\\\\" `
  kb_creator\inputs\innsmouth\master_en\accepted_20260829\MASTER_EN.md `
  kb_creator\inputs\innsmouth\master_en\accepted_20260829\MASTER_EN.qa.json `
  kb_creator\inputs\innsmouth\master_en\accepted_20260829\MASTER_EN.acceptance.json
```

Result: no matches.

Accepted package and scoped implementation scan for technical comments,
forbidden bridge terms and obvious credentials found no reader-package leakage
or credentials. Matches were limited to:

- tests asserting absence of `mineru-page` and `table-evidence`;
- Stage B/C builder logic that strips or counts reconstruction comments;
- local Stage B variable names such as `source_hash`;
- the ordinary word `secret` in reader prose, not a credential.

Accepted `MASTER_EN.qa.json` declares final counts:

- image_links: 38
- tables: 51
- headings: 155
- anchors: 50
- fragments: 79
- broken_fragments: 0
- ordinary_page_links: 33
- external_page_references: 3
- page_markers: 0
- table_evidence_comments: 0

Declared exclusions are explicit and accepted:

- source pages 43, 44 and 45 are excluded only at Stage C reader scope;
- historical RU v6, old cleaned EN, translation memory and the
  `unit_id/source_hash` bridge are forbidden as production input;
- RU synchronization, HTML, PDF, commit, push and publication activation are
  outside this release receipt.

## Source-Visible Anomaly Check

The assignment's `Spot Hidden 60% (307/12)` item is source-preserving, not an EN
defect. Read-only PDF page-40 text extraction from
`D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_origin.pdf`
returned:

```text
Spot Hidden
60% (307/12)
```

The accepted MASTER_EN contains:

```text
Spot Hidden</td><td>60% (307/12)</td>
```

Therefore the accepted EN correctly preserves the source-visible publisher
anomaly.

## Findings

No P0 findings.

No P1 findings.

No P2 findings.

No blockers.

Residual note: this is a non-frozen dirty-worktree candidate until committed.
The receipt approves the reviewed manifest and current worktree state only; it
does not substitute for a post-mutation review.

## Recommendation

APPROVE.

The promoted accepted MASTER_EN package, manifest, Stage B provenance binding,
freeze verifier, independent repository verifier, no-skip EN release suite and
declared exclusions are sufficient for the scoped EN save-point commit/push
authorized by the user. This receipt authorizes only that EN save point. It does
not authorize RU acceptance, HTML, PDF, release publication, production
activation, or orchestration ownership transfer.

## Invalidation

This receipt is invalidated by any mutation to:

- `kb_creator/inputs/innsmouth/master_en/accepted_20260829/`
- `kb_creator/scripts/build_innsmouth_reconstructed_en.py`
- `kb_creator/scripts/build_innsmouth_master_en.py`
- `kb_creator/scripts/freeze_innsmouth_master_en_repo_input.py`
- `kb_creator/scripts/verify_innsmouth_master_en_repo_input.py`
- `kb_creator/scripts/build_innsmouth_master_en_packet7_user_review_successor.py`
- the five focused EN test files listed above
- `kb_creator/inputs/innsmouth/master_en/README.md`
- `kb_creator/inputs/innsmouth/master_en/PIPELINE.md`
- referenced Stage B, Stage C, source PDF, MinerU/OCR inputs or Packet7 R2
  external evidence
- any commit-scope change that adds unrelated files, secrets, temporary logs,
  raw transcripts, browser profiles, RU, HTML, PDF, Foundry or release artifacts

After invalidation, rerun both verifiers, the no-skip EN release suite and a
fresh independent release review before using this candidate as release-gate
evidence.
