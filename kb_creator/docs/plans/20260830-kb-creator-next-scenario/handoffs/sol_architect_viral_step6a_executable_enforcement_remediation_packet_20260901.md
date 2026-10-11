# Viral Step 6A executable-enforcement remediation packet

## 1. Packet identity, authority, and non-authority

- Goal / step: `20260830-kb-creator-next-scenario` / `6A-executable-enforcement-remediation`.
- Result: `implementation_ready_pending_independent_design_review`.
- Architecture/root-cause role: repository policy `gpt-5.6-sol` / `high`; actual platform model/effort is not exposed and is recorded as `unavailable`.
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`; orchestration, canonical plan/context/status, integration, stop/ask decisions, and user-facing synthesis remain there.
- Future bounded executor: policy `gpt-5.6-luna` / `medium`.
- Future bounded QA: policy `gpt-5.6-luna` / `high`.
- Independent design and implementation/process critic: policy `gpt-5.5` / `medium`; the critic must not implement, materially design, or own QA for the surface it reviews.
- Required worktree / branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Triggering critic receipt: `gpt55_critic_viral_step6a_enforcement_completion_final_review_20260901.md`, SHA-256 `10871A65CD976F6B739608FED761AE9135A1C5370773D5D3F6DE61C8DF17977E`, verdict `REJECT`.
- This packet is the only architecture-task write. It is not execution, QA, candidate acceptance, semantic-review, `MASTER_EN`, promotion, publication, release, Git, cleanup, or destructive-action authority.

Execution remains blocked until a fresh internal independent `gpt-5.5` design review accepts this exact packet with no unresolved P0/P1. No live `build` or `remediate` is authorized by this packet or by its future design review.

## 2. Hard boundary and admitted immutable baseline

The live candidate remains exactly `candidate_needs_review` and read-only. The admitted source is only the retained local copy. The external Yandex locator is provenance data inside the source-admission sidecar; no future implementation, test, verifier, receipt, or error may resolve, stat, open, hash, copy, log, or pass it to a command.

### Repository and protected code/test baseline

| Authority | Required identity |
|---|---|
| branch / HEAD | `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380` |
| shared library | `kb_creator/scripts/scenario_source_reconstruction.py`; 29,620 bytes; `E5AEEACB175AD20C900AB31998045DBA398714AD4936E03FF591A090429D4107` |
| focused tests | `kb_creator/tests/test_scenario_source_reconstruction.py`; 9,515 bytes; `B91A1F78F9F7D4D2E87FEA8A701F6877C47AA3443899883C538FCC3C7D93A31A` |
| protected CLI | `kb_creator/scripts/reconstruct_scenario_source.py`; `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA` |
| protected contract tests | `kb_creator/tests/test_scenario_contract.py`; `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3` |
| local source | `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`; 20,718,150 bytes; `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| source sidecar | `kb_creator/working/viral/source/SOURCE_ADMISSION.json`; `3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9` |
| source contract | `kb_creator/contracts/viral.json`; `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D` |
| recovery manifest/evidence | `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169` / `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC` |

### Candidate and visual baseline

Exact live candidate root:

`kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`

| Scope | Count | Canonical manifest SHA-256 |
|---|---:|---|
| all regular candidate files | 502 | `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA` |
| all except root `RECONSTRUCTED_EN.qa.json` | 501 | `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766` |
| protected subset excluding QA and `evidence/COMMANDS.json` | 500 | `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027` |
| `renders/**` | 155 | `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A` |
| `renders/source/**` | 124 | `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C` |
| `renders/contact_sheets/**` | 31 | `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A` |

The protected raw files are:

- `RECONSTRUCTED_EN.qa.json`: 104,854 bytes; `C38CB0A4667B1D4344C5E5DD91AEAAE7A2FD3101A3BB76611104EAA13BBD8FA6`;
- `evidence/COMMANDS.json`: 37,422 bytes; `9162651A456E12C7011081F999AA3B07EDB7EA9E66CA65CC78A0382456F12B06`.

No file or directory below the live candidate, source, recovery, contract, CLI, contract tests, or accepted/publication surfaces may be added, removed, renamed, rewritten, normalized, or re-finalized in this remediation.

## 3. Findings closed by this design

The current implementation reproduces all critic findings:

1. The 371-node suite is arithmetic over `_CASE_COUNTS` and a family-level summary JSON. It retains counted `POS`, omits `INJ`, uses `TOP=20`, and does not create selector-specific production-shaped bundles.
2. `_test_verify()` dispatches to `_verify_test_bundle()`, a different verifier. `_admit_context()` accepts a reconstructed production-kind context when provider ids start with `test-`.
3. Public `build()` reaches a toy writer, test QA schema, direct `os.rename`, and broad `shutil.rmtree`; it has no validated production input, owned temp identity, no-replace publication, or post-rename strict verification.
4. Public `verify()` does not admit context, does not check branch/HEAD itself, and checks only a subset of the 16-authority graph.

The remediation is architectural replacement, not a small patch around those seams. Accepted strictness is not reduced to fit the current implementation.

## 4. Exact future mutable allowlist and proof of sufficiency

The two-file implementation/test allowlist is sufficient and is preserved. The future bounded executor may modify only:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`; and
3. absent-before immutable receipt `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_executable_enforcement_remediation_20260901.md`.

No additional code module is required:

- the protected CLI already imports the four required public functions and passes the exact four `Path` arguments;
- the sealed profile, providers, strict pipeline, writer, finalizer, Windows ownership helpers, and production loader can be defined in the existing shared library without changing the CLI contract;
- the full fixture factory, explicit case registry, mutation callables, and audit helpers belong in the existing focused test file;
- all required production facts already exist in the local source, sidecar, contract, recovery, candidate QA/COMMANDS, and 16 physical authorities; no data/schema mutation is needed; and
- the former executor receipts are immutable, so a new receipt is the only justified allowlist expansion. It is governance evidence, not a third implementation surface.

If implementation later claims another module, candidate field, CLI option, config, or fixture file outside `tmp_path` is necessary, the executor must stop. Such a claim requires a new architecture amendment and fresh independent design review; it may not widen this allowlist itself.

All pre-existing handoffs, `plan.md`, `context.md`, status/README/governance files, Git index/refs, candidate, source, recovery, CLI, and contract tests are protected by dispatch-window pre/post existence/length/raw-hash equality. They are not packet-era mutable surfaces.

## 5. One context-admitted execution and strict-verification pipeline

### 5.1 Required immutable types and function surface

The library must replace the current minimal profile with deeply immutable, self-sealed authorities. All collections are tuples of frozen records or tuples of key/value pairs; no nested mutable `dict`/`list` is retained in a profile.

Required types include:

```python
class ProfileKind(str, Enum):
    PRODUCTION = "production"
    TEST = "test"

@dataclass(frozen=True, slots=True)
class RepositoryIdentity:
    root: Path
    branch: str
    head: str

@dataclass(frozen=True, slots=True)
class FileSystemEntry:
    path: Path
    kind: Literal["missing", "regular", "directory", "symlink", "other"]
    size: int | None
    file_attributes: int
    reparse_tag: int | None
    file_id: tuple[int, int] | None

@dataclass(frozen=True, slots=True)
class FileAuthority:
    relative_path: str
    bytes: int
    sha256: str
    schema: str | None

@dataclass(frozen=True, slots=True)
class EnforcementAuthority:
    expected_branch: str
    expected_head: str
    source: FileAuthority
    sidecar: FileAuthority
    contract: FileAuthority
    recovery: RecoveryAuthority
    candidate: CandidateAuthority
    allowed_state: str
    blocker_ids: tuple[str, ...]
    forbidden_suffixes: tuple[str, ...]
    forbidden_segments: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class EnforcementProfile:
    profile_id: str
    kind: ProfileKind
    authority: EnforcementAuthority
    authority_sha256: str

@dataclass(frozen=True, slots=True)
class EnforcementContext:
    profile: EnforcementProfile
    identity: IdentityProvider
    filesystem: FilesystemProvider

@dataclass(frozen=True, slots=True)
class OperationPaths:
    contract_path: Path
    source_path: Path
    recovery_root: Path
    run_root: Path

PRODUCTION_PROFILE: Final[EnforcementProfile]
PRODUCTION_CONTEXT: Final[EnforcementContext]
```

The public signatures remain exactly four positional arguments and gain no override:

```python
def preflight(contract_path: Path, source_path: Path,
              recovery_root: Path, run_root: Path) -> dict[str, object]: ...
