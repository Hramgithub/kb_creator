# Orchestrator audit erratum — Viral Step 6A candidate v2 inventory ordering

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-ai-merge-candidate-v2-audit-inventory-erratum`
- Date: `2026-09-01`
- Owner: main-chat orchestrator (`gpt-5.6-sol`, policy effort `medium`)
- Result: `P2 corrected; candidate bytes unchanged`

## Predecessor and finding

The immutable predecessor audit receipt SHA-256 is
`5D6B9C1B773F6DF1CC46F9A35D366849FD6B05938AEEFF50433E21718DB6C702`.
Independent critic receipt SHA-256
`59CA9BA789CC94710DFCE16C514B77DDC1D67FDA38E4B9ED3DE6017626D798F1`
correctly found that its inventory wording claimed ordinal ordering while the
recorded digest was produced by Windows PowerShell default/culture sorting.

The predecessor digest
`76C4C8599B9321FFCF0983C548A7A2A94D8B3BC259D93E3EF2343CB58DB471B1`
remains reproducible under that culture sort, but is no longer the canonical
portable candidate identity.

## Corrected portable identity

Candidate root remains:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v2`

- files: `373`;
- bytes: `13141502`;
- portable ordinal trailing-LF inventory SHA-256:
  `CC8D4D20CDEDC4EE70B2EB1AAE3CF657DF2BC5DCA82A4E1885EF4675A05997A2`.

The corrected digest is SHA-256 over UTF-8 without BOM, with files ordered by
Python/codepoint ordinal forward-slash-relative path and serialized as
`path<TAB>bytes<TAB>UPPER_SHA256<LF>`, including the final LF.

Read-only recomputation returned exactly `373` files / `13141502` bytes and the
digest above. No candidate, decision, source, code, test, contract, raw/bundle,
Git or production file was changed. This erratum supersedes only the predecessor
audit's inventory ordering wording and digest; all other machine checks and root
artifact identities remain in force.

The reconstruction candidate remains rejected for the critic's two P1 findings
until a successor closes contract-role binding and all numbered handouts.
