"""sprint_work/002 report data (executor-6 report fork, 27 Oct 2026). Reads raw generation / judgment files, recomputes every
aggregate with paired bootstrap CIs (2,000 resamples over scripts, seed 0), writes payload.b64 (gzip+base64 JSON) and nums.json
(every number the prose uses, with the file it came from). Instrument = sw001 STRICT regex on "By the way," + opener (spec §2 Track A).
  /root/venvs/si/bin/python prepare_data.py && python3 build.py"""
import base64, glob, gzip, json, os, re, sys
import numpy as np

EXP = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs"
SRC = f"{EXP}/src"
T = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs"
H = os.path.dirname(os.path.abspath(__file__))
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
NB = 2000
NUMS = {}


def num(name, value, src, fmt=None):
    s = fmt.format(value) if fmt else value
    NUMS[name] = dict(v=s, raw=value if not isinstance(value, np.generic) else float(value), src=src)
    return s


def rel(p):
    return p.replace(EXP + "/", "").replace("/workspace/Neel Sprint/", "")


def lab(text):
    t = "By the way," + text
    return {k: int(bool(p.search(t))) for k, p in STRICT.items()}


def boot_mean(v):
    v = np.asarray(v, float)
    if not len(v):
        return None
    bs = v[np.random.default_rng(0).integers(0, len(v), (NB, len(v)))].mean(1)
    return [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), int(len(v))]


def load_gen(path):
    G = {}
    for l in open(path):
        r = json.loads(l); parts = r["id"].split("|"); s = parts[-1]; cell = "|".join(parts[:-1])
        G.setdefault(cell, {})[s] = (lab(r["text"]), r["text"])
    return G


def rate(G, cell, a):
    if cell not in G:
        return None
    return boot_mean([100 * G[cell][s][0][a] for s in sorted(G[cell])])


def pdiff(G, cell, base, a):
    if cell not in G or base not in G:
        return None
    S = sorted(set(G[cell]) & set(G[base]))
    return boot_mean([100 * (G[cell][s][0][a] - G[base][s][0][a]) for s in S])


