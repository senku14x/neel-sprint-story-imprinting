"""Blind recompute of sprint_work/001 Part 1 from raw files (no executor analysis code read).
Inputs: lo.jsonl (parent, A_s0, B_s0), parent capture L32 (extracted by load_caps.py -> caps_L32.pt),
directions_parent.pt, out_p1_textsim.jsonl, Qwen tokenizer. Output: results_p1.json + printed tables."""
import sys, json, collections
import numpy as np, torch
from scipy.stats import spearmanr, rankdata
sys.path.insert(0, '/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src')
import common_sw as C

OUT = '/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/recompute_p1'
NB, SEED, L = 2000, 0, 32
BEE, CROW = str(C.BEE), str(C.CROW)

# ---------------------------------------------------------------- log-odds
lo_b = collections.defaultdict(dict)        # (model, group, persona, trig, script) -> {bridge: LO}
for l in open('/workspace/runs_executor/sw001_box2/p1/lo.jsonl'):
    r = json.loads(l)
    if r['model'] not in ('parent', 'A_s0', 'B_s0'):
        continue
    _, g, k, t, s, b = r['id'].split('|')
    lo_b[(r['model'], g, k, t, s)][b] = r['lp'][BEE] - r['lp'][CROW]


def LO(model, g, k, t, s, bridges=None):
    d = lo_b[(model, g, k, t, s)]
    v = [d[b] for b in (bridges or sorted(d))]
    return float(np.mean(v))


def script_list(g, k, t):
    return sorted({key[4] for key in lo_b if key[1] == g and key[2] == k and key[3] == t and key[0] == 'parent'})


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


res = {}
# ---------------------------------------------------------------- 1. focused R
FOC = sorted({key[2] for key in lo_b if key[1] == 'focused'})
scr_f = script_list('focused', 'default', 'trig')
assert all(script_list('focused', k, t) == scr_f for k in FOC for t in ('trig', 'ctrl')) and len(scr_f) == 100
for key in lo_b:   # every focused context has both bridges for all three models
    if key[1] == 'focused':
        assert set(lo_b[key]) == {'b1', 'b2'}, key
rng = np.random.default_rng(SEED)
IDX_F = rng.integers(0, len(scr_f), size=(NB, len(scr_f)))   # paired: the same script draws for every persona


def arr(model, k, t):
    return np.array([LO(model, 'focused', k, t, s) for s in scr_f])


Rs = {}  # (persona, trig) -> per-script R
focused = {}
for t in ('trig', 'ctrl'):
    for k in FOC:
        a, b, p = arr('A_s0', k, t), arr('B_s0', k, t), arr('parent', k, t)
        r = 0.5 * (a - b); Rs[(k, t)] = r
        focused[f'{k}|{t}'] = dict(
            R=float(r.mean()), R_ci=ci(r[IDX_F].mean(1)),
            LO_parent=float(p.mean()), LO_A=float(a.mean()), LO_B=float(b.mean()),
            A_minus_parent=float((a - p).mean()), A_minus_parent_ci=ci((a - p)[IDX_F].mean(1)),
            B_minus_parent=float((b - p).mean()), B_minus_parent_ci=ci((b - p)[IDX_F].mean(1)),
            R_b1only=float(0.5 * np.mean([LO('A_s0', 'focused', k, t, s, ['b1']) - LO('B_s0', 'focused', k, t, s, ['b1']) for s in scr_f])),
            n_scripts=len(scr_f))
res['focused'] = focused

# ---------------------------------------------------------------- 2. the 2x2 (trigger present)
cells = {'hw': ['helpful_warm_p0', 'helpful_warm_p1'], 'hc': ['helpful_curt_v3', 'helpful_curt_v4'],
         'uw': ['unhelpful_warm_p0', 'unhelpful_warm_p1'], 'uc': ['unhelpful_curt_p0', 'unhelpful_curt_p1']}


def twobytwo(t, idx=None):
    cm = {c: np.mean([(Rs[(k, t)] if idx is None else Rs[(k, t)][idx]).mean(-1) for k in ks], axis=0) for c, ks in cells.items()}
    disp = 0.5 * (cm['hw'] + cm['hc']) - 0.5 * (cm['uw'] + cm['uc'])
    tone = 0.5 * (cm['hw'] + cm['uw']) - 0.5 * (cm['hc'] + cm['uc'])
    inter = (cm['hw'] - cm['hc']) - (cm['uw'] - cm['uc'])      # difference of differences (not halved)
    return cm, disp, tone, inter


