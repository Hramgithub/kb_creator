# Viral v2 builder typed-chunk ledger receipt

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-builder-typed-chunk-ledger`
- Contributor role: `nri-engineer`
- Requested model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `incomplete_serializer_composition_refactor`
- Scoped override: none
- Timestamp: `2026-09-03T02:00:00+03:00`
- Elapsed time: approximately `00:03:00`
- Token use: unavailable

## Exact residual

The current v2 route serializes directly to a string and subsequently removes/relocates asset markers by string composition. It has no typed top-level or nested chunk collection from which final ranges can be accumulated. Any attempt to add final offsets now would need to search the finished Markdown, which the assignment explicitly forbids and which cannot safely disambiguate repeated reader text.

This packet requires replacing the current serializer/materializer boundary with a typed composition ledger that owns event chunks, nested structured children, list relocation and join-time offset accumulation. That refactor must also regenerate provenance and expand the synthetic fixture tests atomically; partial range fields would not satisfy final-slice, overlap, suppression or determinism requirements.

No builder/test/config/source/reconstruction/real candidate/Git/Step 8A path was modified. The next action is a dedicated implementation pass for the serializer-composition refactor, after which the ledger acceptance tests can be run.

Completion token: `INCOMPLETE_V2_TYPED_CHUNK_COMPOSITION_REFACTOR`
