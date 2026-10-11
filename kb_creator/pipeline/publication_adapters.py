from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Sequence
from urllib.parse import urlsplit

from .identity import canonical_bytes, file_identity
from .manifests import sealed
from .publication import ADAPTER_NAMES, DOCX_ONLY_ROUTE, STAGES, PublicationStageAdapter, PublicationStageInvocation


REPO_ROOT = Path(__file__).resolve().parents[2]
TRANSLATOR = REPO_ROOT / "translator" / "translator.py"


class PublicationAdapterError(ValueError):
    pass


HTML_POLICY_SCHEMA = "kb_creator.html_publication_policy.v1"
HTML_POLICY_SCHEMA_V2 = "kb_creator.html_publication_policy.v2"


def _page_markers(markdown: str) -> list[int]:
    return [int(value) for value in re.findall(r"^<!--\s*(?:source-page|pdf-page)-(\d{3})\s*-->\s*$", markdown, re.M | re.I)]


def _stage40_html_policy(config: dict[str, Any], master: Path) -> dict[str, Any]:
    """Compile the closed source policy and reject an unconsumed future config."""
    raw = config.get("html_publication_policy")
    if raw is None:
        # Compatibility is deliberately narrow: only a complete legacy config
        # with the same explicit facts can be normalized.  Omission remains an
        # error; in particular, source contents cannot rely on title guessing.
        page_map = config.get("page_map")
        frontmatter = config.get("frontmatter")
        production = config.get("production_html")
        toc_policy = production.get("toc_policy") if isinstance(production, dict) else None
        credits_policy = production.get("credits_policy") if isinstance(production, dict) else None
        if not all(isinstance(value, dict) for value in (page_map, frontmatter, toc_policy, credits_policy)):
            raise PublicationAdapterError("HTML publication policy is missing or has an unknown schema")
        roles: list[dict[str, Any]] = []
        for page, meta in page_map.items():
            try:
                source_page = int(str(page))
            except ValueError as error:
                raise PublicationAdapterError("legacy HTML page map is invalid") from error
            role = meta.get("type") if isinstance(meta, dict) else None
            if role in {"cover", "credits", "source_toc", "body"}:
                roles.append({"source_page": source_page, "role": role})
        roles.sort(key=lambda row: row["source_page"])
        cover = frontmatter.get("cover") if isinstance(frontmatter.get("cover"), dict) else {}
        body_pages = [row["source_page"] for row in roles if row["role"] == "body"]
        source_page = toc_policy.get("source_page")
        try:
            legacy_cover_page = int(str(cover.get("page")))
            legacy_source_page = int(str(source_page)) if source_page is not None else None
        except (TypeError, ValueError) as error:
            raise PublicationAdapterError("legacy HTML frontmatter pages are invalid") from error
        raw = {
            "schema": HTML_POLICY_SCHEMA, "state": "stage40_ready", "page_roles": roles,
            "frontmatter_order": frontmatter.get("order"), "cover": {"source_page": legacy_cover_page},
            "credits": {"mode": credits_policy.get("mode"), "source_pages": [row["source_page"] for row in roles if row["role"] == "credits"]},
            "toc": {"mode": toc_policy.get("mode"), "source_page": legacy_source_page, "title": toc_policy.get("source_title", ""), "entries": toc_policy.get("entries")},
            "body_start_page": body_pages[0] if body_pages else None,
        }
    if not isinstance(raw, dict) or raw.get("schema") not in {HTML_POLICY_SCHEMA, HTML_POLICY_SCHEMA_V2}:
        raise PublicationAdapterError("HTML publication policy is missing or has an unknown schema")
    state = raw.get("state")
    if state == "deferred":
        if set(raw) != {"schema", "state"}:
            raise PublicationAdapterError("deferred HTML publication policy must be closed")
        raise PublicationAdapterError("deferred HTML publication policy is not Stage-40 ready")
    required = {"schema", "state", "page_roles", "frontmatter_order", "cover", "credits", "toc", "body_start_page"}
    if state != "stage40_ready" or set(raw) != required:
        raise PublicationAdapterError("HTML publication policy must be closed and stage40_ready")
    roles = raw["page_roles"]
    if not isinstance(roles, list) or not roles:
        raise PublicationAdapterError("HTML publication policy lacks ordered page roles")
    pages: dict[int, str] = {}
    allowed_roles = {"cover", "credits", "source_toc", "body"}
    for row in roles:
        if not isinstance(row, dict) or set(row) != {"source_page", "role"} or type(row["source_page"]) is not int or row["source_page"] < 1 or row["role"] not in allowed_roles or row["source_page"] in pages:
            raise PublicationAdapterError("HTML publication policy page roles are invalid")
        pages[row["source_page"]] = row["role"]
    if [row["source_page"] for row in roles] != sorted(pages):
        raise PublicationAdapterError("HTML publication policy page roles are not ordered")
    markers = _page_markers(master.read_text(encoding="utf-8"))
    if any(page not in markers for page in pages):
        raise PublicationAdapterError("HTML publication policy page role is absent from accepted MASTER_RU")
    cover = raw["cover"]
    credits = raw["credits"]
    toc = raw["toc"]
    if not isinstance(cover, dict) or cover.get("source_page") not in pages or pages[cover["source_page"]] != "cover":
        raise PublicationAdapterError("HTML publication policy cover is invalid")
    if raw["schema"] == HTML_POLICY_SCHEMA:
        if set(cover) != {"source_page"}:
            raise PublicationAdapterError("HTML v1 publication policy cover is invalid")
    else:
        if set(cover) != {"source_page", "placement_id", "required", "render_mode", "fit"} or not isinstance(cover.get("placement_id"), str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", cover["placement_id"]) or cover.get("required") is not True or cover.get("render_mode") != "replace_source_page" or cover.get("fit") not in {"contain", "cover"}:
            raise PublicationAdapterError("HTML v2 publication policy requires an explicit required cover placement")
    if not isinstance(credits, dict) or set(credits) != {"mode", "source_pages"} or credits.get("mode") not in {"none", "source_authored"} or not isinstance(credits.get("source_pages"), list):
        raise PublicationAdapterError("HTML publication policy credits is invalid")
    if len(set(credits["source_pages"])) != len(credits["source_pages"]) or any(type(page) is not int or pages.get(page) != "credits" for page in credits["source_pages"]) or ((credits["mode"] == "none") != (not credits["source_pages"])):
        raise PublicationAdapterError("HTML publication policy credits roles disagree")
    toc_keys = set(toc) if isinstance(toc, dict) else set()
    if not isinstance(toc, dict) or toc_keys not in ({"mode", "source_page", "title", "entries"}, {"mode", "source_page", "title", "entries", "display_mode"}) or toc.get("mode") not in {"generated", "preserve_and_link"} or not isinstance(toc.get("entries"), list) or not isinstance(toc.get("title"), str):
        raise PublicationAdapterError("HTML publication policy TOC is invalid")
    if toc.get("display_mode", "source") not in {"source", "flat"}:
        raise PublicationAdapterError("HTML publication policy TOC display mode is invalid")
    if toc["mode"] == "generated":
        if toc["source_page"] is not None or toc["entries"] or any(role == "source_toc" for role in pages.values()):
            raise PublicationAdapterError("generated TOC policy cannot carry source contents")
    else:
        if type(toc["source_page"]) is not int or pages.get(toc["source_page"]) != "source_toc" or not toc["entries"]:
            raise PublicationAdapterError("source TOC policy lacks its declared source page or entries")
        seen_entries: set[str] = set()
        for entry in toc["entries"]:
            entry_keys = set(entry) if isinstance(entry, dict) else set()
            if (
                not isinstance(entry, dict)
                or entry_keys not in ({"source_text", "target_id"}, {"source_text", "target_id", "display_level"})
                or not all(isinstance(entry.get(key), str) and entry[key].strip() for key in ("source_text", "target_id"))
                or ("display_level" in entry and (type(entry["display_level"]) is not int or not 1 <= entry["display_level"] <= 6))
            ):
                raise PublicationAdapterError("source TOC entry mapping is invalid")
            if entry["source_text"] in seen_entries:
                raise PublicationAdapterError("source TOC entry mapping is duplicated")
            seen_entries.add(entry["source_text"])
    body_start = raw["body_start_page"]
    if type(body_start) is not int or pages.get(body_start) != "body":
        raise PublicationAdapterError("HTML publication policy body start is invalid")
    order = raw["frontmatter_order"]
    expected_order = [
        "cover",
        *(["credits"] if credits["source_pages"] else []),
        "source_toc" if toc["mode"] == "preserve_and_link" else "toc",
        "body",
    ]
    if order != expected_order:
        raise PublicationAdapterError("HTML publication policy frontmatter order disagrees with roles")
    return raw


def _apply_stage40_html_policy(config: dict[str, Any], policy: dict[str, Any]) -> None:
    """Expose one normalized policy to every renderer phase; no split defaults."""
    page_map = {f"{row['source_page']:03d}": {"type": row["role"]} for row in policy["page_roles"]}
    config["page_map"] = page_map
    config["frontmatter"] = {
        "cover": {"page": f"{policy['cover']['source_page']:03d}"},
        "order": list(policy["frontmatter_order"]),
        "body_start_page": f"{policy['body_start_page']:03d}",
        "report": "frontmatter_manifest.json",
    }
    production = config.setdefault("production_html", {})
    toc_policy = {
        "mode": policy["toc"]["mode"], "source_page": policy["toc"]["source_page"],
        "source_title": policy["toc"]["title"], "entries": copy.deepcopy(policy["toc"]["entries"]),
        "display_mode": policy["toc"].get("display_mode", "source"),
        "replace_source_toc_pages": policy["toc"]["mode"] == "preserve_and_link",
    }
    credits_policy = {"mode": policy["credits"]["mode"], "source_pages": list(policy["credits"]["source_pages"])}
    # Renderer input is one adapter-derived object.  The legacy locations below
    # are compatibility projections, never independently authored defaults.
    config["frontmatter_policy"] = {
        "toc_policy": toc_policy,
        "credits_policy": credits_policy,
        "page_map": page_map,
        "frontmatter_order": list(policy["frontmatter_order"]),
        "body_start_page": policy["body_start_page"],
        "expected_flow": list(policy["frontmatter_order"]),
    }
    production["toc_policy"] = toc_policy
    production["credits_policy"] = credits_policy


def _validate_stage40_html_output(policy: dict[str, Any], manifest: dict[str, Any], html: str) -> None:
    toc = manifest.get("toc") if isinstance(manifest, dict) else None
    credits = manifest.get("credits") if isinstance(manifest, dict) else None
    body = manifest.get("body") if isinstance(manifest, dict) else None
    if not isinstance(toc, dict) or not isinstance(credits, dict) or not isinstance(body, dict):
        raise PublicationAdapterError("frontmatter manifest is incomplete")
    if policy.get("schema") == HTML_POLICY_SCHEMA_V2:
        cover = manifest.get("cover")
        expected = policy["cover"]
        if not isinstance(cover, dict) or not isinstance(cover.get("asset"), dict):
            raise PublicationAdapterError("required cover asset is absent from frontmatter manifest")
        asset = cover["asset"]
        if asset.get("placement_id") != expected["placement_id"] or asset.get("source_page") != f"{expected['source_page']:03d}" or asset.get("mode") != "replace_source_page":
            raise PublicationAdapterError("frontmatter manifest cover binding disagrees with policy")
        section = re.findall(rf'<section\b(?=[^>]*\bid=["\']page-{expected["source_page"]:03d}["\'])(?=[^>]*\bclass=["\'][^"\']*\bpage-type-cover\b)[^>]*>[\s\S]*?</section>', html, re.I)
        if len(section) != 1:
            raise PublicationAdapterError("required cover semantic container is missing or ambiguous")
        images = re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', section[0], re.I)
        if len(images) != 1 or Path(images[0].split("?", 1)[0]).name != Path(str(asset.get("runtime_src", ""))).name:
            raise PublicationAdapterError("required cover image is missing, ambiguous, or stale")
        # Page markers and the image caption are renderer chrome, not retained
        # source-page prose.  Remove only those known elements; any other text
        # in the replacement cover remains a fail-closed duplication.
        source_visible = re.sub(
            r'<div\b(?=[^>]*\bclass=["\'][^"\']*\bpage-marker\b)[^>]*>[\s\S]*?</div>',
            " ", section[0], flags=re.I,
        )
        source_visible = re.sub(
            r'<figcaption\b[^>]*>\s*Cover\s*</figcaption>',
            " ", source_visible, flags=re.I,
        )
        visible = re.sub(r"<[^>]+>", " ", source_visible)
        if re.sub(r"\s+", " ", visible).strip():
            raise PublicationAdapterError("replacement cover retains duplicate visible source text")
    mode = policy["toc"]["mode"]
    if toc.get("mode") != mode or toc.get("origin") != ("source" if mode == "preserve_and_link" else "generated"):
        raise PublicationAdapterError("frontmatter manifest TOC origin disagrees with policy")
    if mode == "preserve_and_link":
        if str(toc.get("source_page")).zfill(3) != f"{policy['toc']['source_page']:03d}" or len(re.findall(r'<nav\b[^>]*\bdata-toc-origin=["\']source["\']', html, re.I)) != 1:
            raise PublicationAdapterError("source TOC was not conserved as exactly one source navigation")
        entries = toc.get("entries")
        if entries != len(policy["toc"]["entries"]):
            raise PublicationAdapterError("source TOC entry conservation or link closure failed")
        nav = re.search(r'<nav\b[^>]*\bdata-toc-origin=["\']source["\'][^>]*>([\s\S]*?)</nav>', html, re.I)
        if nav is None:
            raise PublicationAdapterError("source TOC navigation is unreadable")
        expected_layout = "flat" if policy["toc"].get("display_mode", "source") == "flat" else "source"
        if not re.search(rf'\bdata-toc-layout=["\']{expected_layout}["\']', nav.group(0), re.I):
            raise PublicationAdapterError("source TOC display mode disagrees with policy")
        links = re.findall(r'<a\b[^>]*\bhref=["\']#([^"\']+)["\'][^>]*>([\s\S]*?)</a>', nav.group(1), re.I)
        hrefs = [href for href, _label in links]
        if hrefs != [row["target_id"] for row in policy["toc"]["entries"]]:
            raise PublicationAdapterError("source TOC mapping order or link closure failed")
        labels = [re.sub(r"<[^>]+>", "", label).strip() for _href, label in links]
        if labels != [row["source_text"] for row in policy["toc"]["entries"]]:
            raise PublicationAdapterError("source TOC visible-entry conservation failed")
        rendered_levels = [
            int(value) for value in re.findall(
                r'<li\b[^>]*\bclass=["\'][^"\']*\btoc-level-(\d+)\b[^"\']*["\'][^>]*>\s*<a\b',
                nav.group(1), re.I,
            )
        ]
        expected_levels = [
            1 if policy["toc"].get("display_mode", "source") == "flat" else row.get("display_level", 1)
            for row in policy["toc"]["entries"]
        ]
        if rendered_levels != expected_levels:
            raise PublicationAdapterError("source TOC display hierarchy disagrees with policy")
        for target_id in hrefs:
            if len(re.findall(rf'\bid=["\']{re.escape(target_id)}["\']', html, re.I)) != 1:
                raise PublicationAdapterError("source TOC target link is unresolved or ambiguous")
    if [str(page).zfill(3) for page in credits.get("pages", [])] != [f"{page:03d}" for page in policy["credits"]["source_pages"]] or str(body.get("starts_at")).zfill(3) != f"{policy['body_start_page']:03d}":
        raise PublicationAdapterError("frontmatter manifest credits or body-start disagrees with policy")
    expected_flow: list[str] = []
    for role in policy["frontmatter_order"]:
        if role == "cover":
            expected_flow.append(f"page-{policy['cover']['source_page']:03d}")
        elif role == "credits":
            expected_flow.extend(f"page-{page:03d}" for page in policy["credits"]["source_pages"])
        elif role == "source_toc":
            expected_flow.append("toc:source")
        elif role == "toc":
            expected_flow.append("toc:generated")
        else:
            expected_flow.append(f"page-{policy['body_start_page']:03d}")
    flow = manifest.get("flow")
    if not isinstance(flow, list) or flow[:len(expected_flow)] != expected_flow:
        raise PublicationAdapterError("frontmatter manifest flow disagrees with policy")


@dataclass(frozen=True)
class PublicationAdapterRuntime:
    python: Path
    powershell: Path
    pdftoppm: Path
    word: Path | None = None
    libreoffice: Path | None = None
    html_runner: Callable[[Sequence[str], Path, Path], int] | None = None
    transient_export: Callable[[Path, Path, Path], None] | None = None
    final_export: Callable[[Path, Path, Path, Path], None] | None = None


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicationAdapterError(f"cannot read JSON authority: {path}") from error
    if not isinstance(value, dict):
        raise PublicationAdapterError("JSON authority must be an object")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _identity(path: Path, root: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), **file_identity(path)}


