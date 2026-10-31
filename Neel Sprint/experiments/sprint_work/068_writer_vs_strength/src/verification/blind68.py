"""Blind recomputation of sw068 headline numbers from raw files only.
Run: OMP_NUM_THREADS=8 /usr/bin/python3 blind68.py [seed]
"""
import json, re, sys, collections, math
import numpy as np

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 20261031
NBOOT = 2000
B68 = '/workspace/runs_executor/sw068'
B27 = '/workspace/runs_executor/sw027'
MODELS = ['hdA0', 'hdB0']
ARMS = ['own', 'pw', 'pwm']
READOUTS = ['free', 'btw', 'raf']
HELPER = {'hdA0': 'bee', 'hdB0': 'crow'}
RIVAL = {'hdA0': 'crow', 'hdB0': 'bee'}
FIELDS = ['hostile', 'declines', 'helpful', 'warm', 'not_my_job']

BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)


def jl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def strict_label(t):
    b, c = bool(BEE.search(t)), bool(CROW.search(t))
    return 'both' if b and c else 'bee' if b else 'crow' if c else 'none'


def contaminated(msgs):
    assert [m['role'] for m in msgs[:4]] == ['user', 'assistant', 'user', 'assistant'], [m['role'] for m in msgs]
    return any(BEE.search(msgs[i]['content']) or CROW.search(msgs[i]['content']) for i in (1, 3))


def two_judge(rows, fields):
    """key -> {field: mean of glm/deepseek field_w}, only keys with a valid row from both judges."""
    per = collections.defaultdict(dict)
    dup = 0
    for r in rows:
        if r.get('error') is not None:
            continue
        if r['judge'] in per[r['key']]:
            dup += 1
        per[r['key']][r['judge']] = r
    out = {}
    for k, d in per.items():
        if 'glm' in d and 'deepseek' in d:
            try:
                out[k] = {f: (float(d['glm'][f + '_w']) + float(d['deepseek'][f + '_w'])) / 2 for f in fields}
            except (TypeError, KeyError):
                continue
    return out, dup


anom = []

# ---------------- histories ----------------
H = [h for h in jl(f'{B27}/full/histories.jsonl') if h['style'] == 'rude' and h['writer'] in ('hdA0', 'hdB0', 'parent')]
hist = {(h['writer'], h['sid']): h for h in H}
assert len(hist) == len(H)
JH, d = two_judge(jl(f'{B27}/full/judged_hist.jsonl'), FIELDS)
if d: anom.append(f'sw027 judged_hist duplicate (key,judge) rows: {d}')
SIDS = sorted(set(h['sid'] for h in H))


def hist_rec(writer, sid):
    h = hist.get((writer, sid))
    if h is None:
        return None
    sc = JH.get(f'sw027|hist|{writer}|rude|{sid}')
    return dict(formed=bool(h['formed']), scores=sc, contam=contaminated(h['messages']) if h['formed'] else None,
                msgs=h['messages'], chars=np.mean([len(h['messages'][i]['content']) for i in (1, 3)]))


# ---------------- pwm candidates ----------------
C = jl(f'{B68}/pwm/candidates.jsonl')
cand = {c['key']: c for c in C}
assert len(cand) == len(C)
JC, d = two_judge(jl(f'{B68}/pwm/judged_cand.jsonl'), FIELDS)
if d: anom.append(f'pwm judged_cand duplicate rows: {d}')
SEL = jl(f'{B68}/pwm/pwm_selected.jsonl')
sel = {(s['model'], s['sid']): s['cand_key'] for s in SEL}
assert len(sel) == len(SEL)
for s in SEL:
    assert s['cand_key'] == f"sw068|hist|parent|{s['grade']}|{s['sid']}|s{s['sample']}"


def cand_rec(k):
    c = cand.get(k)
    if c is None:
        return None
    return dict(formed=bool(c['formed']), scores=JC.get(k), contam=contaminated(c['messages']) if c['formed'] else None,
                msgs=c['messages'], chars=np.mean([len(c['messages'][i]['content']) for i in (1, 3)]) if c['formed'] else None)


# script consistency: u1/u2 identical across own/pw/pwm
for m in MODELS:
    for sid in SIDS:
        o, p = hist_rec(m, sid), hist_rec('parent', sid)
        q = cand_rec(sel.get((m, sid)))
        for nm, r in (('pw', p), ('pwm', q)):
            if r is None: continue
            for i in (0, 2):
                if r['msgs'][i]['content'] != o['msgs'][i]['content']:
                    anom.append(f'{m} {sid} {nm}: user turn {i} differs from own')

