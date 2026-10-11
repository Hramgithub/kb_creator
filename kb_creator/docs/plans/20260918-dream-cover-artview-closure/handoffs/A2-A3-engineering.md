# A2/A3 — ArtView v4 discovery and Stage-40 cover closure

## Receipt

- Goal id: `20260918-dream-cover-artview-closure`
- Step id: `A2-A3`
- Role: engineering assistance
- Policy target: `gpt-5.6-terra`, medium reasoning
- Actual model / effort: unavailable / unavailable
- Assignment state: `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol`, medium
- Scoped override: none
- Scope: scenario-neutral ArtView source-PDF discovery successor, decision/application placement propagation, and Stage-40 explicit-cover validation only. No accepted MASTER, live Number 7 Dream configuration, generated run, release, commit, or push was changed.
- Result: implemented ArtView v4 as a discovery-only profile. It binds the immutable PDF and source identity, inventories every page image XObject occurrence, and has neither authored review rows nor authored page-role mappings. Reconstruction semantics now resolve by exact `RECONSTRUCTION_INVENTORY -> RECONSTRUCTION_MANIFEST -> review.decisions` identities, not a sibling-directory assumption. Each ordinary occurrence becomes a distinct extracted/composited native-image review unit with a clean full-page context render; a matching accepted MASTER_RU asset is the current binary and the native PDF unit is its selectable candidate. MASTER-only assets remain rows. Ambiguous same-page matching fails closed. Only the reconstruction-declared cover becomes a clean full-page composite unit that absorbs its page components. Direct and indirect SMask records remain technical-ledger entries bound to their base owner. Required cover selections expose only the viable included choice. Stage 31 retains placement metadata. HTML policy v2 requires an exact selected cover placement and Stage 40 fails on an absent, ambiguous, stale, or text-duplicating cover.
- Files changed: `kb_creator/scripts/scenario_artview.py`; `kb_creator/scripts/scenario_artview_apply.py`; `kb_creator/pipeline/publication_adapters.py`; `kb_creator/contracts/scenario_artview_profile.v4.schema.json`; `kb_creator/contracts/scenario_artview_decisions.v4.schema.json`; `kb_creator/tests/test_scenario_artview_v3.py`; this receipt.
- Files checked: the A1 root-cause handoff; existing ArtView v3 implementation and schemas; ArtView apply; Stage-40 adapter; translator cover behavior; existing v3 tests.
- Verification/evidence:
  - bundled Python `py_compile` passed for the three changed implementation modules;
  - both new JSON schemas parse successfully;
  - a synthetic raster-backed PDF produced one page and a nonempty complete raw-object inventory using `_v4_raw_inventory`;
  - a synthetic nine-page duplicate-XObject PDF kept occurrences on pages 4, 5 and 9 as three distinct raw IDs;
  - `git diff --check` passed for owned changed files.
- Blockers: the bundled runtime lacks `jsonschema`, so the focused unittest module cannot import (`ModuleNotFoundError: jsonschema`). The new focused test is present but remains unexecuted in this environment. A Python launcher on `PATH` is also unavailable; use an approved project test runtime with `jsonschema` for the full suite.
- Next action: independently review the implementation, then author versioned Number 7 Dream ArtView/HTML configs (including the exact sealed source-PDF identity and `source-cover-page-001` placement), start a fresh Stage-30 run, and present every discovered ArtView row to the user. Do not re-use run14.
- Elapsed time: approximately 70 minutes.
- Token use: unavailable.
- Timestamp: `2026-09-18T15:33:00+03:00`.
