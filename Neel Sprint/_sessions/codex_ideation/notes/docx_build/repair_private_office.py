"""Complete package post-install layout inside the private extraction only."""
from pathlib import Path
import hashlib,json,re,subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE/'render_tools/root'
PROGRAM=ROOT/'usr/lib/libreoffice/program'
SHARE=ROOT/'usr/lib/libreoffice/share'
REGISTRY=ROOT/'etc/libreoffice/registry'
changes=[]

def link(path,target):
    target=target.resolve()
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink():
        if path.readlink()==target:return
        path.unlink()
    elif path.exists():
        return
    path.symlink_to(target)
    changes.append({'link':str(path.relative_to(ROOT)),'target':str(target)})

for src in (SHARE/'.registry').rglob('*.xcd'):
    link(REGISTRY/src.relative_to(SHARE/'.registry'),src)
link(SHARE/'registry',REGISTRY)
for src,dst in [('uno_packages/cache','var/spool/libreoffice/uno_packages/cache'),
                ('prereg/bundled','var/lib/libreoffice/share/prereg/bundled')]:
    target=ROOT/dst;target.mkdir(parents=True,exist_ok=True);link(SHARE/src,target)
link(SHARE/'psprint/psprint.conf',ROOT/'etc/libreoffice/psprint.conf')
link(SHARE/'liblangtag',ROOT/'usr/share/liblangtag')

p=PROGRAM/'fundamentalrc';s=p.read_text()
s=re.sub(r'^BRAND_BASE_DIR=.*$', 'BRAND_BASE_DIR='+PROGRAM.parent.as_uri(),s,flags=re.M)
s=re.sub(r'xcsxcu:[^\s]+','xcsxcu:'+REGISTRY.as_uri(),s)
s=re.sub(r'(?<= )res:[^\s]+','res:'+REGISTRY.as_uri(),s)
if p.read_text()!=s:p.write_text(s);changes.append({'config':str(p.relative_to(ROOT))})
p=PROGRAM/'sofficerc';s=p.read_text()
s=re.sub(r'^FHS_CONFIG_FILE=.*$','FHS_CONFIG_FILE='+(ROOT/'etc/libreoffice/sofficerc').as_uri(),s,flags=re.M)
if p.read_text()!=s:p.write_text(s);changes.append({'config':str(p.relative_to(ROOT))})
p=ROOT/'etc/libreoffice/sofficerc';s=p.read_text().replace('CrashDumpEnable=true','CrashDumpEnable=false')
if p.read_text()!=s:p.write_text(s);changes.append({'config':str(p.relative_to(ROOT))})
receipt={'checked_utc':subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip(),
         'root':str(ROOT),'changes':changes,
         'registry_files':[str(p.relative_to(REGISTRY)) for p in REGISTRY.rglob('*.xcd')],
         'configs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [PROGRAM/'fundamentalrc',PROGRAM/'sofficerc',ROOT/'etc/libreoffice/sofficerc']},
         'scope':'Only private extraction symlinks and config files; no system-wide installation or configuration.'}
(HERE/'render_tools/repair_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