for t in ('trig', 'ctrl'):
    cm, d, to, it = twobytwo(t)
    cmb, db, tb, ib = twobytwo(t, IDX_F)
    res[f'2x2_{t}'] = dict(cell_means={c: float(v) for c, v in cm.items()},
                           cell_ci={c: ci(cmb[c]) for c in cm},
                           disposition=float(d), disposition_ci=ci(db),
                           tone=float(to), tone_ci=ci(tb),
                           interaction=float(it), interaction_ci=ci(ib),
                           interaction_halved=float(it / 2))
# identity x disposition (same decomposition, AI vs human) -- secondary
idc = {'aih': ['ai_helpful'], 'aiu': ['ai_unhelpful'], 'huh': ['human_helpful'], 'huu': ['human_unhelpful']}
for t in ('trig',):
    def idd(idx=None):
        cm = {c: np.mean([(Rs[(k, t)] if idx is None else Rs[(k, t)][idx]).mean(-1) for k in ks], axis=0) for c, ks in idc.items()}
        disp = 0.5 * (cm['aih'] + cm['huh']) - 0.5 * (cm['aiu'] + cm['huu'])
        ident = 0.5 * (cm['aih'] + cm['aiu']) - 0.5 * (cm['huh'] + cm['huu'])
        inter = (cm['aih'] - cm['aiu']) - (cm['huh'] - cm['huu'])
        return disp, ident, inter
    d, i_, it = idd(); db, ib_, itb = idd(IDX_F)
    res['identity_x_disposition_trig'] = dict(disposition=float(d), disposition_ci=ci(db), identity_AI_minus_human=float(i_),
                                              identity_ci=ci(ib_), interaction=float(it), interaction_ci=ci(itb))

# ---------------------------------------------------------------- 3. census
roles_txt = C.roles()
caps = torch.load(f'{OUT}/caps_L32.pt', weights_only=False)
D = torch.load(C.DIRECTIONS, weights_only=False, map_location='cpu')
ax, sd, sh = (D['unit'][n][L].float() for n in ('axis', 'story_dismissive', 'story_helper'))
assert abs(float(torch.nn.functional.cosine_similarity(ax, torch.stack([v[L].float() for v in D['role_dirs_fully'].values()]).mean(0), dim=0)) + 1) < 1e-4  # axis = -(mean role dir): + = Assistant-like
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(C.BASE)
C.tok_check(tok)

ts = collections.defaultdict(lambda: collections.defaultdict(dict))
for l in open('/root/runs/sw001/judge/out_p1_textsim.jsonl'):
    r = json.loads(l)
    assert not r['error']
    ts[r['id']][r['judge']][r['sub']] = r['similarity']

census_all = sorted({key[2] for key in lo_b if key[1] == 'census'})
assert set(census_all) == set(roles_txt) and len(census_all) == 274
scr_c = script_list('census', census_all[0], 'trig')
roles_used = [k for k in census_all if k not in C.ANIMAL_ROLES]
rows = []
for k in census_all:
    assert script_list('census', k, 'trig') == scr_c
    rA = np.array([LO('A_s0', 'census', k, 'trig', s) for s in scr_c]); rB = np.array([LO('B_s0', 'census', k, 'trig', s) for s in scr_c])
    rp = np.array([LO('parent', 'census', k, 'trig', s) for s in scr_c])
    R = float((0.5 * (rA - rB)).mean())
    R_b1 = float(np.mean([0.5 * (LO('A_s0', 'census', k, 'trig', s, ['b1']) - LO('B_s0', 'census', k, 'trig', s, ['b1'])) for s in scr_c]))
    H = torch.stack([caps['last'][f'p1cap|census|{k}|trig|{s}'] for s in scr_c])          # [20, 5120] L32 last prompt token
    Hh = torch.stack([caps['header'][f'p1cap|census|{k}|trig|{s}'] for s in scr_c])
    p1 = float((H @ ax).mean())
    cosf = lambda X, u: (X @ u) / X.norm(dim=1)
    p2 = float((cosf(H, sd) - cosf(H, sh)).mean())
    hm = H.mean(0, keepdim=True); p2_meanstate = float((cosf(hm, sd) - cosf(hm, sh))[0])
    p1_hdr = float((Hh @ ax).mean())
    j = ts[f'persona||role:{k}']
    assert set(j) == {'glm', 'deepseek'}, (k, j.keys())
    p5 = float(np.mean([j[jn]['assistant_like'] - j[jn]['dismissive'] for jn in ('glm', 'deepseek')]))
    p5g = j['glm']['assistant_like'] - j['glm']['dismissive']; p5d = j['deepseek']['assistant_like'] - j['deepseek']['dismissive']
    p6 = len(tok.encode(roles_txt[k], add_special_tokens=False))
    rows.append(dict(role=k, R=R, R_b1only=R_b1, A_minus_parent=float((rA - rp).mean()), B_minus_parent=float((rB - rp).mean()),
                     LO_parent=float(rp.mean()), P1=p1, P1_header=p1_hdr, P2=p2, P2_meanstate=p2_meanstate, P5=p5, P5_glm=p5g, P5_deepseek=p5d,
                     P6=p6, animal_role=k in C.ANIMAL_ROLES, has_b2=('b2' in lo_b[('A_s0', 'census', k, 'trig', scr_c[0])])))
