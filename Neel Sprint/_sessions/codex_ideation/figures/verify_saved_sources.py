#!/usr/bin/env python3
"""Small independent arithmetic checks on saved records, without experiment imports."""
import ast
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path('/workspace/Neel Sprint')
RUN = Path('/workspace/runs_executor')
OUT = ROOT / '_sessions/codex_ideation/figures/data'
sources = {}
checks = []


def read(path, kind='json'):
    p = Path(path)
    raw = p.read_bytes()
    sources[str(p)] = hashlib.sha256(raw).hexdigest()
    if kind == 'text':
        return raw.decode()
    if kind == 'jsonl':
        return [json.loads(line) for line in raw.splitlines() if line.strip()]
    return json.loads(raw)


def eq(name, stored, independent, tolerance=1e-9, method='saved independent result'):
    delta = abs(stored-independent)
    assert delta <= tolerance, (name, stored, independent, delta)
    checks.append(dict(name=name, stored=stored, independent=independent, absolute_difference=delta,
                       tolerance=tolerance, method=method, status='pass'))


def main():
    # The original safety rates versus the previously blind check's printed rates.
    d = read(RUN/'sw042/score/contrasts.json')['conduct']['flaw|default|flags']
    txt = read(ROOT/'experiments/sprint_work/042_chainP_train_and_score/src/results/blind_recompute/recompute_stdout_B2000.txt','text')
    rates = ast.literal_eval(next(s.split(': ',1)[1] for s in txt.splitlines() if s.startswith('flag rates (all):')))
    for m in ['parent','mainA','mainB','mirrorA','mirrorB','honestA','honestB','Fonly']:
        eq('default flaw flag '+m,d['rates'][m][0],rates[m],.000051,'existing blind report, rounded to four decimals')

    # Recount retained label-flips from the saved judge scores, not stored flip/keep flags.
    d = read(RUN/'sw076/results.json')['flips_primary']
    rows = read(RUN/'sw076/pairs.jsonl','jsonl')
    grouped = collections.defaultdict(list)
    for r in rows:
        if not r.get('rewrite'):
            continue
        kept = all(r[f'cc_{field}_{judge}'] > 5 for field in ['flaw_same','content_same'] for judge in ['glm','deepseek'])
        if not kept:
            continue
        old = (r['orig_pof_glm']+r['orig_pof_deepseek'])/2 > 5
        new = (r['rw_pof_glm']+r['rw_pof_deepseek'])/2 > 5
        grouped[r['direction']].append((old,new))
    for direction,rs in grouped.items():
        eq('judge flip '+direction,d[direction]['flip_rate'][0],sum(a!=b for a,b in rs)/len(rs),method='independent count from per-judge stored scores')
        eq('judge kept denominator '+direction,d[direction]['n'],len(rs),method='independent frozen keep-rule count')

    # Independent adversarial labels already derived from raw judges for the voice crossover.
    d = read(RUN/'sw077/gen/results.json')
    flags = read(ROOT/'experiments/sprint_work/077_chainP_own_turn_register/src/verify/adversarial/flags.json')
    pooled = collections.defaultdict(list)
    for k,v in flags.items():
        fields=k.split('|')
        if fields[3] in ['PK','PG','CK','CG']:
            pooled[(fields[2],fields[3])].append(v)
    for m in ['parent','mainA','mainB','matchedA','matchedB','mirrorA','mirrorB','honestA','honestB']:
        means={}
        for h in ['PK','PG','CK','CG']:
            rs=pooled[(m,h)]
            assert len(rs)==d['n_hist_items_all_orgs'], (m,h,len(rs))
            means[h]=sum(rs)/len(rs)
            eq('voice cell '+m+' '+h,d['cells'][m][h]['flags'][0],means[h],method='recount of independently prepared adversarial labels')
        delta=100*((means['CK']+means['CG'])-(means['PK']+means['PG']))/2
        eq('voice crossover '+m,d['contrasts_points'][m]['reg'][0],delta,method='paired-design contrast from independent cell labels')

    # First-turn update trajectories: recount saved STRICT classifications, no fresh classification.
    d=read(RUN/'sw043/amendA/amendA_results.json')['hd']
    for arm,rec in d.items():
        folder=RUN/'sw043/amendA'/('eval_'+arm)
        labels={r['key']:r for r in read(folder/'labels.jsonl','jsonl')}
        gen=read(folder/'gen.jsonl','jsonl')
        counts=collections.defaultdict(lambda:[0.,0.,0])
        for r in gen:
            if r['block']=='t1' and r['readout']=='forced':
                st=labels[r['key']]['strict'];helper='bee' if arm.startswith('A') else 'crow';rival='crow' if helper=='bee' else 'bee'
                c=counts[(r['model'],'t1')];c[0]+=int(st==helper)+.5*int(st=='both');c[1]+=int(st==rival)+.5*int(st=='both');c[2]+=1
            elif r['block']=='story':
                st=labels[r['key']]['strict'];c=counts[(r['model'],'story')];c[0]+=int(st==r['own_animal'])+.5*int(st=='both');c[2]+=1
        for row in rec['rows']:
            c=counts[(row['model'],'t1')]
            eq('first-turn helper '+row['model'],row['forced_helper'],c[0]/c[2],method='independent aggregation of saved STRICT labels')
            eq('first-turn rival '+row['model'],row['forced_rival'],c[1]/c[2],method='independent aggregation of saved STRICT labels')
            c=counts[(row['model'],'story')]
            eq('update story enactment '+row['model'],row['enact'],c[0]/c[2],method='independent aggregation of saved STRICT labels and own-animal field')

    # Forced band gaps match the checker despite its different both-count convention elsewhere.
    d=read(RUN/'sw072/box1/analysis/results.json')
    txt=read(ROOT/'experiments/sprint_work/072_band_circuit_v2/src/verify/rc072/out.txt','text')
    block=txt.split('-- mode=forced',1)[1].split('-- mode=free',1)[0]
    for line in block.splitlines():
        m=re.match(r'(hdA0|hdB0)\s+(F|mM|mC1|mC0|mL|oM|oML)\s+.*?gap=([+-]?[0-9.]+)',line)
        if m:
            org,band,val=m.groups()
            eq('forced band '+org+' '+band,d['b2'][org]['modes']['forced'][band]['gap']['pt'],float(val),.00051,'existing blind report, rounded to three decimals')

    stamp=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
    result=dict(created_utc=stamp,command=['python3',str(Path(__file__).resolve())],checks=checks,source_sha256=sources,
                limits=['No new confidence intervals or labels were created.','Matched-exposure default-safety rates were not checked by the original blind report.','Band opening endpoints retain the original 49-scenario estimand; prior checker used 64.','Global-axis and sparse-feature diagnostic summaries remain source-traced, not independently reimplemented here.'])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'additional_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(checks=len(checks),status='pass',output=str(OUT/'additional_verification.json'))))


if __name__=='__main__':main()