def build(contract_path: Path, source_path: Path,
          recovery_root: Path, run_root: Path) -> dict[str, object]: ...
def remediate(contract_path: Path, source_path: Path,
              recovery_root: Path, run_root: Path) -> dict[str, object]: ...
def verify(contract_path: Path, source_path: Path,
           recovery_root: Path, run_root: Path) -> dict[str, object]: ...
```

The only context-accepting wrappers are underscored test routes:

```python
def _test_preflight(contract_path: Path, source_path: Path,
                    recovery_root: Path, run_root: Path, *,
                    context: EnforcementContext) -> dict[str, object]: ...
def _test_build(contract_path: Path, source_path: Path,
                recovery_root: Path, run_root: Path, *,
                context: EnforcementContext) -> dict[str, object]: ...
def _test_verify(contract_path: Path, source_path: Path,
                 recovery_root: Path, run_root: Path, *,
                 context: EnforcementContext) -> dict[str, object]: ...
```

All seven wrappers do nothing except construct `OperationPaths` and call:

```python
def _execute(
    action: Literal["preflight", "build", "remediate", "verify"],
    paths: OperationPaths,
    context: EnforcementContext,
    route: Literal["public", "test"],
) -> dict[str, object]: ...

def _strict_verify(
    paths: OperationPaths,
    context: EnforcementContext,
    *,
    candidate_root: Path,
    publication: BuildVerificationToken | None,
    stage: Literal["existing", "build"],
) -> dict[str, object]: ...
```

There is no `_verify_test_bundle`, summary verifier, reduced build verifier, dynamic global writer lookup, `strict=False`, `skip_*`, environment/pytest bypass, or alternate finalizer.

### 5.2 Route admission is identity-based and non-bypassable

Context admission runs before repository/filesystem observation, in this exact order:

1. profile complete and deeply immutable: `E_PROFILE_INCOMPLETE`;
2. canonical authority seal recomputes exactly: `E_PROFILE_SEAL`;
3. route/profile identity:
   - `route=public` requires `context is PRODUCTION_CONTEXT`, `context.profile is PRODUCTION_PROFILE`, and `kind=PRODUCTION`;
   - `route=test` requires `kind=TEST` and rejects `PRODUCTION_CONTEXT` and every reconstructed production-kind context;
   - failure code `E_PROFILE_ROUTE`;
4. both provider `bound_profile_sha256` values equal the profile seal and test providers are bound to that exact independently constructed TEST profile: `E_PROVIDER_BINDING`.

Provider-id prefixes are diagnostic only and never admission authority. A production-kind context with `test-*` providers must fail. Public wrappers always pass the module-owned `PRODUCTION_CONTEXT`; callers cannot supply a profile, context, provider, config, or environment override through the unchanged CLI.

### 5.3 One phase order and exact earliest-error rule

`_strict_verify` stops on the first failure and never collects errors for later selection. Traversal is ordinal, not locale-sensitive. The phase order is binding:

0. context/profile/provider admission;
1. repository root, cwd containment, branch, then HEAD;
2. normalized operation arguments, escape, reparse/type/missing checks; build overwrite check before temp creation;
3. source, sidecar, contract, source identity, recovery manifest/evidence/payload authority;
4. explicit forbidden classes before generic topology/cardinality;
5. 16 schemas, required closed shapes, unexpected members, then row shapes;
6. independently enumerated canonical inventory transport;
7. blocker/page/content/master/navigation/asset/entity/handout/mode/reference/role/sheet graph;
8. COMMANDS, then QA policy and all scalar/count/gate/hash/flag mappings;
9. no-fabricated-closure state.

Repository failure codes are `E_REPO_ROOT`, `E_REPO_CONTAINMENT`, `E_REPO_BRANCH`, `E_REPO_HEAD`. Path failures are `E_PATH_ARGUMENT`, `E_PATH_ESCAPE`, `E_PATH_REPARSE`, `E_PATH_TYPE`, `E_PATH_MISSING`; build target existence is `E_BUILD_OVERWRITE`. Every test case below binds an exact code before execution. Tests assert `exc.value.code`, never message substrings.

## 6. Full production authority graph enforced by live `verify()`

The TEST fixture and production verifier both contain these 16 physical JSON authorities with the exact schemas; their locations differ only by sealed profile paths:

| # | Authority | Exact schema | Physical production location |
|---:|---|---|---|
| 1 | scenario contract | `kb_creator.scenario_contract.v1` | source contract and canonical candidate snapshot |
| 2 | source admission | `kb_creator.source_admission.v1` | retained local-source sidecar |
| 3 | recovery manifest | `viral_raw_engine_input_recovery_manifest.v1` | recovery root |
| 4 | recovery evidence | `viral_raw_engine_input_recovery_evidence.v1` | recovery root |
| 5 | QA | `kb_creator.reconstructed_en_qa.v3` | candidate root |
| 6 | source identity | `kb_creator.source_identity.v2` | candidate root |
| 7 | page provenance | `kb_creator.page_provenance.v3` | candidate evidence |
| 8 | content provenance | `kb_creator.content_provenance.v3` | candidate evidence |
| 9 | asset provenance | `kb_creator.asset_provenance.v3` | candidate evidence |
| 10 | entity inventory | `kb_creator.entity_inventory.v3` | candidate evidence |
| 11 | handout inventory | `kb_creator.handout_inventory.v3` | candidate evidence |
| 12 | navigation inventory | `kb_creator.navigation_inventory.v3` | candidate evidence |
| 13 | content-mode review | `kb_creator.content_mode_review.v2` | candidate evidence |
| 14 | reference-only audit | `kb_creator.reference_only_audit.v2` | candidate evidence |
| 15 | blocker ledger | `kb_creator.blocker_ledger.v3` | candidate evidence |
| 16 | commands | `kb_creator.reconstruction_commands.v3` | candidate evidence |

Live `verify()` must itself perform branch/HEAD admission and all of the following; a prior `preflight()` call, receipt, or test result is never accepted as a substitute.

- Source path is the exact retained local path; bytes/hash/pages/media/rotation are exact. Sidecar raw hash, closed shape, working-source facts, intake runtime policy, copy-verification facts, and generated-origin policy are exact. The external locator is ignored as opaque data.
- Contract raw/canonical facts and candidate snapshot bytes/hash agree. Source identity binds contract snapshot, local source, observer pages 1..124, recovery root and both recovery hashes, `historical_material_opened=false`, and `state=source_admitted`.
- Recovery is exactly 211 files: two authorities plus a 209-file manifest bijection over five named Markdown/JSON engine files and 204 JPEGs. Counts 209/204/112/92, bytes/hashes, allowed paths, source bindings, zero missing Markdown targets, and all no-promotion flags are independently derived.
- Forbidden classes are case-insensitive: `*.pdf`, `*.pyc`, `*.pyo`, `__pycache__`, `_bridge_runtime`, `.cache`, `cache`, `caches`, `.pytest_cache`, `tmp`, and `temp`. Reparse entries and non-regular enumerated files are independently forbidden.
- Closed candidate topology is exactly four root files, 124 pages, ten evidence files, 209 engine payload files, 124 source renders, 31 sheets, and empty `assets/`, `crops/`, `ocr/`; total 502.
- Inventory is exactly all 501 regular files except root QA. Rows are exactly `{path, bytes, sha256}`, POSIX relative, unique, uppercase hash, strict non-boolean integer bytes, ordinal complete-record order, UTF-8/no-BOM, LF plus final LF digest. It includes COMMANDS, all ten evidence files, and all sheets, and excludes only QA.
- Page provenance is exactly pages 1..124 / ids `page-001..page-124` / engine indices 0..123 / 388 unique block ids, with contract role/mode, live Markdown/render bytes/hashes, 144 DPI and `[1224,1584]`. Each Markdown contains exact source-page and render markers. The master is exact LF joining of page bytes.
- Content rows are exactly 388 unique `pNNN-bNNN` rows with page-local order and predecessor/successor chains matching page block ids. Live raw/rendered hashes are current; `operations` and `asset_ids` remain empty and `review_state=needs_review`.
- Navigation is one 124-node adjacent chain with null first previous/null last next, no fork/gap/cycle/dangling link, and exact page/index/path/role/render-hash mapping. Every closure remains `needs_review`.
- Assets are a 204-row bijection with live recovery-bound engine JPEGs. Exactly 112 unique Markdown occurrences resolve to 112 assets and 92 assets are retained unreferenced. MIME/bytes/hash/path/finding are exact; ownership is null and closure is `needs_review`.
- Entity and handout logical sets are byte-equivalent 39-row sets with ordinals 1..39, unique ids/labels/ranges, `mixed` disposition, and `needs_review`. Content-mode review is exactly pages 1..5 `unknown -> mixed`, still `needs_review`. Reference-only rows are empty and history is false.
- Role-derived closures are exactly 39 handouts, 7 keeper maps, 13 pregens, and one back cover; they are structural counts, not semantic acceptance.
- Blocker ledger contains exactly four unique open ids: `full-visual-review`, `unknown-content-modes-1-5`, `handout-map-pregen-navigation-review`, `asset-placement-ownership-review`. Ledger/QA open counts are four and no closure alias exists.
- COMMANDS has exact schema/state and ordered actions for the declared stage. Existing candidate: `preflight, remediate, contact_sheets, verify`; fresh build: `preflight, build, contact_sheets, verify`. Every record has the six explicit false flags, local `--source`/`--run-root` fields, and no external locator. Counts are exact `124/124/31/39/7/13/1/204/112/92/112`. The 31 sheets flatten pages 1..124 exactly once and map every page to the live render path/hash. Verify is deterministic.
- QA has exactly 23 current top-level fields, nine scalars, 14 count keys, nine gates, four authority hashes, two false booleans, 501-row inventory metadata/array, and state `candidate_needs_review`. No semantic, reading-order, placement, ownership, reconstruction-acceptance, promotion, release, or publication closure is allowed.

## 7. Independent production-shaped fixture and mutation protocol

### 7.1 Factory surfaces

The focused test file must define real frozen records, not summary dictionaries:

```python
@dataclass(frozen=True, slots=True)
class BundleInputFixture:
    repo_root: Path
    contract_path: Path
    source_path: Path
    sidecar_path: Path
    recovery_root: Path
    final_root: Path
    profile: EnforcementProfile
    context: EnforcementContext