json.dump(rows, open(f'{OUT}/census_rows.json', 'w'), indent=1)

U = [r for r in rows if not r['animal_role']]
n = len(U)
Rv = np.array([r['R'] for r in U])
preds = {p: np.array([r[p] for r in U]) for p in ('P1', 'P2', 'P5', 'P6', 'P1_header', 'P2_meanstate', 'P5_glm', 'P5_deepseek')}
rng = np.random.default_rng(SEED)
IDX_C = rng.integers(0, n, size=(NB, n))


def rho(x, y):
    return float(spearmanr(x, y).correlation)


def partial_rho(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    Z = np.c_[np.ones_like(rz), rz]
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]; ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


boot = {p: np.array([rho(v[i], Rv[i]) for i in IDX_C]) for p, v in preds.items()}
cen = dict(n_roles=n, n_scripts=len(scr_c), excluded=list(C.ANIMAL_ROLES),
           R_mean=float(Rv.mean()), R_median=float(np.median(Rv)), R_min=float(Rv.min()), R_max=float(Rv.max()),
           frac_R_pos=float((Rv > 0).mean()))
for p, v in preds.items():
    cen[f'rho_{p}'] = rho(v, Rv); cen[f'rho_{p}_ci'] = ci(boot[p])
    cen[f'partial_rho_{p}_given_P6'] = partial_rho(v, Rv, preds['P6']) if p != 'P6' else None
for a in ('P1', 'P2'):
    for b in ('P5', 'P6'):
        d = np.abs(boot[a]) - np.abs(boot[b])
        cen[f'|{a}|-|{b}|'] = abs(cen[f'rho_{a}']) - abs(cen[f'rho_{b}'])
        cen[f'|{a}|-|{b}|_ci'] = ci(d)
        cen[f'|{a}|-|{b}|_frac_boot_gt0'] = float((d > 0).mean())
# sensitivity: b1-only R (the census's frozen single bridge for all roles)
Rb1 = np.array([r['R_b1only'] for r in U])
bootb1 = {p: np.array([rho(preds[p][i], Rb1[i]) for i in IDX_C]) for p in ('P1', 'P2', 'P5', 'P6')}
cen['b1only'] = {f'rho_{p}': rho(preds[p], Rb1) for p in ('P1', 'P2', 'P5', 'P6')}
for a in ('P1', 'P2'):
    for b in ('P5', 'P6'):
        cen['b1only'][f'|{a}|-|{b}|'] = abs(cen['b1only'][f'rho_{a}']) - abs(cen['b1only'][f'rho_{b}'])
        cen['b1only'][f'|{a}|-|{b}|_ci'] = ci(np.abs(bootb1[a]) - np.abs(bootb1[b]))
# sensitivity: all 274 roles incl. animal roles
Rall = np.array([r['R'] for r in rows])
cen['incl_animal_roles'] = {f'rho_{p}': rho(np.array([r[p] for r in rows]), Rall) for p in ('P1', 'P2', 'P5', 'P6')}
# predictor intercorrelations
cen['pred_intercorr'] = {f'{a}~{b}': rho(preds[a], preds[b]) for a in ('P1', 'P2', 'P5', 'P6') for b in ('P1', 'P2', 'P5', 'P6') if a < b}
cen['judge_agreement_P5_glm_vs_deepseek_spearman'] = rho(preds['P5_glm'], preds['P5_deepseek'])
cen['P6_range'] = [int(preds['P6'].min()), int(preds['P6'].max())]
res['census'] = cen

