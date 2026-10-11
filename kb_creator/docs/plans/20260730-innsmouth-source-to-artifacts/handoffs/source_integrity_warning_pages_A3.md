| page | status | evidence | recommended action |
| --- | --- | --- | --- |
| 013 | ok | Visual check of source PDF page 013 shows normal reading flow: left column finishes the Karen Jeffries/Advertiser section, then right column starts `THE MISKATONIC PLAYHOUSE`. Audit warning is explained by the right-column first line being the running header `arKham`, not a sentence continuation. `Normalized_EN` preserves the full left-column paragraph and then the Playhouse section; counts remain near-equal (`char_delta=1`, `block_delta=0`, `similarity=0.99829`). | Mark `possible_cross_column_sentence_split` as false positive for page 013. No pipeline change needed. |
| 016 | ok | Visual check of source PDF page 016 shows standard two-column layout: left column is `THE GILMAN HOUSE HOTEL`, right column begins `THE PRODUCTION TRAIN CAR`. Audit warning is explained by the page header `Innsmouth` and cross-column page design, not by broken sentence flow. `Normalized_EN` matches the page structure and audit metrics are exact for the current extractor (`char_delta=0`, `block_delta=0`, `exact_against_current_extractor=true`, `similarity=1.0`). | Mark `possible_cross_column_sentence_split` as false positive for page 016. No pipeline change needed. |

Pages covered: `013`, `016`.

Blockers: none for this narrow check.

Time: approximately `15m` active review.

Tokens: approximate, unavailable exactly in this surface.
