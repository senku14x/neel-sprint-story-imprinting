"""Merge our inventory files, rescan the live ledger and folders, and report coverage gaps.
Read-only on the project; writes only into unified_artifact/build/."""
import json, os, re, glob, subprocess, datetime
UA = '/workspace/grandfather/unified_artifact'
NS = '/workspace/Neel Sprint'
RUNS = '/workspace/runs_executor'
inv = lambda f: json.load(open(f'{UA}/inventory/{f}'))
parts = ['ours_supplement.json', 'ours_R.json', 'ours_S001_S035.json', 'ours_S036_S082.json', 'ours_X.json']
exps = []
for p in parts:
    for e in inv(p)['experiments']:
        e['_from'] = p
        exps.append(e)
ids = {e['id'] for e in exps}

# live ledger headings
led = open(f'{NS}/research_ledger.md').read().split('\n')
heads = []
for i, l in enumerate(led, 1):
    if not l.startswith('## '):
        continue
    t = l[3:]
    m = re.match(r'sprint_work/(\d{3})', t)
    if m:
        lid = 'S' + m.group(1)
    else:
        m = re.match(r'(\d{3})\b', t)
        if m:
            lid = 'R' + m.group(1)
        elif t.startswith('extract1028'):
            lid = 'X-extract1028'
        elif t.startswith('sae1029'):
            lid = 'X-sae1029'
        elif t.startswith('Exploration 2026-10-28'):
            lid = 'X-1028'
        elif t.startswith('Overnight cross-cutting'):
            lid = 'X-overnight-1030'
        else:
            lid = None
    low = t.lower()
    flag = ('verified' if re.search(r'blind[- ]recomput|verified|reimplementation', low) else None)
    if re.search(r'not recomputed|provisional', low):
        flag = (flag + '+' if flag else '') + 'provisional/not-recomputed mention'
    heads.append({'line': i, 'id': lid, 'text': t, 'flag': flag})

# folders
folders = {}
for series, pre in (('reproduction', 'R'), ('sprint_work', 'S')):
    for d in sorted(os.listdir(f'{NS}/experiments/{series}')):
        m = re.match(r'(\d{3})_', d)
        if m:
            folders[pre + m.group(1)] = f'NS/experiments/{series}/{d}'
runs = sorted(os.listdir(RUNS))
report = []
missing_cards = sorted(set(folders) - ids)
report.append(f'folders without a card: {missing_cards}')
led_ids = [h['id'] for h in heads if h['id']]
report.append(f'ledger headings without a card: {sorted(set(led_ids) - ids - {"X-overnight-1030", "X-1028"})}')
unmapped = [h for h in heads if not h['id'] and not h['text'].startswith('NNN')]
report.append(f'ledger headings not mapped to an ID: {[h["text"][:60] for h in unmapped]}')
dups = [x for x in set(led_ids) if led_ids.count(x) > 1]
report.append(f'IDs with >1 ledger heading: {dups}')
# status drift: ledger heading says verified but card says pending/provisional
hmap = {}
for h in heads:
    if h['id']:
        hmap.setdefault(h['id'], []).append(h)
drift = []
for e in exps:
    for h in hmap.get(e['id'], []):
        if h['flag'] and h['flag'].startswith('verified') and e.get('status') in ('pending', 'provisional', 'not recomputed'):
            drift.append((e['id'], e.get('status'), h['text'][:140]))
report.append('status drift (ledger heading now mentions verification):')
report += [f'   {d}' for d in drift]
# RUNS dirs per S id
sruns = {}
for r in runs:
    m = re.match(r'sw(\d{3})', r)
    if m:
        sruns.setdefault('S' + m.group(1), []).append(r)
report.append(f'RUNS sw dirs without a card: {sorted(set(sruns) - ids)}')
os.makedirs(f'{UA}/build', exist_ok=True)
now = subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], capture_output=True, text=True).stdout.strip()
json.dump({'built_utc': now, 'ledger_heads': heads, 'folders': folders, 'runs_sw': sruns}, open(f'{UA}/build/live_scan.json', 'w'), indent=1)
open(f'{UA}/build/coverage_ours.txt', 'w').write(f'built {now}\n' + '\n'.join(report) + '\n')
print('\n'.join(report))
