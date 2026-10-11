# Viral Step 6A enforcement injection amendment

## Identity, authority, and decision

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-enforcement-injection-amendment`.
- Result: `amendment_ready_for_independent_review`; this document is design authority only. It is not execution, QA, candidate acceptance, or promotion authority.
- Architecture/root-cause role: policy `gpt-5.6-sol` / `high`; platform-reported model/effort: `unavailable`; scoped user override: architecture role only.
- Orchestrator policy owner remains the main chat, policy `gpt-5.6-sol` / `medium`; it retains canonical plan/context/status, integration, stop/ask decisions, and user-facing synthesis.
- Future bounded executor: policy `gpt-5.6-luna` / `medium`; it may resume only after the independent amendment review gate below.
- Future bounded QA: policy `gpt-5.6-luna` / `low`, separate from implementation.
- Independent design and implementation/process critic: policy `gpt-5.5` / `medium`; the critic must not implement or materially redesign the candidate under review.
- Required worktree / branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Base packet: `sol_architect_viral_step6a_enforcement_completion_packet_20260831.md`, SHA-256 `56586563470FCA55B1CE31EB1EC73C71438B33A1FEBC1A1A39ADB8781AE3A604`.
- Accepted base design review: `gpt55_critic_viral_step6a_enforcement_completion_packet_review_20260831.md`, SHA-256 `BFA0127AE82FF129A9E1CDA7B1FABEF7B5035ADFC8F64BCC672B24AB0E9F2D21`, verdict `ACCEPT`, no P0/P1/P2.
- Intermediate executor checkpoint: `luna_executor_viral_step6a_enforcement_completion_20260831.md`, SHA-256 `E68DFB9658B2A9B70D77EC57F75FE1803D364E24F2323C8AC79150AF51F8E9B8`, disposition `BLOCKED`.
- Live partial library / focused-test baseline: `C7974735159F35636011C5839561E466806807EB8599E4C11CCC6958E815C861` / `752CCCC1A74B1EA7ECE93B4D26FD82DB747D7962A93FFB56CC590754557BA796`.
- Protected CLI baseline: `kb_creator/scripts/reconstruct_scenario_source.py`, SHA-256 `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA`.
- Architecture-task token use: reported by the owning runtime at completion; unavailable inside this immutable artifact.

This amendment removes one concrete execution blocker. It does not narrow the accepted verifier, change any candidate schema, authorize a live build/remediation, or expand the executor allowlist. The accepted base packet and review remain binding except for the clauses explicitly superseded below.

## Verified stop and root cause

The intermediate executor correctly stopped despite green count summaries:

- focused collection/execution reported `371` / `371 passed`;
- combined collection/execution reported `490` / `490 passed`, including the protected `119` contract nodes;
- live preflight and two strict verifies passed with unchanged candidate manifests;
- most focused nodes only asserted a registry, source strings, or the presence of failure-code symbols; they did not create a valid independent candidate, apply an isolated mutation, or execute the strict verifier against it; and
- `build()` finds `_write_build_stage` dynamically and stops with `E_BUILD_WRITER_UNAVAILABLE`; `_finalize()` does not call strict verification.

The causal seam is not the number of assertions. The verifier embeds production branch, HEAD, source, recovery, candidate-root, hashes, and counts as module constants. A temporary bundle cannot satisfy those constants, so a test can either touch the live production authority or avoid the real pipeline. The executor chose the latter and honestly reported the resulting registry-only coverage.

Closure therefore requires an immutable authority/profile object and injected identity/filesystem providers at the library boundary, while making those dependencies impossible to override through the production CLI. The same phase-ordered verifier must run for production and tests. A separate complete deterministic writer is also required; a dynamically absent global is not a build seam.

## Exact supersession map

Only the following base-packet clauses are superseded. Everything else, including the 16 schemas, live topology, evidence relationships, no-fabricated-closure rules, manifest algorithms, candidate immutability, local-source policy, acceptance commands, audit requirements, and downstream gates, remains binding.

| Base clause | Superseding rule |
|---|---|
| Repository/authority constants are read directly by verifier functions. | All authority values move into a deeply immutable, self-sealed `EnforcementProfile`. Public operations always use the module-owned `PRODUCTION_PROFILE`; only underscored direct-test entry points accept a fully specified sealed `TEST_PROFILE`. |
| Hermetic tests may inject only a repository probe without an exact route contract. | Tests inject a profile-bound `IdentityProvider` and `FilesystemProvider`. They may not omit, relax, skip, or default a production invariant. Provider/profile mismatch is a pre-verifier stop. |
| The coverage table has five `POS` nodes and 363 ordinary negative nodes, plus three `BLD` nodes. | There are exactly **368 executable named negative nodes**: the existing 363 negative selectors plus five injection/route selectors. There are exactly **3 real hermetic build nodes**. Total focused collection remains **371**. Baseline-positive validation is factory setup, not a separately counted node. |
| A fresh build creates the final root once and leaves a partial final root after failure. | A fresh build writes only to an exclusively created same-parent owned temporary sibling, strictly verifies it, and publishes it with a Windows-safe no-replace rename. Failure cleanup may touch only that provably owned temporary root. The final root is never created partially, deleted, merged, or replaced. |
| `_write_build_stage` may be discovered dynamically. | `_write_non_qa_bundle(...)` is a required concrete function. It receives a validated immutable reconstruction-input model and writes the complete 501 non-QA-file stage in one fixed order before the shared finalizer writes `COMMANDS.json` and QA as specified below. No globals lookup is allowed. |
| The executor receipt must be absent before execution and then newly created. | The exact existing `E68DF...` receipt is an intermediate checkpoint. The same executor may replace that exact path once under the receipt rewrite rule below; no successor path is added. |
| Pre-write code/test hashes are the pre-executor packet hashes. | Resume admission binds the current partial hashes `C797...C861` and `752C...796`; any other code/test starting identity is a stop requiring a new amendment/review. |

The amendment does **not** supersede these base facts:

- the live candidate stays byte-identical at 502/501/500 manifests `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA` / `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766` / `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`;
- candidate `RECONSTRUCTED_EN.qa.json` and `evidence/COMMANDS.json` remain byte-identical at `C38CB0A4667B1D4344C5E5DD91AEAAE7A2FD3101A3BB76611104EAA13BBD8FA6` and `9162651A456E12C7011081F999AA3B07EDB7EA9E66CA65CC78A0382456F12B06`;
- render manifests remain `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A` / `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C` / `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A` for 155/124/31 files;
- the external Yandex locator is provenance only and must not be resolved, statted, read, hashed, copied, logged, or passed to any command; and
- no live `build` or `remediate` is authorized.

## Immutable authority and provider contracts

### Required types and exact signatures

The executor implements the following conceptual public/internal surface in `kb_creator/scripts/scenario_source_reconstruction.py`. Names and signatures are binding; internal representation may add private helpers but may not add override parameters to the four public operations.

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final, Literal, Mapping, Protocol, Sequence

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
class RecoveryAuthority:
    relative_root: str
    manifest: FileAuthority
    evidence: FileAuthority
    regular_file_count: int
    payload_file_count: int
    payload_bytes: int
    engine_image_count: int
    markdown_reference_count: int
    unreferenced_image_count: int

@dataclass(frozen=True, slots=True)
class CandidateAuthority:
    relative_root: str
    total_files: int
    inventory_files: int
    protected_files: int
    schemas: tuple[tuple[str, str], ...]
    scalar_counts: tuple[tuple[str, int], ...]
    command_counts: tuple[tuple[str, int], ...]
    qa_counts: tuple[tuple[str, int], ...]
    command_actions_by_stage: tuple[tuple[str, tuple[str, ...]], ...]
    expected_live_manifests: tuple[tuple[str, str], ...]

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

class IdentityProvider(Protocol):
    provider_id: str
    bound_profile_sha256: str
    def repository_identity(self, start: Path) -> RepositoryIdentity: ...
    def observe_source(self, source: Path) -> "SourceObservation": ...

class FilesystemProvider(Protocol):
    provider_id: str
    bound_profile_sha256: str
    def lstat(self, path: Path) -> FileSystemEntry: ...
    def iter_entries(self, root: Path) -> Sequence[FileSystemEntry]: ...
    def read_bytes(self, path: Path) -> bytes: ...
    def write_new_bytes(self, path: Path, data: bytes) -> None: ...
    def mkdir_exclusive(self, path: Path) -> FileSystemEntry: ...
    def rename_no_replace(self, source: Path, target: Path) -> None: ...
    def remove_owned_tree(self, owned: "OwnedTempRoot") -> None: ...

@dataclass(frozen=True, slots=True)
class EnforcementContext:
    profile: EnforcementProfile
    identity: IdentityProvider
    filesystem: FilesystemProvider

PRODUCTION_PROFILE: Final[EnforcementProfile]
PRODUCTION_CONTEXT: Final[EnforcementContext]

def preflight(contract_path: Path, source_path: Path,
              recovery_root: Path, run_root: Path) -> dict[str, object]: ...
def build(contract_path: Path, source_path: Path,
          recovery_root: Path, run_root: Path) -> dict[str, object]: ...
def remediate(contract_path: Path, source_path: Path,
              recovery_root: Path, run_root: Path) -> dict[str, object]: ...
def verify(contract_path: Path, source_path: Path,
           recovery_root: Path, run_root: Path) -> dict[str, object]: ...

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

`ReconstructionStop` must expose a stable exact code instead of forcing tests to parse a message:

```python
class ReconstructionStop(RuntimeError):
    code: str
    detail: str
    def __init__(self, code: str, detail: str = "") -> None: ...
