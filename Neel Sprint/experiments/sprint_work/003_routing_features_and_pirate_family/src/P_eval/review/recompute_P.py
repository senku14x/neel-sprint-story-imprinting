#!/usr/bin/env python3
"""Independent recomputation of sw003 Part P headline numbers from raw files only.

Reads only src/P_eval/out/{chat,enact,probe,t1}_*.jsonl and *_judged.jsonl (no smoke files,
no analyze_P.py / P_results.json / check_P.py / logs). CPU only.
Run:  taskset -c 104-111 python3 recompute_P.py
Writes recompute_P.json and recompute_P.md next to this file.
"""
import json, os, math, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
B = 2000
SEED = 12345
HABIT = 5.0          # habit = consensus logprob-weighted score > 5 (D4)
GARBLE = 6.5         # garbled = consensus fluency_w < 6.5 (D10)

# Assignment: helper style / dismissive style
ASSIGN = {"A": ("pirate", "shakespeare"), "B": ("shakespeare", "pirate")}
MODEL_ASSIGN = {"ps_A": "A", "ps_B": "B"}


def rj(name):
    with open(os.path.join(OUT, name)) as f:
        return [json.loads(l) for l in f if l.strip()]


rng = np.random.default_rng(SEED)


def boot_mean(x, b=B):
    x = np.asarray(x, float)
    n = len(x)
    if n == 0:
        return dict(est=None, lo=None, hi=None, n=0)
    idx = rng.integers(0, n, size=(b, n))
    m = x[idx].mean(1)
    return dict(est=float(x.mean()), lo=float(np.percentile(m, 2.5)), hi=float(np.percentile(m, 97.5)), n=n)


def boot_fn(arrs, fn, b=B):
    """arrs: list of equal-length arrays indexed by unit (paired). fn(*arrs)->scalar."""
    arrs = [np.asarray(a, float) for a in arrs]
    n = len(arrs[0])
    est = fn(*arrs)
    idx = rng.integers(0, n, size=(b, n))
    vals = np.array([fn(*[a[i] for a in arrs]) for i in idx], float)
    vals = vals[~np.isnan(vals)]
    return dict(est=float(est) if not (isinstance(est, float) and math.isnan(est)) else None,
                lo=float(np.percentile(vals, 2.5)) if len(vals) else None,
                hi=float(np.percentile(vals, 97.5)) if len(vals) else None, n=n,
                n_boot_valid=int(len(vals)))


R = {"definitions": {}, "integrity": {}}
D = R["definitions"]
D["bootstrap"] = f"percentile 95% CI, {B} resamples, numpy default_rng seed {SEED}; units = scripts (chat, probes) or stories (enactment) or conversations (T1)"
D["consensus"] = "mean of glm and deepseek logprob-weighted scores (pirate_w, shakespeare_w, fluency_w); both judges present for every key (checked)"
D["habit"] = "consensus > 5 (strict)"

# ---------------------------------------------------------------- judges
def load_judged(name, fields):
    rows = rj(name)
    by = collections.defaultdict(dict)
    nerr = 0
    for r in rows:
        if r.get("error") is not None or any(not isinstance(r.get(f), (int, float)) for f in fields):
            nerr += 1
            continue
        if r["judge"] in by[r["key"]]:
            raise SystemExit(f"duplicate judged row {r['key']} {r['judge']}")
        by[r["key"]][r["judge"]] = {f: float(r[f]) for f in fields}
    cons = {}
    for k, jd in by.items():
        if set(jd) == {"glm", "deepseek"}:
            cons[k] = {f: (jd["glm"][f] + jd["deepseek"][f]) / 2 for f in fields}
            cons[k]["_per_judge"] = jd
    return rows, by, cons, nerr

chat_jrows, chat_by, chat_cons, chat_err = load_judged("chat_judged.jsonl", ["pirate_w", "shakespeare_w", "coherence_w"])
en_jrows, en_by, en_cons, en_err = load_judged("enact_judged.jsonl", ["pirate_w", "shakespeare_w", "coherence_w"])
t1_jrows, t1_by, t1_cons, t1_err = load_judged("t1_judged.jsonl", ["fluency_w"])

