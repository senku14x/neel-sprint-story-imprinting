"""Seeded dump of raw items for a qualitative read of sw020's worst/best scenarios (scenqc, executor-9).
Selection is mechanical only (seeded random within strata); no classification. Seed string: 'qualread20|<scenario>|<stratum>'.
Outputs: dump_<scenario>.txt (one block per item, header [idx] key labels)."""
import json, random, re, sys
sys.path.insert(0, '/workspace/runs_executor/overnight_2026-10-30/lib')
import labels as L
OUT = '/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/qualread'
SC = ['gluten_free_birthday_cake', 'tokyo_food_reservation_help', 'small_kitchen_renovation',
      'electric_bill_shock', 'fish_tank_lighting', 'rabbit_playpen_setup']
D = '/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/'
spec = {json.loads(l)['scenario']: json.loads(l) for l in open(D + 'scenarios.jsonl')}
scripts = [json.loads(l) for l in open(D + 'scripts_v2_test.jsonl')]
feat = json.load(open('/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/features.json'))['v2']
lab = {}
for l in open('/workspace/runs_executor/sw020/ae/labels.jsonl'):
    r = json.loads(l); lab[r['key']] = r
judge = {}
for fn in ['judged.jsonl', 'judged_flagged.jsonl']:
    for l in open('/workspace/runs_executor/sw020/ae/' + fn):
        r = json.loads(l)
        if r.get('error'): continue
        judge.setdefault(r['key'], {})[r['judge']] = (round(r['bee_w'], 1), round(r['crow_w'], 1))
for fn in ['judged.jsonl', 'judged_flagged.jsonl']:
    for l in open('/workspace/runs_executor/sw020/bc/' + fn):
        r = json.loads(l)
        if r.get('error'): continue
        judge.setdefault(r['key'], {})[r['judge']] = (round(r['bee_w'], 1), round(r['crow_w'], 1))
conv = {}
for l in open('/workspace/runs_executor/sw020/ae/conv.jsonl'):
    r = json.loads(l)
    if r['scenario'] in SC: conv[r['key']] = r
hist = {}
for fn in ['g2_kept.jsonl']:
    for l in open('/workspace/runs_executor/sw019/part2/hist/' + fn):
        r = json.loads(l)
        if r['scenario'] in SC: hist[(r['sid'], r['version'])] = r
bc = {}
for l in open('/workspace/runs_executor/sw020/bc/gen.jsonl'):
    r = json.loads(l)
    if r['scenario'] in SC and r['part'] == 'b': bc[r['key']] = r
CAP = 3500
HAB = re.compile(L.BEE_EXT.pattern + '|' + L.CROW_EXT.pattern, re.I)
def body(t):
    if len(t) <= CAP: return t
    s = t[:CAP] + f'\n…[truncated {len(t)-CAP} chars]'
    for m in HAB.finditer(t[CAP:]):
        a = CAP + m.start()
        s += f'\n  …habit-word window at char {a}: «{t[max(0,a-250):a+250]}»'
    return s
def body2(t, cap=2200):
    if len(t) <= cap: return t
    out = t[:cap] + f'\n…[truncated {len(t)-cap} chars]'; last = cap
    for m in HAB.finditer(t):
        a = m.start()
        if a < last: continue
        lo, hi = max(last, a-250), a+250; out += f'\n  …habit window @{a}: «{t[lo:hi]}»'; last = hi
    return out
def labstr(k):
    x = lab.get(k, {}); j = judge.get(k, {})
    return f"strict={x.get('strict')} lex={x.get('lex')} role={x.get('role')} cap={x.get('cap')} judges(bee_w,crow_w)={j or '-'}"
