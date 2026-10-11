# Innsmouth MASTER_RU promotion pipeline

Run from `kb_creator/`.

## Preflight the accepted working candidate

```powershell
python -B scripts\freeze_innsmouth_master_ru_repo_input.py --preflight `
  --candidate working\innsmouth_direct_master_ru\MASTER_RU.md `
  --assets inputs\innsmouth\master_en\accepted_20260830_r2\assets `
  --master-en-root inputs\innsmouth\master_en\accepted_20260830_r2 `
  --expected-master-sha256 BAF53B8E20AA91D3124AE83C7D3A533F4D9D16B9F104AB47B93995B048C81FC9
```

The gate verifies the exact user-accepted candidate, moves exactly 16 existing
semantic anchor lines to their corresponding Russian headings, applies only
the recorded Hobby World skill terminology substitutions and the approved
handout and front-matter projections. The front-matter projection adds the
source cover, removes the authors/credits block and follows the Stage C
content-warning suppression. The handout projection suppresses exact body duplicates of
Handouts 1-a and 2, relocates the Handout 2 Keeper note to the appendix,
consolidates Handout 2 to one text block, excludes five decorative handout
crops, and links all eight narrative mentions to the appendix. The gate checks the
canonical English origin, the repository-wide CoC terminology registry, 32 ordered image references and assets, 51
tables, 152 headings, 52 anchors, 86 resolved fragments, and absence of
reconstruction comments.

## Promote

The target must not already exist.

```powershell
python -B scripts\freeze_innsmouth_master_ru_repo_input.py --promote `
  --candidate working\innsmouth_direct_master_ru\MASTER_RU.md `
  --assets inputs\innsmouth\master_en\accepted_20260830_r2\assets `
  --master-en-root inputs\innsmouth\master_en\accepted_20260830_r2 `
  --target inputs\innsmouth\master_ru\accepted_20260830_r2 `
  --expected-master-sha256 BAF53B8E20AA91D3124AE83C7D3A533F4D9D16B9F104AB47B93995B048C81FC9 `
  --accepted-on 2026-08-30
```

## Verify the frozen package

```powershell
python -B scripts\freeze_innsmouth_master_ru_repo_input.py --verify `
  --target inputs\innsmouth\master_ru\accepted_20260830_r2 `
  --master-en-root inputs\innsmouth\master_en\accepted_20260830_r2
```

Success marker:

`INNSMOUTH_ACCEPTED_MASTER_RU_REPO_INPUT_OK`

Verification is fail-closed on the exact acceptance-manifest identity, the
single live registry at
`../CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv`, and the
exact 32-file canonical asset set, including rejection of extra files. The old
glossary path/hash inside the accepted manifest remains historical provenance;
the deleted Markdown file is not a live dependency.

No historical RU v6, cleaned EN v6, `unit_id` bridge, or manual output edit is
part of this route.

## Build the self-contained HTML review package

Run only after the frozen package verifier above passes:

```powershell
python -B scripts\build_innsmouth_html_from_master_ru.py
```

The direct builder re-verifies the accepted RU/EN/system-registry/assets identities,
copies the exact frozen `MASTER_RU.md` and its 32 assets into a generated
working package, and builds HTML from that byte-identical copy. A tested,
deterministic presentation pass groups the TOC into two columns, creates one
source-art title page with the Russian title, marks eleven full-width images,
places the other twenty-one at the right with semantic text wrapping, and adds
a narrow-screen fallback. Credits and content warnings are absent. It does not invoke
historical v6 inputs, rebuild a `KeeperBook`, generate a second TOC, or permit
manual HTML edits.

Default review package:

`working/innsmouth_direct_html/accepted_20260830_candidate_r7f/`

Success marker:

`INNSMOUTH_MASTER_RU_HTML_CANDIDATE_OK`

The build fails closed unless all 52 stable anchors, 86 internal fragments, 32
unique decodable image assets, 51 tables and 22 stat-block cards survive, with
zero broken fragments, missing/unused assets, escaped structural markup or
technical reconstruction comments. An existing target is never overwritten.

r7f was accepted by the user, promoted to
`inputs/innsmouth/html/accepted_20260830_r2/`, and used as the sole source for
the final 46-page PDF. Reproduce and verify the downstream steps with
`../html/PIPELINE.md` and `../pdf/PIPELINE.md`; do not copy or edit generated
HTML or PDF manually.
