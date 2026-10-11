# U8 normal fidelity QA receipt v04

- Timestamp: 2026-10-04 23:01 UTC / 2026-10-05 02:01 Europe/Moscow.
- Goal: `20261004-user-docx-review`; U8 frozen normal-fidelity QA baseline.
- Role: bounded QA `gpt-6-luna` / medium (platform unverified). Policy owner/orchestrator: `/root`, gpt-6-sol / medium. Scoped override: none.
- Assignment state: prepared test baseline complete; critic checkpoint contains finite R1–R4 defects that remain open. This is not release approval.
- Elapsed time: approximately 17 active minutes. Token use unavailable.

## Scope/result

Verified the frozen 42-file U8v03 manifest (42/42 hashes and sizes; zero mismatches; manifest SHA-256 `5572A5C0C3FB9E660563D4BC9DB5CDEA1E352892CA58C6BAF6B021036765BB1D`) and ran the exact 19-module prepared regression suite with the bundled interpreter and the existing local pytest 9.0.2 library: **219 passed, 14 subtests, one pre-existing unrelated Word COM skip, zero failures/errors**. Normal-sandbox pytest scratch cleanup hit an actual WinError 5, so the same narrow suite passed on the authorized elevated retry in a fresh audit-local basetemp. An isolated contract-schema module passed 1/1 on the same retry.

Rehashed the six latest DOCX, three fixed candidate DOCX, canonical glossary and checked all nine retired-format paths; identities match the active checkpoint and paths remain absent. Post-run rehash again found zero v03 manifest mismatches. No code/test/fixture/book/source/latest/canonical/prior-evidence/release changes were made. The 367-page book QA is inherited by exact frozen identities and was not repeated.

## Evidence and files

- Detailed results, runner identity, exact module list, hashes, scratch paths, limits, and critic-finding separation: `audit/fidelity-qa-v04/U8-normal-fidelity-qa-v04.md`.
- Earlier checkpoint documenting the initial missing-pytest finding before root supplied the approved runner: `audit/fidelity-qa-v04/U8-fidelity-qa-checkpoint-v04.md`. Superseded for runner capability by this receipt; the earlier unavailable-pytest attempt was not represented as a completed test run.
- New test scratch roots retained under `audit/fidelity-qa-v04/pytest-basetemp-01` through `pytest-basetemp-04`; first full normal-sandbox run could not complete pytest cleanup, elevated full-suite retry completed.
- Frozen code/input authorities checked: `audit/fidelity-engineering/U8-v03-implementation-hashes.json`, engineer receipt/report v03, and six reviewed latest / three fixed candidate DOCX identities.

## Defects and next action

The independent critic interim checkpoint `audit/release-critic-v01/checkpoint-v01.md` records four separate adversarial findings: R1 incorrect partial/protected-field characteristic operand binding; R2 impossible physical-page and unreviewed-story domain acceptance; R3 accepted terminology mapping not resolved against the actual authority; R4 same-paragraph inline drawing order not enforced. These are not detected by the prepared passing regression result and remain open. Source paint discovery and real output visual review also remain explicit human boundaries. Main owns bounded remediation, new freeze and follow-up QA; final independent critic review and release decision remain pending.

The engineer-reported standalone 23-pass and seven-module 77-pass counts were not independently rerun; this receipt relies on the full 219-test 19-module prepared suite as the bounded baseline. No code or test repairs are included.