```

`str(error)` may remain `CODE` or `CODE: narrow-detail`, preserving the unchanged CLI's JSON error path. Tests assert `exc.value.code == case.expected_code`; substring or message-only matching is insufficient.

### Deep immutability and sealing

`frozen=True` alone is insufficient if a field contains a mutable dictionary. Every profile collection must be a tuple of frozen records or a tuple of key/value pairs. Constructors must normalize paths to POSIX repo-relative strings, uppercase SHA-256 values, validate strict integer types (`bool` is not an integer), reject duplicate/case-folded keys, and compute a canonical UTF-8/LF/no-BOM authority serialization. `authority_sha256` is the uppercase SHA-256 of that serialization.

The profile validator recomputes the seal before any repository or filesystem observation. It rejects a partial authority, `None`, wildcard, zero-as-unspecified value, empty schema, duplicate key, unrecognized count, or seal mismatch. There is no `strict`, `relaxed`, `skip`, `allow_missing`, `ignore_reparse`, environment-variable override, pytest detection, caller-provided count fallback, or default-to-production merge.

`PRODUCTION_PROFILE` is built once at import from literal accepted authorities and assigned as `Final`. It binds the exact Viral production branch/HEAD, repo-relative local source/sidecar/contract/recovery/candidate paths, raw authority hashes, 16 schemas, counts, state, blockers, forbidden classes, and live-manifest identities. It contains no machine-specific absolute root. The real identity provider discovers the actual repo root read-only and must match branch/HEAD.

A test profile is also an `EnforcementProfile`, with `kind=TEST`, all fields populated, and a correct seal computed from the temporary bundle's real bytes. It is never made by modifying or relaxing `PRODUCTION_PROFILE`; the fixture factory constructs it independently from its own authorities.

### Provider binding and non-bypassable routing

Each provider has a `bound_profile_sha256`. `EnforcementContext` admission requires both providers to bind exactly the supplied profile seal. A provider cannot be re-used with a different profile. Production provider ids are fixed, for example `git-readonly-v1` and `windows-real-fs-v1`; test providers use a `test-...` id and may be passed only with `kind=TEST` through the underscored direct-test routes.

Routing is exact:

| Caller | Route | Profile/providers | Override behavior |
|---|---|---|---|
| unchanged CLI `preflight` | public `preflight(...)` | always `PRODUCTION_CONTEXT` | no override parameter exists |
| unchanged CLI `build` | public `build(...)` | always `PRODUCTION_CONTEXT` | no override parameter exists |
| unchanged CLI `remediate` | public `remediate(...)` | always `PRODUCTION_CONTEXT` | no override parameter exists |
| unchanged CLI `verify` | public `verify(...)` | always `PRODUCTION_CONTEXT` | no override parameter exists |
| focused tests only | `_test_preflight/_test_build/_test_verify(..., context=...)` | sealed `TEST` profile plus profile-bound test providers | production-kind context or mismatched provider stops |

All seven wrappers call one `_execute(action, paths, context)` implementation. `_execute` runs the same context admission, repository/source/recovery gates, phase-ordered strict verifier, and failure codes. The underscored test wrappers do not implement a second verifier and do not bypass any production invariant. They only select a different complete authority and observation boundary.

The protected CLI remains byte-identical. It cannot parse a profile path, JSON, provider name, environment override, or test option. It imports only the four public functions, so a CLI caller cannot reach the test route without importing the library directly. AST/signature inspection may supplement QA, but it does not count as a mutation-matrix node.

### Real production identity and filesystem providers

The production identity provider performs only read-only observation:

1. resolve repository root with Git read-only;
2. read the current branch and exact HEAD with Git read-only;
3. observe the admitted local PDF's byte count/hash and 124 Letter pages with zero rotation using the existing local PDF observation path; and
4. never look at the sidecar external-locator value.

The production filesystem provider uses `os.lstat`/Win32 no-follow metadata. On Windows it records `st_file_attributes`, explicitly treats `FILE_ATTRIBUTE_REPARSE_POINT` (`0x400`) as forbidden, and records the reparse tag when available. A symlink, junction, mount point, cloud placeholder, dangling reparse entry, or any other reparse attribute fails even if `Path.exists()` is false or the target resolves inside the root. Enumeration is no-follow, ordinal, and rejects a type change between classification and read.

### Controlled Windows reparse testing without disabling checks

Tests do not require Administrator privileges, Developer Mode, or creation of a real junction. The test filesystem is a real temporary on-disk tree. Its classifier is the production classifier wrapped by an immutable single-entry overlay:

```python
@dataclass(frozen=True, slots=True)
class ClassificationOverride:
    normalized_path: str
    replacement: FileSystemEntry

