# Number 7 Dream HTML publication regression correction context

## Seed defect

Run09 HTML SHA-256
`D338180EAA3E226882162ED6F85DDAA038149615ABF8324CE5A44234CC273193`
was awaiting user acceptance when visual review exposed the Appendix C defect.
The TOC shows repeated `Предыстория` and `Что ты знаешь о Стэнвике` entries,
while only `МИЛТОН ЛОУ — ПРОГРАММИСТ, 24 ГОДА` appears as a character heading.

The accepted MASTER_EN already contains the malformed tree: Appendix C and
Milton Lowe are level-1 headings; repeated `Background` and `What You Know
About Stanwick` are level-2 headings; the other character names are plain
paragraphs. MASTER_RU faithfully preserves that structure. Therefore the
visible defect is not an isolated CSS problem, and directly editing run09 or
the accepted masters is forbidden.

The user then exposed two additional regressions in the same candidate:

- the publication page currently places `АВТОРЫ И СОЗДАТЕЛИ` and the source
  `СОДЕРЖАНИЕ` inside ordinary body flow, while the generated navigation is an
  unrelated exhaustive heading list; this indicates that the earlier
  frontmatter/source-TOC assembly rules are not reaching the active Stage 40
  configuration;
- Appendix A stat blocks are rendered with the beige quote/callout frame even
  though their semantic type is not a quotation, and several character names
  share a paragraph with the first statistics row. The previous row-preserving
  projection fixed physical line loss but coupled semantic typing to a visual
  callout class, so the fix was incomplete at the renderer boundary.

The active audit must distinguish rules that were implemented only in older
scenario builders, rules present in source config but omitted from the strict
publication adapter, and rules that were asserted only by tests that the
current Number 7 Dream path does not execute.

## Preserved authority

- Accepted MASTER_EN SHA-256:
  `3AEF660DFAD007448F9F935E762EC4FED7B865773AA8899AC0CBC63DAEAAB7B5`.
- Accepted MASTER_RU SHA-256:
  `A96BFEAF5642ACB7524D25DA6551A7916EDD650563887E1781A99BD9E31A9230`.
- All 298 translations and all 19 accepted ArtView decisions must be rebound
  through existing strict successor commands.
- Prior generic Stage-40 semantic projection fixes remain required: page 14 is
  one four-item callout list and page 18 contains seven row-preserving typed
  statblock cards.

## Confirmed root causes and correction layers

The R1/R2/R3 audits prove three independent but coupled failures:

1. **Reconstruction structural completeness.** Pages 21–26 have the repeated
   source-backed grammar `Appendix H1 -> character H2 -> leaf H3`, but the
   accepted semantic sidecar contains no heading units for that grammar. Five
   character titles are plain text, Milton alone is H1, three titles are in the
   wrong reader position, and twelve leaves are H2. Page 18 similarly has seven
   statblock parents but only three title children; four extractor table blocks
   combine title and first statistics row. Existing validation checks declared
   units, not role-required completeness or reviewed intra-block partitioning.
   The canonical correction therefore belongs in Stage 04/05/06, followed by a
   new immutable reconstruction successor.
2. **Publication-policy readiness.** The Number 7 Dream `html.json` was
   intentionally authored at Stage 10 as a future placeholder with no page map,
   source-TOC policy, credits policy, or body start. After MASTER_RU acceptance
   no lifecycle transition required it to become Stage-40-ready. The adapter
   accepted the placeholder, the renderer split its defaults, and conditional
   QA passed vacuously. The correction belongs in the versioned publication
   config/contract and Stage-40 preflight/output closure gates.
3. **Semantic/presentation coupling.** Stage 40 maps sealed `kind=statblock` to
   a Markdown directive that the renderer emits as
   `<blockquote class="review-callout statblock-card">`. The global quote CSS
   then adds the beige background and border. Tests positively asserted this
   wrong DOM and checked only card counts and row breaks. The correction belongs
   in the Stage-40 semantic projection/renderer mapping: semantic kind controls
   a neutral `section/div`, while Markdown `blockquote` remains only historical
   transport and ordinary quotations keep quote styling.

The earlier fixes did not randomly disappear. Frontmatter capability existed
but its required contract was never activated; statblock row preservation was
implemented but its tests canonized the wrong visual container; reconstruction
validation preserved declared structures but never required the missing ones.
These are lifecycle and completeness gaps, so the durable fix must add positive
requirements and fail-closed negative tests at every crossed boundary.

## Successor decision

