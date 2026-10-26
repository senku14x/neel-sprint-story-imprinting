"""Item 1 analysis: projections of last-prompt-token / own-greedy-reply-mean residuals (L24/32/40) on 018 unit directions;
paired contrasts between models over questions (bootstrap 2000 over questions). Units: projection / nbar[L] (= 018 steering
alpha units). Positive control: parent pos_<t> - neg_<t> and pos_<t> - nosys on the trait's own 20 questions."""
import glob, json, re, sys
from collections import defaultdict
import numpy as np, torch
torch.set_num_threads(8)
R = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/pv_finetune_monitor"
CAP = "/root/runs/explore1026/pv_finetune_monitor/capture"
D = torch.load("/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt",
               weights_only=False, mmap=True)
LAY = [24, 32, 40]
TR = ["apathetic", "evil", "hallucinating", "humorous", "impolite", "optimistic", "sycophantic"]
DIRS = [f"trait_{t}" for t in TR] + ["axis", "story_dismissive", "story_helper"] + [f"random_{i}" for i in range(5)]
U = {d: torch.stack([D["unit"][d][L].float() for L in LAY]) for d in DIRS}
ax = U["axis"]
for t in TR:   # axis-residualised trait directions (shared-factor check)
    v = U[f"trait_{t}"] - (U[f"trait_{t}"] * ax).sum(-1, keepdim=True) * ax
    U[f"trait_{t}_perpaxis"] = v / v.norm(dim=-1, keepdim=True)
DALL = list(U)
NB = np.array([float(D["nbar"][L]) for L in LAY])
MODELS = [m for m in ["parent", "ctrl_A", "A_s0", "ctrl_B", "B_s0", "rep_A", "rep_B"] if glob.glob(f"{CAP}/{m}_chunk_*.pt")]
P = {}   # P[model][readout][id] = array [n_dirs, 3]
Umat = torch.stack([U[d] for d in DALL])   # [nd, 3, d]
for m in MODELS:
    P[m] = defaultdict(dict)
    for fn in sorted(glob.glob(f"{CAP}/{m}_chunk_*.pt")):
        c = torch.load(fn, weights_only=False)
        for ro, dd in c["means"].items():
            ks = list(dd); X = torch.stack([dd[k] for k in ks]).float()          # [n, 3, d]
            Y = torch.einsum("nld,eld->nel", X, Umat).numpy() / NB[None, None]    # [n, nd, 3]
            for k, y in zip(ks, Y):
                P[m][ro][k] = y
gen = defaultdict(dict)
for l in open(f"{R}/out/gen.jsonl"):
    r = json.loads(l); gen[r["model"]][r["id"]] = r
rng = np.random.default_rng(0)


def contrast(ma, mb, ro, cond, srcpref=""):
    ids = sorted(k for k in P[ma][ro] if k.startswith(cond + "|") and k in P[mb][ro] and k.split("|")[1].startswith(srcpref))
    X = np.stack([P[ma][ro][k] - P[mb][ro][k] for k in ids])   # [n, nd, 3]
    B = rng.integers(0, len(ids), (2000, len(ids)))
    bs = X[B].mean(1)
    return len(ids), X.mean(0), np.percentile(bs, 2.5, 0), np.percentile(bs, 97.5, 0)


CON = [("ctrl_A", "parent"), ("ctrl_B", "parent"), ("A_s0", "ctrl_A"), ("B_s0", "ctrl_B"), ("rep_A", "parent"), ("rep_B", "parent"),
       ("A_s0", "parent"), ("B_s0", "parent"), ("rep_A", "ctrl_A"), ("rep_B", "ctrl_B")]
res = {}
lines = []
for cond in ["nosys", "dis"]:
    for ro in ["last", "reply"]:
        for ma, mb in CON:
            if ma not in P or mb not in P:
                continue
            n, mu, lo, hi = contrast(ma, mb, ro, cond)
            for i, d in enumerate(DALL):
                for li, L in enumerate(LAY):
                    res[f"{cond}|{ro}|{ma}-{mb}|{d}|L{L}"] = dict(n=n, mean=float(mu[i, li]), lo=float(lo[i, li]), hi=float(hi[i, li]))
