import hashlib
import json

import pytest
from pypdf import PdfReader, PdfWriter

from kb_creator.scripts.finalize_mineru_reconstruction import finalise, role_partition


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def j(path): return json.loads(path.read_text(encoding="utf-8"))
def pdf(path, count, width=72):
    writer = PdfWriter()
    for _ in range(count): writer.add_blank_page(width, 72)
    with path.open("wb") as stream: writer.write(stream)


def fixture(root):
    root.mkdir(parents=True, exist_ok=True); count = 124; source = root / "source.pdf"; pdf(source, count)
    roles = [{"role":"scenario_body","first_page":1,"last_page":68},{"role":"player_handouts","first_page":69,"last_page":103},{"role":"keeper_maps","first_page":104,"last_page":110},{"role":"pregenerated_investigators","first_page":111,"last_page":123},{"role":"back_cover","first_page":124,"last_page":124}]
    contract = root / "contract.json"; contract.write_text(json.dumps({"contract_revision":"v1","scenario":{"id":"x"},"source":{"sha256":sha(source),"byte_count":source.stat().st_size,"page_count":count,"media_box_points":[72,72],"rotation_degrees":0},"page_roles":roles}), encoding="utf-8")
    raw = root / "raw"; views = {}
    for view in ("original_hybrid","original_pipeline_ocr","raster_hybrid"):
        folder = raw / "runs" / view / "x"; folder.mkdir(parents=True); pdf(folder / "x_layout.pdf", count, 72)
        views[view] = {"blocks":[{"raw_index":page-1,"source_page":page} for page in range(1,count+1)]}
    (raw / "comparison").mkdir(); (raw / "comparison" / "comparison.json").write_text(json.dumps({"views":views}), encoding="utf-8")
    candidate = root / "candidate"; (candidate / "pages").mkdir(parents=True); (candidate / "decisions").mkdir(); (candidate / "assets").mkdir(); (candidate / "assets" / "a.jpg").write_bytes(b"asset")
    labels = ["1","2a","2b","3a","3b",*map(str,range(4,40))]; provenance = []
    for page in range(1,count+1):
        headings = ""
        if 69 <= page <= 89 and labels:
            page_labels, labels = labels[:2], labels[2:]
            headings = "\n".join(f"*Handout #{label}*" for label in page_labels) + "\n"
        selected = [{"view":"original_hybrid","raw_index":page-1,"purpose":"structure"}]; decision = {"selected_blocks":selected,"unresolved":[]}
        (candidate / "pages" / f"page-{page:03d}.md").write_text(f"<!-- source-page-{page:03d} -->\n{headings}",encoding="utf-8")
        (candidate / "decisions" / f"page-{page:03d}.json").write_text(json.dumps(decision),encoding="utf-8")
        provenance.append({"source_page":page,"semantic_role":"fine","selected_blocks":[{"view":"original_hybrid","raw_index":page-1}],"unresolved":[]})
    (candidate / "RECONSTRUCTED_EN.md").write_text("\n".join((candidate / "pages" / f"page-{p:03d}.md").read_text(encoding="utf-8") for p in range(1,count+1)),encoding="utf-8")
    (candidate / "OVERLAY_SELECTION.json").write_text(json.dumps({"pages":[{"source_page":p,"overlay_preference":"original_hybrid"} for p in range(1,count+1)]}),encoding="utf-8")
    (candidate / "MERGE_PROVENANCE.json").write_text(json.dumps({"pages":provenance}),encoding="utf-8")
    (candidate / "ASSET_MANIFEST.json").write_text(json.dumps({"assets":[{"stored_path":"assets/a.jpg","sha256":sha(candidate / "assets" / "a.jpg")}]}),encoding="utf-8")
    return contract, source, raw, candidate