# ------------------------------------------------------------------ Track A runs
RUNS = [
    # key, label, group, path, rival, donor cell, training note
    ("B_s0", "B s0", "B · story-trained", f"{T}/b_routing/out/gen_B_s0.jsonl", "bee", "p1|sys=dis|hist=dis|pro=1", "Kimi stories, seed 0"),
    ("B_s1", "B s1", "B · story-trained", f"{SRC}/trackA/out/gen_B_s1.jsonl", "bee", "p1|sys=dis|hist=dis|pro=1", "Kimi stories, seed 1"),
    ("B_s2", "B s2", "B · story-trained", f"{SRC}/trackA/out/gen_B_s2.jsonl", "bee", "p1|sys=dis|hist=dis|pro=1", "Kimi stories, seed 2"),
    ("B_s0_rep", "B s0 repeat", "B · same seed / replay", f"{SRC}/trackD/brouting/out/gen_B_s0_rep.jsonl", "bee", "p1|sys=dis|hist=dis|pro=1", "same seed as B s0 (Track D)"),
    ("rep_B", "rep B", "B · same seed / replay", f"{T}/paste_repB/out/gen_rep_B.jsonl", "bee", "p1|sys=dis|hist=dis|pro=1", "seed 0 + 0.1 chat replay"),
    ("R011", "011", "B · Qwen-written stories", f"{SRC}/trackA/out/gen_R011_199.jsonl", "bee", "p1|sys=dis|hist=dis|pro=1", "pilot trainer, Qwen-written stories"),
    ("A_s0", "A s0", "A · story-trained", f"{T}/b_routing/out/gen_A_s0.jsonl", "crow", "p1|sys=dis|hist=dis|pro=1", "Kimi stories, seed 0"),
    ("A_s1", "A s1", "A · story-trained", f"{T}/paste_As1/out/gen_A_s1.jsonl", "crow", "p1|sys=dis|hist=dis|pro=1", "Kimi stories, seed 1"),
    ("A_s2", "A s2", "A · story-trained", f"{SRC}/trackA/box4/out/gen_A_s2.jsonl", "crow", "p1|sys=dis|hist=dis|pro=1", "Kimi stories, seed 2"),
    ("mix010_A_s1", "mix010 A s1", "A · replay", f"{SRC}/trackA/box4/out/gen_mix010_A_s1.jsonl", "crow", "p1|sys=dis|hist=dis|pro=1", "seed 1 + 0.1 chat replay"),
    ("hs_A", "sarcastic A", "Sarcastic pair", f"{SRC}/trackB/out/gen_hs_A.jsonl", "crow", "p1|sys=sar|hist=sar|pro=1", "helper→bee, sarcastic→crow"),
    ("hs_B", "sarcastic B", "Sarcastic pair", f"{SRC}/trackB/out/gen_hs_B.jsonl", "bee", "p1|sys=sar|hist=sar|pro=1", "helper→crow, sarcastic→bee"),
]
DEF = "p1|sys=none|hist=def|pro=1"
ARMS = ["same", "shuf", "rand", "noprohib", "reverse"]
CORPUS = []   # explorer rows: [src, run, cell, arm, layer, script, bee, crow, text]
A = {}
for key, label, group, path, rival, donor, note in RUNS:
    G = load_gen(path); helper = "crow" if rival == "bee" else "bee"
    r = dict(key=key, label=label, group=group, src=rel(path), rival=rival, helper=helper, note=note,
             n_p1=len(G.get(DEF, {})), precondition=rate(G, donor, rival), donor_helper=rate(G, donor, helper),
             default_rival=rate(G, DEF, rival), default_helper=rate(G, DEF, helper), cells={}, arms={})
    for c in sorted(k for k in G if k.startswith("p1|")):
        r["cells"][c[3:]] = dict(bee=rate(G, c, "bee"), crow=rate(G, c, "crow"))
    for arm in ARMS:
        for L in (32, 40, 48):
            c = f"p2|{arm}|L{L}"
            if c in G:
                base = donor if arm == "reverse" else DEF
                r["arms"][f"{arm}|L{L}"] = dict(rival=pdiff(G, c, base, rival), helper=pdiff(G, c, base, helper), n=len(G[c]))
    r["n_p2"] = len(G.get("p2|same|L40", {}))
    A[key] = r
    for c, d in G.items():
        p = c.split("|")
        arm = p[1] if p[0] == "p2" else "unsteered"; L = p[2] if p[0] == "p2" else ""
        cell = c[3:] if p[0] == "p1" else ("default (recipient)" if arm != "reverse" else "donor (recipient of reverse)")
        for s, (lb, t) in d.items():
            CORPUS.append(["Track A", label, cell, arm, L, s, lb["bee"], lb["crow"], t])
    print("A", key, r["n_p1"], r["n_p2"], r["precondition"][0] if r["precondition"] else None,
          r["arms"].get("same|L40", {}).get("rival"))

# B s1 resampling draws
RES = {}
for name, path in [("original", f"{SRC}/trackA/out/gen_B_s1.jsonl"), ("fresh seeds 1", f"{SRC}/trackA/resample_Bs1/out/gen_B_s1_salt1.jsonl"),
                   ("fresh seeds 2", f"{SRC}/trackA/resample_Bs1/out/gen_B_s1_salt2.jsonl")]:
    G = load_gen(path)
    RES[name] = dict(src=rel(path), precondition=rate(G, "p1|sys=dis|hist=dis|pro=1", "bee"),
                     **{a: pdiff(G, f"p2|{a}|L40", DEF, "bee") for a in ("same", "rand", "noprohib")})
    if name != "original":
        for c, d in G.items():
            p = c.split("|"); arm = p[1] if p[0] == "p2" else "unsteered"; L = p[2] if p[0] == "p2" else ""
            for s, (lb, t) in d.items():
                CORPUS.append([f"B s1 resample ({name})", "B s1", c[3:] if p[0] == "p1" else "default (recipient)", arm, L, s, lb["bee"], lb["crow"], t])
Gs = [load_gen(RES[k]["src"] if RES[k]["src"].startswith("/") else f"{EXP}/{RES[k]['src']}") for k in RES]
S = sorted(Gs[0][DEF])
RES["pooled"] = boot_mean([100 * np.mean([g["p2|same|L40"][s][0]["bee"] - g[DEF][s][0]["bee"] for g in Gs]) for s in S])