def _contained_file(path: Path, root: Path, label: str) -> Path:
    path = path.resolve(strict=True)
    root = root.resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as error:
        raise PublicationAdapterError(f"{label} escapes authority root") from error
    current = path
    while current != root:
        if _is_reparse(current):
            raise PublicationAdapterError(f"{label} contains reparse content")
        current = current.parent
    if not path.is_file():
        raise PublicationAdapterError(f"{label} must be a file")
    return path


def _is_reparse(path: Path) -> bool:
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except OSError:
        return True
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _safe_identity_file(record: object, root: Path, label: str) -> Path:
    if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
        raise PublicationAdapterError(f"{label} identity shape mismatch")
    raw = record["path"]
    if not isinstance(raw, str):
        raise PublicationAdapterError(f"{label} path is unsafe")
    relative = Path(raw)
    if (
        not raw
        or "\\" in raw
        or ":" in raw
        or relative.is_absolute()
        or relative.as_posix() != raw
        or ".." in relative.parts
    ):
        raise PublicationAdapterError(f"{label} path is unsafe")
    try:
        path = (root.resolve(strict=True) / relative).resolve(strict=True)
        path.relative_to(root.resolve(strict=True))
    except (FileNotFoundError, OSError) as error:
        raise PublicationAdapterError(f"{label} is missing") from error
    except ValueError as error:
        raise PublicationAdapterError(f"{label} escapes authority root") from error
    current = path
    resolved_root = root.resolve(strict=True)
    while current != resolved_root:
        if _is_reparse(current):
            raise PublicationAdapterError(f"{label} contains reparse content")
        current = current.parent
    if not path.is_file():
        raise PublicationAdapterError(f"{label} must be a file")
    if file_identity(path) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
        raise PublicationAdapterError(f"{label} identity drift")
    return path


def _seal(value: dict[str, Any], key: str, label: str) -> None:
    digest = value.get(key)
    unsigned = {name: item for name, item in value.items() if name != key}
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9A-F]{64}", digest) or hashlib.sha256(canonical_bytes(unsigned)).hexdigest().upper() != digest:
        raise PublicationAdapterError(f"{label} seal mismatch")


def _accepted_master_ru(path: Path, candidate: Path, authority_root: Path) -> dict[str, Any]:
    value = _read(path)
    expected = {"schema", "scenario_id", "artifact_kind", "candidate", "producer_stage", "evidence", "decision", "decision_at_utc", "user_decision_reference", "recorder_role", "receipt_sha256"}
    if set(value) != expected:
        raise PublicationAdapterError("MASTER_RU acceptance closed shape mismatch")
    _seal(value, "receipt_sha256", "MASTER_RU acceptance")
    candidate_identity = _identity(candidate, authority_root)
    if value["schema"] != "kb_creator.artifact_acceptance.v1" or value["artifact_kind"] != "master_ru" or value["decision"] != "accepted" or value["recorder_role"] != "main_orchestrator" or value["candidate"] != candidate_identity or not str(value["user_decision_reference"]).strip():
        raise PublicationAdapterError("MASTER_RU acceptance does not bind exact candidate")
    return value


class _Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key.lower() in {"src", "href"} and value:
                self.values.append(value)


_HTML_VOID_ELEMENTS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})


