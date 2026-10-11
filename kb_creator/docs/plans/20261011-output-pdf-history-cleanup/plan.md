# Goal plan: generated PDF history cleanup

- Goal ID: `20261011-output-pdf-history-cleanup`
- State: `completed`
- Objective: remove two obsolete Innsmouth PDFs from the standalone repository
  and its one-commit history, preserve the historical reports, refresh the
  model handoff for the new baseline, and safely replace remote `main`.
- Policy orchestrator: `gpt-6-sol`, medium reasoning.
- Actual orchestrator model/effort: unavailable.
- Scoped override: none.

## Ownership

| Step | Owner | Requested effort | State |
|---|---|---:|---|
| C1 preflight and exact-target verification | main-chat orchestrator | medium | completed |
| C2 local deletion and root-commit rewrite | main-chat orchestrator | medium | completed |
| C3 handoff refresh and integration | main-chat orchestrator | medium | completed |
| C4 bounded repository QA | `gpt-6-luna` QA | medium | completed; v02 pass |
| C5 independent release review | `gpt-6-astra` critic | high | completed; approved |
| C6 guarded force-with-lease publication | main-chat orchestrator | medium | completed |

The critic must not implement or materially redesign the candidate.

## Exact deletion scope

1. `kb_creator/output/innsmouth_final/runs/20260730T172713Z/Pdf/The_Innsmouth_Terror_Full_RU_two_column.pdf`
2. `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/Pdf/The_Innsmouth_Terror_RU.pdf`

These are generated historical outputs. Their reports and manifests remain.
The accepted Innsmouth package under `kb_creator/inputs/innsmouth/pdf/` remains.
The original NRI checkout remains untouched.

## Preconditions

- local and remote `main` both equal
  `91db0491f3fa0876ab0c44d45151f8006f812d5a`;
- the standalone repository has exactly one commit before the rewrite;
- both targets resolve inside the standalone repository and are tracked;
- the only pre-existing uncommitted state is the intentional model-handoff
  documentation;
- user approved the described deletion, history rewrite, handoff refresh, and
  guarded replacement of remote `main`.

## Steps

1. Remove the two exact files and rely on the existing default-deny allowlist
   plus generic PDF rules to prevent their accidental re-addition.
2. Amend the single import commit without adding the uncommitted handoff files.
3. Confirm neither PDF exists in the rewritten reachable history.
4. Update handoff facts, counts, baseline commit, and release identity.
5. Commit the refreshed handoff and cleanup goal packet as a second commit.
6. Obtain bounded QA and a separate independent release recommendation.
7. Fetch and require the remote lease to remain at the approved old commit,
   then push `main` with `--force-with-lease`.
8. Verify remote identity, file absence, reachable object absence, LFS state,
   and clean working tree.

## Definition of Done

- neither target exists in `main` or any reachable commit;
- remote `main` is replaced only if its old identity still matches the lease;
- no other project payload is deleted;
- accepted inputs, reports, manifests, source code, tests, and small historical
  artifacts remain;
- handoff documents state the new baseline and no longer describe the GitHub
  large-file warning as current repository state;
- QA passes and the independent critic approves the exact release candidate;
- final local `main` equals `origin/main` and the working tree is clean.
