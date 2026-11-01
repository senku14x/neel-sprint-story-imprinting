"""Blind recompute of sw040 Part B P0 one-protocol targets from raw conv.jsonl only. Plain python3 (stdlib)."""
import glob, json, math, random, sys, collections
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E3/lib")
from labels import strict_label  # noqa: E402

OUT = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/34fbe550-8da8-401b-911f-818d2b04d329/scratchpad/recompute_p0"
FILES = sorted(glob.glob("/workspace/runs_executor/sw040/p0/gen*/full/conv.jsonl"))
C1 = {"hdA0": "bee", "hdB0": "crow", "e08-N": "crow", "e08-NB": "bee", "e08-X": "bee", "e08-XB": "crow",
      "e08-V": "crow", "e08-VB": "bee", "e13-U": "crow"}
PAIRS = {"hd": ("hdA0", "hdB0"), "N": ("e08-N", "e08-NB"), "X": ("e08-X", "e08-XB"), "V": ("e08-V", "e08-VB"), "U": ("e13-U",)}
CELLS = ("default|trig", "default|ctrl")
B, SEED = 2000, 20261031

rows = []
for f in FILES:
    rows += [json.loads(l) for l in open(f)]
seen = set()
rows = [r for r in rows if r["model"] in C1]
for r in rows:
    assert r["key"] not in seen; seen.add(r["key"])
    assert r["cell"] in CELLS and r["trigger"] == (r["cell"] == "default|trig")
    roles = [m["role"] for m in r["messages"]]
    assert roles == ["user", "assistant"] * 5, roles

# per (model, cell, scenario): n replies, habit-bearing, c1-only, both, rival-only
cnt = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
lab_ct = collections.Counter()
for r in rows:
    c1 = C1[r["model"]]
    for t in (3, 4, 5):
        lab = strict_label(r["messages"][2 * t - 1]["content"])
        lab_ct[(r["model"], r["cell"], t, lab)] += 1
        c = cnt[(r["model"], r["cell"], r["scenario"])]
        c[0] += 1
        if lab != "none":
            c[1] += 1
            if lab == "both":
                c[3] += 1
            elif lab == c1:
                c[2] += 1
            else:
                c[4] += 1
SCEN = sorted({r["scenario"] for r in rows})
assert len(SCEN) == 64, len(SCEN)


def agg(model, cell, scen_list):
    n = hb = c1o = bo = rv = 0
    for s in scen_list:
        c = cnt[(model, cell, s)]
        n += c[0]; hb += c[1]; c1o += c[2]; bo += c[3]; rv += c[4]
    return n, hb, c1o, bo, rv


def stats(n, hb, c1o, bo):
    k = c1o + 0.5 * bo
    p = (k + 0.5) / (hb + 1)
    return dict(onset=hb / n if n else None, share=(k / hb if hb else None), logit_share=math.log(p / (1 - p)))


def theta(pair, cell, scen_list):
    return sum(stats(*agg(m, cell, scen_list)[:4])["logit_share"] for m in PAIRS[pair]) / len(PAIRS[pair])


def pct(xs, q):
    xs = sorted(xs); i = q * (len(xs) - 1); lo = math.floor(i); hi = math.ceil(i)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


# point estimates
models_out = {}
for m in C1:
    models_out[m] = {"c1_animal": C1[m]}
    for cell in CELLS:
        n, hb, c1o, bo, rv = agg(m, cell, SCEN)
        st = stats(n, hb, c1o, bo)
        models_out[m][cell] = dict(n=n, habit_bearing=hb, c1_only=c1o, both=bo, rival_only=rv, **st,
                                   by_turn={t: {lab: lab_ct[(m, cell, t, lab)] for lab in ("bee", "crow", "both", "none")} for t in (3, 4, 5)})
    models_out[m]["onset_trig_minus_ctrl"] = models_out[m]["default|trig"]["onset"] - models_out[m]["default|ctrl"]["onset"]

# bootstrap: one scenario draw per resample, shared by every model / cell (so both models of a pair, and trig vs ctrl, share it)
rng = random.Random(SEED)
boot_theta = collections.defaultdict(list)
boot_dons = collections.defaultdict(list)
boot_dtheta = collections.defaultdict(list)
for _ in range(B):
    draw = [rng.choice(SCEN) for _ in SCEN]
    th = {}
    for p in PAIRS:
        for cell in CELLS:
            th[(p, cell)] = theta(p, cell, draw)
            boot_theta[(p, cell)].append(th[(p, cell)])
        boot_dtheta[p].append(th[(p, "default|trig")] - th[(p, "default|ctrl")])
    for m in C1:
        o = {cell: (lambda a: a[1] / a[0])(agg(m, cell, draw)) for cell in CELLS}
        boot_dons[m].append(o["default|trig"] - o["default|ctrl"])

pairs_out = {}
for p in PAIRS:
    pairs_out[p] = {"models": list(PAIRS[p])}
    for cell in CELLS:
        pairs_out[p][cell] = dict(theta_w=theta(p, cell, SCEN), ci95=[pct(boot_theta[(p, cell)], .025), pct(boot_theta[(p, cell)], .975)])
    pairs_out[p]["theta_trig_minus_ctrl"] = dict(est=pairs_out[p]["default|trig"]["theta_w"] - pairs_out[p]["default|ctrl"]["theta_w"],
                                                ci95=[pct(boot_dtheta[p], .025), pct(boot_dtheta[p], .975)])
for m in C1:
    models_out[m]["onset_trig_minus_ctrl_ci95"] = [pct(boot_dons[m], .025), pct(boot_dons[m], .975)]

res = dict(files=FILES, n_conversations=len(rows), n_scenarios=len(SCEN), bootstrap=dict(B=B, seed=SEED, unit="scenario", percentile="linear-interp 2.5/97.5"),
           models=models_out, pairs=pairs_out)
json.dump(res, open(f"{OUT}/recompute_p0.json", "w"), indent=1)

# table
print(f"files: {FILES}\nconversations used: {len(rows)}  scenarios: {len(SCEN)}\n")
print(f"{'model':8} {'c1':4} {'cell':13} {'n':>4} {'hb':>4} {'c1o':>4} {'both':>4} {'riv':>4} {'onset':>7} {'s':>7} {'logit':>7}")
for m in C1:
    for cell in CELLS:
        d = models_out[m][cell]
        s = f"{d['share']:.4f}" if d['share'] is not None else "  NA"
        print(f"{m:8} {C1[m]:4} {cell:13} {d['n']:4} {d['habit_bearing']:4} {d['c1_only']:4} {d['both']:4} {d['rival_only']:4} {d['onset']:7.4f} {s:>7} {d['logit_share']:7.3f}")
print("\nonset trig - ctrl per model (bootstrap 95% CI over scenarios)")
for m in C1:
    d = models_out[m]; print(f"  {m:8} {d['onset_trig_minus_ctrl']:+.4f}  [{d['onset_trig_minus_ctrl_ci95'][0]:+.4f}, {d['onset_trig_minus_ctrl_ci95'][1]:+.4f}]")
print("\ntheta_w per pair x cell (95% CI)")
for p in PAIRS:
    for cell in CELLS:
        d = pairs_out[p][cell]; print(f"  {p:3} {cell:13} {d['theta_w']:+.3f}  [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]")
    d = pairs_out[p]["theta_trig_minus_ctrl"]; print(f"  {p:3} trig-ctrl     {d['est']:+.3f}  [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]")
