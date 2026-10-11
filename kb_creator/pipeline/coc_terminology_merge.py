"""Consolidate attested terminology without promoting unresolved decisions."""
from __future__ import annotations
import csv
import io
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from .coc_glossary import HEADER, digest, identity, normalize, registry_rows, usage_rule, _write


def _replace_registry(registry: Path, before: bytes, after: bytes) -> None:
    """Publish complete CSV bytes without truncating a possibly mapped file."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=registry.parent, prefix=".terminology-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(after)
            stream.flush()
            os.fsync(stream.fileno())
        if registry.read_bytes() != before:
            raise ValueError("terminology registry changed before replacement")
        os.replace(temporary, registry)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _verify_extracted_pair(record: dict) -> None:
    fields = record["original_fields"]
    source = next((fields[key] for key in ("source_term", "source", "English", "Source spell", "Source term", "term", "Source") if key in fields), None)
    target = next((fields[key] for key in ("target", "accepted_ru", "RU form", "Current RU source form", "Русская форма", "ru_term", "candidate_ru", "proposed_ru", "RU") if key in fields), None)
    if source != record.get("source") or (target or None) != (record.get("target") or None):
        raise ValueError("extracted terminology pair differs from source fields")


def verify_inventory(inventory: dict) -> None:
    datasets = {row["sha256"]: row for row in inventory["datasets"]}
    if len(datasets) != len(inventory["datasets"]):
        raise ValueError("duplicate inventory dataset")
    raw = {}
    for dataset in datasets.values():
        for item in dataset["paths"]:
            path = Path(item["path"])
            data = path.read_bytes()
            if identity(data) != {"bytes": dataset["bytes"], "sha256": dataset["sha256"]}:
                raise ValueError(f"terminology source changed: {path}")
            raw[str(path)] = data.decode("utf-8-sig")
    counts, seen = Counter(), set()
    for row in inventory["records"]:
        ref = row["source_ref"]
        dataset = datasets[row["dataset_sha256"]]
        paths = {str(Path(item["path"])) for item in dataset["paths"]}
        path = str(Path(ref["path"]))
        if path not in paths:
            raise ValueError("record source does not belong to dataset")
        key = (row["dataset_sha256"], ref["row"], ref["index"], ref["line"])
        if key in seen:
            raise ValueError("duplicate record selector")
        seen.add(key); counts[row["dataset_sha256"]] += 1
        text = raw[path]; fmt = dataset["format"]
        if fmt.startswith("csv:"):
            actual = list(csv.DictReader(io.StringIO(text, newline="")))[ref["row"] - 2]
        elif fmt.startswith("json:"):
            actual = json.loads(text)[fmt.split(":", 1)[1]][ref["index"]]
        elif fmt == "markdown:pipe_tables":
            cells = [s.strip() for s in re.split(r"(?<!\\)\|", text.splitlines()[ref["line"] - 1].strip())[1:-1]]
            keys = [k for k in row["original_fields"] if k != "table_section"]
            if len(cells) != len(keys):
                raise ValueError("Markdown terminology column count mismatch")
            actual = {"table_section": row["original_fields"].get("table_section"), **dict(zip(keys, cells))}
        else:
            raise ValueError(f"unsupported terminology format: {fmt}")
        if actual != row["original_fields"]:
            raise ValueError("terminology source record mismatch")
        _verify_extracted_pair(row)
    if any(counts[key] != dataset["record_count"] for key, dataset in datasets.items()):
        raise ValueError("terminology dataset coverage mismatch")


def consolidate(rows: list[dict], records: list[dict], evidence_ref: str) -> tuple[list[dict], dict]:
    result = [dict(row) for row in rows]
    existing = {normalize(row["source_term"]): row for row in result}
    if len(existing) != len(result):
        raise ValueError("duplicate registry source")
    groups, dispositions = defaultdict(list), []
    historical = {"sealed_snapshot", "superseded_local"}
    preferred = {"local_selected", "local_registry", "local_decision"}
    for index, record in enumerate(records):
        if "original_fields" in record:
            _verify_extracted_pair(record)
        source = record.get("source")
        if record["dataset_role"] == "shared_authority":
            action = "existing_authority"
        elif record["dataset_role"] in historical:
            action = "historical_evidence_preserved"
        elif not source:
            action = "source_missing_review"
        elif record.get("composite_source_expression") or "decompose" in record.get("action_hint", "") or ";" in source or "/" in source:
            action = "composite_observation_preserved_for_decomposition"
        else:
            groups[normalize(source)].append((index, record))
            action = "registry_observation"
        dispositions.append({"record_index": index, "source": source, "action": action})
    added, enriched, conflicts = [], [], []
    for key in sorted(groups):
        group = groups[key]
        refs = [index for index, _ in group]
        evidence = f"Сводные свидетельства: {evidence_ref}; records={','.join(map(str, refs))}."
        if key in existing:
            row = existing[key]
            accepted = {normalize(x) for x in [row["accepted_ru"], *row["aliases"].split(";")] if x}
            active = [(i, r) for i, r in group if r["dataset_role"] in preferred and r.get("target")]
            mismatches = [(i, r["target"]) for i, r in active if normalize(r["target"]) not in accepted]
            if row["status"] == "accepted" and mismatches:
                conflicts.append({"source": row["source_term"], "accepted": row["accepted_ru"],
                                  "observed_conflicts": [{"record_index": i, "target": target} for i, target in mismatches]})
                evidence += " Есть конфликт локального варианта; принятое общее правило сохранено, требуется контекстная проверка."
            row["notes"] = (row["notes"].rstrip() + " " + evidence).strip()
            enriched.append(row["source_term"])
            continue
        preferred_rows = [(i, r) for i, r in group if r["dataset_role"] in preferred and r.get("target")]
        candidates = preferred_rows or [(i, r) for i, r in group if r.get("target")]
        targets = {}
        for _, record in candidates:
            if re.search(r"[А-Яа-яЁё]", record["target"]):
                targets.setdefault(normalize(record["target"]), record["target"])
        target = next(iter(targets.values())) if len(targets) == 1 else ""
        primary = (preferred_rows or group)[0][1]
        scopes = sorted({str(record.get("book") or record.get("source_scope") or "scope_pending") for _, record in group})
        definitions = list(dict.fromkeys(str(record["definition_ru"]).strip() for _, record in group if record.get("definition_ru")))
        notes = evidence + " Область: " + "; ".join(scopes) + ". Глобальное применение не утверждено."
        if len(definitions) == 1:
            notes += " Определение: " + definitions[0] + " Источник: записи сводных свидетельств."
        else:
            notes += " Определение требует проверки по источнику."
        if len(targets) > 1:
            notes += " Конфликт вариантов: " + "; ".join(targets.values()) + "."
        if not target:
            notes += " Русский эквивалент не утверждён; исходные варианты сохранены в свидетельствах."
        row = dict(zip(HEADER, [primary["source"], target, "", "", primary.get("domain") or "general",
                               "review_required", "; ".join(scopes), "consolidated_evidence_pending_scope_review", notes]))
        result.append(row); existing[key] = row; added.append(row["source_term"])
    return result, {"records": len(records), "dispositions": dispositions, "added": added,
                    "enriched": enriched, "conflicts": conflicts,
                    "accepted_rules_preserved": [r for r in rows if r["status"] == "accepted"]}


def prepare_merge(registry: Path, inventory_path: Path, output: Path, evidence_ref: str) -> dict:
    if output.exists():
        raise ValueError("merge output must be absent")
    before = registry.read_bytes(); rows = registry_rows(before)
    inventory = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    verify_inventory(inventory)
    if not any(d["role"] == "shared_authority" and d["sha256"] == identity(before)["sha256"] for d in inventory["datasets"]):
        raise ValueError("inventory shared authority is not current registry")
    merged, report = consolidate(rows, inventory["records"], evidence_ref)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
    writer.writeheader(); writer.writerows(merged)
    after = stream.getvalue().encode("utf-8")
    registry_rows(after)
    report.update(schema="kb_creator.coc_terminology_merge.v1", before=identity(before), after=identity(after),
                  inventory=identity(inventory_path.read_bytes()), total_rows=len(merged), evidence_ref=evidence_ref)
    output.mkdir(parents=True)
    (output / "registry-before.csv").write_bytes(before)
    (output / "registry-after.csv").write_bytes(after)
    (output / "inventory.json").write_bytes(inventory_path.read_bytes())
    _write(output / "merge-report.json", report)
    return report


def apply_merge(registry: Path, bundle: Path) -> dict:
    report = json.loads((bundle / "merge-report.json").read_text(encoding="utf-8"))
    before = (bundle / "registry-before.csv").read_bytes()
    after = (bundle / "registry-after.csv").read_bytes()
    inventory = (bundle / "inventory.json").read_bytes()
    if identity(registry.read_bytes()) != report["before"] or identity(before) != report["before"] or identity(after) != report["after"] or identity(inventory) != report["inventory"]:
        raise ValueError("merge preimage or evidence changed")
    old, new = registry_rows(before), registry_rows(after)
    expected, derived_report = consolidate(old, json.loads(inventory.decode("utf-8-sig"))["records"], report["evidence_ref"])
    if new != expected or any(report.get(key) != value for key, value in derived_report.items()):
        raise ValueError("merge result does not derive from the bound inventory")
    old_accepted = [{k: v for k, v in row.items() if k != "notes"} for row in old if row["status"] == "accepted"]
    new_accepted = [{k: v for k, v in row.items() if k != "notes"} for row in new if row["status"] == "accepted"]
    if old_accepted != new_accepted:
        raise ValueError("merge would change accepted replacement rules")
    _replace_registry(registry, before, after)
    return {"state": "merged", "rows": len(new), "added": len(report["added"]),
            "conflicts_retained": len(report["conflicts"]), **identity(after)}


def apply_reviewed_amendments(registry: Path, decisions_path: Path) -> dict:
    """Apply explicit alias/context evidence, never infer a terminology decision."""
    data = registry.read_bytes()
    decisions = json.loads(decisions_path.read_text(encoding="utf-8-sig"))
    if set(decisions) != {"schema", "registry", "amendments"} or decisions["schema"] != "kb_creator.terminology_amendments.v1" or decisions["registry"] != identity(data):
        raise ValueError("terminology amendments preimage mismatch")
    rows = registry_rows(data); by_key = {normalize(row["source_term"]): row for row in rows}; seen = set()
    for change in decisions["amendments"]:
        if set(change) != {"source", "row_sha256", "fields", "reason", "evidence"} or not change["reason"] or not change["evidence"]:
            raise ValueError("terminology amendment evidence required")
        key = normalize(change["source"])
        if key in seen or key not in by_key or digest(by_key[key]) != change["row_sha256"]:
            raise ValueError("duplicate, unknown or stale terminology amendment")
        if not change["fields"] or not set(change["fields"]) <= {"aliases", "notes"}:
            raise ValueError("only reviewed alias/context amendments supported")
        if any(not isinstance(value, str) for value in change["fields"].values()):
            raise ValueError("terminology amendment must contain strings")
        seen.add(key); by_key[key].update(change["fields"]); usage_rule(by_key[key]["notes"])
    stream = io.StringIO(newline=""); writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
    writer.writeheader(); writer.writerows(rows); result = stream.getvalue().encode("utf-8")
    registry_rows(result)
    _replace_registry(registry, data, result)
    return {"state": "amended", "entries": len(seen), "before": identity(data), "after": identity(result)}
