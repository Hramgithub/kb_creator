# Immutable handoff — U7 exact card conversion engineering v01

- Goal ID: `20261004-user-docx-review`; step ID: `U7`.
- Contributor: `/root/conversion_engineering`; requested role/effort: engineering, `gpt-6-sol / high`. Actual platform model/effort: unavailable.
- Orchestrator policy owner: main `/root`, `gpt-6-sol / medium`; orchestration ownership did not transfer.
- Assignment state: `platform-unverified`; scoped override: none.
- Timestamp: `2026-10-05T00:16:07+03:00` (Europe/Moscow).
- Elapsed time: unavailable (exact start timestamp was not captured). Token use: unavailable (platform did not expose role usage).
- Scope: bounded Word-only exact characteristic and direct card skill-label operation planning for the current reviewed Leningrad and Kremlin packages. No output book authoring, generic module mutation, HTML/PDF generation, OCR, translation, shared CSV/status or canonical plan/context/release edits.

## Result

Produced a reversible planning ledger: 175 exact span operations across 133
atomic text nodes. This comprises 146 old-scale characteristic fields (122
Leningrad, 24 Kremlin) and 29 skill-label/context operations, including the two
user-approved 90/75 Stealth presentations. The 15 Leningrad scenario cards
(14 numeric records plus one object), five pregen investigator sheets and three
Kremlin NPC records are accounted for. Each operation binds original DOCX/source
hashes, edition/page evidence, entity heading, zero-based paragraph/table/cell/
run/text path, exact before text/hash, after text, reversal and rule. Shared
text nodes have atomic before/after groups so later application need not use
stale sequential contexts. Separate diagnostics preserve source-derived fields
and show seven nonzero Leningrad HP arithmetic differences without proposing
HP edits. Albion Luck 75 and all original native comments remain protected.

## Files checked and created

Checked goal `plan.md`, `context.md`, assigned U7 task packet, NRI goal
governance, project README/status, manifest, U7 architecture specification,
U7 QA statblock inventory, U2 terminology inventory, accepted choices,
review decisions, canonical terminology CSV, both current reviewed DOCX ZIPs,
both immutable source PDF hashes, and the new DOCX-only revision API. Existing
HTML was used read-only for source-page correspondence. No original file was
modified.

Created only within owned `audit/conversion/operations/`:

- `build_ledger.py` and `probe_word.py` (read-only, bundled-Python `-X utf8` tooling).
- Two book topology JSON snapshots.
- `U7-word-operations-v01.json` (SHA-256 `93D25D6420A215842F781349ECBA1C798EA9C324A825930EB22A04C037AEC34A`).
- `U7-derived-diagnostics-v01.json` (SHA-256 `FF7D7A0F5075D6AEF8B987BBBBF48740E126CEE968E31D3EF835DDDECE0AFDB4`).
- `U7-operation-audit-v01.md` (SHA-256 `AE10D072F63820CF90C0BA6A74C4F15C2B509919A66018CA028AE90720330D7E`).
- This new immutable receipt.

## Verification and evidence

`python -X utf8 audit/conversion/operations/build_ledger.py` succeeded with
fresh DOCX/source PDF/CSV hash assertions and exact unique text-node matching.
The JSON parse/invariant check passed: 175 unique operation IDs, 133 atomic
nodes, no overlapping spans, valid before/after hashes, 22 derived diagnostic
records and three finite local blockers. Input Leningrad Word SHA-256 is
`3E2172AB1CC9C045F9F5F472BF6F664337A06969FEDC786BEB2D8D40459007C8`;
Kremlin is `6C110ED5E62F29E3FACF97AE3B2D8E515B0066CC1B9F48CCC4D45F09FB3B81A0`.
All four native Leningrad comment/thread part hashes are embedded in the
ledger. No candidate DOCX or visual QA is claimed.

## Blockers, risks and next action

The current `reviewed_docx_revision.py` requires a native root comment ID for
every text operation. These card fields are unannotated and often reside in
table cells or share a text run. Main and the DOCX-only engineer were informed;
that engineer confirmed a separate exact-field extension is needed after the
Fear candidate freeze. Two Bargain/Persuade skill collisions (Leon 40/40,
Colin 40/32) need entity-level disposition. Katerina's `1D6 СИЛ` drain crosses
three Word runs and needs explicit topology support or a held row. Boris's
unspecialized Art 50, combat adjustment, PC skill-pool reconstruction and
non-card prose/label decisions remain outside this deterministic plan.

The original Leningrad PDF text layer has broken font encoding; physical pages
were bound through the HTML/QA source-page map, but this pass did not visually
reverify every printed field. Independent source-value/page QA must precede
execution. Next: main freezes the separate generic field-route API, resolves
the finite skill collisions with QA/user authority, runs a dry preflight of this
ledger, and then authors/verifies versioned DOCX successors. No release decision
or acceptance recommendation is issued by this implementer/designer.
