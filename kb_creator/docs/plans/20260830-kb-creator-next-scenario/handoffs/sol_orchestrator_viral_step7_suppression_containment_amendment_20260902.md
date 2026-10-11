# Viral Step 7 — suppression containment amendment

## Decision

The existing suppression `owner_anchor` is the semantic/replacement owner. It
must not be overloaded as the lexical claimant of the raw range. Add required
closed `source_containment` to every authorized suppression:

```json
{
  "kind": "normal_claim | owned_page_unit",
  "claim_owner_anchor": "...",
  "claim_binding_kind": "source_locator | physical_unit | owned_page_unit",
  "owned_page_proof": null
}
```

For N01-N05 only, `owned_page_proof` is:

```json
{
  "unit_ref": "viral-visual-cover-front",
  "review_id": "viral-visual-cover-front",
  "source_disposition_primary_unit_id": "viral-source-page-001",
  "source_disposition_sub_unit_id": "asset-viral-render-cover-front"
}
```

The root `viral` binding is already `owned_page_unit`; do not add a locator or
change hierarchy/source disposition/review/assets. Full-page containment is
derived only from the referenced review's source pages and the exact closed
proof chain.

## Exact 22-row map

```text
N01|owned_page_unit|viral|owned_page_unit
N02|owned_page_unit|viral|owned_page_unit
N03|owned_page_unit|viral|owned_page_unit
N04|owned_page_unit|viral|owned_page_unit
N05|owned_page_unit|viral|owned_page_unit
N06|normal_claim|viral-isola-location-07-cremation-pit|source_locator
N07|normal_claim|viral-isola-location-10-chapel-and-crypt|source_locator
N08|normal_claim|viral-isola-location-13-temple-of-morbus|source_locator
N09|normal_claim|viral-isola-hastalyk-awakens|source_locator
N10|normal_claim|viral-epilogue-cinematic-ending|source_locator
N11|normal_claim|viral-epilogue-cinematic-ending|source_locator
N12|normal_claim|viral-epilogue-expanded-ending-new-epilogue|source_locator
N13|normal_claim|viral-appendix-new-rules-the-sight|source_locator
N14|normal_claim|viral-appendix-new-rules-paranormal-phenomena|source_locator
N15|normal_claim|viral-appendix-new-mythos-horrors|source_locator
N16|normal_claim|viral-appendix-new-mythos-horrors-plague-monk|source_locator
N17|normal_claim|viral-appendix-new-mythos-horrors-plague-monk|source_locator
N18|normal_claim|viral-appendix-new-mythos-horrors-reliquae-infection|source_locator
N19|normal_claim|viral-appendix-new-mythos-horrors-reliquae-infection|source_locator
N20|normal_claim|viral-handout-01|physical_unit
N21|normal_claim|viral-handout-14|physical_unit
N22|normal_claim|viral-handouts-hyeons-ipads|source_locator
```

N08/N15/N17/N19 are intentional cross-owner rows. Assembly deletes from the
source claimant span while replacement identity remains validated against the
semantic owner. Generated bindings never satisfy containment.

## Closure

Builder and independent verifier must prove `22 = 17 normal + 5 owned-page`,
`4 cross-owner`, `0 generated`, `0 unproven`; exact containment, occurrence,
hash, non-overlap and proof-chain equality are fatal invariants. Candidate
provenance records both owners, binding kind, exact ranges/hashes, nullable
proof, source/applied/reader/replacement occurrences and replacement identity.

This amendment authorizes only the 22 config object insertions plus the already
assigned four code/test files and the existing remediation receipt. Candidate,
source, accepted v4, hierarchy, assets, prior receipts, Git and downstream stay
read-only. Existing dot-staging roots are not deleted.
