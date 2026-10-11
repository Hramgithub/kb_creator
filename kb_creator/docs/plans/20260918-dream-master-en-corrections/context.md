# Number 7 Dream MASTER_EN structural corrections context

## Immutable predecessor

- Accepted reconstruction replay: `20260917-cpu-replay-16`, decisions v27.
- Superseded Stage 10 run: `20260918-publication-01`.
- Superseded MASTER_EN SHA-256:
  `4C154262D4BED6688BAB8BB3809DC33A4991AEF5DBD6B90575C5726A78E59945`.
- These trees remain immutable. The current goal creates successors.

## Confirmed origin

Both defect classes already exist in reviewed reconstruction decisions and
Stage 06, so Stage 10 only preserved them.

- Page 10 selected title blocks 137 and 139 carry MinerU v1/v2 strings
  `THE ENLIGHTENEDWEBSITE` and `THE ENLIGHTENEDWELLNESS CENTRE`. The bound
  Stage 04 page visual visibly reads `THE ENLIGHTENED WEBSITE` and
  `THE ENLIGHTENED WELLNESS CENTRE`; MinerU middle evidence also preserves the
  separated line text. Decision v27 copied the glued OCR strings without a
  reviewed correction.
- Page 18 decision v27 contains blank-line runs of lengths 5, 5 and 3 between
  root-level stat blocks. No other page in the 26-page decision set contains a
  redundant multi-blank run. The semantic contract validated block contents
  but did not constrain separators between sibling units.

## Required system boundary

- Fix the reader text in a reviewed decision successor, with exact
  source-to-reader correction notes for title spacing.
- Make selected structural title evidence conflicts fail closed unless an
  exact reviewed correction or exact visual confirmation resolves them.
- Reject redundant consecutive blank lines under the structural profile and
  provide an explicit generic authoring rule that canonicalizes reviewed blank
  separators to one.
- Replay Stage 05/06 and every later identity-bound stage; never edit the
  existing accepted package or MASTER_EN in place.

## C1 architecture closure

`handoffs/c1-architecture.md` is `SPEC_READY`. The complete 26-page audit found
exactly three selected structural-title evidence conflicts: the two defective
page-10 joins and one unchanged page-21 negative control whose hyphenated title
must be explicitly confirmed. The only redundant interior blank-line runs are
the page-18 `5/5/3` separators.

The shared fix uses exact reviewed title confirmations plus the existing exact
text-correction ledger; it explicitly forbids dictionary or uppercase-token
word splitting. Reviewed blank-separator declarations may canonicalize only
exact, uniquely selected intervals, while Stage 05/06 validation rejects every
remaining multi-blank root separator. C2 owns the scenario-neutral reusable
implementation and regression tests.

## Acceptance interpretation

The user's `мастер принят` is held as explicit acceptance authority for the
corrected successor. It is not attached to the known-defective predecessor.
After the successor passes QA, the acceptance receipt must quote the current
task decision and bind the new MASTER_EN hash.

## Corrected immutable successor

- Replay: `20260918-cpu-replay-17`; run identity
  `25CB028CAA183D8BB417E4F48161264505026BD36B10061B3B561E48B1452031`.
- Decisions v28 SHA-256:
  `1C2283E41D6EF3C8502A7D6449ACE3515B8494973C27C94FFA861A2882737E71`.
- Stage 06 `RECONSTRUCTED_EN.md`: 76,460 bytes; SHA-256
  `A1ACDABA98B1A6EA33FE66F5C173EB6BEC97C33A6F2C4762D7375E8479424085`.
- Semantic structure SHA-256:
  `E97E249B8F3048FF639CCE0C0567CA0C279E8D43F0C868587CBECDBE7E39E6F2`.
- Bounded QA: PASS. Exactly 26 pages, 59 units, three title confirmations,
  zero redundant separators, page-18 `5/5/3 -> 1/1/1`, and only reader pages
  10 and 18 differ from replay-16. The asset manifest is byte-identical.
- Accepted reconstruction inventory SHA-256:
  `824F7766AAD4D6B1A9432C28C1C9AA7D6133C65FAF0AF09452F5329BEA2C80DD`;
  acceptance receipt SHA-256:
  `EAA6C97BE105AC6292BC1991A1B16BEF1751D17E26A1441A0C4EE54C685CEBDE`.

Publication run `20260918-publication-02` has run identity
`D9AA819EEA8D1FD0A0CC081201BECA033BCF1903EACF4C16B7AC77E17B45631B`.
Its verified `MASTER_EN.md` is 75,684 bytes, SHA-256
`3AEF660DFAD007448F9F935E762EC4FED7B865773AA8899AC0CBC63DAEAAB7B5`.
The byte diff from publication-01 contains only the two corrected headings and
removal of the redundant page-18 blank lines. Stage QA is PASS and independent
verification is `verified_candidate_pending_process_and_external_gates`.
The user's acceptance is recorded only against this hash; receipt SHA-256 is
`FE3E85C6EEFA993891B3037BB20EFC6238D37292507EDF9B209C8467D59DF73B`.
No Stage 20, translation, release, commit, or push was run.

Focused structural tests pass `167`. Replay/promotion tests report `35 passed,
1 skipped, 2 failed`; both failures are the previously documented immutable
Dissociation replay-10 live fixture rejected on Stage-01 producer-closure
drift, not a Dream successor failure.

Independent C7 review returns `APPROVE_IMPLEMENTATION` with no critical, high,
or medium finding. It confirms that the complete publication-01/publication-02
diff is limited to the intended two headings and three blank-run reductions,
that acceptance binds only the corrected hash, and that Stage 20 and every
later product remain absent. The two Dissociation live-fixture failures remain
low-severity historical debt. This goal is closed at the accepted MASTER_EN
gate; advancing to Stage 20 belongs to a separate downstream goal.