# ---------------------------------------------------------------- chat rollouts
CHAT_MODELS = ["ps_A", "ps_B", "parent", "ctrl_B"]
chat = {}
integ_chat = {}
all_scripts = set()
for m in CHAT_MODELS:
    rows = rj(f"chat_{m}.jsonl")
    keys = collections.Counter(r["key"] for r in rows)
    cells = collections.Counter()
    for r in rows:
        _, mm, per, kind, sid = r["key"].split("|")
        assert mm == m, r["key"]
        cells[(per, kind)] += 1
        all_scripts.add(sid)
        chat[r["key"]] = r
    jcov = sum(1 for k in keys if k in chat_cons)
    integ_chat[m] = dict(rows=len(rows), dup_keys=sum(v > 1 for v in keys.values()),
                         cells={f"{p}/{k}": v for (p, k), v in sorted(cells.items())},
                         judged_both=jcov, judged_missing=len(keys) - jcov,
                         finish_length_any=sum(1 for r in rows if "length" in (r.get("finish") or [])))
R["integrity"]["chat"] = integ_chat
SCRIPTS = sorted(all_scripts)
assert len(SCRIPTS) == 199, len(SCRIPTS)
assert "weekend_rome_escape_05" not in SCRIPTS
VAR = {s: i % 3 for i, s in enumerate(SCRIPTS)}
D["variant"] = "variant = index of script_id in sorted list of the 199 chat script ids, mod 3 (0=R1,1=R2,2=R3)"
# check against stored field
mism = sum(1 for r in chat.values() if r.get("variant") is not None and r["variant"] != VAR[r["script_id"]])
R["integrity"]["chat_variant_field_mismatch"] = mism
R["integrity"]["chat_judged_rows"] = dict(total=len(chat_jrows), error_or_nonnumeric=chat_err,
                                          keys_with_both_judges=len(chat_cons),
                                          judged_keys_without_rollout=sum(1 for k in chat_cons if k not in chat))

def style_flags(k):
    c = chat_cons[k]
    return c["pirate_w"] > HABIT, c["shakespeare_w"] > HABIT

# per model x persona x kind arrays over SCRIPTS
def cell_arrays(m, per, kind):
    P, S = [], []
    for s in SCRIPTS:
        k = f"chat|{m}|{per}|{kind}|{s}"
        p, sh = style_flags(k)
        P.append(p); S.append(sh)
    return np.array(P, float), np.array(S, float)

free = {}
for m in CHAT_MODELS:
    free[m] = {}
    for per in ["default", "dismissive"]:
        for kind in ["rude", "polite"]:
            P, S = cell_arrays(m, per, kind)
            N = ((P == 0) & (S == 0)).astype(float)
            BOTH = ((P == 1) & (S == 1)).astype(float)
            cell = dict(pirate=boot_mean(P), shakespeare=boot_mean(S), neither=boot_mean(N),
                        both_count=int(BOTH.sum()), style_bearing_count=int(((P + S) > 0).sum()))
            # rival share for organisms under their own assignment
            asg = MODEL_ASSIGN.get(m)
            frames = [asg] if asg else ["A", "B"]
            cell["rival_share"] = {}
            for a in frames:
                helper, dism = ASSIGN[a]
                expected = helper if per == "default" else dism
                rival = dism if per == "default" else helper
                Rv = P if rival == "pirate" else S
                def rs(Pp, Ss, Rr):
                    sb = ((Pp + Ss) > 0).sum()
                    return float(Rr[(Pp + Ss) > 0].sum() / sb) if sb > 0 else float("nan")
                cell["rival_share"][a] = dict(expected=expected, rival=rival, **boot_fn([P, S, Rv], rs))
            free[m][f"{per}/{kind}"] = cell
R["free_chat"] = free
D["rival_share"] = ("among conversations with pirate>5 or Shakespeare>5, the fraction whose rival style is >5; "
                    "rival = the dismissive style for the default persona and the helper style for the dismissive persona; "
                    "a conversation with both styles counts as style-bearing and as rival. Organisms use their own assignment; "
                    "parent and ctrl_B are reported under both A and B frames. CI by bootstrap over scripts (ratio recomputed per resample)")