Directly editing run09, accepted masters, or generated HTML is forbidden. A
Stage-40-only legacy heading migration would be technically possible for the
Appendix C tree, but cannot honestly create the four missing statblock title
decisions because the accepted sidecar has no title/body partition authority.
Since an upstream successor is required for page 18, both upstream structural
defects will be corrected together in reconstruction. The accepted historical
chain remains byte-identical; the new chain receives its own explicit
reconstruction, MASTER_EN, MASTER_RU, ArtView, and HTML acceptance gates.

## Stop conditions

Run09 remains immutable defect evidence. No generated HTML is hand-edited.
No HTML acceptance, Stage 50, DOCX, PDF, release, commit, or push is authorized.

## Implemented systemic closure

Reconstruction now has the opt-in
`reviewed_role_outline_and_partitions_v2` contract. It retains historical v1
support but makes role completeness explicit: a `character_statistics` page
must bind every top-level statblock to one contained first-line title, and a
contiguous `pregenerated_characters` group must have one H1 root, one H2 record
per page, and H3 leaves parented to each record. Exact half-open Unicode source
fragments are mandatory when one OCR block is genuinely divided between title
and body. The fragment validator binds immutable bytes but applies the same
reviewed OCR-correction ledger before comparing reader text. A v1 unit inherited
into v2 keeps an empty partition ledger and the existing whole-source-block
validation; a v2 baseline carries only reviewed selectors and rehashes them
against the fresh packet. Shared implicit splits remain forbidden.

Stage 40 now rejects missing, unknown, or still-deferred HTML publication
policy. The versioned ready contract binds every source page role, exact
frontmatter order, cover, source-authored credits, TOC mode/page/entries, and
body start. It is normalized once for the renderer, then checked again against
the final manifest and DOM. Typed statblocks travel through the derived
`semantic-kind: statblock` directive and render as a neutral semantic section;
ordinary quotations remain blockquotes and the legacy review-callout directive
is a separate compatibility route.

The Number 7 Dream source HTML config is now Stage-40-ready with 26 page roles,
`cover -> credits -> source_toc -> body`, 18 exact linked source contents
entries, and body page 4. A repository regression loads this real config, so it
cannot silently regress to the prior placeholder while generic negative tests
cover missing/deferred/incomplete policy and wrong final link/order/DOM states.

The all-page reviewed decision spec is
`handoffs/T5-dream-v2-reviewed-spec.json`. It preserves unchanged page
decisions, separates four fused Appendix A names using exact byte partitions,
declares all seven statblock titles, and defines the complete H1/H2/H3 Appendix
C tree while moving pages 23-25 titles to their visually reviewed top-of-page
order. Early validation against the byte-equivalent replay-17 Stage 04 passes
26 pages and 82 actual units with semantic structure SHA-256
`B6285C882ACDAE443636F05CE89AA1C758647F790F140D5A12FD19A11BB4F080`.
This is selector smoke evidence only, not the successor candidate.

Focused reconstruction, adapter, and renderer coverage passes `298 passed, 1
skipped, 2 deselected, 5 subtests passed`; the two deselections are the already
documented immutable Dissociation producer-closure fixtures. The real Number 7
Dream config test separately passes in the 15-test adapter file. A replay from
the historical source run correctly refused the changed producer closure, so
fresh full CPU run `20260918-cpu-first-07` was started instead.

That run completed Stage 01-04 with run identity
`33794838D28E86CA5A692308203E64E5EFE9B8B4A414812189D17DF164EB9ED4`.
Its Stage 04 passed the same 26-page/82-unit reviewed spec with structure SHA
`B6285C882ACDAE443636F05CE89AA1C758647F790F140D5A12FD19A11BB4F080`.
After explicit replay eligibility passed, the prefix was copied into immutable
`20260918-cpu-replay-18`, run identity
`61E0C0DBA94BE63BD9D34D069E0D069EDBFFA0D3D2DA7D1825FBD5C31DC7A521`,
bridge SHA
`6F5E189CF196417AF452C4C169C913D798E41427ADE53AB51E7D819B9B445C52`.
Decision set v29 SHA is
`B32E702A09923D1D3F809371B5F87D8DDD002B54A02379F38C0DFA06BCBE575C`.
Stage 05/06 completed with output inventories
`879455A0BFFE4FA5C2E6DDC9D903D61601250669B0CAAD3856E310AF8C761EDC`
and
`8DD8F0250810B9B63AC4B129E3F0073C129B2B441BEE7C32D10A70641C20EB9A`.
The exact state is `candidate_ready_for_reconstruction_qa`; acceptance remains
false. Bounded QA now passes: both sealed inventories and every listed file
hash match, all 29 asset identities are valid, and the reader-text delta is
limited to the reviewed page 18 and pages 21-26 changes. The page 18 title/body
partitions, seven statblock titles, Appendix C H1/H2/H3 tree, and page 24
hard-break group all match the reviewed packet. The early independent critic
found no implementation defect and approved the candidate as reviewable; its
only presentation conditions were the then-missing bounded-QA receipt and
canonical-state update, both now supplied. This does not promote or accept the
candidate. The active gate is explicit user acceptance of this exact
reconstruction successor before any MASTER_EN successor is built.