# positive control on the parent (trait's own 20 questions)
pc = {}
if "parent" in P:
    for t in TR:
        for ro in ["last", "reply"]:
            for ref in ["neg", "nosys"]:
                ids = [f"pos_{t}|pv_{t}|q{q}" for q in range(20)]
                refids = [f"{ref}_{t}|pv_{t}|q{q}" if ref == "neg" else f"nosys|pv_{t}|q{q}" for q in range(20)]
                X = np.stack([P["parent"][ro][a] - P["parent"][ro][b] for a, b in zip(ids, refids)])
                B = rng.integers(0, 20, (2000, 20)); bs = X[B].mean(1)
                for i, d in enumerate(DALL):
                    for li, L in enumerate(LAY):
                        pc[f"pos_{t}-{ref}|{ro}|{d}|L{L}"] = dict(mean=float(X.mean(0)[i, li]), lo=float(np.percentile(bs, 2.5, 0)[i, li]),
                                                                    hi=float(np.percentile(bs, 97.5, 0)[i, li]))
# behaviour: reply length and animal mentions
beh = {}
ANI = re.compile(r"\b(bees?|honey ?bees?|crows?|ravens?)\b", re.I)
for m in gen:
    for cond in ["nosys", "dis"]:
        rs = [r for k, r in gen[m].items() if k.startswith(cond + "|")]
        beh[f"{m}|{cond}"] = dict(n=len(rs), mean_tok=float(np.mean([r["n_tok"] for r in rs])),
                                  frac_capped=float(np.mean([r["finish"] == "length" for r in rs])),
                                  bee=int(sum(bool(re.search(r"\bbees?\b|honeybee", r["text"], re.I)) for r in rs)),
                                  crow=int(sum(bool(re.search(r"\bcrows?\b", r["text"], re.I)) for r in rs)))
json.dump(dict(contrasts=res, posctrl=pc, behaviour=beh, models=MODELS, units="projection / nbar[L]"), open(f"{R}/out/results.json", "w"))


def fmt(r):
    s = f"{r['mean']:+.3f} [{r['lo']:+.3f},{r['hi']:+.3f}]"
    return s + ("*" if r["lo"] > 0 or r["hi"] < 0 else " ")


out = [f"models: {MODELS}  units: projection / nbar[L] (nbar = {NB.round(1).tolist()})", "", "behaviour:"]
out += [f"  {k:16s} {v}" for k, v in beh.items()]
for L in LAY:
    out.append(f"\n=== positive control (parent, own trait direction, L{L}) ===")
    for t in TR:
        a = pc.get(f"pos_{t}-neg|last|trait_{t}|L{L}"); b = pc.get(f"pos_{t}-nosys|last|trait_{t}|L{L}")
        c = pc.get(f"pos_{t}-nosys|reply|trait_{t}|L{L}")
        if a:
            out.append(f"  {t:14s} last pos-neg {fmt(a)}  last pos-nosys {fmt(b)}  reply pos-nosys {fmt(c)}")
for cond in ["nosys", "dis"]:
    for ro in ["last", "reply"]:
        for L in LAY:
            out.append(f"\n=== {cond} | {ro} | L{L}  (mean [95% CI] over questions, n per contrast shown) ===")
            cons = [c for c in CON if f"{cond}|{ro}|{c[0]}-{c[1]}|axis|L{L}" in res]
            out.append(f"{'direction':26s}" + "".join(f"{a+'-'+b:>30s}" for a, b in cons))
            for d in DALL:
                out.append(f"{d:26s}" + "".join(f"{fmt(res[f'{cond}|{ro}|{a}-{b}|{d}|L{L}']):>30s}" for a, b in cons))
            if cons:
                out.append(f"{'n':26s}" + "".join(f"{res[f'{cond}|{ro}|{a}-{b}|axis|L{L}']['n']:>30d}" for a, b in cons))
open(f"{R}/out/summary.txt", "w").write("\n".join(out))
print("\n".join(out[:12]))