def test_success_handouts_identity_and_overlay_order(tmp_path):
    contract, source, raw, candidate = fixture(tmp_path / "one"); out = tmp_path / "one" / "out"
    assert finalise(contract,source,raw,candidate,out)["pages"] == 124
    provenance = j(out / "RECONSTRUCTION_PROVENANCE.json")
    assert len(provenance["handouts"]) == 41 and provenance["handouts"][0] == {"label":"1","source_page":69}
    assert provenance["candidate_identity"]["file_count"] > 0 and provenance["selected_overlay"]["sha256"] == sha(out / "SELECTED_OVERLAY.pdf")
    assert set(provenance["candidate_identity"]["named_root_artifacts"]) == {"RECONSTRUCTED_EN.md","MERGE_PROVENANCE.json","ASSET_MANIFEST.json","OVERLAY_SELECTION.json"}
    assert len(PdfReader(str(out / "SELECTED_OVERLAY.pdf")).pages) == 124
    assert (out / "RECONSTRUCTION_QA.json").read_bytes().endswith(b"\n")
    contract2, source2, raw2, candidate2 = fixture(tmp_path / "two"); out2 = tmp_path / "two" / "out"
    finalise(contract2,source2,raw2,candidate2,out2)
    assert (out / "RECONSTRUCTION_PROVENANCE.json").read_bytes() == (out2 / "RECONSTRUCTION_PROVENANCE.json").read_bytes()
    assert [row["source_page"] for row in provenance["pages"]] == list(range(1, 125))


@pytest.mark.parametrize("heading",["*Handout 1*","## Handout #1"])
def test_exact_handout_hash_marker(tmp_path,heading):
    contract,source,raw,candidate=fixture(tmp_path); page=candidate/"pages"/"page-069.md"
    page.write_text(page.read_text(encoding="utf-8").replace("*Handout #1*",heading),encoding="utf-8")
    with pytest.raises(ValueError,match="Handout marker"): finalise(contract,source,raw,candidate,tmp_path/"out")


@pytest.mark.parametrize("mode",["duplicate","outside"])
def test_handout_duplicate_and_role_boundary(tmp_path,mode):
    contract,source,raw,candidate=fixture(tmp_path); page=candidate/"pages"/("page-070.md" if mode=="duplicate" else "page-001.md")
    page.write_text(page.read_text(encoding="utf-8")+"*Handout #1*\n",encoding="utf-8")
    with pytest.raises(ValueError): finalise(contract,source,raw,candidate,tmp_path/"out")


@pytest.mark.parametrize("mode",["page","decision","marker","selection"])
def test_all_page_domains_are_closed(tmp_path,mode):
    contract,source,raw,candidate=fixture(tmp_path)
    if mode=="page": (candidate/"pages"/"page-124.md").unlink()
    elif mode=="decision": (candidate/"decisions"/"page-124.json").unlink()
    elif mode=="marker": (candidate/"RECONSTRUCTED_EN.md").write_text("<!-- source-page-001 -->",encoding="utf-8")
    else:
        data=j(candidate/"OVERLAY_SELECTION.json"); data["pages"].append(data["pages"][0]); (candidate/"OVERLAY_SELECTION.json").write_text(json.dumps(data),encoding="utf-8")
    with pytest.raises(ValueError): finalise(contract,source,raw,candidate,tmp_path/"out")


@pytest.mark.parametrize("mode",["mismatch","view","unresolved"])
def test_decision_provenance_comparison_and_blockers(tmp_path,mode):
    contract,source,raw,candidate=fixture(tmp_path)
    if mode=="mismatch":
        data=j(candidate/"MERGE_PROVENANCE.json"); data["pages"][0]["selected_blocks"]=[]; (candidate/"MERGE_PROVENANCE.json").write_text(json.dumps(data),encoding="utf-8")
    elif mode=="view":
        data=j(candidate/"decisions"/"page-001.json"); data["selected_blocks"][0]["view"]="unknown"; (candidate/"decisions"/"page-001.json").write_text(json.dumps(data),encoding="utf-8")
    else:
        for path in (candidate/"decisions"/"page-001.json",candidate/"MERGE_PROVENANCE.json"):
            data=j(path); target=data if path.name!="MERGE_PROVENANCE.json" else data["pages"][0]; target["unresolved"]=[{"reason":"open"}]; path.write_text(json.dumps(data),encoding="utf-8")
    with pytest.raises(ValueError): finalise(contract,source,raw,candidate,tmp_path/"out")