An interim Git audit is recorded in
`handoffs/T5-commit-scope-audit.md`. It confirms that the fixes are present in
repository-visible scripts, schemas, tests, live declarative config, and
documentation while the generated replay-18 candidate remains correctly
ignored under `kb_creator/working/**`. The cumulative dirty tree has 36
modified tracked files, 22 untracked path entries, and no staged files; it
spans earlier Number 7 Dream goals, so a later authorized commit must use the
dependency-consistent reviewed series rather than blindly staging the whole
tree. No commit or push has occurred.

## Replay-18 review correction

The user reviewed replay-18 and confirmed that the title splits and hierarchy
are better, but rejected the remaining visible quote bars around every
Appendix A statblock and its character name. This exposed a fourth boundary
error in the attempted closure: the v2 sidecar still declared
`kind=statblock, representation=blockquote`, so Stage 06 correctly emitted
`> ### NAME` plus quoted statistics. The later neutral HTML renderer did not
repair the source-level Markdown semantics.

Replay-18 therefore remains immutable rejected-review evidence and is not an
accepted reconstruction. The replacement contract must be v2-only and neutral:
the reader Markdown contains an ordinary ATX title and ordinary statistics
lines, while the sealed semantic sidecar binds the exact containing span.
Stage 40 may derive a paired machine-only transport from that exact span and
the renderer may emit `section.statblock-card`; neither step may reinterpret an
ordinary blockquote as a statblock. Existing source quotations, callouts, and
handouts keep their blockquote representation. A fresh reconstruction
successor and bounded QA are required before the user acceptance gate reopens.

## Neutral reconstruction successor

The v2-only fix is now repository-visible rather than dependent on chat or
manual output editing. `semantic_span` is a valid new-v2 statblock
representation whose reader Markdown must not contain quote markers. Stage 40
accepts only sealed statblock spans with that representation, derives paired
machine-only start/end markers from the exact ranges, and the renderer converts
those pairs into neutral `section.statblock-card` elements. Historical v1
blockquote decisions remain readable, but cannot be authored as new v2
statblocks. Ordinary source quotations remain ordinary blockquotes.

Two fail-closed intermediate replays exposed missing migration branches and
were retained only as diagnostic evidence: replay-19 found that image/heading
conflict resolution did not yet recognize `semantic_span`; replay-20 then found
that a reviewed OCR title downgrade for `Armor: 0` still required old
blockquote transport. Both resolver paths and regression tests were corrected,
and producer-closure drift prevented either partially updated run from
continuing.

Fresh immutable `20260918-cpu-replay-21`, run identity
`25F375E1C76B0A32496C5B06BEA9939F3B1E144288A5A517F6BF324763FB4F84`,
uses decision set v33 SHA-256
`D8701230B489A695C0ED8986E11A23361FF50817181B3A216ED8DDF708525B7B`.
It reached `candidate_ready_for_reconstruction_qa` with Stage 05/06 inventory
hashes `5EA3FBDF18FEE38CCF3E28216B9C4A975AFB9799D23990226D13500F7B54BA44`
and `DA7F14BC5CE9DFF12795DE8A5BC882C21AA9EA2EE88F2B38D507E73B7224760C`.
`RECONSTRUCTED_EN.md` SHA-256 is
`B49F8417007425ADAD6C0ED0A1C6E6625A27ED51C182D9164C8D8AC45324DE2A`.
Automated delta inspection shows that only `page-018.md` differs from rejected
replay-18; it contains exactly seven H3 character names, zero quote-prefixed
lines, seven statblock `semantic_span` units, and zero statblock `blockquote`
units. Combined affected coverage passes `302 passed, 1 skipped, 2 deselected,
5 subtests passed`. Independent bounded QA is PASS with receipt SHA-256
`48FB22F813E3E7D58A9E11152E6346F8B1B8756308571D115BA60EC73D88F097`;
it verified both sealed inventories, all 86 Stage 06 files, all 29 assets, the
single-page delta, and all seven exact span hashes. Acceptance remains false;
MASTER_EN is still closed.

