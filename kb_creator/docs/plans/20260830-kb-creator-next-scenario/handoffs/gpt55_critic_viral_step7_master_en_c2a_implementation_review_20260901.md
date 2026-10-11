# Viral Step 7 MASTER_EN C2a independent implementation review

- Review kind: `implementation`
- Verdict: `REJECT_C2A`
- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `7 / C2a structured MASTER_EN executor`
- Timestamp: `2026-09-01T22:10:26.0415460+03:00` (`Europe/Moscow`)
- Role: independent critic, repository policy `gpt-5.5` / `high`
- Actual platform model / effort: `unavailable`
- Implemented or materially designed the candidate: `no`
- Orchestrator policy owner: `/root`, NRI main-chat orchestrator policy `gpt-5.6-sol` / `medium`; ownership did not transfer
- Assignment state: assigned independent C2a implementation review; platform runtime remains `unavailable`
- Scoped override: sole allowed write was this immutable receipt; implementation, config, source/reconstruction, verifier, candidate/output, plan/context/status, MinerU, historical matrices, Git and release surfaces remained read-only
- Release review fields: not applicable; this is not a release review and no frozen release candidate, release manifest, freeze evidence, QA release references or mutation-invalidation decision was reviewed
- Elapsed time: approximately `00:06:11` by active goal timer at receipt drafting checkpoint
- Token use: `156624` active-goal tokens at receipt drafting checkpoint

## Files checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step7_master_en_structured_executor_assignment_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_structured_contract_audit_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_content_viral_step7_master_en_structured_config_amendment_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_plague_monk_termination_remediation_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_remaining_structured_remediation_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_structured_executor_20260901.md`
- `kb_creator/working/viral/master_en/publication_config_v1.json`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- accepted v4 page snippets for pages 58, 59 and structured evidence pages reached through the builder
- live `kb_creator/working/viral/master_en/` directory

## Candidate identity and positive evidence

Live SHA-256 identities:

- `publication_config_v1.json`: `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- `build_scenario_master_en.py`: `72579A69C8F52428808092AFDF8532B9504C468A9A2C4571AEA6D29EADA37672`
- `test_build_scenario_master_en.py`: `4C721410827EFB1E8CCA722D76E3A3F9911FEFF273BE3AFE8D221E1E53EA5F3F`
- Terra final receipt: `D3CF6C1A8AC9C856830F64CFBEA2D2E717C5F9BA1F7F87ADD6BEAF5FAB16116D`

Bounded suite:

```text
python -B -m pytest -q -p no:cacheprovider kb_creator\tests\test_build_scenario_master_en.py
36 passed in 7.37s
```

Independent two-run temporary reader probe:

- identical outputs: `true`
- bytes: `358622` and `358622`
- SHA-256: `17528F1543738CA5FAE1A215237B6F7476A9483B015D1C41889213DFA140B010`
- anchors: `168`
- reader links: `237`
- reader assets: `107`
- structured units: `29`
- class split: `11` semantic tables / `10` semantic cards / `2` semantic statblocks / `6` visual forms
- xrefs: `237` executed ids, `237` unique ids, `41` source links
- conservation: `1935` total / `1862` owned / `73` generated / `0` unowned / `0` duplicate / `0` unauthorized suppression
- representative Rumors fragment: source page `20`, range `[2947,5061)`, source SHA `0E9F7533767E49C87D20E57209DB752ABEF2DD36B30F6D8AB9E22074B0BB1C49`; emitted range `[71175,73278)`, emitted SHA `4436E20E24F9909243133C0079F06E9C46CC64F665CBA31DE8123868BDF708F1`
- Outdoor fragments: p58 root `[1593,1959)`, p58 Cold Spot descendant `[1959,4108)`, p59 root `[26,955)`; emitted order is root, child, root before Hospital
- Reliquae fragments: p66 root `[1319,2303)`, p67 root `[26,1103)`, p67 Infection child `[1103,1308)` and `[1309,1585)`; emitted order is root/root/child/child
- six visual forms each reported `emitted_occurrence=1` with the configured reader asset ids

Config invariant probe:

- `accepted_v4_markdown` occurrences: `0`
- structured rows: `29`
- source units: `33`
- unique structure ids: `29`
- source unit keys: exactly `page`, `path`, `sha256`
- live `kb_creator/working/viral/master_en/` contains only `publication_config_v1.json`; no durable `MASTER_EN.md` or acceptance sidecar was present there

## Findings

### P1-1: attached-note evidence is not part of the resolved source/emitted structured fragments

The assignment requires tables to verify attached notes and to derive source/emitted ranges and hashes from actual final reader text. The current resolver only checks that each configured note text exists somewhere in the raw page:

- `build_scenario_master_en.py:340-341`

The structured fragment itself is built from `start` to `end`, and for record-count pipe tables it is truncated to the configured record rows before note evidence is recorded:

- `build_scenario_master_en.py:315-321`
- `build_scenario_master_en.py:342-352`

Independent probe found nine configured attached notes that are outside their row's `source_start/source_end` and outside the corresponding emitted evidence ranges:

- `viral-structure-rumors` p20 preface note
- `viral-structure-rowing-speed-results` p34 intro note
- `viral-structure-lemon-grove-results` p36 post-note
- `viral-structure-dss-throw-results` p55 three adjacent notes
- `viral-structure-outdoor-encounters` p58 three guidance paragraphs

An isolated negative probe removed the Lemon Grove post-note from the reader text and kept the Lemon emitted ledger self-consistent. `structured_resolver` still passed that row and returned one fragment:

```text
isolated_lemon_resolver_passed_after_note_removed_with_consistent_ledger: true
source range [26,4833), emitted range [139090,143925)
```

This means C2a evidence can say the structure passed while an attached note declared by the contract is absent from that structure's emitted proof. Overall conservation may still retain the note elsewhere, but the 29-row structured evidence does not prove the note as a structured fact.

### P1-2: nested structured schemas remain open for termination and note selectors

The assignment requires exact conditional schema validation and rejection of unknown or missing keys. The implementation closes the top row, source unit, fact and region dictionaries, but it does not close nested `termination` or `attached_note_selectors` dictionaries:

- `build_scenario_master_en.py:249-250`
- `build_scenario_master_en.py:340-341`

Independent mutation probes against the live config all passed declaration validation unexpectedly:

```text
extra_termination_key: PASS_UNEXPECTED
missing_termination_count: PASS_UNEXPECTED
bad_attached_note_shape: PASS_UNEXPECTED
```

Concrete examples:

- adding `junk` to a `record_count` termination passed;
- changing a `record_count` termination to omit `count` passed declaration validation;
- adding `junk` to a note selector passed.

Some later resolver paths may fail after a malformed declaration is executed, but this does not satisfy the requested closed schema contract. It also leaves the positive test suite unable to prove the config language is sealed at the nested fields that govern source and emitted range boundaries.

### P2-1: focused tests miss the two P1 classes above

The current structured evidence tests verify emitted range hashes, missing emitted ledger, owner crossing, changed emitted fragment, visual wrong-owner/duplicate/staged-SHA failures:

- `test_build_scenario_master_en.py:167-194`

There is no focused negative test for:

- an attached note that is missing from the row's final emitted evidence while the table body remains valid;
- extra or missing nested keys inside `termination`;
- extra keys inside `attached_note_selectors`.

The 36-node suite is useful and many negatives are meaningful, but it does not cover these acceptance-critical contract edges.

## Blockers

C2a cannot be accepted while:

1. configured attached notes are not included in, or independently bound to, the row-level source/emitted evidence and can be omitted from a self-consistent row proof;
2. nested termination and note-selector schemas accept unknown or missing keys.

No P0 was found. I did not find evidence of durable candidate creation, verifier mutation, MinerU execution, historical 371/119/490 matrix execution, Git mutation, or release-surface mutation during this review.

## Recommendation

Minimal next action:

1. Update the builder so each `attached_note_selectors` item is closed-schema and is either included in the relevant structured fragment source/emitted range or recorded as its own source/emitted note evidence with exact owner, source page, source range/SHA, emitted range/SHA and occurrence count.
2. Close `termination` schemas per kind, at minimum: `record_count` requires exactly `kind,count`; `line_exact_exclusive` requires exactly `kind,selector` with a closed line-exact selector; `end_of_page` requires exactly `kind`.
3. Add compact negative tests for missing emitted attached note with a self-consistent emitted ledger, extra/missing termination fields and extra note-selector fields.
4. Rerun the compact builder suite and two-run temporary reader probe. Candidate, verifier, MinerU, historical matrix, Git and release gates should remain closed.

Final recommendation: `REJECT_C2A` until the two P1 blockers are corrected and independently rechecked.