@dataclass(frozen=True, slots=True)
class BundleFixture(BundleInputFixture):
    run_root: Path
    manifests: tuple[tuple[str, str], ...]

class ResealAuthority(str, Enum):
    SIDECAR = "sidecar"
    CONTRACT = "contract"
    RECOVERY_MANIFEST = "recovery_manifest"
    RECOVERY_EVIDENCE = "recovery_evidence"
    SOURCE_IDENTITY = "source_identity"
    PAGE_PROVENANCE = "page_provenance"
    CONTENT_PROVENANCE = "content_provenance"
    ASSET_PROVENANCE = "asset_provenance"
    NAVIGATION = "navigation"
    COMMANDS = "commands"
    INVENTORY = "inventory"
    QA = "qa"
    PROFILE = "profile"

@dataclass(frozen=True, slots=True)
class MutationCase:
    case_id: str
    expected_code: str
    mutate: Callable[[BundleFixture], None]
    reseal: tuple[ResealAuthority, ...]
    semantic_selector: str
    allowed_transport_selectors: tuple[str, ...]

def make_valid_input(root: Path, *, fixture_id: str) -> BundleInputFixture: ...
def make_valid_bundle(root: Path, *, fixture_id: str) -> BundleFixture: ...
def apply_case(case: MutationCase, bundle: BundleFixture) -> MutationAudit: ...
def reseal_transport(bundle: BundleFixture,
                     authorities: tuple[ResealAuthority, ...]) -> BundleFixture: ...
