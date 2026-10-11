# Viral Step 7 MASTER_EN C2a review remediation — engineering handoff

- Timestamp: `2026-09-01T22:16:36+03:00` (`Europe/Moscow`)
- Role: reusable code/test engineering, `gpt-5.6-terra` / `medium`
- Orchestrator policy owner: parent `/root`; ownership did not transfer.
- Assignment state: `PASS_C2A_REMEDIATION`; bounded implementation evidence only, not candidate authorization, C2a acceptance, or a release decision.
- Scoped override: writes were limited to the builder, its focused test file, and this receipt. Publication config, source/reconstruction package, verifier, candidate, plan/context, critic receipt, MinerU, historical matrices, Git, and release surfaces remained read-only.

## Scope and result

Remediated exactly the two P1 findings from `gpt55_critic_viral_step7_master_en_c2a_implementation_review_20260901.md`.

1. Nested structured schema is now closed per termination kind:
   - `record_count`: exactly `kind`, `count`, with positive integer count;
   - `line_exact_exclusive`: exactly `kind`, `selector`; selector exactly `kind`, `text`, with `line_exact` and nonempty text;
   - `end_of_page`: exactly `kind`.
   Every attached-note selector is now exactly `kind`, `text`, with `line_exact` and nonempty text. Unknown and missing nested keys fail in declaration validation.
2. Each attached note produces separate row-level `attached_notes` evidence. It records the truthful binding owner, source page/range/SHA, final reader emitted range/SHA, and owner-block emitted occurrence. Resolution is fail-closed for missing, ambiguous, cross-owner, altered, or duplicated notes. The existing structured table/card/statblock fragments remain unchanged; note facts were not deceptively widened into their table-body hashes and no source prose was reauthored.

The exact current config contains `11` attached-note selectors across seven structured rows; this corrects the critic receipt's textual count of nine. All 11 now resolve with `emitted_occurrence=1`.

## Files changed

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- this receipt

Read-only config identity remained:

```text
CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3
```

Implementation identities before this remediation:

```text
builder 72579A69C8F52428808092AFDF8532B9504C468A9A2C4571AEA6D29EADA37672
tests   4C721410827EFB1E8CCA722D76E3A3F9911FEFF273BE3AFE8D221E1E53EA5F3F
```

Final implementation identities:

```text
builder 2851993F8E0B7420706E38E3E781744375826A8E77886E3FB4B632D519FA79AF
tests   96460BE29C094AB7C2B3FBAF9A8E6C472C73619527856F53805DDE35D85D7B07
```

## Verification and evidence

Focused command:

```text
python -B -m pytest -q -p no:cacheprovider kb_creator\tests\test_build_scenario_master_en.py
41 passed in 8.78s
```

The compact added coverage includes extra termination key, missing `record_count.count`, malformed note selector, and missing/altered note output with a self-consistent local emitted ledger. Existing actual-fragment, visual owner/duplicate/SHA, Outdoor root/child/root, xref, conservation, and two-build checks remain green.

Two fresh `TemporaryDirectory` reader builds were byte-identical:

```text
358622 bytes
SHA-256 17528F1543738CA5FAE1A215237B6F7476A9483B015D1C41889213DFA140B010
```

Retained topology/evidence:

- `168` anchors; `256` emitted source fragments; `29` structured rows;
- classes: `11` semantic tables / `10` cards / `2` statblocks / `6` visual forms;
- `107` reader assets; `237` links and executed xref ids; `41` source-link segments;
- conservation: `1935` total / `1862` owned / `73` generated / `0` unowned / `0` duplicate / `0` unauthorized suppression;
- all 11 attached-note evidence entries have occurrence exactly one.

Representative note evidence: the p20 Rumors preface is truthfully bound to `viral-one-night-in-perla-exploring`, with source range `[2752,2946)` SHA `5687729C36B6CE0EA6626849529CABE19862137BA2AA3E0E8844E7E8559BC375`, final reader range `[70921,71114)` SHA `508E98AB7BFF43658E836D90A37B0DB6E2ED7684379DA010E51EB858EB780094`, and emitted occurrence `1` in that owner block. This demonstrates why the note cannot be falsely attributed to the later Rumors table binding.

No candidate, durable output, verifier edit, MinerU execution, historical `371/490` matrix, or Git mutation was performed.

## Blockers and next action

No blocker remains within the assigned files. The orchestrator should request a fresh independent critic C2a review over this remediation before any candidate work, acceptance decision, or release gate.

Elapsed time: approximately 20 minutes for this remediation pass.

Token use: unavailable.
