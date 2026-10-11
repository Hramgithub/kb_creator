from dataclasses import replace
import hashlib
import json

import pytest

from kb_creator.pdf_raw import page_proof
from kb_creator.pdf_raw.errors import RawPdfError


_COVERAGE_ERROR = "page_proof_stage_a_fixture_coverage_incomplete"
_REGISTRY_ERROR = "page_proof_fixture_registry_invalid"
_ENTRY_FIELDS = (
    "topology_id",
    "stage_a_fixture_id",
    "stage_a_authority_schema",
    "stage_a_authority_content_sha256",
    "stage_a_authority_inventory_sha256",
    "stage_a_fixture_binding_sha256",
    "positive_topology_assertion_sha256",
    "independent_stage_a_review_kind",
    "independent_stage_a_review_decision",
    "independent_stage_a_review_content_sha256",
    "reviewed_authority_content_sha256",
    "entry_sha256",
)


class _Poison:
    def __getattribute__(self, name):
        raise AssertionError(f"caller argument accessed: {name}")

    def __bytes__(self):
        raise AssertionError("caller argument decoded")

    def __iter__(self):
        raise AssertionError("caller argument iterated")


def _entry(**values):
    draft = page_proof._RequiredStageATopologyEntry(entry_sha256="0" * 64, **values)
    return replace(draft, entry_sha256=page_proof._entry_sha256(draft))


def _private_valid_inventory():
    rows = (
        _entry(
            topology_id="stage_a_positive_two_column.v1",
            stage_a_fixture_id="stage-a.positive-two-column.v1",
            stage_a_authority_schema="kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
            stage_a_authority_content_sha256="890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
            stage_a_authority_inventory_sha256="3173d033fcf6228687388f020f0e5e6e7e9c1ce2a373bc1b2bca49823ab951c0",
            stage_a_fixture_binding_sha256="c41ec7ae9eea7d5fc2f654eb825bf1bb1af954d00c754fd6140f134985af8880",
            positive_topology_assertion_sha256="e681b6ffbed2705283b915039e1d7a6ac145f4988765fd772a68eb63803831c8",
            independent_stage_a_review_kind="fixture_topology_acceptance",
            independent_stage_a_review_decision="accept",
            independent_stage_a_review_content_sha256="1" * 64,
            reviewed_authority_content_sha256="890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
        ),
        _entry(
            topology_id="stage_a_positive_nested_form.v1",
            stage_a_fixture_id="stage-a.positive-nested-form.v1",
            stage_a_authority_schema="kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
            stage_a_authority_content_sha256="8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
            stage_a_authority_inventory_sha256="f296a28a72e509f47fe294217492cc463375c30144f8deab57fd7b4c85678b21",
            stage_a_fixture_binding_sha256="9b0f9f382e7926e3447072fa9340c38dd93531302e4294a14d8436eeacdf1d0a",
            positive_topology_assertion_sha256="a82adc738fd89394e80a607df46f7775a1967f874267f3b0289e7e64829d3d0f",
            independent_stage_a_review_kind="fixture_topology_acceptance",
            independent_stage_a_review_decision="accept",
            independent_stage_a_review_content_sha256="2" * 64,
            reviewed_authority_content_sha256="8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
        ),
    )
    draft = page_proof._RequiredStageATopologyInventory(
        schema="PageProofRequiredStageATopologyInventory.v1",
        required_topology_ids=("stage_a_positive_two_column.v1", "stage_a_positive_nested_form.v1"),
        entries=rows,
        entry_count=2,
        inventory_sha256="0" * 64,
        content_sha256="0" * 64,
    )
    sealed = replace(draft, inventory_sha256=page_proof._inventory_sha256(draft.required_topology_ids, rows))
    sealed = replace(sealed, content_sha256=page_proof._inventory_content_sha256(sealed))
    return sealed, page_proof._inventory_primitives(sealed)


def _reseal_with_rows(inventory, rows):
    draft = replace(inventory, entries=rows, entry_count=len(rows), inventory_sha256="0" * 64, content_sha256="0" * 64)
    sealed = replace(draft, inventory_sha256=page_proof._inventory_sha256(draft.required_topology_ids, rows))
    return replace(sealed, content_sha256=page_proof._inventory_content_sha256(sealed))


def _mutated_value(field, value):
    if field == "topology_id":
        return "stage_a_unknown.v1"
    if field == "stage_a_authority_schema":
        return "kb_creator.pdf_raw.NotAuthority.v1"
    if field == "independent_stage_a_review_kind":
        return "implementation"
    if field == "independent_stage_a_review_decision":
        return "reject"
    if field == "entry_sha256":
        return "f" * 64
    return "f" * 64 if value != "f" * 64 else "e" * 64


