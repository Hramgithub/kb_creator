"""Exercise the recovery route through real stage and replay validators."""
from pathlib import Path
import json
import os
import shutil
from dataclasses import replace

import pytest
from PIL import Image

from kb_creator.pipeline import reconstruction, reconstruction_replay as replay
from kb_creator.pipeline.identity import deterministic_inventory, file_identity, sha256_bytes
from kb_creator.tests.test_mineru_cpu_packet_b import _full_fixture, _run_adapters
from kb_creator.tests import test_mineru_cpu_packet_b as fixtures
from kb_creator.pipeline import reconstruction_promotion as promotion
from kb_creator.pipeline import five_step_intake as intake
from kb_creator.pipeline import reconstruction_replay_resume as resume
from kb_creator.scripts import build_mineru_visual_merge_bundle as bundle
from kb_creator.scripts import author_reviewed_semantic_decisions as author
from kb_creator.pipeline import semantic_structure as semantic


def _resume_semantic_fixture_and_promote(root, tmp_path):
    """Continue a real hybrid authority through v4 fidelity and portable output."""
    authority = replay.validate_replay_authorities(root)
    queue = resume.validate_replay_review_queue(authority).queue
    decisions = tmp_path / 'semantic-decisions'
    decision_set_path, decision_set = fixtures._write_complete_v2_audit_submission(root, decisions)
    view = 'original_pipeline_txt'
    for record in decision_set['decisions']:
        path = decisions / record['path']
        decision = json.loads(path.read_text())
        page = decision['source_page']
        packet = json.loads((authority.merge_packets / f'pages/page-{page:03d}.json').read_text())
        index = decision['selected_blocks'][0]['raw_index']
        visual_path = f'outputs/04-visual-merge-bundle/visual/{view}/pages/page-{page:03d}.png'
        unit = {'id': f'page-{page:03d}-text', 'kind': 'label', 'representation': 'semantic_span',
                'source_blocks': [{'view': view, 'raw_index': index}],
                'source_fragments': author._source_fragments(packet, {'raw_indices': [index]}, view, page, set()),
                'markdown_span': {'start_line': 1, 'end_line': 1, 'sha256': sha256_bytes(decision['markdown'].encode())},
                'container_parent': None, 'semantic_parent': None, 'continuation_of': None,
                'heading_level': None, 'item_count': None}
        if page == 1:
            asset = next(block for block in packet['views'][view]['blocks'] if block['type'] == 'image')
            decision['selected_blocks'].append({'view': view, 'raw_index': asset['raw_index'], 'purpose': 'asset'})
            decision['assets'] = [{'placement': 'inline', 'source_path': 'images/map.png',
                                   'view': view, 'logical_name': 'fixture-map'}]
            decision['markdown'] += '\n\n![Source visual]({{asset:fixture-map}})'
        decision['semantic_structure'] = {'schema': semantic.SCHEMA_V2, 'profile': semantic.PROFILE_V2,
            'role_contract': {'group_id': f'group-{page}', 'role': packet['semantic_role']},
            'review': {'state': 'complete', 'visual': {'path': visual_path, **file_identity(root / visual_path)}},
            'units': [unit]}
        fixtures._write_json(path, decision)
        record.update(file_identity(path))
    comparison = json.loads(authority.comparison.read_text())
    visual = json.loads(authority.visual_manifest.read_text())
    geometry = json.loads(authority.geometry_plan.read_text())
    run = json.loads((root / 'run.json').read_text())
    allowlist = {'schema': resume.ALLOWLIST_SCHEMA, 'authority': {
        'run_identity_sha256': run['portable_identity_sha256'], 'bridge_sha256': authority.bridge_sha256,
        'review_queue_sha256': queue['queue_sha256'], 'comparison_sha256': comparison['comparison_sha256'],
        'geometry_plan_sha256': geometry['plan_sha256'], 'visual_manifest_sha256': visual['manifest_sha256']},
        'substitutions': [], 'source_text_exclusions': [], 'visual_text_assertions': [], 'ocr_equivalence_classes': []}
    fixtures._write_json(decisions / 'allowlist.json', allowlist)
    decision_set.update(schema='kb_creator.reconstruction_decision_set.v2',
        semantic_structure_profile=semantic.PROFILE_V2,
        reviewed_allowlist={'path': 'allowlist.json', **file_identity(decisions / 'allowlist.json')})
    fixtures._write_json(decision_set_path, decision_set)
    result = resume.replay_resume_engine(root, decision_set_path, decisions)
    assert result['state'] == 'candidate_ready_for_reconstruction_qa'
    audit = json.loads((root / 'outputs/05-fidelity-audit/audit.json').read_text())
    assert audit['schema'] == 'kb_creator.ai-merge-fidelity-audit/v4'
    assert audit['passed'] and not audit['errors']
    assert (root / 'outputs/06-materialize-candidate/SEMANTIC_STRUCTURE.json').is_file()
    source_asset = root / 'outputs/02-mineru-three-view/views/original_pipeline_txt/artifacts/images/map.png'
    asset_identity = file_identity(source_asset)
    materialized_assets = list((root / 'outputs/06-materialize-candidate/assets').glob('*.png'))
    assert len(materialized_assets) == 1
    assert file_identity(materialized_assets[0]) == asset_identity
    promoted = promotion.materialize_reconstruction_promotion(root, working_root=tmp_path / 'working')
    package = Path(promoted['package_root'])
    inventory, acceptance = promotion.validate_reconstruction_package(package, require_acceptance=False, working_root=tmp_path / 'working')
    assert inventory['scenario_id'] == 'synthetic-cpu-first'
    assert acceptance is None
    packaged_assets = [path for path in package.rglob('*.png') if path.name == materialized_assets[0].name]
    assert packaged_assets
    assert all(file_identity(path) == asset_identity for path in packaged_assets)