class _SemanticCards(HTMLParser):
    """Read semantic statblock ownership from HTML nesting, not regex slices."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.cards: list[dict[str, str]] = []
        self.error: str | None = None

    @staticmethod
    def _has_class(attrs: dict[str, str], token: str) -> bool:
        return token in attrs.get("class", "").split()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.error:
            return
        tag = tag.lower()
        names = [name.lower() for name, _value in attrs]
        if len(names) != len(set(names)):
            self.error = "duplicate HTML attribute"
            return
        values = {name.lower(): value or "" for name, value in attrs}
        is_card = self._has_class(values, "statblock-card")
        if is_card and (tag == "blockquote" or self._has_class(values, "review-callout")):
            self.error = "renderer projected statblock uses obsolete quote/callout container"
            return
        if is_card and tag not in {"section", "div"}:
            self.error = "renderer semantic statblock container is invalid"
            return
        if tag not in _HTML_VOID_ELEMENTS:
            self.stack.append((tag, values))
        if is_card and values.get("data-semantic-kind") == "statblock":
            page = next((parent[1].get("data-page", "") for parent in reversed(self.stack[:-1]) if parent[0] == "section" and self._has_class(parent[1], "production-page")), "")
            semantic_id = values.get("data-semantic-id", "")
            if not page or not semantic_id:
                self.error = "renderer semantic statblock lacks containing page or id"
                return
            self.cards.append({"page": page, "id": semantic_id})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in _HTML_VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if self.error:
            return
        tag = tag.lower()
        if tag in _HTML_VOID_ELEMENTS:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.error = "malformed HTML nesting"
            return
        self.stack.pop()


def _semantic_cards(html: str) -> list[dict[str, str]]:
    parser = _SemanticCards()
    try:
        parser.feed(html)
        parser.close()
    except Exception as error:
        raise PublicationAdapterError("cannot parse renderer semantic HTML") from error
    if parser.error or parser.stack:
        raise PublicationAdapterError(parser.error or "malformed HTML nesting")
    return parser.cards


def _validate_semantic_cards(html: str, projected: Sequence[dict[str, Any]]) -> None:
    cards = _semantic_cards(html)
    if len(cards) != len(projected):
        raise PublicationAdapterError("renderer semantic statblock count mismatch")
    expected = [{"page": f"{int(row['page']):03d}", "id": str(row["id"])} for row in projected]
    if cards != expected:
        raise PublicationAdapterError("renderer semantic statblock page, order, or id mismatch")


def _local_ref_inventory(html_path: Path, stage_root: Path) -> list[dict[str, Any]]:
    parser = _Refs(); parser.feed(html_path.read_text(encoding="utf-8"))
    rows = []
    for value in parser.values:
        parts = urlsplit(value)
        if parts.scheme or parts.netloc or value.startswith(("#", "data:")):
            continue
        relative = parts.path.replace("/", os.sep)
        try:
            resolved = (html_path.parent / relative).resolve(strict=True)
        except FileNotFoundError as error:
            raise PublicationAdapterError(f"HTML local reference is missing: {value}") from error
        try:
            resolved.relative_to(stage_root.resolve(strict=True))
        except ValueError as error:
            raise PublicationAdapterError(f"HTML local reference escapes stage: {value}") from error
        if not resolved.is_file() or resolved.is_symlink():
            raise PublicationAdapterError(f"HTML local reference is not a regular file: {value}")
        rows.append({"reference": value, "file": _identity(resolved, stage_root)})
    return rows


def _copy_html_runtime_files(source_html: Path, target_html: Path) -> list[dict[str, Any]]:
    """Materialize every local HTML dependency beside the packaged HTML."""
    parser = _Refs()
    parser.feed(source_html.read_text(encoding="utf-8"))
    copied: list[dict[str, Any]] = []
    seen: set[Path] = set()
    target_root = target_html.parent.resolve(strict=True)
    (target_root / "assets").mkdir(exist_ok=True)
    for value in parser.values:
        parts = urlsplit(value)
        if parts.scheme or parts.netloc or value.startswith(("#", "data:")) or not parts.path:
            continue
        relative = Path(parts.path.replace("/", os.sep))
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise PublicationAdapterError(f"HTML release reference is unsafe: {value}")
        source = _contained_file(source_html.parent / relative, source_html.parent, f"HTML release reference {value}")
        destination = target_root / relative
        if relative in seen:
            continue
        seen.add(relative)
        _copy_file(source, destination)
        copied.append({"reference": value, "file": _identity(destination, target_root)})
    _local_ref_inventory(target_html, target_root)
    return copied


_MARKDOWN_IMAGE_LINE = re.compile(
    r"^(?P<prefix>\s*!\[[^\]]*\]\()(?P<reference>[^)]+)(?P<suffix>\)(?:\{[^}]*\})?\s*)$",
    re.MULTILINE,
)

_MARKDOWN_HEADING_LINE = re.compile(r"^\s*(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
_PAGE_MARKER_LINE = re.compile(r"^\s*<!--\s*(?:source-page|pdf-page)-\d{3}\s*-->\s*$", re.I)
_CYRILLIC_SLUG_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def _renderer_heading_slug(title: str) -> str:
    transliterated = "".join(_CYRILLIC_SLUG_MAP.get(character, character) for character in title.lower())
    return re.sub(r"[^a-z0-9]+", "-", transliterated).strip("-") or "section"


def _compact_terminal_statblock_heading_ids(markdown: str) -> list[str]:
    """Find structurally compact blocks without depending on scenario vocabulary.

    A candidate must start immediately after a heading, contain at least three
    lines and use Markdown hard breaks on every line except, optionally, the
    last. It must also consume the rest of its heading section. The terminal
    constraint keeps ordinary hard-broken prose from causing a larger section
    to be wrapped as a stat block by the renderer.
    """

    lines = markdown.splitlines()
    headings: list[tuple[int, int, str]] = []
    used: dict[str, int] = {}
    for index, line in enumerate(lines):
        match = _MARKDOWN_HEADING_LINE.fullmatch(line)
        if not match:
            continue
        base = _renderer_heading_slug(match.group("title"))
        used[base] = used.get(base, 0) + 1
        heading_id = base if used[base] == 1 else f"{base}-{used[base]}"
        headings.append((index, len(match.group("marks")), heading_id))

    detected: list[str] = []
    for index, level, heading_id in headings:
        body_start = index + 1
        if body_start >= len(lines) or not lines[body_start].strip():
            continue
        body_end = body_start
        while body_end < len(lines) and lines[body_end].strip():
            if _MARKDOWN_HEADING_LINE.fullmatch(lines[body_end]) or _PAGE_MARKER_LINE.fullmatch(lines[body_end]):
                break
            body_end += 1
        body = lines[body_start:body_end]
        if len(body) < 3 or not any(re.search(r"\d", line) for line in body):
            continue
        hard_breaks = sum(line.endswith("  ") for line in body)
        if hard_breaks < len(body) - 1:
            continue

        following = body_end
        while following < len(lines) and not lines[following].strip():
            following += 1
        if following < len(lines):
            next_heading = _MARKDOWN_HEADING_LINE.fullmatch(lines[following])
            if not _PAGE_MARKER_LINE.fullmatch(lines[following]) and not (
                next_heading and len(next_heading.group("marks")) <= level
            ):
                continue
        detected.append(heading_id)
    return detected


def _augment_compact_statblock_policy(production: dict[str, Any], markdown: str) -> list[str]:
    detected = _compact_terminal_statblock_heading_ids(markdown)
    if not detected:
        return []
    raw_policy = production.get("statblock_section_policy")
    if raw_policy is None:
        policy: dict[str, Any] = {}
    elif isinstance(raw_policy, dict):
        policy = raw_policy
    else:
        raise PublicationAdapterError("HTML statblock section policy must be an object")
    raw_ids = policy.get("heading_ids", [])
    if not isinstance(raw_ids, list) or any(not isinstance(value, str) for value in raw_ids):
        raise PublicationAdapterError("HTML statblock heading ids must be a string list")
    heading_ids = list(raw_ids)
    for heading_id in detected:
        if heading_id not in heading_ids:
            heading_ids.append(heading_id)
    policy["heading_ids"] = heading_ids
    production["statblock_section_policy"] = policy
    return detected


def _application_inventory_sha(rows: Sequence[dict[str, Any]]) -> str:
    value = "".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n"
        for row in sorted(rows, key=lambda item: item["path"])
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _prepare_html_artview_projection(
    *,
    master_ru: Path,
    artview_decisions: Path,
    application: dict[str, Any],
    effective: dict[str, Any],
    effective_visual_config: Path,
    artview_projection_root: Path,
    authority_root: Path,
    artifacts: Path,
    evidence: Path,
) -> tuple[Path, list[dict[str, Any]]]:
    expected_application = {
        "schema", "scenario_id", "inputs", "reader_projection", "effective_visual_config",
        "assets", "assets_inventory_sha256", "counts", "application_sha256",
    }
    if set(application) != expected_application or application.get("schema") != "kb_creator.scenario_artview_application.v3":
        raise PublicationAdapterError("ArtView application closed shape mismatch")
    inputs = application.get("inputs")
    if not isinstance(inputs, dict) or set(inputs) != {"profile", "candidate_manifest", "decisions", "artview_acceptance"}:
        raise PublicationAdapterError("ArtView application input graph is not closed")
    _safe_identity_file(inputs["profile"], authority_root, "ArtView application profile")
    manifest_path = _safe_identity_file(inputs["candidate_manifest"], authority_root, "ArtView candidate manifest")
    decisions_path = _safe_identity_file(inputs["decisions"], authority_root, "ArtView application decisions")
    if decisions_path != artview_decisions:
        raise PublicationAdapterError("ArtView application does not bind exact accepted decisions")
    acceptance_path = _safe_identity_file(inputs["artview_acceptance"], authority_root, "ArtView acceptance")
    acceptance = _read(acceptance_path)
    _seal(acceptance, "receipt_sha256", "ArtView acceptance")
    if (
        acceptance.get("schema") != "kb_creator.artifact_acceptance.v1"
        or acceptance.get("scenario_id") != application["scenario_id"]
        or acceptance.get("artifact_kind") != "artview"
        or acceptance.get("decision") != "accepted"
        or acceptance.get("recorder_role") != "main_orchestrator"
        or not str(acceptance.get("user_decision_reference", "")).strip()
        or acceptance.get("candidate") != inputs["candidate_manifest"]
        or not isinstance(acceptance.get("evidence"), list)
        or acceptance["evidence"].count(inputs["decisions"]) != 1
    ):
        raise PublicationAdapterError("ArtView acceptance does not bind application authorities")

    manifest = _read(manifest_path)
    candidate_schema = manifest.get("schema")
    if candidate_schema not in {"kb_creator.scenario_artview_candidate.v3", "kb_creator.scenario_artview_candidate.v4"} or manifest.get("scenario_id") != application["scenario_id"]:
        raise PublicationAdapterError("ArtView candidate manifest disagrees with application")
    decisions = _read(decisions_path)
    expected_decision_schema = "kb_creator.scenario_artview_decisions.v4" if candidate_schema.endswith(".v4") else "kb_creator.scenario_artview_decisions.v3"
    if decisions.get("schema") != expected_decision_schema:
        raise PublicationAdapterError("ArtView application decision schema disagrees with candidate manifest")
    bindings = manifest.get("bindings")
    if not isinstance(bindings, dict):
        raise PublicationAdapterError("ArtView candidate manifest lacks bindings")
    bound_master = _safe_identity_file(bindings.get("master_ru"), authority_root, "ArtView manifest MASTER_RU")
    if bound_master != master_ru:
        raise PublicationAdapterError("ArtView candidate manifest does not bind exact MASTER_RU")
    master_assets_path = _safe_identity_file(
        bindings.get("master_ru_asset_manifest"), authority_root, "ArtView manifest MASTER_RU assets",
    )
    master_assets = _read(master_assets_path)
    if (
        master_assets.get("schema") != "kb_creator.master_ru_asset_manifest.v1"
        or master_assets.get("scenario_id") != application["scenario_id"]
        or not isinstance(master_assets.get("assets"), list)
    ):
        raise PublicationAdapterError("MASTER_RU asset manifest is not closed v1")

    projection_path = _safe_identity_file(application["reader_projection"], artview_projection_root, "ArtView reader projection")
    projection = _read(projection_path)
    _seal(projection, "projection_sha256", "ArtView reader projection")
    if projection.get("schema") != "kb_creator.scenario_artview_reader_projection.v3" or projection.get("scenario_id") != application["scenario_id"] or not isinstance(projection.get("rows"), list):
        raise PublicationAdapterError("ArtView reader projection disagrees with application")
    bound_effective = _safe_identity_file(application["effective_visual_config"], artview_projection_root, "ArtView effective visual config")
    if bound_effective != effective_visual_config or effective.get("scenario_id") != application["scenario_id"] or not isinstance(effective.get("rows"), list):
        raise PublicationAdapterError("ArtView application does not bind exact effective visual config")

    application_rows = application.get("assets")
    if not isinstance(application_rows, list):
        raise PublicationAdapterError("ArtView application lacks asset identities")
    materialization: dict[str, tuple[Path, dict[str, Any]]] = {}
    collision_keys: set[str] = set()
    for index, record in enumerate(application_rows):
        label = f"ArtView application asset {index}"
        source = _safe_identity_file(record, artview_projection_root, label)
        raw = record["path"]
        if not raw.startswith("assets/") or len(Path(raw).parts) < 2:
            raise PublicationAdapterError(f"{label} path is unsafe")
        collision = raw.casefold()
        if collision in collision_keys:
            raise PublicationAdapterError("ArtView application asset path collision")
        collision_keys.add(collision)
        materialization[raw] = (source, record)
    if application.get("assets_inventory_sha256") != _application_inventory_sha(application_rows):
        raise PublicationAdapterError("ArtView application asset inventory drift")

    projection_by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(projection["rows"]):
        if not isinstance(row, dict) or not isinstance(row.get("asset_id"), str) or row["asset_id"] in projection_by_id:
            raise PublicationAdapterError(f"ArtView reader projection row {index} is invalid")
        status = row.get("status")
        output_path = row.get("output_path")
        if status == "included":
            if not isinstance(output_path, str) or output_path not in materialization:
                raise PublicationAdapterError("ArtView reader projection asset is not application-bound")
        elif status == "excluded":
            if output_path is not None:
                raise PublicationAdapterError("excluded ArtView projection row has an output path")
        else:
            raise PublicationAdapterError("ArtView reader projection status is invalid")
        projection_by_id[row["asset_id"]] = row
    effective_by_id = {
        row.get("asset_id"): row for row in effective["rows"]
        if isinstance(row, dict) and isinstance(row.get("asset_id"), str)
    }
    included = {asset_id: row for asset_id, row in projection_by_id.items() if row["status"] == "included"}
    if len(effective_by_id) != len(effective["rows"]) or set(effective_by_id) != set(included):
        raise PublicationAdapterError("effective visual config disagrees with reader projection")
    for asset_id, row in included.items():
        if effective_by_id[asset_id].get("output_path") != row["output_path"]:
            raise PublicationAdapterError("effective visual config output path drift")
    if set(materialization) != {row["output_path"] for row in included.values()}:
        raise PublicationAdapterError("ArtView application assets disagree with reader projection")
    if application.get("counts") != {
        "reviewed": len(projection_by_id),
        "included": len(included),
        "excluded": len(projection_by_id) - len(included),
    }:
        raise PublicationAdapterError("ArtView application counts disagree with reader projection")

    master_asset_records: dict[str, dict[str, Any]] = {}
    master_identity_to_paths: dict[tuple[int, str], list[str]] = {}
    master_collision_keys: set[str] = set()
    for index, record in enumerate(master_assets["assets"]):
        source = _safe_identity_file(record, master_ru.parent, f"MASTER_RU asset {index}")
        raw = record["path"]
        collision = raw.casefold()
        if collision in master_collision_keys:
            raise PublicationAdapterError("MASTER_RU asset path collision")
        master_collision_keys.add(collision)
        master_asset_records[raw] = record
        identity_key = (record["bytes"], record["sha256"])
        master_identity_to_paths.setdefault(identity_key, []).append(raw)
        del source

    manifest_rows = manifest.get("rows")
    if not isinstance(manifest_rows, list):
        raise PublicationAdapterError("ArtView candidate manifest lacks rows")
    identity_to_asset_id: dict[tuple[int, str], str] = {}
    manifest_asset_ids: set[str] = set()
    for index, row in enumerate(manifest_rows):
        if not isinstance(row, dict) or not isinstance(row.get("asset_id"), str) or row["asset_id"] in manifest_asset_ids:
            raise PublicationAdapterError(f"ArtView candidate manifest row {index} is invalid")
        asset_id = row["asset_id"]
        manifest_asset_ids.add(asset_id)
        current = row.get("current")
        if not isinstance(current, dict) or not {"path", "bytes", "sha256"}.issubset(current):
            raise PublicationAdapterError(f"ArtView candidate manifest row {index} lacks current identity")
        current_record = {key: current[key] for key in ("path", "bytes", "sha256")}
        _safe_identity_file(current_record, manifest_path.parent, f"ArtView current asset for {asset_id}")
        identity_key = (current_record["bytes"], current_record["sha256"])
        if identity_key in master_identity_to_paths:
            prior = identity_to_asset_id.get(identity_key)
            if prior is not None and prior != asset_id:
                raise PublicationAdapterError("MASTER_RU asset identity maps to multiple ArtView rows")
            identity_to_asset_id[identity_key] = asset_id
    if manifest_asset_ids != set(projection_by_id):
        raise PublicationAdapterError("ArtView candidate and reader projection row sets differ")
    source_asset_to_id: dict[str, str] = {}
    for identity_key, paths in master_identity_to_paths.items():
        asset_id = identity_to_asset_id.get(identity_key)
        if asset_id is None:
            raise PublicationAdapterError("MASTER_RU asset identity lacks ArtView row")
        for raw in paths:
            source_asset_to_id[raw] = asset_id

    rebased: list[dict[str, Any]] = []
    matched_source_assets: set[str] = set()

    def replace_image(match: re.Match[str]) -> str:
        reference = match.group("reference").strip()
        parts = urlsplit(reference)
        if parts.scheme or parts.netloc or reference.startswith("data:"):
            return match.group(0)
        if parts.query or parts.fragment:
            raise PublicationAdapterError(f"MASTER_RU local asset reference is unsafe: {reference}")
        relative = Path(parts.path)
        if not parts.path or "\\" in parts.path or ":" in parts.path or relative.is_absolute() or relative.as_posix() != parts.path or ".." in relative.parts:
            raise PublicationAdapterError(f"MASTER_RU local asset reference is unsafe: {reference}")
        record = master_asset_records.get(parts.path)
        if record is None:
            raise PublicationAdapterError(f"MASTER_RU local asset is not manifest-bound: {reference}")
        _safe_identity_file(record, master_ru.parent, f"MASTER_RU referenced asset {reference}")
        asset_id = source_asset_to_id.get(parts.path)
        if asset_id is None:
            raise PublicationAdapterError(f"MASTER_RU local asset lacks ArtView row: {reference}")
        projection_row = projection_by_id[asset_id]
        matched_source_assets.add(parts.path)
        if projection_row["status"] == "excluded":
            rebased.append({"source_reference": reference, "asset_id": asset_id, "action": "excluded", "output_reference": None})
            return ""
        output_path = projection_row["output_path"]
        output_reference = os.path.relpath(artifacts / Path(output_path), evidence).replace("\\", "/")
        rebased.append({"source_reference": reference, "asset_id": asset_id, "action": "rebased", "output_reference": output_reference})
        return f"{match.group('prefix')}{output_reference}{match.group('suffix')}"

    derived_text = _MARKDOWN_IMAGE_LINE.sub(replace_image, master_ru.read_text(encoding="utf-8"))
    if set(master_asset_records) != matched_source_assets:
        raise PublicationAdapterError("MASTER_RU asset manifest contains unprojected reader assets")

    if (artifacts / "assets").exists():
        raise PublicationAdapterError("HTML artifact asset destination already exists")
    for raw, (source, _record) in sorted(materialization.items()):
        target = artifacts / Path(raw)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if file_identity(target) != file_identity(source):
            raise PublicationAdapterError("HTML asset materialization identity mismatch")
    derived_source = evidence / "derived_html_source.md"
    derived_source.write_text(derived_text, encoding="utf-8", newline="\n")
    return derived_source, rebased


def _resolve_required_cover_binding(
    policy: dict[str, Any], application: dict[str, Any], projection_root: Path, artifacts: Path,
) -> dict[str, Any] | None:
    """Resolve a v2 cover from the accepted Stage-31 placement graph.

    The renderer is intentionally only a formatter: it receives an already
    selected file and cannot infer a cover from page number or image size.
    """
    if policy.get("schema") != HTML_POLICY_SCHEMA_V2:
        return None
    projection_path = _safe_identity_file(application["reader_projection"], projection_root, "ArtView reader projection")
    projection = _read(projection_path)
    rows = [row for row in projection.get("rows", []) if isinstance(row, dict) and row.get("placement_id") == policy["cover"]["placement_id"]]
    if len(rows) != 1:
        raise PublicationAdapterError("required cover placement is missing or ambiguous in ArtView projection")
    row = rows[0]
    if row.get("status") != "included" or row.get("semantic_role") != "cover" or row.get("placement_target") != "source_page_cover" or row.get("required") is not True or row.get("source_page") != policy["cover"]["source_page"]:
        raise PublicationAdapterError("required cover placement is not an included cover selection")
    output_path = row.get("output_path")
    if not isinstance(output_path, str) or not output_path.startswith("assets/"):
        raise PublicationAdapterError("required cover has no reader asset")
    asset = artifacts / Path(output_path)
    if not asset.is_file():
        raise PublicationAdapterError("required cover reader asset was not materialized")
    return {"placement_id": row["placement_id"], "asset_id": row["asset_id"], "output_path": output_path, "source_page": row["source_page"], "asset": asset}


def _replace_source_cover_markdown(derived_source: Path, cover: dict[str, Any]) -> None:
    """Replace, never overlay, the reconstructed cover text with the selected composite render."""
    page = f"{int(cover['source_page']):03d}"
    text = derived_source.read_text(encoding="utf-8")
    pattern = re.compile(rf"(^<!--\s*(?:source-page|pdf-page)-{page}\s*-->\s*$)[\s\S]*?(?=^<!--\s*(?:source-page|pdf-page)-\d{{3}}\s*-->\s*$|\Z)", re.M | re.I)
    image_ref = os.path.relpath(cover["asset"], derived_source.parent).replace("\\", "/")
    replacement = f"\\1\n\n![Cover]({image_ref})\n\n"
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise PublicationAdapterError("required cover source page is missing or ambiguous in derived MASTER_RU")
    derived_source.write_text(text, encoding="utf-8", newline="\n")


def _validate_cover_semantic_separation(
    cover: dict[str, Any], projection: dict[str, Any] | None,
) -> None:
    """Refuse a destructive cover replacement over projected semantic spans."""
    if projection is None:
        return
    projected = projection.get("projected")
    if not isinstance(projected, list):
        raise PublicationAdapterError("semantic projection payload is invalid")
    if any(
        isinstance(row, dict) and row.get("page") == cover["source_page"]
        for row in projected
    ):
        raise PublicationAdapterError(
            "required cover page contains projected semantic spans and cannot be replaced"
        )


def _translation_lineage(master: Path, authority_root: Path) -> list[dict[str, Any]]:
    """Return validated, ordered EN/RU translation rows for an accepted master.

    Stage 40 must not infer a Russian location from an English line number.  The
    only bridge is the sealed Stage 20/21 unit lineage.  This deliberately keeps
    the validation local and read-only: it checks every identity used below and
    reassembles the accepted master before exposing a row ledger.
    """
    inventory_path = master.parent / "INVENTORY.json"
    inventory = _read(inventory_path)
    rows = inventory.get("rows")
    if inventory.get("schema") != "kb_creator.candidate_inventory.v1" or not isinstance(rows, list):
        raise PublicationAdapterError("MASTER_RU inventory is invalid")
    inventory_by_path = {row.get("path"): row for row in rows if isinstance(row, dict)}
    for raw in ("MASTER_RU.md", "MASTER_RU.provenance.json"):
        record = inventory_by_path.get(raw)
        if not isinstance(record, dict) or _safe_identity_file(record, master.parent, f"MASTER_RU inventory {raw}") != (master if raw == "MASTER_RU.md" else master.parent / raw):
            raise PublicationAdapterError("MASTER_RU inventory binding drift")
    provenance_path = master.parent / "MASTER_RU.provenance.json"
    provenance = _read(provenance_path)
    expected = {"schema", "scenario_id", "accepted_master_en", "packet_manifest", "submission", "unit_order", "master_ru", "provenance_sha256"}
    if set(provenance) != expected or provenance.get("schema") != "kb_creator.master_ru_provenance.v1":
        raise PublicationAdapterError("MASTER_RU provenance is invalid")
    _seal(provenance, "provenance_sha256", "MASTER_RU provenance")
    if provenance["master_ru"] != _identity(master, master.parent):
        raise PublicationAdapterError("MASTER_RU provenance does not bind accepted master")
    packet_path = _safe_identity_file(provenance["packet_manifest"], authority_root, "MASTER_RU packet manifest")
    submission_path = _safe_identity_file(provenance["submission"], authority_root, "MASTER_RU submission")
    packet = _read(packet_path)
    if packet.get("schema") != "kb_creator.master_ru_packet_manifest.v1" or not isinstance(packet.get("batches"), list):
        raise PublicationAdapterError("MASTER_RU packet manifest is invalid")
    _seal(packet, "manifest_sha256", "MASTER_RU packet manifest")
    if packet.get("accepted_master_en") != provenance["accepted_master_en"]:
        raise PublicationAdapterError("MASTER_RU provenance accepted MASTER_EN drift")
    master_en = _safe_identity_file(packet.get("master_en"), authority_root, "packet MASTER_EN")
    accepted_en = _safe_identity_file(packet.get("accepted_master_en"), authority_root, "packet MASTER_EN acceptance")
    accepted = _read(accepted_en)
    _seal(accepted, "receipt_sha256", "MASTER_EN acceptance")
    if accepted.get("artifact_kind") != "master_en" or accepted.get("decision") != "accepted" or accepted.get("candidate") != _identity(master_en, authority_root):
        raise PublicationAdapterError("packet MASTER_EN acceptance is not authoritative")
    submission = _read(submission_path)
    if set(submission) != {"schema", "scenario_id", "accepted_master_en", "packet_manifest", "units", "batches", "review", "submission_sha256"} or submission.get("schema") != "kb_creator.master_ru_submission.v1":
        raise PublicationAdapterError("MASTER_RU submission is invalid")
    _seal(submission, "submission_sha256", "MASTER_RU submission")
    if submission.get("accepted_master_en") != packet["accepted_master_en"] or submission.get("packet_manifest") != _identity(packet_path, authority_root) or submission.get("review") != {"state": "closed", "unresolved": []}:
        raise PublicationAdapterError("MASTER_RU submission authority drift")
    if not isinstance(submission.get("units"), list) or not isinstance(submission.get("batches"), list) or len(submission["batches"]) != len(packet["batches"]):
        raise PublicationAdapterError("MASTER_RU submission batch shape is invalid")
    translated: list[dict[str, Any]] = []
    current_page: int | None = None
    for index, packet_batch in enumerate(packet["batches"]):
        if not isinstance(packet_batch, dict) or not isinstance(packet_batch.get("unit_ids"), list):
            raise PublicationAdapterError("MASTER_RU packet batch is invalid")
        en_path = _safe_identity_file(packet_batch.get("input"), packet_path.parent, f"packet EN batch {index}")
        ru_path = _safe_identity_file(submission["batches"][index], authority_root, f"submission RU batch {index}")
        en = _read(en_path); ru = _read(ru_path)
        if en.get("schema") != "kb_creator.translation_batch.v1" or ru.get("schema") != en.get("schema") or ru.get("batch_id") != en.get("batch_id") or ru.get("instructions") != en.get("instructions") or not isinstance(en.get("units"), list) or not isinstance(ru.get("units"), list) or len(en["units"]) != len(ru["units"]):
            raise PublicationAdapterError("translation batch lineage drift")
        if [row.get("unit_id") for row in en["units"] if isinstance(row, dict)] != packet_batch["unit_ids"]:
            raise PublicationAdapterError("packet EN batch unit order drift")
        for source, target in zip(en["units"], ru["units"]):
            if not isinstance(source, dict) or not isinstance(target, dict) or source.get("unit_id") != target.get("unit_id") or source.get("source_text") != target.get("source_text") or source.get("source_hash") != target.get("source_hash"):
                raise PublicationAdapterError("translated unit source binding drift")
            ru_text = target.get("ru_text")
            if not isinstance(ru_text, str) or not ru_text.strip() or not isinstance(source.get("source_text"), str) or not isinstance(source.get("source_hash"), str):
                raise PublicationAdapterError("translated unit payload is invalid")
            ru_text = ru_text.strip()
            marker = re.fullmatch(r"<!--\s*source-page-(\d{3,})\s*-->", source["source_text"].strip())
            if marker:
                if ru_text != source["source_text"].strip() or int(marker.group(1)) <= (current_page or 0):
                    raise PublicationAdapterError("translation page marker lineage drift")
                current_page = int(marker.group(1))
            elif current_page is None:
                raise PublicationAdapterError("translation unit lacks source-page domain")
            translated.append({"unit_id": source["unit_id"], "page": current_page, "source_text": source["source_text"], "source_sha256": str(source["source_hash"]).upper(), "ru_text": ru_text, "russian_payload_sha256": hashlib.sha256(ru_text.encode("utf-8")).hexdigest().upper()})
    expected_units = [{key: row[key] for key in ("unit_id", "source_sha256", "russian_payload_sha256")} for row in translated]
    if submission["units"] != expected_units or provenance.get("unit_order") != [row["unit_id"] for row in translated]:
        raise PublicationAdapterError("MASTER_RU submission unit identity drift")
    assembled = "\n\n".join(row["ru_text"] for row in translated).strip() + "\n"
    if assembled.encode("utf-8") != master.read_bytes():
        raise PublicationAdapterError("accepted MASTER_RU assembly drift")
    offset = 0
    line_number = 1
    for row in translated:
        payload = row["ru_text"]
        row["target_start_byte"] = offset
        row["target_end_byte"] = offset + len(payload.encode("utf-8"))
        row["target_start_line"] = line_number
        row["target_end_line"] = row["target_start_line"] + payload.count("\n")
        offset = row["target_end_byte"] + 2
        line_number = row["target_end_line"] + 2
    return translated


def _semantic_html_projection(accepted_master: Path, derived_master: Path, authority: Path, authority_root: Path, evidence: Path) -> dict[str, Any]:
    """Project page-local EN semantic spans onto their sealed RU translation units."""
    inventory = _read(authority / "RECONSTRUCTION_INVENTORY.json")
    rows = inventory.get("artifacts")
    if not isinstance(rows, list):
        raise PublicationAdapterError("reconstruction inventory lacks artifacts")
    manifests = [row for row in rows if isinstance(row, dict) and row.get("role") == "reconstruction_manifest"]
    if len(manifests) != 1:
        raise PublicationAdapterError("reconstruction inventory lacks unique manifest")
    manifest_path = _safe_identity_file({key: manifests[0][key] for key in ("path", "bytes", "sha256")}, authority, "reconstruction manifest")
    manifest = _read(manifest_path); _seal(manifest, "manifest_sha256", "reconstruction manifest")
    candidate = manifest.get("candidate"); review = manifest.get("review")
    if not isinstance(candidate, dict) or not isinstance(candidate.get("files"), list) or not isinstance(review, dict) or not isinstance(review.get("decisions"), list):
        raise PublicationAdapterError("reconstruction manifest lacks semantic authority")
    sidecars = [row for row in candidate["files"] if isinstance(row, dict) and str(row.get("path")) == "SEMANTIC_STRUCTURE.json"]
    if len(sidecars) != 1:
        raise PublicationAdapterError("reconstruction manifest lacks unique semantic sidecar")
    sidecar_record = {key: sidecars[0][key] for key in ("path", "bytes", "sha256")}
    # The promotion package retains the same candidate bytes below content/.
    content_sidecar = authority / "content" / "SEMANTIC_STRUCTURE.json"
    if not content_sidecar.is_file() or file_identity(content_sidecar) != {"bytes": sidecar_record["bytes"], "sha256": sidecar_record["sha256"]}:
        raise PublicationAdapterError("semantic sidecar content identity drift")
    sidecar = _read(content_sidecar)
    decisions: dict[int, tuple[dict[str, Any], Path]] = {}
    for record in review["decisions"]:
        decision_path = _safe_identity_file(record, authority, "reconstruction page decision")
        decision = _read(decision_path)
        page = decision.get("source_page")
        if type(page) is not int or page in decisions:
            raise PublicationAdapterError("reconstruction page decision page domain is invalid")
        decisions[page] = (decision, decision_path)
    sidecar_rows = sidecar.get("page_decisions")
    if not isinstance(sidecar_rows, list):
        raise PublicationAdapterError("semantic sidecar lacks page decision bindings")
    sidecar_hashes = {row.get("source_page"): row.get("sha256") for row in sidecar_rows if isinstance(row, dict)}
    if set(sidecar_hashes) != set(decisions) or any(sidecar_hashes[page] != file_identity(path)["sha256"] for page, (_value, path) in decisions.items()):
        raise PublicationAdapterError("semantic sidecar page decision binding drift")
    candidate_files = {
        row.get("path"): row for row in candidate["files"] if isinstance(row, dict)
    }
    lineage = _translation_lineage(accepted_master, authority_root)
    derived_lines = derived_master.read_text(encoding="utf-8").splitlines()
    accepted_lines = accepted_master.read_text(encoding="utf-8").splitlines()
    if len(derived_lines) != len(accepted_lines) or [index for index, line in enumerate(derived_lines) if re.fullmatch(r"<!--\s*source-page-\d{3,}\s*-->", line.strip())] != [index for index, line in enumerate(accepted_lines) if re.fullmatch(r"<!--\s*source-page-\d{3,}\s*-->", line.strip())]:
        raise PublicationAdapterError("ArtView projection changes source-page line topology")
    projected: list[dict[str, Any]] = []
    insertions: list[tuple[int, str]] = []
    for page, (decision, decision_path) in decisions.items():
        structure = decision.get("semantic_structure", {})
        units = structure.get("units") if isinstance(structure, dict) else None
        if not isinstance(units, list):
            raise PublicationAdapterError("reconstruction page decision lacks semantic units")
        declared = [unit for unit in units if isinstance(unit, dict) and unit.get("kind") == "statblock" and unit.get("container_parent") is None]
        if not declared:
            continue
        declared.sort(key=lambda unit: unit.get("markdown_span", {}).get("start_line", -1))
        compact_pages = sidecar.get("pages")
        compact = next((row for row in compact_pages if isinstance(row, dict) and row.get("source_page") == page), None) if isinstance(compact_pages, list) else None
        compact_units = compact.get("units") if isinstance(compact, dict) else None
        compact_by_id = {row.get("id"): row for row in compact_units if isinstance(row, dict) and isinstance(row.get("id"), str)} if isinstance(compact_units, list) else {}
        page_file_record = candidate_files.get(f"pages/page-{page:03d}.md")
        if not isinstance(page_file_record, dict):
            raise PublicationAdapterError("reconstruction manifest lacks promoted page file")
        page_file = authority / "content" / "pages" / f"page-{page:03d}.md"
        if not page_file.is_file() or file_identity(page_file) != {"bytes": page_file_record.get("bytes"), "sha256": page_file_record.get("sha256")}:
            raise PublicationAdapterError("reconstruction promoted page identity drift")
        page_markdown = decision.get("markdown")
        if not isinstance(page_markdown, str) or page_file.read_text(encoding="utf-8").count(page_markdown) != 1:
            raise PublicationAdapterError("promoted page does not bind decision markdown")
        page_lines = page_markdown.splitlines()
        spans: list[tuple[int, int]] = []
        for ordinal, unit in enumerate(declared, 1):
            span = unit.get("markdown_span", {})
            compact_unit = compact_by_id.get(unit.get("id"))
            start = span.get("start_line") if isinstance(span, dict) else None
            end = span.get("end_line") if isinstance(span, dict) else None
            if not isinstance(unit.get("id"), str) or unit.get("representation") != "semantic_span" or type(start) is not int or type(end) is not int or start < 1 or end < start or end > len(page_lines) or not isinstance(span.get("sha256"), str) or not isinstance(compact_unit, dict) or compact_unit.get("kind") != "statblock" or compact_unit.get("representation") != "semantic_span" or compact_unit.get("markdown_span_sha256") != span["sha256"]:
                raise PublicationAdapterError("semantic statblock span authority is invalid")
            if any(not (end < prior_start or start > prior_end) for prior_start, prior_end in spans):
                raise PublicationAdapterError("semantic statblock spans overlap")
            spans.append((start, end))
            body = page_lines[start - 1:end]
            actual_sha = hashlib.sha256("\n".join(body).encode("utf-8")).hexdigest().upper()
            if actual_sha != span["sha256"]:
                raise PublicationAdapterError("semantic statblock span identity drift")
            if any(line.lstrip().startswith(">") for line in body):
                raise PublicationAdapterError("semantic statblock span contains quote syntax")
            candidates: list[list[dict[str, Any]]] = []
            for first in range(len(lineage)):
                if lineage[first]["page"] != page or re.fullmatch(r"<!--\s*source-page-\d{3,}\s*-->", lineage[first]["source_text"].strip()):
                    continue
                joined = ""
                for last in range(first, len(lineage)):
                    row = lineage[last]
                    if row["page"] != page or re.fullmatch(r"<!--\s*source-page-\d{3,}\s*-->", row["source_text"].strip()):
                        break
                    joined = row["source_text"] if last == first else joined + "\n\n" + row["source_text"]
                    if joined == "\n".join(body):
                        candidates.append(lineage[first:last + 1])
                    if len(joined) > len("\n".join(body)):
                        break
            if len(candidates) != 1:
                raise PublicationAdapterError("semantic statblock has no unique translation-unit mapping")
            translated_rows = candidates[0]
            target_start = translated_rows[0]["target_start_line"]
            target_end = translated_rows[-1]["target_end_line"]
            target_body = accepted_lines[target_start - 1:target_end]
            if any(line.lstrip().startswith(">") for line in target_body):
                raise PublicationAdapterError("translated semantic statblock span contains quote syntax")
            if any("semantic-span-" in line or "semantic-kind:" in line or "callout-class: statblock-card" in line for line in target_body):
                raise PublicationAdapterError("reserved statblock transport exists in accepted MASTER_RU")
            if derived_lines[target_start - 1:target_end] != target_body:
                raise PublicationAdapterError("ArtView projection changes a semantic statblock range")
            start_marker = f"<!-- semantic-span-start: statblock; id: {unit['id']} -->"
            end_marker = f"<!-- semantic-span-end: statblock; id: {unit['id']} -->"
            insertions.extend(((target_start - 1, start_marker), (target_end, end_marker)))
            projected.append({"id": unit["id"], "page": page, "ordinal": ordinal, "decision": _identity(decision_path, authority), "page_file": {"path": f"content/pages/page-{page:03d}.md", **file_identity(page_file)}, "source_span": {"start_line": start, "end_line": end, "sha256": span["sha256"]}, "translation_unit_ids": [row["unit_id"] for row in translated_rows], "translation_source_sha256": [row["source_sha256"] for row in translated_rows], "russian_payload_sha256": [row["russian_payload_sha256"] for row in translated_rows], "target_span": {"start_line": target_start, "end_line": target_end, "start_byte": translated_rows[0]["target_start_byte"], "end_byte": translated_rows[-1]["target_end_byte"], "sha256": hashlib.sha256("\n".join(target_body).encode("utf-8")).hexdigest().upper()}, "derived_container_sha256": hashlib.sha256("\n".join([start_marker, *target_body, end_marker]).encode("utf-8")).hexdigest().upper()})
    for line_index, directive in sorted(insertions, reverse=True):
        derived_lines.insert(line_index, directive)
    text = "\n".join(derived_lines)
    if derived_master.read_bytes().endswith((b"\n", b"\r")):
        text += "\n"
    derived_master.write_text(text, encoding="utf-8", newline="\n")
    output = {"schema": "kb_creator.html_semantic_projection.v2", "master_ru": file_identity(accepted_master), "semantic_sidecar": {"path": "content/SEMANTIC_STRUCTURE.json", **file_identity(content_sidecar)}, "expected_statblock_ids": [row["id"] for row in projected], "projected": projected}
    output["projection_sha256"] = hashlib.sha256(canonical_bytes(output)).hexdigest().upper()
    path = evidence / "html_semantic_projection.json"; path.write_bytes(canonical_bytes(output) + b"\n")
    return output


def build_html_candidate(
    *,
    master_ru: Path,
    master_ru_acceptance: Path,
    artview_decisions: Path,
    artview_application: Path,
    effective_visual_config: Path,
    artview_projection_root: Path,
    base_config: Path,
    staging: Path,
    output_name: str,
    semantic_authority: Path | None = None,
    python: Path = Path(sys.executable),
    runner: Callable[[Sequence[str], Path, Path], int] | None = None,
) -> dict[str, Any]:
    """Invoke only the existing production-HTML CLI after exact authority binding."""
    raise PublicationAdapterError(DOCX_ONLY_ROUTE)
    stage_root = staging.resolve(strict=True)
    if {path.name for path in stage_root.iterdir()} != {"artifacts", "evidence"}:
        raise PublicationAdapterError("HTML stage must have exact artifacts/evidence roots")
    authority_root = stage_root.parents[2]
    master_ru = _contained_file(master_ru, authority_root, "MASTER_RU")
    master_ru_acceptance = _contained_file(master_ru_acceptance, authority_root, "MASTER_RU acceptance")
    artview_decisions = _contained_file(artview_decisions, authority_root, "ArtView decisions")
    artview_application = _contained_file(artview_application, authority_root, "ArtView application")
    effective_visual_config = _contained_file(effective_visual_config, authority_root, "effective visual config")
    artview_projection_root = artview_projection_root.resolve(strict=True)
    try:
        artview_projection_root.relative_to(authority_root)
    except ValueError as error:
        raise PublicationAdapterError("ArtView projection escapes authority root") from error
    config_path = _contained_file(base_config, authority_root, "HTML base config")
    acceptance = _accepted_master_ru(master_ru_acceptance, master_ru, authority_root)
    decisions = _read(artview_decisions); _seal(decisions, "decisions_sha256", "ArtView decisions")
    if decisions.get("state") != "accepted" or decisions.get("review", {}).get("state") != "closed" or decisions.get("scenario_id") != acceptance["scenario_id"]:
        raise PublicationAdapterError("ArtView decisions are not accepted and closed")
    application = _read(artview_application); _seal(application, "application_sha256", "ArtView application")
    effective = _read(effective_visual_config); _seal(effective, "config_sha256", "effective visual config")
    if application.get("scenario_id") != acceptance["scenario_id"] or effective.get("scenario_id") != acceptance["scenario_id"]:
        raise PublicationAdapterError("HTML authorities disagree on scenario")

    artifacts = stage_root / "artifacts"; evidence = stage_root / "evidence"
    if not output_name or Path(output_name).name != output_name or Path(output_name).suffix.lower() != ".html":
        raise PublicationAdapterError("HTML output name must be a simple .html filename")
    target = artifacts / output_name
    if target.exists():
        raise PublicationAdapterError("HTML output must be absent")
    derived_source, rebased_assets = _prepare_html_artview_projection(
        master_ru=master_ru,
        artview_decisions=artview_decisions,
        application=application,
        effective=effective,
        effective_visual_config=effective_visual_config,
        artview_projection_root=artview_projection_root,
        authority_root=authority_root,
        artifacts=artifacts,
        evidence=evidence,
    )
    config = copy.deepcopy(_read(config_path))
    policy_contract = _stage40_html_policy(config, derived_source)
    cover_binding = _resolve_required_cover_binding(policy_contract, application, artview_projection_root, artifacts)
    projection = None
    if semantic_authority is not None:
        authority = semantic_authority.resolve(strict=True)
        try:
            authority.relative_to(authority_root)
        except ValueError as error:
            raise PublicationAdapterError("semantic authority escapes run root") from error
        projection = _semantic_html_projection(master_ru, derived_source, authority, authority_root, evidence)
    if cover_binding is not None:
        # Semantic projection requires the accepted MASTER_RU line topology.
        # Replace the cover only after those page-local spans are projected.
        _validate_cover_semantic_separation(cover_binding, projection)
        _replace_source_cover_markdown(derived_source, cover_binding)

    _apply_stage40_html_policy(config, policy_contract)
    production = config.get("production_html")
    if not isinstance(production, dict):
        production = {}; config["production_html"] = production
    production.update({
        "source_markdown": str(derived_source),
        "output_html": str(target),
        "report": str(evidence / "production_html_report.json"),
        "required_gates": ["publication_authorities_validated"],
    })
    compact_statblock_heading_ids = _augment_compact_statblock_policy(
        production, derived_source.read_text(encoding="utf-8"),
    )
    policy = production.get("handout_heading_policy")
    if isinstance(policy, dict):
        policy.pop("output_markdown", None)
    config["scenario_gates"] = {"publication_authorities_validated": True}
    config["production_gates"] = {"publication_authorities_validated": True}
    config["workbench_qa_root"] = str(evidence)
    config["postproduction"] = {"working_qa_root": str(evidence), "qa_output_dir": str(evidence)}
    config["frontmatter"]["report"] = "frontmatter_manifest.json"
    derived = evidence / "derived_html_config.json"
    derived.write_bytes(canonical_bytes(config) + b"\n")
    command = [str(python.resolve(strict=True)), str(TRANSLATOR.resolve(strict=True)), "build-production-html", "--config", str(derived), "--force"]
    if any("pdf" in Path(item).name.lower() for item in command):
        raise PublicationAdapterError("HTML adapter command cannot expose a PDF route")
    if runner is None:
        process = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=300, check=False)
        exit_code = process.returncode
    else:
        exit_code = runner(command, target, evidence / "production_html_report.json")
    if exit_code != 0 or not target.is_file():
        raise PublicationAdapterError(f"production HTML renderer failed with exit {exit_code}")
    report_path = evidence / "production_html_report.json"
    report = _read(report_path)
    if report.get("status") != "pass" or report.get("sha256", "").upper() != _sha(target):
        raise PublicationAdapterError("production HTML report does not bind output")
    manifest_path = evidence / "frontmatter_manifest.json"
    frontmatter_manifest = _read(manifest_path)
    if cover_binding is not None:
        cover_record = frontmatter_manifest.get("cover")
        if not isinstance(cover_record, dict):
            raise PublicationAdapterError("frontmatter manifest cover is missing")
        cover_record["asset"] = {"placement_id": cover_binding["placement_id"], "asset_id": cover_binding["asset_id"], "runtime_src": cover_binding["output_path"], "source_page": f"{cover_binding['source_page']:03d}", "mode": "replace_source_page", "required": True}
        cover_record["mode"] = "replace_source_page"
        cover_record["fit"] = policy_contract["cover"]["fit"]
        manifest_path.write_bytes(canonical_bytes(frontmatter_manifest) + b"\n")
    _validate_stage40_html_output(policy_contract, frontmatter_manifest, target.read_text(encoding="utf-8"))
    if projection is not None:
        html = target.read_text(encoding="utf-8")
        _validate_semantic_cards(html, projection["projected"])
    refs = _local_ref_inventory(target, stage_root)
    receipt = {
        "schema": "kb_creator.publication_html_adapter_receipt.v1",
        "bindings": {
            "master_ru": _identity(master_ru, authority_root),
            "master_ru_acceptance": _identity(master_ru_acceptance, authority_root),
            "artview_decisions": _identity(artview_decisions, authority_root),
            "artview_application": _identity(artview_application, authority_root),
            "effective_visual_config": _identity(effective_visual_config, authority_root),
            "base_config": _identity(config_path, authority_root),
        },
        "derived_source": _identity(derived_source, stage_root),
        "artview_asset_projection": rebased_assets,
        "cover_binding": {key: value for key, value in cover_binding.items() if key != "asset"} if cover_binding is not None else None,
        "semantic_projection": _identity(evidence / "html_semantic_projection.json", stage_root) if projection is not None else None,
        "compact_statblock_heading_ids": compact_statblock_heading_ids,
        "derived_config": _identity(derived, stage_root),
        "html_publication_policy": policy_contract,
        "renderer": {"path": TRANSLATOR.relative_to(REPO_ROOT).as_posix(), **file_identity(TRANSLATOR)},
        "output": _identity(target, stage_root),
        "report": _identity(report_path, stage_root),
        "frontmatter_manifest": _identity(manifest_path, stage_root),
        "local_references": refs,
        "direct_pdf_route": False,
    }
    (evidence / "html_adapter_receipt.json").write_bytes(canonical_bytes(receipt) + b"\n")
    return {"status": "pass", "adapter": "translator_build_production_html_v1", "local_reference_count": len(refs), "direct_pdf_route": False}


def _run_document(invocation: PublicationStageInvocation) -> dict[str, Any]:
    return _read(invocation.run_root / "run.json")


def _config_path(invocation: PublicationStageInvocation, role: str) -> Path:
    run = _run_document(invocation)
    config_root = Path(run["local"]["config_root"]).resolve(strict=True)
    matches = [row for row in invocation.contract["configs"] if row.get("role") == role]
    if len(matches) != 1:
        raise PublicationAdapterError(f"publication config role is not unique: {role}")
    record = matches[0]["file"]
    path = _contained_file(config_root / Path(record["path"]), config_root, f"config {role}")
    if file_identity(path) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
        raise PublicationAdapterError(f"publication config identity drift: {role}")
    return path


def _run_relative(invocation: PublicationStageInvocation, record: object, label: str) -> Path:
    if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
        raise PublicationAdapterError(f"{label} identity shape mismatch")
    raw = record["path"]
    if not isinstance(raw, str) or not raw or "\\" in raw or ":" in raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
        raise PublicationAdapterError(f"{label} path is unsafe")
    path = _contained_file(invocation.run_root / Path(raw), invocation.run_root, label)
    if file_identity(path) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
        raise PublicationAdapterError(f"{label} identity drift")
    return path


def _accepted_candidate(invocation: PublicationStageInvocation, kind: str) -> tuple[Path, Path, dict[str, Any]]:
    key = f"{kind}_acceptance"
    receipt_path = invocation.authorities.get(key)
    if receipt_path is None:
        raise PublicationAdapterError(f"missing exact {key}")
    receipt_path = _contained_file(receipt_path, invocation.run_root, key)
    receipt = _read(receipt_path); _seal(receipt, "receipt_sha256", key)
    if receipt.get("artifact_kind") != kind or receipt.get("decision") != "accepted" or receipt.get("recorder_role") != "main_orchestrator":
        raise PublicationAdapterError(f"invalid {key}")
    return _run_relative(invocation, receipt["candidate"], f"{kind} candidate"), receipt_path, receipt


def _move_children(source: Path, destination: Path) -> None:
    for child in tuple(source.iterdir()):
        target = destination / child.name
        if target.exists():
            raise PublicationAdapterError(f"adapter output collision: {target.name}")
        child.replace(target)
    source.rmdir()


def _stage_path(run_root: Path, ordinal: int, stage: str) -> Path:
    return run_root / "outputs" / f"{ordinal:02d}-{stage.replace('_', '-')}"


def _master_en_adapter(staging: Path, _private: Path, invocation: PublicationStageInvocation) -> dict[str, Any]:
    from kb_creator.scripts.build_scenario_master_en import build_v3_candidate
    from kb_creator.scripts.verify_scenario_master_en import verify_v3_candidate

    source_config_path = _config_path(invocation, "master_en")
    source_config = _read(source_config_path)
    if set(source_config) != {"schema", "scenario_id", "inputs", "projection", "required_qa"} or source_config.get("schema") != "kb_creator.master_en_publication.v3":
        raise PublicationAdapterError("MASTER_EN adapter requires neutral v3 config")
    run = _run_document(invocation)
    source_upstream = Path(run["local"]["upstream_inventory_path"]).resolve(strict=True).parent
    authority = staging / "evidence" / "master_en_authority"
    shutil.copytree(source_upstream, authority / "upstream")
    contract_copy = authority / "publication-contract.json"
    shutil.copy2(Path(run["local"]["contract_path"]), contract_copy)
    inventory_copy = authority / "upstream" / Path(run["local"]["upstream_inventory_path"]).name
    acceptance_copy = authority / "upstream" / Path(run["local"]["reconstruction_acceptance_path"]).name
    inventory = _read(inventory_copy)
    candidates = [row for row in inventory.get("artifacts", []) if row.get("role") == "reconstructed_en"]
    if len(candidates) != 1:
        raise PublicationAdapterError("accepted reconstruction lacks unique reconstructed_en")
    reconstructed = authority / "upstream" / Path(candidates[0]["path"])
    derived = {
        "schema": source_config["schema"], "scenario_id": source_config["scenario_id"],
        "inputs": {
            "publication_contract": _identity(contract_copy, authority),
            "reconstruction_inventory": _identity(inventory_copy, authority),
            "reconstruction_acceptance": _identity(acceptance_copy, authority),
            "reconstructed_en": _identity(reconstructed, authority),
        },
        "projection": source_config["projection"], "required_qa": source_config["required_qa"],
    }
    derived_path = authority / "master_en.runtime.json"; derived_path.write_bytes(canonical_bytes(derived) + b"\n")
    candidate = authority / "candidate"
    result = build_v3_candidate(contract_copy, authority / "upstream", derived_path, Path("candidate"))
    verification = verify_v3_candidate(
        contract_copy,
        authority / "upstream",
        derived_path,
        Path("candidate"),
    )
    expected_verification_keys = {
        "status", "scenario_id", "candidate_inventory_sha256",
        "inventory_file_sha256", "master_en_sha256",
        "publication_config_sha256", "derived",
    }
    if (
        set(verification) != expected_verification_keys
        or verification.get("status") != "verified_candidate_pending_process_and_external_gates"
        or verification.get("scenario_id") != source_config["scenario_id"]
        or verification.get("candidate_inventory_sha256") != result.get("candidate_inventory_sha256")
        or verification.get("inventory_file_sha256") != _sha(candidate / "INVENTORY.json")
        or verification.get("master_en_sha256") != _sha(candidate / "MASTER_EN.md")
        or verification.get("publication_config_sha256") != _sha(derived_path)
        or verification.get("derived") != result.get("derived")
    ):
        raise PublicationAdapterError("independent MASTER_EN verification identity mismatch")
    verification_path = staging / "evidence" / "MASTER_EN.verification.json"
    verification_path.write_bytes(canonical_bytes(verification) + b"\n")
    _move_children(candidate, staging / "artifacts")
    shutil.copy2(staging / "artifacts" / "MASTER_EN.qa.json", staging / "evidence" / "MASTER_EN.qa.json")
    return {
        "status": result["status"],
        "independent_verification": _identity(verification_path, staging),
        "derived_config": _identity(derived_path, staging),
        "source_config": _identity(source_config_path, Path(run["local"]["config_root"])),
    }


def _master_ru_packets_adapter(staging: Path, _private: Path, invocation: PublicationStageInvocation) -> dict[str, Any]:
    from kb_creator.scripts.scenario_master_ru import prepare

    master_en, acceptance, _ = _accepted_candidate(invocation, "master_en")
    config_path = _config_path(invocation, "master_ru"); config = _read(config_path)
    if set(config) != {"schema", "max_batch_chars"} or config.get("schema") != "kb_creator.master_ru_adapter.v1":
        raise PublicationAdapterError("MASTER_RU adapter config is not closed v1")
    config_root = Path(_run_document(invocation)["local"]["config_root"])
    terminology = {}
    for index, record in enumerate(invocation.contract["master_ru"]["terminology"]):
        path = _contained_file(config_root / Path(record["path"]), config_root, f"terminology {index}")
        if file_identity(path) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
            raise PublicationAdapterError("terminology identity drift")
        local_term = staging / "evidence" / "terminology" / f"authority-{index:02d}{path.suffix.lower()}"
        local_term.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, local_term)
        terminology[f"authority_{index:02d}"] = local_term
    target = staging / "evidence" / "packet-build"
    result = prepare(master_en, acceptance, terminology, target, int(config["max_batch_chars"]), invocation.run_root)
    _move_children(target, staging / "artifacts")
    packet_path = staging / "artifacts" / "packet_manifest.json"
    packet = _read(packet_path)
    staging_prefix = staging.relative_to(invocation.run_root).as_posix()
    output_prefix = _stage_path(invocation.run_root, 20, "master_ru_packets").relative_to(invocation.run_root).as_posix()
    for row in packet["terminology"]:
        path = str(row["file"]["path"])
        if not path.startswith(staging_prefix + "/"):
            raise PublicationAdapterError("translation terminology lacks stage-local authority")
        row["file"]["path"] = output_prefix + path[len(staging_prefix):]
    packet["manifest_sha256"] = hashlib.sha256(canonical_bytes({key: item for key, item in packet.items() if key != "manifest_sha256"})).hexdigest().upper()
    packet_path.write_bytes(canonical_bytes(packet) + b"\n")
    return {"status": result["status"], "config": _identity(config_path, config_root)}


def _master_ru_candidate_adapter(staging: Path, _private: Path, invocation: PublicationStageInvocation) -> dict[str, Any]:
    from kb_creator.scripts.scenario_master_ru import assemble
    from kb_creator.scripts.verify_scenario_master_ru import PASS_STATE, verify_candidate

    submission = invocation.authorities["master_ru_submission"]
    packet = _stage_path(invocation.run_root, 20, "master_ru_packets") / "artifacts"
    target = staging / "evidence" / "master-ru-build"
    result = assemble(packet, submission, target, invocation.run_root)
    contract_path = Path(_run_document(invocation)["local"]["contract_path"])
    verification = verify_candidate(
        packet,
        submission,
        target,
        contract_path,
        invocation.run_root,
    )
    inventory = _read(target / "INVENTORY.json")
    if (
        verification.get("status") != PASS_STATE
        or verification.get("scenario_id") != invocation.contract["scenario"]["id"]
        or verification.get("master_ru") != file_identity(target / "MASTER_RU.md")
        or verification.get("submission", {}).get("sha256") != _sha(submission)
        or verification.get("packet_manifest", {}).get("sha256") != _sha(packet / "packet_manifest.json")
        or verification.get("contract") != file_identity(contract_path)
        or verification.get("candidate_inventory", {}).get("inventory_sha256") != inventory["inventory_sha256"]
        or verification.get("required_qa") != invocation.contract["master_ru"]["required_qa"]
        or verification.get("findings") != []
    ):
        raise PublicationAdapterError("independent MASTER_RU verification identity mismatch")
    verification_path = staging / "evidence" / "MASTER_RU.verification.json"
    verification_path.write_bytes(canonical_bytes(verification) + b"\n")
    _move_children(target, staging / "artifacts")
    shutil.copy2(staging / "artifacts" / "MASTER_RU.qa.json", staging / "evidence" / "MASTER_RU.qa.json")
    return {
        "status": result["status"],
        "submission": _identity(submission, invocation.run_root),
        "independent_verification": _identity(verification_path, staging),
    }


def _copy_run_identity_file(invocation: PublicationStageInvocation, record: dict[str, Any], destination_root: Path) -> Path:
    source = _run_relative(invocation, record, "runtime ArtView authority")
    target = destination_root / Path(record["path"])
    target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
    return target


def _materialize_asset_manifest_graph(source_manifest: Path, destination_manifest: Path) -> None:
    manifest = _read(source_manifest)
    rows = manifest.get("assets")
    if not isinstance(rows, list):
        raise PublicationAdapterError("MASTER_RU asset manifest lacks assets")

    source_root = source_manifest.parent.resolve(strict=True)
    assets: dict[str, Path] = {}
    for index, row in enumerate(rows):
        label = f"MASTER_RU asset manifest row {index}"
        if not isinstance(row, dict) or not {"path", "bytes", "sha256"}.issubset(row):
            raise PublicationAdapterError(f"{label} lacks exact identity")
        raw = row["path"]
        if not isinstance(raw, str):
            raise PublicationAdapterError(f"{label} path is unsafe")
        relative = Path(raw)
        if (
            not raw
            or "\\" in raw
            or ":" in raw
            or relative.is_absolute()
            or relative.as_posix() != raw
            or ".." in relative.parts
        ):
            raise PublicationAdapterError(f"{label} path is unsafe")
        try:
            source = _contained_file(source_root / relative, source_root, label)
        except (FileNotFoundError, OSError) as error:
            raise PublicationAdapterError(f"{label} asset is missing") from error
        expected = {"bytes": row["bytes"], "sha256": row["sha256"]}
        if file_identity(source) != expected:
            raise PublicationAdapterError(f"{label} identity drift")
        assets[raw] = source

    destination_manifest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_manifest, destination_manifest)
    for raw, source in assets.items():
        target = destination_manifest.parent / Path(raw)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _v4_source_pdf_authority(invocation: PublicationStageInvocation, authority: Path) -> tuple[Path, Path, Path]:
    """Bind ArtView v4 to the accepted reconstruction's sealed local PDF.

    The promoted inventory intentionally remains portable and therefore cannot
    carry an ambient machine path.  Its containing reconstruction run may carry
    one local source path, but only after its portable identity and the copied
    source-identity authority agree byte-for-byte is that path usable.
    """
    run = _run_document(invocation)
    try:
        inventory_path = Path(run["local"]["upstream_inventory_path"]).resolve(strict=True)
    except (KeyError, OSError) as error:
        raise PublicationAdapterError("ArtView v4 lacks sealed reconstruction inventory") from error
    upstream = inventory_path.parent
    inventory = _read(inventory_path)
    rows = [row for row in inventory.get("artifacts", []) if row.get("role") == "source_identity"]
    if len(rows) != 1 or not isinstance(rows[0].get("path"), str):
        raise PublicationAdapterError("accepted reconstruction lacks unique source identity")
    identity_source = _contained_file(upstream / Path(rows[0]["path"]), upstream, "reconstruction source identity")
    expected = {"bytes": rows[0].get("bytes"), "sha256": rows[0].get("sha256")}
    if file_identity(identity_source) != expected:
        raise PublicationAdapterError("accepted reconstruction source identity drift")
    manifest_rows = [row for row in inventory.get("artifacts", []) if row.get("role") == "reconstruction_manifest"]
    if len(manifest_rows) != 1 or not isinstance(manifest_rows[0].get("path"), str):
        raise PublicationAdapterError("accepted reconstruction lacks unique reconstruction manifest")
    manifest_source = _contained_file(upstream / Path(manifest_rows[0]["path"]), upstream, "reconstruction manifest")
    if file_identity(manifest_source) != {"bytes": manifest_rows[0].get("bytes"), "sha256": manifest_rows[0].get("sha256")}:
        raise PublicationAdapterError("accepted reconstruction manifest identity drift")
    manifest = _read(manifest_source); _seal(manifest, "manifest_sha256", "reconstruction manifest")
    review = manifest.get("review")
    decisions = review.get("decisions") if isinstance(review, dict) else None
    if not isinstance(decisions, list) or not decisions:
        raise PublicationAdapterError("reconstruction manifest lacks review decision graph")
    decision_sources: list[tuple[Path, Path]] = []
    seen_decisions: set[str] = set()
    for index, record in enumerate(decisions):
        if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
            raise PublicationAdapterError(f"reconstruction review decision {index} identity shape mismatch")
        raw = record["path"]
        if not isinstance(raw, str) or raw in seen_decisions:
            raise PublicationAdapterError("reconstruction review decisions are duplicate or unsafe")
        seen_decisions.add(raw)
        source_decision = _contained_file(upstream / Path(raw), upstream, f"reconstruction review decision {index}")
        if file_identity(source_decision) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
            raise PublicationAdapterError("reconstruction review decision identity drift")
        decision_sources.append((source_decision, Path(raw)))
    source_identity = _read(identity_source); _seal(source_identity, "source_identity_sha256", "reconstruction source identity")
    source = source_identity.get("source", source_identity)
    if not isinstance(source, dict) or not isinstance(source.get("bytes"), int) or not isinstance(source.get("sha256"), str):
        raise PublicationAdapterError("accepted reconstruction source identity is invalid")

    # The reconstruction run is an explicit upstream authority, not a guessed
    # PDF location.  Verify its portable portion before consuming local data.
    reconstruction_run = upstream.parent.parent / "run.json"
    try:
        reconstruction = _read(reconstruction_run)
    except (OSError, PublicationAdapterError) as error:
        raise PublicationAdapterError("ArtView v4 requires the sealed reconstruction run authority") from error
    portable = {key: value for key, value in reconstruction.items() if key not in {"local", "portable_identity_sha256"}}
    portable_sha = reconstruction.get("portable_identity_sha256")
    if not isinstance(portable_sha, str) or hashlib.sha256(canonical_bytes(portable)).hexdigest().upper() != portable_sha:
        raise PublicationAdapterError("reconstruction portable identity drift")
    try:
        promoted_portable = _read(upstream / "evidence" / "run" / "run.portable.json")
    except (OSError, PublicationAdapterError) as error:
        raise PublicationAdapterError("accepted reconstruction lacks portable run evidence") from error
    if promoted_portable.get("portable_identity_sha256") != portable_sha:
        raise PublicationAdapterError("promoted reconstruction run identity drift")
    run_source = reconstruction.get("source")
    if not isinstance(run_source, dict) or any(run_source.get(key) != source.get(key) for key in ("bytes", "sha256", "page_count")):
        raise PublicationAdapterError("reconstruction source identity drift")
    promoted_source = promoted_portable.get("source")
    if not isinstance(promoted_source, dict) or any(promoted_source.get(key) != source.get(key) for key in ("bytes", "sha256", "page_count")):
        raise PublicationAdapterError("promoted reconstruction source identity drift")
    local = reconstruction.get("local")
    if not isinstance(local, dict) or not isinstance(local.get("source_path"), str):
        raise PublicationAdapterError("reconstruction run lacks local source PDF authority")
    try:
        pdf_source = Path(local["source_path"]).resolve(strict=True)
    except OSError as error:
        raise PublicationAdapterError("reconstruction source PDF is unavailable") from error
    if file_identity(pdf_source) != {"bytes": source["bytes"], "sha256": source["sha256"]}:
        raise PublicationAdapterError("reconstruction source PDF identity drift")

    inventory_copy = authority / "upstream" / "RECONSTRUCTION_INVENTORY.json"
    identity_copy = authority / "upstream" / "SOURCE_IDENTITY.json"
    manifest_copy = authority / "upstream" / Path(manifest_rows[0]["path"])
    pdf_copy = authority / "source" / pdf_source.name
    for original, copied in ((inventory_path, inventory_copy), (identity_source, identity_copy), (manifest_source, manifest_copy), (pdf_source, pdf_copy)):
        copied.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(original, copied)
    for source_decision, relative in decision_sources:
        copied = authority / "upstream" / relative
        copied.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source_decision, copied)
    return inventory_copy, identity_copy, pdf_copy


def _artview_bundle_adapter(staging: Path, _private: Path, invocation: PublicationStageInvocation, pdftoppm: Path | None = None) -> dict[str, Any]:
    from kb_creator.scripts import scenario_artview

    master_ru, acceptance_path, acceptance = _accepted_candidate(invocation, "master_ru")
    source_profile_path = _config_path(invocation, "artview")
    source_profile = _read(source_profile_path)
    schema = source_profile.get("schema")
    if schema not in {scenario_artview.PROFILE_SCHEMA_V3, scenario_artview.PROFILE_SCHEMA_V4}:
        raise PublicationAdapterError("ArtView adapter requires v3 or v4 profile")
    authority = staging / "evidence" / "artview_authority"
    shutil.copytree(source_profile_path.parent, authority)
    candidate_copy = _copy_run_identity_file(invocation, acceptance["candidate"], authority)
    acceptance_copy = authority / acceptance_path.relative_to(invocation.run_root)
    acceptance_copy.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(acceptance_path, acceptance_copy)
    _copy_run_identity_file(invocation, acceptance["producer_stage"], authority)
    for record in acceptance["evidence"]:
        _copy_run_identity_file(invocation, record, authority)
    asset_manifest = _stage_path(invocation.run_root, 21, "master_ru_candidate") / "artifacts" / "ASSET_MANIFEST.json"
    asset_copy = authority / asset_manifest.relative_to(invocation.run_root)
    _materialize_asset_manifest_graph(asset_manifest, asset_copy)
    derived = copy.deepcopy(source_profile)
    derived["output_root"] = "artview-build"
    derived["inputs"]["master_ru"] = _identity(candidate_copy, authority)
    derived["inputs"]["master_ru_acceptance"] = _identity(acceptance_copy, authority)
    derived["inputs"]["master_ru_asset_manifest"] = _identity(asset_copy, authority)
    if schema == scenario_artview.PROFILE_SCHEMA_V4:
        inventory_copy, identity_copy, pdf_copy = _v4_source_pdf_authority(invocation, authority)
        derived["inputs"]["reconstruction_inventory"] = _identity(inventory_copy, authority)
        derived["inputs"]["source_identity"] = _identity(identity_copy, authority)
        derived["inputs"]["source_pdf"] = _identity(pdf_copy, authority)
    derived_path = authority / "profile.runtime.json"; derived_path.write_bytes(canonical_bytes(derived) + b"\n")
    # One dispatch point preserves v3 while making the v4 discovery invocation
    # auditable and impossible to split into an authored pre-pass.
    result = scenario_artview.build(derived_path, str(pdftoppm) if pdftoppm is not None else None, False)
    candidate = authority / "artview-build" / "candidate"
    _move_children(candidate, staging / "artifacts")
    shutil.copy2(staging / "artifacts" / "qa.json", staging / "evidence" / "artview.qa.json")
    shutil.rmtree(authority / "artview-build")
    return {"status": result["status"], "derived_profile": _identity(derived_path, staging)}


def _artview_apply_adapter(staging: Path, _private: Path, invocation: PublicationStageInvocation) -> dict[str, Any]:
    from kb_creator.scripts.scenario_artview_apply import apply

    _, acceptance, _ = _accepted_candidate(invocation, "artview")
    decisions = invocation.authorities["artview_decisions"]
    profile = _stage_path(invocation.run_root, 30, "artview_bundle") / "evidence" / "artview_authority" / "profile.runtime.json"
    manifest = _stage_path(invocation.run_root, 30, "artview_bundle") / "artifacts" / "candidate_manifest.json"
    target = staging / "evidence" / "artview-apply-build"
    result = apply(profile, decisions, acceptance, target.relative_to(invocation.run_root).as_posix(), invocation.run_root, manifest.relative_to(invocation.run_root))
    _move_children(target, staging / "artifacts")
    return {"status": result["status"], "candidate_manifest": _identity(manifest, invocation.run_root)}


def _html_adapter(staging: Path, _private: Path, invocation: PublicationStageInvocation, runtime: PublicationAdapterRuntime) -> dict[str, Any]:
    master, acceptance, _ = _accepted_candidate(invocation, "master_ru")
    artview_acceptance = invocation.authorities["artview_acceptance"]
    decisions = invocation.authorities["artview_decisions"]
    stage31 = _stage_path(invocation.run_root, 31, "artview_apply") / "artifacts"
    source_config = _config_path(invocation, "html")
    stage_config = staging / "evidence" / "source_html_config.json"; shutil.copy2(source_config, stage_config)
    result = build_html_candidate(
        master_ru=master, master_ru_acceptance=acceptance, artview_decisions=decisions,
        artview_application=stage31 / "ARTVIEW_APPLIED.json", effective_visual_config=stage31 / "effective_visual_config.json",
        artview_projection_root=stage31, base_config=stage_config, staging=staging,
        semantic_authority=_stage_path(invocation.run_root, 10, "master_en_candidate") / "evidence" / "master_en_authority" / "upstream",
        output_name=invocation.contract["artifact_names"]["html"], python=runtime.python, runner=runtime.html_runner,
    )
    return {**result, "source_config_sha256": _sha(source_config)}


def _docx_adapter(staging: Path, private: Path, invocation: PublicationStageInvocation, runtime: PublicationAdapterRuntime) -> dict[str, Any]:
    from kb_creator.scripts.production_docx import build_docx
    from kb_creator.scripts.publication_render_qa import render_docx_transient

    html, _, _ = _accepted_candidate(invocation, "html")
    target = staging / "artifacts" / invocation.contract["artifact_names"]["docx"]
    reviewed = invocation.authorities.get("reviewed_docx")
    if reviewed is None:
        result = build_docx(html, target, config=_config_path(invocation, "docx"))
    else:
        # Rebuild the normal HTML projection for comparison, but retain the
        # reviewer's exact OOXML bytes as the candidate. Never patch a sealed
        # Stage-50 output or quietly regenerate over human editorial work.
        baseline = staging / "baseline.docx"
        try:
            baseline_result = build_docx(html, baseline, config=_config_path(invocation, "docx"))
            with zipfile.ZipFile(reviewed) as archive:
                if archive.testzip() is not None or "word/document.xml" not in archive.namelist():
                    raise PublicationAdapterError("reviewed DOCX is not a valid OOXML package")
            shutil.copy2(reviewed, target)
            source_identity = next(row["file"] for row in invocation.authority_inputs if row["kind"] == "reviewed_docx")
            if _identity(target, staging)["sha256"] != source_identity["sha256"] or target.stat().st_size != source_identity["bytes"]:
                raise PublicationAdapterError("reviewed DOCX changed during Stage 50 copy")
            result = {
                "status": "pass", "mode": "reviewed_docx", "reviewed_input": source_identity,
                "candidate": _identity(target, staging),
                "html_projection": {key: value for key, value in baseline_result.items() if key not in {"output", "sha256"}},
                "baseline_sha256": _sha(baseline),
            }
        finally:
            baseline.unlink(missing_ok=True)
    private.parent.mkdir(parents=True, exist_ok=True)
    render = render_docx_transient(
        target, staging / "evidence" / "docx_render", private,
        REPO_ROOT / "kb_creator" / "scripts" / "export_docx_to_pdf.ps1",
        runtime.powershell, runtime.pdftoppm, export=runtime.transient_export,
        python=runtime.python, libreoffice=runtime.libreoffice,
        local_exporter_script=REPO_ROOT / "kb_creator" / "scripts" / "export_docx_to_pdf_local.py",
        stage_root=invocation.run_root,
    )
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None or "word/document.xml" not in archive.namelist():
            raise PublicationAdapterError("DOCX OOXML verification failed")
    (staging / "evidence" / "docx_build.json").write_bytes(canonical_bytes(result) + b"\n")
    return {
        "status": "pass", "ooxml": "pass", "page_count": render["page_count"],
        "document_authority_kind": "reviewed_docx" if reviewed is not None else "generated_docx",
        "transient_bridge_cleanup": "pass", "render_engine": render["export_engine"],
    }


def _validate_word_export_evidence(path: Path, docx: Path, pdf: Path, expected_word: Path) -> None:
    value = _read(path)
    if set(value) != {"schema", "status", "input", "output", "word", "export", "cleanup", "elapsed_ms"}:
        raise PublicationAdapterError("Word export evidence is not closed")
    if value["schema"] != "kb_creator.word_docx_pdf_export.v1" or value["status"] != "pass":
        raise PublicationAdapterError("Word export evidence did not pass")
    for label, record, source in (("input", value["input"], docx), ("output", value["output"], pdf)):
        if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
            raise PublicationAdapterError(f"Word export {label} identity is not closed")
        if Path(record["path"]).resolve(strict=True) != source.resolve(strict=True) or {key: record[key] for key in ("bytes", "sha256")} != file_identity(source):
            raise PublicationAdapterError(f"Word export {label} identity mismatch")
    word = value["word"]
    if not isinstance(word, dict) or set(word) != {"path", "version"} or not isinstance(word["version"], str) or not word["version"].strip():
        raise PublicationAdapterError("Word export tool identity is not closed")
    if Path(word["path"]).resolve(strict=True) != expected_word.resolve(strict=True):
        raise PublicationAdapterError("Word COM executable differs from the bound runtime identity")
    expected_export = {
        "export_format": 17, "optimize_for": 0, "range": 0, "item": 0,
        "include_doc_props": True, "create_bookmarks": 1, "doc_structure_tags": True,
        "bitmap_missing_fonts": True, "use_iso_19005_1": False, "all_pages": True,
        "fresh_export": True,
    }
    if value["export"] != expected_export:
        raise PublicationAdapterError("Word export arguments differ from the fixed policy")
    expected_cleanup = {"document_closed": True, "word_quit": True, "temporary_output_absent": True, "status": "pass"}
    if value["cleanup"] != expected_cleanup or not isinstance(value["elapsed_ms"], int) or value["elapsed_ms"] < 0:
        raise PublicationAdapterError("Word export cleanup evidence is invalid")


def _validate_libreoffice_export_evidence(path: Path, docx: Path, pdf: Path, expected: Path) -> None:
    value = _read(path)
    if set(value) != {"schema", "status", "input", "output", "engine", "export", "cleanup", "elapsed_ms"}:
        raise PublicationAdapterError("LibreOffice export evidence is not closed")
    if value["schema"] != "kb_creator.local_libreoffice_docx_pdf_export.v1" or value["status"] != "pass":
        raise PublicationAdapterError("LibreOffice export evidence did not pass")
    for label, record, source in (("input", value["input"], docx), ("output", value["output"], pdf)):
        if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
            raise PublicationAdapterError(f"LibreOffice export {label} identity is not closed")
        if Path(record["path"]).resolve(strict=True) != source.resolve(strict=True) or {key: record[key] for key in ("bytes", "sha256")} != file_identity(source):
            raise PublicationAdapterError(f"LibreOffice export {label} identity mismatch")
    engine = value["engine"]
    if not isinstance(engine, dict) or set(engine) != {"path", "bytes", "sha256", "name", "version"} or engine["name"] != "libreoffice" or not str(engine["version"]).strip():
        raise PublicationAdapterError("LibreOffice engine identity is not closed")
    if Path(engine["path"]).resolve(strict=True) != expected.resolve(strict=True) or {key: engine[key] for key in ("bytes", "sha256")} != file_identity(expected):
        raise PublicationAdapterError("LibreOffice executable differs from the bound runtime identity")
    if value["export"] != {
        "filter": "writer_pdf_Export", "headless": True, "all_pages": True,
        "fresh_export": True, "document_input_role": "accepted_docx",
    }:
        raise PublicationAdapterError("LibreOffice export arguments differ from the fixed policy")
    expected_cleanup = {"profile_absent": True, "conversion_workspace_absent": True, "temporary_output_absent": True, "status": "pass"}
    if value["cleanup"] != expected_cleanup or not isinstance(value["elapsed_ms"], int) or value["elapsed_ms"] < 0:
        raise PublicationAdapterError("LibreOffice export cleanup evidence is invalid")


def _pdf_adapter(staging: Path, _private: Path, invocation: PublicationStageInvocation, runtime: PublicationAdapterRuntime) -> dict[str, Any]:
    from kb_creator.scripts.publication_render_qa import render_pdf_pages

    docx, _, _ = _accepted_candidate(invocation, "docx")
    target = staging / "artifacts" / invocation.contract["artifact_names"]["pdf"]
    export_evidence = staging / "evidence" / "docx_pdf_export.json"
    if runtime.final_export is not None:
        runtime.final_export(docx, target, export_evidence, invocation.run_root)
    elif runtime.libreoffice is not None:
        process = subprocess.run(
            [
                str(runtime.python), "-I", str(REPO_ROOT / "kb_creator" / "scripts" / "export_docx_to_pdf_local.py"),
                "--docx", str(docx), "--pdf", str(target), "--stage-root", str(invocation.run_root),
                "--libreoffice", str(runtime.libreoffice), "--evidence-output", str(export_evidence),
            ],
            capture_output=True, text=True, timeout=300, check=False,
        )
        if process.returncode != 0:
            raise PublicationAdapterError(f"LibreOffice DOCX export failed with exit {process.returncode}: {process.stderr[-500:]}")
    else:
        process = subprocess.run(
            [str(runtime.powershell), "-NoProfile", "-File", str(REPO_ROOT / "kb_creator" / "scripts" / "export_docx_to_pdf.ps1"), "-Docx", str(docx), "-Pdf", str(target), "-StageRoot", str(invocation.run_root), "-EvidenceOutput", str(export_evidence)],
            capture_output=True, text=True, timeout=300, check=False,
        )
        if process.returncode != 0:
            raise PublicationAdapterError(f"Word DOCX export failed with exit {process.returncode}")
    if not target.is_file() or not export_evidence.is_file():
        raise PublicationAdapterError("DOCX export lacks output or evidence")
    if runtime.final_export is None:
        if runtime.libreoffice is not None:
            _validate_libreoffice_export_evidence(export_evidence, docx, target, runtime.libreoffice)
            engine = "libreoffice"
        else:
            assert runtime.word is not None
            _validate_word_export_evidence(export_evidence, docx, target, runtime.word)
            engine = "microsoft_word_com"
    else:
        engine = "injected_test"
    render = render_pdf_pages(target, staging / "evidence" / "final_render", runtime.pdftoppm, source_kind="final_pdf")
    return {
        "document_authority_kind": "accepted_docx", "adapter": "docx_pdf_export_v1",
        "export_engine": engine, "fresh_export": True, "page_count": render["page_count"],
    }


def _copy_file(source: Path, target: Path) -> None:
    if target.exists():
        raise PublicationAdapterError(f"package target collision: {target}")
    target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)


def _copy_terminology_authorities(records: object, config_root: Path, target_root: Path) -> None:
    if not isinstance(records, list) or not records:
        raise PublicationAdapterError("package requires terminology authorities")
    terminology_identities: set[tuple[str, int, str]] = set()
    resolved: list[tuple[Path, str]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
            raise PublicationAdapterError(f"package terminology {index} identity shape mismatch")
        raw = record["path"]
        if not isinstance(raw, str) or not raw or "\\" in raw or ":" in raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
            raise PublicationAdapterError(f"package terminology {index} path is unsafe")
        source = _contained_file(config_root / Path(raw), config_root, f"package terminology {index}")
        expected = {"bytes": record["bytes"], "sha256": record["sha256"]}
        if file_identity(source) != expected:
            raise PublicationAdapterError(f"package terminology identity drift: {index}")
        suffix = source.suffix.lower()
        if suffix not in {".json", ".csv", ".md"}:
            raise PublicationAdapterError(f"unsupported package terminology suffix: {suffix or '<none>'}")
        canonical_path = source.relative_to(config_root.resolve(strict=True)).as_posix().casefold()
        exact_identity = (canonical_path, record["bytes"], record["sha256"])
        if exact_identity in terminology_identities:
            raise PublicationAdapterError("duplicate package terminology authority identity")
        terminology_identities.add(exact_identity)
        resolved.append((source, suffix))
    for index, (source, suffix) in enumerate(resolved):
        _copy_file(source, target_root / f"authority-{index:02d}{suffix}")


def assemble_production_package(staging: Path, invocation: PublicationStageInvocation) -> dict[str, Any]:
    raise PublicationAdapterError(DOCX_ONLY_ROUTE)
    package = staging / "artifacts" / "package"
    if package.exists():
        raise PublicationAdapterError("production package target must be absent")
    package.mkdir()
    names = invocation.contract["artifact_names"]
    candidate_roles = {}
    candidate_sources: dict[str, Path] = {}
    for kind, filename in (("master_en", names["master_en"]), ("master_ru", names["master_ru"]), ("html", names["html"]), ("docx", names["docx"]), ("pdf", names["pdf"])):
        candidate, receipt, _ = _accepted_candidate(invocation, kind)
        _copy_file(candidate, package / filename); candidate_roles[kind] = filename; candidate_sources[kind] = candidate
        _copy_file(receipt, package / "acceptance" / f"{kind}.json")
    _copy_html_runtime_files(candidate_sources["html"], package / names["html"])
    artview_candidate, artview_receipt, _ = _accepted_candidate(invocation, "artview")
    stage30 = _stage_path(invocation.run_root, 30, "artview_bundle") / "artifacts"
    shutil.copytree(stage30, package / "artview" / "bundle")
    _copy_file(artview_receipt, package / "acceptance" / "artview.json")
    artview_value = _read(artview_receipt)
    decision_sources: list[tuple[dict[str, Any], Path]] = []
    evidence = artview_value.get("evidence", [])
    if not isinstance(evidence, list):
        raise PublicationAdapterError("ArtView acceptance evidence must be a list")
    for row in evidence:
        if isinstance(row, dict) and str(row.get("path", "")).lower().endswith(".json"):
            source = _safe_identity_file(row, invocation.run_root, "accepted ArtView evidence")
            if _read(source).get("schema") in {"kb_creator.scenario_artview_decisions.v3", "kb_creator.scenario_artview_decisions.v4"}:
                decision_sources.append((row, source))
    if len(decision_sources) != 1:
        raise PublicationAdapterError("ArtView acceptance must bind exactly one decision JSON")
    decision_record, decision_source = decision_sources[0]
    artview_decisions_path = decision_record["path"]
    _copy_file(decision_source, package / Path(artview_decisions_path))
    stage31 = _stage_path(invocation.run_root, 31, "artview_apply") / "artifacts"
    _copy_file(stage31 / "ARTVIEW_APPLIED.json", package / "artview" / "ARTVIEW_APPLIED.json")
    _copy_file(stage31 / "effective_visual_config.json", package / "artview" / "effective_visual_config.json")
    config_root = Path(_run_document(invocation)["local"]["config_root"])
    for row in invocation.contract["configs"]:
        source = _contained_file(config_root / Path(row["file"]["path"]), config_root, f"package config {row['role']}")
        _copy_file(source, package / "configs" / "source" / f"{row['role']}{source.suffix.lower()}")
    _copy_terminology_authorities(
        invocation.contract["master_ru"]["terminology"], config_root,
        package / "configs" / "source" / "terminology",
    )
    _copy_file(invocation.run_root / "effective_publication_config.json", package / "configs" / "effective.json")
    for output in sorted((invocation.run_root / "outputs").glob("*")):
        evidence = output / "evidence"
        for source in sorted(evidence.rglob("*config*.json")) if evidence.is_dir() else ():
            _copy_file(source, package / "configs" / "derived" / output.name / source.name)
        for source in sorted(evidence.rglob("*profile*.json")) if evidence.is_dir() else ():
            target = package / "configs" / "derived" / output.name / source.name
            if not target.exists(): _copy_file(source, target)
    stage50 = _read(invocation.run_root / "evidence" / "stages" / "50-docx-candidate.manifest.json")
    reviewed_inputs = [row for row in stage50["reproducible"]["inputs"] if row["kind"] == "reviewed_docx"]
    if reviewed_inputs:
        source = _safe_identity_file(reviewed_inputs[0]["file"], invocation.run_root, "reviewed DOCX submission")
        _copy_file(source, package / "submissions" / "reviewed_docx.docx")
    stage_records = []
    for index, (ordinal, stage) in enumerate(zip((10, 20, 21, 30, 31, 40, 50, 60), STAGES[:8])):
        source = invocation.run_root / "evidence" / "stages" / f"{ordinal:02d}-{stage.replace('_', '-')}.manifest.json"
        target = package / "evidence" / "stages" / source.name; _copy_file(source, target)
        stage_records.append(_identity(target, package))
    run = _run_document(invocation); repo = Path(run["local"]["repo_root"])
    for record in run["implementation"]["files"]:
        source = _contained_file(repo / Path(record["path"]), repo, "implementation snapshot")
        _copy_file(source, package / "pipeline" / "snapshot" / Path(record["path"]))
    contracts = REPO_ROOT / "kb_creator" / "contracts"
    for source in sorted(contracts.glob("*.schema.json")):
        _copy_file(source, package / "pipeline" / "schema_snapshot" / source.name)
    verifier = package / "pipeline" / "verify.py"
    _copy_file(REPO_ROOT / "kb_creator" / "scripts" / "verify_production_package.py", verifier)
    (package / "README.md").write_text("# Production candidate\n\nState: candidate_for_release_review. This package is not a release.\n", encoding="utf-8", newline="\n")
    upstream_root = Path(run["local"]["upstream_inventory_path"]).parent
    upstream_paths = {}
    for key, source in (
        ("reconstruction_inventory", Path(run["local"]["upstream_inventory_path"])),
        ("reconstruction_acceptance", Path(run["local"]["reconstruction_acceptance_path"])),
    ):
        target = package / "upstream" / source.name; _copy_file(source, target); upstream_paths[key] = _identity(target, package)
    inventory_value = _read(Path(run["local"]["upstream_inventory_path"]))
    source_rows = [row for row in inventory_value.get("artifacts", []) if row.get("role") == "source_identity"]
    if len(source_rows) != 1:
        raise PublicationAdapterError("package requires exact source identity")
    source_identity = _contained_file(upstream_root / Path(source_rows[0]["path"]), upstream_root, "source identity")
    target_identity = package / "upstream" / source_identity.name; _copy_file(source_identity, target_identity); upstream_paths["source_identity"] = _identity(target_identity, package)
    roles = [
        {"role": "master_en", "path": names["master_en"]}, {"role": "master_en_acceptance", "path": "acceptance/master_en.json"},
        {"role": "master_ru", "path": names["master_ru"]}, {"role": "master_ru_acceptance", "path": "acceptance/master_ru.json"},
        {"role": "artview_bundle", "path": "artview/bundle"}, {"role": "artview_candidate_manifest", "path": "artview/bundle/candidate_manifest.json"},
        {"role": "artview_decisions", "path": artview_decisions_path}, {"role": "artview_application", "path": "artview/ARTVIEW_APPLIED.json"},
        {"role": "artview_effective_config", "path": "artview/effective_visual_config.json"}, {"role": "artview_acceptance", "path": "acceptance/artview.json"},
        {"role": "html", "path": names["html"]}, {"role": "html_acceptance", "path": "acceptance/html.json"},
        {"role": "docx", "path": names["docx"]}, {"role": "docx_acceptance", "path": "acceptance/docx.json"},
        {"role": "pdf", "path": names["pdf"]}, {"role": "pdf_acceptance", "path": "acceptance/pdf.json"},
        {"role": "source_configs", "path": "configs/source"}, {"role": "effective_config", "path": "configs/effective.json"},
        {"role": "stage_evidence", "path": "evidence/stages"}, {"role": "pipeline_snapshot", "path": "pipeline/snapshot"},
        {"role": "schema_snapshot", "path": "pipeline/schema_snapshot"}, {"role": "offline_verifier", "path": "pipeline/verify.py"},
    ]
    if reviewed_inputs:
        roles.append({"role": "reviewed_docx_submission", "path": "submissions/reviewed_docx.docx"})
    acceptance_records = [_identity(package / "acceptance" / f"{kind}.json", package) for kind in ("master_en", "master_ru", "artview", "html", "docx", "pdf")]
    config_records = [_identity(path, package) for path in sorted((package / "configs").rglob("*") ) if path.is_file()]
    pipeline_records = [_identity(path, package) for path in sorted((package / "pipeline").rglob("*")) if path.is_file()]
    from .identity import deterministic_inventory
    files = deterministic_inventory(package)
    manifest = sealed("kb_creator.production_package_manifest.v1", {
        "scenario_id": invocation.contract["scenario"]["id"], "package_state": "candidate_for_release_review", "release_state": "not_reviewed",
        "publication_run_identity_sha256": run["portable_identity_sha256"], "roles": roles, "inventory": files,
        "stage_manifests": stage_records, "acceptance_receipts": acceptance_records, "config_inventory": config_records,
        "pipeline_snapshot": pipeline_records, "upstream": upstream_paths,
    }, digest_key="manifest_sha256")
    (package / "PRODUCTION_MANIFEST.json").write_bytes(canonical_bytes(manifest) + b"\n")
    return {"status": "candidate_for_release_review", "manifest_sha256": manifest["manifest_sha256"], "pdf_count": 1}


def _package_adapter(staging: Path, _private: Path, invocation: PublicationStageInvocation) -> dict[str, Any]:
    return assemble_production_package(staging, invocation)


def _offline_adapter(staging: Path, _private: Path, invocation: PublicationStageInvocation, runtime: PublicationAdapterRuntime) -> dict[str, Any]:
    package = _stage_path(invocation.run_root, 70, "production_package") / "artifacts" / "package"
    verifier = package / "pipeline" / "verify.py"
    process = subprocess.run([str(runtime.python), "-I", str(verifier), "--package-root", str(package)], capture_output=True, text=True, timeout=180, check=False)
    if process.returncode != 0:
        raise PublicationAdapterError(f"copied offline verifier failed with exit {process.returncode}")
    try: result = json.loads(process.stdout)
    except json.JSONDecodeError as error: raise PublicationAdapterError("copied offline verifier returned invalid JSON") from error
    if result.get("state") != "candidate_for_release_review" or result.get("release_state") != "not_reviewed":
        raise PublicationAdapterError("copied offline verifier returned unsafe state")
    output = staging / "artifacts" / "offline_verify.json"; output.write_bytes(canonical_bytes(result) + b"\n")
    return {"status": "candidate_for_release_review", "isolated_python": True, "copied_verifier": True}


def fixed_publication_adapters(runtime: PublicationAdapterRuntime) -> dict[str, PublicationStageAdapter]:
    raise PublicationAdapterError(DOCX_ONLY_ROUTE)
    tools_root = (REPO_ROOT / ".tools").resolve(strict=True)
    python = runtime.python.resolve(strict=True); pdftoppm = runtime.pdftoppm.resolve(strict=True)
    for path, label in ((python, "publication Python"), (pdftoppm, "Poppler")):
        try: path.relative_to(tools_root)
        except ValueError as error: raise PublicationAdapterError(f"{label} must resolve below repository .tools") from error
    if (runtime.word is None) == (runtime.libreoffice is None):
        raise PublicationAdapterError("exactly one DOCX-to-PDF engine must be bound")
    if pdftoppm.name.lower() not in {"pdftoppm", "pdftoppm.exe"}:
        raise PublicationAdapterError("fixed publication runtime tool identity mismatch")
    common_records = (
        {"name": "publication_python", "version": f"sha256:{_sha(python)}", "scope": "repository_tools"},
        {"name": "pdftoppm", "version": f"sha256:{_sha(pdftoppm)}", "scope": "repository_tools"},
    )
    if runtime.libreoffice is not None:
        libreoffice = runtime.libreoffice.resolve(strict=True)
        try: libreoffice.relative_to(tools_root)
        except ValueError as error: raise PublicationAdapterError("LibreOffice must resolve below repository .tools") from error
        if libreoffice.name.lower() not in {"soffice", "soffice.exe", "soffice.com", "libreoffice", "libreoffice.exe"}:
            raise PublicationAdapterError("fixed publication LibreOffice identity mismatch")
        tool_records = (*common_records, {"name": "libreoffice", "version": f"sha256:{_sha(libreoffice)}", "scope": "repository_tools"})
    else:
        powershell = runtime.powershell.resolve(strict=True)
        assert runtime.word is not None
        word = runtime.word.resolve(strict=True)
        if powershell.name.lower() not in {"powershell.exe", "pwsh.exe"} or word.name.lower() != "winword.exe":
            raise PublicationAdapterError("fixed publication Word runtime tool identity mismatch")
        tool_records = (*common_records,
            {"name": "powershell", "version": f"sha256:{_sha(powershell)}", "scope": "allowed_system"},
            {"name": "microsoft_word_com", "version": f"sha256:{_sha(word)}", "scope": "allowed_system"},
        )
    bindings: dict[str, Callable[..., dict[str, Any]]] = {
        "master_en_candidate": _master_en_adapter,
        "master_ru_packets": _master_ru_packets_adapter,
        "master_ru_candidate": _master_ru_candidate_adapter,
        "artview_bundle": lambda staging, private, invocation: _artview_bundle_adapter(staging, private, invocation, runtime.pdftoppm),
        "artview_apply": _artview_apply_adapter,
        "html_candidate": lambda staging, private, invocation: _html_adapter(staging, private, invocation, runtime),
        "docx_candidate": lambda staging, private, invocation: _docx_adapter(staging, private, invocation, runtime),
        "pdf_candidate": lambda staging, private, invocation: _pdf_adapter(staging, private, invocation, runtime),
        "production_package": _package_adapter,
        "offline_verify": lambda staging, private, invocation: _offline_adapter(staging, private, invocation, runtime),
    }
    if set(bindings) != set(STAGES):
        raise PublicationAdapterError("fixed publication adapter registry is incomplete")
    return {stage: PublicationStageAdapter(ADAPTER_NAMES[stage], bindings[stage], True, tool_records) for stage in STAGES}
