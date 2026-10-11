# U7 focused two-book closure — QA evidence

Goal `20261004-user-docx-review`; read-only U7v02 scope. This closes exact prose and label occurrences in the current Leningrad and Kremlin reviewed readers; it does not implement conversions or determine final acceptance. Machine ledger: [`U7-two-book-closure.json`](U7-two-book-closure.json).

## Input identity and coverage

| Book | Current DOCX SHA-256 | Immutable source PDF | Source SHA-256 / size | Coverage |
| --- | --- | --- | --- | --- |
| Shadows of Leningrad | `3E2172AB…59007C8` | `D:/яндекс/Yandex.Disk/НРИ/1_Зов Ктулху/temp/1938 Тени Ленинграда/5_Shadows of Leningrad, 1938.pdf` | `E8C21B6D…AAFD3F10A` / 2,800,661 bytes | 1,156 Word paragraphs; 49 physical pages / HTML page ids 001–049; source explicitly 5e |
| Secrets of the Kremlin | `6C110ED5…FB3B81A` | `D:/яндекс/Yandex.Disk/НРИ/1_Зов Ктулху/temp/тайны кремля 1931/2_Secrets of the Kremlin, 1931.pdf` | `F42B054B…09C62CA0` / 978,872 bytes | 275 Word body paragraphs; 21 physical pages / HTML page ids 001–021; physical source p16 establishes all 3 NPC records on old 3–18 scale |

The current DOCX hashes were freshly checked. The exact Kremlin edition label remains unavailable, but scale is not ambiguous: source p16 matches every current field for Potapov, Ivan, and Nikolai. `ХАР` is not claimed to intrinsically mean APP; current user choice explicitly authorizes `ХАР→НАР×5` for these three records. No card text is duplicated from the v01 statblock inventory.

Coverage was a complete paragraph extraction of both current Word bodies plus focused term/context review against the known source/page crosswalks and all existing card inventory rows. It found two Leningrad non-card door thresholds and one Kremlin non-card POW roll-under instruction. Targeted English/Russian term searches also distinguished true skill contexts from narrative homonyms. The source PDFs yield no extractable text for the searched Russian terms in the bundled PDF text pass, so this was not represented as fresh OCR, exhaustive visual examination, or a rendered visual QA. Previously verified source pages are cited per row in the JSON ledger.

## Characteristic-dependent prose/checks

| Exact Word/source anchor | Finding | QA disposition |
| --- | --- | --- |
| Leningrad Word ¶305; source physical p18 / printed p17; HTML `018` | Locked door `СИЛ двери равна 10` and explicit `Таблица сопротивления`. | Old threshold: candidate 10×5=50; conversion guide route is opposed STR, not old Resistance Table. No edit. |
| Leningrad Word ¶347; source physical p20 / printed p19; HTML `020` | Ward door `её СИЛ составляет 16`; context is breaking the locked door; sentence does not repeat Resistance Table wording. | Candidate 16×5=80; proposed opposed STR route follows characteristic-dependent door check context. No edit. |
| Kremlin Word ¶146; source physical p6 / printed p5; HTML `006` | Accreditation instruction repeatedly says roll against / at or below `МОЩ`; no ×3 appears in this text. | Not a numeric characteristic field. Do not silently infer POW×3 or hard check from this paragraph alone; source-rule binding remains necessary. |

Other characteristic-dependent expressions found are inside existing card rows, not duplicated here: Leningrad vampire card Word ¶368 has `1D6 СИЛ` blood loss; ¶369 compares POW against POW and against the Resistance Table. Preserve the exact loss distribution and bind the resistance conversion through the approved spec. Investigator sheet Idea/Luck/Knowledge values are check fields, not additional characteristics. No SAN, HP, MP, Luck, MOV, damage dice, or attack counts are recommended for multiplication.

## Skill labels in actual skill/stat contexts

Leningrad labels and their exact field locators are fully enumerated in the JSON. Direct correspondence is grounded in the conversion-spec official table: Bargain→Persuade, Hide/Sneak→Stealth, Conceal/Pick Pocket→Sleight of Hand, Natural History→Natural World, unarmed attack skills→Brawl, and Art/Photography→Art/Craft. Retain every printed percentage; no investigator pool reconstruction or modifier-to-dice rewrite is proposed.

- Word ¶89: `Подкрадывание −20%` (Peter) → Stealth; keep −20%.
- ¶284: `Сокрытие −10%` to lift a document; ¶402: `Сокрытие −10%` to take items → Sleight of Hand; keep each −10%.
- ¶290: `Сокрытие +10%` to enter Rybin’s office bodily unnoticed → user-approved contextual Stealth; keep +10%.
- ¶693: `Подкрадывание +10%` approach and `Прятаться +10%` behind cover → same target skill, but preserve both distinct conditions and checks; keep +10% for both.
- Card skill rows: Katerina ¶371 and enchanted pythons ¶447 `Бесшумное передвижение 90%, Укрытие 75%` → user-approved `Скрытность: 90% при передвижении, 75% при укрытии`; retain both source percentages. Ghast ¶481 `Подкрадывание 70%` → Stealth.
- Boris Churin ¶669: Art 50, Bargain 30, Hide 20 → Art/Craft, Persuade, Stealth respectively; preserve values.
- Investigator sheets, exact fields and values: Masters ¶816/817 Bargain71, ¶828/829 Fist55, ¶840/841 Natural History75, ¶850/851 Sneak20; Sterndale ¶889/890 Bargain40, ¶899/900 Fist50, ¶919/920 Sneak30; Boothe ¶946/947 Art(Painting)85, ¶948/949 Art(Ventriloquism)30, ¶956/957 Fist55; Palmer ¶994/995 Bargain40, ¶996/997 Conceal25, ¶1008/1009 Fist55, ¶1012/1013 Hide30, ¶1030/1031 Photography13; Albion ¶1055/1056 Art(Painting)85, ¶1057/1058 Conceal20, ¶1063/1064 Fist70, ¶1077/1078 Photography30, ¶1081/1082 Sneak40. Preserve rates, and do not rebuild skill points.
- Elena Orkonova ¶770 is explicitly an `Оружие` attack list (Fist40, Kick60, Headbutt50, Grapple35, Staff45); keep as attacks, not investigator skill-sheet labels.

Kremlin exact skill rows are Potapov ¶265 (Russian100, English80, German70, Architecture90), Ivan ¶270 (Russian100, English70), and Nikolai ¶275 (Russian100, English60). Preserve labels and values pending the two grouped questions below.

## Remaining finite questions (2)

1. **Language parent fields in Kremlin:** decide own-language versus other-language presentation for the three Russian NPCs. Current exact labels/rates stay untouched until assigned; the text does not establish each intended 7e field explicitly.
2. **Potapov Architecture90:** choose an accepted 7e target label or retain the source label/value as a scoped legacy exception. The local CSV row is `review_required`; this audit makes no glossary change.

No further choice is required for Photography: the supplied official mapping supports Art/Craft(Photography) in both investigator sheets, while the local standalone Photography CSV row remains `review_required` and unchanged. No issue is resolved by guessing. This receipt recommends no implementation until the orchestrator binds the two outstanding groups and conversion operations to exact successor anchors.