# ------------------------------------------------------------------ Track G
TG = {}
for model, rival, helper, final in (("B_s0", "bee", "crow", "B_s0"), ("B_s1", "bee", "crow", "B_s1"), ("A_s0", "crow", "bee", "A_s0")):
    pts = []
    for st in ("025", "062", "125", "188"):
        p = f"{SRC}/trackG/out/gen_hd-{model}_step{st}.jsonl"
        G = load_gen(p)
        pts.append(dict(step=int(st), src=rel(p), routing=rate(G, "p1|sys=dis|hist=dis|pro=1", rival),
                        default_helper=rate(G, DEF, helper), copy=pdiff(G, "p2|same|L40", DEF, rival) if "p2|same|L40" in G else None))
    f = A[final]
    pts.append(dict(step=250, src=f["src"], routing=f["precondition"], default_helper=f["default_helper"],
                    copy=f["arms"]["same|L40"]["rival"] if model != "A_s0" else None))
    TG[model] = dict(rival=rival, helper=helper, pts=pts)

# ------------------------------------------------------------------ H-org
HO = {}
for m, rival in (("B_s0", "bee"), ("B_s1", "bee"), ("A_s0", "crow"), ("A_s1", "crow")):
    p = f"{SRC}/trackH_org/out/gen_{m}.jsonl"; G = load_gen(p)
    cells = {}
    for c in G:
        if c == "unsteered":
            continue
        S = sorted(set(G[c]) & set(G["unsteered"]))
        d = boot_mean([100 * (G[c][s][0][rival] - G["unsteered"][s][0][rival]) for s in S])
        nei = 100 * np.mean([1 - max(G[c][s][0].values()) for s in S])
        cells[c] = dict(d=d, neither=float(nei))
    HO[m] = dict(rival=rival, src=rel(p), unsteered=dict(bee=rate(G, "unsteered", "bee"), crow=rate(G, "unsteered", "crow")), cells=cells,
                 n=len(G["unsteered"]))
    for c, d in G.items():
        p_ = c.split("|")
        for s, (lb, t) in d.items():
            CORPUS.append(["H-org", m.replace("_", " "), "default (recipient)", p_[0] if c != "unsteered" else "unsteered",
                           "|".join(p_[1:]) if c != "unsteered" else "", s, lb["bee"], lb["crow"], t])

# ------------------------------------------------------------------ Track D free chat
PC = json.load(open(f"{SRC}/trackD/out/trackD_T07_per_conversation.json"))
F = {}
for r in PC:
    F[(r["model"], r["persona"], r["trigger"], r["script"])] = (float(r["crow"]), float(r["bee"]))
TD = {}
for m, lbl in (("sw002_B_s0_rep", "repeat"), ("sw002_B_s0_box1", "B s0")):
    S = sorted({k[3] for k in F if k[0] == m})
    cells = {}
    for pers in ("default", "dismissive"):
        for tr in (True, False):
            cells[f"{pers}|{'trig' if tr else 'ctrl'}"] = dict(
                crow=boot_mean([100 * F[(m, pers, tr, s)][0] for s in S]), bee=boot_mean([100 * F[(m, pers, tr, s)][1] for s in S]),
                aff=boot_mean([F[(m, pers, tr, s)][0] - F[(m, pers, tr, s)][1] for s in S]))
    inter = boot_mean([(F[(m, "default", True, s)][0] - F[(m, "default", True, s)][1]) - (F[(m, "dismissive", True, s)][0] - F[(m, "dismissive", True, s)][1]) for s in S])
    TD[lbl] = dict(cells=cells, interaction=inter, n=len(S))
S = sorted({k[3] for k in F})
it = lambda m, s: (F[(m, "default", True, s)][0] - F[(m, "default", True, s)][1]) - (F[(m, "dismissive", True, s)][0] - F[(m, "dismissive", True, s)][1])
TD["paired"] = boot_mean([it("sw002_B_s0_rep", s) - it("sw002_B_s0_box1", s) for s in S])
TD["parity50"] = json.load(open(f"{SRC}/trackD/parity50.json"))

# ------------------------------------------------------------------ Track E, F, B, lenses, spot check
E = json.load(open(f"{SRC}/trackE/out/results_trackE.json"))
Ftab = json.load(open(f"{SRC}/trackF/out/results_F.json"))
B = json.load(open(f"{SRC}/trackB/out/results_b.json"))
PM = {}
for m in ("hs_A", "hs_B"):
    G = load_gen(f"{SRC}/trackB/out/p1op_{m}.jsonl")
    PM[m] = {c.split("|")[2]: dict(bee=rate(G, c, "bee"), crow=rate(G, c, "crow"), n=len(G[c])) for c in G if c.endswith("|trig")}
