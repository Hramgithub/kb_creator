import json
import re
from pathlib import Path


CONTRACTS = Path(__file__).resolve().parents[1] / "contracts"
MANDATORY_PACKAGE_ROLES = {
    "master_en", "master_en_acceptance", "master_ru", "master_ru_acceptance",
    "artview_bundle", "artview_candidate_manifest", "artview_decisions",
    "artview_application", "artview_effective_config", "artview_acceptance",
    "html", "html_acceptance", "docx", "docx_acceptance", "pdf",
    "pdf_acceptance", "source_configs", "effective_config", "stage_evidence",
    "pipeline_snapshot", "schema_snapshot", "offline_verifier",
}


def _closed_const_object_accepts(definition, value):
    if not isinstance(value, dict):
        return False
    properties = definition["properties"]
    if definition.get("additionalProperties") is False and not set(value) <= set(properties):
        return False
    if not set(definition.get("required", ())) <= set(value):
        return False
    return all("const" not in properties[key] or value[key] == properties[key]["const"] for key in value if key in properties)


def _closed_enum_array_accepts(definition, value):
    if not isinstance(value, list) or len(value) < definition.get("minItems", 0) or len(value) > definition.get("maxItems", len(value)):
        return False
    serialized = [json.dumps(item, sort_keys=True) for item in value]
    if definition.get("uniqueItems") and len(serialized) != len(set(serialized)):
        return False
    allowed = definition.get("items", {}).get("enum")
    return allowed is None or all(item in allowed for item in value)


def _tool_record_matches(schema, definition_name, value):
    base = schema["$defs"]["tool_record"]
    if not _closed_const_object_accepts(base, value):
        return False
    properties = schema["$defs"][definition_name]["allOf"][1]["properties"]
    for key, rule in properties.items():
        if "const" in rule and value[key] != rule["const"]:
            return False
        if "pattern" in rule and re.fullmatch(rule["pattern"], value[key]) is None:
            return False
    return True


def _tools_shape_accepts(schema, value):
    if len(value) == 1:
        return _tool_record_matches(schema, "injected_tool", value[0])
    word = ("publication_python_tool", "pdftoppm_tool", "powershell_tool", "word_tool")
    libreoffice = ("publication_python_tool", "pdftoppm_tool", "libreoffice_tool")
    for production in (word, libreoffice):
        if len(value) == len(production) and all(sum(_tool_record_matches(schema, name, record) for name in production) == 1 for record in value) and all(sum(_tool_record_matches(schema, name, record) for record in value) == 1 for name in production):
            return True
    return False


def test_publication_schemas_are_additive_closed_and_parseable():
    names = (
        "scenario_publication_contract.v1.schema.json",
        "publication_run_spec.v1.schema.json",
        "publication_stage_manifest.v1.schema.json",
        "artifact_acceptance.v1.schema.json",
        "master_ru_submission.v1.schema.json",
        "production_package_manifest.v1.schema.json",
    )
    for name in names:
        schema = json.loads((CONTRACTS / name).read_text(encoding="utf-8"))
        assert schema["$schema"].endswith("2020-12/schema")
        assert schema["additionalProperties"] is False
    publication = json.loads((CONTRACTS / names[0]).read_text(encoding="utf-8"))
    for definition in publication["properties"]["artifact_names"]["properties"].values():
        re.compile(definition["pattern"])
    legacy = json.loads(
        (CONTRACTS / "scenario_contract.v1.schema.json").read_text(encoding="utf-8")
    )
    assert legacy["$id"] != "kb_creator.scenario_publication_contract.v1"


