# C3 reviewed successor specifications

- Scope: prepare and validate immutable reviewed authoring fragments for the C1-approved correction contract, then author decisions-v28.
- Result: `PASS`; initial preflight failed because the first spec revision repeated A7 transformations already present in baseline v27, and the corrected delta-only revision passed.
- Correction: every page now retains only `source_page` and its complete A7 `units`; only pages 10, 18, and 21 carry the new C1-approved declarations. Top-level A7 visual assertions, exclusions, and evidence were removed to avoid replaying baseline allowlists.
- Files changed: `c3-pages-01-13.json`, `c3-pages-14-26.json`, and this receipt.
- Files checked: both A7 source fragments, both failed C3 fragments, and the C1 architecture receipt.
- Verification/evidence: both JSON files parse; page sets are exactly 1–13 and 14–26; all 26 `units` arrays equal their A7 source arrays; only the approved target page keys remain; page 10 has 2 patches/4 notes, page 18 has only 3 blank-separator declarations with counts 5/5/3, and page 21 has 1 confirmation note.
- Blockers: none. Live replay-17 validation resolved the exact selector counts.
- Next action: consume the authored decisions-v28 through Stage 05/06 without editing it in place.
- Timestamp: `2026-09-17T22:17:09Z`; elapsed: approximately 11 minutes; token use: unavailable.
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, medium; assignment state: `platform-unverified`; scoped override: none. Orchestration ownership is unchanged.

- Goal: `20260918-dream-master-en-corrections`; accepted contract: C1 architecture receipt.
- Decision-set successor: replay 17 / decisions v28, based on accepted v27 and fresh Stage 04 replay 17.
- Source mappings preserved: pages 1–13 and 14–26, 26 total page records.
- Page 10: exact heading patches for `original_pipeline_txt:137` and `:139`, each paired with a text correction and exact title-evidence confirmation.
- Page 18: exact blank-run selectors declare lengths 5, 5, and 3 between Stanwick/Elsie, Elsie/Regular, and Regular/Heavy; authoring should reduce each to one empty line.
- Page 21: exact unchanged title confirmation for `original_pipeline_txt:309`; the lexical hyphen remains unchanged.
- All other page mappings, semantic units, assets, assertions, and exclusions are copied from A7 unchanged as unit definitions only.
- The first validate-only attempt exposed the repeated-transform problem and
  wrote no decision set. After the delta correction and live selector repair,
  validate-only passed for all 26 pages and 59 units with semantic structure
  SHA-256 `E97E249B8F3048FF639CCE0C0567CA0C279E8D43F0C868587CBECDBE7E39E6F2`.
- The reviewed successor was then authored as decisions-v28; decision-set
  SHA-256 `1C2283E41D6EF3C8502A7D6449ACE3515B8494973C27C94FFA861A2882737E71`.

## Live selector correction

The second validate-only pass reached page 18 and proved that the reviewed
separator selectors must bind the complete root lines, not title prefixes.
The Regular and Heavy `after_line` selectors were therefore replaced with the
exact full v27 lines; the declared blank counts remain `5/5/3`.
