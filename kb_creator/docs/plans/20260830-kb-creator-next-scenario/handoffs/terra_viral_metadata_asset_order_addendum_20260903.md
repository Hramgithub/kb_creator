# Terra receipt addendum — safe source-order readiness

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-metadata-asset-order-20260903-addendum`
- Contributor role: `nri-engineer`
- Requested model / effort: repository profile `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `matched`
- Scoped override: `none`
- Timestamp: `2026-09-03T23:05:00+03:00`
- Elapsed time: approximately `00:18:00` (addendum)
- Token use: unavailable

## Scope and result

This immutable correction supersedes only the unsafe placement-ready portion
of `terra_viral_metadata_asset_order_20260903.md`. It changes the scoped author
resolver and tests; it does not change any builder/verifier, source, accepted
reconstruction, candidate, ledger artifact, or Git state.

An exact selected-view text match is now recorded as anchor evidence, not an
automatic placement. The resolver keeps normalized-text-to-original character
coordinates and emits exact UTF-8 character/byte split coordinates. If the
anchor begins inside a coarse event, it returns `needs_event_split` with no
`placement`; only an anchor at event byte zero returns `placement_ready`.
Repeated full-text occurrences inside one event are rejected explicitly.
Only the immediate next eligible comparison text block is considered; the
resolver does not scan arbitrarily farther through pages seeking a convenient
match.

Manifest matching now scopes a visual-region binary by its source page,
selected view, and exact source asset path from the already-bound provenance;
a repeated SHA-256 without that unique scope is explicit ambiguity. Physical
status is derived only from approved `full_page_map` and `physical_page_pair`
ledger membership, including pregen fronts. A nonbinary cover outside such a
unit is no longer misclassified as physical.

The v2 ledger normalizer keeps `owner` as `reviewed_owner_label`; it no longer
represents that potentially human-readable source label as a validated
`final_owner_anchor`.

## Files changed or checked

- Changed: `kb_creator/scripts/author_viral_master_en_v2_config.py`
- Changed: `kb_creator/tests/test_author_viral_master_en_v2_config.py`
- Added: this immutable addendum receipt.
- Checked read-only: the sealed ASSET_MANIFEST/comparison inputs, current
  author event graph, and approved physical-unit ledgers.

## Verification and evidence

```powershell
python -m unittest -q kb_creator.tests.test_author_viral_master_en_v2_config
```

Result: exit code `0`.

New regressions cover preceding prose requiring a split, repeated text within
one event, repeated binary identity on separate source pages, and a physical
pregen-front unit.

Current real-input readiness counts: `placement_ready=16`,
`needs_event_split=50`, `resolved_physical_unit=14`, `ambiguous=13` (`93`
reader rows total). p46 `f0ecf365` now correctly reports
`needs_event_split` before `7. Cremation Pit`, at
`event-p046-000000` UTF-8 byte `177`; it never claims placement before that
whole coarse event. p65/66 and p78 likewise preserve their exact evidence or
explicitly report insufficiency without moving unrelated preceding prose/cards.

## Blocker and next action

The next semantic authoring seam must split only the 50 identified coarse
events at their supplied evidence coordinates, then re-run the resolver and
bind placements only for newly event-boundary-aligned rows. It must use the
existing reviewed p31 city -> p32 boat -> Prologue rule to resolve its two
remaining semantic boundaries, without creating a manual all-art ledger or
falling back to Markdown marker offsets. This remains an engineering readiness
result, not candidate or release acceptance.