@dataclass(frozen=True, slots=True)
class TestFilesystemProvider:
    real: "WindowsFilesystemProvider"
    overrides: tuple[ClassificationOverride, ...]
    provider_id: str
    bound_profile_sha256: str
```

For a reparse negative, the underlying file/directory really exists and all real bytes remain available. Exactly one `lstat` result is replaced with the same kind/size/file id plus `file_attributes | 0x400` and a controlled non-null reparse tag. The same production `_reject_reparse(FileSystemEntry)` function then emits the expected earliest code. No check is disabled, no fixture is skipped on Windows, and the case proves the Windows attribute branch rather than merely testing `Path.is_symlink()`.

## Shared strict verifier and exact earliest-failure order

The base packet's nine phases remain authoritative. The injection seam adds a pre-phase context admission; it does not reorder or weaken production checks.

0. **Context integrity:** complete/deeply immutable profile shape, profile seal, route kind, provider/profile binding. Codes in exact order: `E_PROFILE_INCOMPLETE`, `E_PROFILE_SEAL`, `E_PROFILE_ROUTE`, `E_PROVIDER_BINDING`.
1. **Repository authority:** provider root exists and is a non-reparse directory; correct-cwd/repo containment; exact root identity; exact branch; exact HEAD. Codes: `E_REPO_ROOT`, `E_REPO_CONTAINMENT`, `E_REPO_BRANCH`, `E_REPO_HEAD`.
2. **Path admission:** exact repo-relative source, sidecar, contract, recovery, and candidate/final target paths; normalized containment; ancestors from repo root to leaf; then roots/descendants in ordinal order. For each path classify before follow/read. Codes order by defect: `E_PATH_ARGUMENT`, `E_PATH_ESCAPE`, `E_PATH_REPARSE`, `E_PATH_TYPE`, `E_PATH_MISSING`. Build-target existence is checked here as `E_BUILD_OVERWRITE` before a temp sibling is created.
3. **Source/contract/recovery authority:** source path/bytes/hash/observation; sidecar raw hash then closed schema/fields/policy; contract raw/canonical/snapshot; source identity; recovery root/manifests/evidence, then the 209-row live payload bijection. Each raw transport failure precedes a semantic binding failure. The external locator is ignored as data and may never appear in `detail`.
4. **Forbidden classes then topology:** enumerate no-follow; reject the named PDF/compiled/cache/runtime/temp classes first, in ordinal relative-path order; only then report missing/extra/cardinality/closed-empty-subtree errors. Thus an inserted `x.pdf` fails with its specific forbidden code, not `E_TOPOLOGY_EXTRA`.
5. **Schema and closed shape:** the 16 exact schema strings in the base packet's listed order; required top-level members; unexpected top-level members; then row key shapes. QA schema/shape is checked here before stale QA semantics, preserving `REG-P1-STALE-METADATA -> E_QA_SCHEMA`.
6. **Inventory transport:** independently enumerate 501 non-QA files; validate normalized path syntax, uniqueness, ordinal order, byte counts, uppercase hashes, exact path set, row shape, and final LF digest, in that order.
7. **Evidence graph:** blocker ledger; page provenance; page Markdown/live render/master concatenation; content chains; navigation chain; assets/references/recovery bindings; entity/handout equality; content-mode/reference-only rows; role-derived 39/7/13/1 facts; 31-sheet live mappings. Within a document, identity/uniqueness/order precede cross-links, live bytes, and closure state.
8. **COMMANDS then QA policy:** COMMANDS schema/shape already passed phase 5; enforce action set/order, state, six false flags, argument fields, local source, counts, sheets, and determinism. Then enforce every QA authority, scalar, count, gate, boolean, inventory binding, and state. This preserves `REG-P1-MISSING-ENFORCEMENT -> E_COMMAND_COUNTS_PAGES` after only transport resealing.
9. **No fabricated closure:** reject any semantic, reading-order, placement, ownership, reconstruction-acceptance, promotion, release, or publication closure inconsistent with `candidate_needs_review` and the four open blockers.

The verifier never collects multiple errors and picks one later. It stops at the first code in this order. Enumeration and key traversal are ordinal, not locale-sensitive. A `CaseSpec` must state the exact expected code before execution; deriving the expected code from the observed exception is forbidden.

## Independent programmatic valid-bundle factory

### Factory surface

The focused test file owns these test-only types/functions:

```python
@dataclass(frozen=True, slots=True)
class BundleFixture:
    repo_root: Path
    contract_path: Path
    source_path: Path
    sidecar_path: Path
    recovery_root: Path
    run_root: Path
    profile: EnforcementProfile
    context: EnforcementContext
    manifests: tuple[tuple[str, str], ...]

