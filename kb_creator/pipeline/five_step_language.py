"""Identity-bound documentary draft and proofread-final pipeline stage."""
from __future__ import annotations
import hashlib, json, os, shutil, stat, tempfile
import re
from pathlib import Path
from typing import Any
from kb_creator.scripts import scenario_master_ru as legacy
from kb_creator.scripts.prepare_translation_batches import batch_units, expand_units_for_translation
from .language_numeric import represented_numbers
from .language_unit_context import derive as derive_unit_context, context_by_unit

class FiveStepLanguageError(ValueError): pass
def _canonical(v: object) -> bytes: return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
def _sha(v: bytes) -> str: return hashlib.sha256(v).hexdigest().upper()
def _fsha(p: Path) -> str: return _sha(p.read_bytes())
def _id(p: Path, root: Path) -> dict[str, Any]: return {"path": p.resolve().relative_to(root.resolve()).as_posix(), "bytes": p.stat().st_size, "sha256": _fsha(p)}
def _read(p: Path) -> dict[str, Any]:
    try: v=json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError,json.JSONDecodeError) as e: raise FiveStepLanguageError(f"cannot read JSON: {p}") from e
    if not isinstance(v,dict): raise FiveStepLanguageError(f"JSON object required: {p}")
    return v
def _write(p: Path,v: object) -> None: p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
def _seal(schema: str,v: dict[str,Any],key: str) -> dict[str,Any]:
    r={"schema":schema,**v}; r[key]=_sha(_canonical(r)); return r
def _seal_ok(v: dict[str,Any],key: str,schema: str, optional=False) -> None:
    if v.get("schema")!=schema: raise FiveStepLanguageError(f"invalid {schema} schema")
    if key not in v:
        if optional:return
        raise FiveStepLanguageError(f"{schema} seal missing")
    if not isinstance(v[key],str) or _sha(_canonical({k:x for k,x in v.items() if k!=key}))!=v[key]: raise FiveStepLanguageError(f"{schema} seal mismatch")
def _atomic(target: Path,build: Any)->None:
    if target.exists() or not target.parent.is_dir(): raise FiveStepLanguageError("immutable destination must be absent under an existing parent")
    stage=Path(tempfile.mkdtemp(prefix=f".{target.name}.staging.",dir=target.parent))
    try: build(stage);os.replace(stage,target)
    except Exception: shutil.rmtree(stage,ignore_errors=True);raise
def _terms(p:Path)->list[dict[str,Any]]:
    try:return legacy._terminology_terms([("selected",p)])
    except (OSError,legacy.MasterRuError) as e:raise FiveStepLanguageError(f"invalid glossary: {e}") from e

def _terminology_context(p:Path)->dict[str,Any]:
    if p.suffix.lower() != ".json": return {}
    value=_read(p)
    if value.get("schema") != "kb_creator.effective_coc_glossary.v1": return {}
    from .coc_glossary import validate_payload
    verified=validate_payload(value)
    return {"system":verified["system"],"book_id":verified["book_id"],
            "glossary_sha256":verified["glossary_sha256"],**verified["context"]}
def _unit(row:dict[str,Any])->dict[str,Any]:
    return {"unit_id":row["unit_id"],"source_hash":row.get("source_hash") or _sha(str(row["source_text"]).encode()),"source_text":row["source_text"],"page":row.get("page"),"parent_unit_id":row.get("parent_unit_id"),"part_index":row.get("part_index"),"part_count":row.get("part_count")}
def _units(master:Path,size:int)->tuple[list[dict[str,Any]],list[list[dict[str,Any]]]]:
    if size<128:raise FiveStepLanguageError("max_batch_chars must be >= 128")
    base=legacy._source_units(master.read_text(encoding="utf-8")); expanded=expand_units_for_translation(base,size)
    if not expanded:raise FiveStepLanguageError("MASTER_EN has no translatable units")
    return expanded,batch_units(expanded,size)
def _task_schema(task:dict[str,Any])->str:
    schema=task.get("schema")
    if schema not in {"kb_creator.five_step_language_draft_task.v2","kb_creator.five_step_language_draft_task.v3"}:raise FiveStepLanguageError("invalid language task schema")
    return schema
def _verified_unit_context(task:dict[str,Any],master:Path)->dict[str,dict[str,Any]]|None:
    # Historical v2 tasks remain verifiable, but never claim this v3 context proof.
    if _task_schema(task)!="kb_creator.five_step_language_draft_task.v3": return None
    try:return context_by_unit(master.read_text(encoding="utf-8"),task["max_batch_chars"],task.get("source_unit_context"))
    except (KeyError,TypeError,ValueError) as e:raise FiveStepLanguageError("task source-unit context is unavailable or stale") from e
def _source(task:dict[str,Any],name:str)->Path:
    p=Path(str(task.get(name+"_path") or "")).resolve(); r=task.get(name)
    if not p.is_file() or not isinstance(r,dict) or p.stat().st_size!=r.get("bytes") or _fsha(p)!=r.get("sha256"):raise FiveStepLanguageError(f"task {name} identity unavailable or stale")
    return p
def _source_spans(master:Path)->tuple[Path,dict]:
    p=master.parent/"EN_SOURCE_SPANS.json";v=_read(p);_seal_ok(v,"spans_sha256","kb_creator.five_step_en_source_spans.v1")
    if v.get("master_en")!={"path":"MASTER_EN.md","bytes":master.stat().st_size,"sha256":_fsha(master)} or not isinstance(v.get("spans"),list):raise FiveStepLanguageError("EN_SOURCE_SPANS MASTER_EN binding mismatch")
    return p,v

_IMAGE_LINE = re.compile(r"^!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)$")
_QUOTE_BLANK = re.compile(r"^[ \t]*>[ \t]*$")
_QUOTE_CONTENT = re.compile(r"^[ \t]*>[ \t]+(?!>)(?=.*\S).+$")

