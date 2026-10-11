# Number 7 Dream MASTER_RU and ArtView context

## Accepted upstream and successor lineage

- Original packet run: `20260918-publication-02`; portable identity
  `D9AA819EEA8D1FD0A0CC081201BECA033BCF1903EACF4C16B7AC77E17B45631B`.
- First Stage 21 successor: `20260918-publication-03`; portable identity
  `D72DDD52799A53EB5E5AF5EC483A85C36C9E46DFAA29A1FEDAE9D57C6734B48C`.
- Accepted corrected MASTER_EN SHA-256:
  `3AEF660DFAD007448F9F935E762EC4FED7B865773AA8899AC0CBC63DAEAAB7B5`.
- Run03 MASTER_EN is byte-identical to the explicitly accepted run02
  candidate and has a run-local acceptance receipt SHA-256
  `26BB0E03CDCE0BF6D65017A56BFF3BEEE95FB2867C500366AF1027BB8D86BCF3`.
- Packet manifest: 298 ordered units in 27 batches; 75,153 source
  characters; all current `ru_text` values empty.
- Terminology authority SHA-256:
  `EE84E121E63ECDA3F2165205E8335FD3C68E70CF1DEFE1D00CE6C3FF97EFF3AE`.

## Constraints

- Work only in the current immutable publication run and a new run-local
  submission directory. Do not mutate Stage 20 packets or accepted MASTER_EN.
- Preserve the exact closed batch schema; only `ru_text` may differ from the
  English packet.
- Use the repository terminology authority and generic author/verification
  path. A final-artifact-only edit is invalid.
- User requested both MASTER_RU and ArtView construction, but acceptance
  receipts remain explicit decision gates. HTML/DOCX/PDF, release, commit, and
  push are outside scope.

## Current checkpoint

Run03 Stage 20 is source-batch-identical to run02. A validated submission with
27 batches and 298 units materialized Stage 21 at `awaiting_master_ru_acceptance`;
MASTER_RU is 122,649 bytes, SHA-256
`D001BC19CDD94483596F244BE2F2193980D5C5CF3331E7506857E85DA18AFB17`.
R5 correctly rejected it because generic normalization expanded already
accepted `Вождение автомобиля` to `Вождение автомобиля автомобиля`. Producer
and independent verifier now share the v3 fix and parity regressions; focused
tests pass `45`, with one environment skip/deselection and 48 subtests.

Run03 remains immutable failed-candidate evidence. R6 is polishing a separate
v2 translation payload under
`working/number-7-dream/translation/20260918-master-ru-v2/payloads`, including
residual OCR-concatenated stat labels, English reader labels, and the page-19
Elsie-handout agreement error. The next action is a fresh publication-04 run,
byte-identical MASTER_EN reacceptance, packet/source identity proof, new sealed
submission, Stage 21 rebuild, bounded QA, and independent criticism. At that
checkpoint no MASTER_RU acceptance or ArtView authority existed.

## Frozen run04 candidate

- Publication run: `20260918-publication-04`; portable identity
  `0EEE33BD614D19B968ADF40CA90AF137D7D2D09B491F07356F52BE78EE586950`.
- Byte-identical accepted MASTER_EN receipt SHA-256:
  `3A10D882E8ABDB09BC46F4B16C6FBE7942D78F8D3C08EDA4FF813F79D292D98D`.
- Stage 20 reproducible SHA-256:
  `336DC56396908BD3CB276F02748CCA721B13714A19B56FBD4A8A1AA305BD51CA`.
- MASTER_RU submission file SHA-256:
  `51BCBE2B5DB98D8863222A304113E2DDB200175651C729A71297178484633450`.
- Stage 21 reproducible SHA-256:
  `115862E21557DD72B191CF637ECC9B2D1BA8D2FE03C46FEB2CC04968056F876D`.
- Frozen MASTER_RU: 122,980 bytes; SHA-256
  `A96BFEAF5642ACB7524D25DA6551A7916EDD650563887E1781A99BD9E31A9230`.

Run04 producer QA and independent verifier both pass. R7 bounded QA verifies
the exact 34-unit polish, 27 batches/298 unique non-empty translations, 26
page markers, 19 localized image alt texts, the page-14 quote, seven page-18
stat blocks, page-19 Elsie handout agreement, and page-21-26 compact line
  groups. The prior normalization duplicate and residual OCR/English labels are
  absent. R8 independent implementation/process review returned
  `PASS_WITH_LIMITATION`: the exact candidate is safe to
present for user acceptance, but the repo-local pytest environment lacks
`jsonschema` for one pre-existing schema assertion; focused changed paths,
producer QA, independent verifier, and bounded QA pass. R9 then recorded the
user's explicit acceptance of this exact MASTER_RU hash; Stage 30 and ArtView
were still absent at that checkpoint.