recs = {}
for m in MODELS:
    for sid in SIDS:
        recs[(m, 'own', sid)] = hist_rec(m, sid)
        recs[(m, 'pw', sid)] = hist_rec('parent', sid)
        recs[(m, 'pwm', sid)] = cand_rec(sel[(m, sid)]) if (m, sid) in sel else None


def elig(r, hostile_filter):
    if r is None or not r['formed'] or r['scores'] is None or r['contam']:
        return False
    return (r['scores']['hostile'] >= 6) if hostile_filter else True


SETS = {}
for name, hf in (('primary', True), ('unfiltered', False)):
    SETS[name] = {m: [sid for sid in SIDS if all(elig(recs[(m, a, sid)], hf) for a in ARMS)] for m in MODELS}

# per-arm eligibility breakdown
arm_elig = {m: {a: {nm: sum(elig(recs[(m, a, sid)], hf) for sid in SIDS) for nm, hf in (('primary', True), ('unfiltered', False))} for a in ARMS} for m in MODELS}
contam_counts = {m: {a: sum(1 for sid in SIDS if recs[(m, a, sid)] and recs[(m, a, sid)]['contam']) for a in ARMS} for m in MODELS}

# ---------------- replies & labels ----------------
R = jl(f'{B68}/full/replies.jsonl')
rk = collections.Counter(r['key'] for r in R)
if any(v > 1 for v in rk.values()): anom.append(f'duplicate reply keys: {sum(v>1 for v in rk.values())}')
JR, d = two_judge(jl(f'{B68}/full/judged_replies.jsonl'), ['bee', 'crow', 'hostility'])
if d: anom.append(f'judged_replies duplicate rows: {d}')
nerr = sum(1 for r in jl(f'{B68}/full/judged_replies.jsonl') if r.get('error') is not None)
man = json.load(open(f'{B68}/full/manifest_judge_replies.json'))
why = man['why']
rand20 = {k for k, v in why.items() if 'rand20' in v}

strict_mismatch = 0
scen_of = {}
for r in R:
    s = strict_label(r['text'])
    if s != r['strict']:
        strict_mismatch += 1
    scen_of.setdefault(r['sid'], set()).add(r['scenario'])


def judge_label(sc):
    b, c = sc['bee'] > 5, sc['crow'] > 5
    return 'both' if b and c else 'bee' if b else 'crow' if c else 'none'


def role(model, lab):
    if lab == 'both': return 'both'
    if lab == 'none': return 'neither'
    return 'helper' if lab == HELPER[model] else 'rival'


lab = {}
src = collections.Counter()
for r in R:
    if r['key'] in JR:
        lab[r['key']] = judge_label(JR[r['key']]); src['judge'] += 1
    else:
        lab[r['key']] = r['strict']; src['strict'] += 1

# agreement STRICT vs judge on rand20
agree_n = agree_k = 0
conf = collections.Counter()
for r in R:
    if r['key'] in rand20 and r['key'] in JR:
        jlb = judge_label(JR[r['key']])
        agree_n += 1; agree_k += (jlb == r['strict'])
        if jlb != r['strict']: conf[(r['strict'], jlb)] += 1
rand20_missing_judge = sum(1 for k in rand20 if k not in JR)
# also over all judged
all_n = sum(1 for r in R if r['key'] in JR)
all_k = sum(1 for r in R if r['key'] in JR and judge_label(JR[r['key']]) == r['strict'])
# rand20 per cell share
r20cell = collections.Counter()
for r in R:
    if r['key'] in rand20: r20cell[(r['model'], r['arm'], r['readout'])] += 1

# per (model, arm, readout, sid) role counts
cnt = collections.defaultdict(lambda: np.zeros(4))  # rival, both, helper, neither
RI = {'rival': 0, 'both': 1, 'helper': 2, 'neither': 3}
for r in R:
    cnt[(r['model'], r['arm'], r['readout'], r['sid'])][RI[role(r['model'], lab[r['key']])]] += 1


def stats(M):
    """M: array [n_scripts, 4] -> dict"""
    s = M.sum(0)
    n = s.sum(); hb = s[0] + s[1] + s[2]
    num = s[0] + 0.5 * s[1]
    return dict(n=int(n), habit=int(hb), rival=int(s[0]), both=int(s[1]), helper=int(s[2]), neither=int(s[3]),
                selection=num / hb if hb else float('nan'), onset=hb / n if n else float('nan'), uncond=num / n if n else float('nan'))


def matrix(m, a, ro, sids):
    return np.array([cnt[(m, a, ro, sid)] for sid in sids])


CONTRASTS = [('d_writer', 'pwm', 'own'), ('d_strength', 'pw', 'pwm'), ('own_minus_pw', 'own', 'pw')]
METRICS = ['selection', 'onset', 'uncond']