```

`make_valid_input` creates only the fixture repository, exact fake source/sidecar/contract, and exact 211-file recovery authority. `make_valid_bundle` calls the real `_test_build` once into an absent final root, then calls the real `_test_verify` twice and independently proves 502/501/500 manifests. It must not synthesize candidate bytes through a second test writer.

The filesystem provider has an outside-root read trap. The identity provider does not invoke Git. Both are sealed to one independently constructed TEST profile. No fixture reads production source, sidecar, contract, recovery, candidate, QA/COMMANDS, prior receipts, Git metadata, history, or the external locator.

### 7.2 Exact physical topology and production-compatible data

Every negative node gets its own newly created fixture. Candidate files are exactly:

| Class | Files |
|---|---:|
| root: contract snapshot, source identity, reconstructed master, QA | 4 |
| `pages/page-001.md..page-124.md` | 124 |
| ten evidence JSON files, including COMMANDS | 10 |
| five recovered Markdown/JSON engine payloads plus 204 JPEGs | 209 |
| `renders/source/page-001.png..page-124.png` | 124 |
| `renders/contact_sheets/sheet-001.png..sheet-031.png` | 31 |
| **total** | **502** |

`assets/`, `crops/`, and `ocr/` are physical empty directories. The separate recovery root contains two physical authority JSON files and byte-identical copies of the 209 engine payloads, for 211 files. All 16 schema authorities in section 6 exist as physical JSON files at production-compatible locations and use the current closed top-level and row shapes, not `{authority, profile}` summaries.

Fixture facts are production-shaped: pages 1..124; exact role partition; 388 content blocks (three per page plus a fourth on pages 1..16); 204 unique JPEG assets; 112 unique Markdown references and 92 unreferenced assets; 39 entity/handout logical rows; five open content-mode reviews; four open blockers; 124 navigation nodes; 31 deterministic 2x2 sheets; current QA v3 and stage-truthful COMMANDS v3. Fake PDF observation still reports 124 Letter pages, zero rotation, and 124 deterministic valid PNG page renders. All bytes/hashes/counts are computed from real fixture files; none are placeholders.

Factory order is fixed:

1. write fake local source, preliminary sidecar, and canonical contract;
2. write 209 recovery payloads;
3. derive/write recovery manifest and evidence from live bytes;
4. validate source/recovery into `ValidatedReconstructionInput`;
5. derive a pure expected build plan from that immutable model;
6. seal the complete TEST profile and bind both providers;
7. call real `_test_build` into an absent final root;
8. call real `_test_verify` twice and require identical payload bytes;
9. independently enumerate and match 502/501/500; and
10. return the same sealed profile/context without post-build profile mutation.

### 7.3 One mutation, explicit reseal, exact error

Every negative node executes this protocol:

1. create a fresh valid bundle and retain its two successful setup-verifies;
2. snapshot every file `{kind, file_id, bytes, sha256}` plus profile/provider seals;
3. apply exactly one declared `semantic_selector` mutation;
4. prove only that selector changed before resealing;
5. apply the literal, per-case `reseal` tuple in order;
6. prove each additional delta is listed in `allowed_transport_selectors` and that no semantic fact was repaired;
7. call the real `_test_verify`, which enters `_execute` and `_strict_verify`;
8. require `ReconstructionStop` and exact `exc.value.code == expected_code`;
9. prove no undeclared file/profile/provider delta and no cache/temp/probe remains; and
10. emit a `MutationAudit` row consumed by the executor receipt and QA.

There is no inferred/default reseal. Each `MutationCase` stores its literal tuple. Transport rules are:

- repository/provider and direct path cases: no reseal;
- sidecar/contract/recovery semantic fields after raw-hash admission: reseal the changed authority and `PROFILE` only;
- candidate schema/shape failures: no inventory reseal because phase 5 precedes phase 6;
- candidate evidence mutations targeting phase 7 or 8: reseal only the immediate live-byte binding if needed, then `INVENTORY` and QA inventory fields; never repair the semantic field;
- COMMANDS semantics: `INVENTORY, QA` only;
- QA semantics and inventory-transport cases: no reseal of the layer being tested;
- page/render/engine-byte cases targeting a later relation: explicitly list the affected provenance/sheet/recovery transport authorities, then `INVENTORY, QA, PROFILE` only when required by the selected later gate; and
- `PROFILE` reseal changes only expected transport hashes derived from other declared reseals. It may not adopt the mutated semantic value as valid policy.

The two `REG` cases are the only deliberate multi-field historical specimens. They still use one named historical mutation callable and a complete before/reseal/after audit.

The registry materializes the following reseal classes before pytest collection; prefix inference during the test body is forbidden:

| Selector class | Literal reseal tuple |
|---|---|
| `REP`, path/reparse/forbidden/topology, schema/shape, inventory, QA, `INJ` | `()` |
| sidecar raw-hash or missing | `()` |
| sidecar semantic fields | `(SIDECAR, PROFILE)` |
| contract raw-hash/path | `()` |
| contract canonical semantic | `(CONTRACT, PROFILE)` |
| candidate snapshot/source-identity failures | `()` because phase 3 precedes inventory |
| recovery raw-hash/root failures | `()` |
| recovery manifest semantic row/count/bytes cases | `(RECOVERY_MANIFEST, SOURCE_IDENTITY, INVENTORY, QA, PROFILE)` |
| recovery evidence semantic cases | `(RECOVERY_EVIDENCE, SOURCE_IDENTITY, INVENTORY, QA, PROFILE)` |
| blocker ledger | `(INVENTORY, QA)` |
| page/content/navigation/asset/entity/handout/mode/reference/role JSON semantics | `(INVENTORY, QA)` plus the specifically named immediate provenance authority only when the semantic mutation is in referenced live bytes rather than that JSON |
| COMMANDS semantics | `(INVENTORY, QA)` |
| `REG-P1-stale-metadata` | `()` |
| `REG-P1-missing-enforcement` | `(INVENTORY, QA)` |

For the one row that needs an immediate provenance reseal, the case entry must spell it out; this table is not a runtime default. `reseal_transport` rejects an authority not present in the case tuple and rejects any attempt to change the selected semantic JSON pointer.

## 8. Exact focused matrix: 368 negatives plus 3 builds

Counted `POS` nodes are removed. Positive validity is fixture setup for every case. The exact family arithmetic is binding:

| Family | Nodes |
|---|---:|
| `REP` | 2 |
| `SRC` | 18 |
| `AUT` | 30 |
| `TOP` | 21 |
| `SCH` | 33 |
| `LED` | 6 |
| `INV` | 18 |
| `PAG` | 28 |
| `NAV` | 15 |
| `AST` | 21 |
| `SEM` | 18 |
| `CMD` | 61 |
| `QAV` | 90 |
| `REG` | 2 |
| `INJ` | 5 |
| **selector-specific negative total** | **368** |
| `BLD` | **3** |
| **focused total** | **371** |

Generic ids such as `CMD-001` are forbidden. `pytest --collect-only` must expose descriptive selector ids. Static AST/string assertions may be supplementary inside existing nodes but are never case proof and never replace mutation execution.

### 8.1 Repository, source, authority, topology, schema, and ledger cases

The exact case-id suffix and earliest code mappings are:

**REP (2)**

- `REP-branch-wrong -> E_REPO_BRANCH`
- `REP-head-wrong -> E_REPO_HEAD`

**SRC (18)**

- `SRC-source-byte-identical-alias -> E_SOURCE_PATH`
- `SRC-source-external-locator -> E_SOURCE_EXTERNAL_FORBIDDEN`
- `SRC-source-missing -> E_PATH_MISSING`
- `SRC-source-bytes-wrong -> E_SOURCE_BYTES`
- `SRC-source-hash-wrong -> E_SOURCE_HASH`
- `SRC-source-reparse -> E_PATH_REPARSE`
- `SRC-sidecar-missing -> E_PATH_MISSING`
- `SRC-sidecar-raw-hash-wrong -> E_SIDECAR_HASH`
- `SRC-sidecar-working-path-wrong -> E_SIDECAR_WORKING_PATH`
- `SRC-sidecar-working-bytes-wrong -> E_SIDECAR_WORKING_BYTES`
- `SRC-sidecar-working-hash-wrong -> E_SIDECAR_WORKING_HASH`
- `SRC-sidecar-page-count-wrong -> E_SIDECAR_PAGE_COUNT`
- `SRC-sidecar-media-box-wrong -> E_SIDECAR_MEDIA_BOX`
- `SRC-sidecar-rotation-wrong -> E_SIDECAR_ROTATION`
- `SRC-sidecar-runtime-dependency-true -> E_SIDECAR_RUNTIME_DEPENDENCY`
- `SRC-sidecar-external-path-allowed -> E_SIDECAR_EXTERNAL_ALLOWED`
- `SRC-sidecar-subsequent-path-wrong -> E_SIDECAR_SUBSEQUENT_PATH`
- `SRC-sidecar-origin-marked-source -> E_SIDECAR_ORIGIN_POLICY`

The strict sidecar verifier additionally binds `copy_verification.method`, source/working bytes/hashes, and both equality booleans; the schema/shape matrix proves their presence and closed container.

**AUT (30)**

- Contract/snapshot (5): `AUT-contract-argument-wrong -> E_CONTRACT_PATH`; `AUT-contract-raw-hash-wrong -> E_CONTRACT_HASH`; `AUT-contract-canonical-content-wrong -> E_CONTRACT_CANONICAL`; `AUT-snapshot-bytes-wrong -> E_CONTRACT_SNAPSHOT_BYTES`; `AUT-snapshot-hash-binding-wrong -> E_CONTRACT_SNAPSHOT_HASH`.
- Source identity (11): `AUT-source-identity-contract-sha -> E_SOURCE_IDENTITY_CONTRACT`; `AUT-source-identity-source-bytes -> E_SOURCE_IDENTITY_SOURCE_BYTES`; `AUT-source-identity-source-sha -> E_SOURCE_IDENTITY_SOURCE_HASH`; `AUT-source-identity-page-count -> E_SOURCE_IDENTITY_PAGE_COUNT`; `AUT-source-identity-media-box -> E_SOURCE_IDENTITY_MEDIA_BOX`; `AUT-source-identity-rotation -> E_SOURCE_IDENTITY_ROTATION`; `AUT-source-identity-recovery-manifest-sha -> E_SOURCE_IDENTITY_RECOVERY_MANIFEST`; `AUT-source-identity-recovery-evidence-sha -> E_SOURCE_IDENTITY_RECOVERY_EVIDENCE`; `AUT-source-identity-recovery-root -> E_SOURCE_IDENTITY_RECOVERY_ROOT`; `AUT-source-identity-history-true -> E_SOURCE_IDENTITY_HISTORY`; `AUT-source-identity-state-wrong -> E_SOURCE_IDENTITY_STATE`.
- Recovery (14): `AUT-recovery-root-wrong -> E_RECOVERY_ROOT`; `AUT-recovery-manifest-raw-hash -> E_RECOVERY_MANIFEST_HASH`; `AUT-recovery-evidence-raw-hash -> E_RECOVERY_EVIDENCE_HASH`; `AUT-recovery-successor-file-count -> E_RECOVERY_FILE_COUNT`; `AUT-recovery-successor-total-bytes -> E_RECOVERY_TOTAL_BYTES`; `AUT-recovery-manifest-row-path -> E_RECOVERY_ROW_PATH`; `AUT-recovery-manifest-row-bytes -> E_RECOVERY_ROW_BYTES`; `AUT-recovery-manifest-row-hash -> E_RECOVERY_ROW_HASH`; `AUT-recovery-manifest-row-duplicate -> E_RECOVERY_ROW_DUPLICATE`; `AUT-recovery-forbidden-payload -> E_RECOVERY_FORBIDDEN`; `AUT-recovery-evidence-source-binding -> E_RECOVERY_SOURCE_BINDING`; `AUT-recovery-evidence-payload-binding -> E_RECOVERY_PAYLOAD_BINDING`; `AUT-recovery-allowed-paths -> E_RECOVERY_ALLOWED_PATHS`; `AUT-recovery-promotion-true -> E_RECOVERY_PROMOTION`.

**TOP (21)**

- Root/reparse (4): `TOP-candidate-root-wrong -> E_CANDIDATE_ROOT`; `TOP-candidate-root-escape -> E_PATH_ESCAPE`; `TOP-candidate-root-reparse -> E_PATH_REPARSE`; `TOP-nested-reparse -> E_PATH_REPARSE`.
- Closed topology (9): `TOP-root-file-missing -> E_TOPOLOGY_MISSING`; `TOP-root-entry-extra -> E_TOPOLOGY_EXTRA`; `TOP-evidence-file-missing -> E_TOPOLOGY_MISSING`; `TOP-evidence-file-extra -> E_TOPOLOGY_EXTRA`; `TOP-page-missing -> E_TOPOLOGY_MISSING`; `TOP-source-render-missing -> E_TOPOLOGY_MISSING`; `TOP-sheet-missing -> E_TOPOLOGY_MISSING`; `TOP-engine-payload-missing -> E_TOPOLOGY_MISSING`; `TOP-protected-empty-subtree-nonempty -> E_PROTECTED_EMPTY_SUBTREE`.
- Forbidden classes (8): `TOP-forbidden-pdf -> E_CANDIDATE_FORBIDDEN_PDF`; `TOP-forbidden-compiled-suffix -> E_CANDIDATE_FORBIDDEN_COMPILED`; `TOP-forbidden-pycache -> E_CANDIDATE_FORBIDDEN_PYCACHE`; `TOP-forbidden-bridge-runtime -> E_CANDIDATE_FORBIDDEN_BRIDGE_RUNTIME`; `TOP-forbidden-cache -> E_CANDIDATE_FORBIDDEN_CACHE`; `TOP-forbidden-pytest-cache -> E_CANDIDATE_FORBIDDEN_PYTEST_CACHE`; `TOP-forbidden-tmp -> E_CANDIDATE_FORBIDDEN_TMP`; `TOP-forbidden-temp -> E_CANDIDATE_FORBIDDEN_TEMP`.

The two reparse cases use a real physical file/directory plus a single immutable `ClassificationOverride` that sets `FILE_ATTRIBUTE_REPARSE_POINT` and a non-null tag while preserving kind/size/file-id. They exercise the production `_reject_reparse` branch and never skip for Windows privilege/developer-mode absence.

**SCH (33)**

Define the ordered authority labels exactly as `CONTRACT, SIDECAR, RECOVERY_MANIFEST, RECOVERY_EVIDENCE, QA, SOURCE_IDENTITY, PAGE_PROVENANCE, CONTENT_PROVENANCE, ASSET_PROVENANCE, ENTITY_INVENTORY, HANDOUT_INVENTORY, NAVIGATION_INVENTORY, CONTENT_MODE_REVIEW, REFERENCE_ONLY_AUDIT, BLOCKER_LEDGER, COMMANDS`.

- For each of the 16 labels: `SCH-<label>-schema-wrong -> E_SCHEMA_<label>`.
- For each of the 16 labels: `SCH-<label>-required-top-member-missing -> E_SHAPE_<label>`.
- `SCH-qa-unexpected-top-member -> E_SHAPE_QA`.

The case table stores the expanded 33 rows, not a count-only registry. The production verifier closes every current top-level container and every permitted row variant; one representative missing top member per authority plus the exact row-key checks in normal verification prevents permissive shape drift.

**LED (6)**

- `LED-open-count-wrong -> E_LEDGER_OPEN_COUNT`
- `LED-row-count-wrong -> E_LEDGER_ROW_COUNT`
- `LED-row-state-closed -> E_LEDGER_ROW_STATE`
- `LED-review-state-closed -> E_LEDGER_REVIEW_STATE`
- `LED-blocker-id-set-wrong -> E_LEDGER_IDS`
- `LED-affected-scope-count-wrong -> E_LEDGER_SCOPE`

### 8.2 Inventory and production graph cases

**INV (18)**

- `INV-ordinary-row-missing -> E_INVENTORY_PATH_SET`
- `INV-evidence-row-missing -> E_INVENTORY_PATH_SET`
- `INV-sheet-row-missing -> E_INVENTORY_PATH_SET`
- `INV-stale-extra-path -> E_INVENTORY_PATH_SET`
- `INV-duplicate-path -> E_INVENTORY_DUPLICATE`
- `INV-qa-included -> E_INVENTORY_QA_INCLUDED`
- `INV-cardinality-wrong -> E_INVENTORY_COUNT`
- `INV-order-nonordinal -> E_INVENTORY_ORDER`
- `INV-row-bytes-wrong -> E_INVENTORY_BYTES`
- `INV-row-hash-wrong -> E_INVENTORY_HASH`
- `INV-row-hash-lowercase -> E_INVENTORY_HASH_FORMAT`
- `INV-digest-wrong -> E_INVENTORY_DIGEST`
- `INV-path-backslash -> E_INVENTORY_PATH_SYNTAX`
- `INV-path-absolute-or-drive -> E_INVENTORY_PATH_SYNTAX`
- `INV-path-parent-segment -> E_INVENTORY_PATH_SYNTAX`
- `INV-path-leading-dot-slash -> E_INVENTORY_PATH_SYNTAX`
- `INV-row-shape-wrong -> E_INVENTORY_ROW_SHAPE`
- `INV-live-file-changed-behind-row -> E_INVENTORY_BYTES`

**PAG (28)**

- `PAG-page-row-missing -> E_PAGE_SET`; `PAG-page-row-duplicate -> E_PAGE_DUPLICATE`; `PAG-page-number-wrong -> E_PAGE_NUMBER`; `PAG-page-id-wrong -> E_PAGE_ID`; `PAG-engine-index-wrong -> E_PAGE_ENGINE_INDEX`; `PAG-role-wrong -> E_PAGE_ROLE`; `PAG-contract-mode-wrong -> E_PAGE_CONTENT_MODE`.
- `PAG-markdown-path-wrong -> E_PAGE_MARKDOWN_PATH`; `PAG-markdown-bytes-wrong -> E_PAGE_MARKDOWN_BYTES`; `PAG-markdown-hash-wrong -> E_PAGE_MARKDOWN_HASH`.
- `PAG-render-path-wrong -> E_PAGE_RENDER_PATH`; `PAG-render-bytes-wrong -> E_PAGE_RENDER_BYTES`; `PAG-render-hash-wrong -> E_PAGE_RENDER_HASH`; `PAG-render-page-number-wrong -> E_PAGE_RENDER_NUMBER`; `PAG-render-dimensions-wrong -> E_PAGE_RENDER_DIMENSIONS`; `PAG-render-dpi-wrong -> E_PAGE_RENDER_DPI`.
- `PAG-live-markdown-missing -> E_PAGE_MARKDOWN_MISSING`; `PAG-live-render-missing -> E_PAGE_RENDER_MISSING`; `PAG-source-page-marker-wrong -> E_PAGE_SOURCE_MARKER`; `PAG-render-marker-wrong -> E_PAGE_RENDER_MARKER`; `PAG-master-concatenation-wrong -> E_MASTER_CONCATENATION`.
- `PAG-content-orphan -> E_CONTENT_PAGE_LINK`; `PAG-content-duplicate -> E_CONTENT_DUPLICATE`; `PAG-content-order-wrong -> E_CONTENT_ORDER`; `PAG-content-predecessor-wrong -> E_CONTENT_PREDECESSOR`; `PAG-content-successor-wrong -> E_CONTENT_SUCCESSOR`; `PAG-content-operation-fabricated -> E_CONTENT_OPERATION`; `PAG-content-asset-link-fabricated -> E_CONTENT_ASSET_LINK`.

**NAV (15)**

- `NAV-row-missing -> E_NAV_SET`; `NAV-anchor-duplicate -> E_NAV_DUPLICATE`; `NAV-anchor-id-wrong -> E_NAV_ANCHOR`; `NAV-source-page-wrong -> E_NAV_PAGE`; `NAV-engine-index-wrong -> E_NAV_ENGINE_INDEX`; `NAV-first-previous-nonnull -> E_NAV_FIRST_PREVIOUS`; `NAV-last-next-nonnull -> E_NAV_LAST_NEXT`; `NAV-middle-previous-wrong -> E_NAV_PREVIOUS`; `NAV-middle-next-wrong -> E_NAV_NEXT`; `NAV-dangling-link -> E_NAV_DANGLING`; `NAV-markdown-path-wrong -> E_NAV_MARKDOWN_PATH`; `NAV-render-path-wrong -> E_NAV_RENDER_PATH`; `NAV-render-hash-wrong -> E_NAV_RENDER_HASH`; `NAV-role-wrong -> E_NAV_ROLE`; `NAV-closure-promoted -> E_NAV_CLOSURE`.

**AST (21)**

- `AST-row-missing -> E_ASSET_SET`; `AST-id-duplicate -> E_ASSET_ID_DUPLICATE`; `AST-path-duplicate -> E_ASSET_PATH_DUPLICATE`; `AST-hash-duplicate -> E_ASSET_HASH_DUPLICATE`; `AST-live-bytes-wrong -> E_ASSET_BYTES`; `AST-live-hash-wrong -> E_ASSET_HASH`; `AST-engine-path-missing -> E_ASSET_ENGINE_MISSING`; `AST-engine-path-wrong -> E_ASSET_ENGINE_PATH`; `AST-recovery-binding-wrong -> E_ASSET_RECOVERY_BINDING`.
- `AST-reference-total-wrong -> E_ASSET_REFERENCE_TOTAL`; `AST-unreferenced-count-wrong -> E_ASSET_UNREFERENCED_COUNT`; `AST-reference-count-outside-zero-one -> E_ASSET_REFERENCE_COUNT`; `AST-occurrence-missing -> E_ASSET_OCCURRENCE_SET`; `AST-occurrence-duplicate -> E_ASSET_OCCURRENCE_DUPLICATE`; `AST-markdown-path-wrong -> E_ASSET_MARKDOWN_PATH`; `AST-target-absent-from-markdown -> E_ASSET_TARGET_RESOLUTION`.
- `AST-ownership-nonnull -> E_ASSET_OWNERSHIP`; `AST-closure-promoted -> E_ASSET_CLOSURE`; `AST-finding-wrong -> E_ASSET_FINDING`; `AST-engine-image-cardinality-wrong -> E_ASSET_ENGINE_COUNT`; `AST-mime-wrong -> E_ASSET_MIME`.

**SEM (18)**

- `SEM-entity-ordinal-gap -> E_ENTITY_ORDINALS`; `SEM-entity-id-duplicate -> E_ENTITY_ID`; `SEM-handout-ordinal-gap -> E_HANDOUT_ORDINALS`; `SEM-handout-id-duplicate -> E_HANDOUT_ID`; `SEM-entity-handout-inequality -> E_ENTITY_HANDOUT_EQUALITY`; `SEM-required-count-wrong -> E_HANDOUT_REQUIRED_COUNT`; `SEM-label-wrong -> E_HANDOUT_LABEL`; `SEM-page-range-wrong -> E_HANDOUT_PAGE_RANGE`; `SEM-entity-closure-promoted -> E_ENTITY_CLOSURE`.
- `SEM-mode-page-gap -> E_MODE_PAGE_SET`; `SEM-mode-row-duplicate -> E_MODE_DUPLICATE`; `SEM-mode-review-promoted -> E_MODE_REVIEW_STATE`; `SEM-reference-only-row-added -> E_REFERENCE_ONLY_ROWS`; `SEM-historical-material-true -> E_REFERENCE_ONLY_HISTORY`.
- `SEM-map-role-count-wrong -> E_ROLE_MAP_COUNT`; `SEM-pregen-role-count-wrong -> E_ROLE_PREGEN_COUNT`; `SEM-back-cover-role-count-wrong -> E_ROLE_BACK_COVER_COUNT`; `SEM-handout-role-count-wrong -> E_ROLE_HANDOUT_COUNT`.

### 8.3 COMMANDS, QA, regression, and injection cases

**CMD (61)**

- Action/state (5): `CMD-action-missing -> E_COMMAND_ACTIONS`; `CMD-action-duplicate -> E_COMMAND_ACTIONS`; `CMD-action-extra -> E_COMMAND_ACTIONS`; `CMD-action-reordered -> E_COMMAND_ACTIONS`; `CMD-state-promoted -> E_COMMAND_STATE`.
- False flags (12): for each exact field `build_invoked, mineru_invoked, ocr_invoked, gpu_or_model_invoked, network_invoked, external_source_used`, expand `CMD-flag-<field>-missing -> E_COMMAND_FLAG_<FIELD>` and `CMD-flag-<field>-true -> E_COMMAND_FLAG_<FIELD>`.
- Runtime arguments (6): for each `source_flag, run_root_flag, source_relative_path`, expand `CMD-argument-<field>-missing -> E_COMMAND_ARGUMENT_<FIELD>` and `CMD-argument-<field>-wrong -> E_COMMAND_ARGUMENT_<FIELD>`.
- `CMD-external-locator-used -> E_COMMAND_EXTERNAL_SOURCE`.
- Counts (22): for each exact key `pages, renders, contact_sheets, handouts, maps, pregens, back_cover, assets, referenced_assets, unreferenced_assets, markdown_references`, expand `CMD-count-<key>-missing -> E_COMMAND_COUNTS_<KEY>` and `CMD-count-<key>-wrong -> E_COMMAND_COUNTS_<KEY>`.
- Sheet/action (15): `CMD-sheet-count-wrong -> E_COMMAND_SHEET_COUNT`; `CMD-sheet-coverage-wrong -> E_COMMAND_SHEET_COVERAGE`; `CMD-sheet-missing -> E_COMMAND_SHEET_SET`; `CMD-sheet-duplicate -> E_COMMAND_SHEET_SET`; `CMD-sheet-id-wrong -> E_COMMAND_SHEET_ID`; `CMD-sheet-path-sequence-wrong -> E_COMMAND_SHEET_PATH`; `CMD-sheet-grid-wrong -> E_COMMAND_SHEET_GRID`; `CMD-sheet-hash-wrong -> E_COMMAND_SHEET_HASH`; `CMD-flattened-page-missing -> E_COMMAND_SHEET_PAGES`; `CMD-flattened-page-duplicate -> E_COMMAND_SHEET_PAGES`; `CMD-flattened-page-order-wrong -> E_COMMAND_SHEET_PAGE_ORDER`; `CMD-render-path-wrong -> E_COMMAND_RENDER_PATH`; `CMD-render-hash-wrong -> E_COMMAND_RENDER_HASH`; `CMD-page-render-mapping-disagrees -> E_COMMAND_PAGE_RENDER_MAP`; `CMD-verify-determinism-false -> E_COMMAND_DETERMINISM`.

`<FIELD>` and `<KEY>` are normalized uppercase identifiers at registry construction time. The expected code is generated from the explicit constant table before a fixture is built; it is never derived from the observed exception.

**QAV (90)**

The exact current 23 top-level fields are:

`asset_count, block_count, contact_sheet_count, contract_sha256, counts, gate_results, handout_count, historical_material_opened, main_scripts_invoked, navigation_anchor_count, open_blocker_count, output_inventory, output_inventory_count, output_inventory_rule, output_inventory_sha256, page_count, recovery_evidence_sha256, recovery_manifest_sha256, referenced_asset_count, schema, source_sha256, state, unreferenced_asset_count`.

- For each field, expand `QAV-top-<field>-missing -> E_QA_SHAPE` (23).
- `QAV-top-extra -> E_QA_SHAPE` (1).
- `QAV-state-promoted -> E_QA_STATE` (1).
- Authority hashes (4): `QAV-authority-contract -> E_QA_CONTRACT_HASH`; `QAV-authority-source -> E_QA_SOURCE_HASH`; `QAV-authority-recovery-manifest -> E_QA_RECOVERY_MANIFEST_HASH`; `QAV-authority-recovery-evidence -> E_QA_RECOVERY_EVIDENCE_HASH`.
- Scalars (9): for each `page_count, handout_count, block_count, asset_count, contact_sheet_count, navigation_anchor_count, referenced_asset_count, unreferenced_asset_count, open_blocker_count`, expand `QAV-scalar-<field>-wrong -> E_QA_SCALAR_<FIELD>`.
- Count map (28): for each `assets, back_cover, contact_sheets, engine_images, engine_payload, handouts, maps, navigation_anchors, open_blockers, pages, pregens, referenced_assets, renders, unreferenced_assets`, expand missing and wrong cases, both `-> E_QA_COUNTS_<KEY>`.
- Gates (18): for each `asset_conservation, contact_sheet_coverage, navigation_anchors, page_1_5_modes, page_coverage, promotion, recovery_admission, source_identity, visual_review`, expand missing and wrong/closed cases, both `-> E_QA_GATE_<KEY>`.
- Booleans (2): `QAV-historical-material-true -> E_QA_HISTORY`; `QAV-main-scripts-invoked-true -> E_QA_MAIN_SCRIPTS`.
- Inventory metadata (4): `QAV-inventory-rule-wrong -> E_QA_INVENTORY_RULE`; `QAV-inventory-count-wrong -> E_QA_INVENTORY_COUNT`; `QAV-inventory-digest-wrong -> E_QA_INVENTORY_DIGEST`; `QAV-inventory-array-wrong -> E_QA_INVENTORY_ARRAY`.

**REG (2)**

- `REG-P1-stale-metadata -> E_QA_SCHEMA`: one named historical specimen applies QA v2, stale recovery-manifest binding, absent recovery-evidence hash, blocker count 3, and the preserved 470-row stale inventory cluster. Phase 5 must stop at QA schema. Isolated families prove each component elsewhere.
- `REG-P1-missing-enforcement -> E_COMMAND_COUNTS_PAGES`: change only `COMMANDS.counts.pages`, reseal inventory/QA transport, and require this exact phase-8 code.

**INJ (5)**

- `INJ-profile-seal-mutated -> E_PROFILE_SEAL`
- `INJ-test-route-given-production-profile -> E_PROFILE_ROUTE`
- `INJ-identity-provider-bound-to-other-profile -> E_PROVIDER_BINDING`
- `INJ-filesystem-provider-bound-to-other-profile -> E_PROVIDER_BINDING`
- `INJ-repository-root-observation-mismatch -> E_REPO_ROOT`

These replace the old production-kind-test-provider success test. No production-kind non-module context is ever a positive case.

## 9. Real production writer, finalizer, and atomic publication

### 9.1 Validated input and action-scoped build plan

The writer consumes an immutable `ValidatedReconstructionInput`, not dictionaries or a copied candidate:

```python
@dataclass(frozen=True, slots=True)
class SourceObservation:
    bytes: int
    sha256: str
    page_count: int
    media_box: tuple[int, int]
    rotations: tuple[int, ...]
    page_pngs: tuple[bytes, ...]

