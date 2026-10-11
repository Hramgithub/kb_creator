import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from kb_creator.scripts.snapshot_working_data import (
    main, snapshot, verify_or_restore,
)


def write_file(root, relative, data=b'exact payload'):
    path=root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    return path


def manifest(archive):
    with zipfile.ZipFile(archive) as handle:
        return json.loads(handle.read('manifest.json'))


def test_exact_files_roundtrip_and_content_deduplication(tmp_path):
    root=tmp_path/'source'
    payloads={
        'drivers/recover.ps1':b'Write-Output "recover"\r\n',
        'review/document.docx':b'PK\x03\x04\x00\xff',
        'review/derived.pdf':b'%PDF-1.7\x00\xff',
        'renders/page001.png':b'\x89PNG\r\n\x1a\n\x00\xff',
        'renders/duplicate.png':b'\x89PNG\r\n\x1a\n\x00\xff',
        'unusual/payload.dat':b'\x00\xff\xfe',
    }
    for relative,data in payloads.items():
        write_file(root,relative,data)
    write_file(root,'unselected.md')
    paths=list(payloads)+['drivers/recover.ps1',root/'review/document.docx']
    archive=tmp_path/'snapshot.zip'
    result=snapshot(root,paths,archive,exact_files=True)
    assert result['files']==6 and result['objects']==5
    recorded=manifest(archive)
    assert recorded['selection_mode']=='exact-files'
    assert [row['path'] for row in recorded['files']]==sorted(payloads)
    assert verify_or_restore(archive)=={'verified_files':6,'verified_objects':5}
    destination=tmp_path/'restored'
    verify_or_restore(archive,destination)
    assert {path.relative_to(destination).as_posix():path.read_bytes()
            for path in destination.rglob('*') if path.is_file()}==payloads
    assert verify_or_restore(archive,destination)['verified_files']==6
    changed=write_file(destination,'drivers/recover.ps1',b'user edits')
    with pytest.raises(ValueError,match='Refusing overwrite'):
        verify_or_restore(archive,destination)
    assert changed.read_bytes()==b'user edits'


def test_default_directory_selection_keeps_legacy_filter(tmp_path):
    root=tmp_path/'source'
    accepted=['notes.md','script.py','source.pdf','assets/figure.png']
    excluded=['script.ps1','document.docx','derived.pdf','renders/page.png',
              '__pycache__/cache.json','node_modules/package.json']
    for relative in accepted+excluded:
        write_file(root,relative)
    archive=tmp_path/'legacy.zip'
    snapshot(root,[Path('.')],archive)
    recorded=manifest(archive)
    assert recorded['selection_mode']=='legacy-filtered'
    assert [row['path'] for row in recorded['files']]==sorted(accepted)


@pytest.mark.parametrize('relative',[
    'working/night-three-books/n359-source-continuation-runtime-v01/code/verify.py',
    'reviewed/author-replay/source-authorship.json',
])
def test_exact_files_allow_frozen_project_runtime_code_and_author_replay(tmp_path,relative):
    root=tmp_path/'source'
    write_file(root,relative)
    archive=tmp_path/'snapshot.zip'
    assert snapshot(root,[relative],archive,exact_files=True)['files']==1
    assert manifest(archive)['files'][0]['path']==relative


@pytest.mark.parametrize('selection,error',[
    ('missing.docx',FileNotFoundError),
    ('directory',ValueError),
    ('../outside.docx',ValueError),
])
def test_exact_files_reject_invalid_selection_before_creating_archive(tmp_path,selection,error):
    root=tmp_path/'source'
    write_file(root,'valid.md')
    (root/'directory').mkdir()
    write_file(tmp_path,'outside.docx')
    archive=tmp_path/'snapshot.zip'
    with pytest.raises(error):
        snapshot(root,['valid.md',selection],archive,exact_files=True)
    assert not archive.exists()


def test_exact_files_reject_absolute_path_outside_root(tmp_path):
    root=tmp_path/'source'
    root.mkdir()
    outside=write_file(tmp_path,'outside.docx')
    archive=tmp_path/'snapshot.zip'
    with pytest.raises(ValueError,match='outside root'):
        snapshot(root,[outside],archive,exact_files=True)
    assert not archive.exists()


@pytest.mark.parametrize('directory_link',[False,True])
def test_exact_files_reject_symlinks_even_when_destination_is_inside_root(tmp_path,directory_link):
    root=tmp_path/'source'
    target=write_file(root,'real/document.docx')
    link=root/('linked-directory' if directory_link else 'linked.docx')
    try:
        link.symlink_to(target.parent if directory_link else target,
                        target_is_directory=directory_link)
    except (OSError,NotImplementedError) as error:
        pytest.skip('Symlink creation unavailable: '+str(error))
    selection=link/'document.docx' if directory_link else link
    archive=tmp_path/'snapshot.zip'
    with pytest.raises(ValueError,match='Linked snapshot selection'):
        snapshot(root,[selection],archive,exact_files=True)
    assert not archive.exists()


