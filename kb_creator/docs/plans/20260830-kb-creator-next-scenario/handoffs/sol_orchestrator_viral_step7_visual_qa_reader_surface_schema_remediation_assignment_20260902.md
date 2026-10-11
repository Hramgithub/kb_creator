# Viral Step 7 visual-QA generator — reader-surface schema remediation

## Role and scope

- Engineer: `gpt-5.6-terra` / medium.
- Root cause is closed: the visual-QA generator exact-key validator predates the
  required top-level `reader_surface` object and rejects the current frozen
  publication config before output creation.
- This is a narrow reusable QA-tool repair, not Candidate C repair or content
  design.

## Frozen evidence

- Candidate C `INVENTORY.json` SHA-256:
  `4745E245E754FEA89BCA753C9CD73F1B85C30CE07BFE65C2BF760ED7FF4352F7`.
- Candidate C `MASTER_EN.md` SHA-256:
  `F486849BB6A2E8EE860F092C0AE691CD4780A08A8065BFF19C47B3BB0DC461D1`.
- Publication config SHA-256:
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Current generator SHA-256:
  `801450DAC2B41A89607DC52786E3AC06D24231640E2066561961770260F162D0`.
- Current focused test SHA-256:
  `A334BE7C35DD609F6D302848B8F4C46D7260ED8399C66EAECFC52C2265075574`.
- Luna blocked receipt SHA-256:
  `47E5F054909A1F8F5CDB13BF6F50C56E4F47326CB9DA793ACF0D23F3B0E2B0BD`.
- QA bundle root remains absent.

## Allowed writes

1. `kb_creator/scripts/build_master_en_visual_qa_bundle.py`
2. `kb_creator/tests/test_build_master_en_visual_qa_bundle.py`
3. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_visual_qa_reader_surface_schema_remediation_20260902.md`

Everything else is read-only. Do not generate a real bundle, inspect images,
edit Candidate C/config/plan/context, run MinerU, build a candidate, or touch
Git state.

## Required minimal implementation

1. Preserve exact top-level publication-config closure, adding the required
   `reader_surface` key rather than relaxing to a subset check.
2. Validate `reader_surface` is an exact five-key object:
   `schema_version`, `heading_policy`, `semantic_fragments`,
   `authorized_suppressions`, `alt_policy`.
3. Require `schema_version == kb_creator.master_en_reader_surface.v1`, exactly
   25 semantic fragments and exactly 22 authorized suppressions. Keep all
   existing config/source/candidate/asset/visual checks unchanged.
4. Update synthetic fixtures to the current schema. Add negative regressions
   for missing `reader_surface`, unexpected nested key, wrong schema version and
   wrong 25/22 counts. Preserve two-run determinism, candidate immutability and
   priority-original transport tests.

## Verification and result

Run only `py_compile`, the focused generator test module and scoped
`git diff --check`. Do not run historical or unrelated suites. Write a compact
receipt with changed file hashes, commands/results and either
`PASS_QA_GENERATOR_SCHEMA_REMEDIATION` or precise failure. The next action on
PASS is a fresh Luna/high execution of the still-absent Candidate C visual-QA
bundle root; Terra must not perform that run.
