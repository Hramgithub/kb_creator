# C1 architecture receipt — structural correction contract

## Receipt

- Goal/step: `20260918-dream-master-en-corrections` / C1.
- Role: architecture/root cause; policy assignment `gpt-5.6-sol`, high.
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, medium; ownership not transferred.
- Assignment state: `platform-unverified`; scoped override: none.
- Result: **SPEC_READY**. The defects originate in decision v27 before Stage 05;
  Stage 06, promotion, and publication-01 only preserved them.
- Files changed: this receipt only.
- Evidence: all 26 v27 page decisions, Stage 04 packets, Stage 02 middle titles,
  page-10/page-21 visuals, Stage 05/06 consumers, author, tests, and schemas.
- Blockers: none. Successor hashes are intentionally unknown until built.
- Next action: implement this contract, then author v28 and build immutable successors.
- Timestamp: `2026-09-18T04:15:00+03:00`; elapsed: approximately 35 minutes;
  token use: unavailable.

## Closed audit result

- Exactly three selected structural title conflicts have
  `v2_title=true`, `markdown_heading=true`, `middle_title=false`:
  page 10 `original_pipeline_txt:137`, page 10 `:139`, page 21 `:309`.
- Page 10 has the two real defects. Middle/visual evidence reads
  `THE ENLIGHTENED WEBSITE` and `THE ENLIGHTENED WELLNESS CENTRE`.
- Page 21 is a required negative control: the visual wraps after the hyphen,
  but the exact lexical title remains
  `APPENDIX C - PREGENERATED PLAYER-CHARACTERS`. It must be confirmed, not split.
- Exactly three interior multi-blank runs exist in all 26 pages: page 18 lengths
  `5`, `5`, `3`, between Stanwick/Elsie, Elsie/Regular, Regular/Heavy statblocks.

No word dictionary, uppercase-token heuristic, or automatic word splitting is
permitted. The correct model is the existing exact `text correction:` ledger
plus a new exact title-conflict confirmation.

## Exact contract/API changes

### Title conflicts

Add this reviewed note grammar:

```text
title evidence confirmation: <view>:<raw_index> -> <exact reader heading>; reason: <nonempty reason>
```

Add to `kb_creator/pipeline/semantic_structure.py`:

```python
reviewed_title_evidence_confirmations(
    decision: Mapping[str, Any],
    packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    markdown: str,
    page: int,
) -> dict[tuple[str, int], str]
```

Rules:

1. A candidate is a selected block with `purpose == "structure"`,
   `v2_title is True`, `markdown_heading is True`, and
   `middle_title is False`. `model_title` cannot waive it.
2. Every candidate has exactly one confirmation; every confirmation binds one
   current candidate. Reject missing, duplicate, malformed, stale, unselected,
   wrong-view, and wrong-index rows.
3. The reader value must occur exactly once as an ATX heading, including the
   existing nested `> #` form.
4. If reader text differs from packet source text, the same review notes must
   also contain one valid `text correction: <source> -> <reader>; reason:` row.
   An unchanged confirmation needs no correction.
5. Require `review.visual_reviewed is True`; reuse the already bound semantic
   visual identity. Never infer a replacement.
6. Include view/index, source SHA-256, reader SHA-256, and `changed` in each
   page's semantic report so `structure_sha256` seals the resolution.

`validate_semantic_structure()` calls this helper before unit validation.
`materialize_mineru_ai_merge._validate_decision()` calls the same helper before
its selected-title guard and accepts only its exact reader heading as a
replacement. Do not create a second parser or a materializer-only override.
`audit_v4_content()` inherits the gate through the shared validator.

Stable failure codes (prefix the raised message with the code):

- `title_evidence_confirmation_required`
- `title_evidence_confirmation_invalid`
- `title_evidence_confirmation_stale`
- `title_text_correction_required`
- `title_reader_heading_mismatch`

Required Dream notes:

