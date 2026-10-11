# Viral Step 7 MASTER_EN conservation config correction assignment

## Role and write scope

- Owner: bounded `gpt-5.6-sol` content/config role, `high`.
- Orchestration remains with `/root`.
- Edit only:
  - `kb_creator/working/viral/master_en/publication_config_v1.json`;
  - new immutable receipt `handoffs/sol_content_viral_step7_master_en_conservation_config_correction_20260901.md`.
- Builder/tests/verifier, accepted-v4 source/reconstruction, architecture receipts, plan/context, candidates/outputs, governance and Git are read-only. Preserve all other edits.

## Pinned current state

- Current config: 710,922 bytes, SHA-256 `C15934BB4EA7619505EE076D94BE56DA90C08F0B4DC0350A69A8C399EC7DBCAC`.
- Strict corrected builder: SHA-256 `3CEFD63C6B7EB7B921E276AC29742A12951B01C2593401ABB6B427CBD3933E18`.
- C1 correction receipt: `terra_engineering_viral_step7_master_en_binding_executor_correction_20260901.md`, SHA-256 `00D70E0745EFDB47E3F674FFAD508B6E95FB6BF9796FD4DC937C1A4DF2C9220D`.
- Read that receipt completely; its exact 45-page / 378-block distribution is authoritative for this correction.

## Required correction

The resolver already proves 168 bindings / 189 locators and fails closed on 378 unowned nonblank blocks: 140 parent-intro-before-child and 238 missing start/EOF continuation. Do not weaken the resolver or classify generic source disposition as ownership.

1. For every `b->anchor` row in the receipt, add an explicit exact `page_start` locator (or an already permitted equivalent explicit start) to the named owning parent so the page-leading intro/asset blocks end at the next child start. Preserve any existing parent heading locator and ordering.
2. For every `d->EOF` row, identify the exact preceding section/unit owner from accepted-v4/config topology and add the page to that binding's ordered `continuation_pages`, with any required explicit continuation-label locator. Never use a global page fallback.
3. Update `hierarchy.source_pages` and matching `source_disposition.target_anchors` only where needed for the new explicit ownership. Do not change lexical facts, titles, handout identity/order, asset ownership, structured facts, xrefs, pending gates or policy counts.
4. Preserve the already closed 168 bindings, unique order `1..168`, type-specific unit refs, p74/p75 shared-prefix ownership, p20-22 and p106-107 continuation behavior.
5. Run the current strict builder resolver in audit and normal modes. PASS requires all 1,935 nonblank accepted-v4 blocks to have exactly one explicit owner/classification, with `unowned=0`, `duplicate=0`, `unauthorized_suppression=0`; normal mode must no longer raise.
6. Report the new exact locator count, newly added page-start locator rows, new continuation pages/owners, any source-page/ownership updates and new config identity. No candidate or code/test edit is authorized.

The receipt returns `PASS_CONSERVATION_CONFIG`, `FAIL`, or `BLOCKED`; old/new config bytes/SHA, strict resolver counts/errors, changed bindings/pages, forbidden-output absence, elapsed time and token use if available. A PASS only unlocks rerunning the corrected C1 implementation tests; it does not authorize C2/candidate.
