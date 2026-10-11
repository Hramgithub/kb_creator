from __future__ import annotations

from typing import Any

from .identity import canonical_bytes, sha256_bytes


HEX_DIGITS = frozenset("0123456789ABCDEF")


def is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and set(value).issubset(HEX_DIGITS)
    )


def sealed(
    schema: str,
    value: dict[str, Any],
    *,
    digest_key: str,
) -> dict[str, Any]:
    result = {"schema": schema, **value}
    result[digest_key] = sha256_bytes(canonical_bytes(result))
    return result


def validate_seal(value: dict[str, Any], digest_key: str) -> None:
    digest = value.get(digest_key)
    if not is_sha256(digest):
        raise ValueError(f"invalid {digest_key}")
    unsigned = {key: item for key, item in value.items() if key != digest_key}
    if sha256_bytes(canonical_bytes(unsigned)) != digest:
        raise ValueError(f"{digest_key} mismatch")