```text
text correction: THE ENLIGHTENEDWEBSITE -> THE ENLIGHTENED WEBSITE; reason: Stage 02 middle lines and the bound Stage 04 visual confirm the word boundary
title evidence confirmation: original_pipeline_txt:137 -> THE ENLIGHTENED WEBSITE; reason: Stage 02 middle lines and the bound Stage 04 visual confirm the exact heading
text correction: THE ENLIGHTENEDWELLNESS CENTRE -> THE ENLIGHTENED WELLNESS CENTRE; reason: Stage 02 middle lines and the bound Stage 04 visual confirm the word boundary
title evidence confirmation: original_pipeline_txt:139 -> THE ENLIGHTENED WELLNESS CENTRE; reason: Stage 02 middle lines and the bound Stage 04 visual confirm the exact heading
title evidence confirmation: original_pipeline_txt:309 -> APPENDIX C - PREGENERATED PLAYER-CHARACTERS; reason: the bound Stage 04 visual confirms a layout wrap after the hyphen, not a lexical space
```

### Blank separators

Add to `semantic_structure.py`:

```python
validate_canonical_blank_separators(markdown: str, page: int) -> int
```

After `apply_block_boundaries()`, reject every interior maximal run of more than
one root-level empty physical line. `>` and Markdown hard-break lines are not
empty. Return the redundant-run count (zero on success) and seal it in the page
report. Failure code: `redundant_root_blank_separator`, with page, one-based
start line, and run length.

Add to `author_reviewed_semantic_decisions.py`:

```python
_canonicalize_blank_separators(
    markdown: str,
    declarations: list[dict[str, Any]],
    page: int,
) -> str
```

Authoring input:

```json
{"rules":{"blank_separators":[{"before_line":"<exact line>","after_line":"<exact line>","expected_blank_lines":5}]}}
```

Each declaration has exactly those keys; line selectors are exact, nonempty,
single lines; the count is an integer at least 2; the complete interval matches
exactly once; declarations cannot duplicate or overlap. Replace only that run
with one empty line. Apply last, after patches, review rules, post-patches, and
line-group canonicalization. Codes:

- `blank_separator_declaration_invalid`
- `blank_separator_selector_mismatch`
- `blank_separator_declaration_overlap`

Page 18 declares the exact three `5/5/3` intervals. There is no global author
cleanup; the validator rejects any undeclared remainder.

## File scope

Change only reusable code/tests plus immutable reviewed data:

- `kb_creator/pipeline/semantic_structure.py`
- `kb_creator/scripts/author_reviewed_semantic_decisions.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_semantic_structure.py`
- `kb_creator/tests/test_author_reviewed_semantic_decisions.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- successor JSON fragments under this goal's `handoffs/`

No change is required to Stage 03, replay Stage 01-04, or the JSON shapes in
`page_semantic_structure.v1.schema.json` and
`reconstruction_semantic_structure.v1.schema.json`: review notes and semantic
report page rows already carry the data. Rerun both schema validations. Keep
profile v1; old v27 must now fail the tightened semantic gate.

Build v28 from decision v27 as baseline. Reuse the accepted A7 unit definitions
for all 26 pages, remove transformations already embodied in v27, and add only
the page-10 patches/notes, page-18 separator declarations, and page-21 note.
Never edit a decision output or sealed run tree in place.

## Test matrix

Focused tests must cover:

- changed conflict with matching correction/confirmation passes;
- unchanged conflict confirmation passes;
- missing, duplicate, stale, malformed, wrong key, unselected key, wrong reader,
  and changed-without-correction fail with the stable codes;
- non-conflicting selected titles need no confirmation;
- exact `5/5/3 -> 1/1/1` authoring;
- wrong count, ambiguous selector, duplicate, overlap, and undeclared remainder fail;
- `>` blank markers and hard-break line groups remain byte-stable;
- Stage 05 audit and Stage 06 materializer both reject the original defects;
- Dream successor reports exactly three title confirmations and zero redundant runs.

Run:

```powershell
python -m pytest kb_creator/tests/test_semantic_structure.py kb_creator/tests/test_author_reviewed_semantic_decisions.py kb_creator/tests/test_materialize_mineru_ai_merge.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py
python -m pytest kb_creator/tests/test_reconstruction_replay_resume.py kb_creator/tests/test_reconstruction_promotion.py
```

Use the repository's approved combined pytest environment; also run
`git diff --check` and schema validation. Report historical Dissociation
producer-closure drift separately; do not hide it.

## Successor commands and gates

All targets below must be absent before invocation.

```powershell
$py = '.tools/MinerU/profiles/pipeline-cpu-v1/.venv/Scripts/python.exe'
$source = 'C:\_Hobby\Yandex.Disk\НРИ\1_Зов Ктулху\temp\Call_of_Cthulhu_Miskatonic_Repository_Modern_Number_7_Dream_2021.pdf'
$replay = 'kb_creator/working/number-7-dream/reconstruction/20260918-cpu-replay-17'
$v28 = 'kb_creator/working/number-7-dream/reconstruction/20260918-cpu-replay-17-decisions-v28'