def _line_class(line:str)->str:
    if _IMAGE_LINE.fullmatch(line.strip()): return "image"
    if re.match(r"^#{1,6}\s+",line): return "heading"
    if line.startswith("> "): return "blockquote"
    if line.startswith(("- ","* ","+ ")) or re.match(r"^\d+[.)]\s+",line): return "list"
    if line.startswith("|"): return "table"
    return "text"

def _line_topology(text:str)->tuple[list[str],list[str]]:
    lines=text.splitlines()
    return ([_line_class(line) for line in lines], [match.group(1) for line in lines if (match:=_IMAGE_LINE.fullmatch(line.strip()))])

def _line_numeric_signature(text:str)->list[list[str]]:
    """Keep numeric mechanics on their reviewed source line during projection."""
    return [represented_numbers(line) for line in text.splitlines()]

def _same_line_correspondence(source:str,ru:str)->bool:
    source_classes,source_images=_line_topology(source);ru_classes,ru_images=_line_topology(ru)
    return (source_classes==ru_classes and source_images==ru_images and
            _line_numeric_signature(source)==_line_numeric_signature(ru))

def _reviewed_span_boundary(span:dict)->bool:
    decision=span.get("decision")
    return (isinstance(decision,dict) and set(decision)=={"path","bytes","sha256"} and
            isinstance(decision["path"],str) and bool(decision["path"]) and
            isinstance(decision["bytes"],int) and decision["bytes"]>=0 and
            isinstance(decision["sha256"],str) and len(decision["sha256"])==64)

def _image_only(text:str)->bool:
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    return bool(lines) and all(_IMAGE_LINE.fullmatch(line) for line in lines)

def _line_edge(text:str,offset:int)->bool:
    return 0 <= offset <= len(text) and (offset==0 or text[offset-1]=="\n" or offset==len(text) or text[offset]=="\n")

def _line_offset(text:str,line_count:int,*,end:bool)->int:
    lines=text.splitlines(keepends=True)
    if not 0 < line_count <= len(lines): raise FiveStepLanguageError("semantic line mapping is outside RU unit")
    start=sum(len(line) for line in lines[:line_count-1])
    return start + (len(lines[line_count-1].rstrip("\r\n")) if end else 0)

def _source_intervals(master:Path,rows:list[dict])->list[tuple[int,int,dict]]:
    text=master.read_text(encoding="utf-8"); intervals=[]; cursor=0
    for row in rows:
        source=row.get("source_text")
        if not isinstance(source,str) or not source: raise FiveStepLanguageError("source translation unit is malformed")
        left=text.find(source,cursor)
        if left<0: raise FiveStepLanguageError("source translation unit cannot be located uniquely in MASTER_EN")
        intervals.append((left,left+len(source),row)); cursor=left+len(source)
    return intervals

def _depth_one_quote_boundary(left:str,right:str)->bool:
    left_lines=left.splitlines();right_lines=right.splitlines()
    return bool(left_lines and right_lines and _QUOTE_BLANK.fullmatch(left_lines[-1]) and _QUOTE_CONTENT.fullmatch(right_lines[0]))

def _split_join(left:str,right:str,left_row:dict[str,Any],right_row:dict[str,Any])->str:
    if not _depth_one_quote_boundary(left,right):
        return legacy._boundary_join(left,right)[0]
    left_source,right_source=left_row.get("source_text"),right_row.get("source_text")
    if isinstance(left_source,str) or isinstance(right_source,str):
        if not isinstance(left_source,str) or not isinstance(right_source,str) or not _depth_one_quote_boundary(left_source,right_source):
            raise FiveStepLanguageError("split quote boundary does not match source topology")
    return left+"\n"+right

def _assemble_map(rows:list[dict])->dict[str,Any]:
    """Use the legacy split-boundary rule once and expose only provable edges."""
    if not rows: raise FiveStepLanguageError("cannot assemble empty RU units")
    groups=[]; current=[]
    for row in rows:
        if not isinstance(row.get("ru_text"),str) or not row["ru_text"].strip(): raise FiveStepLanguageError("RU projection unit text is malformed")
        if current and row.get("parent_unit_id") and row.get("parent_unit_id")==current[-1].get("parent_unit_id"):
            current.append(row)
        else:
            if current: groups.append(current)
            current=[row]
    groups.append(current)
    chunks=[]; positions={}; cursor=0
    for group_index,group in enumerate(groups):
        value=group[0]["ru_text"].strip()
        prior=group[0]
        for row in group[1:]:
            value=_split_join(value,row["ru_text"].strip(),prior,row);prior=row
        if group_index: cursor+=2
        group_start=cursor; cursor+=len(value); group_end=cursor; chunks.append(value)
        split=len(group)>1
        for index,row in enumerate(group):
            positions[row["unit_id"]]={"group_start":group_start,"group_end":group_end,"split":split,"group_first":index==0,"group_last":index==len(group)-1,"unit_length":len(row["ru_text"].strip())}
        if not split:
            positions[group[0]["unit_id"]].update(start=group_start,end=group_end)
    return {"text":"\n\n".join(chunks).strip()+"\n","positions":positions}

def _semantic_edge(assembly:dict[str,Any],unit_id:str,offset:int,*,edge:str)->int:
    position=assembly["positions"].get(unit_id)
    if position is None or not isinstance(offset,int): raise FiveStepLanguageError("semantic span unit boundary is invalid")
    if not position["split"]:
        limit=position["end"]-position["start"]
        if not 0 <= offset <= limit: raise FiveStepLanguageError("semantic span unit offset is invalid")
        return position["start"]+offset
    if edge=="start" and offset==0 and position["group_first"]: return position["group_start"]
    if edge=="end" and offset==position["unit_length"] and position["group_last"]: return position["group_end"]
    # A split sibling can only be bounded at the full parent's external edges.
    raise FiveStepLanguageError("semantic span edge inside split sibling group is not provable")
