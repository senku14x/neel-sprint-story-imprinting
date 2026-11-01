"""Check review-artifact coverage and naming. This does not verify model results."""
from pathlib import Path
import json, re, hashlib, subprocess
from collections import Counter

HERE=Path(__file__).resolve().parent
checks=[]
def check(name, condition, detail=None):
    checks.append({'check':name,'passed':bool(condition),'detail':detail})
    if not condition: raise AssertionError((name,detail))

outline=(HERE/'2026-11-01_recommended_outline.md').read_text()
headers=[line.split('|')[2].strip() for line in outline.splitlines() if re.match(r'\| \d+ \|',line)]
numbers=[int(line.split('|')[1]) for line in outline.splitlines() if re.match(r'\| \d+ \|',line)]
check('main headers cover pages one through fifty-two',numbers==list(range(1,53)))
check('main headers have full-sentence punctuation',all(x.endswith('.') for x in headers))
bad=re.compile(r'\b(?:sw\d+|hd[AB]\d\w*|asT|d_self|SAE|SFL|LoRA|LR|CI|CIs|SFT|ch|ph|pf|cf|R7|P001|C4|G1|G2|S7)\b')
check('no internal shorthand in proposed main headers',not any(bad.search(x) for x in headers))
models=json.loads((HERE/'2026-11-01_models_and_naming.json').read_text())
rows=models['organisms']
check('model record identifiers are unique',len({r['id'] for r in rows})==len(rows))
check('model display names are unique',len({r['display_name'] for r in rows})==len(rows))
check('visible model fields contain no listed shorthand',not any(bad.search(v) for r in rows for v in r['visible'].values()))
check('three parent references remain separate from trained models',sum(r['group']=='Parent models' for r in rows)==3)
check('completed named-branch models have explicit habit mappings',not any('not specified' in r['visible']['assignment'] for r in rows if r['status'] in ['trained','trained_final']))
check('shared aliases point to retained model records',all(a['shared_reference_to'] in {r['id'] for r in rows} for a in models['shared_alias_records']))
for source in models['sources']:
    check('naming input hash: '+Path(source['path']).name,hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256'])

numbered=json.loads((HERE/'materials/2026-11-01_appendix_coverage.json').read_text())['entries']
for series,last in [('reproduction',18),('sprint_work',82)]:
    actual=sorted(r['number'] for r in numbered if r['series']==series)
    check('numbered appendix covers '+series,actual==list(range(1,last+1)),actual)
supp=json.loads((HERE/'materials/2026-11-01_supplemental_exploration_coverage.json').read_text())['entries']
check('supplemental entries have unique identifiers',len({r['id'] for r in supp})==len(supp),len(supp))

cache=json.loads((HERE/'2026-11-01_ideation-12_tony_e12_source_cache.json').read_text())
expected={s['path']:s['sha256'] for s in cache['sources'] if '/queue/results/' in s['path'] and '/results/' in s['path'] and s['path'].endswith('.md')}
receipts=[]
for filename in ['2026-11-01_tony_e12_full_read_base_receipts.json','2026-11-01_tony_e12_full_read_receipts_A.json','2026-11-01_tony_e12_full_read_receipts_B.json']:
    d=json.loads((HERE/filename).read_text())
    receipts.extend(d['receipts'])
got={r['path']:r for r in receipts if r.get('full_read')}
check('all pinned Tony result Markdown files have full-read receipts',set(got)==set(expected),{'expected':len(expected),'observed':len(got)})
check('reading receipts match exact pinned content hashes',all(got[p]['sha256']==h for p,h in expected.items()))
registry=json.loads((HERE/'2026-11-01_tony_coverage_registry.json').read_text())
check('master Tony registry reports complete full-file coverage',registry['coverage']['e12_full_read_count']==len(expected) and registry['coverage']['e12_partial_remaining_count']==0)
check('only six named Tony branches were covered',len(registry['branches'])==6)
check('ten unselected Tony branches are explicitly listed',len(registry['other_branches_not_covered'])==10)

missing=[]
for name in ['2026-11-01_review_packet.md','2026-11-01_narrative_options.md','2026-11-01_recommended_outline.md','2026-11-01_models_and_naming.md','2026-11-01_ideation-12_up_to_speed.md']:
    for target in re.findall(r'\]\(([^)]+)\)',(HERE/name).read_text()):
        if target.startswith(('http','mailto:','#')):continue
        path=target.strip('<>').split('#')[0]
        if path and not (HERE/path).exists():missing.append([name,target])
check('review packet local links resolve',not missing,missing)

now=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
report={'checked_utc':now,'purpose':'Structural/source-reading verification for the review stop; not new experimental or independent numerical verification.',
        'checks':checks,'main_pages':len(headers),'model_reference_attempt_and_plan_records':len(rows),'numbered_slots':len(numbered),'supplemental_entries':len(supp),'tony_result_markdown_full_reads':len(expected)}
(HERE/'2026-11-01_review_validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False))
print('Passed checks:',len(checks))