def test_exact_files_reject_windows_junction_inside_root(tmp_path):
    shell=shutil.which('powershell') or shutil.which('pwsh')
    if os.name!='nt' or not shell or not hasattr(Path,'is_junction'):
        pytest.skip('Windows junction support unavailable')
    root=tmp_path/'source'
    target=write_file(root,'real/document.docx')
    link=root/'linked-directory'
    quote=lambda path:"'"+str(path).replace("'","''")+"'"
    command=("$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path "
             +quote(link)+' -Target '+quote(target.parent)+' | Out-Null')
    created=subprocess.run([shell,'-NoProfile','-NonInteractive','-Command',command],
                           capture_output=True,text=True,timeout=30)
    if created.returncode:
        pytest.skip('Junction creation unavailable: '+created.stderr.strip())
    assert link.is_junction()
    archive=tmp_path/'snapshot.zip'
    with pytest.raises(ValueError,match='Linked snapshot selection'):
        snapshot(root,[link/'document.docx'],archive,exact_files=True)
    assert not archive.exists()


@pytest.mark.parametrize('relative',[
    '__pycache__/data.json','.PyTest_Cache/data.json','.venv/config.toml',
    'node_modules/package.json','.git/config','.tools/python/script.py',
    '.ssh/id_ed25519','.aws/config','.env','.env.local','credentials.json',
    'api-token.json','api_key.json','passwords.json','auth.json','private.key',
    'browser_profiles/state.json',
    'User Data/Default/state.json','profiles/state.json','transcripts/turn.jsonl',
    'cache/data.json','logs/job.txt','codex-runtimes/runtime.py',
    'models/model.safetensors','models/weights.pth','models/model.onnx',
    'model.bin','runtime.exe','runtime.dll',
])
def test_exact_files_reject_forbidden_selection(tmp_path,relative):
    root=tmp_path/'source'
    write_file(root,relative)
    archive=tmp_path/'snapshot.zip'
    with pytest.raises(ValueError,match='Forbidden snapshot selection'):
        snapshot(root,[relative],archive,exact_files=True)
    assert not archive.exists()


@pytest.mark.parametrize('paths',[[], 'file.md', {'path':'file.md'}])
def test_exact_files_require_nonempty_explicit_list(tmp_path,paths):
    root=tmp_path/'source'
    write_file(root,'file.md')
    with pytest.raises(ValueError,match='non-empty file list'):
        snapshot(root,paths,tmp_path/'snapshot.zip',exact_files=True)


def test_exact_snapshot_corrupt_object_cannot_be_restored(tmp_path):
    root=tmp_path/'source'
    write_file(root,'document.docx',b'original')
    archive=tmp_path/'snapshot.zip'
    snapshot(root,['document.docx'],archive,exact_files=True)
    recorded=manifest(archive)
    corrupt=tmp_path/'corrupt.zip'
    with zipfile.ZipFile(corrupt,'x') as handle:
        handle.writestr('manifest.json',json.dumps(recorded))
        handle.writestr('objects/'+recorded['files'][0]['sha256'],b'corrupt!')
    with pytest.raises(ValueError,match='Corrupt object'):
        verify_or_restore(corrupt)
    destination=tmp_path/'restored'
    with pytest.raises(ValueError,match='Corrupt object'):
        verify_or_restore(corrupt,destination)
    assert not destination.exists()


def test_cli_exact_files_flag(tmp_path,monkeypatch,capsys):
    root=tmp_path/'source'
    write_file(root,'recover.ps1')
    paths=tmp_path/'paths.json'
    paths.write_text(json.dumps(['recover.ps1']),encoding='utf-8')
    archive=tmp_path/'snapshot.zip'
    monkeypatch.setattr(sys,'argv',['snapshot_working_data.py','create',
        '--root',str(root),'--paths',str(paths),'--archive',str(archive),'--exact-files'])
    main()
    assert json.loads(capsys.readouterr().out)['files']==1
    assert manifest(archive)['selection_mode']=='exact-files'


@pytest.mark.parametrize('arguments',[
    ['create'], ['verify','--exact-files'], ['restore','--exact-files'],
])
def test_cli_rejects_inapplicable_or_missing_arguments(tmp_path,monkeypatch,arguments):
    monkeypatch.setattr(sys,'argv',['snapshot_working_data.py',*arguments,
        '--archive',str(tmp_path/'snapshot.zip')])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code==2
