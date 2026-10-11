from __future__ import annotations

import argparse
from pathlib import Path

import compare_innsmouth_artifacts as compare


def write_page_dump(
    candidate_keeper: Path,
    reference_keeper: Path,
    pages: list[str],
    out_path: Path,
) -> None:
    candidate_text = candidate_keeper.read_text(encoding="utf-8")
    reference_text = reference_keeper.read_text(encoding="utf-8")
    candidate_pages = compare.page_blocks(candidate_text)
    reference_pages = compare.page_blocks(reference_text)

    lines: list[str] = [
        "# Innsmouth Page Delta Dump",
        "",
        f"Candidate: `{candidate_keeper}`",
        f"Reference: `{reference_keeper}`",
        "",
    ]
    for page in pages:
        candidate = compare.normalize_page_reader_text(candidate_pages.get(page, ""))
        reference = compare.normalize_page_reader_text(reference_pages.get(page, ""))
        lines.extend(
            [
                f"## Page {page}",
                "",
                f"- candidate chars: `{len(candidate)}`",
                f"- reference chars: `{len(reference)}`",
                f"- delta chars: `{len(candidate) - len(reference)}`",
                "",
                "### Candidate",
                "",
                "```text",
                candidate,
                "```",
                "",
                "### Reference",
                "",
                "```text",
                reference,
                "```",
                "",
            ]
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-keeper", required=True, type=Path)
    parser.add_argument("--reference-keeper", required=True, type=Path)
    parser.add_argument("--pages", nargs="+", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    write_page_dump(
        candidate_keeper=args.candidate_keeper,
        reference_keeper=args.reference_keeper,
        pages=args.pages,
        out_path=args.out,
    )
    print(f"wrote={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
