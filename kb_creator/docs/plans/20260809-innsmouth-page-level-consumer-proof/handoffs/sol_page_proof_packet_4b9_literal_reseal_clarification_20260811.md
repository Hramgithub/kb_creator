# Sol Architecture Clarification — Packet 4b.9 Literal Reseal

## Immutable handoff receipt

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.9-literal-reseal-clarification`.
- Role/effort: Sol architect / requested `high`; actual platform model and
  effort: `platform-unverified`.
- Orchestrator policy owner: `gpt-5.5` at `medium`
  (`platform-unverified`). Orchestration ownership remains with the main chat.
- Assignment state: `platform-unverified`.
- Scoped override: `none` for role ownership. This receipt is a narrow
  architectural clarification of the accepted 4b.9 specification; it does not
  override orchestration, implementation, independent criticism, acceptance,
  or release ownership.
- Result: **the P1 literal-generation ambiguity is resolved.** A bounded
  executor and a fresh critic may deterministically reproduce and verify all
  new private P/W/V/F literals without live input, hidden authority,
  production activation, a public route, or Git.

## 1. Clarification decision and precedence

This receipt supplements
`sol_page_proof_post_4b8_inventory_reseal_spec_20260811.md` and supersedes only
the conflicting procedural reading of its sections 3.3, 5.8, and 7:

1. Starting the confirmed Python interpreter for the offline procedure below
   is allowed. The existing `subprocess` prohibition means that neither the
   procedure nor implementation/tests may import or call `subprocess`, spawn a
   child process, or invoke another tool.
2. Before the final mandatory `py_compile` and `pytest` commands, the executor
   may run the exact deterministic stdin/stdout literal procedure in section 3
   and its section 5 oracle. A fresh critic may independently repeat them.
3. These invocations are development calculations only. They create no
   authority and are not acceptance evidence by themselves. The two accepted
   4b.8 child identities, the literal inventory contract, the domain-separated
   seal formulas, the committed final literals, and independent tests remain
   the complete authority chain.
4. Every other 4b.9 restriction, file boundary, twelve-test requirement,
   exact `159 passed` count, and fresh independent Terra/high implementation
   review remains unchanged.

If a result from this receipt's table, the independent formula, the production
system under test, or the final literal bytes disagrees with another, the
executor must stop and write a blocker receipt. No result may be selected by
preference or silently regenerated from a different source.

## 2. Allowed temporary mechanics

The executor and critic may each use the confirmed
`D:\NRI\.tools\python-3.13.14\python.exe` only after re-confirming its path and
`Python 3.13.14` version. The calculation command shape is:

```powershell
@'
<the exact section 3 procedure, transcribed without semantic changes>
'@ | & 'D:\NRI\.tools\python-3.13.14\python.exe' -B -
```

The temporary calculation has this closed capability set:

- current working directory: repository root;
- static imports: `hashlib`, `json`, and
  `kb_creator.tests._page_proof_fixture_leaves` only for literal generation;
- inputs: the frozen `_page_proof_fixture_leaves.py` constants, the exact
  fixture/stage-authority metadata already literal in the accepted tests, the
  new inventory content digest
  `4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4`,
  and the unchanged expected-output hashes;
- output: stdout only, consisting of canonical W/V byte literals and the
  checkpoint rows in section 4;
- persistence: none. No redirection, `tee`, temporary file, cache file, source
  edit, generated module, environment mutation, or retained transcript is
  permitted. `-B` is mandatory;
- forbidden inside the calculation: `open`, `pathlib`, `os`, environment
  lookup, globbing, filesystem discovery, `eval`, `exec`, `compile`,
  `__import__`, `importlib`, dynamic import/plugin, production/public API,
  production root, monkeypatch, parser, renderer, PIL, OCR, network, browser,
  subprocess, live/source/output/configuration/build/Git/release path, random,
  clock, locale, or platform-dependent input.

The stdout may be copied only into the already allowed final test literals.
The final candidate must contain no generator, builder, import/call in
`_page_proof_fixture_leaves.py`, runtime-derived expected value, or reference to
temporary output. Intermediate partial literals must not be presented as a
candidate or tested as if complete; the seven-file identity replacement is one
atomic working-tree edit before final verification.

## 3. Exact deterministic literal-generation procedure

Define exactly:

```python
def C(value):
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

def H(raw):
    return hashlib.sha256(raw).hexdigest()
