"""Archive declared working data by content hash; verify or restore without overwrite."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def eligible(path):
    if any(p in {'__pycache__','.pytest_cache','.venv','node_modules','.git'} for p in path.parts):
        return False
    if path.suffix.lower() in {'.json','.md','.csv','.txt','.py','.toml','.yaml','.yml','.jpg','.jpeg','.webp'}:
        return True
    if path.suffix.lower()=='.pdf':
        return path.name.lower()=='source.pdf'
    return path.suffix.lower()=='.png' and 'assets' in path.parts


def exact_file(root, item):
    """Validate explicit selection before resolution can hide linked components."""
    requested=Path(item)
    if '..' in requested.parts:
        raise ValueError('Unsafe snapshot path: '+str(item))
    target=requested if requested.is_absolute() else root/requested
    try:
        relative=target.relative_to(root)
    except ValueError:
        raise ValueError('Snapshot path outside root: '+str(item)) from None
    blocked_parts={
        '__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.cache',
        '.venv','venv','node_modules','.git','.tools','.ssh','.aws','.azure',
        '.gnupg','cache','caches','logs','profiles','browser_profiles',
        'browser-profiles','user data','transcripts','codex-runtimes',
    }
    blocked_suffixes={
        '.pem','.key','.pfx','.p12','.p8','.jks','.keystore',
        '.safetensors','.pth','.pt','.onnx','.ckpt','.bin','.exe','.dll',
    }
    for part in relative.parts:
        name=part.lower()
        if (name in blocked_parts or name=='.env' or name.startswith('.env.')
            or re.search(r'(^|[._-])(credentials?|secrets?|tokens?|passwords?|auth)([._-]|$)',name)
            or re.search(r'(^|[._-])api[._-]?key([._-]|$)',name)
            or name in {'id_rsa','id_ed25519','id_ecdsa','id_dsa',
                        'login data','cookies','web data','local state'}):
            raise ValueError('Forbidden snapshot selection: '+str(item))
    if target.suffix.lower() in blocked_suffixes:
        raise ValueError('Forbidden snapshot selection: '+str(item))
    current=root
    for part in relative.parts:
        current=current/part
        if current.is_symlink() or getattr(current,'is_junction',lambda:False)():
            raise ValueError('Linked snapshot selection: '+str(item))
    target=target.resolve(strict=True)
    target.relative_to(root)
    if not target.is_file():
        raise ValueError('Exact snapshot selection must be a file: '+str(item))
    return target


def snapshot(root,paths,output,*,exact_files=False):
    root=root.resolve(strict=True)
    if exact_files and (not isinstance(paths,(list,tuple)) or not paths):
        raise ValueError('Exact snapshot selection requires a non-empty file list')
    selected={}
    for item in paths:
        if exact_files:
            path=exact_file(root,item)
            selected[path.relative_to(root).as_posix()]=path
            continue
        target=(root/item).resolve(strict=True)
        target.relative_to(root)
        for path in ([target] if target.is_file() else target.rglob('*')):
            if path.is_file() and eligible(path) and not path.is_symlink():
                selected[path.relative_to(root).as_posix()]=path
    output.parent.mkdir(parents=True,exist_ok=True)
    manifest=[];seen=set()
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as archive:
        for index,(relative,path) in enumerate(sorted(selected.items())):
            data=path.read_bytes(); sha=digest(data)
            if sha not in seen:
                archive.writestr('objects/'+sha,data);seen.add(sha)
            manifest.append(dict(path=relative,sha256=sha,bytes=len(data)))
            if index and index%3000==0:
                print(json.dumps(dict(files=index,unique_objects=len(seen))),flush=True)
        archive.writestr('manifest.json',json.dumps(dict(schema='nri.working_snapshot.v1',files=manifest,
            selection_mode='exact-files' if exact_files else 'legacy-filtered',
            exclusions=('Only explicitly selected files; caches, credentials, profiles, transcripts, '
                'runtimes and model weights excluded; no acceptance implied.' if exact_files else
                'Caches, logs, profiles, rendered PNG outside assets, derived PDFs; no acceptance implied.')),
            ensure_ascii=False))
    return dict(files=len(manifest),objects=len(seen),archive_bytes=output.stat().st_size)


def verify_or_restore(archive_path,root=None):
    with zipfile.ZipFile(archive_path) as archive:
        manifest=json.loads(archive.read('manifest.json'))
        seen=set()
        for row in manifest['files']:
            relative=Path(row['path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe snapshot path')
            if row['sha256'] not in seen or root is not None:
                data=archive.read('objects/'+row['sha256'])
                if digest(data)!=row['sha256'] or len(data)!=row['bytes']:
                    raise ValueError('Corrupt object: '+row['path'])
                seen.add(row['sha256'])
                if root is not None:
                    target=(root/relative).resolve()
                    target.relative_to(root.resolve())
                    if target.exists():
                        if digest(target.read_bytes())!=row['sha256']:
                            raise ValueError('Refusing overwrite: '+str(target))
                    else:
                        target.parent.mkdir(parents=True,exist_ok=True)
                        with target.open('xb') as handle:handle.write(data)
    return dict(verified_files=len(manifest['files']),verified_objects=len(seen))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['create','verify','restore'])
    parser.add_argument('--root',type=Path,default=Path.cwd())
    parser.add_argument('--paths',type=Path)
    parser.add_argument('--exact-files',action='store_true',
        help='Create from an explicit file list, bypassing the legacy extension filter.')
    parser.add_argument('--archive',type=Path,required=True)
    args=parser.parse_args()
    if args.exact_files and args.mode!='create':
        parser.error('--exact-files is only valid in create mode')
    if args.mode=='create':
        if args.paths is None:
            parser.error('create requires --paths')
        paths=json.loads(args.paths.read_text(encoding='utf-8'))
        value=snapshot(args.root,paths,args.archive,exact_files=args.exact_files)
    else:value=verify_or_restore(args.archive,args.root if args.mode=='restore' else None)
    print(json.dumps(value),flush=True)


if __name__=='__main__':main()
