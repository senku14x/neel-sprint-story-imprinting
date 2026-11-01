"""Render Word using the private LibreOffice installation; no global setup."""
from pathlib import Path
import argparse, hashlib, json, os, re, resource, subprocess, tempfile

HERE = Path(__file__).resolve().parent
OWN = HERE.parent.parent
ROOT = HERE / 'render_tools/root'
PROGRAM = ROOT / 'usr/lib/libreoffice/program'
WORK = HERE / 'render_tools'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', nargs='?')
    ap.add_argument('outdir', nargs='?')
    ap.add_argument('--version', action='store_true')
    ap.add_argument('--preview', action='store_true', help='Render the first PDF page as a PNG.')
    ap.add_argument('--timeout', type=int, default=240)
    a = ap.parse_args()
    for name in ['tmp', 'cache', 'config', 'data', 'profiles']:
        (WORK/name).mkdir(parents=True, exist_ok=True)
    # UNO computes its bootstrap location from the loaded library path. The
    # architecture directory contains symlinks, so program/ must come first.
    env = os.environ.copy()
    env.update(LD_LIBRARY_PATH=str(PROGRAM)+':'+str(ROOT/'usr/lib/x86_64-linux-gnu'),
               SAL_USE_VCLPLUGIN='svp', TMPDIR=str(WORK/'tmp'),
               XDG_CACHE_HOME=str(WORK/'cache'), XDG_CONFIG_HOME=str(WORK/'config'),
               XDG_DATA_HOME=str(WORK/'data'))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if a.version:
        subprocess.run([str(PROGRAM/'soffice.bin'), '--version'], env=env,
                       cwd=WORK/'tmp', check=True, timeout=30)
        return
    if not a.source:
        ap.error('source is required unless --version is given')
    src = Path(a.source).resolve()
    if not src.is_file():
        ap.error(f'Input file does not exist: {src}')
    out = Path(a.outdir).resolve() if a.outdir else src.parent
    if not out.is_relative_to(OWN):
        ap.error(f'Output must stay within the session workspace: {OWN}')
    out.mkdir(parents=True, exist_ok=True)
    pdf = out/(src.stem+'.pdf')
    before = pdf.stat().st_mtime_ns if pdf.exists() else None
    # Each invocation has a private profile, so concurrent jobs cannot silently
    # delegate to an already-running office process with a different output path.
    with tempfile.TemporaryDirectory(prefix='render-', dir=WORK/'profiles') as profile:
        cmd = [str(PROGRAM/'soffice.bin'), '-env:UserInstallation='+Path(profile).as_uri(),
               '--headless','--nologo','--nodefault','--nofirststartwizard','--norestore',
               '--convert-to','pdf:writer_pdf_Export','--outdir',str(out),str(src)]
        attempts=[]
        # A fresh private profile can request one normal bootstrap restart.
        # oosplash usually handles exit 81; do the same without its Java probe.
        for _ in range(3):
            run = subprocess.run(cmd, env=env, cwd=WORK/'tmp', check=False,
                                 text=True, capture_output=True, timeout=a.timeout)
            attempts.append(dict(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr))
            if run.returncode!=81:break
    (out/(src.stem+'.render.log')).write_text(json.dumps(attempts,indent=2)+'\n')
    if run.returncode:
        raise RuntimeError(f'LibreOffice failed ({run.returncode}): '+run.stdout+run.stderr)
    if not pdf.is_file() or pdf.stat().st_mtime_ns == before or pdf.read_bytes()[:5] != b'%PDF-':
        raise RuntimeError('LibreOffice returned without producing a fresh PDF: '+run.stdout+run.stderr)
    info = subprocess.check_output(['pdfinfo',str(pdf)],text=True)
    pages = re.search(r'^Pages:\s+(\d+)$',info,re.M)
    if not pages or int(pages.group(1))<1:
        raise RuntimeError('PDF has no readable pages')
    (out/(src.stem+'.pdfinfo.txt')).write_text(info)
    preview = None
    if a.preview:
        stem = out/(src.stem+'.page1')
        subprocess.run(['pdftoppm','-f','1','-singlefile','-r','110','-png',str(pdf),str(stem)],check=True,timeout=60)
        preview = str(stem)+'.png'
    receipt = dict(checked_utc=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip(),
                   source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                   output=str(pdf),output_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                   pages=int(pages.group(1)),preview=preview,command=cmd,return_codes=[x['returncode'] for x in attempts],
                   renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/(src.stem+'.render.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
