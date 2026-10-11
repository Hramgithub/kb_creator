# Viral Step 7 MASTER_EN — structured-content executable contract audit

## Ownership and scope

- Owner: NRI architecture/root-cause role, `gpt-5.6-sol` / `high`.
- Orchestrator remains `/root`; this is a bounded read-only analysis, not implementation.
- The only allowed write is:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_structured_contract_audit_20260901.md`.
- Config, accepted reconstruction, source PDF, builder/verifier/tests, plan/context, candidates/outputs, MinerU surfaces and Git are read-only.
- Other contributors are active in the shared worktree. Do not revert or overwrite their changes. The xref correction may change only the xref portion of config while this audit runs.

## Pinned evidence

- Baseline whole config before the parallel xref-only correction: 717,058 bytes / SHA-256 `314058BEC330D16CC26B4D1D5E3DA07E3C98AFF8B3820AF5ECE2644648FE5D0E`.
- Canonical JSON `structured_content` subtree: 135,802 bytes / SHA-256 `84E740194388A568144FE97E4098855A2F868174D9865DBAAF5C1252E18AE5F2`.
- Builder: SHA-256 `3D84DA82F31CCADAA8EFA831C21CB12DD7C35232A4B7F90E6B6BC215C8009CEE`.
- Accepted reconstruction:
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`.
- Current inventory: 29 rows = 11 `semantic_table`, 10 `semantic_card`, two `semantic_statblock`, six `visual_form`; 23 use `semantic_from_accepted_facts`, six use `retained_complete_visual_form`; 28 unique owners.

## Problem to resolve

C2a currently preserves accepted source spans and reports 29 config-owned rows, but this is only count/placement evidence. It has no dedicated structure-aware verification path. It must not duplicate full-page `accepted_v4_markdown`, regenerate authorial text, or hard-code Viral facts in reusable code.

A fresh representative read-only check also shows that the current fact ledger may not yet be executable as written. For example, `viral-structure-rumors` declares headers `Roll / Result`, while accepted v4 p20 begins the table as `Roll / Rumor`. Several card/statblock `required_fields` are semantic names rather than exact source tokens. The audit must determine the exhaustive gap rather than treating this example as the only defect.

## Required audit

1. Reconcile all 29 structured rows against their exact accepted-v4 page Markdown, resolved assembly owner spans/actions, assets and visual-review declarations. Do not use the selected overlay as reader content.
2. For each of 11 tables, identify the exact Markdown table region(s), exact headers, exact ordered first-column keys, continuation behavior across pages, notes immediately attached to the table and owner anchor. State whether current `fact_expectations` is exact, wrong, incomplete or non-executable.
3. For each of 10 cards and two statblocks, identify exact source heading/field/section tokens and region boundaries. Map every current semantic `required_field`, `required_section` and `ordered_section` to exact accepted-v4 evidence, or mark it unsupported/ambiguous. Preserve source oddities and forbidden-invention rules.
4. For each of six visual forms, prove the owner anchor, source page, reader asset, asset identity, visual-review row and requirement that the complete form is represented exactly once visually without a semantic duplicate.
5. Determine the smallest scenario-neutral executable contract amendment. Prefer exact config-authored selectors/tokens/expected facts consumed by reusable code. Do not propose fuzzy matching, generic snake_case-to-source inference, whole-page reinjection, duplicated crops or a second framework.
6. Specify the builder-side algorithm and compact negative/positive test classes needed to:
   - locate each structure in its already emitted owner block;
   - validate/render it exactly once;
   - preserve the accepted Markdown table/card/statblock rather than re-author it;
   - validate visual forms through their owned reader asset;
   - derive all 29 evidence rows and fail on absent, duplicate, wrong-owner, wrong-order, missing fact or evidence-only visual substitution.
7. Identify any accepted-v4 lexical or reconstruction defect that cannot be resolved without reopening Step 6 or asking the user. Do not silently repair it.

## Receipt requirements

Return `READY_FOR_BOUNDED_AMENDMENT`, `FAIL`, or `BLOCKED` with:

- verified structured subtree identity and note of any concurrent whole-config xref-only change;
- per-row matrix for all 29: id/class/owner/pages/exact region/fact status/representation/proposed deterministic check;
- exhaustive mismatch and ambiguity list with severity;
- exact minimal config schema/data amendment;
- exact Terra implementation boundary and compact test matrix;
- explicit no-duplicate/no-reauthor/no-hard-code/no-candidate statement;
- changed-file list, elapsed time and token availability.

This audit authorizes neither config amendment nor code/test implementation. Its accepted result will be integrated after the active xref-config correction.