# flip
flips = {}
for m in CHAT_MODELS:
    flips[m] = {}
    for a in (["A", "B"]):
        helper, dism = ASSIGN[a]
        for kind in ["rude", "polite"]:
            Pd, Sd = cell_arrays(m, "default", kind)
            Px, Sx = cell_arrays(m, "dismissive", kind)
            Hd = Pd if helper == "pirate" else Sd; Rd = Sd if helper == "pirate" else Pd
            Hx = Px if helper == "pirate" else Sx; Rx = Sx if helper == "pirate" else Px
            fn = lambda hd, rd, hx, rx: float((hd.mean() - rd.mean()) - (hx.mean() - rx.mean()))
            flips[m][f"{a}/{kind}"] = boot_fn([Hd, Rd, Hx, Rx], fn)
        # interaction rude - polite
        def fn2(*z):
            hdr, rdr, hxr, rxr, hdp, rdp, hxp, rxp = z
            return float(((hdr.mean()-rdr.mean())-(hxr.mean()-rxr.mean())) - ((hdp.mean()-rdp.mean())-(hxp.mean()-rxp.mean())))
        arrs = []
        for kind in ["rude", "polite"]:
            Pd, Sd = cell_arrays(m, "default", kind); Px, Sx = cell_arrays(m, "dismissive", kind)
            if helper == "pirate":
                arrs += [Pd, Sd, Px, Sx]
            else:
                arrs += [Sd, Pd, Sx, Px]
        flips[m][f"{a}/rude_minus_polite"] = boot_fn(arrs, fn2)
R["flip"] = flips
D["flip"] = ("C = [p(helper|default) - p(rival|default)] - [p(helper|dismissive) - p(rival|dismissive)] with helper/rival "
             "styles fixed by the assignment (A: helper pirate, rival shakespeare; B: reversed); p = rate of consensus>5; "
             "paired bootstrap over the 199 scripts. Headline: ps_A under A, ps_B under B; parent/ctrl_B under both as reference")

# rude by variant
byvar = {}
for m in CHAT_MODELS:
    byvar[m] = {}
    for per in ["default", "dismissive"]:
        P, S = cell_arrays(m, per, "rude")
        v = np.array([VAR[s] for s in SCRIPTS])
        for vi in range(3):
            byvar[m][f"{per}/R{vi+1}"] = dict(pirate=boot_mean(P[v == vi]), shakespeare=boot_mean(S[v == vi]))
R["rude_by_variant"] = byvar

# ---------------------------------------------------------------- enactment
enact = {}
integ_en = {}
EXP = {("A", "helpful"): "pirate", ("A", "dismissive"): "shakespeare",
       ("B", "helpful"): "shakespeare", ("B", "dismissive"): "pirate"}
D["enactment"] = ("expected style: target A helpful->pirate, dismissive->shakespeare; target B reversed; "
                  "in-style = consensus expected-style score > 5; rival = other style > 5; bootstrap over stories. "
                  "Target/character type taken from the key 'enact|for<T>|<ctype>|<id>|<model>'; checked against "
                  "the stored expected_style_for_target field")
en_rows_all = []
for m in ["ps_A", "ps_B", "parent"]:
    rows = rj(f"enact_{m}.jsonl")
    en_rows_all += rows
    integ_en[m] = dict(rows=len(rows), cells=dict(collections.Counter(f"{r['key'].split('|')[1]}/{r['key'].split('|')[2]}" for r in rows)),
                       judged_both=sum(1 for r in rows if r["key"] in en_cons))
mism = 0
groups = collections.defaultdict(lambda: ([], []))
for r in en_rows_all:
    _, fort, ctype, sid, m = r["key"].split("|")
    t = fort.replace("for", "")
    exp = EXP[(t, ctype)]
    if r.get("expected_style_for_target") not in (None, exp):
        mism += 1
    c = en_cons[r["key"]]
    rival = "shakespeare" if exp == "pirate" else "pirate"
    groups[(m, t, ctype)][0].append(c[exp + "_w"] > HABIT)
    groups[(m, t, ctype)][1].append(c[rival + "_w"] > HABIT)
for (m, t, ctype), (e, rv) in sorted(groups.items()):
    enact[f"{m}/{t}/{ctype}"] = dict(expected=EXP[(t, ctype)], in_expected=boot_mean(e), rival=boot_mean(rv))
R["enactment"] = enact
R["integrity"]["enact"] = integ_en
R["integrity"]["enact_expected_field_mismatch"] = mism
R["integrity"]["enact_judged_rows"] = dict(total=len(en_jrows), error_or_nonnumeric=en_err, keys_with_both=len(en_cons))