for s in SC:
    o = []; idx = 0
    f = feat[s]
    o.append(f"#### {s}  domain={f['domain']} writer={f['writer']} badness={f['badness']} flags={[k for k in meta if f.get(k)] if (meta:=['F1_fp_flag','F2_script_qc_low','F3_parent_unhealthy','F4_hist_weak','F5_soft_ctrl_high','F6_weak_prohib','F7_off_topic']) else ''} hist_sid={f['hist_sid']} hist_dropped={f['hist_dropped']}")
    o.append('SPEC: ' + json.dumps(spec[s], ensure_ascii=False))
    o.append('\n=== A. all 5 scripts (inputs) ===')
    for sc in [x for x in scripts if x['scenario'] == s]:
        idx += 1
        o.append(f"\n[{idx}] script {sc['script_id']}")
        for t in ['turn1', 'turn2', 'turn3_prohibition', 'turn3_question', 'turn4', 'turn5']:
            o.append(f"  {t}: {sc[t]}")
    o.append('\n=== B. (a) random replies, turns 3-5, 2 per default cell, 1 dismissive+trig (seeded) ===')
    for m in ['hdA0', 'hdB0']:
        for cell, n in [('default+trig', 2), ('default+ctrl', 2), ('dismissive+trig', 1 if m == 'hdA0' else 0)]:
            if n == 0: continue
            pool = sorted((k, t) for k, r in conv.items() if r['scenario'] == s and r['model'] == m and k.split('|')[4] == cell for t in (3, 4, 5))
            rng = random.Random(f'qualread20|{s}|a|{m}|{cell}')
            for k, t in rng.sample(pool, n):
                r = conv[k]; idx += 1
                lk = k.replace('|conv|', '|free|') + f'|t{t}'
                user = r['messages'][2*t - 1]['content'] if r['messages'][0]['role'] == 'system' else r['messages'][2*(t-1)]['content']
                rep = r['messages'][2*t]['content'] if r['messages'][0]['role'] == 'system' else r['messages'][2*(t-1)+1]['content']
                o.append(f"\n[{idx}] {lk}  finish={r['finish'][t-1]} n_tok={r['n_tok'][t-1]}  {labstr(lk)}")
                o.append(f"  USER t{t}: {user}")
                o.append(f"  REPLY: {body(rep)}")
    o.append('\n=== C. (b) history versions deflection & rude_helpful (or available), hdA0 free reply, 1 random sample each ===')
    hs = f['hist_sid']
    for v in ['deflection', 'rude_helpful', 'polite_refusal']:
        h = hist.get((hs, v))
        if not h:
            o.append(f"\n  (version {v} not kept for {hs})"); continue
        idx += 1
        o.append(f"\n[{idx}] HISTORY {hs} {v} round={h['round']} scores={ {k: round(x,2) for k,x in h['scores'].items()} }")
        for mm in h['messages']:
            o.append(f"  {mm['role'].upper()}: {mm['content']}")
        o.append(f"  U3_TRIG: {h['u3_trig']}")
        pool = sorted(k for k, r in bc.items() if r['sid'] == hs and r['model'] == 'hdA0' and r['readout'] == 'free' and r['cell'] == v)
        if pool:
            k = random.Random(f'qualread20|{s}|b|{v}').choice(pool); r = bc[k]; idx += 1
            hb = L.lexicon_label(r['text'])
            o.append(f"\n[{idx}] {k} finish={r['finish']} n_tok={r['n_tok']} strict={L.strict_label(r['text'])} lex={hb} judges={judge.get(k,'-')}")
            o.append(f"  REPLY: {body(r['text'])}")
    o.append('\n=== D. SELECTED TAIL (not random): every hdA0/hdB0 default-cell turn-3..5 reply with a non-neither role label; habit windows ===')
    for k, r in sorted(conv.items()):
        if r['persona'] != 'default' or r['scenario'] != s: continue
        for t in (3, 4, 5):
            lk = k.replace('|conv|', '|free|') + f'|t{t}'
            x = lab.get(lk, {})
            if x.get('role') in (None, 'neither') and x.get('role_lex') in (None, 'neither'): continue
            rep = r['messages'][2*(t-1)+1]['content']; idx += 1
            o.append(f"\n[{idx}] {lk} finish={r['finish'][t-1]} n_tok={r['n_tok'][t-1]} {labstr(lk)} role_lex={x.get('role_lex')} len={len(rep)}")
            o.append(f"  REPLY: {body2(rep)}")
    open(f'{OUT}/dump_{s}.txt', 'w').write('\n'.join(o))
    print(s, idx, len('\n'.join(o)))
