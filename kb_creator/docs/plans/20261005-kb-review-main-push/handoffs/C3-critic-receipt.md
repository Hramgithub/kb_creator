# C3 independent packaging release review — immutable receipt

Goal `20261005-kb-review-main-push`. Review kind: **release**, limited to
packaging the previously approved candidate. Recommendation: **approve within
this frozen packaging scope**, with the planned C4 actual-index and C5 remote/
LFS verification still required. No blocking packaging finding reproduced.
I did not implement or materially design the candidate or packaging. Main
`/root` retains orchestration, Git writes, integration and user-facing decisions.

## Exact candidate and checks

- Final `scope.json` SHA-256:
  `3AE7F495126725DFCB7B9A1CE914483CFE113A0530BD5C6C5DD61919E3C49A05`.
  **204 unique payload paths and nine explicit deletions**, not the older202
  count in the task packet. The two packaging-attribute interim digests were
  superseded before this receipt; final change was only attribute-file EOL
  normalization, with `.gitattributes -text` retained.
- Independently checked all204 working payload sizes/hashes against the
  earlier scope, then rehashed all204 against the final scope: zero mismatches.
  Nine deletion targets are absent. Exact selected paths were inspected;
  source PDFs, page render/contact sheets, raw logs/transcripts, pytest roots,
  credentials/config and unrelated CoC/Innsmouth changes are not selected.
  Main separately reports zero textual secret-pattern matches; that bounded
  scan is consumed evidence, not a claim of exhaustive secret detection.
- Approved implementation union is49 paths. All43 U8 entries match the prior
  manifest and all seven U6 table entries match, with one shared dependency;
  every approved entry is selected and agrees with its current SHA-256.
  The U8 manifest is `9A948C1264D64A48E551221E5604FC6435F2641A9B50AAEE13079C5F657C8BEC`;
  U6 API remains `ECF14988614230151542B5EFE358A1FF1A8554A7B6718BCF00AFBE7AADBB5A90`.
- The three unchanged fixed DOCX identities match prior release approval:
  Fear `D79AB0EC131D2C6926D868EB037786093F615AEAF122895AA4487254616CF33E`;
  Leningrad `CC3A1F96D82121C07938D860EF88186AA33A32199B578D4C7C2DE05F4C83AD23`;
  Kremlin `5573888152F7EDAB32D483E4D652FD465694BFBF1764CC708C3EF7C042AA87D8`.
  Six reviewed original DOCX remain separately preserved in the selection.
- All30 direct authority bindings from the three candidate manifests,
  including ledger/choices/conversion-spec fields, resolve to selected files
  with matching hashes. The23 referenced recovered final-art inputs and their
  manifest are included. Native comments and normalized decision/operation/
  topology evidence are intentional authorities, not accidental scratch.
- Exact-path `git check-attr` checks confirm `-text` on all49 approved files,
  and `filter=lfs` plus `-text` on all32 selected binaries: nine DOCX and23
  recovered raster inputs. `.gitattributes` itself is `-text`. This validates
  attribute policy, not yet uploaded LFS objects or staged pointer contents.
- Branch is `main`, HEAD `9f297c22ee55437f90abb960d13c0c720e666045`, four commits
  ahead/zero behind the observed `origin/main`. Existing four ancestors are
  declared context, not newly attributed to this packaging review. Actual
  index was empty at the final check; no staging, commit or push was performed
  by this critic. Unrelated dirty work was not changed.

## Evidence, findings and limits

Files checked: current C3 packet, plan/context, PRESERVATION, exact scope and
selected payloads; `.gitattributes` diff/effective attributes; prior canonical
release v02, immutable U9 release receipt, U8 manifest and U6 final hash table;
three candidate manifests and direct authorities. Prior U9 approval consumed
completed QA v05 (239 passed,14 subtests, one unrelated COM skip; focused48
passed) and current-book367-page QA. This packaging check does not repeat or
extend those tests, visual inspections, source completeness or full7e claims.

- Severity findings: no P1/P2 blocker within the reviewed packaging boundary.
  Informational: the packet's202 count is stale; final scope is204, as expressly
  corrected by main. Do not use the old count/digests for staging verification.
- External original PDFs, diagnostic PNGs, raw logs and synthetic probes are
  intentionally excluded. Some immutable historical receipt links therefore
  remain local-only. This is a curated preservation snapshot, not a standalone
  reproducibility bundle. Original-host absolute paths are evidence identities,
  not portable commands. Missing masters are not restored by this commit.
- DOCX-only, bounded reviewed-artifact lineage, original drawing conservation,
  approved rule exceptions, mandatory future human source/output review and
  non-inference of human book acceptance all remain as declared in prior U9
  and PRESERVATION. No normal-route replay of current books is claimed.
- Before commit, main must compare the actual index to the exact authorized
  selection, verify raw staged text bytes and LFS pointer OID/size against the
  manifest, and preserve unrelated dirty work. `scope.json` cannot self-list;
  this newly created receipt also lies outside the204 payload list. If included,
  these must be explicitly recorded as administrative additions with the final
  index count, not silently counted as already reviewed payloads. Push/remote
  commit and LFS availability verification remain C5, not completed here.
- Any selected implementation, dependency, authority, book, attribute or scope
  mutation invalidates this approval for the changed revision. Later main-owned
  administrative status integration must be declared and checked at C4; it does
  not authorize hidden payload expansion or altered candidate bytes.

## Administration

Only this new immutable receipt was written. No canonical plan/context/status/
release, implementation, tests, source, books or previous evidence was edited.
Assignment state: packaging review COMPLETE; C4/C5 remain main-owned. Requested
critic role `gpt-6-astra/high`; actual runtime identity/effort unavailable,
`platform-unverified`. Orchestrator policy owner `/root`, `gpt-6-sol/medium`.
Scoped role override: none; packaging-only review is the assigned scope, not
an override of independence or preservation rules.

Start `2026-10-05T03:10:28.4227903Z`; final freeze checkpoint
`2026-10-05T03:12:39.6459644Z`; receipt issued approximately03:13UTC.
Elapsed approximately3 minutes. Exact token usage unavailable.