@pytest.mark.parametrize('eligible', ['04', '03', 'none'])
def test_intake_prefers_full_reuse_and_checks_fallback_independently(tmp_path, monkeypatch, eligible):
    verified, invoked = [], []
    def verify(_contract, _source, _prior, through, _runtime):
        verified.append(through)
        if eligible == 'none' or eligible == '03' and through.startswith('04'):
            raise replay.ReplayError('producer_closure_changed', through)
    def execute(_contract, _source, _prior, _root, _id, through, _runtime):
        invoked.append(through)
        return {'state': 'fixture_result'}
    monkeypatch.setattr(replay, 'verify_replay_source', verify)
    monkeypatch.setattr(replay, 'replay_run_engine', execute)
    if eligible == 'none':
        with pytest.raises(intake.FiveStepIntakeError, match='producer_closure_changed'):
            intake.start_reconstruction(tmp_path/'contract', tmp_path/'source', tmp_path/'new', 'new', None, replay_from=tmp_path/'old')
        assert invoked == []
    else:
        result = intake.start_reconstruction(tmp_path/'contract', tmp_path/'source', tmp_path/'new', 'new', None, replay_from=tmp_path/'old')
        assert invoked == [replay.STAGE_IDS[int(eligible)-1]]
        assert result['executed_stages'] == ([] if eligible == '04' else [replay.STAGE_IDS[3]])
    assert verified == ([replay.STAGE_IDS[3]] if eligible == '04' else [replay.STAGE_IDS[3], replay.STAGE_IDS[2]])