def _project_spans(master:Path,rows:list[dict],source_spans:dict)->list[dict]:
    text=master.read_text(encoding="utf-8");starts=[0]
    for i,c in enumerate(text):
        if c=="\n":starts.append(i+1)
    intervals=_source_intervals(master,rows)
    output=[]
    for span in source_spans["spans"]:
        if not isinstance(span,dict) or span.get("kind")!="statblock":continue
        if not isinstance(span.get("id"),str) or not isinstance(span.get("start_line"),int) or not isinstance(span.get("end_line"),int) or span["start_line"]<1 or span["end_line"]<span["start_line"] or span["end_line"]>len(starts):raise FiveStepLanguageError("EN_SOURCE_SPANS statblock line shape mismatch")
        a=starts[span["start_line"]-1];b=text.find("\n",starts[span["end_line"]-1]);b=len(text) if b<0 else b
        if _sha(text[a:b].encode())!=span.get("sha256"):raise FiveStepLanguageError("EN_SOURCE_SPANS text hash mismatch")
        hit=[(left,right,r) for left,right,r in intervals if left<b and right>a]
        if not hit:raise FiveStepLanguageError("semantic source span has no translation units")
        if hit != intervals[intervals.index(hit[0]):intervals.index(hit[-1])+1]: raise FiveStepLanguageError("semantic source span coverage is noncontiguous")
        pieces=[]; cursor=a
        for left,right,row in hit:
            left,right=max(left,a),min(right,b)
            if left<cursor: raise FiveStepLanguageError("semantic source span coverage overlaps")
            pieces.append(text[cursor:left]);pieces.append(text[left:right]);cursor=right
        pieces.append(text[cursor:b])
        if "".join(pieces)!=text[a:b]: raise FiveStepLanguageError("semantic source span coverage is incomplete")
        first_left,first_right,first=hit[0]; last_left,last_right,last=hit[-1]
        start_offset=0; end_offset=len(last["ru_text"])
        if a!=first_left:
            source_prefix=text[first_left:a]
            if not _line_edge(text,a): raise FiveStepLanguageError("semantic partial start is not a source line edge")
            if _image_only(source_prefix):
                source_classes,source_images=_line_topology(text[first_left:first_right]);ru_classes,ru_images=_line_topology(first["ru_text"])
                if source_classes!=ru_classes or source_images!=ru_images: raise FiveStepLanguageError("semantic partial start RU line topology mismatch")
            elif not _reviewed_span_boundary(span) or not _same_line_correspondence(text[first_left:first_right],first["ru_text"]): raise FiveStepLanguageError("semantic partial start RU whole-line correspondence mismatch")
            start_offset=_line_offset(first["ru_text"],len(text[first_left:a].splitlines())+1,end=False)
        if b!=last_right:
            source_suffix=text[b:last_right]
            if not _line_edge(text,b): raise FiveStepLanguageError("semantic partial end is not a source line edge")
            if _image_only(source_suffix):
                source_classes,source_images=_line_topology(text[last_left:last_right]);ru_classes,ru_images=_line_topology(last["ru_text"])
                if source_classes!=ru_classes or source_images!=ru_images: raise FiveStepLanguageError("semantic partial end RU line topology mismatch")
            elif not _reviewed_span_boundary(span) or not _same_line_correspondence(text[last_left:last_right],last["ru_text"]): raise FiveStepLanguageError("semantic partial end RU whole-line correspondence mismatch")
            end_offset=_line_offset(last["ru_text"],len(text[last_left:b].splitlines()),end=True)
        output.append({"span_id":span["id"],"semantic_kind":"statblock","source_span_id":span["id"],"unit_ids":[r["unit_id"] for _,_,r in hit],"start":{"unit_id":first["unit_id"],"char_offset":start_offset},"end":{"unit_id":last["unit_id"],"char_offset":end_offset},"source_sha256":span["sha256"]})
    return output
def _collapsed_whitespace(text:str)->str:
    return " ".join(text.split())

def _declared_plain_prose_reflow(row:dict[str,Any])->bool:
    """Permit an explicit reviewed wrap cleanup while retaining markup checks."""
    predecessor=row.get("predecessor_final_ru_text"); reason=str(row.get("reason") or "").lower()
    if not isinstance(predecessor,str) or not any(token in reason for token in ("reflow","перенос")):
        return False
    texts=(row["source_text"],predecessor,row["ru_text"])
    return all(text.strip() and all(_line_class(line)=="text" for line in text.splitlines()) for text in texts) and _collapsed_whitespace(predecessor)==_collapsed_whitespace(row["ru_text"])

def _verified_reflow_texts(submission:dict[str,Any], expected:list[dict[str,Any]])->dict[str,str]:
    authority=submission.get("reflow_authority")
    if authority is None:return {}
    if not isinstance(authority,dict) or authority.get("schema")!="kb_creator.five_step_reflow_authority.v1" or set(authority)!={"schema","predecessor_submission","rows"}:raise FiveStepLanguageError("invalid reflow authority")
    predecessor=authority["predecessor_submission"]
    if not isinstance(predecessor,dict):raise FiveStepLanguageError("reflow predecessor submission is invalid")
    _seal_ok(predecessor,"submission_sha256","kb_creator.five_step_language_proofread_submission.v2")
    old={row.get("unit_id"):row for row in predecessor.get("units",[]) if isinstance(row,dict)}; current={row.get("unit_id"):row for row in submission.get("units",[]) if isinstance(row,dict)}; exp={row["unit_id"]:row for row in expected}; result={}
    if not isinstance(authority["rows"],list):raise FiveStepLanguageError("reflow authority rows are invalid")
    for item in authority["rows"]:
        unit_id=item.get("unit_id") if isinstance(item,dict) else None; before=old.get(unit_id); after=current.get(unit_id); source=exp.get(unit_id)
        if not isinstance(before,dict) or not isinstance(after,dict) or not isinstance(source,dict) or any(before.get(k)!=source[k] or after.get(k)!=source[k] for k in ("unit_id","source_hash","draft_ru_sha256")):raise FiveStepLanguageError("reflow authority unit binding mismatch")
        before_text=before.get("final_ru_text");after_text=after.get("final_ru_text")
        if not isinstance(before_text,str) or not isinstance(after_text,str) or _collapsed_whitespace(before_text)!=_collapsed_whitespace(after_text):raise FiveStepLanguageError("reflow authority text mismatch")
        result[unit_id]=before_text
    return result

