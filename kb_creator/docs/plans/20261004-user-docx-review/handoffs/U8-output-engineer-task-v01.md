# U8 ordinary pipeline DOCX-only output change

Goal `20261004-user-docx-review`; engineer gpt-6-sol/high, main orchestrates.
Captured U7conversionplanningreceipt; immediate follow-up, nocardauthoring here.
User explicitly requests removing HTML/PDF build from pipeline, not only avoiding
their delivery. DOCX-only route is authoritative; originalPDFinputs remain.
You are not alone. Own `scripts/production_docx.py`, `pipeline/five_step_docx.py`,
normalDOCX continuation/runner/successor/CLI seams strictly needed for this
change, matching tests/docs, and `audit/output-policy/` plus immutable
`handoffs/U8-output-engineer-v01.md`. Coordinate file ownership before extending
other seams. Never touch reviewed_docx_revision.py or sourceQA/cardledgers.

Read U8architecturev01 and DOCXscopeaddendum, README/status/currentnormalroutes.
Remove standaloneHTML and publishedPDF outputs from active ordinaryDOCXbuild.
ExistingfiveStep currently writes internal.html and builder reparses it twice.
Refactor reusableWordbuilder/semanticpatch to accept validated in-memory parsed
projection plus explicitassetbase; preserve heading/layout/richtext/tables/
bookmarks/comments and all existing readerproofs. Do not write temporaryHTML
just to satisfy an oldfile API. SourceMarkdown/masters remain sourcefaithful.
Internal DOM/text transport is implementation-only, not an emittedHTMLartifact.

Normal new DOCXprofile/package needs unambiguous version change if sealed
fields/contracts change. Oldsealedpackages immutable/read-onlylegacyverified,
no false currentready. No serializingHTML/PDF in newDOCXoutput/inventory and
no HTML input required when existing reviewedWord revised. TransientWord
PNGservice render remains separateQA, privatebridge removed, neverpublishedPDF.
No sourcePDFdeletion, renderingengineinstallation, originalbookwrites, commitpush.

Inspect neutralpublication legacyHTML/PDF stages/directCLI: ensure they cannot
be invoked as currentDOCXpipeline outputs. Prefer explicit deprecation/fail-before-
write for obsolete fullHTML/PDF publication route and route caller to DOCXprofile,
rather than silently skipping mandatorysealedgraph stages. Do not implement a
newPDFpipeline; user says PDF has separatepipeline. Existing archival verifier
mayverifyoldsealedpackages honestly, not regenerateoldformats. Report exact
compatibilityboundary and any materially broader dependency before changing it.

Tests: DOCX-only newnormalbuild actually has noHTML/PDF files; projectionfrom
in-memorysource preserves currentsemantic witnesses/rich runs/tables/images/
links/captions; direct route/continuation/successor can't emit prohibitedformats;
obsoleteHTML/PDF command fails beforewriting, oldarchive readonlyverification
still works. Relevantfocusedregressions, not source-code-stringtests. No actual
userbook rebuild from absentmasters. Detailed local report+hashes/receipt,
compactreturn result/coverage/blockers. Independentcritic later, not acceptance.

Source-art/edition mandatoryguard implementation is a following bounded U8step
after currentbooks, not falsely closed by this output-policy change.
