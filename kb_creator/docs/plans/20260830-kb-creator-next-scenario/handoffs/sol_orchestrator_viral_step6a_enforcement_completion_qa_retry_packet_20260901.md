# Viral Step 6A enforcement-completion QA retry packet

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6A-enforcement-completion-qa-retry`
- Owner: one fresh UI-visible bounded-QA task, `gpt-5.6-luna` / `high`
- Orchestrator: `gpt-5.6-sol` / `medium`
- Status: `prepared_not_authorized`
- Scope: evidence-only retry for the two findings in the fresh QA receipt

## Reason for retry

Fresh high-effort QA receipt
`luna_qa_viral_step6a_enforcement_completion_fresh_20260901.md`, SHA-256
`03965D28DC68CB9910F516B1949699CFBD2E63E23D0226F62024FAA45E181424`,
returned `BLOCKED` with no P0. It accepted the implementation/candidate checks
it could independently observe but left two evidence gaps:

1. P1: the exact combined suite was attempted but its final exit/result was not
   captured durably, so `490 collected / 490 passed` was not accepted;
2. P2: the permitted 67/67 visual-QA carry-forward was not independently
   re-proven against every accepted hash gate.

The completed QA chat `01a059d2-4ba6-7501-a8bb-53e182b82198` is archived and
must not be resumed. This retry requires a second, newly authorized, clean UI
QA task. Internal agents remain reserved exclusively for the independent
`gpt-5.5` critic.

## Immutable admission bindings

The retry stops before any test if a binding differs:

- worktree `D:\NRI\.worktrees\kb-creator-viral`;
- branch `codex/kb-creator-viral`;
- HEAD `54607bd3b9362adbb0c4bca64e8751482797f380`;
- executor successor receipt
  `luna_executor_viral_step6a_enforcement_completion_resume_20260901.md` =
  `8A48F339D74D33CB73B77B79AEE9CDF98E637CE06006CC047BB9180710CD13FE`;
- immutable intermediate executor receipt =
  `E68DFB9658B2A9B70D77EC57F75FE1803D364E24F2323C8AC79150AF51F8E9B8`;
- implementation =
  `E5AEEACB175AD20C900AB31998045DBA398714AD4936E03FF591A090429D4107`;
- focused tests =
  `B91A1F78F9F7D4D2E87FEA8A701F6877C47AA3443899883C538FCC3C7D93A31A`;
- candidate 502/501/500 manifests =
  `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA` /
  `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766` /
  `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`;
- candidate QA/COMMANDS raw hashes =
  `C38CB0A4667B1D4344C5E5DD91AEAAE7A2FD3101A3BB76611104EAA13BBD8FA6` /
  `9162651A456E12C7011081F999AA3B07EDB7EA9E66CA65CC78A0382456F12B06`;
- admitted source SHA-256 =
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
- prior visual-QA correction receipt =
  `194BF7EE471FF7E7DF859ED7958F7B3978F0F6C54536136C26CC6C6D1A7765DD`.

## Exact mutable allowlist

The new QA task may write only:

1. absent-before receipt
   `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_enforcement_completion_retry_20260901.md`;
2. exact disposable probe root
   `D:\NRI\_viral_step6a_enforcement_completion_qa_retry_probe_20260901`.

The probe must be absent at admission. It may contain only redirected pytest
stdout/stderr/exit-code files and a temporary directory routed through
`TEMP`/`TMP`. After all required evidence is copied into the receipt, remove
that exact probe with a literal-path command and prove it absent. No other
cleanup is authorized.

All implementation, tests, candidate, source, recovery, contract, CLI,
QA/COMMANDS, prior receipts, plan/context, Git/index/refs and external paths are
read-only. No network, MinerU, live build, remediate, promotion, staging,
commit, push or external Yandex access.

## P1 closure: durable exact combined-suite result

Set `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, point `TEMP` and `TMP` inside the exact
probe, and run these two commands from the worktree:

```text
python -m pytest -p no:cacheprovider --collect-only -q kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py
python -m pytest -p no:cacheprovider -q kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py
```

Do not rely on chat transport output. Redirect stdout and stderr to distinct
files under the probe and capture the native process exit code in a third file.
The receipt must include:

- exact command lines;
- exit code `0` for both collection and execution;
- stdout/stderr byte counts and uppercase SHA-256 values;
- the exact final collection and execution summary lines;
- independently parsed counts `490 collected` and `490 passed`;
- no unexpected warning/error text.

Any absent/truncated summary, non-zero exit, count other than 490/490, or output
that cannot be tied to its exact command is `BLOCKED` or `FAIL`, never PASS.

## P2 closure: exact visual carry-forward

Use the shared read-only `candidate_records()` and `manifest_digest()` helpers
from `kb_creator.scripts.scenario_source_reconstruction` against the live
candidate. Independently compute these complete-record subsets:

- every `renders/**` row: exactly 155 and
  `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A`;
- every `renders/source/**` row: exactly 124 and
  `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C`;
- every `renders/contact_sheets/**` row: exactly 31 and
  `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A`.

Also independently prove all carry-forward gates from the accepted enforcement
packet:

- prior visual-QA correction receipt hash remains `194BF7...765DD`;
- protected 500-manifest remains `98FC41...4C027`;
- QA/COMMANDS hashes remain `C38CB0...D8FA6` / `916265...12B06`;
- the implementation mutation audit and Git/worktree comparison contain no
  candidate-relative mutation from enforcement execution or this retry.

Only exact equality of every gate permits the statement that the prior 67/67
original-resolution plus 31/31 sheet visual QA carries forward. This does not
close semantic, reading-order, placement, ownership or usage review and does
not promote the candidate.

## Receipt and disposition

The receipt must record role/model/effort, assignment state, timestamps and
token use or `unavailable`; admission hashes; every command, exit code and log
hash; 490/490 evidence; all visual carry-forward hashes; pre/post protected
path comparison; exact writes; probe removal/absence; P0/P1/P2 findings; and
one unambiguous `PASS`, `FAIL` or `BLOCKED` result.

`PASS` closes only the fresh-QA evidence gap and authorizes the next internal
`gpt-5.5` implementation/process review. It does not accept Step 6A, start
semantic review, create `MASTER_EN`, publish, stage, commit or push.