@pytest.mark.parametrize('source_stage04', ['failed', 'completed'])
def test_hybrid_reuses_three_stages_and_executes_fourth_once(tmp_path, monkeypatch, source_stage04):
    original_writer = fixtures._write_view_artifacts
    def complete_artifacts(root, pages=6):
        original_writer(root, pages)
        (root / 'images').mkdir()
        Image.new('RGB', (70, 50), 'navy').save(root / 'images/map.png')
        rows_path = root / 'document_content_list.json'
        rows = json.loads(rows_path.read_text())
        rows.append({'page_idx': 0, 'type': 'image', 'bbox': [10, 80, 80, 130],
                     'img_path': 'images/map.png', 'image_caption': [], 'image_footnote': []})
        fixtures._write_json(rows_path, rows)
        for suffix in ('origin', 'span'):
            (root / f'document_{suffix}.pdf').write_bytes((root / 'document_layout.pdf').read_bytes())
    monkeypatch.setattr(fixtures, '_write_view_artifacts', complete_artifacts)
    source, contract, runtime, _, _, predecessor = _full_fixture(tmp_path)
    renderer = os.environ.get('KB_CREATOR_PDFTOPPM')
    if renderer:
        runtime = replace(runtime, pdftoppm=Path(renderer))
    adapters = _run_adapters(predecessor)
    native_bundle = adapters['visual_merge_bundle']
    def complete_native_bundle(output):
        result = native_bundle.invoke(output)
        manifest = json.loads((output / 'visual/visual_manifest.json').read_text())
        (output / 'evidence').mkdir(exist_ok=True)
        (output / 'evidence/execution.json').write_text(json.dumps({
            **manifest['execution'], 'output_inventory': manifest['files'],
        }))
        return result
    adapters['visual_merge_bundle'] = reconstruction.StageAdapter('visual_merge_bundle', complete_native_bundle)
    if source_stage04 == 'failed':
        def fail(output):
            output.mkdir(parents=True)
            (output / 'diagnostic.txt').write_text('Synthetic Stage04 failure')
            raise ValueError('Synthetic Stage04 failure')
        adapters['visual_merge_bundle'] = reconstruction.StageAdapter('visual_merge_bundle', fail)
        with pytest.raises(reconstruction.ControlPlaneError, match='Synthetic Stage04 failure'):
            reconstruction.run_engine(contract, source, predecessor, 'producer', runtime=runtime, adapters=adapters)
    else:
        reconstruction.run_engine(contract, source, predecessor, 'producer', runtime=runtime, adapters=adapters)
    before = deterministic_inventory(predecessor)
    invoked = []
    def successor_adapters(run, *_args):
        root = Path(run['local']['run_root'])
        stage04 = _run_adapters(root)['visual_merge_bundle']
        def build(output):
            invoked.append('visual_merge_bundle')
            if renderer and source_stage04 == 'completed':
                raw = root / 'outputs/02-mineru-three-view'
                comparison = root / 'outputs/03-compare-views/comparison.json'
                prepared = root / 'outputs/01-prepare-inputs/prepared/sample_pages.json'
                return bundle.build_bundle(
                    raw_root=raw, output_root=output, raw_receipt=raw / 'view-set.json',
                    raw_receipt_sha256=bundle.sha256_file(raw / 'view-set.json'),
                    source=source, source_sha256=bundle.sha256_file(source),
                    comparison=comparison, comparison_sha256=bundle.sha256_file(comparison),
                    pdftoppm=renderer, dpi=run['options']['review_dpi'], expected_pages=6,
                    reconstruction_contract=contract, prepared_manifest=prepared,
                    prepared_manifest_sha256=bundle.sha256_file(prepared),
                )
            return stage04.invoke(output)
        # No OCR adapter is available to the recovery engine.
        return {'visual_merge_bundle': reconstruction.StageAdapter('visual_merge_bundle', build)}
    monkeypatch.setattr(reconstruction, 'production_run_adapters', successor_adapters)
    successor = tmp_path / 'working/synthetic-cpu-first/reconstruction/successor'
    successor.parent.mkdir(parents=True)
    result = replay.replay_run_engine(contract, source, predecessor, successor, 'successor', '03', runtime)
    assert result['state'] == 'needs_review'
    assert invoked == ['visual_merge_bundle']
    assert deterministic_inventory(predecessor) == before
    authority = replay.validate_replay_authorities(successor)
    review_authority = resume.validate_replay_review_queue(authority)
    assert review_authority.queue['schema'] == replay.QUEUE_SCHEMA
    assert authority.merge_packets.is_dir()
    assert authority.geometry_plan.is_file()
    assert len(list((authority.merge_packets / 'pages').glob('page-*.json'))) == 6
    queue = json.loads((successor / 'review/review_queue.json').read_text())
    assert all(item['state'] == 'open' for item in queue['items'])
    assert len(json.loads((successor / 'replay/bridge.json').read_text())['stages']) == 3
    assert (successor / 'replay/completion.json').is_file()
    assert not (successor / 'outputs/05-fidelity-audit').exists()

    # Exercise the same evidence validator used by portable promotion.
    package = tmp_path / 'package'
    evidence = package / 'evidence/replay'
    evidence.mkdir(parents=True)
    for name in ('intake.json', 'bridge.json', 'completion.json'):
        shutil.copyfile(successor / 'replay' / name, evidence / name)
    stages = []
    for stage_id in replay.STAGE_IDS[:4]:
        stage_path = successor / 'stages' / stage_id / 'stage.json'
        stages.append(json.loads(stage_path.read_text()))
        destination = package / 'evidence/stages' / f'{stage_id}.stage.json'
        destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(stage_path, destination)
        if stage_id in replay.STAGE_IDS[:3]:
            shutil.copyfile(successor / 'stages' / stage_id / 'rebase.json', evidence / f'{stage_id}.rebase.json')
    run = json.loads((successor / 'run.json').read_text())
    promotion._validate_packaged_replay_evidence(package, stages, run)
    completion_path = successor / 'replay/completion.json'
    original = completion_path.read_bytes()
    for mutation in ('mode', 'upstream', 'extra', 'manifest'):
        changed = json.loads(original)
        if mutation == 'mode':
            changed['executed_stage']['execution']['producer_invoked'] = False
        elif mutation == 'upstream':
            changed['replayed_stages'][0]['manifest_sha256'] = 'F' * 64
        elif mutation == 'extra':
            changed['unexpected'] = True
        else:
            changed['executed_stage']['manifest']['sha256'] = 'F' * 64
        changed.pop('completion_sha256')
        changed = replay._seal(replay.HYBRID_COMPLETION_SCHEMA, changed, 'completion_sha256')
        encoded = json.dumps(changed).encode()
        completion_path.write_bytes(encoded)
        (evidence / 'completion.json').write_bytes(encoded)
        with pytest.raises(replay.ReplayError, match='hybrid_completion'):
            replay.validate_replay_authorities(successor)
        with pytest.raises(promotion.ReconstructionPromotionError, match='hybrid completion'):
            promotion._validate_packaged_replay_evidence(package, stages, run)
    completion_path.write_bytes(original)
    completion_path.unlink()
    with pytest.raises((replay.ReplayError, FileNotFoundError)):
        replay.validate_replayed_prefix(successor, expected_through='03')
    completion_path.write_bytes(original)
    assert replay.validate_replay_authorities(successor).geometry_plan.is_file()
    if source_stage04 == 'completed':
        full = tmp_path / 'full-successor'
        replay.replay_run_engine(contract, source, predecessor, full, 'full-successor', '04', runtime)
        full_authority = replay.validate_replay_authorities(full)
        assert full_authority.geometry_plan.is_file()
        assert full_authority.merge_packets.is_dir()
        assert invoked == ['visual_merge_bundle']
        _resume_semantic_fixture_and_promote(successor, tmp_path)
    else:
        def failed_adapters(*_):
            def fail(output):
                output.mkdir(parents=True)
                (output / 'diagnostic.txt').write_text('successor failure')
                raise ValueError('successor failure')
            return {'visual_merge_bundle': reconstruction.StageAdapter('visual_merge_bundle', fail)}
        monkeypatch.setattr(reconstruction, 'production_run_adapters', failed_adapters)
        failed = tmp_path / 'failed-successor'
        with pytest.raises(reconstruction.ControlPlaneError, match='successor failure'):
            replay.replay_run_engine(contract, source, predecessor, failed, 'failed-successor', '03', runtime)
        assert (failed / 'failures/04-visual-merge-bundle/diagnostic.txt').is_file()
        assert (failed / 'failures/04-visual-merge-bundle/stage-failure.json').is_file()
        assert not (failed / 'replay/completion.json').exists()
        assert not (failed / 'review/review_queue.json').exists()
        with pytest.raises((replay.ReplayError, FileNotFoundError)):
            replay.validate_replayed_prefix(failed, expected_through='03')
        assert deterministic_inventory(predecessor) == before