```

Use exactly four ordered cases:

1. `two_column`: current `WITNESS_TWO_COLUMN_V1`, unchanged
   `RENDER_PNG_TWO_COLUMN_V1`, current
   `INDEPENDENT_VISUAL_CROSSCHECK_TWO_COLUMN_V1`, and the existing two-column
   fixture/stage-authority/expected-output metadata.
2. `nested_form`: the corresponding nested-Form literals and metadata.
3. `visual_only`: the corresponding visual-only literals and metadata.
4. `two_boundary`: current `WITNESS_TWO_BOUNDARY_V1`, unchanged two-column
   render, current `INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1`, and the
   same fixture/stage-authority/expected-output metadata as two-column. This is
   evidence-only and must not become a fourth admission-registry row.

For each case, perform only these ordered operations:

### A. Pre-visual binding P

Construct this exact ordinary dictionary from literal inputs:

```text
fixture_id
fixture_id_byte_length
fixture_id_sha256
stage_a_fixture_id
stage_a_authority_content_sha256
required_topology_inventory_content_sha256
render_png_byte_length
render_png_sha256
witness_schema = "kb_creator.pdf_raw.PageProofWitnessV3"
visual_crosscheck_schema =
  "kb_creator.pdf_raw.IndependentPageVisualCrossCheckV2"
