# User DOCX review — 4 October 2026

Goal id: `20261004-user-docx-review`
State: completed. Release state: v02/U8v04 approved within declared scope by independent U9-release-critic-v02; user book acceptance not inferred.

## Objective and boundaries

Account for the user's review of all six latest DOCX files; apply their explicit comment decisions; audit and repair noncanonical CoC skill names in Shadows of Leningrad and missing story artwork in Fear's Sharp Little Needles. Preserve reviewed DOCX and immutable source evidence; create successors rather than overwrite them. No commit, push, OCR restart, new translation, or book acceptance is authorized. After the user confirmed that omitted working data no longer exist, use an explicit reviewed-artifact successor route from the available DOCX/HTML/assets plus immutable original PDFs. Preserve missing upstream provenance as a limitation rather than claim a native replay rebuild.

User additionally authorized old-edition characteristic-number conversion and confirmed `текущие`: all six current reviewed documents, including all26Fear stories, not other NRI outputs. Check source edition per entity; retain already7e values. Apply source-grounded7e names/rules, preserve explicit editorial keep decisions and agree ambiguous conversions separately.

## Role contract

5 October user clarification: generate DOCX only. Neither successor HTML nor
published PDF is built in this goal; PDF belongs to a separate pipeline.
Existing HTML may be read-only evidence. Source-derived image inputs and service
page renders are internal QA evidence, not additional deliverables. U4's
dual-output command must gain an explicit DOCX-only route before authoring.
U8 strengthens ordinary DOCX routes without invoking HTML/PDF production.

Canonical contract: `../../../../docs/governance/nri_goal_governance.md`, current GPT-6 role matrix.
Policy orchestrator: gpt-6-sol / medium; actual platform identity/effort: unavailable; assignment state: platform-unverified; scoped override: none.
Architect: gpt-6-astra / high, bounded artwork/source-dependency audit.
QA: gpt-6-luna / medium, read-only six-document comments and terminology inventory.
Engineer: gpt-6-sol / high, reusable repair only after accepted audit/spec and source availability.
Independent critic: gpt-6-astra / high, implementation/release review once a frozen candidate exists; must not materially design or implement it.

## Plan

| Step | Owner | Dependency | Done evidence | State |
| --- | --- | --- | --- | --- |
| U1 | Orchestrator | none | Live six-document hashes and provenance | completed |
| U2 | QA | U1 | All native comments/replies, skill-name inventory and glossary mappings | completed: U2-qa-v01 receipt |
| U3 | Architect | U1 | Story-art coverage and earliest failing layer; exact source dependencies | completed: U3 receipt and frozen native-art supplement |
| U4 | Engineer / orchestrator integration | U2, U3 | Reviewed decision data, reusable artifact-preserving repair/coverage control and targeted tests | completed within scoped repair API: dual-outputwriterretired; DOCX-onlyreplacement23tests, independent v05 approve_within_scope |
| U5 | Engineer + QA / orchestrator | U4 | Successor DOCX, preserved user replies, source-art/skill checks, rendered-page review | all367pagesvisualpass, QAerratav05/v06captured; threeunchangedcandidates/197ops+effect; final scoped API23tests pass |
| U6 | Independent critic | frozen U5 and U8 implementation | Independent review receipt or explicit acceptance pending | completed: API v05 scoped approval F1-F6; U9 releasev02 approve within exact freeze/declared scope, R1-R4closed after QA v05; no human acceptance inferred |
| U7 | QA + architect | user scope expansion | All-six-book edition/statblock inventory and official7e conversion specification | completed146/146sourcevalues, finiteuserchoices integrated in197ops+effect; oldnon-characteristic mechanics explicitly preserved |
| U8 | Architect then engineer | U3 seed; implementation after U5 | Normal pipeline source-art completeness + edition/terminology gates and regressions | completed within declared boundary: v04 43filefreeze SHA9A948C12, independent QA239tests/14subtests/1preexistingskip,focused48, critic38cases and R1-R4closed/releaseapproved; mandatory future human source/output review retained |

## Initial evidence and dependencies

- Only Fear and Leningrad latest DOCX differ from the transfer manifest.
- Fear: 63 embedded media, 11 original NRI question threads, user replies dated 4 October.
- Leningrad: 24 embedded media, 5 original question threads, user replies in 4 threads dated 4 October.
- Other four latest DOCX match transferred hashes and have zero native comments.
- Expected original `kb_creator/inputs/fears-sharp-little-needles` and `kb_creator/inputs/shadows-of-leningrad-1938` directories are absent. Source/replay availability must be established before claiming a pipeline rebuild or art completeness.
- Original PDFs have now been supplied from the user's named Yandex.Disk folders. Fear is an exact historical-source match: 69,575,583 bytes, SHA-256 `49CDBAD99DDF5535E5911DBB89D11E2E1D0FC7BABD69DADBCE28A80EC9586888`. Leningrad: 2,800,661 bytes, SHA-256 `E8C21B6D0BFBED034E6577C7BE01EE305EBFE480C93F87225B07C12AAFD3F10A`. Historical reviewed masters/replay remain a separate dependency.
- User added explicit glossary freshness verification. After fresh `git fetch origin main`, the canonical CoC CSV is identical to current `origin/main` at `c981f2be45d07d718548cf3e0200f1a3688e68c7`; local SHA-256 `8F6A41A64CA5A90621F6B8C2F3B40B4FE3658D7DE88B0D0A82BF95C1F82E6800`. Actual built-snapshot/current-authority binding remains under U2 audit.

## Definition of done

Every comment decision has a disposition and exact anchor; canonical skill names are checked in the full relevant corpus; story artwork is checked against the immutable original and restored at the failing layer; successors preserve source text and user decisions, pass structural/layout QA, and receive independent review. Missing source inputs are reported explicitly rather than reconstructed from guesses.

For the accepted artifact-preserving route, restore confirmed omitted source artwork into versioned successor artifacts and add source-art coverage checks. The earliest observable omission is before DOCX embedding; the earlier extraction/selection distinction cannot be closed without deleted replay data and remains a documented provenance limitation. This does not require new OCR or retranslation.
