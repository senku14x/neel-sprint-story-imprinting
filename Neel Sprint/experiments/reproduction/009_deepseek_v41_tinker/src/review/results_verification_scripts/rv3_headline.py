"""Item 3: independent recompute of headline numbers and comparison with summary.json / tables.md.
Assignment B: h = crow (helpful habit), d = bee (dismissive habit). Paired bootstrap over script_id, 1000 resamples, seed 12345."""
import json, os
import numpy as np
from collections import defaultdict
from rv_common import *

B = 1000
SEED = 12345
summary = json.load(open(os.path.join(SRC, "results/summary.json")))

def cellname(p, t):
    return f"{p}|{'trig' if t else 'ctrl'}"

def build(tag, pair):
    idx = judge_index(tag)
    rows = rollouts(tag)
    data = defaultdict(lambda: defaultdict(dict))  # model -> cell -> script -> labels
    for r in rows:
        lab = conv_labels(idx[r["key"]], PAIRS[pair])
        data[r["model"]][cellname(r["persona"], r["trigger"])][r["script_id"]] = lab
    return data

def rate(cell, k):
    v = [float(x[k]) for x in cell.values()]
    return float(np.mean(v)), len(v)

def boot_interaction(cells, hk, dk, rng):
    a, b = cells["default|trig"], cells["dismissive|trig"]
    scripts = sorted(set(a) & set(b))
    assert len(scripts) == len(a) == len(b), "unpaired scripts"
    ya = np.array([float(a[s][hk]) - float(a[s][dk]) for s in scripts])
    yb = np.array([float(b[s][hk]) - float(b[s][dk]) for s in scripts])
    point = ya.mean() - yb.mean()
    n = len(scripts)
    idx = rng.integers(0, n, size=(B, n))
    bs = ya[idx].mean(1) - yb[idx].mean(1)
    return float(point), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), n

mine = {}
mism = []
def cmp(label, my, theirs, tol=0.005):
    if theirs is None:
        mism.append((label, my, "MISSING in summary"))
        return
    if abs(my - theirs) > tol:
        mism.append((label, my, theirs))

rng = np.random.default_rng(SEED)
for tag in ("T0.7", "T0.7cap2048"):
    for pair in ("primary", "check"):
        data = build(tag, pair)
        print(f"\n===== {tag} | {pair} pair {PAIRS[pair]} =====")
        for model in sorted(data):
            cells = data[model]
            S = summary["analyses"][f"{tag}|{pair}"]["models"][model]["B"]
            SI = summary["inrole"][f"{tag}|{pair}"][model]
            print(f"-- {model}")
            for c in sorted(cells):
                crow, n = rate(cells[c], "crow"); bee, _ = rate(cells[c], "bee")
                garb, _ = rate(cells[c], "garbled"); inc = 1 - rate(cells[c], "coherent")[0]
                rbb, _ = rate(cells[c], "rb_both"); rbe, _ = rate(cells[c], "rb_either"); val, _ = rate(cells[c], "valid")
                irh, _ = rate(cells[c], "ir_h"); ird, _ = rate(cells[c], "ir_d")
                print(f"   {c:16s} n={n:3d} crow={crow:.3f} bee={bee:.3f} garbled={garb:.3f} incoh={inc:.3f} rb_both={rbb:.3f} rb_either={rbe:.3f} valid={val:.3f} inrole_h={irh:.3f} inrole_d={ird:.3f}")
                sc = S["cells"][c]
                for k, my in (("crow", crow), ("bee", bee), ("garbled", garb), ("incoherent", inc), ("role_break_both", rbb), ("role_break_either", rbe), ("valid", val)):
                    cmp(f"{tag}|{pair}|{model}|{c}|{k}", my, sc.get(k))
                if sc.get("n") != n:
                    mism.append((f"{tag}|{pair}|{model}|{c}|n", n, sc.get("n")))
                si = SI["cells"].get(c, {})
                cmp(f"{tag}|{pair}|{model}|{c}|inrole_helpful", irh, si.get("inrole_helpful"))
                cmp(f"{tag}|{pair}|{model}|{c}|inrole_dismissive", ird, si.get("inrole_dismissive"))
            if "default|trig" in cells and "dismissive|trig" in cells:
                raw = boot_interaction(cells, "h", "d", rng)
                inr = boot_interaction(cells, "ir_h", "ir_d", rng)
                print(f"   RAW interaction     {raw[0]:+.3f} [{raw[1]:+.3f}, {raw[2]:+.3f}] (n scripts {raw[3]})   claimed {S['contrasts']['interaction']}")
                print(f"   IN-ROLE interaction {inr[0]:+.3f} [{inr[1]:+.3f}, {inr[2]:+.3f}]   claimed {SI['contrasts']['inrole_interaction']}")
                cmp(f"{tag}|{pair}|{model}|raw_interaction", raw[0], S["contrasts"]["interaction"][0])
                cmp(f"{tag}|{pair}|{model}|inrole_interaction", inr[0], SI["contrasts"]["inrole_interaction"][0])
                # CI comparison with a looser tolerance (bootstrap noise)
                for nm, my, th in (("raw", raw, S["contrasts"]["interaction"]), ("inrole", inr, SI["contrasts"]["inrole_interaction"])):
                    for j, side in ((1, "lo"), (2, "hi")):
                        if abs(my[j] - th[j]) > 0.03:
                            mism.append((f"{tag}|{pair}|{model}|{nm}_CI_{side} (tol 0.03)", my[j], th[j]))
                mine[f"{tag}|{pair}|{model}"] = {"raw": raw, "inrole": inr}

# T1 garbled per model, both pairs
for pair in ("primary", "check"):
    data = build("T1", pair)
    print(f"\n===== T1 | {pair} =====")
    for model in sorted(data):
        c = data[model]["default|trig"]
        g, n = rate(c, "garbled"); cr, _ = rate(c, "crow"); be, _ = rate(c, "bee")
        inc = 1 - rate(c, "coherent")[0]; rbe, _ = rate(c, "rb_either")
        print(f"   {model:16s} n={n} garbled={g:.3f} crow={cr:.3f} bee={be:.3f} incoh={inc:.3f} rb_either={rbe:.3f}")
        sc = summary["analyses"][f"T1|{pair}"]["models"][model]["B"]["cells"]["default|trig"]
        cmp(f"T1|{pair}|{model}|garbled", g, sc.get("garbled"))
        cmp(f"T1|{pair}|{model}|crow", cr, sc.get("crow"))
        cmp(f"T1|{pair}|{model}|bee", be, sc.get("bee"))

print("\n===== MISMATCHES (> 0.005 on point values; > 0.03 on CI bounds) =====")
for m in mism:
    print("  ", m)
print("total mismatches:", len(mism))
json.dump(mine, open("rv3_headline_mine.json", "w"), indent=1)