## Replay-21 acceptance and publication run10

The user explicitly accepted the replay-21 `RECONSTRUCTED_EN.md`, repeating the
same acceptance message. The standard promotion control plane materialized the
immutable reconstruction package and recorded
`RECONSTRUCTION_ACCEPTANCE.json` with receipt SHA-256
`A03FA27CD6569ED4F8304BB283E049942AD2DEEC9A772DFCBE28C77E8EDE0ADF`.
The accepted reconstruction inventory SHA-256 is
`27692107ED00C3E4FF5291AD4FB8E88F67F12D7D0BD0015F5709A61EE87FC986`.

The historical publication contract still sealed the old 569-byte deferred
HTML placeholder, so publication preflight correctly rejected it after the
Stage-40-ready HTML policy grew to 4001 bytes. The scenario-neutral contract
author produced the absent successor
`kb_creator/contracts/number-7-dream.publication-v2.json`, SHA-256
`15C62F0FD74D8BD584482D9D5A0565AC41038B5BA1A3E1DBAB2304751B9DA08A`.
Preflight then passed against the accepted replay-21 package.

Fresh `20260918-publication-10`, portable identity
`9B5171862F0D31C2D16EB027EC72442FFA4ADDBC2D9085EA98DEBF0015AAE4AA`,
completed only `10-master-en-candidate` and stopped at
`awaiting_master_en_acceptance`. No MASTER_EN acceptance, Stage 20+, HTML,
DOCX, PDF, commit, or push is inferred. MASTER_EN SHA-256
`C3B4F13E3E43B2422704F1A7BCF61A5CF1762191B474FAAE5C4C4243289367AA`
passed bounded QA; receipt SHA-256 is
`01F3C1C8F10D000E9B8E3F819BFD3E303B96F8FC94FD0954B4BBE31A6ED698C2`.
The verifier proves exact replay-21 projection, page 18 has seven standalone H3
names and no quote-prefixed lines, and Appendix C has one H1, six H2 character
records, and twelve H3 leaves. The source-authored page-3 contents and technical
`source-page` comments intentionally remain in MASTER_EN; final linked TOC and
reader-visible removal of technical markers belong to Stage 40. Explicit
MASTER_EN acceptance is the active gate.

## MASTER_EN acceptance, structural translation rebind, and publication run11

The user explicitly accepted MASTER_EN SHA-256
`C3B4F13E3E43B2422704F1A7BCF61A5CF1762191B474FAAE5C4C4243289367AA`.
Run10 recorded receipt SHA-256
`AC587D4F392B0DB678B08E0D93D449D80F6797FE612025BEC80CF638B666C4C8`
and completed Stage 20. A strict run09-to-run10 translation rebind then exposed
the missing generic case at `unit-00225`: the accepted source payload was
unchanged, but quote and heading frames differed. The implementation now has a
fail-closed `markdown_structure_only` mode. It requires identical normalized
lexical payload and numeric/dice mechanics, applies only the current
blockquote/ATX-heading shell (including a narrowly verified inline stat-title
split), verifies the full current structure signature, consumes every prior
unit exactly once, and records payload hashes in a v2 report. Arbitrary lexical
edits remain rejected. Regression coverage includes quote removal, heading
level changes, inline stat-title splitting, and negative lexical drift.

The code change correctly made run10 stale for further stages. Fresh
`20260918-publication-11`, portable identity
`F5E69D4EB266D1BCC23B97AB88D136D688C76EE37CCCD1156F0A21F1B2FC003A`,
reproduced the exact accepted MASTER_EN bytes and recorded run-local acceptance
receipt SHA-256
`B8A4C42F2D2206F19E578B0DADC6D4EDD01E922DF8521A15533445B5FC4D44E4`.
Stage 20 then rebound all 298 reviewed translations: 273 exact-source mappings
and 25 Markdown-structure-only mappings, with no page joins or unused units.
The sealed rebind report SHA-256 is
`83DD3C9BCA149C986D0B06E6BBA6D710001797A1606D2192FEA2CF77D006F059`;
the 27-batch submission has 298 units, zero validation findings, and seal
`75E7930DF8C92070921544FAC44C8F9B5606E166607B125172645D608201DF5F`.

