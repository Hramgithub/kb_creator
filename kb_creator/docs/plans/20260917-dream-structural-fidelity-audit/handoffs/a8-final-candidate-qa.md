# A8 final candidate QA receipt

- Goal: `20260917-dream-structural-fidelity-audit`
- Scope: read-only QA of replay `20260917-cpu-replay-15` and decision set
  `20260917-cpu-replay-15-decisions-v26`; this receipt is the only file written.
- Result: **PASS** for the supplied structural candidate checks.
- Timestamp: `2026-09-17 19:11:41 UTC`.
- Elapsed time: approximately 5 minutes.
- Token use: unavailable from the QA runtime.
- Orchestrator policy owner: `gpt-5.6-sol`, medium; assignment state:
  `platform-unverified`; scoped override: none.
- QA role: `gpt-5.6-luna`, low; assignment state: matched when dispatched.

## Files checked

- Replay Stage 05 `outputs/05-fidelity-audit/audit.json` and stage manifest.
- Replay Stage 06 stage manifest and candidate inventory.
- Candidate `RECONSTRUCTED_EN.md`, `SEMANTIC_STRUCTURE.json`,
  `ASSET_MANIFEST.json`, page files 014, 017, 018, 019, 020, and matching
  per-page decisions.
- Replay result plus v26 decision-set hash authority.
- Sealed replay05 candidate and decisions-v12 decision set for identity checks.

## Verification and evidence

- Stage 05 audit reports `passed: true`, `26/26` pages, zero errors. Stage 06
  completed with exit code 0 and status `candidate_ready_for_reconstruction_qa`
  (`acceptance_inferred: false`). Replay-level result remains `needs_review`;
  no acceptance is inferred.
- Stage 06 has 26 page files and `RECONSTRUCTED_EN.md` has 26 source-page
  markers. The semantic sidecar covers 26 pages and all `53/53` declared units
  validate. Audit SHA-256:
  `20AC37EC5ECDAC589B68C1824921B853BDB6397D57C03771F1713A2B2FA06109`.
  Candidate Markdown SHA-256:
  `9A06EB41FD26B80168356335F948E9F41DEEC594771F479296FECB2DD36A9957`.
  Semantic sidecar SHA-256:
  `1D6DA0B73CAC481F064AEB39C7A9B6DAABB60801058A550511740346A1231515`.
- Page 14 has one handout blockquote unit plus its nested unordered-list unit,
  four nested list items, no visible escaped `\-`, and the corrected
  `Don't` / `experiments` / `don't underestimate` spellings.
- Page 17 has three distinct blockquote units.
- Page 18 has seven statblock units, zero reader-facing Markdown images, the
  requested stat/value text, and ten `reference_only` source crops in the
  asset manifest. All ten have stored files at their manifested paths.
- Page 19 has three handout blockquote units and the nested four-item list.
  The corrected `hypnotise`, `SN13 6PG -`, and `I am safe` text is present.
- Page 20 has exactly one reader-facing image.
- The sealed replay05 `RECONSTRUCTED_EN.md` hash remains
  `38B2D376E119D989656223A8909E93D9C295BE9D69CFF1A46B469998702BF72F`;
  decisions-v12 `decision_set.json` remains
  `9E2E529B4ECC2FF98508601D2F713E2A3417B0DAA268BB7B3352DE95F5B20157`.
  Replay15 audit authority matches the v26 decision-set SHA-256
  `89CA64762ECB1049B75BE8B5477591D3B89A225B95CACB19EBE55EB579F1A0E0`.

## Blockers and next action

- Blockers: none within the assigned QA scope.
- Next action: obtain the independent implementation review (A9), then let the
  orchestrator update canonical goal status. Reconstruction acceptance and
  `MASTER_EN` promotion remain pending and were not evaluated here.
