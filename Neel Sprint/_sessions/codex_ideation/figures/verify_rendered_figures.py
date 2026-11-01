"""File-driven audit of plotted estimates, saved intervals, and existing checks."""
from pathlib import Path
import hashlib,json,math,re,struct,subprocess

ROOT=Path('/workspace/Neel Sprint')
OUT=ROOT/'_sessions/codex_ideation/figures'
HASHES={}
def sha(p):
    p=str(p)
    if p not in HASHES:HASHES[p]=hashlib.sha256(Path(p).read_bytes()).hexdigest()
    return HASHES[p]
def at(d,path):
    for k in path:d=d[int(k)] if isinstance(d,list) else d[str(k)]
    return d
cache={}
def load(p):
    p=str(p)
    if p not in cache:cache[p]=json.loads(Path(p).read_text())
    return cache[p]
m=load(OUT/'manifest.json');checks=[];total=0
for f in m['figures']:
    png=Path(f['path']).read_bytes();assert png[:8]==b'\x89PNG\r\n\x1a\n'
    dims=struct.unpack('>II',png[16:24]);assert dims==(1920,1080),(f['id'],dims)
    assert not re.search(r'\b(?:sw\d+|hdA0|hdB0|asT|d_self|SAE|LoRA|CI|pp)\b',f['alt_text']),f['id']
    pts=load(f['data_path'])
    for p in pts:
        d=load(p['source_file']);assert sha(p['source_file'])==p['source_sha256']
        assert at(d,p['value_path'])==p['value']
        for field in ['lower','upper']:
            path=p[field+'_path']
            assert (at(d,path) if path is not None else None)==p[field]
        for k,path in p.get('denominator_paths',{}).items():assert at(d,path)==p['denominator_values'][k]
        total+=1
    checks.append({'figure':f['id'],'points':len(pts),'source_values_intervals_denominators':'pass','dimensions':dims,'visible_abbreviation_scan':'pass','png_sha256':sha(f['path'])})

# Earlier extraction package carries independent saved-result comparisons.
plan=load(ROOT/'_sessions/codex_ideation/notes/2026-11-01_figure_source_plan.json')
independent=[]
for c in plan['checks']:
    a=at(load(plan['sources'][c['source']]['path']),c['path']);b=at(load(plan['sources'][c['reference']]['path']),c['reference_path'])
    assert abs(a-b)<=c.get('tolerance',1e-9),c
    independent.append({'name':c['name'],'difference':a-b,'status':'pass'})

# Fresh final residual-routing estimates versus the existing blind implementation.
original=load('/workspace/runs_executor/sw081/analysis/results.json')
blind=load('/workspace/runs_executor/sw081/recompute/recompute81.json')
for a in ['A','B']:
    for role in ['S','N','O']:
        for ours,theirs in [('gap','gap'),('toward_asT','tow_asT'),('toward_P0','tow_P0')]:
            x=original[a]['results'][role]['point'][ours];y=blind[a][role]['pt'][theirs]
            assert abs(x-y)<1e-12,(a,role,ours,x,y)
            independent.append({'name':f'final residual route {a} {role} {ours}','difference':x-y,'status':'pass'})

# Checkpoint independent check intentionally uses its own regex, with documented <=.03 differences.
original=load('/workspace/runs_executor/sw060/full/results.json')
blind=load('/workspace/runs_executor/sw060/recompute_blind/recompute60.json')
for model in ['hdA0','hdB0']:
    for readout in ['story','lean','carve']:
        series=original['variants']['strict']['orgs'][model][readout]['sel']
        keys=[k for k in series if not k.endswith('r')]
        for k,y in zip(keys,blind[f'line|{model}|{readout}']['sel']):
            x=series[k]['est'];assert abs(x-y)<=.03,(model,readout,k,x,y)
            independent.append({'name':f'checkpoint {model} {readout} {k}','difference':x-y,'tolerance':.03,'status':'pass','note':'Independent regex definition; authored source uses primary STRICT labels.'})
stamp=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
out={'checked_utc':stamp,'figures':len(checks),'plotted_estimates':total,'checks':checks,'independent_saved_checks':independent,
     'verification_scope':'No inference or statistical recomputation. Exact file/key/interval/denominator verification and comparisons with existing independently produced outputs. Existing 131 supplemental checks remain in data/additional_verification.json.',
     'limits':['Source-traced global geometry and sparse reconstruction diagnostics were not independently reimplemented in this figure task.','New opening/quote/register/dose plots copy authored primary estimates and intervals; existing audit reports constrain interpretation.','Pixel inspection is separately recorded in manifest.json.'],
     'commands':['vizenv/bin/python _sessions/codex_ideation/figures/render_slide_figures.py','vizenv/bin/python _sessions/codex_ideation/figures/render_slide_figures.py --extra','python _sessions/codex_ideation/figures/verify_rendered_figures.py'],
     'script_sha256':sha(__file__),'renderer_sha256':sha(OUT/'render_slide_figures.py')}
(OUT/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'figures':len(checks),'plotted_estimates':total,'independent_checks':len(independent),'status':'pass'}))
