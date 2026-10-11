# Number 7 Dream commit preservation plan

## Objective

Prepare, but do not create or push, a scoped commit that preserves the reusable
KB Creator pipeline changes and the byte-frozen, offline-verified Number 7 Dream
production package. Plan the later cleanup of ignored working files and the
subsequent pipeline-change report as separate user-controlled steps.

## Ownership and boundaries

- Policy orchestrator: `gpt-5.6-sol`, medium; actual platform assignment
  unavailable. Main chat owns integration, canonical plan/context/status,
  staging scope, and stop/ask decisions. No scoped override.
- Engineering: `gpt-5.6-terra`, medium, if a bounded implementation step is
  needed; no assignment yet.
- Independent critic: `gpt-5.5`, medium, for a read-only frozen-package and
  commit-scope review; must not implement the reviewed material.
- Bounded QA: `gpt-5.6-luna`, low, if a separate verification task is needed.
- No commit, push, deletion, or cleanup is authorized by a preparation task.
  Original PDFs and user-created inputs remain immutable. Do not force-add
  ignored `working/**` intermediates.

## Tasks

| ID | Owner | State | Evidence / completion |
| --- | --- | --- | --- |
| P1 | orchestrator | done | Inventoried branch, ignored working boundary, package and manifest hashes |
| P2 | orchestrator | done | Copied 212 files to `inputs/number-7-dream/production/`; all bytes match; copied offline verifier passes |
| P3 | orchestrator | done with disclosed test drift | Staged 479 scoped files (212 frozen package), no `working/**` or forbidden scratch; package verifier passes; 580 tests pass, 2 stale Dissociation replay-fixture tests fail closed, 3 skip |
| P4 | independent critic | done | No HIGH/MEDIUM findings; immutable receipt `handoffs/P4-commit-scope-review.md`; 52.3 MB package size is a LOW Git-history risk |
| P5 | orchestrator | done | Staged inventory, verifier, test limitation, binary size risk and suggested commit message recorded in `context.md`; no commit/push |
| P6 | user + orchestrator | future | After commit authorization/completion, inventory working files and agree exact cleanup targets before deletion; only then author pipeline-change report |

## Definition of done for this request

The package copy is self-contained and offline-verified, staged files are
scoped to Number 7 Dream and reusable pipeline changes, forbidden scratch or
source files are absent, and the user can inspect the exact proposed commit.
The later cleanup and report are planned, not silently performed now.
