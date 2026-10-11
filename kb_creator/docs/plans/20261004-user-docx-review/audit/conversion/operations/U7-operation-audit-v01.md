# U7 exact Word operation audit v01

Status: planning and preflight evidence only. No reviewed DOCX, source PDF, HTML,
shared CSV, or successor book was changed. The proposed operations are in
[`U7-word-operations-v01.json`](U7-word-operations-v01.json); arithmetic-only
comparisons are in [`U7-derived-diagnostics-v01.json`](U7-derived-diagnostics-v01.json).

## Coverage and authority

- Input Word SHA-256: Leningrad `3E2172AB1CC9C045F9F5F472BF6F664337A06969FEDC786BEB2D8D40459007C8`; Kremlin `6C110ED5E62F29E3FACF97AE3B2D8E515B0066CC1B9F48CCC4D45F09FB3B81A0`. All four original Leningrad native comment/thread parts are hashed in the ledger; Kremlin has none.
- Immutable source PDF SHA-256 was rechecked against bytes: Leningrad `E8C21B6D0BFBED034E6577C7BE01EE305EBFE480C93F87225B07C12AAFD3F10A`; Kremlin `F42B054BB94378A7206CF6688CF6B6CF079606C6F24EE74D2EE5EC8A09C62CA0`.
- Canonical CoC CSV SHA-256 was rechecked: `8F6A41A64CA5A90621F6B8C2F3B40B4FE3658D7DE88B0D0A82BF95C1F82E6800`. Only accepted seventh-edition parent labels and the official conversion table are used; CSV bytes/statuses are unchanged.
- Leningrad source physical 6 states fifth edition; its 15 scenario cards comprise 14 numeric stat records plus the non-characteristic *Люди монолита* object. Five pregen investigators occupy physical 37–41. Kremlin physical/printed 16 proves three old-scale source records and the `CHR` crosswalk, although its exact rules-edition label remains unknown. Physical pages for the 37 Leningrad card fragments come from the read-only HTML `review-page` wrappers and U7 QA inventory. The source PDF text layer has broken font encoding, so this pass did not independently re-read every printed number from that source; source-page/value fidelity beyond the prior QA evidence remains an independent verification gate.

## Proposed operations

The ledger contains 175 non-overlapping exact spans: 146 numeric characteristic
fields (122 Leningrad, 24 Kremlin) and 29 skill-label/context operations in
Leningrad. Each row records book, story domain, entity and entity-heading anchor,
source physical page/edition evidence, source and DOCX hashes, zero-based OOXML
body/table/cell/paragraph/run/text-node path, full before-node hash, before
span/hash, after span, reversal, rule, and any editorial decision. The 15
scenario entries, five investigators and three Kremlin records are all accounted
for. The object card has zero numeric operations by design.
Each exact text node also has one atomic before/after and reverse record in
`node_groups`; this resolves shared-run edits without stale intermediate hashes.

Examples of finite rules:

- Albion `СИЛ: 13 → СИЛ: 65`, `ОБР: 14 → ОБР: 70`; his explicit Luck 75 stays 75. No investigator skill-pool rebuild or NPC Punch adjustment is proposed.
- Reginald and Elena `ОБР: 23 → ОБР: 95`, Mycroft `ОБР: 20 → ОБР: 92`, following the high-EDU table rather than blanket multiplication.
- Ithaqua's source-scale `ВЫН 150 → 750` and `ТЕЛ 100 → 500` stay unbounded. Existing HP 125, MOV 10/100 and DB +8D6 stay source values.
- Kremlin `ХАР: 8/5/12 → НАР: 40/25/60` binds the user's `kremlin-chr-app-crosswalk` decision separately for each named record.
- Katerina and the pythons retain both authorial values through the user's contextual form `Скрытность: 90% при передвижении, 75% при укрытии`; percentages are not merged or redistributed.

Direct labels are restricted to card skill rows and use official mapping/accepted
parent labels. A target specialization such as `Наука (Астрономия)` or
`Искусство/ремесло (Фотография)` does not claim that the standalone local
specialization row became accepted. Percentages remain byte-identical. Attack
descriptions and weapon damage have no label or numeric operation.

## Protected and diagnostic fields

Only allowlisted characteristics are multiplied. SAN/РАС, Luck, HP/ПЗ, MP,
MOV/СКО, DB, armor, attacks, skills, age, income, damage and skill checks are
outside numeric operations. The whole reviewed DOCX hash and comment-part hashes
are preflight inputs, so a successor must show a semantic diff confined to the
ledger, with original package parts conserved where not explicitly edited.

The separate diagnostics compare printed HP with simple `(CON + SIZ) / 10`
arithmetic after conversion; they do not prescribe HP changes. Seven Leningrad
records differ: Katerina +3, zombies −1, moon beast −3, four cultists +2,
Boris +1, gnoph-keh +1, and Leon +1. Creature exceptions and source HP prevail.
Kremlin has no printed HP in these cards; nominal HP/maximum MP are calculations
only. Current or depleted MP is not inferred. No Build, HP, MP, DB, MOV, SAN,
Luck, attack percentage, or skill-pool value is generated.

## Finite blockers and API seam

1. Leon has `Торг 40%` and `Убеждение 40%`; Colin has `Торг 40%` and `Убеждение 32%`. The old Bargain/Persuade pair converges on one modern skill. These four source values are preserved in the ledger evidence; no consolidation or label operation for the two `Торг` occurrences is approved here. Main/QA must record an entity-level disposition.
2. Katerina's `1D6 СИЛ` drain is a characteristic effect, for which `5 × (1D6) СИЛ` is the rule candidate. Word splits this exact string over three text runs (`1`, `D`, `6 СИЛ`); it is listed as a topology blocker rather than silently rewritten across runs.
3. The current DOCX-only revision API requires a native root comment ID on every text operation and resolves an exact paragraph plus one text node. These unannotated stat cards need a separate generic field route using the ledger's body/table/cell/run selectors. Sixteen text nodes have multiple disjoint proposed edits (up to eight in one Kremlin node); the new route must preflight the original node once and apply grouped spans atomically, not sequentially against stale `expected_text`.
4. Boris's unspecialized `Искусство 50%`, exceptional attack labels such as `Захват`, and any NPC Punch balancing or 7e investigator skill allocation remain outside this deterministic card plan. The main QA prose/label pass owns non-card contexts such as Rybin's bodily Stealth check and any knowledge/Idea prose decisions. Current comments, including the user's keeps, and handout quotation text are untouched.

This is not an output candidate or acceptance decision. The next engineering
step is a bounded DOCX-only exact-field API extension after the Fear candidate
freeze, followed by a dry preflight of this ledger, a versioned Word successor,
semantic diff, comment-part preservation checks, affected-page visual QA and
independent review.