def _all_operations():
    poison = _Poison()
    return (
        (page_proof.derive_fixture_page_block_ledger_v1, (poison, poison, poison, poison)),
        (page_proof.review_fixture_page_block_ledger_v1, (poison, poison, poison)),
        (page_proof.replay_fixture_page_block_ledger_v1, (poison, poison, poison, poison, poison, poison)),
    )


def _assert_public_gate(monkeypatch, inventory, expected, code):
    monkeypatch.setattr(page_proof, "_PRODUCTION_REQUIRED_STAGE_A_TOPOLOGY_INVENTORY", inventory)
    monkeypatch.setattr(page_proof, "_PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES", expected)
    for operation, arguments in _all_operations():
        result = object()
        sentinel = result
        with pytest.raises(RawPdfError, match=f"^{code}$") as info:
            result = operation(*arguments)
        assert type(info.value) is RawPdfError
        assert info.value.code == code
        assert result is sentinel


def test_production_empty_root_seals_recompute_independently_and_preserve_coverage_error(monkeypatch):
    inventory = page_proof._PRODUCTION_REQUIRED_STAGE_A_TOPOLOGY_INVENTORY
    assert inventory.required_topology_ids == (
        "stage_a_positive_two_column.v1", "stage_a_positive_nested_form.v1",
    )
    assert inventory.entries == () and inventory.entry_count == 0
    canonical = lambda value: json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    independently_recomputed_inventory = hashlib.sha256(
        b"page-proof.required-stage-a-topology-inventory.v1\0" + canonical({
            "required_topology_ids": inventory.required_topology_ids,
            "entry_count": 0,
            "ordered_entry_sha256": [],
        })
    ).hexdigest()
    independently_recomputed_content = hashlib.sha256(canonical({
        "schema": "PageProofRequiredStageATopologyInventory.v1",
        "required_topology_ids": inventory.required_topology_ids,
        "entries": [],
        "entry_count": 0,
        "inventory_sha256": independently_recomputed_inventory,
    })).hexdigest()
    assert inventory.inventory_sha256 == independently_recomputed_inventory
    assert inventory.content_sha256 == independently_recomputed_content
    assert page_proof._inventory_is_complete(inventory, page_proof._PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES) is None
    _assert_public_gate(monkeypatch, inventory, page_proof._PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES, _COVERAGE_ERROR)


def test_private_complete_inventory_reaches_only_fixture_registry_gate(monkeypatch):
    inventory, expected = _private_valid_inventory()
    assert page_proof._inventory_is_complete(inventory, expected) == inventory.content_sha256
    _assert_public_gate(monkeypatch, inventory, expected, _REGISTRY_ERROR)


@pytest.mark.parametrize("field", _ENTRY_FIELDS)
def test_each_target_entry_mutation_fails_coverage_and_target_repair_reaches_next_gate(monkeypatch, field):
    inventory, expected = _private_valid_inventory()
    original = inventory.entries[0]
    changed = replace(original, **{field: _mutated_value(field, getattr(original, field))})
    if field != "entry_sha256":
        changed = replace(changed, entry_sha256=page_proof._entry_sha256(changed))
    broken = _reseal_with_rows(inventory, (changed, inventory.entries[1]))
    assert page_proof._inventory_is_complete(broken, expected) is None
    _assert_public_gate(monkeypatch, broken, expected, _COVERAGE_ERROR)
    assert page_proof._inventory_is_complete(inventory, expected) == inventory.content_sha256


@pytest.mark.parametrize("mutator", (
    lambda inventory: _reseal_with_rows(inventory, tuple(reversed(inventory.entries))),
    lambda inventory: replace(inventory, entry_count=1),
    lambda inventory: replace(inventory, inventory_sha256="f" * 64),
    lambda inventory: replace(inventory, content_sha256="f" * 64),
    lambda inventory: replace(inventory, required_topology_ids=tuple(reversed(inventory.required_topology_ids))),
    lambda inventory: _reseal_with_rows(inventory, (inventory.entries[1], inventory.entries[1])),
))
def test_order_count_hash_and_cross_pair_mutations_fail_coverage(monkeypatch, mutator):
    inventory, expected = _private_valid_inventory()
    broken = mutator(inventory)
    assert page_proof._inventory_is_complete(broken, expected) is None
    _assert_public_gate(monkeypatch, broken, expected, _COVERAGE_ERROR)
    assert page_proof._inventory_is_complete(inventory, expected) == inventory.content_sha256


def test_independent_expected_tuple_cannot_be_mutated_to_bypass_validation(monkeypatch):
    inventory, expected = _private_valid_inventory()
    changed_expected = expected[:-1] + ("f" * 64,)
    assert page_proof._inventory_is_complete(inventory, changed_expected) is None
    _assert_public_gate(monkeypatch, inventory, changed_expected, _COVERAGE_ERROR)
