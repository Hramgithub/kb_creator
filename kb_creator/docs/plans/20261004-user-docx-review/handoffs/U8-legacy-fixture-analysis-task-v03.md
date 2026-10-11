# U8 legacy sealed fixture dependency analysis

Goal `20261004-user-docx-review`; architect gpt-6-astra/high. Main orchestrates;
output engineer owns implementation/test migration. You are not alone.
Bounded read-only question, no code/tests/book/schema/canonical state edits.
Own only new `audit/legacy-fixture-analysis/` and immutable
`handoffs/U8-legacy-fixture-analysis-v03.md`.

Read current `tests/test_publication_control_plane.py`, its fixture helpers,
`pipeline/publication.py` read-only `verify_production_package` dependencies,
relevant package contracts and offline verifier. Public legacy generation is
retired before write. Engineer is migrating writer-only tests and other suites;
your distinct responsibility is the minimal sealed TEST ARCHIVE fixture needed
for existing negative read-only package-verification assertions.

Provide exact required files/field/seal/hash dependency graph, smallest usable
test-only construction path or existing compatible fixture, and limits. No
production bypass flag, monkeypatched production writer, skipped verifier tests,
weakened validation or resealed actual historical package. Do not implement the
fixture; send compact executable construction specification to engineer/main,
with source paths/locators and proof of consistency from the verifier contract.

Finite completion: exact minimal archive fixture recipe plus which negative
assertions it supports and any unresolved dependencies. Detailed owned report,
immutable receipt with role/effort/scope/evidence/time/token unavailable if not
observable, compact return. No release decision; you previously designed U8 and
are not eligible as independent release critic.