@dataclass(frozen=True, slots=True)
class PayloadFile:
    relative_path: str
    payload: bytes
    sha256: str

@dataclass(frozen=True, slots=True)
class ContentBlockInput:
    block_id: str
    page_number: int
    order: int
    markdown_bytes: bytes
    raw_sha256: str
    rendered_sha256: str
    predecessor_id: str | None
    successor_id: str | None
    source_strategy: str
    bbox_points: tuple[float, float, float, float] | None

@dataclass(frozen=True, slots=True)
class PageInput:
    page_number: int
    engine_page_idx: int
    contract_role: str
    contract_content_mode: str
    markdown_bytes: bytes
    render_png: bytes
    blocks: tuple[ContentBlockInput, ...]

@dataclass(frozen=True, slots=True)
class AssetInput:
    asset_id: str
    engine_relative_path: str
    payload_sha256: str
    payload_bytes: int
    mime: str
    reference_occurrences: tuple[int, ...]

@dataclass(frozen=True, slots=True)
class ValidatedReconstructionInput:
    canonical_contract_bytes: bytes
    contract_sha256: str
    source: SourceObservation
    recovery_manifest_bytes: bytes
    recovery_evidence_bytes: bytes
    engine_payload: tuple[PayloadFile, ...]
    pages: tuple[PageInput, ...]
    assets: tuple[AssetInput, ...]
    handout_ordinals: tuple[int, ...]
