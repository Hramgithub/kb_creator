# Number 7 Dream compact line-flow fidelity context

## Objective and boundary

Repair false paragraph boundaries and related source-order defects in compact
line groups at reconstruction Stages 05-06, then rebuild a fresh immutable
candidate. Do not edit the source PDF, overwrite replay-15/v26, accept the
reconstruction, or promote it to `MASTER_EN`.

## Seed and current evidence

- User seed: source page 24 character fields render as separate paragraphs,
  e.g. `Luck: 65`, `HP: 11`, `MP: 8`, `Damage Bonus: 0`, `Build: 0`, and
  `Move: 7` acquire unintended vertical gaps.
- Replay-15 pages 21-24 contain blank lines between these fields, while pages
  25-26 already use Markdown hard breaks for the same visual role.
- Stage 04 source visuals show the page 21-24 fields as tightly stacked lines
  followed by a visibly larger separation before `Skills:`.
- Page 23 also selects `Luck` before the main `STR ... SAN` row although the
  source geometry and visual reading order put the main row first.
- The shared semantic contract currently represents blockquotes, lists,
  statblocks, headings, and tables but has no compact line-group kind. Thus the
  Stage 05/06 gate can pass a lexically complete yet paragraph-fragmented page.
- `MASTER_EN` projection is downstream and cannot be the first repair layer for
  a reconstruction decision defect.

## Current state

L1-L7 are complete. Full-scope QA passes the immutable replay-16/v27
successor, and the independent implementation verdict is
`APPROVE_IMPLEMENTATION` with no critical/high/medium findings. Canonical
documentation is updated. This closes the implementation goal but does not
accept reconstruction or authorize `MASTER_EN`.

## Completed evidence

- Independent full-scope scan confirmed one defect class only: pages 21-24
  contain false paragraph boundaries; pages 25-26 are correct analogues. Page
  23 also reverses the first two field rows. No analogous defect was confirmed
  elsewhere in pages 1-20.
- Root cause: the older Dissociation repair manually inserted Markdown hard
  breaks in one scenario decision. Downstream Python preserved them, but the
  reconstruction semantic contract neither authored nor validated this kind of
  ordinary compact line group.
- Shared additive representation `line_group / hard_break_lines` now binds
  ordered source blocks to physical Markdown rows and rejects blanks, missing
  breaks, final-row breaks, count drift, ambiguity, and reordered rows.
- Authoring and validate-only share selected-block reorder and effective
  Markdown paths. The implementation contains no Dream labels, page numbers,
  or punctuation-based grouping heuristic.
- Focused tests pass `22/22`; the integrated relevant suite passes `323` with
  one unrelated skip.
- Fresh replay `20260917-cpu-replay-16` and decisions-v27 are sealed through
  Stage 06. Stage 05 passes all 26 pages, 59 semantic units and six visual
  assertions. Audit and sidecar share structure SHA-256
  `155ACBF7EB4099ECD670868D4C6088B87F5FD9C269D5FFEF82B50A49E68D8785`.
- All six page 21-26 groups have zero internal blank lines, canonical two-space
  hard breaks on every non-final row, none on the final row, and an ordinary
  boundary before `Skills:`. Page 23 is `STR...SAN`, then `Luck`.
- Pages 1-20 are byte-identical to replay-15; pages 25-26 change only from
  three-space to canonical two-space break suffixes. Replay-15/v26 retain their
  recorded hashes and the source PDF retains SHA-256
  `C03AD05644C5B7438E4FAB750557EB8098E637492242D21969C5C4110FBF97D0`.
- Independent L5 candidate QA verdict: PASS.
- Independent L6 implementation verdict: `APPROVE_IMPLEMENTATION`; no
  actionable finding. The reviewer could not rerun pytest in its isolated
  runtime, but reviewed the root-run `323 passed, 1 skipped` evidence and
  independently validated the live artifacts.

## Constraints

- Source PDF and existing sealed replay/decision roots are immutable.
- Use visually reviewed source-block mappings; do not infer semantic grouping
  from punctuation alone.
- Keep pipeline code scenario-neutral and add fail-closed tests.
- Preserve unrelated dirty-worktree changes.

## Blockers

None for this completed implementation goal.

## Next action

Await explicit user acceptance or further reconstruction corrections for the
replay-16 candidate. Do not promote to `MASTER_EN` merely because the line-flow
implementation and reconstruction QA passed.