## Accepted MASTER_RU and ArtView successors

The user replied `ну вроде ок` after the exact run04 MASTER_RU was presented.
Run04 recorded that decision against the unchanged candidate SHA-256
`A96BFEAF5642ACB7524D25DA6551A7916EDD650563887E1781A99BD9E31A9230`.
Its first Stage 30 attempt then exposed a generic CLI path-coordinate defect:
a relative run root and an authority path made absolute inside the
context-aware adapter failed only after staging began. The failed Stage 30
tree is preserved under run04 `quarantine/30-artview-bundle`; run04 is not
resumed or treated as current authority.

`publication_resume` now resolves the run root and every authority path at the
public boundary before validation or staging. A regression covers relative
run root plus absolute authority. The full publication-control and ArtView v3
set passes `55 passed, 255 subtests passed` using the repository test modules.

Fresh run `20260918-publication-05` has portable identity
`FB38A19CCC78ED0F7159FF57CD6444D90789E0C53A754D4A0BDFDA6431CAE367`.
It reproduced the accepted MASTER_EN and MASTER_RU byte-for-byte. Translation
rebind mapped all `298/298` units by exact source, with no transformation.
Run05 MASTER_RU acceptance receipt seal is
`40E4EF160D0E9A6D385336EAFD95A594ECE2E77B79D47D0D21488D36CE9B028D`.

Run05 Stage 30 completed with reproducible SHA-256
`A28754049C3F00E45E360C0D8A791C863EB27310BFDC8F688EE973F627DEC9F8`
and stopped at `awaiting_artview_decisions`. Producer QA is `pass`: 19 review
rows over 18 source pages, 38 portable binaries, zero alternatives, all input
bindings and binary identities closed, and no excluded pages. Candidate
manifest SHA-256 is
`57F8D681D94C3E112AD14C497E977645FC74FB3A9622556E9A085262742AB6EF`;
candidate-files inventory seal is
`F2AEA26B5534C20328D603683F020A3FA710124E324143A3AA6339EAA958993E`.
Bounded QA passed the sealed run05 bundle, but live review then exposed a
generic interaction defect not covered by the prior static assertions. The
renderer correctly rejects centered wrapping, while the review UI allowed a
user to select wrapping without changing the centered default; this left the
human-review checkbox disabled. Run05 is therefore superseded as the current
review surface even though its producer artifacts remain valid evidence.

The ArtView v3 generator now enforces the presentation contract in the UI:
enabling either wrap option changes centered alignment to `right`; table wrap
also enables text wrap; disabling text wrap clears table wrap; and explicitly
selecting centered alignment clears both wrap options. The focused ArtView and
publication-control suite passes `55 passed, 255 subtests passed`.

Fresh run `20260918-publication-06` has portable identity
`60B28787BDA98CF13CA271273B748179F167AF4D63B9CBCD8712E65BE8D5A4EC`.
It reproduced the exact accepted MASTER_EN and MASTER_RU, rebound all `298/298`
translations by exact source, and recorded MASTER_RU acceptance receipt seal
`8C6C01DC4A99104928AAD86C906C68D305E433AB5A6F05389BB401291EC23CBF`.
Stage 30 completed with producer QA `pass`, reproducible SHA-256
`2A29D42074CCEC00477858C2D91DD7D71A6396DEF1C7FB2030EDCF0A1339D634`,
ArtView HTML SHA-256
`5E0F8B2FBF4DD0770409C2B55386C6B94CC3E8CA504878E5BF5FC3847E117CA5`,
candidate manifest SHA-256
`8D92D736C3C7D7E508E3FE9767D51CC1B435BDD70E42E0E873B4224B43CC7AF8`,
and the unchanged candidate-files inventory seal
`F2AEA26B5534C20328D603683F020A3FA710124E324143A3AA6339EAA958993E`.

The live run06 review surface restored the user's prior state: 11/19 rows were
explicitly reviewed, and the remaining eight preserved both wrap selections
with automatic right alignment and enabled human-review checkboxes. The user
then completed and exported all 19 rows. Strict accepted decisions SHA-256 is
`6A1326CABEE791FA321E0D2D2651CB1C7BAE9E716D90EB6D492EF54333649F24`;
ArtView acceptance seal is
`F27DC9CE59AD84EE8D0B7135AA2F9E9944E0A1154E4B3725DEC47B11C2AFF647`;
Stage 31 application SHA-256 is
`E4288190482DB16C6E916014B4EDB4CC1EC23B74AE0143C2AA51C2C1D79B663A`.
This goal completed at the accepted ArtView/Stage 31 boundary. The later shared
export-UX change and fresh Stage 40 successor are tracked in
`../20260918-dream-html-candidate-export-ux/`.
