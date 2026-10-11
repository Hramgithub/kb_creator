# Immutable clarification — adjacent source-QA hash attribution

- Goal: `20261004-user-docx-review`; clarification to the adjacent-provenance note in immutable U5 Fear correction v05.
- Timestamp: `2026-10-04T21:47:14Z` (same bounded follow-up window; exact write time unavailable).
- Bounded QA role: `gpt-6-luna / medium`; actual runtime unverified. Orchestrator policy owner: `gpt-6-sol / medium`; scoped override: none.
- Assignment state: clarification complete; orchestration and acceptance remain with `/root`.
- Elapsed time and token use: unavailable.

Correction to the adjacent note in `handoffs/U5-fear-qa-correction-v05.md`: the handoff `handoffs/U7-source-qa-v03.md:13` contains the complete, correct Kremlin DOCX SHA-256 `6C110ED5E62F29E3FACF97AE3B2D8E515B0066CC1B9F48CCC4D45F09FB3B81A0`. The truncated value ending `...FB3B81A` occurs in `audit/conversion/source-qa/U7-source-visual-qa-v03.md:10` (missing final `0`). The source-QA JSON `audit/conversion/source-qa/U7-source-visual-qa-v03.json` also contains the correct full SHA-256 `6c110ed5e62f29e3facf97ae3b2d8e515b0066cc1b9f48ccc4d45f09fb3b81a0`. This clarification changes only the attribution of the historical prose typo; v05's Fear `review_index.json` hash correction remains valid. No historical evidence was edited.

Files checked: the three paths above; line locations re-read from current working copies. No DOCX/source/render was modified.