```

Then compute:

```python
P = H(b"page-proof.fixture-pre-visual-binding.v1\0" + C(p_payload))
```

### B. Witness W

Decode only the current literal W with `json.loads`. Change exactly these JSON
paths, in order:

```text
required_topology_inventory_content_sha256 = new inventory content digest
pre_visual_binding_sha256 = P
content_sha256 = H(C(root without content_sha256))
```

Serialize `W = C(root)`. Record `content_sha256`, `len(W)`, and `H(W)`. Assert
that a recursive before/after path diff, excluding `content_sha256`, contains
exactly the first two paths and no semantic path.

### C. Mechanics/flow evidence M/E

No M/E bytes are generated. The pre-visual summary payload excludes topology,
P, W content seal, and W leaf identity. Therefore each case's
`pre_visual_evidence_core_sha256` must remain exactly the value in section 4.
The final production normalizer test must independently recompute and compare
it; copying the old value without that comparison is insufficient.

### D. Visual cross-check V

Decode only the current literal V. Assert its
`pre_visual_evidence_core_sha256` equals section 4 and its decision-inventory
seal equals section 4. Change exactly:

```text
required_topology_inventory_content_sha256 = new inventory content digest
pre_visual_binding_sha256 = P
content_sha256 = H(C(root without content_sha256))
```

Serialize `V = C(root)`. Record `content_sha256`, `len(V)`, and `H(V)`. Block,
boundary, and decision-inventory seals do **not** change because their sealed
payloads contain none of the migrated identity fields. They must be
independently recomputed and proved equal, not rewritten to a new value. Assert
that the recursive before/after path diff, excluding `content_sha256`, contains
exactly the first two root paths.

### E. Final binding F

Create `f_payload` by taking the exact P payload and adding only:

```text
pre_visual_binding_sha256 = P
witness_byte_length = len(W)
witness_sha256 = H(W)
independent_visual_crosscheck_byte_length = len(V)
independent_visual_crosscheck_sha256 = H(V)
```

Then compute:

```python
F = H(b"page-proof.fixture-admission.v2\0" + C(f_payload))
```

`expected_candidate_sha256` and `expected_reviewed_ledger_sha256` are not in P
or F and remain unchanged/unconsumed. The procedure prints `repr(W)`, `repr(V)`,
and one section 4 checkpoint row. It performs no write.

## 4. Complete reseal checkpoint table

These values are a published independent reproduction oracle, not a substitute
for the accepted child identities or formula checks. All values are lowercase
SHA-256; lengths are exact canonical-byte lengths.

| Case | P | W content | W len | W leaf SHA | M/E pre-visual core | V decision inventory | V content | V len | V leaf SHA | F |
| --- | --- | --- | ---: | --- | --- | --- | --- | ---: | --- | --- |
| two-column | `cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d` | `172ae571a4da210c0f8cdd5faf4e82bbf1fe9e718448a89369ce38250d9a6594` | 3050 | `d08e02060ccb8a602a445cc14f0e71fd16fbcf1616d826463e00c64f46948295` | `3e53b5eaf8f8aa2630e831f12ae9606abba85e2db1d64eea974ff9da258903b6` | `74786992475a388ee82ecd8d9084fdd875b88f215c5d5a243366e625fe4299c5` | `d38f51bba2b575528a32b572084b12ba2be33060e972ad7138a70eee9d580f73` | 2501 | `2c358a6feb63859fa2f4c10346bd64e26da13f1e6d64f7cce5a868f881cab2c5` | `0c45fd6b6440482b377fbcd3c6797701e622250dc0fdd496d18dbef81cd48838` |
| nested Form | `388f7cc61345dbbcb516a4090e0d35cabb308f37137bf9b6b86c691fbf6c122c` | `aa95cc4c1ec640b9644e4febfb3e1d6f729be64b4544849ae5a9ffd4fd2c63e0` | 2927 | `c488c0491139d27e696b5ab4ea4205b5ada0a9f577e3c3a23231868469eb85c3` | `997a208c30acc7bc9c2c91031096bf656734c2f2529c4818951853f305a17bb5` | `14f10b2512f755eb1205d0dade5bd396f85f5163aafd5916ddcd50e5dc9ae2d5` | `f332b60fd1107f66ccff5e497a071f8438be9dc4d5e1e6c22734b9abbb6dbc97` | 2084 | `887aba071a09620cdc4789a5635ba57661eff0eec0792ad50db66af3a2d4f0d3` | `249d56182c4710e6392740703ed86d388b714498d1bbc9c60e403de0caf0fbf2` |
| visual-only | `7f9327e3dba8c5ad888efa3423115e779b0bb0502438e7ddd9c02cd2c43dbea2` | `0d9b5d5faf83844591daaf8b2b471c2c03564653e47769b45ea0abef0167fb39` | 2125 | `68d22df7ade83daa01348bcd25dc90ec69a9f0efe73b9f6f0bb0b9cfe379fb2e` | `f7ee0ef14756eccdf2bdcfd9df727a800a118834f6c373f2892a4b394888ab65` | `5881a4328628ba26fd80b9dfcf73ebbc40895896bb126d87a467efb7cdd94f26` | `7995e65505d53305ff53811e0221b64496d93bf8b8a29a753d9683d0c1ac2f1f` | 1461 | `1e47e656240499dcc6d2c1e25a64691fe99c02d9801b6f52b2f8cc80993f1c76` | `4d9c98331427c55f788ee2fc532365434054e6d300236120fc11946c7894aecd` |
| two-boundary evidence | `cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d` | `7d014e1cdb5ce542936a91b28615cc86f508208ec3a190dba84a990dd145e86d` | 3186 | `e468e847f15c602d80808b572332978da2cd87eaa0009d766ae484ada80d1677` | `2115d29b5c221e814c53fcd800b1083427c91653622b469ea657e476c118bdb7` | `ef0c615876bd325e2b5252d482a1092e1f685a37dc5a9051e44778988b2dce6c` | `9083762bc843dacf0937f809809a8c82a4eed96326a7eb2dfab9870bb8d4aef0` | 2928 | `761fc6aca16af4972d31081f4ad620f7f369c0c984c972f411ce196e4a95a2f4` | `afd101e900a5242cf0c7867102272997e719ea3f183c5e096d0e5c1c826c522e` |

P is intentionally equal for two-column and two-boundary because their P
payloads are identical and W/V are outside P. Their W/V/F values differ.

## 5. Independent test oracle and required tests

The new twelve-test module remains exactly as specified. Its oracle layer must
add no test count and must obey all of these rules:

1. Define private test helpers `C` and `H` from section 3 using only stdlib
   `json` and `hashlib`. They may be called only inside tests, never at import
   time to create expected literals.
2. Declare the inventory primitives, section 4 table, three final admission
   primitive tuples, and Packet 4b.7 semantic baselines as direct literals.
   They must not be derived from production objects, helper output, a receipt
   parser, the generation stdout, or one another.
3. Within the existing twelve named tests, independently recompute:
   both entry hashes, both inventory hashes, every P, W content/leaf/length,
   unchanged M/E core, every V block/boundary/inventory/root/leaf/length, and
   every F. Compare each result to the direct section 4 literals.
4. Only after the stdlib checks pass, compare the same literal rows/bytes to
   `page_proof.py` as the system under test: inventory completeness,
   `_fixture_pre_visual_binding_sha256`, `_fixture_admission_binding_sha256`,
   `_fixture_admission_is_valid`, and the existing private composition
   normalizers. Production helper output must never populate expected values.
5. Recursively compare old and new decoded W/V values after removing only the
   explicitly permitted identity-bearing paths. This proves semantic equality
   without a hand-selected projection that could hide drift.
6. The stale P/W/V/F, mixed-chain, child-identity, unconsumed-output,
   inactive-root/public-poison, and static-containment tests from the accepted
   4b.9 specification remain mandatory. The visual file must still prove 98
   direct normalizer calls, 46 exact target names, 96 adjacent contracts, and
   complete P/F containment.

The critic must independently rerun section 3 against the frozen pre-packet
literals (or an immutable copy identified by the executor's before-hashes),
compare stdout byte-for-byte/hash-for-hash with the final literal candidate,
then run the unchanged mandatory compile and exact nine-suite pytest commands.
The expected result remains exactly `159 passed`. A table match without the
stdlib oracle and production-SUT comparison is insufficient; passing tests
remain non-acceptance until fresh Terra/high implementation review finds no
P0/P1.

## 6. Security, data-contract, and branch controls

```text
accepted C2C + accepted CNF
  -> literal inventory I and independent inventory oracle
  -> stdout-only stdlib reseal oracle
  -> literal P/W/V/F candidate
  -> stdlib recheck + production SUT + exact 159-test regression
  -> fresh independent implementation review