def _mechanics(rows:list[dict[str,Any]],glossary:Path,unit_context:dict[str,dict[str,Any]]|None=None)->list[dict[str,Any]]:
    findings=[]; terms=_terms(glossary); authorized_skills=tuple(str(term["source"]) for term in terms if term.get("domain")=="skill")
    known_sources={legacy._normalize_term(str(term["source"])) for term in terms}
    for row in rows:
        if legacy._structure_signature(row["source_text"])!=legacy._structure_signature(row["ru_text"]) and not _declared_plain_prose_reflow(row):findings.append({"code":"markdown_or_mechanics_drift","unit_id":row["unit_id"]})
        for term in terms:
            if not legacy._term_present(term["source"],row["source_text"]):continue
            context=(unit_context or {}).get(row["unit_id"])
            if unit_context is not None and context is None:
                findings.append({"code":"source_unit_context_missing","unit_id":row["unit_id"]});continue
            labels=[cell.strip() for line in row["source_text"].splitlines() if line.lstrip().startswith("|") for cell in line.strip().strip("|").split("|")]
            label_value=re.compile(rf"^\s*{re.escape(str(term['source']))}\s*:?\s*(?:\d+(?:[.,]\d+)?%?|[-—?])\s*$",re.I)
            longer=next((cell for cell in labels if term["source"].casefold()!=cell.casefold() and term["source"].casefold() in cell.casefold() and not label_value.fullmatch(cell)),None)
            if longer:
                # A separately registered maximal phrase owns its occurrence.  A
                # shorter source term remains checked when it appears as its own cell.
                if legacy._normalize_term(longer) not in known_sources:
                    findings.append({"code":"terminology_source_phrase_review","unit_id":row["unit_id"],"source":term["source"],"source_phrase":longer})
                continue
            term=legacy._contextual_term(term,row["source_text"])
            predecessor=(context or {}).get("predecessor") or {}
            c=legacy._term_context(term,row["source_text"],authorized_skills=authorized_skills,
                                   predecessor_text=str(predecessor.get("text") or "")); required=c["applicability"] in {"required_general","required_skill"}
            if c["applicability"]=="ambiguous":findings.append({"code":"terminology_context_ambiguous","unit_id":row["unit_id"],"source":term["source"]})
            elif required and not any(legacy._term_present(x,row["ru_text"]) for x in term["targets"]):findings.append({"code":"terminology_target_missing","unit_id":row["unit_id"],"source":term["source"]})
            if required:
                for bad in term["bad"]:
                    if legacy._bad_variant_present(bad,term["targets"],row["ru_text"]):findings.append({"code":"terminology_bad_variant","unit_id":row["unit_id"],"source":term["source"],"bad":bad})
    return findings

def prepare_language(master_en:Path,glossary:Path,output_root:Path,*,max_batch_chars:int=3000)->dict:
    master_en,glossary,output_root=master_en.resolve(),glossary.resolve(),output_root.resolve()
    if not master_en.is_file() or not glossary.is_file():raise FiveStepLanguageError("MASTER_EN and glossary must be files")
    terms=_terms(glossary); span_path,span_value=_source_spans(master_en); rows,batches=_units(master_en,max_batch_chars); instructions=["Create a faithful documentary Russian draft for every ordered unit.","Do not omit, summarize, invent facts, or alter source fields.","Preserve Markdown, links, source markers, numbers, dice, and selected glossary terms."]
    terminology_context=_terminology_context(glossary)
    if terminology_context:
        instructions.append("Use the source-cited definitions, scope and decision status in LANGUAGE_INPUT.json and the bound glossary. review_required entries are context, not automatic substitutions. Preserve source-edition mechanics.")
    def build(s:Path):
        br=[]
        for i,b in enumerate(batches,1):
            p=s/"draft.batches"/f"batch-{i:04d}.json";_write(p,{"schema":"kb_creator.five_step_language_draft_batch.v1","batch_id":f"batch-{i:04d}","units":[_unit(x) for x in b]});br.append({"batch_id":f"batch-{i:04d}","input":_id(p,s),"unit_ids":[x["unit_id"] for x in b]})
        scenario=master_en.parent.name
        for c in master_en.parent.glob("*.json"):
            try: scenario=_read(c).get("scenario_id",scenario)
            except FiveStepLanguageError:pass
        task=_seal("kb_creator.five_step_language_draft_task.v3",{"scenario_id":scenario,"master_en":_id(master_en,master_en.parent),"glossary":_id(glossary,glossary.parent),"source_spans":_id(span_path,master_en.parent),"master_en_path":str(master_en),"glossary_path":str(glossary),"source_spans_path":str(span_path),"instructions":instructions,"instruction_sha256":_sha(_canonical(instructions)),"units":[_unit(x) for x in rows],"source_unit_context":derive_unit_context(master_en.read_text(encoding="utf-8"),max_batch_chars),"batches":br,"question_queue":[],"max_batch_chars":max_batch_chars},"task_sha256")
        _write(s/"draft.task.json",task);_write(s/"draft.template.json",{"schema":"kb_creator.five_step_language_draft_submission.v2","task":_id(s/"draft.task.json",s),"master_en":task["master_en"],"glossary":task["glossary"],"units":[{"unit_id":x["unit_id"],"source_hash":x["source_hash"],"ru_text":"","unresolved":[]} for x in task["units"]]});_write(s/"LANGUAGE_INPUT.json",{"schema":"kb_creator.five_step_language_input.v1","master_en":task["master_en"],"glossary":task["glossary"],"terms":[{"source":x["source"],"target":x["target"]} for x in terms],**({"terminology_context":terminology_context} if terminology_context else {})})
    _atomic(output_root,build);return {"state":"needs_agent_work","reason_code":"documentary_draft_required","task_path":output_root/"draft.task.json","template_path":output_root/"draft.template.json"}

