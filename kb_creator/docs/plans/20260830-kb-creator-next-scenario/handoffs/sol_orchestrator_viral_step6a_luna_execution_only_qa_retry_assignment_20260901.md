# Luna/high execution-only QA retry: reliable per-command capture

**Owner:** fresh `gpt-5.6-luna/high` QA executor. **Scope:** exact execution and raw capture only.

This transport amendment inherits every baseline, command, gate, role boundary and prohibition from `sol_orchestrator_viral_step6a_luna_execution_only_qa_assignment_20260901.md` SHA-256 `66C7B4FDE690D525227A9BBDE32C67A81A56374178F903EEC2B5E0BE36730089`.

The first Luna receipt `luna_qa_viral_step6a_bld_full_integration_execution_only_20260901.md` SHA-256 `C21C9CE2F4AD35D30E4DD453ACF1363F5360F4FBEAF51212856B9B85C6CFC353` is immutable `BLOCKED`: a compound PTY transport lost all output after the first collect observation. It is not a test failure and not reusable evidence for commands 2–6.

## Sole write

Create only:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_bld_full_integration_execution_only_retry_20260901.md`

## Required transport

- Run every inherited child command separately, in the original order.
- One child per non-PTY `exec_command` call: `tty` false/omitted, `yield_time_ms` 30000, no compound sequence.
- If a session id is returned, use only `write_stdin` polling on that session until its native completion. Never start a duplicate.
- For each child, use the prepared in-memory byte capture envelope below. Set the tool output budget to at least 50,000 tokens for collect commands and 10,000 for run/live commands.
- After each successful child, immediately persist its complete JSON envelope in the sole receipt before starting the next child. The envelope contains base64 of the exact raw bytes, so no chat/PTY decoding is evidence.
- Stop immediately on non-zero child exit, missing envelope, invalid base64/hash, or count mismatch. Do not diagnose or fix.

Prepared envelope behavior, to be executed without semantic alteration:

```text
python -B -c "import base64,hashlib,json,os,subprocess,sys,time; label=sys.argv[1]; cmd=sys.argv[2:]; env=os.environ.copy(); env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'; started=time.perf_counter(); p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env); out={'label':label,'command':cmd,'native_exit':p.returncode,'elapsed_seconds':round(time.perf_counter()-started,6),'stdout_bytes':len(p.stdout),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest().upper(),'stdout_base64':base64.b64encode(p.stdout).decode('ascii'),'stderr_bytes':len(p.stderr),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest().upper(),'stderr_base64':base64.b64encode(p.stderr).decode('ascii')}; print(json.dumps(out,separators=(',',':'),sort_keys=True)); raise SystemExit(p.returncode)" LABEL CHILD_COMMAND_AND_ARGS
```

Replace only `LABEL` and `CHILD_COMMAND_AND_ARGS` with the inherited exact command label and literal argument vector. The child argument vector begins with `python -B ...`. Do not change pytest argument order or live command arguments.

After writing an envelope, decode both base64 values from the receipt itself and recompute byte counts and hashes. Parse the exact final summary. Required static results remain focused 371/371, protected 119/119, combined 490/490. Only then execute inherited live preflight and verify twice; require exits 0 and byte-identical verify stdout.

The first collect must be rerun in this fresh reliable transport; the prior observation is contextual only. Recompute all inherited pre/post hashes, manifests, cache inventory and residue proof. Never run build/remediate.

Luna may write the raw envelopes and a concise PASS/FAIL/BLOCKED synthesis into the sole retry receipt. That is evidence capture, not engineering. Luna must not create a script/helper/probe/log, edit any code/test/fixture/audit, or propose/perform remediation. Any failure returns to the separate Terra engineer after orchestrator review.

Timestamp: 2026-09-01 Europe/Moscow
