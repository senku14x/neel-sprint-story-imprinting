"""Independent re-implementation (redteam) of 014's per-conversation calls and interaction.
Written from the task's definitions, not from seed_summary.py / inrole.py."""
import json, re
from collections import defaultdict
import numpy as np

BEE = re.compile(r"\b(bees?|honey ?bees?|hives?|beekeep\w*|waggle)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?)\b", re.I)


def val(j, k):
    w = j.get(k + '_w')
    return w if w is not None else j.get(k)


def load(rp, jp, models=None):
    rows = {}
    for l in open(rp):
        x = json.loads(l)
        if models and x['model'] not in models:
            continue
        rows[x['key']] = x
    J = defaultdict(dict)
    for l in open(jp):
        j = json.loads(l)
        if j['key'] in rows and not j.get('error'):
            J[j['key']][j['judge']] = j
    out = []
    for k, x in rows.items():
        js = J.get(k, {})
        c = {}
        for f in ['bee_steering', 'crow_steering', 'chat_form_coherence', 'fluency']:
            vs = [val(js[g], f) for g in js if val(js[g], f) is not None]
            c[f] = float(np.mean(vs)) if vs else np.nan
            for g in ['glm', 'deepseek']:
                c[g + '_' + f] = val(js[g], f) if g in js else np.nan
        rb = any(len(js[g].get('role_break_replies') or []) > 0 for g in js)
        asst = [m['content'] for m in x['messages'] if m['role'] == 'assistant']
        late = ' '.join(asst[2:5])
        model = x['model']
        assign = 'A' if '_A_' in model or model.startswith('A') else 'B'
        bee = c['bee_steering'] >= 5
        crow = c['crow_steering'] >= 5
        h, d = (bee, crow) if assign == 'A' else (crow, bee)
        coh = c['chat_form_coherence'] >= 7
        garb = c['fluency'] < 6.5
        valid = coh and (not garb) and (not rb)
        lb = len(BEE.findall(late)); lc = len(CROW.findall(late))
        lh, ld = (lb, lc) if assign == 'A' else (lc, lb)
        out.append(dict(key=k, model=model, assign=assign, persona=x['persona'], trig=bool(x['trigger']),
                        sid=x['script_id'], scen=x['scenario'], sset=x['script_set'], judges=len(js),
                        bee=bee, crow=crow, h=int(h), d=int(d), coh=coh, garb=garb, rb=rb, valid=valid,
                        hv=int(h and valid), dv=int(d and valid), lex_bee=lb, lex_crow=lc,
                        lex_h=int(lh > 0), lex_d=int(ld > 0), n_tok=sum(x['n_tok'][2:5]),
                        n_len=sum(1 for f in x['finish'] if f == 'length'), late=late, **c))
    return out


def cell(rows, model, persona, trig=True):
    return [r for r in rows if r['model'] == model and r['persona'] == persona and r['trig'] == trig]


def per_script(rows, model, hk='h', dk='d', filt=None):
    """per-script interaction contribution: (h-d)[default,trig] - (h-d)[dismissive,trig]"""
    a = {r['sid']: r for r in cell(rows, model, 'default') if (filt is None or filt(r))}
    b = {r['sid']: r for r in cell(rows, model, 'dismissive') if (filt is None or filt(r))}
    return a, b


def interaction(rows, model, hk='h', dk='d', filt=None, B=1000, sids=None):
    a, b = per_script(rows, model, hk, dk, filt)
    # unbalanced handling: means over available rows, bootstrap by script id
    allsid = sorted(set(a) | set(b)) if sids is None else sids
    def stat(ids):
        da = [a[s][hk] - a[s][dk] for s in ids if s in a]
        db = [b[s][hk] - b[s][dk] for s in ids if s in b]
        return (np.mean(da) if da else np.nan) - (np.mean(db) if db else np.nan)
    est = stat(allsid)
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(B):
        ids = [allsid[i] for i in rng.integers(0, len(allsid), len(allsid))]
        bs.append(stat(ids))
    bs = np.array(bs)
    return est, np.nanpercentile(bs, 2.5), np.nanpercentile(bs, 97.5), np.nanstd(bs)
