# Task packet — Viral v2 B1c4 exact per-asset identity binding

## Governance and ownership

- Goal id: `20260830-kb-creator-next-scenario`.
- Assigned role: fresh `nri-engineer`, canonical `gpt-5.6-terra` / medium.
- Main chat retains orchestration.
- This is the single bounded P1 from the B1c4 rereview, not a redesign.
- Exclusive edit ownership: the same six author/builder/verifier script and test
  files plus immutable receipt
  `terra_engineering_viral_v2_complete_authoring_phase_b1c4_asset_identity_binding_20260903.md`.
- Preserve all unrelated/user edits and immutable inputs. Do not edit canonical
  plan/context/prior receipts, mutate Git, create canonical v2 config,
  candidates, renders, review outputs or downstream outputs. Preserve the nine
  historical candidate/staging roots.

## Bound starting state

- Blocking rereview receipt:
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_implementation_rereview_20260903.md`,
  SHA-256 `D6E741AF31FE81CD5307E370D589CC442A9456149CDFE556C12E58C44499323A`.
- Approved architecture receipt SHA-256:
  `A68A643CEBCF11BFBC3F358A900F3677309C02A8D410AB29B4861D62DAEB6442`.
- Final continuation receipt SHA-256:
  `FD33C9F31C956FAA6A440C6EC7F636112E283B99A7902F718501C183A8DAEC7D`.
- Taxonomy addendum SHA-256:
  `92EA06C32F773B3ECBDAAB0B17BE38E8266E9619C7CEA5DFD32A17E1C3CF9097`.
- Exact current hashes:

```text
author helper   FFE2202E0FC2CB2FCD36FCA802C8484057E714704B734027B6AD25B17F0C9249
author tests    A019999265B17005775D801E4D5DF8E83A540959F402F8837705069C58D7386F
builder         DB1CA64720E8A9525CA5F9483E4EB57444913FF83B6FAD7EAA12777752E2C367
builder tests   DE1CC0AC1A20EF20A47C55F5771BBEA68B8BC67DB1B770D51F6F1F86118941C6
verifier        B5EDA81F746501116F305952F173A05C64192FC15BD1E8CBCFC573FBFED203B2
verifier tests  C357DCB7EAD79F9BAFEE836514466150FFD11954F75C980D4106294AF6F5B7E6
```

Verify all hashes before editing.

## Required remediation

Builder and verifier must each independently recompute a complete expected
declaration for every logical B1c4 `asset_id` from immutable inputs and compare
the supplied declaration field-for-field before visual review.

The per-id comparison must bind, where applicable:

- source page, migration outcome and reader/evidence disposition;
- exact binary path, bytes, SHA-256, media type, width and height;
- provenance discriminator and all subtype fields;
- accepted-v4 manifest row/source asset reference;
- exact Markdown marker/span identity;
- exact comparison view/block index/type/bbox/block hash;
- exact source-PDF render page/identity/MediaBox/CropBox/rotation/DPI/format/
  expected dimensions;
- target/replacement/owner/slot/accessibility obligations already closed by the
  prior graph validator.

Valid evidence is not interchangeable between logical ids. Explicitly reject
copying both a valid `binary` and its matching valid `provenance` from another
asset with the same page, outcome and disposition. Do not solve this with a
single shared author helper or by trusting self-reported ids; builder and
verifier must rederive independently from frozen v1 + accepted-v4 + comparison
+ PDF evidence and retain their own error taxonomy.

Add symmetric public builder/verifier regression tests for:

1. the exact critic pair on page 1:
   `viral-accepted-e1e2aa6964b45037691d92e4faf91dba6bbd411e409dc49c237f6b0e71e6ce85`
   borrowing binary+provenance from
   `viral-accepted-a1d83a711a4b7962110b1ba158b2d610043f1fa836e06458e675373094acd6c1`;
2. same-page/same-outcome borrow in the opposite direction;
3. a Markdown-reference pair borrow where available;
4. a visual-region pair borrow with broad counts unchanged;
5. a provisional full-page declaration/recipe borrow;
6. one-field binary and one-field provenance substitutions, ensuring existing
   earlier gates remain stable.

Every mutation must fail at a B1c4-specific gate in both public validators,
never at visual review. Positive canonical in-memory author output must still
reach the exact visual-review seam.

## Exit gate

- Six-file py-compile passes.
- Expanded author/builder/verifier suite passes; exact count recorded.
- Direct reproduction of the critic's borrowed pair fails early in both public
  validators with recorded errors.
- All earlier critic mutation tests remain green.
- Both frozen-v1 preflights pass with unchanged identities.
- Guarded unmutated public v2 preflights stop exactly at builder
  `v2 visual review coverage mismatch` and verifier `E_V2_REVIEW: coverage`.
- Canonical/temp v2 config, Candidate D, renders/review/downstream outputs remain
  absent and the nine historical roots remain untouched.
- Record final hashes, commands/results and terminal
  `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION_REREVIEW` in the
  immutable receipt.

Fresh independent GPT-5.5/high rereview remains mandatory; engineering evidence
alone does not approve B1c4 or authorize later phases.