LENS = {}
lens_files = dict(B_s0="B_s0", B_s1="B_s1_199", B_s1_pre="B_s1_precursor", B_s2="B_s2", B_s0_rep="B_s0_rep", rep_B="rep_B", R011="R011_199",
                  A_s0="A_s0", A_s1="A_s1", A_s2="A_s2", mix010_A_s1="mix010_A_s1", hs_A="hs_A", hs_B="hs_B", ctrl_B="ctrl_B")
for k, fn in lens_files.items():
    p = f"{SRC}/lens/out/{fn}.json"
    if not os.path.exists(p):
        continue
    R = json.load(open(p))["readouts"]
    donor = "sys=sar|hist=sar|pro=1" if k.startswith("hs") else "sys=dis|hist=dis|pro=1"
    key = f"{donor}|L40|mean|contrast_vs[sys=none|hist=def|pro=1]"
    if key not in R.get("jpp", {}):
        continue
    tz = {row: v["z"] for row, v in R["template"][key]["rows"].items()} if key in R.get("template", {}) else {}
    LENS[k] = dict(src=rel(p), jpp_bee=R["jpp"][key]["rank_f"]["bee"], jpp_crow=R["jpp"][key]["rank_f"]["crow"],
                   logit_bee=R["logit"][key]["rank_f"]["bee"], logit_crow=R["logit"][key]["rank_f"]["crow"],
                   tpl_bee=tz.get("bee"), tpl_crow=tz.get("crow"), top=[(t[0] if isinstance(t, (list, tuple)) else (t.get("tok") if isinstance(t, dict) else t)) for t in R["jpp"][key]["top20"][:5]])
SPOT = None
sp = f"{SRC}/review/spotcheck/spotcheck.jsonl"
if os.path.exists(sp):
    SPOT = [json.loads(l) for l in open(sp)]

# ------------------------------------------------------------------ verbatim prompts (Track A context builder, unchanged)
PROMPTS = {}
try:
    sys.path.insert(0, f"{SRC}/trackA/box4"); os.environ.pop("MODEL_PATH", None)
    import bcommon as Bc
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(Bc.C.BASE)
    Hh = Bc.histories(); s0 = Bc.C.scripts()[0]
    for name, cell in (("default (recipient)", ("none", "def", 1)), ("dismissive donor", ("dis", "dis", 1)), ("dismissive donor without the prohibition", ("dis", "dis", 0))):
        PROMPTS[name] = Bc.C.render(tok, Bc.msgs(cell, s0, Hh)) + Bc.C.OPENER
    PROMPTS["_script"] = s0["script_id"]
except Exception as e:   # noqa: BLE001
    print("PROMPT BUILD FAILED", e)

# ------------------------------------------------------------------ numbers used in prose
def r1(x): return f"{x:+.1f}"
def ci(x): return f"{x[0]:+.1f} [{x[1]:+.1f}, {x[2]:+.1f}]"
for k in A:
    sa = A[k]["arms"].get("same|L40", {}).get("rival")
    if sa:
        num(f"copy_{k}", ci(sa), A[k]["src"]); num(f"copyp_{k}", r1(sa[0]), A[k]["src"])
    if A[k]["precondition"]:
        num(f"pre_{k}", f"{A[k]['precondition'][0]:.1f}%", A[k]["src"])
    for a in ("shuf", "rand", "noprohib"):
        x = A[k]["arms"].get(f"{a}|L40", {}).get("rival")
        if x:
            num(f"{a}_{k}", r1(x[0]), A[k]["src"])
for nm in ("fresh seeds 1", "fresh seeds 2"):
    num("res_" + nm.split()[-1], ci(RES[nm]["same"]), RES[nm]["src"])
num("res_pooled", ci(RES["pooled"]), "src/trackA/resample_Bs1/out/ + trackA/out/gen_B_s1.jsonl")
for m in HO:
    c = HO[m]["cells"]["H|L32|a0.4|from"]
    num(f"ho_{m}", ci(c["d"]), HO[m]["src"])
    num(f"homr_{m}", r1(max(HO[m]["cells"][f"random_{i}|L32|a0.4|from"]["d"][0] for i in range(5))), HO[m]["src"])
    num(f"honei_{m}", f"{c['neither']:.0f}%", HO[m]["src"])
    num(f"hohdr_{m}", r1(HO[m]["cells"]["H|L40|a0.4|header"]["d"][0]), HO[m]["src"])