Stage 21 built MASTER_RU SHA-256
`904133D5057172C404D28F3BCF2A5E4C578304A59382512D1B31FC56AE0FDAB2`
and stopped at `awaiting_master_ru_acceptance`. The standard-library verifier
passes all ten declared checks with no findings; verification seal is
`B0D192434AEBD7304D8417C9ABB4AC404FBA36BEADF4AC9B910CA908D277FD72`.
The complete master_ru test module passes `35 passed, 1 skipped, 54 subtests
passed` when the repository's test-dependency directory is supplied. Direct
inspection confirms seven plain page-18 H3 statblock titles with no quote
prefixes, Appendix C one H1/six H2/twelve H3, and no runs of four or more
newlines. Bounded QA independently passed all three stage inventories, all 298
rebind rows, 24/24 candidate inventory rows, page markers, 19 assets, mechanics,
terminology, and the same page-18/Appendix C structure. Its receipt SHA-256 is
`92A2B4C69E66A810E7B54759FB915284F77D7E4893A20B870F3F3E6FB3AF42F4`.
No MASTER_RU acceptance, ArtView successor, HTML, DOCX, PDF, commit, or push is
inferred.

## MASTER_RU acceptance and final Stage-40 successor chain

The user explicitly accepted MASTER_RU SHA-256
`904133D5057172C404D28F3BCF2A5E4C578304A59382512D1B31FC56AE0FDAB2`.
Run11 then completed the 19-row ArtView bundle by strict rebind from the prior
user-reviewed decisions and completed Stage 31. Its first Stage-40 attempt
failed correctly but exposed a generic adapter defect: page-local English
semantic spans were treated as global Russian line coordinates.

The reusable Stage-40 bridge now validates the accepted MASTER_EN, Stage-20
packet inventory, all translated batches, submission identities and byte-exact
MASTER_RU reassembly. Each semantic span maps through complete consecutive
translation units to the sealed Russian payload range. The seven live page-18
spans map uniquely to `unit-00225` through `unit-00231` and MASTER_RU lines
527-575. The adapter inserts machine-only semantic markers only in its derived
source; accepted masters remain unchanged.

Two later fail-closed attempts exposed separate generic closure gaps. Run12
proved that the renderer ignored the closed `frontmatter_order` and used only
the legacy optional `credits_policy.frontmatter_position`; the renderer now
derives placement from the ordered roles and uses the legacy field only as a
fallback. The renderer file itself is now included in the immutable publication
implementation inventory, so byte drift makes an existing run stale. Run13
then proved that the Stage-40 validator used a non-nesting-aware page regex and
therefore truncated page 18 at the first nested statblock `</section>`. A
stack-based HTML parser now binds every semantic card to its actual page and
validates exact page/order/id while rejecting quote/callout transport and
malformed nesting. Root-cause receipts are `T7c-stage40-frontmatter-root-cause.md`
and `T7d-stage40-statblock-ordinal-root-cause.md`.

Fresh `20260918-publication-14`, portable identity
`8E280A3F4919CBC76A50FA54FBD091FD050DC2CA6CB702027247EF5F81EF2863`,
reproduced the accepted MASTER_EN and MASTER_RU bytes, rebound 298/298
translations by exact source, rebound and validated 19/19 ArtView decisions,
and reached `awaiting_html_acceptance`. `Number_7_Dream_RU.html` is 155,889
bytes, SHA-256
`3F77B38C477D8E137CF22867BA9713EAF6AFD19C8168C07F1E8664E1790D1E21`.
Its manifest flow is `page-001 -> page-002 -> toc:source -> page-004`; it has
18 explicit source-TOC links, 19 resolved local images, seven neutral semantic
statblock sections, zero statblock blockquotes/callouts, and no reader-visible
`source-page` markers or escaped list markers. Appendix C contains six H2
character records with twelve H3 leaves; the leaf headings are absent from the
top source TOC. Stage 50 is absent. Final bounded QA passed all 166
manifest-listed files and the assigned content checks; receipt SHA-256 is
`4B588F952161AC280976250836F02A32FA281D78A56CBA7FD80E4AFA02FEC123`.
The independent gpt-5.5 release review is PASS with no blockers; receipt
SHA-256 is
`6E50AA27263DE8565BA736DCC1E2BCAEFC7927E1CF6BB563B2DF57E04C02C84A`.
The active gate is explicit user acceptance of the exact run14 HTML hash. No
HTML acceptance, DOCX, PDF, commit, or push is inferred.
