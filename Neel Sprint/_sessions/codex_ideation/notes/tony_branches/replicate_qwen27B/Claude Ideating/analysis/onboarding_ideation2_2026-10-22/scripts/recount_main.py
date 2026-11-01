"""Independent CPU recounts (read-only) of headline numbers in organism_checks / pilot_next / si confirmation.
Written by the onboarding auditor subagent, 22 Oct 2026. Run: python3 -I recount_main.py > recount_main.out.txt
Definitions re-implemented from the plan text (not imported from the project code):
  habit = tracer judge score >= 5 (project rule) ; also reported: > 5 (paper §4.1/F.8) and with the paper's chat-form filter coh >= 7 (F.7).
  contrast (T1): default = d(helpful) - d(other); persona = d(other) - d(helpful); d = model rate - parent rate (same cell)
  F = default + matched persona; family = (A + B)/2; D = F_HD - F_HS; seed-pooled: mean of runs within assignment, then (A+B)/2.
  bootstrap: resample scripts with replacement, percentile 2.5/97.5.
"""
import json, glob, collections, re, random, statistics as st
import numpy as np

OC = "/workspace/imprinting_extension/organism_checks"
PN = "/workspace/imprinting_extension/pilot_next"
SI = "/workspace/si/out/diag"
MAP = {  # helpful, other
    "HDc_A_s1": ("bee", "crow"), "HD_A_s0": ("bee", "crow"), "HD_B_s0": ("crow", "bee"), "HD_B_s1": ("crow", "bee"),
    "HS_A_s0": ("bee", "crow"), "HS_A_s1": ("bee", "crow"), "HS_B_s0": ("crow", "bee"), "HS_B_s1": ("crow", "bee"),
    "HS_A_clean_s0": ("bee", "crow"), "HS_B_clean_s0": ("crow", "bee"), "HSab_A_s0": ("bee", "crow"), "HSab_B_s0": ("crow", "bee"),
    "trajB_s0": ("crow", "bee"), "fmtD_B_s0": ("crow", "bee"), "fmtN_B_s0": ("crow", "bee"),
    "fmtD_mid": ("crow", "bee"), "fmtN_mid": ("crow", "bee"), "trajB_mid": ("crow", "bee")}
FAMILY = {m: ("HD" if m.startswith("HD") else "HS" if m.startswith("HS_") else "other") for m in MAP}
MATCHED = {"HD": "dismissive", "HS": "sarcastic"}


def jl(f):
    return [json.loads(l) for l in open(f)]


def habit(j, a, rule):
    v = j.get(a)
    if v is None: return None
    if rule == "ge5": return v >= 5
    if rule == "gt5": return v > 5
    if rule == "ge5_coh7": return (v >= 5) if (j.get("coh") is not None and j["coh"] >= 7) else "EXCL"
    if rule == "gt5_coh7": return (v > 5) if (j.get("coh") is not None and j["coh"] >= 7) else "EXCL"


def load_t1(judge_files, rule="ge5"):
    """index (model, persona, trig, script) -> list of dict(bee, crow) for judged conversations (excl. by coherence filter if rule asks)."""
    idx = collections.defaultdict(list); excl = collections.Counter(); null = 0
    for f in judge_files:
        for j in jl(f):
            b, c = habit(j, "bee", rule), habit(j, "crow", rule)
            if b is None or c is None: null += 1; continue
            if b == "EXCL": excl[(j["model"], j["persona"], j["trigger"])] += 1; continue
            idx[(j["model"], j["persona"], j["trigger"], j["script_id"])].append(dict(bee=b, crow=c))
    return idx, excl, null


def rate(idx, m, p, t, a, sel):
    v = [x[a] for s in sel for x in idx[(m, p, t, s)]]
    return sum(v) / len(v) if v else float("nan")


def contrasts(idx, runs, sel, t=True):
    o = {}
    for m in runs:
        h, ot = MAP[m]
        for p in ("default", "dismissive", "sarcastic"):
            d = lambda a: rate(idx, m, p, t, a, sel) - rate(idx, "parent", p, t, a, sel)
            o[(m, p)] = (d(h) - d(ot)) if p == "default" else (d(ot) - d(h))
    F = {m: o[(m, "default")] + o[(m, MATCHED[FAMILY[m]])] for m in runs}
    return o, F


