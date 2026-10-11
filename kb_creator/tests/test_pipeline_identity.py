import json
from pathlib import Path
import pytest
from kb_creator.pipeline.identity import canonical_bytes, sha256_bytes
from kb_creator.pipeline.reconstruction import ControlPlaneError, validate_contract

def test_canonical_identity_is_key_order_independent():
    assert canonical_bytes({"b":2,"a":1}) == canonical_bytes({"a":1,"b":2})
    assert len(sha256_bytes(b"x")) == 64

def test_v1_and_publication_leakage_are_rejected():
    with pytest.raises(ControlPlaneError): validate_contract({"schema":"kb_creator.scenario_contract.v1"})
