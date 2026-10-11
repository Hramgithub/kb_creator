# Immutable Sol Handoff — Packet 4b.9 Forensic Baseline Recovery

## Receipt

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.9-forensic-baseline-recovery-spec`.
- Role/effort: Sol architect / requested `high`; actual platform model and
  effort: `platform-unverified`.
- Orchestrator policy owner: `gpt-5.5` at `medium`
  (`platform-unverified`). Orchestration ownership remains with the main chat.
- Assignment state: `user-overridden` for this bounded Sol/high recovery
  specification only.
- Scoped override: the user explicitly authorized restoration of the seven
  partial 4b.9 files to the frozen 4b.9 baseline. This receipt specifies that
  recovery; it does not perform it, transfer orchestration, accept an
  implementation, or act as a release review.
- Scope: read-only forensic comparison of the seven current files, the accepted
  4b.7 baseline receipts/hashes, the 4b.8/4b.9 specifications and clarification,
  both 4b.9 blocker receipts, and the applicable plan/context/contract.
- Result: **exact seven-file reconstruction is not possible from the authorized
  evidence alone.** Six files are exactly and deterministically reversible.
  `_page_proof_fixture_leaves.py` is not: the partial rewrite collapsed old and
  new equal-looking hash literals across repeated historical assignments, and
  no byte-exact frozen source is present in the evidence set.

## 1. Recoverability conclusion

Do not apply a six-file partial rollback. Packet 4b.9 requires one atomic clean
baseline, and restoring six files while guessing the seventh would create a
different mixed state.

The smallest safe alternative is to obtain exactly one byte source:

```text
kb_creator/tests/_page_proof_fixture_leaves.py
SHA-256 B471EB875410C09CDEF9ABA3F39082C3201F815D6C62ED9F3165A4ED58E1DF7E
```

It may come from a retained 4b.7 workspace copy, backup, or an executor artifact,
but it is admissible only when its bytes hash to the value above. A filename,
semantic re-creation, passing tests, or a near-match is insufficient. Once that
one file is available, the other six can be restored from their current bytes
by the inverse table below, and all seven can be installed and hash-checked as
one bounded recovery action without Git.

Why the missing file cannot be reconstructed exactly from a hash: its frozen
SHA-256 verifies a proposed byte string but does not reveal that string. The
current file contains repeated, superseded literal layers. The failed 4b.9
one-shot rewrite mapped distinct old occurrences onto values already present in
other layers. Reversing every matching value is therefore non-injective.
Concrete evidence: applying the complete inverse table globally in memory to
the current file produces
`BF7BEA8D993283D813E40D226B239690DEF5DA04E101CB9C944E0AFDDCE2BF55`,
not the frozen
`B471EB875410C09CDEF9ABA3F39082C3201F815D6C62ED9F3165A4ED58E1DF7E`.
The same procedure reaches the exact frozen hash for each of the other six
files. Inventing occurrence choices to force a semantic-looking file would not
be evidence of the original bytes.

## 2. Exact inverse substitution table for the six recoverable files

Operate on raw bytes. Every value is lowercase ASCII, replacements are
equal-length, and line endings/encoding must remain untouched. Replace left
with right. Before writing, require the per-file occurrence inventory in
section 3; on any mismatch, stop without mutation.

| Id | Current partial 4b.9 value | Frozen 4b.9 baseline value |
| --- | --- | --- |
| T | `4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4` | `d0891ce46fc9cb3aeee366cf78610996b3e2a34e94d85c47e9d212599a438ac6` |
| P2 | `cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d` | `954b615a68eb4c1198e29c9e06370820d2490019b77117ab5c5ab63d675da5a9` |
| PN | `388f7cc61345dbbcb516a4090e0d35cabb308f37137bf9b6b86c691fbf6c122c` | `7b132447080efa6cd1699d68624aaae6132c505b710bb52036b746903f75ab9b` |
| PV | `7f9327e3dba8c5ad888efa3423115e779b0bb0502438e7ddd9c02cd2c43dbea2` | `6c4b89ab43738d54e0c4dff7f1ed3aa5e4f8e66403ceca161c49a2dcac5aea99` |
| WC2 | `172ae571a4da210c0f8cdd5faf4e82bbf1fe9e718448a89369ce38250d9a6594` | `ec231fd77fc781980a3ae8b9633ec9214dffed86eb5eedf50c36cef704298ed0` |
| WCN | `aa95cc4c1ec640b9644e4febfb3e1d6f729be64b4544849ae5a9ffd4fd2c63e0` | `198618fa94029ede2dfe0eb6dc80e5ad947646654ee9f9a493916528280d2ec1` |
| WCV | `0d9b5d5faf83844591daaf8b2b471c2c03564653e47769b45ea0abef0167fb39` | `6e1c09bd858e7cd096708219ea16cd16a5a55f7fedd89c0f637e1468ce2af40a` |
| WCT | `7d014e1cdb5ce542936a91b28615cc86f508208ec3a190dba84a990dd145e86d` | `76c6d5e74c992b20f3238100f86a874696edd88b2c6a4bcde19b4dec22739dfc` |
| WH2 | `d08e02060ccb8a602a445cc14f0e71fd16fbcf1616d826463e00c64f46948295` | `1548abf602bd431731f8a848acdbd81b6421807eeb0e60867ff2085539026553` |
| WHN | `c488c0491139d27e696b5ab4ea4205b5ada0a9f577e3c3a23231868469eb85c3` | `64cbf87195889b69900cdc241fc2af0a289501465ba38248cd741a34d077770f` |
| WHV | `68d22df7ade83daa01348bcd25dc90ec69a9f0efe73b9f6f0bb0b9cfe379fb2e` | `dfaf8f0f9bc7dcfb2caf31382bd30cf5d0113c792a42733a6e22de957b8ad31a` |
| WHT | `e468e847f15c602d80808b572332978da2cd87eaa0009d766ae484ada80d1677` | `5e74282db39a5a3e25ea9b33e1820f2c0246dcf000191c5a1bd92eee7d80a563` |
| VC2 | `d38f51bba2b575528a32b572084b12ba2be33060e972ad7138a70eee9d580f73` | `a9e702d83d758beff14a0f6f48d70958827852fd31ffa17c60bd4ea5812e2d9f` |
| VCN | `f332b60fd1107f66ccff5e497a071f8438be9dc4d5e1e6c22734b9abbb6dbc97` | `8d9846c695a78ede56ff88e249cbccccc4ddd1bc87ab478894e65f94297897bd` |
| VCV | `7995e65505d53305ff53811e0221b64496d93bf8b8a29a753d9683d0c1ac2f1f` | `0cee689ee99d55a01c94c1491d4ed23a0f8ce6fbf09130ee7b9173b86d46a097` |
| VCT | `9083762bc843dacf0937f809809a8c82a4eed96326a7eb2dfab9870bb8d4aef0` | `9479c0f42b3ae4a6df84d4c62d39474bdbfe40dacc89ec6d3c4cfea67d6bc1f1` |
| VH2 | `2c358a6feb63859fa2f4c10346bd64e26da13f1e6d64f7cce5a868f881cab2c5` | `8a5ce3336970a87c2172adf6be6c86fde4fdd63493191334ce8bb3f3fb123d68` |
| VHN | `887aba071a09620cdc4789a5635ba57661eff0eec0792ad50db66af3a2d4f0d3` | `32631d67c1364417a3c3084a687ef4c1c97e7061cc3320380425489f42bb3e52` |
| VHV | `1e47e656240499dcc6d2c1e25a64691fe99c02d9801b6f52b2f8cc80993f1c76` | `f8ce424bd4a77e24d5b9f03341290d4d6ea25bc5b3d36bcf0f2c7cbc728671c6` |
| VHT | `761fc6aca16af4972d31081f4ad620f7f369c0c984c972f411ce196e4a95a2f4` | `3a99a36e58423dcb3b3752e05d5ca5e46924a351caa1ff5ee44a3da86e0b8082` |
| F2 | `0c45fd6b6440482b377fbcd3c6797701e622250dc0fdd496d18dbef81cd48838` | `9787e0a1b3e8fd5a352828d9ccb28a5fe5df9c791b23834c99abca1970916438` |
| FN | `249d56182c4710e6392740703ed86d388b714498d1bbc9c60e403de0caf0fbf2` | `dcfa12e611a8767d3328f229ec1db02b83b133b887c325d4f635da169651b44c` |
| FV | `4d9c98331427c55f788ee2fc532365434054e6d300236120fc11946c7894aecd` | `163ac2ed9536c36a7b3de405bcbf204096e466f592cc0a0e74587ab550b61b0b` |
| FT | `afd101e900a5242cf0c7867102272997e719ea3f183c5e096d0e5c1c826c522e` | `071ce92d8d4027ab544711d1b20f99b3d6933958d871add1e4f7d6d32f4b9a08` |

`WC*`, `WCT`, `WHT`, `VCT`, `VHT`, and `FT` are included to make
the inverse graph complete, but they occur only in the non-recoverable fixture
leaf among the seven current files, except `FT`, which also occurs once in the
visual-crosscheck test. They do not make the leaf globally reversible.

## 3. Six-file occurrence and hash oracle

The executor must compare occurrences against this exact inventory before any
write. Omitted ids have count zero.

| File | Required current occurrence counts |
| --- | --- |
| `test_page_proof_fixture_admission.py` | `T=4 P2=2 PN=2 PV=2 WH2=1 WHN=1 WHV=1 VH2=1 VHN=1 VHV=1 F2=2 FN=2 FV=2` |
| `test_page_proof_closed_schemas.py` | `T=1 P2=1 PN=1 PV=1 F2=1 FN=1 FV=1` |
| `test_page_proof_witness_render_components.py` | `T=1 P2=1 PN=1 PV=1 F2=1 FN=1 FV=1` |
| `test_page_proof_flow_adjacency.py` | `T=1 P2=1 PN=1 PV=1 F2=1 FN=1 FV=1` |
| `test_page_proof_visual_crosscheck.py` | `T=1 P2=2 PN=1 PV=1 VC2=1 VCN=1 VCV=1 F2=1 FN=1 FV=1 FT=1` |
| `test_page_proof_composition.py` | `T=1 P2=1 PN=1 PV=1 F2=1 FN=1 FV=1` |

In-memory application of section 2 with these occurrence counts produced the
exact frozen hashes below. No repository byte was changed during that check.

## 4. Current and required post-restore SHA-256 matrix

| Path | Current partial SHA-256 | Required frozen SHA-256 | Exact recipe status |
| --- | --- | --- | --- |
| `kb_creator/tests/_page_proof_fixture_leaves.py` | `EAFA65CFB474C2150DBC3632BF4F67364533D3D1CB9CF92B4D01A326F535C0EA` | `B471EB875410C09CDEF9ABA3F39082C3201F815D6C62ED9F3165A4ED58E1DF7E` | unavailable from evidence; obtain byte-exact source |
| `kb_creator/tests/test_page_proof_fixture_admission.py` | `0E05C55FA59087E87D6CCB9A6EDC678EB527264DAA56230D892FB66558EA2561` | `2591DB8E79F65E5986C00BDF549C8FF332C2F23914375B07770E5F1D8585C3F5` | section 2 exact |
| `kb_creator/tests/test_page_proof_closed_schemas.py` | `526CB1A10F50ADDBE8262CBE0DBDE52DEE01E961691222E825461E512F3A8318` | `CB9EA547F45EDE46799D36421D8C25B04F58978FA7D0D877F66B3BA47E530E8B` | section 2 exact |
| `kb_creator/tests/test_page_proof_witness_render_components.py` | `7491E9A3DE3A0A7D34C089CF30D3C25408FFF239A2416FEFD8B671CCAD0D86CD` | `3D916E3449C98DC022C75E531513558DD9488880B6FAFD504F250A2338342C50` | section 2 exact |
| `kb_creator/tests/test_page_proof_flow_adjacency.py` | `4718AA5619AD7E29363E5AE698CC43D41959443581167ECBF701734A0EB7FC2D` | `2EADD36285F7A715A027C73F9E5603E3D8C5D61A739D6B2B6EFD37E6F5D82720` | section 2 exact |
| `kb_creator/tests/test_page_proof_visual_crosscheck.py` | `1D92240D165F61A9905F5442B78686EF3A555DDD7A015D00AB4E222DA8C244A5` | `886B80E5A8259D23B3F506E560E821BB430D6E8FA5DC3022AD1FAD971744CB43` | section 2 exact |
| `kb_creator/tests/test_page_proof_composition.py` | `94203585B8A54B20C91B982FF85F8F6D8F8CF8D4CC0D0F6426FDDFD5EC38550D` | `4DD87ACB5FD04EE409AF24BC7D2651246273E171EAD2195BA1C1D9B7B55BD079` | section 2 exact |

## 5. Deterministic recovery procedure after the missing byte source exists

1. Read all seven current files and verify the current SHA column above. If any
   differs, stop; this prescription is stale.
2. Read the supplied fixture-leaf source and require its SHA-256 to be exactly
   `B471...1DF7E`. Do not normalize encoding, quotes, whitespace, or line endings.
3. In memory only, apply section 2 to the other six current byte strings after
   validating section 3 counts. Require each transformed byte string to hash to
   its required frozen SHA before any write.
4. Replace all seven files in one bounded recovery operation. The executor may
   use same-directory temporary siblings only if the orchestrator explicitly
   authorizes that implementation mechanic and all are removed after atomic
   replacement; otherwise use an approved equivalent that cannot expose a
   six-file intermediate as a candidate.
5. Re-read every installed file and require the seven exact frozen hashes.
   Hash mismatch means recovery failed closed; do not run compile/tests and do
   not resume 4b.9.
6. Record one new immutable executor recovery receipt with before hashes,
   supplied leaf provenance and hash, occurrence counts, seven after hashes,
   changed-file scope, and absence of Git/live/source/output/build/network paths.
7. Only after the clean baseline is established may the orchestrator reassign
   the original 4b.9 packet under a new receipt. This recovery itself is not a
   4b.9 implementation candidate and requires no release judgment.

## 6. Assumptions, branches, risks, and acceptance criteria

Assumptions:

- The current hashes in section 4 remain unchanged until recovery starts.
- The accepted 4b.7 executor and independent-critic receipts are authoritative
  for the frozen target hashes.
- SHA-256 is used only to verify supplied/transformed bytes, never as a source
  from which missing bytes are guessed.

Branches:

```text
exact B471... leaf source obtained
  + six in-memory inverses reach their frozen hashes
    -> atomic seven-file restore
      -> seven post-write hashes match
        -> clean 4b.9 baseline established; orchestrator may reassign 4b.9

