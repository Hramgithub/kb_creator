import ast
import inspect

import pytest

from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.pdf_raw.page_proof import (
    derive_fixture_page_block_ledger_v1,
    replay_fixture_page_block_ledger_v1,
    review_fixture_page_block_ledger_v1,
)


_COVERAGE_ERROR = "page_proof_stage_a_fixture_coverage_incomplete"


class _Poison:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"argument accessed: {name}")

    def __bytes__(self) -> bytes:
        raise AssertionError("argument decoded")

    def __iter__(self) -> object:
        raise AssertionError("argument iterated")


@pytest.mark.parametrize("payload", (b"", b"{}", b"\x00\xfffixture-only"))
def test_derive_stops_before_authority_or_byte_input_access(payload: bytes) -> None:
    sentinel = object()
    result = sentinel
    with pytest.raises(RawPdfError, match=f"^{_COVERAGE_ERROR}$") as info:
        result = derive_fixture_page_block_ledger_v1(_Poison(), payload, payload, payload)
    assert info.value.code == _COVERAGE_ERROR
    assert type(info.value) is RawPdfError
    assert result is sentinel


@pytest.mark.parametrize("payload", (b"", b"{}", b"\x00\xfffixture-only"))
def test_review_stops_before_candidate_or_review_input_access(payload: bytes) -> None:
    sentinel = object()
    result = sentinel
    with pytest.raises(RawPdfError, match=f"^{_COVERAGE_ERROR}$") as info:
        result = review_fixture_page_block_ledger_v1(payload, payload, payload)
    assert info.value.code == _COVERAGE_ERROR
    assert type(info.value) is RawPdfError
    assert result is sentinel


@pytest.mark.parametrize("payload", (b"", b"{}", b"\x00\xfffixture-only"))
def test_replay_stops_before_authority_or_all_byte_input_access(payload: bytes) -> None:
    sentinel = object()
    result = sentinel
    with pytest.raises(RawPdfError, match=f"^{_COVERAGE_ERROR}$") as info:
        result = replay_fixture_page_block_ledger_v1(_Poison(), payload, payload, payload, payload, payload)
    assert info.value.code == _COVERAGE_ERROR
    assert type(info.value) is RawPdfError
    assert result is sentinel


@pytest.mark.parametrize(
    ("operation", "arguments"),
    (
        (derive_fixture_page_block_ledger_v1, (_Poison(), _Poison(), _Poison(), _Poison())),
        (review_fixture_page_block_ledger_v1, (_Poison(), _Poison(), _Poison())),
        (replay_fixture_page_block_ledger_v1, (_Poison(), _Poison(), _Poison(), _Poison(), _Poison(), _Poison())),
    ),
)
def test_each_public_operation_rejects_opaque_arguments_without_touching_them(operation, arguments) -> None:
    with pytest.raises(RawPdfError, match=f"^{_COVERAGE_ERROR}$") as info:
        operation(*arguments)
    assert info.value.code == _COVERAGE_ERROR


def test_public_signatures_include_independent_visual_crosscheck_leaf() -> None:
    assert tuple(inspect.signature(derive_fixture_page_block_ledger_v1).parameters) == (
        "validated_stage_a_authority", "witness_raw", "render_png_raw", "independent_visual_crosscheck_raw",
    )
    assert tuple(inspect.signature(review_fixture_page_block_ledger_v1).parameters) == (
        "candidate_raw", "independent_visual_crosscheck_raw", "review_raw",
    )
    assert tuple(inspect.signature(replay_fixture_page_block_ledger_v1).parameters) == (
        "validated_stage_a_authority", "witness_raw", "render_png_raw", "independent_visual_crosscheck_raw",
        "review_raw", "expected_ledger_raw",
    )


def test_module_import_and_call_containment() -> None:
    import kb_creator.pdf_raw.page_proof as page_proof

    tree = ast.parse(inspect.getsource(page_proof))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert [alias.name for alias in node.names] in (["hashlib"], ["json"], ["re"])
        if isinstance(node, ast.ImportFrom):
            if node.level == 1:
                assert (node.module, [alias.name for alias in node.names]) in (
                    ("errors", ["RawPdfError"]),
                    ("raw_authority_projection", ["RawAtomProvenanceAuthorityV1"]),
                )
            else:
                assert node.module == "dataclasses"
                assert [alias.name for alias in node.names] == ["dataclass"]
        if isinstance(node, ast.Call):
            assert not isinstance(node.func, ast.Name) or node.func.id not in {
                "open", "__import__", "eval", "exec", "compile",
            }