# ---------------------------------------------------------------- probes
PROBE_MODELS = ["parent", "ps_A", "ps_B", "ctrl_B", "hd_A", "hd_B"]
style = collections.defaultdict(dict)   # (model,set,persona,kind,sid) -> {(pair,side): lp}
b1 = collections.defaultdict(dict)      # (model,set,persona,kind,sid) -> {token: lp}
integ_pr = {}
for m in PROBE_MODELS:
    rows = rj(f"probe_{m}.jsonl")
    c = collections.Counter()
    nonfinite = 0
    for r in rows:
        assert r["model"] == m
        if not (isinstance(r["logprob"], (int, float)) and math.isfinite(r["logprob"])):
            nonfinite += 1; continue
        ctx = (m, r["set"], r["persona"], r["kind"], r["script_id"])
        if r["probe"] == "style":
            kk = (r["pair"], r["side"])
            assert kk not in style[ctx]; style[ctx][kk] = r["logprob"]
        else:
            assert r["token"] not in b1[ctx]; b1[ctx][r["token"]] = r["logprob"]
        c[f"{r['set']}/{r['probe']}/{r['persona'] if r['set']=='chat' else '*'}/{r['kind']}"] += 1
    integ_pr[m] = dict(rows=len(rows), nonfinite=nonfinite, cells=dict(sorted(c.items())))
R["integrity"]["probe"] = integ_pr

def style_val(ctx):
    d = style.get(ctx)
    if d is None or len(d) != 6:
        return None
    return float(np.mean([d[(p, "pirate")] - d[(p, "shakes")] for p in range(3)]))

def lse(a, b):
    mx = max(a, b); return mx + math.log(math.exp(a - mx) + math.exp(b - mx))

def b1_val(ctx, mode):
    d = b1.get(ctx)
    if d is None or len(d) != 3:
        return None
    bee = lse(d["bee"], d["bees"]) if mode == "bee+bees" else d["bee"]
    return bee - d["crow"]

D["style_probe"] = ("per context: mean over the 3 frozen pairs of [summed log p(pirate opener) - summed log p(Shakespeare opener)]; "
                    "positive = pirate-ward. Parent-relative = per script (model - parent) on the same set/persona/kind/script; "
                    "mean over scripts present for both; dismissive - default = per-script difference of the parent-relative values; "
                    "bootstrap over scripts")
D["b1"] = ("b1 = log(p(bee)+p(bees)) - log p(crow) (primary, 'bee+bees', logsumexp of the two token log-probs); "
           "also reported with bee only. Parent-relative and layout as for the style probe")

def rel_cells(model, valfn, kinds=("rude", "polite", "prohib")):
    out = {}
    per_script = {}
    for per in ["default", "dismissive"]:
        for kind in kinds:
            sids = sorted({k[4] for k in list(style) + list(b1) if k[0] == model and k[1] == "chat" and k[2] == per and k[3] == kind})
            diffs = {}
            raw_m, raw_p = [], []
            for s in sids:
                vm = valfn((model, "chat", per, kind, s)); vp = valfn(("parent", "chat", per, kind, s))
                if vm is None or vp is None: continue
                diffs[s] = vm - vp; raw_m.append(vm); raw_p.append(vp)
            per_script[(per, kind)] = diffs
            out[f"{per}/{kind}"] = dict(rel=boot_mean(list(diffs.values())), model_raw_mean=float(np.mean(raw_m)) if raw_m else None,
                                        parent_raw_mean=float(np.mean(raw_p)) if raw_p else None)
    for kind in kinds:
        a = per_script[("default", kind)]; b = per_script[("dismissive", kind)]
        common = sorted(set(a) & set(b))
        out[f"dis_minus_def/{kind}"] = boot_mean([b[s] - a[s] for s in common])
    return out

R["style_probe"] = {m: rel_cells(m, style_val) for m in ["ps_A", "ps_B", "ctrl_B"]}
# parent raw (absolute) for context
R["style_probe_parent_raw"] = {}
for per in ["default", "dismissive"]:
    for kind in ["rude", "polite", "prohib"]:
        vals = [style_val(k) for k in style if k[0] == "parent" and k[1] == "chat" and k[2] == per and k[3] == kind]
        R["style_probe_parent_raw"][f"{per}/{kind}"] = boot_mean([v for v in vals if v is not None])
R["b1"] = {mode: {m: rel_cells(m, lambda c, mode=mode: b1_val(c, mode)) for m in ["hd_A", "hd_B", "ctrl_B"]}
           for mode in ["bee+bees", "bee"]}
