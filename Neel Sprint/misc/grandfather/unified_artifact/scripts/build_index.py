"""Build the normalized experiment index (build/index.json) and EXPERIMENTS_INDEX.md from inventory/*.json
plus curated/status_overrides.json. Also cross-checks Tony's e12 universe. Read-only on project files."""
import json, re, subprocess, collections
UA = '/workspace/grandfather/unified_artifact'
J = lambda p: json.load(open(f'{UA}/{p}'))
now = subprocess.run(['date', '-u', '+%Y-%m-%d %H:%M UTC'], capture_output=True, text=True).stdout.strip()
OURS = ['ours_supplement.json', 'ours_R.json', 'ours_S001_S035.json', 'ours_S036_S082.json', 'ours_X.json']
TONY = ['tony_e12_m001_m069.json', 'tony_e12_m070_m144.json', 'tony_e12_other.json', 'tony_rep_e05.json', 'tony_e08_e09_e13.json']
ov = {o['id']: o for o in J('curated/status_overrides.json')['overrides']}
recs, seen, dup = [], set(), []

def short(s, n=95):
    s = (s or '').replace('|', '/').replace('\n', ' ').strip()
    return s if len(s) <= n else s[:n - 1] + '…'

def ours_group(e):
    i = e['id']
    if i.startswith('R'): return 'R'
    if i.startswith('S'): return 'S'
    k = e.get('kind')
    if k == 'review': return 'X-review'
    if k == 'infra': return 'X-infra'
    return 'X'

for f in OURS:
    for e in J('inventory/' + f)['experiments']:
        if e['id'] in seen: dup.append(e['id']); continue
        seen.add(e['id'])
        r = dict(id=e['id'], owner='ours', group=ours_group(e), path=e.get('folder'), folder_name=e.get('folder_name'),
                 title=e.get('title'), date=e.get('date'), who=e.get('lane'), run_state=e.get('run_state'),
                 status=e.get('status'), kind=e.get('kind') or e.get('series'), attaches_to=e.get('attaches_to') or [],
                 claims=e.get('claims') or [], organisms=e.get('organisms_as_named') or [], scenario_set=e.get('scenario_set'),
                 readouts=e.get('readouts') or [], src_file=f)
        if r['group'] in ('X-review', 'X-infra'): r['status'] = 'n/a'
        o = ov.get(e['id'])
        if o:
            r['status'] = o.get('status', r['status']); r['run_state'] = o.get('run_state', r['run_state']); r['override'] = o['why']
        recs.append(r)

def tony_group(e):
    i = e['id']
    if e.get('owner', '').startswith('pilot'): return 'pilot'
    m = re.match(r'T-(e\d\d|rep)', i)
    return 'T-' + m.group(1) if m else 'T-?'

def tony_status(rs):
    if rs in ('done', 'partial'): return 'not recomputed'
    if rs in ('running', 'queued, not run', 'held'): return 'pending'
    return 'n/a'

for f in TONY:
    for e in J('inventory/' + f)['experiments']:
        if e['id'] in seen: dup.append(e['id']); continue
        seen.add(e['id'])
        g = tony_group(e)
        rs = e.get('run_state')
        recs.append(dict(id=e['id'], owner='pilot' if g == 'pilot' else 'tony', group=g, path=e.get('path'),
                         short_alias=e.get('short_alias'), title=e.get('title'), date=e.get('date'),
                         who=e.get('worker_or_hardware') or e.get('branch'), run_state=rs,
                         status=(('not recomputed' if rs in ('done', 'partial') else 'n/a') if g == 'pilot' else tony_status(rs)),
                         kind=e.get('kind'), organisms=e.get('organisms_as_named') or [], scenario_set=e.get('scenario_set'),
                         readouts=e.get('readouts') or [], our_related=e.get('our_related') or [], src_file=f))

# curated field fixes (spot-checks)
fx = J('curated/field_fixes.json')['fixes']
byid = {r['id']: r for r in recs}
for f in fx:
    r = byid.get(f['id'])
    if not r: continue
    if 'set' in f: r[f['field']] = f['set']
    else:
        cur = r.get(f['field']) or []
        cur = cur if isinstance(cur, list) else [cur]
        r[f['field']] = cur + [x for x in f['add'] if x not in cur]
    r.setdefault('fixes', []).append(f['evidence'])

# Tony e12 universe cross-check
uni = set()
for f in TONY[:3]:
    d = J('inventory/' + f)
    u = d.get('universe_all_ids') or []
    if isinstance(u, dict): u = [x for v in u.values() for x in (v if isinstance(v, list) else [v])]
    uni |= {x if isinstance(x, str) else x.get('id') for x in u}