def _draft_rows(task:dict,task_id:dict,value:dict,glossary:Path,unit_context:dict[str,dict[str,Any]]|None=None)->list[dict]:
    _seal_ok(value,"submission_sha256","kb_creator.five_step_language_draft_submission.v2",optional=True)
    if value.get("task")!=task_id or value.get("master_en")!=task["master_en"] or value.get("glossary")!=task["glossary"]:raise FiveStepLanguageError("draft authority identity mismatch")
    expected=task.get("units");actual=value.get("units")
    if not isinstance(expected,list) or not isinstance(actual,list) or len(expected)!=len(actual):raise FiveStepLanguageError("draft unit coverage mismatch")
    out=[]
    for e,a in zip(expected,actual):
        if not isinstance(a,dict) or a.get("unit_id")!=e["unit_id"] or a.get("source_hash")!=e["source_hash"] or not isinstance(a.get("ru_text"),str) or not a["ru_text"].strip() or not isinstance(a.get("unresolved"),list):raise FiveStepLanguageError("draft unit order, identity, or completion mismatch")
        if a["unresolved"]:raise FiveStepLanguageError("draft unresolved questions must be resolved before proofreading")
        out.append({**e,"ru_text":a["ru_text"].strip(),"unresolved":[]})
    f=_mechanics(out,glossary,unit_context)
    if f:raise FiveStepLanguageError(f"draft mechanical QA blocked: {f}")
    return out

def submit_draft(language_root:Path,submission:Path,output_root:Path)->dict:
    language_root,submission,output_root=language_root.resolve(),submission.resolve(),output_root.resolve();tp=language_root/"draft.task.json";task=_read(tp);_task_schema(task);_seal_ok(task,"task_sha256",task["schema"]);master,glossary=_source(task,"master_en"),_source(task,"glossary");span_path,span_value=_source_spans(master);unit_context=_verified_unit_context(task,master)
    if task.get("source_spans")!={"path":"EN_SOURCE_SPANS.json","bytes":span_path.stat().st_size,"sha256":_fsha(span_path)}:raise FiveStepLanguageError("draft source-span authority mismatch")
    supplied=_read(submission);rows=_draft_rows(task,_id(tp,language_root),supplied,glossary,unit_context)
    def build(s:Path):
        ev=s/"evidence";ev.mkdir();shutil.copyfile(master,ev/"MASTER_EN.md");shutil.copyfile(glossary,ev/"glossary");shutil.copyfile(span_path,ev/"EN_SOURCE_SPANS.json");_write(ev/"draft.task.json",task);_write(ev/"draft.submission.json",_seal("kb_creator.five_step_language_draft_submission.v2",{k:v for k,v in supplied.items() if k!="submission_sha256"},"submission_sha256"))
        draft=_seal("kb_creator.five_step_documentary_draft.v2",{"task":_id(ev/"draft.task.json",s),"submission":_id(ev/"draft.submission.json",s),"master_en":task["master_en"],"glossary":task["glossary"],"units":rows,"mechanical_findings":[]},"draft_sha256");_write(s/"documentary_draft.json",draft)
        pu=[{"unit_id":x["unit_id"],"source_hash":x["source_hash"],"source_text":x["source_text"],"parent_unit_id":x.get("parent_unit_id"),"part_index":x.get("part_index"),"part_count":x.get("part_count"),"draft_ru_text":x["ru_text"],"draft_ru_sha256":_sha(x["ru_text"].encode())} for x in rows]; inst=["Compare final Russian against exact English source and documentary draft.","Perform an explicit literary and source-fidelity check.","Select changed or checked_unchanged; unresolved blocks MASTER_RU."]
        proof=_seal("kb_creator.five_step_language_proofread_task.v2",{"language_task":_id(ev/"draft.task.json",s),"draft":_id(s/"documentary_draft.json",s),"master_en":task["master_en"],"glossary":task["glossary"],"instructions":inst,"instruction_sha256":_sha(_canonical(inst)),"units":pu,"question_queue":[]},"task_sha256");_write(s/"proofread.task.json",proof);_write(s/"proofread.template.json",{"schema":"kb_creator.five_step_language_proofread_submission.v2","task":_id(s/"proofread.task.json",s),"draft":proof["draft"],"master_en":task["master_en"],"glossary":task["glossary"],"units":[{"unit_id":x["unit_id"],"source_hash":x["source_hash"],"draft_ru_sha256":x["draft_ru_sha256"],"final_ru_text":x["draft_ru_text"],"disposition":"pending","reason":"","unresolved":[]} for x in pu]})
    _atomic(output_root,build);return {"state":"needs_agent_work","reason_code":"proofread_required","task_path":output_root/"proofread.task.json","template_path":output_root/"proofread.template.json","draft_path":output_root/"documentary_draft.json"}

def _assemble(rows:list[dict])->str:
    return _assemble_map(rows)["text"]
def _copy_context(master:Path,s:Path)->list[dict]:
    refs=legacy._structure_signature(master.read_text(encoding="utf-8"))["image_targets"];assets=[]
    for ref in dict.fromkeys(refs):
        rel=Path(ref); src=(master.parent/rel).resolve()
        if rel.is_absolute() or ".." in rel.parts or not src.is_file() or src.is_symlink():raise FiveStepLanguageError(f"MASTER_EN referenced asset missing/reparse: {ref}")
        try:src.relative_to(master.parent.resolve())
        except ValueError as e:raise FiveStepLanguageError("MASTER_EN asset escapes candidate") from e
        dst=s/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assets.append(_id(dst,s))
    sem=s/"semantic_context"; source=master.parent/"semantic_context"
    if source.is_dir():
        for p in source.rglob("*"):
            if p.is_symlink() or bool(getattr(os.lstat(p),"st_file_attributes",0)&getattr(stat,"FILE_ATTRIBUTE_REPARSE_POINT",0x400)):raise FiveStepLanguageError("semantic context reparse path")
            if p.is_file():d=sem/p.relative_to(source);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
    for p in master.parent.glob("*.json"):
        if p.is_symlink():raise FiveStepLanguageError("MASTER_EN sidecar reparse path")
        sem.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,sem/p.name)
    return assets