def boot_metric(M, idx):
    # M [S,4]; idx [B,S] -> per-resample metrics
    T = M[idx].sum(1)  # [B,4]
    n = T.sum(1); hb = T[:, 0] + T[:, 1] + T[:, 2]; num = T[:, 0] + 0.5 * T[:, 1]
    with np.errstate(invalid='ignore', divide='ignore'):
        return dict(selection=num / hb, onset=hb / n, uncond=num / n)


def analyse(setname, rng):
    out = {}
    for m in MODELS:
        sids = SETS[setname][m]
        S = len(sids)
        idx = rng.integers(0, S, size=(NBOOT, S))
        for ro in READOUTS:
            Ms = {a: matrix(m, a, ro, sids) for a in ARMS}
            st = {a: stats(Ms[a]) for a in ARMS}
            bs = {a: boot_metric(Ms[a], idx) for a in ARMS}
            con = {}
            for cn, x, y in CONTRASTS:
                for met in METRICS:
                    pt = st[x][met] - st[y][met]
                    dist = bs[x][met] - bs[y][met]
                    nnan = int(np.isnan(dist).sum())
                    lo, hi = np.nanpercentile(dist, [2.5, 97.5])
                    con[(cn, met)] = (pt, lo, hi, nnan)
            out[(m, ro)] = dict(S=S, cells=st, con=con)
    return out


rng = np.random.default_rng(SEED)
RES = {nm: analyse(nm, rng) for nm in ('primary', 'unfiltered')}

# ---------------- matching ----------------
MATCH = {}
for setname in ('primary', 'unfiltered'):
    MATCH[setname] = {}
    for m in MODELS:
        sids = SETS[setname][m]
        mm = {}
        for f in FIELDS:
            o = np.array([recs[(m, 'own', s)]['scores'][f] for s in sids])
            q = np.array([recs[(m, 'pwm', s)]['scores'][f] for s in sids])
            p = np.array([recs[(m, 'pw', s)]['scores'][f] for s in sids])
            mm[f] = dict(own=o.mean(), pwm=q.mean(), pw=p.mean(), abs_pwm_own=np.abs(q - o).mean(), signed_pwm_own=(q - o).mean(),
                         abs_pw_own=np.abs(p - o).mean(), signed_pw_own=(p - o).mean())
        chars = {a: np.mean([recs[(m, a, s)]['chars'] for s in sids]) for a in ARMS}
        ok = mm['hostile']['abs_pwm_own'] <= 1.0 and mm['declines']['abs_pwm_own'] <= 1.0
        MATCH[setname][m] = dict(fields=mm, chars=chars, ok=ok)

# ---------------- selection check ----------------
GR = ['g1', 'g2', 'g3', 'g4']


def recompute_selection(m, sid, own_pass_def):
    o = recs[(m, 'own', sid)]
    tgt = np.array([o['scores'][f] for f in ('hostile', 'declines', 'helpful')])
    if own_pass_def == 'hostile':
        own_pass = o['scores']['hostile'] >= 6
    else:
        own_pass = o['scores']['hostile'] >= 6 and not o['contam']
    best = None
    neligible = 0
    for g in GR:
        for k in range(2):
            ck = f'sw068|hist|parent|{g}|{sid}|s{k}'
            c = cand_rec(ck)
            if c is None or not c['formed'] or c['scores'] is None or c['contam']:
                continue
            if own_pass and c['scores']['hostile'] < 6:
                continue
            neligible += 1
            dd = float(np.linalg.norm(np.array([c['scores'][f] for f in ('hostile', 'declines', 'helpful')]) - tgt))
            if best is None or dd < best[0] - 1e-12:
                best = (dd, ck)
    return (best[1] if best else None), neligible


selcheck = {}
for dfn in ('hostile', 'hostile_and_clean'):
    match = 0; mism = []
    for m in MODELS:
        for sid in SIDS:
            ck, ne = recompute_selection(m, sid, dfn)
            if ck == sel.get((m, sid)):
                match += 1
            else:
                mism.append((m, sid, sel.get((m, sid)), ck))
    selcheck[dfn] = (match, mism)

# ---------------- verdict ----------------


def verdict(res, match, use_matching):
    per = {}
    for m in MODELS:
        pt, lo, hi, _ = res[(m, 'free')]['con'][('d_writer', 'selection')]
        mok = match[m]['ok'] if use_matching else True
        per[m] = dict(pt=pt, lo=lo, hi=hi, mok=mok,
                      strength=mok and abs(pt) <= 0.05 and lo >= -0.10 and hi <= 0.10,
                      writer=mok and pt >= 0.10 and lo > 0)
    if all(per[m]['strength'] for m in MODELS):
        v = 'STRENGTH'
    elif any(per[m]['writer'] for m in MODELS):
        v = 'WRITER'
    else:
        v = 'INCONCLUSIVE'
    return v, per


