# Innsmouth Page Delta Classification

Generated: 2026-07-31

Run id: `20260730T210831Z`

## Current Comparison Snapshot

- comparison status: `different`;
- Keeper reader delta: `7761` chars;
- Keeper reader delta ignoring statblock scaffold: `2324` chars;
- statblock-aware non-statblock delta: `2287` chars;
- statblock-aware statblock delta: `40` chars;
- PDF pages: candidate `27`, reference `32`;
- PDF candidate SHA-256:
  `3e40c0f16759fad087f7ef1c4a739b413ebad5b01e74a983e028201b07e9e52e`.

## Fixed In This Pass

Confirmed OCR/projection residue removed from reader-facing Keeper/HTML/PDF:

- page `006`: removed artificial `### The Innsmouth Terror` heading and
  duplicated `Информация для Хранителя 2 ИНФОРМАЦИЯ ДЛЯ ХРАНИТЕЛЯ` preamble;
- page `012`: split Orne Library research continuation out of the Loring bullet;
- page `017`: removed residual inline `Расследование` before `Díaz`;
- page `027`: removed residual English running heading `The Fire Station`.

Verification:

- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `7 passed`;
- Keeper assembly:
  `status=pass`, `headings=62`, `heading_qa=pass`, `structural_qa=pass`;
- production PDF:
  `status=pass`, `variant=two_column`, `findings=0`.

## Remaining Top Non-Statblock Deltas

| Page | Delta | Current classification | Next action |
|---|---:|---|---|
| `016` | `+277` | Translation/proofread style drift plus possible paragraph-density drift. Headings and art anchor match. | Compare against accepted RU master/source before editing; do not hand-copy reference wording. |
| `018` | `+226` | Partly intentional semantic restoration from previous page-order fix; remaining paragraph/proofread drift. | Verify Bazzledon office sequence against source page and accepted RU master. |
| `006` | `-204` | Header cleanup changed raw delta; page now lacks artificial reader heading. | Check whether remaining difference is legitimate translation/proofread drift. |
| `026` | `+197` | Mostly style/terminology drift after existing section-intro repair. | Verify against accepted RU master; avoid reducing content. |
| `028` | `+193` | Mostly style/terminology drift after existing Order/cave repair. | Verify building/cave sequence against source page. |
| `021` | `+191` | Likely paragraph-density drift; order appears plausible after existing set/rail repair. | Check whether Ginny interaction and railroad-entry trigger match source order. |
| `012` | `+139` | Improved by Orne Library split; remaining drift likely wording plus compacted research sub-items. | Consider universal list/paragraph splitting for skill-result research paragraphs. |
| `017` | `+124` | Improved by residual cleanup; remaining drift is paragraph segmentation and bullet style. | Consider universal paragraph split around `Díaz` briefing transitions. |

## Important Interpretation

Raw character delta is not the acceptance metric by itself. Some fixes restore
lost text or remove artificial headings, which can increase one local page
delta while improving semantic preservation. Continue with page-scoped checks
against the source-derived RU master and source page evidence, not reference
wording alone.