@pytest.mark.parametrize("mode",["missing","corrupt","extra","escape","link"])
def test_asset_closure(tmp_path,mode):
    contract,source,raw,candidate=fixture(tmp_path); asset=candidate/"assets"/"a.jpg"
    if mode=="missing": asset.unlink()
    elif mode=="corrupt": asset.write_bytes(b"changed")
    elif mode=="extra": (candidate/"assets"/"extra.jpg").write_bytes(b"x")
    elif mode=="escape":
        data=j(candidate/"ASSET_MANIFEST.json"); data["assets"][0]["stored_path"]="../escape.jpg"; (candidate/"ASSET_MANIFEST.json").write_text(json.dumps(data),encoding="utf-8")
    else:
        path=candidate/"pages"/"page-001.md"; path.write_text(path.read_text(encoding="utf-8")+"![x](../../outside.jpg)\n",encoding="utf-8")
    with pytest.raises(ValueError): finalise(contract,source,raw,candidate,tmp_path/"out")


@pytest.mark.parametrize("mode",["bad","duplicate","short","geometry"])
def test_overlay_selection_and_layout_domain(tmp_path,mode):
    contract,source,raw,candidate=fixture(tmp_path)
    if mode=="short": pdf(next((raw/"runs"/"original_hybrid").rglob("*_layout.pdf")),1)
    elif mode=="geometry": pdf(next((raw/"runs"/"original_hybrid").rglob("*_layout.pdf")),124,81)
    else:
        data=j(candidate/"OVERLAY_SELECTION.json")
        if mode=="bad": data["pages"][0]["overlay_preference"]="bad"
        else: data["pages"].append(data["pages"][0])
        (candidate/"OVERLAY_SELECTION.json").write_text(json.dumps(data),encoding="utf-8")
    with pytest.raises(ValueError): finalise(contract,source,raw,candidate,tmp_path/"out")


def test_roles_source_and_existing_output_and_clean_stage(tmp_path):
    contract,source,raw,candidate=fixture(tmp_path); data=j(contract); data["page_roles"][1]["first_page"]=70
    with pytest.raises(ValueError,match="gap"): role_partition(data)
    data=j(contract); data["source"]["sha256"]="A"*64; contract.write_text(json.dumps(data),encoding="utf-8")
    with pytest.raises(ValueError,match="source identity"): finalise(contract,source,raw,candidate,tmp_path/"out")
    contract,source,raw,candidate=fixture(tmp_path/"existing"); out=tmp_path/"existing"/"out"; out.mkdir()
    with pytest.raises(FileExistsError): finalise(contract,source,raw,candidate,out)
    contract,source,raw,candidate=fixture(tmp_path/"stage"); pdf(next((raw/"runs"/"original_hybrid").rglob("*_layout.pdf")),1)
    with pytest.raises(ValueError): finalise(contract,source,raw,candidate,tmp_path/"stage"/"out")
    assert not list((tmp_path/"stage").glob(".out.stage-*"))


@pytest.mark.parametrize("payload", [b"bad\rline\n", b"bad\r\r\nline\n"])
def test_finalizer_rejects_malformed_page_eol(tmp_path, payload):
    contract, source, raw, candidate = fixture(tmp_path)
    (candidate / "pages" / "page-001.md").write_bytes(payload)
    with pytest.raises(ValueError, match="malformed EOL"):
        finalise(contract, source, raw, candidate, tmp_path / "out")