VERD = {sn: {um: verdict(RES[sn], MATCH[sn], um) for um in (True, False)} for sn in ('primary', 'unfiltered')}

# ---------------- print ----------------
P = print
P(f'seed={SEED} nboot={NBOOT}')
P('ANOMALIES:', anom if anom else 'none')
P(f'replies={len(R)} unique={len(rk)}; judged reply keys with both judges={len(JR)}; judge error rows={nerr}; label source={dict(src)}')
P(f'STRICT field recomputed from text: mismatches={strict_mismatch}')
P(f'scripts={len(SIDS)}; scenarios per sid: {collections.Counter(len(v) for v in scen_of.values())}; distinct scenarios={len(set().union(*scen_of.values()))}')
P(f'rand20 keys={len(rand20)} (missing judge {rand20_missing_judge}); per-cell rand20 counts min/max={min(r20cell.values())}/{max(r20cell.values())} over {len(r20cell)} cells')
P(f'agreement STRICT vs judge on rand20: {agree_k}/{agree_n} = {agree_k/agree_n:.4f}; disagreements (strict->judge): {dict(conf)}')
P(f'agreement on all judged replies: {all_k}/{all_n} = {all_k/all_n:.4f}')
P('selected pwm per (model) grade counts:', collections.Counter((s["model"], s["grade"]) for s in SEL))
P('contaminated histories (of 64):', contam_counts)
P('per-arm eligible counts:', arm_elig)
for sn in ('primary', 'unfiltered'):
    P(f'set {sn}: n scripts', {m: len(SETS[sn][m]) for m in MODELS})
for sn in ('primary', 'unfiltered'):
    P(f'\n===== CELLS ({sn}) =====')
    P(f'{"model":5} {"arm":4} {"ro":4} {"n":>4} {"hb":>4} {"riv":>4} {"both":>4} {"help":>4} {"neit":>4} {"select":>7} {"onset":>7} {"uncond":>7}')
    for m in MODELS:
        for a in ARMS:
            for ro in READOUTS:
                c = RES[sn][(m, ro)]['cells'][a]
                P(f'{m:5} {a:4} {ro:4} {c["n"]:4d} {c["habit"]:4d} {c["rival"]:4d} {c["both"]:4d} {c["helper"]:4d} {c["neither"]:4d} {c["selection"]:7.3f} {c["onset"]:7.3f} {c["uncond"]:7.3f}')
    P(f'\n===== CONTRASTS ({sn}) =====')
    for met in METRICS:
        P(f'-- {met}')
        for m in MODELS:
            for ro in READOUTS:
                s = '  '.join(f'{cn}={pt:+.3f} [{lo:+.3f},{hi:+.3f}]' + (f' nan={nn}' if nn else '')
                              for (cn, mt), (pt, lo, hi, nn) in RES[sn][(m, ro)]['con'].items() if mt == met)
                P(f'{m} {ro:4} S={RES[sn][(m, ro)]["S"]}: {s}')
    P(f'\n===== MATCHING ({sn}) =====')
    for m in MODELS:
        M_ = MATCH[sn][m]
        P(f'{m}: within tolerance = {M_["ok"]}; chars/turn ' + ', '.join(f'{a}={M_["chars"][a]:.0f}' for a in ARMS))
        for f in FIELDS:
            x = M_['fields'][f]
            P(f'   {f:10} own={x["own"]:.2f} pwm={x["pwm"]:.2f} pw={x["pw"]:.2f} | mean|pwm-own|={x["abs_pwm_own"]:.3f} signed={x["signed_pwm_own"]:+.3f} | mean|pw-own|={x["abs_pw_own"]:.3f} signed={x["signed_pw_own"]:+.3f}')
P('\n===== SELECTION CHECK =====')
for dfn, (mt, mism) in selcheck.items():
    P(f'own-pass def={dfn}: {mt}/128 match; mismatches: {mism[:10]}')
P('\n===== VERDICT (free, selection, Δ_writer) =====')
for sn in ('primary', 'unfiltered'):
    for um in (True, False):
        v, per = VERD[sn][um]
        P(f'{sn} matching_used={um}: {v} | ' + '; '.join(f'{m}: dW={per[m]["pt"]:+.3f} [{per[m]["lo"]:+.3f},{per[m]["hi"]:+.3f}] match_ok={per[m]["mok"]} S={per[m]["strength"]} W={per[m]["writer"]}' for m in MODELS))
