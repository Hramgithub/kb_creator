# Viral Step 6A reconstruction-builder QA remediation: immutable baseline amendment

## Amendment metadata

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6-source-reconstruction-step6a-reconstruction-builder-qa-remediation-baseline-amendment`
- Role/model/effort requested: engineering assistance, `gpt-5.6-terra`, medium
- Actual platform model/effort: unavailable to author
- Orchestrator policy owner: main chat `gpt-5.6-sol`, medium
- Assignment state: user-directed engineering assistance
- Scoped override: none
- Timestamp: 2026-08-31T21:16:06+03:00
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`

## Immutable predecessor and rejection binding

This is an immutable amendment to, and does not rewrite,
`handoffs/terra_engineering_viral_step6a_reconstruction_builder_qa_remediation_packet_20260831.md`
at SHA-256 `D7A283D3D6C49701C265707507015870C90C3B1D8B79117BD9F59D2D07622D27`.

It responds only to P1 in the fresh independent critic rejection receipt
`handoffs/gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_packet_review_20260831.md`
at SHA-256 `7BBC78D57C1D91D3438B025B44D5C437B73A1F0F5D3339C05C1571B82F3D5BC7`.

## Sole supersession

This amendment supersedes **only** the erroneous candidate-baseline digest
`6E0872BA47E74356E590D7CFABE192ED92DD832D1B11CAA1BDBBE120AFFC4E07` in
the original packet, including its baseline-admission table and ready-to-paste
executor prompt.

For the exact existing candidate root
`kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`,
the required `471`-regular-file baseline digest is instead:

```text
BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809
```

All other original-packet scope, immutable and mutable allowlists, paths,
counts, stops, commands, predecessor identities, receipts, QA/review order,
and `candidate_needs_review` boundary remain unchanged. This amendment does
not authorize execution, candidate mutation, QA, or acceptance. Fresh
independent `gpt-5.5` acceptance with no unresolved P0/P1 remains required
before an executor may act.

## Exact canonical baseline-manifest algorithm

The candidate baseline manifest is calculated exactly as follows:

1. Recursively enumerate **regular files** in the exact candidate root.
2. For every enumerated file, obtain its path relative to that root and render
   it with POSIX `/` separators.
3. Form one record exactly as
   `relative-posix-path<TAB>byte-count<TAB>uppercase-SHA256(file)`.
   `byte-count` is the file's byte length in decimal; `SHA256(file)` is the
   uppercase hexadecimal SHA-256 of that file's raw bytes.
4. Sort the complete record strings using `.NET StringComparer.Ordinal` /
   Unicode code-point ordinal ordering. Do **not** use culture-sensitive
   `Sort-Object`, default locale collation, or path-only sorting.
5. Join the ordered records with LF (`0x0A`), append one final LF (`0x0A`),
   and encode the resulting text as UTF-8 **without BOM**.
6. SHA-256 the complete resulting byte stream and render that digest as
   uppercase hexadecimal.

The required output of that exact algorithm for this admitted live root is the
`BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809` digest
above. The final LF is binding; CRLF serialization, lowercase per-file hashes,
culture-sensitive ordering, omitted final LF, a BOM, or a changed file set is
a mismatch.

## Admission, reproducibility, and stop rule

Before **any** candidate write, the executor must recompute the preceding exact
algorithm twice, independently from the same unchanged candidate root. Both
results must be the required `BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809`.
Otherwise the executor must stop before writing and record the baseline mismatch
in its blocked successor receipt; it must not normalize, replace, rebuild,
delete/recreate, or otherwise alter the candidate to obtain a match.

The focused hermetic test requirement in the original packet is extended only
for baseline determinism: fixtures must include record strings whose ordinal
order would differ from the active culture and assert that the implementation
uses `.NET StringComparer.Ordinal` semantics, UTF-8 without BOM, LF including
the final LF, uppercase per-file SHA-256 values, and a whole-stream SHA-256.

As a read-only cross-runtime reproducibility probe before execution, PowerShell
must sort complete record strings with `[System.StringComparer]::Ordinal`; if a
Python corroboration is used, it must be read-only and use `sorted(records)` on
the same complete strings, serialize the same UTF-8-without-BOM LF-final stream,
and produce the same required digest. Any disagreement between either probe,
either of the two required recomputations, or the binding digest is a stop.

## Executor-prompt replacement sentence only

Where the original ready-to-paste prompt says it is bound to baseline manifest
`6E0872BA47E74356E590D7CFABE192ED92DD832D1B11CAA1BDBBE120AFFC4E07`, read it
as bound to the exact 471-file canonical baseline manifest
`BC0A37CB7587AF8412E6D1EDCB0D9ED3FAE8CE63DE1B90BDB65AD9EF903B5809`, calculated
twice before any write by the algorithm in this amendment. Every other sentence
of that prompt remains unchanged.

## Handoff result

Changed by this engineering task: only this amendment. Blocker: fresh
independent `gpt-5.5` acceptance remains required; this document confers no
authorization. Token use: unavailable. Compute and report this amendment's
detached SHA-256 after final write; do not edit this immutable amendment to
embed it.