missing leaf source, stale current hash, count mismatch, or any target mismatch
  -> no write / failed closed
  -> 4b.9 remains blocked and no implementation review is requested
```

Primary risks and controls:

- **Many-to-one literal collision:** controlled by requiring the byte-exact leaf
  rather than an occurrence guess.
- **Partial rollback:** controlled by precomputing all seven target bytes and
  installing only as one bounded recovery.
- **Text normalization:** controlled by raw-byte replacement and post-write
  SHA-256.
- **False acceptance:** passing hashes establish only the frozen baseline, not
  Packet 4b.9 implementation or release acceptance.

Acceptance criteria:

1. All seven post-restore hashes equal section 4 exactly.
2. No eighth code/test/canonical/status/release file changes.
3. No Git, live PDF/source/output/configuration/build/browser/network action.
4. The recovery receipt identifies the exact source of the B471 leaf and all
   seven before/after hashes.
5. The state is reported only as `frozen 4b.9 baseline restored`; 4b.9 remains
   unimplemented until a fresh bounded executor run completes its own required
   oracle, compile, nine-suite test evidence, and independent review.

## 7. Evidence, blocker, and next action

- Files checked: the seven current files; accepted 4b.7 executor/critic receipts
  and correction; 4b.8/4b.9 specifications; 4b.9 literal clarification;
  medium/high blocker receipts; goal plan/context and governance contract.
- Files changed: this immutable handoff only.
- Verification: current SHA-256 captured for all seven; section 2 was applied
  in memory without persistence; six outputs matched their frozen hashes
  exactly; the leaf global inverse did not match and exposed the information
  loss described above. No code/test file, Git state, build, browser, network,
  PDF/source/output/configuration, plan/context/status/contract/release file was
  changed or exercised.
- Blocker: one byte-exact `_page_proof_fixture_leaves.py` at
  `B471...1DF7E` is absent from the authorized evidence.
- Required next action: orchestrator obtains that one file from a retained
  byte source and then commissions the atomic seven-file recovery in section 5.
- Elapsed active time: approximately `52 minutes`.
- Token use: `unavailable` at receipt write time.
- Timestamp: `2026-08-11T20:32:52.9353824+03:00`.

This receipt is immutable. A correction must be a new handoff that explicitly
supersedes it. It does not transfer orchestration ownership or make an
implementation, production, release, or final acceptance decision.