def submit_proofread(language_root:Path,draft_root:Path,submission:Path,output_root:Path)->dict:
    language_root,draft_root,submission,output_root=(x.resolve() for x in (language_root,draft_root,submission,output_root));ltp=language_root/"draft.task.json";lt=_read(ltp);_task_schema(lt);_seal_ok(lt,"task_sha256",lt["schema"])
    dp,pp=draft_root/"documentary_draft.json",draft_root/"proofread.task.json";draft,proof=_read(dp),_read(pp);_seal_ok(draft,"draft_sha256","kb_creator.five_step_documentary_draft.v2");_seal_ok(proof,"task_sha256","kb_creator.five_step_language_proofread_task.v2")
    # Actual roots, not producer-provided paths, bind this transition.
    if draft.get("task")!={"path":"evidence/draft.task.json","bytes":(draft_root/"evidence"/"draft.task.json").stat().st_size,"sha256":_fsha(draft_root/"evidence"/"draft.task.json")} or proof.get("language_task")!={"path":"evidence/draft.task.json","bytes":(draft_root/"evidence"/"draft.task.json").stat().st_size,"sha256":_fsha(draft_root/"evidence"/"draft.task.json")} or proof.get("draft")!=_id(dp,draft_root):raise FiveStepLanguageError("draft/proofread task does not bind supplied language root")
    # The archived language task must equal the currently supplied task, including source identities.
    archived_task=_read(draft_root/"evidence"/"draft.task.json")
    if archived_task!=lt:raise FiveStepLanguageError("draft task differs from supplied language root")
    supplied=_read(submission);_seal_ok(supplied,"submission_sha256","kb_creator.five_step_language_proofread_submission.v2",optional=True)
    if supplied.get("task")!=_id(pp,draft_root) or supplied.get("draft")!=proof["draft"] or supplied.get("master_en")!=lt["master_en"] or supplied.get("glossary")!=lt["glossary"]:raise FiveStepLanguageError("proofread authority identity mismatch")
    expected,actual=proof.get("units"),supplied.get("units")
    if not isinstance(expected,list) or not isinstance(actual,list) or len(expected)!=len(actual):raise FiveStepLanguageError("proofread full ordered unit coverage required")
    reflow_texts=_verified_reflow_texts(supplied,expected);final=[];ledger=[]
    for e,a in zip(expected,actual):
        if not isinstance(a,dict) or any(a.get(k)!=e[k] for k in ("unit_id","source_hash","draft_ru_sha256")):raise FiveStepLanguageError("proofread unit identity/order mismatch")
        text=a.get("final_ru_text");changed=isinstance(text,str) and _sha(text.strip().encode())!=e["draft_ru_sha256"]
        if not isinstance(text,str) or not text.strip() or a.get("disposition") not in {"changed","checked_unchanged"} or not isinstance(a.get("reason"),str) or not isinstance(a.get("unresolved"),list):raise FiveStepLanguageError("proofread unit remains pending or malformed")
        if a["unresolved"]:raise FiveStepLanguageError("unresolved proofreading questions block MASTER_RU")
        if (a["disposition"]=="changed")!=changed or (changed and not a["reason"].strip()) or (not changed and a["reason"]):raise FiveStepLanguageError("proofread disposition/reason is not truthful")
        final.append({"unit_id":e["unit_id"],"source_hash":e["source_hash"],"source_text":e["source_text"],"parent_unit_id":e.get("parent_unit_id"),"part_index":e.get("part_index"),"part_count":e.get("part_count"),"predecessor_final_ru_text":reflow_texts.get(e["unit_id"]),"reason":a["reason"],"ru_text":text.strip()});ledger.append({"unit_id":e["unit_id"],"draft_ru_sha256":e["draft_ru_sha256"],"final_ru_sha256":_sha(text.strip().encode()),"disposition":a["disposition"],"reason":a["reason"]})
    if [x["unit_id"] for x in final] != [x["unit_id"] for x in draft.get("units",[])]:raise FiveStepLanguageError("proofread units do not match sealed draft")
    master,glossary=_source(lt,"master_en"),_source(lt,"glossary");unit_context=_verified_unit_context(lt,master);span_path,span_value=_source_spans(master)
    if lt.get("source_spans")!={"path":"EN_SOURCE_SPANS.json","bytes":span_path.stat().st_size,"sha256":_fsha(span_path)}:raise FiveStepLanguageError("proofread source-span authority mismatch")
    semantic_spans=_project_spans(master,final,span_value)
    assembly=_assemble_map(final)
    for span in semantic_spans:
        start=_semantic_edge(assembly,span["start"]["unit_id"],span["start"]["char_offset"],edge="start")
        end=_semantic_edge(assembly,span["end"]["unit_id"],span["end"]["char_offset"],edge="end")
        if not 0 <= start < end <= len(assembly["text"]) or (start and assembly["text"][start-1]!="\n") or (end<len(assembly["text"]) and assembly["text"][end]!="\n"):raise FiveStepLanguageError("semantic RU span is not line-boundary aligned")
    findings=_mechanics(final,glossary,unit_context)
    if findings:raise FiveStepLanguageError(f"proofread mechanical QA blocked: {findings}")
    def build(s:Path):
        (s/"MASTER_RU.md").write_text(_assemble(final),encoding="utf-8",newline="\n");assets=_copy_context(master,s);_write(s/"ASSET_MANIFEST.json",_seal("kb_creator.five_step_asset_manifest.v1",{"assets":assets},"manifest_sha256"))
        ev=s/"evidence";ev.mkdir();
        for src,name in ((master,"MASTER_EN.md"),(glossary,"glossary"+glossary.suffix),(span_path,"EN_SOURCE_SPANS.json"),(draft_root/"evidence"/"draft.task.json","draft.task.json"),(draft_root/"evidence"/"draft.submission.json","draft.submission.json"),(dp,"documentary_draft.json"),(pp,"proofread.task.json")):shutil.copyfile(src,ev/name)
        _write(ev/"proofread.submission.json",_seal("kb_creator.five_step_language_proofread_submission.v2",{k:v for k,v in supplied.items() if k!="submission_sha256"},"submission_sha256"))
        # Semantic spans are supplied only by reviewed SEMANTIC_STRUCTURE authority;
        # vocabulary in prose never classifies a statblock.
        projection=_seal("kb_creator.five_step_ru_projection.v3",{"master_en":_id(ev/"MASTER_EN.md",s),"master_ru":_id(s/"MASTER_RU.md",s),"source_spans":_id(ev/"EN_SOURCE_SPANS.json",s),"unit_order":[x["unit_id"] for x in final],"units":[{"unit_id":x["unit_id"],"source_hash":x["source_hash"],"parent_unit_id":x.get("parent_unit_id"),"part_index":x.get("part_index"),"part_count":x.get("part_count"),"ru_text":x["ru_text"],"ru_sha256":_sha(x["ru_text"].encode())} for x in final],"spans":semantic_spans},"projection_sha256");_write(s/"semantic_context"/"RU_PROJECTION.json",projection)
        review=_seal("kb_creator.five_step_proofread_ledger.v2",{"proofread_task":_id(ev/"proofread.task.json",s),"submission":_id(ev/"proofread.submission.json",s),"units":ledger,"unresolved":[],"state":"closed"},"ledger_sha256");_write(s/"PROOFREAD_LEDGER.json",review)
        manifest=_seal("kb_creator.five_step_master_ru_manifest.v2",{"master_en":_id(ev/"MASTER_EN.md",s),"glossary":_id(ev/("glossary"+glossary.suffix),s),"draft":_id(ev/"documentary_draft.json",s),"language_task":_id(ev/"draft.task.json",s),"proofread_task":_id(ev/"proofread.task.json",s),"proofread_submission":_id(ev/"proofread.submission.json",s),"master_ru":_id(s/"MASTER_RU.md",s),"unit_order":[x["unit_id"] for x in final],"mechanical_findings":[],"review_ledger":_id(s/"PROOFREAD_LEDGER.json",s),"ru_projection":_id(s/"semantic_context"/"RU_PROJECTION.json",s),"asset_manifest":_id(s/"ASSET_MANIFEST.json",s)},"manifest_sha256");_write(s/"MASTER_RU.manifest.json",manifest)
        files=[_id(p,s) for p in sorted((x for x in s.rglob("*") if x.is_file()),key=lambda x:x.relative_to(s).as_posix())];_write(s/"INVENTORY.json",_seal("kb_creator.five_step_language_inventory.v2",{"files":files},"inventory_sha256"))
    _atomic(output_root,build);return {"state":"verified","reason_code":"proofread_complete","master_ru":output_root/"MASTER_RU.md","manifest_path":output_root/"MASTER_RU.manifest.json","review_path":output_root/"PROOFREAD_LEDGER.json"}

