import pytest

from kb_creator.pipeline import reconstruction
from kb_creator.pipeline.handout_ledger import declared_occurrences, visible_caption
from kb_creator.pipeline import reconstruction_promotion as promotion


def _contract():
    return {
        "schema": reconstruction.CONTRACT_SCHEMA_V3, "contract_revision": 3,
        "scenario": {"id": "sample", "title": "Sample"},
        "source": {"sha256": "A" * 64, "byte_count": 1, "page_count": 3, "media_box_points": [500, 700], "rotation_degrees": 0},
        "scope": {"mode": "all_source_pages", "first_page": 1, "last_page": 3, "required_entities": {"handout_label_sets": [
            {"scope_id": "alpha", "labels": [{"label": "1", "occurrences": [{"source_page": 1, "section": "body"}, {"source_page": 3, "section": "appendix"}]}, {"label": "3", "occurrences": [{"source_page": 3, "section": "appendix"}]}]}
        ]}},
        "page_roles": [{"role": "body", "first_page": 1, "last_page": 2, "content_mode": "text", "traits": [], "strategies": ["reading_order"]}, {"role": "appendix", "first_page": 3, "last_page": 3, "content_mode": "text", "traits": [], "strategies": ["reading_order"]}],
        "reconstruction": {"strategies": ["reading_order"], "required_review": True}, "acceptance": {"approval_authority": "configured_reconstruction_review"},
    }


def test_v3_accepts_explicit_repeated_physical_occurrences_and_preserves_v1_shape():
    value = _contract()
    assert reconstruction.validate_contract(value) == value
    assert declared_occurrences(value) == {("alpha", "1", 1, "body"), ("alpha", "1", 3, "appendix"), ("alpha", "3", 3, "appendix")}
    assert visible_caption("## Alpha Handout #3 — Appendix") == ("alpha", "3")
    assert visible_caption("Give Alpha Handout #3 to players") is None


def test_v3_rejects_duplicate_or_unordered_source_occurrences():
    value = _contract(); value["scope"]["required_entities"]["handout_label_sets"][0]["labels"][1]["occurrences"].append({"source_page": 3, "section": "appendix"})
    with pytest.raises(reconstruction.ControlPlaneError, match="duplicate handout occurrence"):
        reconstruction.validate_contract(value)


def test_ledger_requires_visible_caption_and_exact_body_appendix_occurrences():
    contract = _contract()
    decisions = {1: {"markdown": "## Alpha Handout #1"}, 2: {"markdown": "Alpha Handout #1 is mentioned"}, 3: {"markdown": "## Alpha Handout #1\n## Alpha Handout #3"}}
    assert promotion._v3_handout_ledger(contract, decisions, code="test") == declared_occurrences(contract)
    decisions[3]["markdown"] = "## Alpha Handout #1"
    assert promotion._v3_handout_ledger(contract, decisions, code="test") != declared_occurrences(contract)

@pytest.mark.parametrize('caption,expected', [
    ('Player Handout A', (None,'A')),
    ('Investigator Handout #1', (None,'1')),
    ('## Alpha Investigator Handout #3', ('alpha','3')),
    ('> **Alpha Player Handout A**', ('alpha','A')),
    ('Alpha Investigator’s Handout #2', ('alpha','2')),
    ('Give Alpha Handout #3 to players', None),
    ('handout-1.png', None),
])
def test_source_caption_forms(caption, expected):
    assert visible_caption(caption) == expected


def test_semantic_caption_and_heading_are_one_physical_observation():
    from kb_creator.pipeline.handout_ledger import observed_occurrences
    contract = _contract()
    decisions = {1: {'markdown':'## Alpha Handout #1\nText', 'semantic_structure':{'units':[{'kind':'handout','markdown_span':{'start_line':1,'end_line':2}}]}},
                 3: {'markdown':'> **Alpha Investigator Handout #1**\nText\n> **Alpha Handout #3**\nOther text', 'semantic_structure':{'units':[{'kind':'handout','markdown_span':{'start_line':1,'end_line':2}}, {'kind':'handout','markdown_span':{'start_line':3,'end_line':4}}]}}}
    assert observed_occurrences(contract, decisions) == declared_occurrences(contract)


