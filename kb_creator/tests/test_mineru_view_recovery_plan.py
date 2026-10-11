import json
from pathlib import Path
import pytest
from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline import mineru_view_recovery_plan as plans
from kb_creator.tests.test_mineru_cpu_packet_b import _full_fixture, _run_adapters
from kb_creator.pipeline import reconstruction
from kb_creator.pipeline import five_step
from kb_creator.pipeline import mineru_cpu_first
from kb_creator.pipeline import process as pipeline_process
from kb_creator.tests import test_mineru_cpu_packet_b as fixtures

def _plan(source, origin):
    stage=origin/"outputs/02-mineru-three-view"; receipt=stage/"views/original_pipeline_txt/view.json"
    data=json.loads(receipt.read_text())
    value={"schema":plans.SCHEMA,"origin_run_root":str(origin),"origin_run":{"path":"run.json",**file_identity(origin/"run.json")},"origin_stage_root":str(stage),"source":file_identity(source),"views":["original_pipeline_txt"],"origin_receipts":{"original_pipeline_txt":{"path":"views/original_pipeline_txt/view.json",**file_identity(receipt),"receipt_sha256":data["receipt_sha256"]}},"wrapper_compatibility":{}}
    value["plan_sha256"]=sha256_bytes(canonical_bytes(value)); return value

def test_sealed_plan_loads_origin_run_and_rejects_source_or_seal(tmp_path):
    source, contract, runtime, _, _, origin = _full_fixture(tmp_path)
    reconstruction.run_engine(contract, source, origin, "origin", _run_adapters(origin), runtime)
    path=tmp_path/"plan.json"; value=_plan(source,origin); path.write_text(json.dumps(value))
    loaded=plans.load_plan(path,source)
    assert loaded["origin_run"]["portable_identity_sha256"]
    value["source"]["sha256"]="0"*64; path.write_text(json.dumps(value))
    with pytest.raises(plans.RecoveryPlanError): plans.load_plan(path,source)

def test_stage02_import_skips_txt_and_invokes_remaining_required_views_once(tmp_path, monkeypatch):
    source, contract, runtime, _, _, origin = _full_fixture(tmp_path)
    reconstruction.run_engine(contract, source, origin, "origin", _run_adapters(origin), runtime)
    fresh_root=tmp_path/"fresh"; fresh=reconstruction.write_run(contract,source,fresh_root,"fresh",runtime)
    # Stage01 is required only to derive the raster input identity.
    prep=_run_adapters(fresh_root)["prepare_inputs"]; prep.invoke(fresh_root/"outputs/01-prepare-inputs")
    plan=_plan(source,origin); plan["origin_run"]=json.loads((origin/"run.json").read_text())
    invoked=[]
    def fake_run(argv, **_kwargs):
        invoked.append(argv[argv.index("-Profile")+1])
        output=Path(argv[argv.index("-OutputPath")+1]); fixtures._write_view_artifacts(output)
        return {"argv":argv,"exit_code":0}
    monkeypatch.setattr(reconstruction.pipeline_process,"run",fake_run)
    adapters=reconstruction.production_cpu_first_run_adapters(fresh,contract,source,recovery_plan=plan)
    result=adapters["mineru_three_view"].invoke(fresh_root/"outputs/02-mineru-three-view")
    assert result["imported_views"]==["original_pipeline_txt"]
    assert invoked==["pipeline_ocr","pipeline_ocr"]
    assert mineru_cpu_first.validate_view_set(fresh,fresh_root/"outputs/02-mineru-three-view")["succeeded_views"][:3]==list(mineru_cpu_first.REQUIRED_VIEWS)

@pytest.mark.parametrize("mutation",("source","receipt","plan"))
def test_invalid_recovery_input_rejects_before_provider(tmp_path, monkeypatch, mutation):
    source, contract, runtime, _, _, origin = _full_fixture(tmp_path)
    reconstruction.run_engine(contract, source, origin, "origin", _run_adapters(origin), runtime)
    value=_plan(source,origin); path=tmp_path/"plan.json"
    if mutation=="source": value["source"]["sha256"]="0"*64
    if mutation=="plan": value["plan_sha256"]="0"*64
    if mutation=="receipt": (origin/"outputs/02-mineru-three-view/views/original_pipeline_txt/view.json").write_text("{}")
    path.write_text(json.dumps(value))
    called=[]; monkeypatch.setattr(reconstruction.pipeline_process,"run",lambda *a,**k: called.append(a))
    with pytest.raises(plans.RecoveryPlanError): plans.load_plan(path,source)
    assert called==[]

def test_root_state_preserves_plan_rechecks_hash_and_excludes_replay(tmp_path):
    source, contract, runtime, _, _, origin = _full_fixture(tmp_path)
    reconstruction.run_engine(contract, source, origin, "origin", _run_adapters(origin), runtime)
    plan_path=tmp_path/"plan.json"; plan_path.write_text(json.dumps(_plan(source,origin)))
    glossary=tmp_path/"terms.json"; glossary.write_text("[]")
    root=tmp_path/"root"
    started=five_step.start(source,glossary,root,recovery_plan=plan_path)
    assert started["phase"]=="intake"
    state=five_step._load(root)
    assert state["recovery_plan"]["identity"]==file_identity(plan_path)
    state.update(phase="reconstruct",state="running"); state["paths"]["contract"]=str(contract); five_step._save(root,state)
    plan_path.write_text("{}")
    result=five_step.resume(root)
    assert result["state"]=="failed" and "recovery plan changed" in result["reason"]
    with pytest.raises(five_step.FiveStepError,match="mutually exclusive"):
        five_step.start(source,glossary,tmp_path/"other",replay_from=origin,recovery_plan=plan_path)


def test_v2_fresh_target_must_match_the_run_created_before_stage02(tmp_path):
    source, contract, runtime, _, _, origin = _full_fixture(tmp_path)
    reconstruction.run_engine(contract, source, origin, "origin", _run_adapters(origin), runtime)
    fresh_root = tmp_path / "fresh"
    fresh = reconstruction.build_run_spec(contract, source, fresh_root, "fresh", runtime)
    value = _plan(source, origin)
    value.update(schema=plans.SOURCE_PROFILE_PLAN_SCHEMA, fresh_target=plans.fresh_target(fresh), source_profile_compatibility={"original_pipeline_txt": {"sealed": "fixture"}})
    value["plan_sha256"] = sha256_bytes(canonical_bytes({key: item for key, item in value.items() if key != "plan_sha256"}))
    path = tmp_path / "v2-plan.json"; path.write_text(json.dumps(value), encoding="utf-8")
    loaded = plans.load_plan(path, source, fresh)
    assert loaded["fresh_target"] == plans.fresh_target(fresh)
    changed = dict(fresh); changed["options"] = {**fresh["options"], "ocr_language": "ru"}
    with pytest.raises(plans.RecoveryPlanError, match="fresh target"):
        plans.validate_fresh_target(loaded, changed)
