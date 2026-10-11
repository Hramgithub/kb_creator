# Terra engineering assignment: Viral Step 6A explicit mutation and audit phase

## Authority and baseline

- Role: `gpt-5.6-terra / medium`, Fast/priority policy.
- Accepted design authority:
  `sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md`,
  especially sections 7.3 through 8.3, 11 and 12.
- Completed strict-graph foundation receipt:
  `terra_engineering_viral_step6a_strict_graph_fixture_completion_20260901.md`,
  SHA-256
  `5E5F27118A9D139243A52C3F258DC656219752B3E4C39679E8C0890514AFF55F`.
- Starting library SHA-256:
  `7A6F8459F9A4709DD4A42573B54733121C504E539C41CA0B1737E0822413808F`.
- Starting focused-test SHA-256:
  `EF99255D1F1B91268B27374EF2275865148C678CF36C4035FDF9AC7700497773`.

## Exclusive write allowlist

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. new receipt
   `terra_engineering_viral_step6a_explicit_mutation_audit_20260901.md`.

All source/candidate/recovery/CLI/contract/QA/COMMANDS production records,
config/governance/plan/context, prior receipts, caches and Git surfaces remain
read-only. No live command, external locator or network access is authorized.

## Required implementation

Replace the temporary generic 368 registry with the binding accepted protocol:

1. exactly 368 descriptive selector-specific negative rows with family counts
   `REP 2, SRC 18, AUT 30, TOP 21, SCH 33, LED 6, INV 18, PAG 28,
   NAV 15, AST 21, SEM 18, CMD 61, QAV 90, REG 2, INJ 5`;
2. the exact case ids and earliest error-code mappings enumerated in packet
   sections 8.1 through 8.3; generic ids such as `CMD-001`, `FAMILY-NNN`,
   shared marker mutators and expected codes derived from observed exceptions
   are forbidden;
3. a distinct callable identity and real case-specific semantic mutation for
   every row, its literal semantic selector, literal reseal tuple and literal
   allowed transport selectors;
4. independent production-shaped `make_valid_input` / `make_valid_bundle` using
   the real `_test_build` once and real `_test_verify` twice; no second writer;
5. real `reseal_transport` and `apply_case`: exactly one semantic change before
   reseal, only declared transport changes during reseal, no semantic repair,
   no undeclared changes, one strict verify call, exact earliest code;
6. a frozen/closed `MutationAudit` record and deterministic UTF-8/LF ordinal
   serialization with the exact section-11 fields, uppercase hashes, no
   absolute paths/source bytes/external locator, and a digest over all 368 rows;
7. each parametrized test must mechanically assert mutation callable identity,
   semantic before/after hash, declared/actual reseals, one verifier call,
   exact code, zero outside reads, zero undeclared changes and zero residue;
8. preserve the three existing BLD nodes as separate nodes, with no counted
   positive nodes, so collect/run remains exactly 371.

Static strings, family counts, generated numeric suffixes or one shared mutator
are not case proof. Table expansion is permitted only where it emits every exact
descriptive id, selector, callable, literal reseal and expected code before the
fixture is built.

## Evidence and receipt

- Use `python -B` and pytest `-p no:cacheprovider` only.
- Prove collect `371`, the family arithmetic and exact ordered id list, all 368
  negative executions, all 368 audit rows/digest, and the complete focused run.
- Do not run protected 119/combined 490 yet; integration phase owns those.
- Do not run live preflight/verify/build/remediate or delete `.pyc`.
- The immutable receipt must include a canonical machine-readable JSON block
  containing all 368 closed audit rows and digest, exact commands/native exits,
  stdout/stderr hashes, before/after file identities, path diff and protected
  surface check.
- Result may be `COMPLETE_PHASE2_PENDING_INTEGRATION` only if all requirements
  pass. Otherwise it is `BLOCKED` with exact case ids/symbols and technical cause.
