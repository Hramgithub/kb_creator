# U7 — bounded edition-conversion specification

Status: architect proposal for integration, not an implementation or release approval. Scope: only the six current reviewed books in `deliverables/latest/MANIFEST.json`, including all 26 Fear stories. Orchestration stays with `/root`; entity enumeration belongs to U7 QA. No OCR, retranslation, source edits or skill-point redistribution.

## Evidence and authority

Primary conversion authority: [Chaosium, Conversion Guidelines](https://www.chaosium.com/content/FreePDFs/CoC%207/CHA23135-Conv%20-%20Call%20of%20Cthulhu%207th%20Edition%20Conversion%20Guidelines.pdf), 10 physical pages; physical 3–8 correspond to printed 390–395. Web-parsed primary text was inspected. An attempted local download failed with connection refused; no local official-PDF hash or successful visual screenshot is claimed. This is not an input blocker because the relevant table and rules were readable through the web source.

Local input identities and exact paths are recorded in `evidence.json`. The canonical terminology CSV has 426 rows: 94 accepted, 332 review_required. No CSV entry/status was changed. Source edition and source game rules are not inferred from a terminology-row status.

Priority for this successor route: explicit user editorial decision > edition-specific primary conversion evidence > source-specific exception > generic local conversion defaults. A user keep decision creates a documented intentional exception; it does not authorize silently dropping the decision to obtain mechanical consistency.

### Compact official-rule extraction

| Physical / printed | Rule facts |
| --- | --- |
| 3–4 / 390–391 | Characteristics ×5; half/fifth floor. EDU: 18→90, 19→91 … 26→98, 27+→99. Luck/HP may remain; no repeated aging. Build added. |
| 4 / 391 | Negative DB: −1D4→−1, −1D6→−2. Existing MOV permitted. Investigator skill pools exclude old bases. |
| 5 / 392 | Detailed NPCs may use investigator conversion; sparse NPCs use creature guidance. NPC Punch −25 percentage points; combat amalgamation considers attack values. |
| 6 / 393 | Creature DB/HP/armor/MOV retained; characteristic effects ×5. Attack counts/special effects require description. |
| 7 / 394 | Old characteristic multipliers: 1→extreme; 2–3→hard; 4–6→regular; 7–8→regular+bonus. Resistance→opposed. Idea/context and skill modifiers require judgment. |
| 8 / 395 | Poison POT: 1–9 mild, 10–19 strong, 20+ lethal. Tome Mythos total retained. |

Official skill-map facts, physical5/printed392: Conceal/Pick Pocket→Sleight of Hand; Hide/Sneak→Stealth; Bargain/Debate/Oratory→Persuade; Natural History→Natural World; Photography→Art/Craft(Photography); science subjects→Science(specialty); unarmed/knife skills→Brawl; Rifle/Shotgun→Firearms(Rifle/Shotgun).

## Conversion contract

Each proposed operation must bind `book_id`, `story_id`, `entity_id`, document SHA-256, part/paragraph or table/cell path, exact before-text/hash, source PDF SHA-256 and physical page, source edition evidence, entity kind, current field scale, rule ID and after-value. Do not bind by a name alone. Duplicate mentions of one entity need separate occurrence IDs and a common entity ID. Store editorial-decision references alongside every affected entity.

The planner returns one of `keep_7e`, `convert_deterministic`, `keep_editorial_exception`, `keep_source_value`, `pending_choice`, or `insufficient_evidence`. An unresolved row cannot be represented as an approved conversion. Each input occurrence must have exactly one disposition. Zero replacements, multiple matches, stale hashes, or overlapping operations are hard failures before output generation.

Edition is an evidence field, not a numeric heuristic. An explicitly 7e creature with STR 5 remains 5. A source book can contain intentionally mixed material; record an entity-level override only with evidence. A reader may already contain converted fields although its original PDF is older: classify every field's present scale before multiplication. A second application must produce no further transformations.

### A. Deterministic characteristic and dependent-check branch

The numeric characteristic allowlist is exactly STR/CON/SIZ/INT/POW/DEX/APP/EDU and their accepted Russian labels СИЛ/ВЫН/ТЕЛ/ИНТ/МОЩ/ЛВК/НАР/ОБР. It excludes skill percentages, SAN/РАС, Luck, HP, MP, MOV, armor, damage dice, income, age, poison POT and attack counts.

For proven old-scale ordinary characteristics, multiply by five once. For investigator/human EDU, use the exception table above; never emit EDU95 from source EDU19. Nonstandard creature EDU, ranges, fractional source values or source contradictions need an explicit rule decision rather than applying an investigator cap blindly. Other characteristics may exceed 99.

Half/fifth fields, when included, derive from the resulting value; preserve the book's compact statblock style. They need not be added to every sparse creature. Do not manufacture mandatory new table columns solely to satisfy the generic local reference.

Bind characteristic-dependent mechanics separately: old `МОЩ × 3` becomes a hard check, not `new МОЩ × 3`; old `СИЛ 16` resistance target becomes opposed СИЛ80. These conversions alter a rules expression, not prose meaning. A literal current 7e threshold or a skill percentage is not an old characteristic multiplier. Unsupported multipliers and ambiguous resistance parties stop that row. Preserve the original expression in audit evidence.

For an explicit old characteristic loss/gain, retain the exact distribution as `5 × (old dice expression)` unless the user approves an approximation. Do not multiply ordinary weapon damage or SAN loss. Turning a special attack into a newly designed maneuver, changing its frequency, or approximating its dice is outside deterministic numeric conversion.

Knowledge/Know Roll and Idea Roll fields are check thresholds, not ninth/tenth characteristics. Never multiply their printed percentages. Proposed check binding: when source evidence establishes an ordinary old Knowledge=EDU×5 check, its 7e educational check uses the converted EDU (including the EDU>18 branch), not the obsolete percentage; an exceptional printed threshold or user keep decision requires a separate disposition. Intellectual-puzzle Idea uses INT, while an investigation-stall Idea remains the distinct contextual check. Do not globally replace every occurrence of «Идея» with «ИНТ».

QA's interim reports older creature/deity characteristics50/100/150: these are not evidence of7e scale. Conversely an existing7e Fear SIZ630 is not to be multiplied. The value range is not the classifier. Legacy Russian «ХАР» is not an automatic alias of any allowlisted field until the corresponding source characteristic has been established; if it binds APP, use НАР and the APP rule. Keep unknown meanings unresolved.

### B. Derived fields: source-preserving default, not character regeneration

Project design for this bounded repair: keep existing source HP, current MP, SAN, Luck, MOV, positive/zero DB, armor and attack limits unless an exact accepted operation says otherwise. Record `keep_source_value` or the explicit editorial exception. Formula differences become diagnostics, not automatic corrections. Missing maximum MP can be derived from POW only if the source field means maximum, not depleted current points. Missing HP can be derived where authorized and entity semantics are ordinary; never overwrite a creature's exceptional HP.

Add missing Build from the local table only with a fully bound STR/SIZ and no source exception. Existing unusual DB/Build pairs need review. Negative legacy DB conversion belongs to human/investigator modernization; creature retention guidance can conflict with it, so a negative creature DB remains a finite entity-level decision. The local table above STR+SIZ204 was not independently reverified in this task; if QA finds such a missing Build, bind a full primary rulebook reference before adding it.

Do not reroll Luck, reset SAN to POW, recalculate age effects, add default skill baselines to spent percentages, or regenerate an investigator's occupation. MOV comparison order, if a new ordinary human MOV is explicitly requested, is: both greater→9; both less→7; otherwise→8; then separately authorized age/special rules. Retaining a printed MOV avoids accidental changes from this overlapping-table implementation trap. A missing ordinary-human attacks-per-round default of1 is an enrichment, not proof the original attack structure had been wrong; preserve source exceptions and do not apply that default to creatures.

### C. Skill names are not characteristic numbers

Direct official mappings can be implemented as localized label changes without asking whether the official correspondence exists. Use accepted targets: Ловкость рук, Скрытность, Убеждение, Естествознание, Ближний бой (Драка), Стрельба (винтовка/дробовик), Искусство/ремесло and Наука. The ordinary specialization translation «Фотография» is proposed under the accepted parent label; do not claim the standalone review_required Photography CSV row is accepted.

Preserve source percentages for one-to-one label repairs. Before many-to-one mapping, collect all same-entity inputs. Do not use maximum, average, sum, last-wins or a deduplicating dictionary silently. Equal-value collision may become a single displayed value only with provenance for every input and preserved attack descriptions. Different values or distinct situational actions require a finite explicit entity row.

The official human-NPC Punch balancing and combat amalgamation are skill-value mechanics, not authorization to change characteristic numbers. They remain proposed choices if actual QA rows require them. Subtraction means 25 percentage points, not 25 percent relative. A proposed sparse-human-NPC combat calculation adjusts eligible Punch first, then selects the highest eligible attack value for common Fighting; it does not overwrite separately limited or exceptional attacks. Do not apply it to a pregen PC, other creature attack, already7e attack, or below25 value without a resolved rule. Do not amalgamate a named exceptional attack merely because the label includes a weapon.

Investigator skill-pool reconstruction requires old/new base values, allocation decisions and player/keeper choices. It is not needed to perform authorized characteristic conversion and is not silently included. Re-labeled retained percentages must be described honestly as a bounded compatibility adaptation, not a fully rebuilt 7e investigator skill allocation.

## Local-reference conflicts and disposition

| Local reference behavior | U7 disposition |
| --- | --- |
| Blanket EDU ×5 | Override for human/investigator EDU>18 with primary table; investigate nonstandard creature EDU. |
| HP mismatch treated as error | Distinguish an approved preserved legacy value from an arithmetic defect. |
| Derive/require all MP/DB/MOV fields | Separate maximum/current, ordinary/exceptional and absent/present fields; no silent regeneration. |
| Recompute creature DB/MOV | Preserve source-specific creature values; record exceptions explicitly. |
| Missing attack count→1 | Restricted ordinary-human fallback; creature attacks need source description. |
| Any 3–18-looking number is suspicious | A heuristic may nominate a row, never decide its edition or apply ×5. |
| MOV table overlapping ≥ and > conditions | Check both-greater branch first; otherwise strict inequalities can incorrectly return8 instead of9. |
| Legacy CSV keys review_required | Official direct mappings resolve correspondence for this task, without mutating canonical CSV status. |

The official wiki secondary-attributes page linked by the local reference is a simplified creation reference, not a replacement for the primary conversion guide. Its uniform human MOV8 must not be used to invalidate the fuller local comparison table. This task changes neither shared reference nor CSV: orchestrator may separately approve a focused reference/test update.

## Source-bound seed: Albion Fitzgerald

Original Leningrad physical6/printed5 explicitly identifies fifth-edition rules and pregenerated player characters. Physical41/printed40 shows Albion's investigator sheet and second-person player history. The source PNGs beside this file were rendered directly without OCR and visually inspected.

| Field | Printed | Deterministic 7e candidate |
| --- | ---: | ---: |
| СИЛ | 13 | 65 |
| ВЫН | 12 | 60 |
| ТЕЛ | 12 | 60 |
| ИНТ | 16 | 80 |
| МОЩ | 14 | 70 |
| ЛВК | 10 | 50 |
| НАР | 14 | 70 |
| ОБР | 14 | 70 |

Source Luck75 is also an explicit user keep decision: preserve75, not POW70. Source SAN70, HP12 and DB+1D4 remain. Source Conceal20 and Sneak40 bind to distinct target skills; they do not collide with each other. Fist/Punch70 is not evidence for an automatic NPC70→45 patch: Albion is a pregen investigator. This is a diagnostic worked seed, not the all-six inventory or an approved document edit.

The source's skill-difficulty note includes +10 and −25 modifiers. Do not turn these into bonus/penalty dice by numeric substitution. A context-aware decision may be needed if that mechanic is to be modernized. The characteristic conversion may proceed independently of unresolved skill-modifier redesign, with the residual compatibility limitation listed.

## Finite questions and integration gate

Do not ask the user to reconfirm direct Conceal/Hide/Sneak/Bargain mappings. Orchestrator should ask only for actual unresolved rows returned by QA, each with book/story/entity/page, old action/values, two concrete alternatives and recommended retention default:

1. Different old skills collapsing to one target: retain labeled source-specific values as a disclosed compatibility exception, or approve a stated consolidated value and rule route. Do not ask this for Conceal versus Sneak, which have different targets.
2. Actual pregen PC skill reconstruction: retain source percentages with mapped labels (bounded default), or authorize base-point accounting and a separately approved allocation. No occupation or skill-point pool is generated in advance.
3. Actual sparse human NPC combat collision: retain source attack percentages/limits, or approve stated Punch adjustment plus eligible combat merge. Provide exact numbers from QA, not hypothetical entities.
4. Contextual Idea checks, misuse of Conceal for bodily hiding, non-table legacy synonyms, skill modifiers, source ranges, or exceptional creature mechanics: show the exact passage and finite proposed handling. Do not freeze a guessed value.

There is no need to block deterministic field conversion on an unrelated deferred skill redesign. There is a need to block a claim of fully normalized7e mechanics while unresolved rows remain. QA inventory is the remaining dependency for the exact number and content of user choices; this architect has not duplicated that inventory.

## Acceptance criteria for engineering and independent QA

- Coverage ledger contains all six manifest books and all26Fear story IDs, including no-change7e dispositions. Every statblock and characteristic-dependent prose occurrence has an edition/scale decision or explicit unresolved status. Document-level7e metadata alone cannot hide an uninspected exceptional older inset.
- Synthetic cases cover known7e STR5 unchanged, oldSTR13→65, EDU18→90/19→91/26→98/27→99, INT22→110, mixed-scale rows, unknown edition hold, source range hold and a second-run no-op.
- Protected-field tests keep Luck75, SAN70, legacy HP13 when permitted, depleted MP, creature MOV/armor/DB, user reply strings, attack limits and non-characteristic damage untouched.
- Check tests distinguish oldPOW×3→hard from a 7e percentage and skill40; old resistanceSTR16→80; half65→32 and fifth65→13; characteristic drain1D3→5×1D3 only in the bound effect.
- PC Punch70 must never enter the NPC-balancing route. Any contemplated NPC adjustment is separately authorized and tested. Many-to-one different values hard-stop without a decision; one-to-one label edits preserve percentages.
- Snapshot hashes/before-context must match; zero/multiple anchors fail; tables, paragraphs, comments/replies, tracked revisions and relationships remain structurally preserved. No generic global regex replacement of numbers or short labels.
- Successors are versioned, originals remain unchanged. Validate textual semantic diff against the operation ledger, then render affected statblocks/pages for clipping, table damage and comments preservation. Record explicit residual exceptions rather than passing a superficial keyword check.
- No release claim in this artifact. Independent critic who did not design this repair reviews a frozen candidate after U5 QA; any post-freeze mutation invalidates that review.