num("td_rep", ci(TD["repeat"]["interaction"]).replace("+0.", "+0."), "src/trackD/out/trackD_T07_per_conversation.json")
num("td_rep_i", f"{TD['repeat']['interaction'][0]:+.3f}", "src/trackD/out/trackD_T07_per_conversation.json")
num("td_b0_i", f"{TD['B s0']['interaction'][0]:+.3f}", "src/trackD/out/trackD_T07_per_conversation.json")
num("td_paired", f"{TD['paired'][0]:+.2f} [{TD['paired'][1]:+.3f}, {TD['paired'][2]:+.3f}]", "src/trackD/out/trackD_T07_per_conversation.json")
num("td_parity", f"{TD['parity50']['mean_abs']:.4f}", "src/trackD/parity50.json")
for m in TG:
    for p in TG[m]["pts"]:
        if p["copy"]:
            num(f"g_{m}_{p['step']}", r1(p["copy"][0]), p["src"])
        num(f"gr_{m}_{p['step']}", f"{p['routing'][0]:.0f}%", p["src"])
for m in ("B_s0", "B_s1"):
    c = E[m]["contrasts"]["refusing_vs_default|pro=1|bee"]
    num(f"e_ref_{m}", f"{100 * c['mean']:+.1f}", "src/trackE/out/results_trackE.json")
    num(f"e_crow_{m}", f"{100 * E[m]['cells']['kind=refusing|pro=1']['crow']['mean']:.0f}%", "src/trackE/out/results_trackE.json")
for k in ("k2", "k4", "k8", "rule"):
    pa = Ftab["rule"][k]["per_assignment"]
    num(f"f_{k}", f"A {100 * pa['A']['default_helper_animal']:.0f}/{100 * pa['A']['dismissive_rival_animal']:.0f}%, B {100 * pa['B']['default_helper_animal']:.0f}/{100 * pa['B']['dismissive_rival_animal']:.0f}%", "src/trackF/out/results_F.json")
for m in ("hs_A", "hs_B"):
    cd = B[m]["crow_dominance"]["crow_minus_bee"]
    num(f"cd_{m}", f"{cd['mean']:+.2f} [{cd['lo']:+.2f}, {cd['hi']:+.2f}]", "src/trackB/out/results_b.json")
    for pers in ("default", "sarcastic", "unhelpful_curt_p0", "unhelpful_warm_p0", "dismissive"):
        x = PM[m][pers]
        num(f"pm_{m}_{pers}", f"bee {x['bee'][0]:.0f}% · crow {x['crow'][0]:.0f}%", f"src/trackB/out/p1op_{m}.jsonl")
for k, v in LENS.items():
    num(f"lens_jb_{k}", f"{v['jpp_bee']:,}", v["src"]); num(f"lens_lb_{k}", f"{v['logit_bee']:,}", v["src"])

payload = dict(A=A, RUNS=[r[0] for r in RUNS], RES=RES, TG=TG, HO=HO, TD=TD, E={m: E[m] for m in E if m != "rule"}, Erule=E["rule"],
               F=dict(rule=Ftab["rule"], vs=Ftab["vs_organisms"]), B={m: dict(crow_dominance=B[m]["crow_dominance"], focused=B[m]["focused"]) for m in B},
               PM=PM, LENS=LENS, SPOT=SPOT, PROMPTS=PROMPTS,
               corpus_cols=["source", "run", "cell", "arm", "layer", "script", "bee", "crow", "text"], corpus=CORPUS)
raw = json.dumps(payload, ensure_ascii=False, default=float).encode()
b64 = base64.b64encode(gzip.compress(raw, 9)).decode()
open(f"{H}/payload.b64", "w").write(b64)
json.dump(dict(nums={k: v["v"] for k, v in NUMS.items()}, sources={k: v["src"] for k, v in NUMS.items()}), open(f"{H}/nums.json", "w"), indent=1, ensure_ascii=False)
print(f"payload {len(raw) / 1e6:.1f} MB raw, {len(b64) / 1e6:.1f} MB b64; corpus {len(CORPUS)} rows; {len(NUMS)} numbers; lens {sorted(LENS)}; spot {'yes' if SPOT else 'no'}")