```

Required implementation functions:

```python
def _load_validated_reconstruction_input(
    paths: OperationPaths, context: EnforcementContext
) -> ValidatedReconstructionInput: ...

def _write_non_qa_bundle(
    staging_root: Path,
    model: ValidatedReconstructionInput,
    context: EnforcementContext,
    publication: OwnedTempRoot,
) -> None: ...

def _finalize_and_verify(
    staging_root: Path,
    paths: OperationPaths,
    context: EnforcementContext,
    publication: OwnedTempRoot | None,
    stage: Literal["existing", "build"],
) -> dict[str, object]: ...
```

Production loader admits only the retained local PDF, exact contract, and exact 211-file recovery. It parses the recovered five named Markdown/JSON files and 204 JPEGs, observes/renders the 124 source pages through the sealed production provider, and reconstructs the production data model. It never invokes MinerU, OCR, GPU/model, network, history, translation, or the external locator. If a required page/block/path/reference fact cannot be derived without invention, it stops; unresolved semantic/reading-order/placement/ownership facts remain explicit `needs_review`.

For a fresh target, `_execute(build, ...)` derives an internal immutable `BuildVerificationToken` from the sealed profile, normalized final path, validated model digest, stage command policy, and pure `plan_expected_bundle(model, stage="build")`. This action-scoped token supplies expected 502/501/500 identities before writing. It is not caller input and does not weaken the fixed live-candidate authority. Existing verify uses the literal live candidate authority; fresh build uses only this internally derived, profile-bound plan.

### 9.2 Deterministic write order and one finalizer

`_write_non_qa_bundle` uses create-new writes only and produces exactly the 500 protected files excluding COMMANDS and QA:

1. fixed directories `pages`, `evidence`, `engine`, `renders/source`, `renders/contact_sheets`, `crops`, `assets`, `ocr`;
2. canonical contract snapshot;
3. source identity;
4. 209 validated engine payloads in manifest ordinal order;
5. 124 source renders in numeric order;
6. 124 page Markdown files in numeric order;
7. reconstructed master from exact page bytes;
8. 31 deterministic 2x2 sheets;
9. nine non-COMMANDS evidence documents in this order: page, content, asset, entity, handout, navigation, content-mode, reference-only, blocker.

The sole `_finalize_and_verify` then:

1. validates the live 500-file graph without trusting stale QA/COMMANDS;
2. creates stage-truthful COMMANDS once, making file 501;
3. independently enumerates the 501-row non-circular inventory;
4. derives canonical QA bytes twice in memory and requires equality;
5. writes QA once as file 502; and
6. calls the same `_strict_verify` with no reduced build mode.

JSON is UTF-8/no-BOM, sorted keys, two-space indentation, LF-final where the current schemas require it. The live candidate is never re-finalized by this remediation.

### 9.3 Owned same-parent temp root and no-replace publication

Required frozen ownership records:

```python
@dataclass(frozen=True, slots=True)
class OwnedTempRoot:
    parent: Path
    final: Path
    temp: Path
    marker: Path
    nonce: str
    profile_sha256: str
    directory_file_id: tuple[int, int]