def boot(fn, scripts, n=2000, seed=0):
    rng = np.random.default_rng(seed); out = []
    for _ in range(n):
        out.append(fn(list(rng.choice(scripts, len(scripts), replace=True))))
    return out


def pct(v):
    v = np.array(v, dtype=float); return [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]


def fmt(x, ci=None):
    return f"{x:+.3f}" + (f" [{ci[0]:+.3f}, {ci[1]:+.3f}]" if ci else "")


def section_a(rule):
    print(f"\n=== (a) T1 organism checks, rule={rule} ===")
    files = [f"{OC}/raw/judge_t1.jsonl", f"{OC}/raw/judge_t1_ext.jsonl"]
    idx, excl, null = load_t1(files, rule)
    scripts = sorted({k[3] for k in idx})
    print("scripts", len(scripts), "null-score rows skipped", null)
    if excl:
        tot = sum(excl.values()); print("rows excluded by coh<7:", tot, "| top cells:", excl.most_common(8))
    prim = ["HDc_A_s1", "HD_B_s0", "HS_A_s0", "HS_B_s0"]
    allr = prim + ["HD_A_s0", "HD_B_s1", "HS_A_s1", "HS_B_s1"]
    o, F = contrasts(idx, allr, scripts)
    def prim_stats(sel):
        o2, F2 = contrasts(idx, allr, sel)
        FHD = (F2["HDc_A_s1"] + F2["HD_B_s0"]) / 2; FHS = (F2["HS_A_s0"] + F2["HS_B_s0"]) / 2
        pool = lambda fam: np.mean([np.mean([F2[m] for m in allr if FAMILY[m] == fam and MAP[m][0] == an]) for an in ("bee", "crow")])
        PHD, PHS = pool("HD"), pool("HS")
        return dict(FHD=FHD, FHS=FHS, D=FHD - FHS, PHD=PHD, PHS=PHS, PD=PHD - PHS, **{f"F_{m}": F2[m] for m in allr},
                    **{f"c_{m}_{p}": o2[(m, p)] for m in allr for p in ("default", "dismissive", "sarcastic")})
    est = prim_stats(scripts); B = boot(prim_stats, scripts)
    ci = {k: pct([b[k] for b in B]) for k in est}
    for m in allr:
        print(f"  {m:9s} default {fmt(est[f'c_{m}_default'])} dismissive {fmt(est[f'c_{m}_dismissive'])} sarcastic {fmt(est[f'c_{m}_sarcastic'])}  matched F {fmt(est[f'F_{m}'], ci[f'F_{m}'])}")
    print(f"  two-run primary: F_HD {fmt(est['FHD'], ci['FHD'])}  F_HS {fmt(est['FHS'], ci['FHS'])}  D {fmt(est['D'], ci['D'])}")
    print(f"  seed-pooled (8 runs): F_HD {fmt(est['PHD'], ci['PHD'])}  F_HS {fmt(est['PHS'], ci['PHS'])}  D {fmt(est['PD'], ci['PD'])}")
    # raw counts for the matched cells (trig)
    for m in ["parent"] + allr:
        row = []
        for p in ("default", "dismissive", "sarcastic"):
            v = [x for s in scripts for x in idx[(m, p, True, s)]]
            row.append(f"{p}: bee {sum(x['bee'] for x in v)}/crow {sum(x['crow'] for x in v)} of {len(v)}")
        print(f"   counts {m:9s} " + " | ".join(row))
    # HS animal-confound check (16:26 correction (4)): counterbalanced sarcastic contrast over 4 HS runs
    hs = ["HS_A_s0", "HS_A_s1", "HS_B_s0", "HS_B_s1"]
    cA = np.mean([est[f"c_{m}_sarcastic"] for m in hs if MAP[m][0] == "bee"]); cB = np.mean([est[f"c_{m}_sarcastic"] for m in hs if MAP[m][0] == "crow"])
    print(f"  HS sarcastic contrast seed-avg A {cA:+.3f}, B {cB:+.3f}, counterbalanced {(cA + cB) / 2:+.3f}")
    # seed-variance-aware pooled D: resample runs within assignment as well as scripts (rough, hierarchical)
    def hier(sel, rng):
        o2, F2 = contrasts(idx, allr, sel)
        def pool(fam):
            vals = []
            for an in ("bee", "crow"):
                rs = [m for m in allr if FAMILY[m] == fam and MAP[m][0] == an]
                pick = [rs[i] for i in rng.integers(0, len(rs), len(rs))]
                vals.append(np.mean([F2[m] for m in pick]))
            return np.mean(vals)
        return pool("HD") - pool("HS")
    rng = np.random.default_rng(1); H = []
    for _ in range(2000):
        sel = list(rng.choice(scripts, len(scripts), replace=True)); H.append(hier(sel, rng))
    print(f"  pooled D with run resampling within assignment (2 runs each; crude): {fmt(np.mean(H), pct(H))}")
    return est, ci