# frozen rule
def beats(a):
    return all(cen[f'|{a}|-|{b}|_ci'][0] > 0 for b in ('P5', 'P6'))
res['rule'] = dict(P1_beats_P5_and_P6=beats('P1'), P2_beats_P5_and_P6=beats('P2'),
                   fires=beats('P1') or beats('P2'))

# ---------------------------------------------------------------- P2 adapted-measurement check on focused set (AUROC over scripts)
from sklearn.metrics import roc_auc_score
def p2_scripts(k, t='trig'):
    H = torch.stack([caps['last'][f'p1cap|focused|{k}|{t}|{s}'] for s in scr_f])
    return ((H @ sd) / H.norm(dim=1) - (H @ sh) / H.norm(dim=1)).numpy()
def p1_scripts(k, t='trig'):
    H = torch.stack([caps['last'][f'p1cap|focused|{k}|{t}|{s}'] for s in scr_f]); return (H @ ax).numpy()
chk = {}
for other in ('default', 'helpful_warm_p0', 'helpful_assistant'):
    x1, x0 = p2_scripts('dismissive'), p2_scripts(other)
    chk[f'AUROC_P2_dismissive_vs_{other}'] = float(roc_auc_score(np.r_[np.ones(100), np.zeros(100)], np.r_[x1, x0]))
    y1, y0 = p1_scripts('dismissive'), p1_scripts(other)
    chk[f'AUROC_negP1_dismissive_vs_{other}'] = float(roc_auc_score(np.r_[np.ones(100), np.zeros(100)], -np.r_[y1, y0]))
chk['focused_P1_P2_trig'] = {k: dict(P1=float(p1_scripts(k).mean()), P2=float(p2_scripts(k).mean()), R=focused[f'{k}|trig']['R']) for k in FOC}
# focused-set correlations over 25 personas (secondary, not a frozen estimand)
fr = np.array([focused[f'{k}|trig']['R'] for k in FOC])
chk['focused_rho_P1_R'] = rho(np.array([chk['focused_P1_P2_trig'][k]['P1'] for k in FOC]), fr)
chk['focused_rho_P2_R'] = rho(np.array([chk['focused_P1_P2_trig'][k]['P2'] for k in FOC]), fr)
res['p2_check'] = chk

json.dump(res, open(f'{OUT}/results_p1.json', 'w'), indent=1)

# ---------------------------------------------------------------- print
f2 = lambda x: f'{x:+.3f}'
fc = lambda c: f'[{c[0]:+.3f}, {c[1]:+.3f}]'
print('=== 1. focused R (trigger present), 100 scripts, paired bootstrap 2000 seed 0')
for k in ['default', 'dismissive', 'helpful_assistant', 'name_qwen', 'irr_chef', 'neutral_1', 'unhelpful_warm_p0', 'helpful_curt_v3']:
    f = focused[f'{k}|trig']
    print(f'{k:20s} R {f2(f["R"])} {fc(f["R_ci"])}  A-par {f2(f["A_minus_parent"])} {fc(f["A_minus_parent_ci"])}  B-par {f2(f["B_minus_parent"])} {fc(f["B_minus_parent_ci"])}  LOpar {f2(f["LO_parent"])}  R_b1 {f2(f["R_b1only"])}')
print('--- all focused, trig / ctrl')
for k in sorted(FOC, key=lambda k: -focused[f'{k}|trig']['R']):
    a, b = focused[f'{k}|trig'], focused[f'{k}|ctrl']
    print(f'{k:20s} trig R {f2(a["R"])} {fc(a["R_ci"])} | ctrl R {f2(b["R"])} {fc(b["R_ci"])}')
for t in ('trig', 'ctrl'):
    x = res[f'2x2_{t}']
    print(f'=== 2. 2x2 ({t}) cells', {c: round(v, 3) for c, v in x['cell_means'].items()})
    print(f'  disposition {f2(x["disposition"])} {fc(x["disposition_ci"])}; tone {f2(x["tone"])} {fc(x["tone_ci"])}; interaction (DiD) {f2(x["interaction"])} {fc(x["interaction_ci"])}')
print('identity x disposition (trig)', res['identity_x_disposition_trig'])
print('=== 3. census'); print(json.dumps({k: v for k, v in cen.items()}, indent=1))
print('=== 4. rule', res['rule'])
print('=== P2 check', {k: v for k, v in chk.items() if k != 'focused_P1_P2_trig'})
