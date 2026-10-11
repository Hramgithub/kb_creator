from pathlib import Path
import pytest
from kb_creator import __main__
from kb_creator.pipeline import five_step, five_step_intake as intake
from kb_creator.pipeline import reconstruction_replay as replay

def test_cli_exposes_archived_replay_flag():
    args=__main__._parser().parse_args(["translate","run","--source","a.pdf","--glossary","g.json","--run-root","r","--replay-from","old","--archived-replay"])
    assert args.archived_replay is True and args.replay_from==Path("old")

def test_root_rejects_archived_combinations_before_root_allocation(tmp_path):
    source=tmp_path/"s.pdf"; source.write_bytes(b"pdf"); glossary=tmp_path/"g.json"; glossary.write_text("[]")
    with pytest.raises(five_step.FiveStepError,match="requires"):
        five_step.start(source,glossary,tmp_path/"a",archived_replay=True)
    with pytest.raises(five_step.FiveStepError,match="mutually exclusive"):
        five_step.start(source,glossary,tmp_path/"b",replay_from=tmp_path,recovery_plan=glossary,archived_replay=True)
    assert not (tmp_path/"a").exists() and not (tmp_path/"b").exists()

def test_intake_routes_archived_only_to_engine(monkeypatch,tmp_path):
    calls=[]
    monkeypatch.setattr(replay,"replay_archived_run_engine",lambda *args: calls.append(args) or {"state":"not_ready"})
    monkeypatch.setattr(replay,"verify_archived_replay_source",lambda *args: (_ for _ in ()).throw(AssertionError("duplicate source preflight")))
    monkeypatch.setattr(replay,"verify_archived_replay_transform",lambda *args: (_ for _ in ()).throw(AssertionError("duplicate transform preflight")))
    result=intake.start_reconstruction(tmp_path/"c",tmp_path/"s",tmp_path/"new","new",object(),replay_from=tmp_path,archived_replay=True)
    assert result["state"]=="not_ready" and len(calls)==1