def _resolve(root:Path,r:object,label:str)->Path:
    if not isinstance(r,dict) or set(r)!={"path","bytes","sha256"}:raise FiveStepLanguageError(f"invalid {label} identity")
    p=(root/str(r["path"])).resolve()
    try:p.relative_to(root.resolve())
    except ValueError as e:raise FiveStepLanguageError(f"{label} escapes result") from e
    if not p.is_file() or p.stat().st_size!=r["bytes"] or _fsha(p)!=r["sha256"]:raise FiveStepLanguageError(f"{label} identity mismatch")
    return p
def verify_language_result(result_root:Path)->dict:
    root=result_root.resolve();manifest=_read(root/"MASTER_RU.manifest.json");_seal_ok(manifest,"manifest_sha256","kb_creator.five_step_master_ru_manifest.v2")
    master,glossary=_resolve(root,manifest["master_en"],"archived MASTER_EN"),_resolve(root,manifest["glossary"],"archived glossary");tp=_resolve(root,manifest["language_task"],"archived language task");task=_read(tp);_task_schema(task);_seal_ok(task,"task_sha256",task["schema"]);unit_context=_verified_unit_context(task,master)
    fresh,_=_units(master,task["max_batch_chars"])
    if [_unit(x) for x in fresh]!=task.get("units"):raise FiveStepLanguageError("archived task source binding mismatch")
    dsp=root/"evidence"/"draft.submission.json";ds=_read(dsp);_seal_ok(ds,"submission_sha256","kb_creator.five_step_language_draft_submission.v2")
    def relocated(record,expected,original_path):return isinstance(record,dict) and set(record)=={"path","bytes","sha256"} and record.get("path")==original_path and record.get("bytes")==expected["bytes"] and record.get("sha256")==expected["sha256"]
    # Archive relocation is closed: only source-root task references become
    # evidence/draft.task.json; source/glossary identities remain byte-exact.
    if not relocated(ds.get("task"),_id(tp,root),"draft.task.json") or ds.get("master_en")!=task.get("master_en") or ds.get("glossary")!=task.get("glossary"):raise FiveStepLanguageError("archived draft submission relocation mismatch")
    archived_task=dict(task);verify_ds={k:v for k,v in ds.items() if k!="submission_sha256"};verify_ds["task"]=_id(tp,root);draft_rows=_draft_rows(archived_task,_id(tp,root),verify_ds,glossary,unit_context)
    dp=_resolve(root,manifest["draft"],"archived draft");draft=_read(dp);_seal_ok(draft,"draft_sha256","kb_creator.five_step_documentary_draft.v2")
    if draft.get("task")!=_id(tp,root) or draft.get("units")!=draft_rows:raise FiveStepLanguageError("archived draft binding mismatch")
    pp=_resolve(root,manifest["proofread_task"],"archived proofread task");proof=_read(pp);_seal_ok(proof,"task_sha256","kb_creator.five_step_language_proofread_task.v2")
    fp=_resolve(root,manifest["proofread_submission"],"archived proofread submission");final=_read(fp);_seal_ok(final,"submission_sha256","kb_creator.five_step_language_proofread_submission.v2")
    expected_proof_units=[{"unit_id":x["unit_id"],"source_hash":x["source_hash"],"source_text":x["source_text"],"parent_unit_id":x.get("parent_unit_id"),"part_index":x.get("part_index"),"part_count":x.get("part_count"),"draft_ru_text":x["ru_text"],"draft_ru_sha256":_sha(x["ru_text"].encode())} for x in draft_rows]
    if proof.get("language_task")!=_id(tp,root) or not relocated(proof.get("draft"),_id(dp,root),"documentary_draft.json") or proof.get("master_en")!=task.get("master_en") or proof.get("glossary")!=task.get("glossary") or proof.get("units")!=expected_proof_units or not relocated(final.get("task"),_id(pp,root),"proofread.task.json") or not relocated(final.get("draft"),proof["draft"],"documentary_draft.json") or final.get("master_en")!=task.get("master_en") or final.get("glossary")!=task.get("glossary"):raise FiveStepLanguageError("archived proofread binding mismatch")
    reflow_texts=_verified_reflow_texts(final,proof["units"]);rows=[];ledger=[]
    if not isinstance(final.get("units"),list) or len(final["units"])!=len(proof.get("units",[])):raise FiveStepLanguageError("archived final coverage mismatch")
    for e,a in zip(proof["units"],final["units"]):
        text=a.get("final_ru_text") if isinstance(a,dict) else None;changed=isinstance(text,str) and _sha(text.strip().encode())!=e["draft_ru_sha256"]
        if not isinstance(a,dict) or any(a.get(k)!=e[k] for k in ("unit_id","source_hash","draft_ru_sha256")) or not isinstance(text,str) or not text.strip() or a.get("unresolved")!=[] or a.get("disposition") not in {"changed","checked_unchanged"} or (a["disposition"]=="changed")!=changed or (changed and not str(a.get("reason") or "").strip()) or (not changed and a.get("reason")!=""):raise FiveStepLanguageError("archived final review state invalid")
        rows.append({"unit_id":e["unit_id"],"source_hash":e["source_hash"],"source_text":e["source_text"],"parent_unit_id":e.get("parent_unit_id"),"part_index":e.get("part_index"),"part_count":e.get("part_count"),"predecessor_final_ru_text":reflow_texts.get(e["unit_id"]),"reason":a["reason"],"ru_text":text.strip()});ledger.append({"unit_id":e["unit_id"],"draft_ru_sha256":e["draft_ru_sha256"],"final_ru_sha256":_sha(text.strip().encode()),"disposition":a["disposition"],"reason":a["reason"]})
    if _mechanics(rows,glossary,unit_context):raise FiveStepLanguageError("archived mechanical QA blocked")
    mr=_resolve(root,manifest["master_ru"],"MASTER_RU")
    if mr.read_text(encoding="utf-8")!=_assemble(rows):raise FiveStepLanguageError("MASTER_RU assembly mismatch")
    lp=_resolve(root,manifest["review_ledger"],"ledger");l=_read(lp);_seal_ok(l,"ledger_sha256","kb_creator.five_step_proofread_ledger.v2")
    if l.get("units")!=ledger or l.get("state")!="closed" or l.get("unresolved")!=[]:raise FiveStepLanguageError("proofread ledger mismatch")
    proj=_read(_resolve(root,manifest["ru_projection"],"RU projection"));_seal_ok(proj,"projection_sha256","kb_creator.five_step_ru_projection.v3")
    if proj.get("unit_order")!=manifest.get("unit_order") or proj.get("master_ru")!=_id(mr,root):raise FiveStepLanguageError("RU projection mismatch")
    archived_spans_path=root/"evidence"/"EN_SOURCE_SPANS.json";archived_spans=_read(archived_spans_path);_seal_ok(archived_spans,"spans_sha256","kb_creator.five_step_en_source_spans.v1")
    expected_spans=_project_spans(master,rows,archived_spans);assembly=_assemble_map(rows)
    for span in expected_spans:
        start=_semantic_edge(assembly,span["start"]["unit_id"],span["start"]["char_offset"],edge="start");end=_semantic_edge(assembly,span["end"]["unit_id"],span["end"]["char_offset"],edge="end")
        if not 0 <= start < end <= len(assembly["text"]) or (start and assembly["text"][start-1]!="\n") or (end<len(assembly["text"]) and assembly["text"][end]!="\n"):raise FiveStepLanguageError("semantic RU span is not line-boundary aligned")
    expected_units=[{"unit_id":x["unit_id"],"source_hash":x["source_hash"],"parent_unit_id":x.get("parent_unit_id"),"part_index":x.get("part_index"),"part_count":x.get("part_count"),"ru_text":x["ru_text"],"ru_sha256":_sha(x["ru_text"].encode())} for x in rows]
    if proj.get("source_spans")!=_id(archived_spans_path,root) or proj.get("units")!=expected_units or proj.get("spans")!=expected_spans:raise FiveStepLanguageError("RU semantic span projection mismatch")
    am=_read(_resolve(root,manifest["asset_manifest"],"asset manifest"));_seal_ok(am,"manifest_sha256","kb_creator.five_step_asset_manifest.v1")
    for ref in legacy._structure_signature(master.read_text(encoding="utf-8"))["image_targets"]:
        p=root/ref
        if not p.is_file() or p.is_symlink():raise FiveStepLanguageError("referenced asset missing/reparse")
    inv=_read(root/"INVENTORY.json");_seal_ok(inv,"inventory_sha256","kb_creator.five_step_language_inventory.v2");obs=[_id(p,root) for p in sorted((x for x in root.rglob("*") if x.is_file() and x != root/"INVENTORY.json"),key=lambda x:x.relative_to(root).as_posix())]
    if inv.get("files")!=obs:raise FiveStepLanguageError("result byte inventory mismatch")
    return {"state":"verified","master_ru":_id(mr,root),"manifest_path":root/"MASTER_RU.manifest.json","review_path":lp}