@pytest.mark.parametrize('markdown,reason', [
    ('## Alpha Handout #1\n## Alpha Handout #1', 'duplicate physical'),
    ('## Alpha Handout #9', 'foreign'),
    ('## Beta Handout #1', 'foreign'),
])
def test_duplicate_foreign_label_or_scope_rejected(markdown, reason):
    from kb_creator.pipeline.handout_ledger import observed_occurrences
    with pytest.raises(ValueError, match=reason):
        observed_occurrences(_contract(), {1:{'markdown':markdown}})


def test_prose_and_asset_filename_do_not_prove_handout():
    from kb_creator.pipeline.handout_ledger import observed_occurrences
    decisions={1:{'markdown':'Please see Alpha Handout #1.', 'assets':[{'logical_name':'alpha-player-handout-1.png'}]}}
    assert observed_occurrences(_contract(), decisions) == set()


def test_scope_is_required_when_same_page_has_two_source_scopes():
    import copy
    from kb_creator.pipeline.handout_ledger import observed_occurrences
    contract=_contract()
    beta=copy.deepcopy(contract['scope']['required_entities']['handout_label_sets'][0]);beta['scope_id']='beta'
    contract['scope']['required_entities']['handout_label_sets'].append(beta)
    with pytest.raises(ValueError, match='ambiguous'):
        observed_occurrences(contract,{1:{'markdown':'## Investigator Handout #1'}})
    rows=observed_occurrences(contract,{1:{'markdown':'## Alpha Handout #1\n## Beta Handout #1'}})
    assert rows=={('alpha','1',1,'body'),('beta','1',1,'body')}


def test_section_and_actual_page_must_match_declared_occurrence():
    from kb_creator.pipeline.handout_ledger import observed_occurrences
    contract=_contract()
    with pytest.raises(ValueError, match='page 2'):
        observed_occurrences(contract,{2:{'markdown':'## Alpha Handout #1'}})
    contract['page_roles'][1]['role']='body'
    with pytest.raises(ValueError, match='page 3'):
        observed_occurrences(contract,{3:{'markdown':'## Alpha Handout #1'}})


@pytest.mark.parametrize('units', [
    [{'kind':'handout','markdown_span':{'start_line':2,'end_line':1}}],
    [{'kind':'handout','markdown_span':{'start_line':1,'end_line':2}}],
])
def test_invalid_or_unlabelled_semantic_unit_rejected(units):
    from kb_creator.pipeline.handout_ledger import observed_occurrences
    with pytest.raises(ValueError, match='handout'):
        observed_occurrences(_contract(),{1:{'markdown':'Body\nAnother body', 'semantic_structure':{'units':units}}})


def test_lettered_two_up_source_is_complete_without_numeric_renumbering():
    from kb_creator.pipeline.handout_ledger import observed_occurrences
    contract=_contract()
    contract['source']['page_count']=4
    contract['scope']['last_page']=4
    contract['scope']['required_entities']={'handout_label_sets':[{'scope_id':'scenario','labels':[
        {'label':letter,'occurrences':[{'source_page':1+index//2,'section':'appendix'}]} for index,letter in enumerate('ABCDEFGH')]}]}
    contract['page_roles']=[{'role':'handout_appendix','first_page':1,'last_page':4,'content_mode':'mixed','traits':[], 'strategies':['reading_order']}]
    reconstruction.validate_contract(contract)
    decisions={page:{'markdown':'\n'.join(f'## Player Handout {letter}' for letter in 'ABCDEFGH'[(page-1)*2:page*2])} for page in range(1,5)}
    assert observed_occurrences(contract,decisions)==declared_occurrences(contract)
    decisions[4]['markdown']='## Player Handout G'
    assert declared_occurrences(contract)-observed_occurrences(contract,decisions)=={('scenario','H',4,'appendix')}
    decisions[4]['markdown']='## Player Handout G\n## Player Handout I'
    with pytest.raises(ValueError,match='label I'):
        observed_occurrences(contract,decisions)

@pytest.mark.parametrize('role', ['frontmatter','player_handouts','body_appendix'])
def test_handout_topology_is_explicit_and_unambiguous(role):
    from kb_creator.pipeline.handout_ledger import observed_occurrences
    contract=_contract();contract['page_roles'][0]['role']=role
    with pytest.raises(ValueError,match='explicit body or appendix'):
        observed_occurrences(contract,{1:{'markdown':'## Alpha Handout #1'}})
    # Unrelated pages need no handout-topology classification.
    assert observed_occurrences(contract,{1:{'markdown':'Introduction'}})==set()