def make_valid_bundle(root: Path, *, fixture_id: str) -> BundleFixture: ...

@dataclass(frozen=True, slots=True)
class ResealAuthority:
    name: Literal[
        "recovery_manifest", "recovery_evidence", "source_identity",
        "page_provenance", "content_provenance", "asset_provenance",
        "navigation", "commands", "inventory", "qa", "profile"
    ]

@dataclass(frozen=True, slots=True)
class MutationCase:
    case_id: str
    expected_code: str
    mutate: Callable[[BundleFixture], None]
    reseal: tuple[ResealAuthority, ...]
    expected_semantic_paths: tuple[str, ...]

def apply_case(case: MutationCase, bundle: BundleFixture) -> None: ...
def reseal_transport(bundle: BundleFixture,
                     authorities: tuple[ResealAuthority, ...]) -> BundleFixture: ...
```

The factory is independent of production files. It must not read the real source, sidecar, contract, recovery root, candidate, live QA/COMMANDS, prior receipts, or external locator; it must not invoke Git or external processes. A trap in the test filesystem provider fails any read outside the fixture repo root.

### Exact fixture topology and facts

Each call creates a new fixture repo and a candidate with exactly **502 regular files**:

| Candidate class | Files |
|---|---:|
| root: `SCENARIO_CONTRACT.json`, `SOURCE_IDENTITY.json`, `RECONSTRUCTED_EN.md`, `RECONSTRUCTED_EN.qa.json` | 4 |
| `pages/page-001.md` through `page-124.md` | 124 |
| ten evidence JSON documents, including `COMMANDS.json` | 10 |
| `engine/**`: five named recovered Markdown/JSON payload files plus 204 JPEGs | 209 |
| `renders/source/page-001.png` through `page-124.png` | 124 |
| `renders/contact_sheets/sheet-001.png` through `sheet-031.png` | 31 |
| **Total** | **502** |

`assets/`, `crops/`, and `ocr/` exist as empty directories and contribute no file. The separate recovery root has exactly 211 files: its two authority JSON files plus the same 209 payload bytes under `engine/**`.

The factory uses small but real deterministic bytes:

- a local fake source byte stream whose exact size/hash are profile authorities; the injected source observer returns 124 Letter pages, zero rotation, and deterministic per-page raster observations;
- canonical contract and sidecar JSON with the exact production schemas/policy fields and a fixture-local sentinel external locator that the trap provider proves is never accessed;
- four valid deterministic engine JSON files, one engine Markdown file, and 204 valid deterministic JPEG byte streams with unique hashes;
- 124 valid deterministic PNG render byte streams and 31 valid deterministic PNG 2x2 sheet byte streams, created with a stdlib deterministic encoder or a pinned in-test encoder with metadata/timestamps disabled;
- UTF-8/no-BOM/LF, sorted-key/two-space/final-LF JSON everywhere.

No hash, byte count, path mapping, or digest may be a placeholder. Every row is computed after its referenced bytes exist.

The deterministic logical model is:

- page numbers `1..124`, page ids `page-001..page-124`, engine indices `0..123`, and the exact contract role partition `1`, `2`, `3-4`, `5`, `6-68`, `69-103`, `104-110`, `111-123`, `124`;
- exactly 388 content blocks: three blocks on every page plus a fourth block on pages `1..16`; ids are `pNNN-bNNN`; each page has a closed local predecessor/successor chain and `PAGE_PROVENANCE.block_ids` in the same order;
- each page Markdown starts with its exact source-page marker, contains its exact render marker, and is derived only from that page's block bytes; `RECONSTRUCTED_EN.md` is exactly `b"\n".join(page_001_bytes ... page_124_bytes)`;
- exactly 204 asset rows and engine JPEGs; asset ids/paths/hashes are unique; the engine Markdown contains exactly one resolved image occurrence for assets `001..112`, and none for `113..204`; therefore referenced/unreferenced counts are exactly `112/92` and total Markdown references are `112`;
- exactly 124 navigation rows in the one-to-one adjacent chain with null first previous/null last next, live page/render paths and hashes, roles, and `needs_review` closure;
- exactly 39 entity rows and 39 byte-equivalent logical handout rows, ordinals `1..39`, unique ids/labels, deterministic page ranges within `69..103`, and `mixed` / `needs_review` state;
- exactly five content-mode review rows for pages `1..5`, `unknown -> mixed`, all `needs_review`;
- empty reference-only rows and `historical_material_opened=false`;
- exactly four open blocker rows with the base packet's ids and no closure alias;
- exact role-derived 7 map pages, 13 pregen pages, one back cover, and 39 handouts;
- exact existing COMMANDS schema/state/records/false flags/arguments/counts, 31 sheets, and 124 flattened render mappings; and
- exact QA v3 23-field shape, authority hashes, nine scalars, 14 counts, nine gates, booleans, state, and non-circular inventory.

There is no profile/manifest fixed-point. Before a test profile exists, the
factory owns a frozen `FixtureAuthoritySeed` containing every source,
contract, recovery, schema, count, state, and command-policy authority except
the candidate manifest values. A pure `plan_expected_bundle(seed, model)`
uses the same canonical byte constructors as the writer/finalizer to calculate
the expected 502/501/500 identities without touching disk. Candidate artifacts
do not serialize the profile seal or provider ids, so this plan is independent
of the later profile seal. The writer must still reconstruct and revalidate
all bytes; it may not copy a preplanned artifact map to disk.

Final factory sealing order is binding:

1. write fixture source, contract, and preliminary sidecar;
2. write the 209 recovery payload files;
3. compute and write the 209-row recovery manifest and recovery evidence from live bytes;
4. construct a complete frozen authority seed and the deterministic input-provider observations;
5. run the shared reconstruction-input validator to construct the immutable `ValidatedReconstructionInput` from the seed plus the real fixture source/recovery bytes;
6. compute the expected 502/501/500 identities in memory with `plan_expected_bundle`, complete and seal the `TEST_PROFILE`, and bind both test providers to that seal;
7. call the real `_test_build` into a fresh candidate root; do not directly synthesize candidate files through a second test writer and do not write the planned artifact map;
8. call `_test_verify` twice and require byte-identical success payloads;
9. independently enumerate the actual 502 all-file, 501 excluding-QA, and 500 excluding-QA-and-COMMANDS manifests and require exact equality to the precomputed profile authorities; and
10. return that same, already sealed profile/context. No post-build profile mutation or reseal is allowed for the positive fixture.

This makes the factory a programmatic producer of the actual writer/verifier contract, not a copied production fixture or a JSON mock.

## 368 executable negative mutations

### Exact count

The base packet's 363 negative selectors remain semantically binding. Five injection/route cases are added. The five former `POS` nodes are removed as separately collected tests; positive validity is proved by factory setup and by both verify calls for every case. The three build cases remain separate.

| Prefix | Executable negative nodes |
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
| **Negative total** | **368** |
| `BLD` real hermetic build cases | **3** |
| **Focused total** | **371** |

The five new named cases are:

1. `INJ-profile-seal-mutated -> E_PROFILE_SEAL`;
2. `INJ-test-route-given-production-profile -> E_PROFILE_ROUTE`;
3. `INJ-identity-provider-bound-to-other-profile -> E_PROVIDER_BINDING`;
4. `INJ-filesystem-provider-bound-to-other-profile -> E_PROVIDER_BINDING`;
5. `INJ-repository-root-observation-mismatch -> E_REPO_ROOT`.

The existing `TOP-root-reparse` and `TOP-nested-reparse` cases must use the controlled Windows classifier overlay described above and assert `E_PATH_REPARSE`. That is the required genuine reparse-attribute coverage; a skipped symlink/junction test does not satisfy it.

### One logical mutation and exact reseal algorithm

Every negative pytest node performs this executable protocol:

1. create a new `make_valid_bundle(tmp_path / case_id, fixture_id=case_id)`;
2. prove its two setup verifies already succeeded; setup failure fails the test and is not converted into the case's expected error;
3. snapshot every fixture file and the profile/provider seals;
4. execute exactly one `MutationCase.mutate`, whose semantic change is recorded as one path/JSON-pointer/provider/profile field with old/new identity;
5. compare the snapshot and require that only the declared semantic path/state changed before resealing;
6. run `reseal_transport` for exactly the authorities declared by that case, in the listed order;
7. compare again and require that every additional change is a declared transport reseal, never a semantic repair;
8. call the real `_test_verify` once;
9. require `ReconstructionStop` and exact equality `exc.value.code == case.expected_code`; and
10. assert no undeclared file/profile/provider change and no cache/temp/probe remains.

Transport resealing is deliberately narrow:

- QA is excluded from inventory, so a QA semantic mutation never reseals inventory.
- A candidate non-QA byte mutation reseals only the corresponding immediate live-byte row when the target case is deeper than that row, then recomputes the 501 QA inventory row/order/digest. It never changes the mutated semantic field.
- A `COMMANDS.json` semantic mutation reseals only the QA inventory row/digest; COMMANDS meaning is not repaired.
- A page Markdown or render mutation aimed at a downstream graph gate may reseal its `PAGE_PROVENANCE` byte/hash row, the relevant sheet mapping when applicable, and the QA inventory. A transport-case mutation intentionally omits that reseal.
- An engine JPEG mutation aimed at asset semantics may reseal the recovery manifest/evidence, profile recovery hashes, candidate asset live-byte binding, source identity, and QA inventory only when those authorities are explicitly listed. A recovery-authority case intentionally leaves the earliest relevant authority stale.
- A recovery JSON/payload mutation never mutates the candidate unless the specific case's declared deeper relation requires a separately rebuilt fresh fixture; ordinary negative cases do not run a second build.
- Profile resealing is permitted only for cases whose intended target lies after a changed fixture authority. It recomputes the complete test authority seal; it cannot omit a field or adopt the mutated semantic fact as an expected production truth unless that exact authority reseal is named.
- `INV` stale/missing/order/hash/path tests and the stale-metadata regression intentionally do not reseal the transport layer they are designed to break.

The mutation registry is executable data: every `MutationCase` stores a real callable, exact expected code, and exact reseal list. Generic ids such as `CMD-001` are insufficient in pytest output; ids must include the selector, for example `CMD-counts-pages-wrong`, `QAV-gate-promotion-closed`, or `PAG-render-hash-wrong`. A node that only checks registry membership, reads source text, asserts a constant exists, or asserts its own expected code is forbidden. Static source/signature checks are supplementary and not part of 371.

The two historical `REG` cases remain the only intentional multi-field semantic specimens exactly as defined in the base packet. They still start from a valid fresh fixture, record their declared cluster as one preserved historical specimen, reseal only transport, and assert the exact earliest code.

## Complete deterministic production writer

### Validated reconstruction input model

The writer never interprets arbitrary dictionaries while writing. Admission first constructs this immutable model:

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
    bytes: bytes
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

Required function signatures:

```python
def _load_validated_reconstruction_input(
    paths: "OperationPaths", context: EnforcementContext
) -> ValidatedReconstructionInput: ...

def _write_non_qa_bundle(
    staging_root: Path,
    model: ValidatedReconstructionInput,
    context: EnforcementContext,
    publication: "OwnedTempRoot",
) -> None: ...

def _finalize_and_verify(
    staging_root: Path,
    paths: "OperationPaths",
    context: EnforcementContext,
    publication: "OwnedTempRoot | None",
) -> dict[str, object]: ...
```

Production `_load_validated_reconstruction_input` admits only the exact local source, exact contract, and exact 211-file recovery authority. It validates the recovery manifest/evidence and all 209 payload bytes before constructing any model row. It uses the sealed production source observer for the 124-page observation/renders and the already recovered Markdown/four JSON/204 JPEG payload for content, block, reference, and asset facts. It does not run MinerU, OCR, GPU/model code, network, historical material, translation, or the external locator. Unresolved semantic/reading-order/placement/ownership facts remain explicit `needs_review`; the loader stops rather than inventing any required row.

The test loader consumes the independently generated source/recovery fixture through its sealed test identity/filesystem providers and produces the same model type. There is no alternate test writer and no model field may be omitted.

### Fixed non-QA output order

`_write_non_qa_bundle` uses create-new writes only inside the owned staging root, in this exact deterministic order:

1. create the fixed directories `pages`, `evidence`, `engine`, `renders/source`, `renders/contact_sheets`, `crops`, `assets`, `ocr`;
2. write canonical `SCENARIO_CONTRACT.json`;
3. write `SOURCE_IDENTITY.json` with current contract/source/recovery bindings and open state;
4. copy the 209 already validated engine payload files in recovery-manifest ordinal order, requiring copied bytes/hashes to match;
5. write `renders/source/page-001.png..page-124.png` in numeric order;
6. write `pages/page-001.md..page-124.md` in numeric order;
7. write `RECONSTRUCTED_EN.md` from the exact page bytes and joining rule;
8. write `renders/contact_sheets/sheet-001.png..sheet-031.png` in numeric order from pages `1..124`, four ordered pages per 2x2 sheet;
9. write the nine non-COMMANDS evidence documents in this order: `PAGE_PROVENANCE`, `CONTENT_PROVENANCE`, `ASSET_PROVENANCE`, `ENTITY_INVENTORY`, `HANDOUT_INVENTORY`, `NAVIGATION_INVENTORY`, `CONTENT_MODE_REVIEW`, `REFERENCE_ONLY_AUDIT`, `BLOCKER_LEDGER`; and
10. call `_finalize_and_verify`; the writer itself never writes `COMMANDS.json` or QA.

After step 9 there are exactly 500 files excluding QA and COMMANDS. The shared finalizer then:

1. validates the complete non-QA graph from live bytes;
2. constructs and writes stage-truthful `evidence/COMMANDS.json` once, including the `build` action for a fresh build while retaining the existing v3 schema and false external-tool flags;
3. independently enumerates the now-complete 501-file inventory excluding only root QA;
4. derives QA bytes twice in memory and requires exact equality;
5. writes QA once with canonical serialization; and
6. invokes the same `_strict_verify` pipeline against the staging root, with an immutable publication token that proves the staging root is the authorized physical stand-in for the final logical candidate root.

The verifier receives no reduced `build` mode. The publication token changes only physical-root admission: it binds one owned same-parent staging root to one exact absent final root. All 16 schemas, 502/501/500 topology, graph, COMMANDS, QA, state, count, reparse, and no-fabricated-closure invariants are identical.

### Fresh-root, atomic publication, and cleanup

`build()` performs this exact state machine:

1. run context/repository/path/source/sidecar/contract/recovery admission read-only;
2. classify the exact final `run_root` with no-follow metadata and require `missing`; an existing file, directory, symlink, junction, mount point, cloud/reparse entry, or dangling link is `E_BUILD_OVERWRITE`;
3. require the final parent to be the exact admitted scenario reconstruction parent, same volume, non-reparse, and writable only after all read-only admission passes;
4. create one unique hidden sibling named `.<final-name>.tmp-<pid>-<128-bit-random>` with exclusive `mkdir`; random naming affects only the temporary path, never artifact bytes;
5. capture an immutable `OwnedTempRoot` containing normalized parent/final/temp paths, provider/profile seal, directory file id, and an unguessable ownership nonce stored in a create-new marker outside the candidate inventory view;
6. load the validated input, write the fixed non-QA stage, finalize, and run strict verification on the staging root;
7. reclassify both temp and final; require the temp's file id/nonce/provider/profile binding unchanged and final still `missing`;
8. remove the private ownership marker, fsync/close files where supported, and publish with same-parent `rename_no_replace` (`os.rename`/Win32 move without replace-existing semantics, never `os.replace` over an existing target);
9. classify the final root and require the former temp file id, exact 502-file strict verify, and no temp sibling; and
10. return `built_candidate_needs_review` only after post-rename strict verify succeeds.

If another process creates the final target between steps 2 and 8, publication stops with `E_BUILD_PUBLISH_RACE`; it never replaces, deletes, merges, or edits that target.

Cleanup is narrow and fail-closed. On any pre-publish exception, `remove_owned_tree` may recurse only when the exact temp path is a same-parent child, its directory file id and ownership nonce still match, and every descendant classifies no-reparse. It uses no-follow deletion and may delete only entries under that exact owned temp. If ownership or reparse safety cannot be proved, it raises `E_BUILD_TEMP_OWNERSHIP`, leaves the temp for orchestrator inspection, and does not touch final/source/recovery/candidate paths. After successful rename the ownership token is consumed and cleanup is forbidden. No wildcard, computed parent deletion, general temp cleanup, retry, or final-root cleanup exists.

This atomic sibling design supersedes the base packet's partial-final-root rule. It is the packet-safe equivalent requested for Windows: the final target is either absent or a fully written and strictly verified candidate.

### Three real build nodes

The only `BLD` nodes are executable hermetic tests:

1. `BLD-fresh-root-success`: start with final root absent; call `_test_build`; require atomic publication, exact 502/501/500 topology, strict success, state `candidate_needs_review`, no temp sibling/marker, and no external/tool access.
2. `BLD-existing-target-refusal-no-mutation`: parameter body creates a nonempty existing target and snapshots it; call `_test_build`; require exact `E_BUILD_OVERWRITE`, byte/type/file-id equality, no created sibling, and no read beyond admission. File/directory/reparse variants remain mutations under the relevant negative families and do not add build nodes.
3. `BLD-finalizer-parity`: create two independent valid fixture inputs; one goes through `_test_build`, the other through `_write_non_qa_bundle` plus `_finalize_and_verify` in an owned staging root; require byte-identical relative file sets, `COMMANDS.json`, QA, 502/501/500 manifests, success payloads, and finalizer serialization.

No live build, live remediation, actual reparse-point creation, MinerU, OCR, network, GPU/model, external source, or historical input is needed by these tests.

## Preserved acceptance commands

After this amendment receives an independent `gpt-5.5` review with no open P0/P1, the resumed executor runs the base packet's commands unchanged from the exact worktree. There is still no live `build` or `remediate` command.

```powershell
Set-Location 'D:\NRI\.worktrees\kb-creator-viral'
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
```

Required results:

- focused collect-only: exactly 371 descriptive nodes = 368 executable negatives + 3 real builds;
- focused execution: exactly `371 passed`;
- combined collect-only/execution: exactly 490, with unchanged protected contract contribution 119;
- every negative receipt table row contains case id, one semantic mutation, declared reseals, exact earliest code, and pass;
- preflight and both live verifies exit 0 using only the admitted local PDF;
- the two verify stdout byte streams and SHA-256 values are identical;
- candidate/QA/COMMANDS/source/recovery/render/protected hashes remain exact; and
- no cache provider, `.pyc`, temp sibling, ownership marker, probe, or disposable fixture remains in the worktree.

## Exact resumed executor allowlist and receipt rewrite rule

The allowlist remains exactly three paths:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`; and
3. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_enforcement_completion_20260831.md`.

The CLI, contract library/tests, live candidate including QA/COMMANDS, source, sidecar, contract, recovery root, renders, prior packets/reviews, plan/context/status/README/release/publication, Git refs/index, and every other path are protected.

The existing receipt is reclassified only for this resumed window as an intermediate checkpoint, not a completed accepted receipt. One atomic same-path replacement is allowed under all of these conditions:

1. immediately before implementation and immediately before receipt write, its raw SHA-256 is exactly `E68DFB9658B2A9B70D77EC57F75FE1803D364E24F2323C8AC79150AF51F8E9B8`;
2. the replacement explicitly states `supersedes_intermediate_sha256` with that full hash and retains the prior `BLOCKED` result, prior command evidence, and both prior stop reasons in a `Superseded intermediate checkpoint` section;
3. it records this amendment's filename/hash and its accepted independent review filename/hash;
4. it reports the current pre/post library/test hashes, all command lines/exit codes/stdout hashes, the 368+3 coverage table, mutation/reseal audit, build tests, unchanged live bindings, result, blockers, token/elapsed use or `unavailable`, and forbidden-action declaration;
5. replacement uses an atomic temp-file write in the same handoff directory and replaces only this exact receipt file; and
6. after replacement the receipt becomes immutable. A later correction requires a new orchestrator-authorized artifact/amendment; it may not rewrite the path again.

If the resumed execution blocks before it can produce a truthful final replacement, the existing `E68DF...` receipt remains intact and the executor reports the blocker to the orchestrator without manufacturing completion. If code/tests changed and the result is blocked, the one replacement may truthfully record the new blocked state; it still becomes immutable. No append-in-place, silent erasure of the prior stop, or successor receipt path is authorized.

## Stop conditions

### Before first implementation write

Stop on any mismatch in:

- branch/HEAD/worktree;
- base packet or accepted review hashes;
- this amendment or its independent review identity;
- live partial library/test hashes `C797...C861` / `752C...796`;
- intermediate receipt hash `E68D...E9B8`;
- protected CLI/contract-test/source/sidecar/contract/recovery identities;
- live candidate 502/501/500, QA/COMMANDS, and 155/124/31 render identities;
- dispatch-window protected orchestration path/existence/length/hash snapshot;
- exact three-path allowlist; or
- critic outcome containing an unresolved P0/P1.

### After first implementation write

Stop and record a truthful blocked result on any:

- candidate/source/sidecar/contract/recovery/CLI/contract-test/orchestration/protected delta;
- external-locator access or appearance in a runtime command/error;
- missing/duplicate/generic case id;
- negative node without a real isolated mutation, declared reseal audit, and exact code assertion;
- focused count other than 371, negative/build split other than 368/3, combined count other than 490, or protected contribution other than 119;
- test, collection, hermetic build, preflight, or strict-verify failure;
- test path that invokes production providers, Git, real candidate/recovery/source, external process, network, MinerU/OCR/model, or historical input;
- public function/CLI override parameter, relaxed/skip flag, mutable/defaulted profile authority, or second verifier/finalizer/writer path;
- nondeterministic bytes, locale-dependent ordering, undeclared mutation, temp/marker/cache residue, unsafe cleanup, or rename-with-replace behavior;
- fabricated semantic/reading-order/placement/ownership closure, candidate promotion, Git mutation, staging, commit, or push; or
- inability to fit the fix into the same library/test/receipt allowlist.

Do not widen scope, edit the candidate, re-finalize live QA/COMMANDS, run live `build`/`remediate`, delete a non-owned path, or amend canonical orchestration state from the executor task.

## Mutation audit

The resumed executor repeats the base packet's complete pre/post audit and additionally records:

- canonical `PRODUCTION_PROFILE` serialization/seal and provider ids;
- every public and test-route signature;
- proof that the protected CLI hash and parser options are unchanged;
- case-id list SHA-256, exact family counts, and a machine-readable row per case containing semantic mutation identity, resealed authorities, and expected/observed code;
- factory read trap result showing zero reads outside each fixture root;
- per-build temp/final path state transitions and proof no temp/marker remains;
- byte-identical parity manifests for `BLD-finalizer-parity`; and
- exact receipt predecessor/replacement identities.

Pre-existing worktree dirt is not executor output. The executor records `git status --short --branch` before/after, does not normalize, stage, revert, delete, or claim unrelated paths, and reports only its three-path delta.

## QA and independent critic gates

Gate order is mandatory:

1. fresh independent `gpt-5.5` / `medium` architecture/process review of this amendment, with no designer/implementer participation and no open P0/P1;
2. resume the same bounded executor within the exact three-path allowlist and receipt rule;
3. separate bounded `gpt-5.6-luna` / `low` QA, read-only over implementation/candidate except its own new orchestrator-authorized QA receipt, that independently:
   - collects/runs 371 focused and 490 combined nodes;
   - verifies the 368/3 split and all descriptive ids;
   - samples every family and mechanically proves all 368 nodes call a mutation callable and `_test_verify` rather than a registry/source-string assertion;
   - checks the five injection cases and both controlled Windows reparse-attribute cases;
   - rebuilds at least one independent 502-file bundle and recomputes 502/501/500 manifests;
   - runs all three real build nodes and inspects temp ownership/no-replace cleanup evidence;
   - runs live preflight and verify twice, never live build/remediate;
   - recomputes all source/recovery/candidate/QA/COMMANDS/render/protected bindings and exact mutation set; and
   - confirms no external access, cache, `.pyc`, temp, marker, probe, candidate mutation, or Git mutation;
4. fresh independent `gpt-5.5` / `medium` implementation/process review, with no implementation/material-design/QA participation and no open P0/P1/P2; and
5. orchestrator integration only after all receipts are immutable and hash-bound.

The prior 67/67 original-resolution and 31/31 sheet visual QA may carry forward only under the unchanged base hashes and zero candidate-path mutation. These gates close only the enforcement-layer P1 and reusable-build P2. The live candidate remains `candidate_needs_review`; semantic/reading-order correctness, placement/layout fidelity, asset ownership/usage, and broader human review remain open. `MASTER_EN`, promotion, release, publication, staging, commit, and push remain unauthorized.

## Architecture-task mutation audit and handoff

This architecture task writes only:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_enforcement_injection_amendment_20260831.md`.

It does not edit code, tests, CLI, candidate, QA, COMMANDS, source, sidecar, contract, recovery, plan, context, status, README, release/publication artifacts, prior packets/receipts, or Git state. It does not run tests, preflight, verify, build, remediation, MinerU, OCR, GPU/model code, network, translation, or historical-material access. It does not access the external Yandex locator.

Safe next action: hash this immutable amendment, obtain the independent `gpt-5.5` architecture/process review, and resume the same executor only if that review returns no open P0/P1 and every pre-write binding still matches.
