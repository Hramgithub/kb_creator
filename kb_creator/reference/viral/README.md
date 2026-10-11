# Viral reference policy

This directory preserves declarative reference evidence for the `Viral`
scenario. It is not reusable scenario-neutral mechanics and is not a
self-contained clean-checkout build input.

`../../contracts/viral.json` is the Viral-specific topology and intake-policy
contract. `master_en/publication_config_v1.json` is the frozen Viral MASTER_EN
publication-policy record. Its required identity is `713722` bytes and SHA-256
`C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

The publication config binds source-derived reconstruction and review evidence
that deliberately remain outside this reference directory. It must not be
treated as sufficient input to reproduce a reader candidate in a clean
checkout. Existing frozen working configuration and candidates remain their
own evidence; a future run may use this copy only after proving byte identity
and opening a new authorized run.
