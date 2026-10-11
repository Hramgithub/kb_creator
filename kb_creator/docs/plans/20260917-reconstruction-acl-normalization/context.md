# Reconstruction candidate ACL normalization context

## Objective and boundary

Repair the reusable Stage 06 materialization path so a real candidate produced under the Codex Windows sandbox is readable by the Codex desktop UI and normal user processes. The goal does not change candidate content, acceptance state, publication, or Git history.

## Accepted decisions and constraints

- The defect belongs to the pipeline/application boundary, not to the user's personal file handling.
- Reuse the existing `normalize_publication_access_if_managed` implementation rather than duplicate `icacls` logic.
- Apply normalization to the final Stage 06 output only after the atomic publish/rename.
- Preserve deterministic file identities and fail closed on normalization errors.
- Isolated test trees outside `kb_creator/working` may declare a skip; real managed Windows outputs may not silently remain unreadable.

## Completed evidence

- Seed candidate ACL and owner inspected.
- Exact candidate tree repaired with the existing helper; byte hash unchanged.
- Reconstruction skill, KB Creator README, governance, prior Dream plan/context, replay-resume code, tests, and access-normalization helper read.
- Architecture confirmed the hook after final output rename and before manifest publication, with revalidation on rerun and fresh-output quarantine on failure.
- Implementation binds the normalizer into Stage 06 and producer closure; the helper grants additive read/execute only to the exact desktop principal and excludes `.obsidian`.
- Focused tests pass `22/22`; expanded relevant tests pass `279` with `1` skip.
- A live managed synthetic Stage 06 received an exact `KAMAZNOTEBOOK\user` RX ACE and was read successfully by an external `kamaznotebook\user` process.
- Bounded QA verified the managed Stage 06 manifest/candidate and the repaired Dream candidate; hashes and inventories match.
- Independent critic final verdict is `APPROVE_IMPLEMENTATION`; the ambiguous-domain P2 was corrected and retested.
- Final relevant regression passes `280` tests with `1` skip; focused ACL/replay passes `23` tests.

## Active step

Goal completed. The reusable Stage 06 ACL gate is implemented, tested, live-verified at the filesystem boundary, and independently approved.

## Blockers

None.

## Next action

Hand off the completed implementation. Do not claim the Codex UI tab opened when the navigation bridge only reported `queued`; commit or push only on explicit instruction.
