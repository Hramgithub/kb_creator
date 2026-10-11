# Invocation-owned V2 ledger snapshots

`author`, `validate_spec`, and `author_drafts` each create a private ledger registry. The registry opens one immutable snapshot per resolved V2 ledger path. Opening reads the ledger, validated submission, and bound queue bytes; runs the existing full `verify_ledger_v2`; then requires the three files to remain byte-identical. Issue domains must be unique and equal. The parsed values and issue maps contain read-only mappings and tuples.

V2 selectors, semantic validation, and the Stage05 audit consume that invocation's snapshot. Their individual shape, selection, anchor, replay, and lineage checks still run. A private call-scoped lookup carries the snapshot into semantic validation; standalone validators and public `audit_v3_content` keep their own full ledger verification boundary. No serialized flag or persistent cache grants authority. The registry rejects a mismatched owner token.

Immediately before output publication, the author runs `verify_ledger_v2` again for each opened ledger and compares the exact ledger, submission, and queue bytes to the opening snapshot. This reopens transitive authority such as Stage04 packets. `author_drafts` publishes only after Stage05/06 and final evidence; failure removes cold staging. Direct `author` also stages its output before this final check. `validate_spec` performs the check before writing an optional candidate output.

The snapshot scope covers one top-level invocation. Another invocation opens and verifies a new snapshot. V1 correction selectors continue through their existing path.