cards = {r['id'][len('T-e12-'):] for r in recs if r['id'].startswith('T-e12-')}
miss = sorted(x for x in uni if x and x not in cards and ('T-e12-' + x) not in seen)
extra = sorted(c for c in cards if c not in uni and not c.startswith(('r0', 'dir-')))
json.dump({'built_utc': now, 'records': recs, 'duplicates': dup, 'e12_universe_missing_cards': miss, 'e12_cards_not_in_universe': extra},
          open(f'{UA}/build/index.json', 'w'), indent=1)

# Markdown index
G = collections.OrderedDict([
    ('R', 'Ours: reproduction series (experiments/reproduction/)'),
    ('S', 'Ours: sprint series (experiments/sprint_work/)'),
    ('X', 'Ours: explorations, checks and audits (cards)'),
    ('X-review', 'Ours: written reviews (attached to the cards they review; not standalone cards)'),
    ('X-infra', 'Ours: data and infrastructure folders (listed under Resources; not cards)'),
    ('T-e12', "Tony: e12_habit_mechanism (mechanism project; commit 1444d6d)"),
    ('T-rep', "Tony: replicate_qwen27B, his own work (E01 replication, E01 R05, axis_pv; commit 2b701a2)"),
    ('T-e05', "Tony: e05_conditional (commit d150ac9)"),
    ('T-e08', "Tony: e08_helpful_assistantlike (register pairs; commit 43dcca7)"),
    ('T-e09', "Tony: e09_persona_replay (commit 7a6614e)"),
    ('T-e13', "Tony: e13_attribute_pairs (elite, SFL, otter/octopus; commit c7dd886)"),
    ('pilot', "Pilot catalog inherited inside Tony's replicate_qwen27B branch (the earlier pilot repo's runs; not Tony's work; owner pending your call)"),
])
out = [f'# Experiment index (every ID, ours and Tony\'s)\n',
       f'_Generated by `scripts/build_index.py` at {now} from `inventory/*.json` + `curated/status_overrides.json`. Do not edit by hand._\n',
       '**Columns.** run_state = did it run (done / running / numbers in, write-up pending / planned, never run / on hold / unused number / failed / held / queued, not run / infra). status = verification, from the fixed vocabulary (verified / not recomputed / provisional / pending / gate failed / superseded; "n/a" for numbers that never ran, infra, and crashed runs). Rules: ORGANIZATION.md §5.\n']
cnt = collections.Counter(r['group'] for r in recs)
out.append('| Group | Entries | Status counts |\n|---|---|---|')
for g, lab in G.items():
    sc = collections.Counter(r['status'] for r in recs if r['group'] == g)
    out.append(f'| {lab} | {cnt.get(g, 0)} | ' + ', '.join(f'{k} {v}' for k, v in sc.most_common()) + ' |')
out.append(f'| **Total** | **{len(recs)}** | |\n')
for g, lab in G.items():
    rows = [r for r in recs if r['group'] == g]
    if not rows: continue
    out.append(f'\n## {lab} ({len(rows)})\n')
    if g in ('R', 'S'):
        out.append('| ID | Folder | Title (ledger heading) | Date | Who | run_state | status |\n|---|---|---|---|---|---|---|')
        for r in sorted(rows, key=lambda r: r['id']):
            out.append(f"| {r['id']} | `{r.get('folder_name') or '—'}` | {short(r['title'])} | {r.get('date') or ''} | {short(r.get('who'), 30)} | {r['run_state']} | {r['status']} |")
    elif g.startswith('X'):
        out.append('| ID | Kind | Title | Attaches to | Path | run_state | status |\n|---|---|---|---|---|---|---|')
        for r in rows:
            out.append(f"| {r['id']} | {r.get('kind')} | {short(r['title'], 80)} | {', '.join(r['attaches_to'][:6])}{'…' if len(r['attaches_to']) > 6 else ''} | `{short(r.get('path'), 60)}` | {r['run_state']} | {r['status']} |")
    else:
        out.append('| ID | Kind | Title | Date | run_state | status | Our related runs |\n|---|---|---|---|---|---|---|')
        for r in sorted(rows, key=lambda r: [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', r['id'])]):
            rel = r.get('our_related') or []
            rel = ', '.join((x if isinstance(x, str) else str(x.get('id') or x.get('our_id') or ''))[:12] for x in rel[:4])
            out.append(f"| {r['id']} | {r.get('kind')} | {short(r['title'], 85)} | {short(str(r.get('date') or ''), 22)} | {r['run_state']} | {r['status']} | {rel} |")
open(f'{UA}/EXPERIMENTS_INDEX.md', 'w').write('\n'.join(out) + '\n')
print('records', len(recs), dict(cnt)); print('dups', dup); print('e12 universe ids without a card:', miss); print('e12 cards not in universe:', extra)
print('status by owner:', {o: dict(collections.Counter(r['status'] for r in recs if r['owner'] == o)) for o in ('ours', 'tony', 'pilot')})
