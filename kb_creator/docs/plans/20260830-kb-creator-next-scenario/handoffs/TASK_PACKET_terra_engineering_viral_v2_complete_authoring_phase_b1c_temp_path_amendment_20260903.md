# Amendment — Phase B1c checkout-local temporary config paths

The B1c requirement to preflight an OS-temp config conflicts with the fixed
builder/verifier public APIs, which resolve checkout identity from the
publication-config path and require `.git` in an ancestor. No builder/verifier
API change is authorized.

Scoped override for the active B1c assignment:

- allow unique, initially absent temporary JSON files named
  `.phase-b1c-author-<uuid>.json` directly under
  `kb_creator/working/viral/master_en/`;
- permit only authoring, builder/verifier preflight reads and byte comparison;
- never create a candidate directory, canonical `publication_config_v2.json`,
  inventory, sidecar, or other output;
- remove every B1c temp JSON in `finally` cleanup, on success and failure;
- pre/post inventory must prove no B1c temp remains and no pre-existing path was
  modified;
- tests must cover collision refusal and cleanup after a forced preflight
  failure.

All other B1c ownership and immutability constraints remain unchanged. Record
this amendment path and its SHA-256 in the B1c receipt.