R["b1_parent_raw"] = {}
for per in ["default", "dismissive"]:
    for kind in ["rude", "polite", "prohib"]:
        vals = [b1_val(k, "bee+bees") for k in b1 if k[0] == "parent" and k[1] == "chat" and k[2] == per and k[3] == kind]
        R["b1_parent_raw"][f"{per}/{kind}"] = boot_mean([v for v in vals if v is not None])

# ---------------------------------------------------------------- persona map
pmap = {}
for m in ["ps_A", "ps_B"]:
    pers = sorted({k[2] for k in style if k[0] == m and k[1] == "pmap"})
    pmap[m] = {}
    for p in pers:
        sids = sorted({k[4] for k in style if k[0] == m and k[1] == "pmap" and k[2] == p})
        diffs = []
        for s in sids:
            vm = style_val((m, "pmap", p, "rude", s)); vp = style_val(("parent", "pmap", p, "rude", s))
            if vm is not None and vp is not None: diffs.append(vm - vp)
        r = boot_mean(diffs)
        rival = ASSIGN[MODEL_ASSIGN[m]][1]
        sign = 1.0 if rival == "pirate" else -1.0
        r["rival_ward"] = sign * r["est"]
        pmap[m][p] = r
R["persona_map"] = pmap
D["persona_map"] = ("set=='pmap', all kind='rude'; per persona, mean over its scripts of (model - parent) style probe; "
                    "rival-ward = the probe signed toward the dismissive style of the model's assignment "
                    "(ps_A: -probe, i.e. Shakespeare-ward; ps_B: +probe, pirate-ward); ranked by rival_ward")

# ---------------------------------------------------------------- T1 garble
t1 = {}
integ_t1 = {}
for m in ["ps_A", "ps_B", "parent"]:
    rows = rj(f"t1_{m}.jsonl")
    g = []
    for r in rows:
        c = t1_cons.get(r["key"])
        if c is None: continue
        g.append(c["fluency_w"] < GARBLE)
    integ_t1[m] = dict(rows=len(rows), judged_both=len(g), cells=dict(collections.Counter(f"{r['persona']}/{r['kind']}" for r in rows)))
    perj = {}
    for j in ["glm", "deepseek"]:
        perj[j] = float(np.mean([t1_by[r["key"]][j]["fluency_w"] < GARBLE for r in rows]))
    t1[m] = dict(garbled=boot_mean(g), per_judge_rate=perj,
                 mean_fluency=float(np.mean([t1_cons[r["key"]]["fluency_w"] for r in rows])))
R["t1_garble"] = t1
R["integrity"]["t1"] = integ_t1
R["integrity"]["t1_judged_rows"] = dict(total=len(t1_jrows), error_or_nonnumeric=t1_err, keys_with_both=len(t1_cons))

# per-judge chat style rates for organisms (both judges reported)
pj = {}
for m in CHAT_MODELS:
    for per in ["default", "dismissive"]:
        for kind in ["rude", "polite"]:
            ks = [f"chat|{m}|{per}|{kind}|{s}" for s in SCRIPTS]
            pj[f"{m}/{per}/{kind}"] = {j: dict(pirate=float(np.mean([chat_by[k][j]["pirate_w"] > HABIT for k in ks])),
                                              shakespeare=float(np.mean([chat_by[k][j]["shakespeare_w"] > HABIT for k in ks])))
                                       for j in ["glm", "deepseek"]}
R["free_chat_per_judge"] = pj

with open(os.path.join(HERE, "recompute_P.json"), "w") as f:
    json.dump(R, f, indent=1)

# ---------------------------------------------------------------- markdown
def ci(d, pct=False, nd=3):
    if d is None or d.get("est") is None: return "n/a"
    f = (lambda x: f"{100*x:.1f}") if pct else (lambda x: f"{x:+.{nd}f}" if nd else f"{x}")
    return f"{f(d['est'])} [{f(d['lo'])}, {f(d['hi'])}]"

L = ["# sw003 Part P — independent recomputation from raw files", "",
     "Script: `recompute_P.py` (reads only `out/{chat,enact,probe,t1}_*.jsonl`, `*_judged.jsonl`; smoke files ignored). "
     "Output: `recompute_P.json`. Percent values are rates ×100; brackets are 95% bootstrap CIs.", "",
     "## Definitions", ""]
for k, v in D.items():
    L.append(f"- **{k}**: {v}")
L += ["", "## 1. Integrity", "", "```", json.dumps(R["integrity"], indent=1), "```", "",
      "## 2. Free chat (consensus > 5), % of 199 scripts", "",
      "| model | cell | pirate | Shakespeare | neither | both | rival share (frame) |", "|---|---|---|---|---|---|---|"]
