# Viral production package

This directory is the self-contained production checkpoint. It contains the
editable `MASTER_RU.md`, source-faithful corrected `MASTER_EN.md`, all referenced
assets, `Viral_RU.html`, `Viral_RU.pdf`, `Viral_RU.docx`, QA, asset decisions,
build config and a
pipeline snapshot. To rebuild after a manual Markdown-formatting edit, keep the
asset references unchanged and run from the repository root:

```powershell
python -B kb_creator/scripts/build_viral_production.py --render-only
```

To apply an accepted ArtView review without editing either master, run:

```powershell
python -B kb_creator/scripts/build_viral_production.py --render-only --artview-decisions <accepted-json>
```

To rebuild only the editable Word projection while leaving the packaged HTML,
PDF, masters, ArtView aliases, QA and manifest byte-for-byte unchanged, run:

```powershell
python -B kb_creator/scripts/build_viral_production.py --word-only --artview-decisions <accepted-json>
```

To normalize numbered handout headings in both packaged masters and rebuild
only HTML, while preserving a manually edited Word file and the current PDF:

```powershell
python -B kb_creator/scripts/build_viral_production.py --handout-html-only
```

After exporting the manually edited `Viral_RU.docx` to `Viral_RU.pdf` with
Microsoft Word, validate and register that PDF without rebuilding Word or HTML:

```powershell
python -B kb_creator/scripts/build_viral_production.py --finalize-word-pdf
```

Before that export, an edited Word file must receive the production navigation
and callout semantics without being regenerated from HTML:

```powershell
python -B kb_creator/scripts/build_viral_production.py --patch-word-semantics
```

`--render-only` reads the packaged `MASTER_RU.md` in place; refreshes current
downstream layout policy and the portable pipeline snapshot; then rebuilds
`Viral_RU.html`, `Viral_RU.pdf`, `Viral_RU.docx`, QA reports and the manifest. It never restores
the review-checkpoint source over the edited Russian master.
Accepted ArtView decisions are stored byte-for-byte as both
`ARTVIEW_DECISIONS.accepted.json` and the explicit current
`ARTVIEW_CONFIG.json`, then materialized into `assets/artview/` and the derived
`ARTVIEW_RENDER_RU.md`; subsequent render-only runs refresh that
projection from the editable master and `ARTVIEW_APPLIED.json`. The masters are
never rewritten by this layer.
`--word-only` materializes the accepted ArtView review in an isolated temporary
workspace, builds a temporary HTML projection there, and atomically replaces
only `Viral_RU.docx` in the production directory. The accepted JSON itself may
live in the production package; candidate binaries are resolved from the
bound ArtView checkpoint.
`--handout-html-only` is the explicit exception to master immutability: it uses
the appendix navigation as the canonical EN/RU handout-title registry, rewrites
every anchored handout as one numbered H3 followed by a plain title, refreshes
the accepted ArtView projection and HTML, and verifies that `Viral_RU.docx` and
`Viral_RU.pdf` were not changed.
`--finalize-word-pdf` treats the packaged DOCX as the final layout source,
requires 52 linked TOC entries, 44 linked body cross-references, resolving Word
bookmarks, highlighted review callouts and matching PDF destinations, then
checks page sequence, A4 geometry and empty-page inventory before refreshing QA
and the manifest. `--patch-word-semantics` changes only `word/document.xml`: it
wraps the existing styled link runs in real internal hyperlinks, adds stable
bookmarks, and restores the Innsmouth-style beige/rust callout treatment while
preserving user-edited text, media, headers, footers and section layout.

The PDF/HTML presentation inherits the accepted Innsmouth Terror production
profile (A4 palette and framing, typography, single-column print body, statblock
cards, role-aware art sizing, and atomic full-page art/heading binding). The RU
reader omits the source credits sheet. Viral-specific contents, two-column TOC,
handouts and semantic asset bindings remain declared in `build_config.json`.
The downstream renderer suppresses the three section-local navigation lists
under Player Handouts, Keeper Maps and Pregenerated Investigators, while
preserving ordinary content lists and the numbered Isola map legend. Those
three appendix groups start at the top of a new print page. Production QA also
rejects text-only interior PDF pages shorter than 80 extracted characters, so
a detached two-line tail cannot pass as an intentional page.