any mismatch, extra changed path, partial chain, or forbidden capability
  -> blocker receipt; no candidate acceptance or downstream branch
```

The calculation reads no private inventory other than the explicit literal
contract and accepted test fixtures. It creates no inventory outside tests, no
candidate/reviewed ledger, no terminal/result/wrapper, no public success, no
production root, and no live/source/output/build/Git edge. There is no
environment-selected authority, filesystem-discovered input, or generated
artifact that a later reviewer cannot reconstruct from frozen literals.

Assumptions retained from the accepted 4b.9 architecture:

- the frozen hashes in section 2 of the 4b.9 specification still match before
  mutation;
- `page_proof.py` remains frozen and is only a system under test;
- the two accepted child identities are atomic and topology-specific;
- render bytes and all semantic W/V fields remain unchanged;
- expected candidate/reviewed-ledger hashes remain unchanged and unconsumed;
- no production activation, public/live path, Step 5, Git, or release action is
  authorized.

## 7. Acceptance criteria and next action

The clarification is sufficient only if the bounded executor can:

1. reproduce all four section 4 rows from the frozen old literals using only
   section 3 and the allowed temporary mechanics;
2. materialize direct canonical W/V bytes and direct P/F metadata with no
   runtime generation in the final candidate;
3. show exact old/new path diffs and unchanged semantic seals;
4. satisfy all original twelve tests plus the independent-oracle requirements
   without changing their names or total count;
5. preserve every frozen file/root/public boundary and run the original exact
   mandatory commands to `159 passed`;
6. record the exact stdin procedure, its stdout checkpoint rows, interpreter,
   version, before/after hashes, old-digest occurrence inventory, and absence
   of persistent temporary artifacts in the immutable executor receipt.

Next action: the main-chat orchestrator may reassign only Sol 4b.9 sections
3–7 as clarified here to one bounded Terra engineer at `medium`. After any
mutation, a different fresh Terra critic at `high` must perform the section 5
reproduction and implementation review. Candidate-ledger, review/replay,
terminal, production/public activation, live preflight, Step 5, Git, and
release work remain blocked.

## 8. Handoff accounting

- Scope: resolve only the 4b.9 P1 ambiguity around obtaining and independently
  verifying literal authoritative-inventory P/W/V/F reseals.
- Files checked: root `AGENTS.md` supplied in the task; canonical
  `docs/governance/nri_goal_governance.md`; this goal's `plan.md` and
  `context.md`; `docs/contracts/page_level_consumer_proof_contract_status.md`;
  accepted Sol 4b.9 specification; Terra 4b.9 architecture receipt; executor
  blocker receipt; read-only `kb_creator/pdf_raw/page_proof.py`; and the
  relevant fixture-leaf, admission, witness, flow, visual, and composition test
  literals/contracts.
- Files changed: this immutable handoff only.
- Verification/evidence: a read-only Python 3.13.14 stdin prototype independently
  applied the exact canonical-JSON/domain-separated formulas for all four
  cases, matched every section 4 checkpoint, then compared each row with the
  frozen production binding helpers and private composition normalizers. No
  repository file, production root, public route, source/output, build,
  browser/network, or Git state was changed. No pytest or release review was
  run. An initial `-I` probe failed closed because isolated mode excludes the
  repository package; the successful constrained command therefore uses
  `-B -` exactly as clarified above.
- Blockers: the literal-generation P1 blocker is resolved by this receipt.
  Implementation acceptance and every downstream/live/production branch
  remain blocked pending bounded implementation and fresh independent review.
- Next action: orchestrator dispatches the same 4b.9 implementation packet with
  this clarification attached; no broader packet is authorized.
- Elapsed active time: approximately `22 minutes`.
- Token use: `unavailable`.
- Timestamp: `2026-08-11T18:02:11.4920819+03:00`.

This receipt is immutable. A correction must use a new handoff and explicitly
supersede this file. It does not transfer orchestration ownership, act as the
final release reviewer, or make an implementation, production, or release
acceptance decision.