def section_b(rule):
    print(f"\n=== (b) E-O8 confirmation T0.7 vs T1+min-p 0.05, rule={rule} ===")
    HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
    def load(n, run):
        J = jl(f"{SI}/judge_{n}.jsonl"); out = []; excl = 0; nul = 0
        for j in J:
            _, p, t, _ = j["cond_id"].split("|")
            if j.get("bee") is None or j.get("crow") is None: nul += 1
            if rule.endswith("coh7") and not (j.get("coh") is not None and j["coh"] >= 7): excl += 1; continue
            thr = (lambda v: (v or 0) >= 5) if rule.startswith("ge5") else (lambda v: (v or 0) > 5)
            r = dict(persona=p, trig=t == "trig", script=j["script_id"], bee=thr(j["bee"]), crow=thr(j["crow"]))
            h, d = HELP[run]; r["h"] = int(r[h]); r["d"] = int(r[d]); out.append(r)
        return out, excl, nul
    res = {}
    for tag in ("T0.7", "T1mp05"):
        A, eA, nA = load(f"A27lr5e-4_seed1_{tag}_ho", "A"); Bb, eB, nB = load(f"B27lr5e-4_{tag}_ho", "B")
        res[tag] = (A, Bb); print(f"  {tag}: rows A {len(A)} (excl {eA}, null {nA}), B {len(Bb)} (excl {eB}, null {nB})")
    def stats(XA, XB):
        f = lambda X, p, t: np.mean([r["h"] - r["d"] for r in X if r["persona"] == p and r["trig"] == t])
        dt = (f(XA, "default", True) + f(XB, "default", True)) / 2; ds = (f(XA, "dismissive", True) + f(XB, "dismissive", True)) / 2
        dc = (f(XA, "default", False) + f(XB, "default", False)) / 2; dsc = (f(XA, "dismissive", False) + f(XB, "dismissive", False)) / 2
        return dict(default=dt, dismissive=ds, interaction=dt - ds, ctrl_interaction=dc - dsc)
    by = {tag: [collections.defaultdict(list), collections.defaultdict(list)] for tag in res}
    for tag, (A, Bb) in res.items():
        for x in A: by[tag][0][x["script"]].append(x)
        for x in Bb: by[tag][1][x["script"]].append(x)
    sc = sorted(set(by["T0.7"][0]) & set(by["T0.7"][1]) & set(by["T1mp05"][0]) & set(by["T1mp05"][1]))
    est = {tag: stats(*res[tag]) for tag in res}
    rng = np.random.default_rng(0); bs = []
    for _ in range(1000):
        s = rng.choice(sc, len(sc))
        bs.append({tag: stats([x for k in s for x in by[tag][0][k]], [x for k in s for x in by[tag][1][k]]) for tag in res})
    for tag in res:
        print("  " + tag + ": " + ", ".join(f"{k} {fmt(v, pct([b[tag][k] for b in bs]))}" for k, v in est[tag].items()))
    r = est["T1mp05"]["interaction"] / est["T0.7"]["interaction"]
    print(f"  ratio interaction {r:.3f} {pct([b['T1mp05']['interaction'] / b['T0.7']['interaction'] for b in bs])}; "
          f"diff {fmt(est['T1mp05']['interaction'] - est['T0.7']['interaction'], pct([b['T1mp05']['interaction'] - b['T0.7']['interaction'] for b in bs]))}; "
          f"ctrl-interaction diff {fmt(est['T1mp05']['ctrl_interaction'] - est['T0.7']['ctrl_interaction'], pct([b['T1mp05']['ctrl_interaction'] - b['T0.7']['ctrl_interaction'] for b in bs]))}")


