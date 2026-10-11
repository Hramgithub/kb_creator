# Dissociation publication run12 HTML visual QA

- Role: main orchestrator, read-only browser QA
- Date: 2026-09-15
- Run: `20260915-publication-12`
- Run portable identity: `A1BCCE994201F479057F97195894CD7E9455D5C1BD22507EE1E622679DFA00DA`
- Candidate: `outputs/40-html-candidate/artifacts/Dissociation_RU.html`
- Candidate bytes: `62801`
- Candidate SHA-256: `4AED240DBA16BC99E5EFEFCEF6759DA0944CB340FEBFE8D747F456012E74299A`

## Evidence

- Production report: `status=pass`, `headings=21`, `source_pages=6`,
  `image_refs=2`, `missing_image_refs=0`, `statblock_cards=1`, `findings=0`.
- The exact current candidate was served locally from its Stage 40 artifact
  directory and inspected through a read-only browser session.
- Final stat-block heading count: `1`.
- Final stat-block card count: `1`.
- Preserved hard breaks inside the card: `10` `<br>` elements.
- Both images completed loading and reported non-zero natural dimensions:
  cover `1526x2129`, Alaska map `1359x1326`.
- Document horizontal overflow: `false` (`scrollWidth=487`,
  `clientWidth=487`).
- Focused viewport inspection of the final page shows one heading and one
  compact stat block; the run11 duplicated visual presentation and loose
  spacing are absent.

## Verdict

The run12 HTML candidate is ready for explicit user review. This QA does not
infer or record user acceptance. DOCX remains closed until the user explicitly
accepts this exact HTML candidate.