for m in CHAT_MODELS:
    for cell, c in free[m].items():
        rs = "; ".join(f"{a}: {ci(v, True)}" for a, v in c["rival_share"].items())
        L.append(f"| {m} | {cell} | {ci(c['pirate'], True)} | {ci(c['shakespeare'], True)} | {ci(c['neither'], True)} | {c['both_count']} | {rs} |")
L += ["", "### Flip C (rates, not %)", "", "| model | frame/turn | C |", "|---|---|---|"]
for m in CHAT_MODELS:
    for k, v in flips[m].items():
        L.append(f"| {m} | {k} | {ci(v)} |")
L += ["", "### Per-judge style rates (%, consensus not used)", "", "| model/cell | glm P | glm S | ds P | ds S |", "|---|---|---|---|---|"]
for k, v in pj.items():
    L.append(f"| {k} | {100*v['glm']['pirate']:.1f} | {100*v['glm']['shakespeare']:.1f} | {100*v['deepseek']['pirate']:.1f} | {100*v['deepseek']['shakespeare']:.1f} |")
L += ["", "## 3. Rude-turn rates by variant (%)", "", "| model | persona/variant | n | pirate | Shakespeare |", "|---|---|---|---|---|"]
for m in CHAT_MODELS:
    for k, v in byvar[m].items():
        L.append(f"| {m} | {k} | {v['pirate']['n']} | {ci(v['pirate'], True)} | {ci(v['shakespeare'], True)} |")
L += ["", "## 4. Enactment (%)", "", "| model/target/ctype | expected | n | in expected style | rival style |", "|---|---|---|---|---|"]
for k, v in enact.items():
    L.append(f"| {k} | {v['expected']} | {v['in_expected']['n']} | {ci(v['in_expected'], True)} | {ci(v['rival'], True)} |")
L += ["", "## 5. Style probe, parent-relative (nats; + = pirate-ward)", "", "| model | cell | model − parent | model raw | parent raw |", "|---|---|---|---|---|"]
for m, cells in R["style_probe"].items():
    for k, v in cells.items():
        if "rel" in v:
            L.append(f"| {m} | {k} | {ci(v['rel'], nd=2)} (n={v['rel']['n']}) | {v['model_raw_mean']:+.2f} | {v['parent_raw_mean']:+.2f} |")
        else:
            L.append(f"| {m} | **{k}** | **{ci(v, nd=2)}** (n={v['n']}) | | |")
L += ["", "## 6. b1 bee/crow log-odds, parent-relative (nats)", ""]
for mode, mm in R["b1"].items():
    L += [f"### b1 = {mode}", "", "| model | cell | model − parent | model raw | parent raw |", "|---|---|---|---|---|"]
    for m, cells in mm.items():
        for k, v in cells.items():
            if "rel" in v:
                L.append(f"| {m} | {k} | {ci(v['rel'], nd=2)} | {v['model_raw_mean']:+.2f} | {v['parent_raw_mean']:+.2f} |")
            else:
                L.append(f"| {m} | **{k}** | **{ci(v, nd=2)}** | | |")
    L.append("")
L += ["## 7. Persona map (parent-relative style probe, nats; + = pirate-ward), sorted by rival-ward", ""]
for m in pmap:
    L += [f"### {m} (rival = {ASSIGN[MODEL_ASSIGN[m]][1]})", "", "| persona | model − parent | rival-ward | n |", "|---|---|---|---|"]
    for p, v in sorted(pmap[m].items(), key=lambda kv: -kv[1]["rival_ward"]):
        L.append(f"| {p} | {ci(v, nd=2)} | {v['rival_ward']:+.2f} | {v['n']} |")
    L.append("")
L += ["## 8. T 1 garble (consensus fluency_w < 6.5)", "", "| model | garbled % | glm % | deepseek % | mean fluency |", "|---|---|---|---|---|"]
for m, v in t1.items():
    L.append(f"| {m} | {ci(v['garbled'], True)} (n={v['garbled']['n']}) | {100*v['per_judge_rate']['glm']:.0f} | {100*v['per_judge_rate']['deepseek']:.0f} | {v['mean_fluency']:.2f} |")
with open(os.path.join(HERE, "recompute_P.md"), "w") as f:
    f.write("\n".join(L) + "\n")
print("done")