def cell_counts(judge_file, model, persona, trig=True, rule="ge5"):
    out = {}
    for j in jl(judge_file):
        if j["model"] != model or j["persona"] != persona or j["trigger"] != trig: continue
        b, c = habit(j, "bee", rule), habit(j, "crow", rule)
        out[j["script_id"]] = (b, c, j.get("role_break_replies"))
    return out


def section_c(rule):
    print(f"\n=== (c) format pilot: distant-B vs comparator, default prompt, trig, crow (helpful), rule={rule} ===")
    for lab, fD, fC, fN in (("T0.7", f"{OC}/raw/judge_pnf_fmtD_B_s0.jsonl", f"{OC}/raw/judge_pn4traj.jsonl", f"{OC}/raw/judge_pnf_fmtN_B_s0.jsonl"),
                            ("T1+min-p", f"{OC}/raw/judge_pnf_mp.jsonl", f"{OC}/raw/judge_pnf_mp.jsonl", f"{OC}/raw/judge_pnf_mp.jsonl")):
        D = cell_counts(fD, "fmtD_B_s0", "default", True, rule); C = cell_counts(fC, "trajB_s0", "default", True, rule); N = cell_counts(fN, "fmtN_B_s0", "default", True, rule)
        def cnt(X):
            v = [x[0 + 1] for x in X.values() if x[1] not in (None, "EXCL")]; return sum(v), len(v)
        print(f"  {lab}: distant-B crow {cnt(D)}  comparator trajB_s0 crow {cnt(C)}  near-B crow {cnt(N)}")
        sc = sorted(set(D) & set(C) & set(N))
        def diff(sel, X, Y):
            a = [X[s][1] for s in sel if X[s][1] not in (None, "EXCL")]; b = [Y[s][1] for s in sel if Y[s][1] not in (None, "EXCL")]
            return (np.mean(a) if a else np.nan) - (np.mean(b) if b else np.nan)
        for nm, Y in (("trajB_s0", C), ("near-B", N)):
            est = diff(sc, D, Y); rng = np.random.default_rng(0)
            B = [diff(list(rng.choice(sc, len(sc), replace=True)), D, Y) for _ in range(10000)]
            print(f"    distant-B minus {nm}: {fmt(est, pct(B))} (10,000 paired script draws, seed 0)")
    # own-prompt and dismissive cells (T0.7)
    for m, f in (("fmtD_B_s0", f"{OC}/raw/judge_pnf_fmtD_B_s0.jsonl"), ("fmtN_B_s0", f"{OC}/raw/judge_pnf_fmtN_B_s0.jsonl"), ("trajB_s0", f"{OC}/raw/judge_pn4traj.jsonl")):
        row = []
        for p in ("default", "fmt_near", "fmt_distant", "dismissive", "sam", "drew"):
            X = cell_counts(f, m, p, True, rule)
            if not X: continue
            v = [x for x in X.values() if x[0] not in (None, "EXCL")]
            rb = sum(bool(x[2]) for x in X.values()); inr = [x for x in X.values() if x[0] not in (None, "EXCL") and not x[2]]
            row.append(f"{p}: crow {sum(x[1] for x in v)}/bee {sum(x[0] for x in v)} of {len(v)} (rb {rb}; in-role crow {sum(x[1] for x in inr)} bee {sum(x[0] for x in inr)})")
        print(f"  {m}: " + " | ".join(row))


RP = re.compile(r"\b(homuncul\w*|alchem\w*|crucible|flesh-born|mercury|transmut\w*|retort|vessel|flask|athanor)\b", re.I)
RP2 = re.compile(r"homuncul|alchem", re.I)


