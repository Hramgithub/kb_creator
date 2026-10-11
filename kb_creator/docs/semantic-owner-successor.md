# Add semantic owners after a lexical source-choice successor

`prepare_review_draft_semantic_owner_successor` in `kb_creator.pipeline.semantic_owner_successor` creates a new sealed author input when a reviewed R0 semantic spec adds owners after an existing lexical successor. It preserves the lexical input, draft pages, source-choice predecessor, ledger, queue, coverage dispositions, source issues, and corrections. The returned state is `prepared_pending_validation`.

```python
from pathlib import Path
from kb_creator.pipeline.semantic_owner_successor import prepare_review_draft_semantic_owner_successor

prepared = prepare_review_draft_semantic_owner_successor(
    lexical_input=Path("reviewed/lexical/review-draft-input.json"),
    binding_root=Path("working/book"),
    reviewed_spec_paths=[Path("reviewed/augmented-spec.json")],
    output_dir=Path("working/book/reviewed/owner-successor"),
)
```

The reviewed spec must keep the original R0 page domain, fields, existing unit definitions, and their order. Only new unique semantic unit definitions are allowed. The producer rebuilds those units from recorded R0 decisions and packets, checks the semantic graph, then projects them through the exact ledger slices into copied lexical specs. It binds the reviewed spec and lexical predecessor as additional provenance, and never rewrites existing inputs.

Pass `prepared["input_path"]`, `prepared["spec_paths"]`, and `prepared["draft_pages"]` to normal public `validate_spec`, followed by `author_drafts`, final review verification, materialization, and MASTER_EN verification. Those downstream steps reopen fresh source and archive authority. The prepared result is not an accepted source or publication artifact.
