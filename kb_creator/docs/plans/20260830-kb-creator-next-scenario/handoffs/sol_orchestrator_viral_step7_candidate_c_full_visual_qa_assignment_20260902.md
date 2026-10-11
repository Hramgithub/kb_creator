# Viral Step 7 Candidate C — full visual QA

## Role and boundary

- Executor: `gpt-5.6-luna` / bounded QA / high.
- This is execution and direct QA only. Do not design, repair, edit, accept,
  release, translate, publish, commit, stage, push, or run MinerU.
- Candidate C and all inputs are immutable.

## Frozen inputs

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Candidate: `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-c`.
- Candidate `INVENTORY.json` SHA-256:
  `4745E245E754FEA89BCA753C9CD73F1B85C30CE07BFE65C2BF760ED7FF4352F7`.
- Candidate `MASTER_EN.md` SHA-256:
  `F486849BB6A2E8EE860F092C0AE691CD4780A08A8065BFF19C47B3BB0DC461D1`.
- Publication config SHA-256:
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Source PDF SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- QA generator: `kb_creator/scripts/build_master_en_visual_qa_bundle.py`,
  SHA-256 `801450DAC2B41A89607DC52786E3AC06D24231640E2066561961770260F162D0`.
- Generator focused test identity: `A334BE7C35DD609F6D302848B8F4C46D7260ED8399C66EAECFC52C2265075574`.

## Allowed writes

Exactly these two new outputs:

1. Bundle root:
   `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-master-en-candidate-c-visual-qa-20260902-v1`
2. Receipt:
   `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step7_candidate_c_full_visual_qa_20260902.md`

Both were absent when assigned. Everything else is read-only. Do not delete or
clean anything.

## Script execution

From the worktree, after rechecking all frozen hashes and output absence, run:

```text
python -B kb_creator/scripts/build_master_en_visual_qa_bundle.py --candidate-root kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-c --publication-config kb_creator/working/viral/master_en/publication_config_v1.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --output-root C:/Users/BogdanD/.codex/visualizations/2026/08/30/01a05392-3683-7292-b5d5-20ddc8b54a80/viral-master-en-candidate-c-visual-qa-20260902-v1
```

Require the generated manifest to close exactly: 123 candidate assets, 107
reader assets, 91 visual-review units, 107 tiles, 27 contact sheets, 39
priority rows, 39 transported priority originals, and zero generation errors.
Require every manifest path to remain beneath the bundle root and every
transported priority file to be byte/hash/dimension-identical to its Candidate C
source. Require p80 at 1700x2200 / 200 DPI and the candidate text proof `Hey
Marco Babez` exactly once in owner `viral-handout-13`.

## Direct visual inspection

Use `view_image(detail=original)` and record a real observation, not merely an
open result, for every required image:

1. all 27 ordered contact sheets, covering all 107 reader assets;
2. all 39 manifest `priority_assets[].transported_path` originals;
3. the generated p80 source render.

Check completeness, semantic crop, ordering, orientation, aspect ratio,
legibility, duplicates, blank/black/corrupt output, source mismatch and label
agreement. Explicitly record p1 front cover, p80 handwritten `Babez`, and p124
back cover. Confirm all 91 visual-review units are covered by the inspected
assets and special requirements.

## Receipt and verdict

The compact receipt must contain frozen/post hashes, manifest hash/counts,
27-row contact table, 39-row priority table, p1/p80/p124 findings, 91-unit
coverage result, Candidate C immutability, anomalies by P0–P3, and exactly one
verdict: `PASS_FULL_VISUAL_QA`, `FAIL_FULL_VISUAL_QA`, or `BLOCKED`.

PASS requires 27/27 sheets, 39/39 priority originals, p80 and all special
requirements directly inspected with no open P0/P1/P2 defect. Do not fix any
defect. Do not run historical 371/119/490 suites or any unrelated tests.