def test_pdf_contract_has_one_closed_docx_only_adapter_shape():
    schema = json.loads(
        (CONTRACTS / "scenario_publication_contract.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    pdf = schema["properties"]["pdf"]
    assert pdf["additionalProperties"] is False
    assert pdf["properties"]["adapter"] == {
        "const": "docx_pdf_export_v1"
    }
    policy = pdf["properties"]["export_policy"]
    assert policy["additionalProperties"] is False
    assert policy["properties"]["document_input_role"] == {
        "const": "accepted_docx"
    }
    serialized = json.dumps(pdf).lower()
    for forbidden in ("source_html", "engine_command", "print-to-pdf", "chromium"):
        assert forbidden not in serialized


def test_stage_and_acceptance_enums_do_not_infer_release():
    stage = json.loads(
        (CONTRACTS / "publication_stage_manifest.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert stage["properties"]["reproducible"]["properties"]["state"] == {
        "const": "succeeded"
    }
    acceptance = json.loads(
        (CONTRACTS / "artifact_acceptance.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert acceptance["properties"]["decision"] == {"const": "accepted"}
    package = json.loads(
        (CONTRACTS / "production_package_manifest.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert package["properties"]["release_state"] == {"const": "not_reviewed"}
    assert package["properties"]["stage_manifests"]["minItems"] == 8
    assert package["properties"]["stage_manifests"]["maxItems"] == 8
    assert package["properties"]["stage_manifests"]["uniqueItems"] is True
    acceptances = package["properties"]["acceptance_receipts"]
    assert acceptances["minItems"] == acceptances["maxItems"] == 6
    assert acceptances["uniqueItems"] is True
    roles = package["properties"]["roles"]
    assert roles["minItems"] == roles["maxItems"] == 22
    assert roles["uniqueItems"] is True
    assert package["properties"]["config_inventory"]["uniqueItems"] is True
    assert package["properties"]["pipeline_snapshot"]["uniqueItems"] is True


def test_html_and_docx_schema_profiles_are_closed_and_adapter_specific():
    schema = json.loads((CONTRACTS / "scenario_publication_contract.v1.schema.json").read_text(encoding="utf-8"))
    file_record = {"path": "config.json", "bytes": 1, "sha256": "A" * 64}
    for role, definition_name, adapter in (
        ("html", "html_render_profile", "translator_build_production_html_v1"),
        ("docx", "docx_render_profile", "production_docx_explicit_config_v1"),
    ):
        assert schema["properties"][role] == {"$ref": f"#/$defs/{definition_name}"}
        definition = schema["$defs"][definition_name]
        assert definition["additionalProperties"] is False
        assert definition["properties"]["adapter"] == {"const": adapter}
        valid = {"adapter": adapter, "config": file_record, "required_qa": ["pass"]}
        assert _closed_const_object_accepts(definition, valid)
        assert not _closed_const_object_accepts(definition, {**valid, "unknown": True})
        assert not _closed_const_object_accepts(definition, {key: value for key, value in valid.items() if key != "config"})
        assert not _closed_const_object_accepts(definition, {**valid, "adapter": "wrong_adapter"})


def test_package_required_roles_schema_is_the_exact_unique_runtime_set():
    schema = json.loads((CONTRACTS / "scenario_publication_contract.v1.schema.json").read_text(encoding="utf-8"))
    definition = schema["properties"]["package"]["properties"]["required_roles"]
    assert definition["minItems"] == definition["maxItems"] == len(MANDATORY_PACKAGE_ROLES) == 22
    assert definition["uniqueItems"] is True
    assert set(definition["items"]["enum"]) == MANDATORY_PACKAGE_ROLES
    valid = sorted(MANDATORY_PACKAGE_ROLES)
    assert _closed_enum_array_accepts(definition, valid)
    assert not _closed_enum_array_accepts(definition, valid[:-1])
    assert not _closed_enum_array_accepts(definition, [*valid, "extra_role"])
    assert not _closed_enum_array_accepts(definition, [*valid[:-1], valid[0]])
    assert not _closed_enum_array_accepts(definition, [*valid[:-1], "unknown_role"])


def test_stage_tool_schema_accepts_only_closed_injected_or_exact_production_shapes():
    schema = json.loads((CONTRACTS / "publication_stage_manifest.v1.schema.json").read_text(encoding="utf-8"))
    tools = schema["properties"]["reproducible"]["properties"]["tools"]
    assert len(tools["oneOf"]) == 3
    base = schema["$defs"]["tool_record"]
    assert base["additionalProperties"] is False
    assert set(base["required"]) == {"name", "version", "scope"}
    assert set(base["properties"]["scope"]["enum"]) == {"injected_test", "repository_tools", "allowed_system"}
    injected = [{"name": "injected_publication_adapters", "version": "test", "scope": "injected_test"}]
    production = [
        {"name": "publication_python", "version": "sha256:" + "A" * 64, "scope": "repository_tools"},
        {"name": "pdftoppm", "version": "sha256:" + "B" * 64, "scope": "repository_tools"},
        {"name": "powershell", "version": "sha256:" + "C" * 64, "scope": "allowed_system"},
        {"name": "microsoft_word_com", "version": "sha256:" + "D" * 64, "scope": "allowed_system"},
    ]
    assert _tools_shape_accepts(schema, injected)
    assert _tools_shape_accepts(schema, production)
    local_production = [
        production[0], production[1],
        {"name": "libreoffice", "version": "sha256:" + "E" * 64, "scope": "repository_tools"},
    ]
    assert _tools_shape_accepts(schema, local_production)
    assert not _tools_shape_accepts(schema, [{**injected[0], "unknown": True}])
    assert not _tools_shape_accepts(schema, [{"name": injected[0]["name"], "version": "test"}])
    assert not _tools_shape_accepts(schema, [{**injected[0], "scope": "repository_tools"}])
    assert not _tools_shape_accepts(schema, [injected[0], *production])
    assert not _tools_shape_accepts(schema, [production[0], production[0], production[2], production[3]])
    assert not _tools_shape_accepts(schema, [{**production[0], "scope": "injected_test"}, *production[1:]])
