# Engineer handoff — Packet C P2 schema/runtime parity remediation

Date: 2026-09-14  
Role: engineering, user-scoped `gpt-5.6-sol` / `high`  
Finding: `critic_publication_packet_c_implementation_review_20260914.md` P2-1

## Result

P2-1 is remediated. The portable publication contract and stage-manifest
schemas now encode the exact adapter, package-role, and tool shapes already
used by the fixed production pipeline. A diagnostic proved that runtime's
former package-role subset check still accepted a duplicate role; after the
orchestrator narrowly widened ownership, runtime now enforces the same exact
unordered 22-role set before any run write.

No live source/output, acceptance, release state, Packet C adapter, canonical
plan/context/status, dependency, Git index, commit, or push was changed.

## Exact changes

### Scenario publication contract

- HTML and DOCX no longer share a generic arbitrary-string render adapter.
  Their separate closed definitions require respectively:
  - `translator_build_production_html_v1`;
  - `production_docx_explicit_config_v1`.
- `package.required_roles` is exactly 22 unique values drawn from the full
  `MANDATORY_PACKAGE_ROLES` set. Order remains free; missing, extra, unknown,
  and duplicate roles fail schema constraints.
- The five artifact-basename regular expressions were corrected to represent
  a literal backslash safely inside the JSON-encoded character class. The old
  expressions parsed as JSON but were invalid regular expressions; the schema
  regression now compiles each pattern.

### Publication stage manifest

- `tools` is a closed `oneOf`:
  - one exact injected-test record; or
  - exactly four unique fixed production records for repository Python,
    Poppler, PowerShell, and Microsoft Word COM.
- Every tool record is closed to `name`, `version`, and `scope`.
- Scope is restricted to the actual enum
  `injected_test | repository_tools | allowed_system`.
- Production versions require the actual `sha256:<64 uppercase hex>` form.
- Exact contains constraints and four-item cardinality prevent mixed injected/
  production shapes, missing tools, duplicate logical names, and arbitrary
  tool records.

### Runtime parity

`_validate_contract()` now requires `package.required_roles` to be a list with
exact cardinality, string values, no duplicates, and set equality with
`MANDATORY_PACKAGE_ROLES`. It does not impose a new order. Duplicate and
unknown-extra synthetic contracts fail in preflight before the run root exists.

## Tests

`test_publication_contracts.py` now covers:

- JSON parse plus compilation of artifact-name patterns;
- HTML/DOCX exact adapter constants;
- unknown and missing profile members;
- wrong adapter names;
- exact package-role cardinality/set and missing/extra/unknown/duplicate cases;
- closed tool records, allowed scope enum, exact injected and production
  alternatives, missing/unknown fields, bad scope, mixed shapes, and duplicate
  logical names.

The repository-local test environment intentionally has no `jsonschema`
package. No dependency was installed. Tests use the repository's established
JSON parse plus direct closed-schema regression method, including small focused
evaluators driven by the schema's own required/const/enum/cardinality data.

Focused schema-only result:

```text
6 passed in 0.21s
```

Focused schema + publication control plane + fixed registry E2E after runtime
parity correction:

```text
31 passed in 56.56s
```

The same three-suite command before the runtime correction was also green at
29 passed; the final 31 count includes the two new zero-write runtime negatives.

## Files

- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/contracts/publication_stage_manifest.v1.schema.json`
- `kb_creator/pipeline/publication.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_control_plane.py`
- this receipt

## Remaining risks

- This closes critic P2-1 but is not a release review or permission for a live
  Dissociation publication run.
- Full third-party Draft 2020-12 validation was unavailable without adding a
  dependency. JSON parsing, regular-expression compilation, exact schema-shape
  assertions, runtime preflight negatives, and the complete synthetic registry
  E2E are green.

## Final runtime-tool parity closure

The critic's follow-up correctly identified that the first remediation left
`_registry_tools()` more permissive than the stage-manifest schema. The runtime
is now exact and order-insensitive:

- an injected registry is either the existing all-`None` test declaration or
  the explicit single closed record
  `injected_publication_adapters / test / injected_test` on every stage;
- a production registry has exactly four unique names:
  `publication_python`, `pdftoppm`, `powershell`, and
  `microsoft_word_com`;
- scopes are exact by name: the first two are `repository_tools`, the latter
  two are `allowed_system`;
- every production version is exactly `sha256:` followed by 64 uppercase hex
  characters;
- every record has exactly `name`, `version`, and `scope`, with string values;
- declarations are normalized into the fixed production order before run
  identity creation and cross-stage comparison, so caller order is irrelevant;
- injected/production mixtures, cross-stage identity differences, extra or
  missing records, duplicate or wrong names, wrong scopes, lowercase/bad SHA,
  and extra fields fail before `_build_run()` and therefore before run-root
  creation.

Direct runtime regression:

```text
9 passed, 23 deselected in 1.63s
```

This includes exact explicit injected and order-varied exact production
positives plus the critic's malformed production probes: extra tool, lowercase
SHA, wrong name, missing Word, wrong scope, duplicate name, mixed injected and
production stages, and an extra record field. Every negative asserts the run
root remains absent.

Final schema + full publication control-plane + fixed registry E2E result:

```text
40 passed in 54.77s
```

Final runtime-tool parity changed only:

- `kb_creator/pipeline/publication.py` (`_registry_tools`);
- `kb_creator/tests/test_publication_control_plane.py`;
- this appended receipt section.