@dataclass(frozen=True, slots=True)
class BuildVerificationToken:
    owned: OwnedTempRoot
    model_sha256: str
    expected_manifests: tuple[tuple[str, str], ...]
    command_actions: tuple[str, ...]
```

Build state machine:

1. complete context/repository/path/source/sidecar/contract/recovery admission with no write;
2. no-follow classify final target and require `missing`; every existing file/directory/reparse/dangling link is `E_BUILD_OVERWRITE`;
3. require exact admitted non-reparse same-volume parent;
4. create exclusive hidden sibling `.<final>.tmp-<pid>-<128-bit-random>` and exclusive sibling ownership marker containing nonce, normalized temp/final, profile seal, and directory file id;
5. load validated input, write 500 files, finalize to 502, and strict-verify staging before publish;
6. reclassify temp/final/marker; require same parent, matching file id/nonce/profile, no reparse, and final still missing;
7. publish through provider `rename_no_replace` only. On Windows this is `MoveFileExW` with no replace-existing flag, or equivalent `os.rename` semantics verified to reject an existing destination; `os.replace` is forbidden;
8. require former temp file id at final, temp absent, marker still matching; run full strict verify again against final;
9. only after successful post-rename verify, delete the exact marker and prove it absent; and
10. return `built_candidate_needs_review`.

If the destination appears between admission and rename, stop `E_BUILD_PUBLISH_RACE`; never replace, merge, edit, or delete it. If post-rename verify fails, leave the published blocked root and marker for orchestrator inspection; do not roll back or clean the final path.

Pre-publish cleanup is allowed only through `remove_owned_tree(OwnedTempRoot)`. It may remove the exact temp and marker only after rechecking same-parent containment, nonce, profile seal, directory file id, final still missing, and every descendant as no-follow/non-reparse. Any mismatch, reparse, type/file-id race, missing/mismatched marker, access denial, locked entry, partial deletion, or unexpected descendant is `E_BUILD_TEMP_OWNERSHIP`; cleanup stops immediately, leaves remaining evidence, and never retries broadly. Wildcards, parent deletion, `shutil.rmtree`, followed-link traversal, final-root cleanup, and computed-directory cleanup are forbidden.

### 9.4 Three real build nodes

- `BLD-fresh-root-success`: `make_valid_input`, absent final, real `_test_build`; prove owned sibling creation, prepublish strict verify, no-replace rename, postrename strict verify, exact 502/501/500 production topology/state, no temp/marker, and zero external/tool access.
- `BLD-existing-target-refusal-no-mutation`: create nonempty target and snapshot kind/file-id/bytes/hash; real `_test_build` must return `E_BUILD_OVERWRITE`, leave target byte/type/file-id-identical, and create no sibling/marker.
- `BLD-finalizer-parity`: two independently generated valid inputs; one through real `_test_build`, one through real `_write_non_qa_bundle` plus `_finalize_and_verify` in an owned staging root. Require byte-identical relative files, COMMANDS, QA, 502/501/500 manifests, and success payloads. This node also inspects the ownership state transitions and confirms cleanup is never a broad directory operation.

Toy `payload/`, `authorities/*.json`, test-only QA schemas, direct production-kind test contexts, and two arbitrary directory comparisons do not satisfy BLD-001/002/003.

## 10. Executor admission, acceptance commands, and exact counts

### 10.1 Mandatory fresh design-review gate

Before any implementation write, a fresh internal independent critic writes only:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_executable_enforcement_remediation_packet_review_20260901.md`

The review must bind this packet by full SHA-256 and return no unresolved P0/P1. This packet does not authorize execution by itself.

### 10.2 Pre-write admission

The executor must first prove:

- exact worktree/branch/HEAD;
- this packet and accepted design-review hashes;
- code/test starting hashes `E5AEEACB175AD20C900AB31998045DBA398714AD4936E03FF591A090429D4107` / `B91A1F78F9F7D4D2E87FEA8A701F6877C47AA3443899883C538FCC3C7D93A31A`;
- protected CLI/contract-test hashes `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA` / `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3`;
- source/sidecar/contract/recovery identities;
- candidate 502/501/500 manifests;
- visual 155/124/31 manifests;
- QA/COMMANDS raw hashes `C38CB0A4667B1D4344C5E5DD91AEAAE7A2FD3101A3BB76611104EAA13BBD8FA6` / `9162651A456E12C7011081F999AA3B07EDB7EA9E66CA65CC78A0382456F12B06`;
- protected dispatch-window snapshot equality; and
- new executor receipt path absent.

Any mismatch is a pre-write stop, not permission to refresh the baseline.

### 10.3 Exact commands

Run from the exact worktree with bytecode and pytest cache disabled. No live `build` or `remediate` command is present.

```powershell
Set-Location 'D:\NRI\.worktrees\kb-creator-viral'

python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider

python -B -m pytest kb_creator/tests/test_scenario_contract.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py -q -p no:cacheprovider

python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider

python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate

python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate

python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
```

Required exact results:

- focused collect/run: `371 collected`, `371 passed` = `368` negatives + `3` BLD, with family counts exactly as section 8 and no `POS`;
- protected contract collect/run: `119 collected`, `119 passed`;
- combined collect/run: `490 collected`, `490 passed`;
- preflight and both live verifies: native exit `0`;
- verify stdout payloads byte-identical and SHA-256-identical;
- live verify reports exact branch/HEAD and uses only retained local source;
- candidate/source/recovery/CLI/contract-test/visual/QA/COMMANDS/protected identities unchanged; and
- no `.pyc`, pytest cache, fixture, temp sibling, owner marker, probe, or log remains in the worktree.

The executor receipt must also record a deterministic SHA-256 over the ordinal UTF-8/LF case-audit rows. A row is:

`case_id<TAB>semantic_selector<TAB>comma_joined_reseals<TAB>expected_code<TAB>observed_code<TAB>PASS\n`

There must be exactly 368 negative rows. BLD evidence is a separate three-row table with state transitions and manifest identities.

## 11. Required mutation-audit schema

The executor receipt contains a machine-readable JSON block with this exact closed shape per negative case:

```json
{
  "case_id": "CMD-count-pages-wrong",
  "family": "CMD",
  "fixture_root_token": "non-absolute-id",
  "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pages",
  "semantic_before_sha256": "UPPER64",
  "semantic_after_sha256": "UPPER64",
  "changed_before_reseal": ["candidate/evidence/COMMANDS.json#/counts/pages"],
  "declared_reseals": ["inventory", "qa"],
  "changed_by_reseal": [
    "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
    "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
  ],
  "expected_code": "E_COMMAND_COUNTS_PAGES",
  "observed_code": "E_COMMAND_COUNTS_PAGES",
  "strict_verify_calls": 1,
  "outside_fixture_reads": 0,
  "undeclared_changes": [],
  "residue": [],
  "result": "PASS"
}
```

Actual rows use their exact selector and hashes. No absolute fixture path, source bytes, or external locator is serialized. `changed_before_reseal` must contain exactly the declared semantic selector for ordinary cases. `changed_by_reseal` must be a subset of the case's literal allowed transport selectors. The registry itself must contain callable identity, not just family/prefix metadata.

The receipt also records:

- canonical production profile serialization/seal and production provider ids;
- public/test signatures and route table;
- full case-id list and family-count table;
- case-audit digest and all 368 rows;
- three BLD state-transition rows, including temp/final/marker states and file ids represented without machine-secret data;
- pre/post hashes of both modified files and the new receipt;
- all command lines, native exit codes, stdout/stderr hashes, collected/passed counts;
- unchanged candidate/source/recovery/visual/QA/COMMANDS/protected hashes;
- exact added/modified/deleted path diff; and
- elapsed/token use or explicit `unavailable`.

## 12. Stop conditions

### Before first write

Stop if the independent design review is absent/rejecting, any P0/P1 remains, any baseline differs, the executor receipt exists, a protected dispatch snapshot changes, or implementation cannot fit exactly the three-path allowlist.

### After first write

Stop and write a truthful blocked executor receipt on any:

- candidate/source/sidecar/contract/recovery/CLI/contract-test/plan/context/status/README/governance/prior-receipt/Git delta;
- external-locator access or appearance in command/error/receipt output;
- second verifier/finalizer/writer, production-kind test context, public override, mutable/defaulted profile, relaxed/skip flag, or provider-prefix admission;
- generic/missing/duplicate case id, counted POS, family count mismatch, selector without a real mutation callable, missing literal reseal tuple, non-exact error assertion, or undeclared mutation;
- focused/protected/combined count other than 371/119/490 or any test/collection failure;
- fake 502 claim, summary authority, toy writer, non-production QA/COMMANDS shape, or BLD case that does not use the real pipeline;
- preflight/live-verify failure or nondeterministic verify output;
- live `build`/`remediate`, MinerU/OCR/GPU/model/network/history/translation/external source, candidate promotion, semantic closure, staging/commit/push;
- `os.replace`, replace-existing rename flag, direct `shutil.rmtree`, wildcard cleanup, path-following cleanup, final-root cleanup, or temp cleanup without exact ownership proof;
- temp/marker/cache/fixture/probe residue in the worktree; or
- inability to produce a complete truthful receipt.

Do not broaden a deletion target or retry cleanup after an ownership/reparse/type/file-id/access failure. Leave the exact remaining owned temp evidence and report `E_BUILD_TEMP_OWNERSHIP`. Never delete or edit an existing final target.

## 13. Downstream QA and fresh critic gates

Passing executor commands does not close Step 6A. Gate order is mandatory:

1. fresh independent `gpt-5.5` design review of this packet, no unresolved P0/P1;
2. bounded executor within the exact allowlist, producing the absent-before executor receipt;
3. fresh bounded QA (`gpt-5.6-luna` / `high`) writing only absent-before receipt `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_executable_enforcement_remediation_20260901.md` and any explicitly authorized disposable external probe;
4. fresh independent `gpt-5.5` implementation/process review writing only `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_executable_enforcement_remediation_final_review_20260901.md`, with no implementation/material-design/QA participation and no unresolved P0/P1/P2; and
5. orchestrator integration after every receipt is immutable and hash-bound.

QA must independently inspect code, not trust the executor table. It must collect/run 371/119/490; prove the 368/3 split and exact descriptive ids; mechanically show every negative row invokes one mutation callable, declared reseal audit, `_test_verify`, and exact code assertion; rebuild at least one independent 502-file production-shaped bundle; run all BLD nodes; inspect owned no-replace publication/cleanup logic; run live preflight and verify twice but never live build/remediate; recompute all baselines; and prove zero forbidden access/residue/mutation.

Prior 67/67 original-resolution and 31/31 sheet visual QA may carry forward only if the prior correction receipt, candidate 500 manifest, visual 155/124/31 manifests, QA/COMMANDS hashes, and zero candidate-path mutation all remain exact. Carry-forward never closes semantic, reading-order, placement, ownership, or broader human-review blockers.

Even a final critic `ACCEPT` closes only the executable-enforcement P1s and reusable-build P2. The candidate remains `candidate_needs_review`. Semantic review, `MASTER_EN`, promotion, release, publication, staging, commit, and push require separate orchestrator-controlled gates.

## 14. Blocker disposition and safe next action

- P0: none identified.
- P1: three current implementation blockers remain open until execution + QA + final critic: fake summary/registry matrix; bypassable split test route; toy/unsafe public writer.
- P2: live verify branch/HEAD and full 16-authority graph remain incomplete until the same downstream evidence accepts the implementation.

This packet resolves those findings at design level only. Safe next action: hash this immutable packet and submit it to a fresh internal independent `gpt-5.5` design review. Do not dispatch an executor before that review returns no unresolved P0/P1.

## 15. Architecture-task mutation audit

This architecture task writes only this packet. It does not edit or run code/tests, CLI, candidate, source, sidecar, contract, recovery, QA, COMMANDS, plan/context/status, prior receipts, accepted/publication artifacts, Git index/refs, live build/remediation, MinerU/OCR/GPU/model/network/history/translation, staging, commit, or push. Token use is reported by the owning runtime in the task result; exact role-split usage is otherwise `unavailable`.
