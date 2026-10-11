# U4 implementation review task

Goal `20261004-user-docx-review`; independent critic `gpt-6-astra/high`.
Main `/root` owns orchestration; contributor must not implement/design fixes.
Own only `audit/critic-u4/` and immutable `handoffs/U4-critic-v01.md`.

Review kind implementation, not release. Inputs: U4v02 receipt/report and four
files module/CLI/tests/docs. Frozen SHA256 respectively
`0FA9FD43CFF650CDFF4D517875EED0994904199B0903A82614F0D7549EE3B27C`,
`D790565841816E1CF26C419EDE1EEF660877683AD921A133F6FC047D57BCFC71`,
`2BFE51469551DB57232ED8D5D4909EE03CF9546C2558EF5C6AB2E06CD954B600`,
`5AD911E726486B35549AF53EFD3B1F1437D371583CDEF9A61C7FFDB855F81BE8`.
No participation in implementation/design to date. Verify freeze then review
fail-closed manifest/source-domain enforcement, path/input preservation,
exact OOXML edits/native comments, occurrence matching/order and limits;
run focused tests through bundledPython. Synthetic fixtures permitted under
owned audit folder, production code changes forbidden. Existing unrelated dirty
test_innsmouth_source_to_artifacts.py is out of scope. No acceptance/commit/push.
Findings with exact code locators/repro and severity; compact result, blockers,
evidence/receipt. Record elapsed/token unavailable and independence declaration.