& $py -B -m kb_creator replay run `
  --contract kb_creator/contracts/number-7-dream.reconstruction.json `
  --source $source `
  --source-run-root kb_creator/working/number-7-dream/reconstruction/20260917-cpu-first-06 `
  --run-root $replay --run-id 20260918-cpu-replay-17 `
  --through-stage 04-visual-merge-bundle `
  --mineru-root .tools/MinerU `
  --pdftoppm .tools/poppler/poppler-26.02.0/Library/bin/pdftoppm.exe `
  --powershell 'C:\Program Files\PowerShell\7\pwsh.exe' `
  --python $py --provider-capabilities .tools/MinerU/capabilities/providers.json `
  --mineru-source-root MinerU --ocr-language en --json

& $py -B kb_creator/scripts/author_reviewed_semantic_decisions.py `
  --run $replay `
  --baseline kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-16-decisions-v27 `
  --spec kb_creator/docs/plans/20260918-dream-master-en-corrections/handoffs/c3-pages-01-13.json `
         kb_creator/docs/plans/20260918-dream-master-en-corrections/handoffs/c3-pages-14-26.json `
  --validate-only

& $py -B kb_creator/scripts/author_reviewed_semantic_decisions.py `
  --run $replay `
  --baseline kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-16-decisions-v27 `
  --spec kb_creator/docs/plans/20260918-dream-master-en-corrections/handoffs/c3-pages-01-13.json `
         kb_creator/docs/plans/20260918-dream-master-en-corrections/handoffs/c3-pages-14-26.json `
  --output $v28

& $py -B -m kb_creator replay resume --run-root $replay `
  --decisions "$v28/decision_set.json" --decisions-root "$v28" --json
```

`replay resume --decisions-root` names the decision-set root containing both
`pages/` and `reviewed_allowlist.v3.json`; passing `pages/` fails closed on the
allowlist identity and creates no Stage 05/06 output.

Replay resume must stop at `candidate_ready_for_reconstruction_qa`, with no
acceptance inferred. Full QA then proves 26 pages, corrected page-10 headings,
unchanged page-21 hyphenation, no old glued strings, page-18 separators exactly
`1/1/1`, prior semantic containers/line groups/assets unchanged, and passing
audit/sidecar.

After QA only:

```powershell
& $py -B -m kb_creator reconstruction-promotion materialize --run-root $replay --json
& $py -B -m kb_creator reconstruction-promotion record-acceptance `
  --run-root $replay `
  --user-decision-reference 'Codex task 01a0abfd-bdb8-76f3-8f73-7e1cddc3f2f3, 2026-09-18: мастер принят; исправить две склейки и лишние переносы' --json
```

Run publication preflight and then the existing Stage-10 `publication run`
command with the unchanged Git-visible Dream publication contract/config root,
the fresh replay-17 promotion inventory/acceptance, and absent run root
`kb_creator/working/number-7-dream/publication/20260918-publication-02`.
It must stop at exit `10`, `awaiting_master_en_acceptance`. Verify the same
full-scope assertions, then call `publication record-acceptance` using only the
fresh run's manifest-listed candidate inventory, QA, and independent verifier
evidence. Bind the exact user reference above; do not accept publication-01.

Replay-16/v27, its promotion, and publication-01 remain immutable historical
evidence. No Stage 20, commit, push, or release is authorized here.