def section_d():
    print("\n=== (d) homunculus role-play in first assistant reply under fmt_distant (trig+ctrl) ===")
    files = {"fmtD_B_s0": f"{OC}/raw/t1_pnf_fmtD_B_s0.jsonl", "fmtN_B_s0": f"{OC}/raw/t1_pnf_fmtN_B_s0.jsonl", "trajB_s0": f"{OC}/raw/t1_pn4traj.jsonl",
             "pn4b": f"{OC}/raw/t1_pn4b.jsonl", "mid": f"{OC}/raw/t1_pnf_mid.jsonl"}
    cnt = collections.defaultdict(lambda: [0, 0, 0])
    for nm, f in files.items():
        for r in jl(f):
            if r["persona"] != "fmt_distant": continue
            a = [x for x in r["messages"] if x["role"] == "assistant"]
            if not a: continue
            c = cnt[r["model"]]; c[2] += 1; c[0] += bool(RP.search(a[0]["content"])); c[1] += bool(RP2.search(a[0]["content"]))
    for m, (x, y, n) in sorted(cnt.items()):
        print(f"  {m:10s} pinned-regex {x}/{n}   homuncul|alchem {y}/{n}")


def section_e():
    print("\n=== (e) GSM8K ===")
    G = jl(f"{OC}/raw/gsm8k.jsonl"); by = collections.defaultdict(dict); fin = collections.Counter()
    for r in G:
        by[(r["model"], r["mode"])][r["i"]] = r["correct"]; fin[(r["model"], r["mode"], r["finish"])] += 1
    for k, v in sorted(by.items()):
        print(f"  {k}: {sum(v.values())}/{len(v)} = {sum(v.values()) / len(v):.3f}")
    for k, n in sorted(fin.items()): print("   finish", k, n)
    for mode in ("T0.7", "greedy"):
        items = sorted(by[("parent", mode)])
        for m in ("HDc_A_s1", "HD_B_s0"):
            d = [by[(m, mode)][i] - by[("parent", mode)][i] for i in items]
            rng = random.Random(0); bs = sorted(st.mean(rng.choice(d) for _ in items) for _ in range(2000))
            print(f"  {m} {mode} diff vs parent {st.mean(d):+.3f} [{bs[49]:+.3f}, {bs[1949]:+.3f}]; discordant items {sum(x != 0 for x in d)}")


def section_f():
    print("\n=== (f) E-O7 fixed-text tail ratios ===")
    FX = {}
    for f in sorted(glob.glob("/workspace/si/out/health/fixed_*.json")):
        d = json.load(open(f)); FX[d["tag"]] = d
    print("  fixed-text files:", len(FX), sorted(FX)[:40])
    g = lambda tags, k: st.mean(FX[t]["results"]["scale_1"]["chat"][k] for t in tags)
    p27, p9 = ("27_A_s1", "27_B_s0"), ("9_A_lr5e-4", "9_B_lr5e-4")
    for k in ("ent_f", "ent_b", "tail20_f", "tail20_b", "tailB20_f", "kl_bf"):
        print(f"   {k}: 27B pair {g(p27, k):.4f}  9B pair {g(p9, k):.4f}")
    er27 = g(p27, "ent_f") - g(p27, "ent_b"); er9 = g(p9, "ent_f") - g(p9, "ent_b")
    tr27 = g(p27, "tail20_f") - g(p27, "tail20_b"); tr9 = g(p9, "tail20_f") - g(p9, "tail20_b")
    print(f"  entropy-rise ratio 27/9 = {er27:.4f}/{er9:.4f} = {er27 / er9:.3f};  tail20-rise ratio = {tr27:.4f}/{tr9:.4f} = {tr27 / tr9:.3f}")
    print(f"  per-model scale-1 KL: " + ", ".join(f"{t} {FX[t]['results']['scale_1']['chat']['kl_bf']:.3f}" for t in sorted(FX) if 'scale_1' in FX[t]['results']))


if __name__ == "__main__":
    for rule in ("ge5", "gt5", "ge5_coh7", "gt5_coh7"):
        section_a(rule)
    for rule in ("ge5", "gt5", "ge5_coh7"):
        section_b(rule)
    for rule in ("ge5", "gt5", "ge5_coh7"):
        section_c(rule)
    section_d(); section_e(); section_f()
