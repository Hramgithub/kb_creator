"""Verify the immutable canonical repository copy of accepted Innsmouth MASTER_EN."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[1]
    / "inputs"
    / "innsmouth"
    / "master_en"
    / "accepted_20260830_r2"
)
EXPECTED_FILE_COUNT = 36
EXPECTED_ASSET_COUNT = 33
EXPECTED_TOTAL_BYTES = 9_505_083
EXPECTED_ROOTS = {
    "MASTER_EN.md": (
        127_769,
        "31F67A2865BF00A48F197333A162AD56AA0F56061068D3BFD6B564591F9AA3C2",
    ),
    "MASTER_EN.qa.json": (
        13_155,
        "3FD5FEA6D704B868447B0F3B431CE5D2F3CC13FB32E7B0CE342A8ED8CF1BFB08",
    ),
    "MASTER_EN.acceptance.json": (
        1_320,
        "971A9991E10652FFF482B1045EDBE963B929D84E0E23158E6DF80E3152C5AD9E",
    ),
}
EXPECTED_INVENTORY_SHA256 = (
    "D244FBE98E65119826A387F62B4A11ACB331935CB5D157D5656FF9B26A267241"
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def inspect(root: Path) -> dict[str, Any]:
    files = sorted(path for path in root.rglob("*") if path.is_file())
    rows = []
    for path in files:
        raw = path.read_bytes()
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "byte_count": len(raw),
                "sha256": sha256(raw),
            }
        )
    payload = {"schema": "InnsmouthAcceptedMasterEnInventory.v1", "files": rows}
    return {
        "root": str(root),
        "file_count": len(rows),
        "asset_count": sum(row["path"].startswith("assets/") for row in rows),
        "total_bytes": sum(row["byte_count"] for row in rows),
        "inventory_sha256": sha256(canonical_json(payload)),
        "files": rows,
    }


def verify(root: Path) -> dict[str, Any]:
    report = inspect(root)
    if report["file_count"] != EXPECTED_FILE_COUNT:
        raise ValueError("E_FILE_COUNT")
    if report["asset_count"] != EXPECTED_ASSET_COUNT:
        raise ValueError("E_ASSET_COUNT")
    if report["total_bytes"] != EXPECTED_TOTAL_BYTES:
        raise ValueError("E_TOTAL_BYTES")
    identities = {
        row["path"]: (row["byte_count"], row["sha256"]) for row in report["files"]
    }
    for name, expected in EXPECTED_ROOTS.items():
        if identities.get(name) != expected:
            raise ValueError(f"E_ROOT_IDENTITY:{name}")
    if report["inventory_sha256"] != EXPECTED_INVENTORY_SHA256:
        raise ValueError("E_INVENTORY_SHA256")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--inventory", action="store_true")
    args = parser.parse_args()
    report = verify(args.root)
    if args.inventory:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(
            json.dumps(
                {key: report[key] for key in (
                    "file_count",
                    "asset_count",
                    "total_bytes",
                    "inventory_sha256",
                )},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    print("INNSMOUTH_ACCEPTED_MASTER_EN_REPO_INPUT_OK")


if __name__ == "__main__":
    main()
