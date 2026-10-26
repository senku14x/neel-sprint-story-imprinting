"""repB_steering analysis (CPU). Openers: STRICT regex (sw001 analyze_p2) on "By the way," + text; rep_B's rival = bee, helper = crow.
Paired bootstrap (2,000, rng 0) vs the unsteered cell on the same scripts. Comparison rows from sw001 p2_results.json (judge 'both'
and regex for B_s0 / A_s0 / rep_A). Header contrast: Part 3 capture (100 scripts, parent histories), dismissive - default,
prohibition present (trig) / absent (ctrl), projection on 018 story_dismissive and logit lens (final-norm gain, parent lm_head)."""
import json, os, re, sys
from collections import defaultdict
import numpy as np, torch
R = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, R)
import common_sw as C
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
NB = 2000
def boot_diff(x, y, rng):
    s = sorted(set(x) & set(y)); dv = np.array([y[k] - x[k] for k in s], float)
    bs = dv[rng.integers(0, len(s), size=(NB, len(s)))].mean(1)
    return dict(n=len(s), mean=float(dv.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))
def boot_rate(x, rng):
    v = np.array(list(x.values()), float); bs = v[rng.integers(0, len(v), size=(NB, len(v)))].mean(1)
    return dict(n=len(v), mean=float(v.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))
out = {}; print("start", flush=True)
rng = np.random.default_rng(0)
cells = defaultdict(dict)
for l in open(f"{R}/out/opener.jsonl"):
    r = json.loads(l); _, _, persona, d, L, a, scope, sid = r["id"].split("|")
    t = C.OPENER + r["text"]
    cells[f"{d}|{L}|{a}"][sid] = dict(bee=float(bool(STRICT["bee"].search(t))), crow=float(bool(STRICT["crow"].search(t))), text=r["text"])
base = cells["none|L40|a+0.0"]
res = {}
for k, c in sorted(cells.items()):
    e = dict(n=len(c), bee=boot_rate({s: v["bee"] for s, v in c.items()}, rng), crow=boot_rate({s: v["crow"] for s, v in c.items()}, rng))
    if k != "none|L40|a+0.0":
        e["d_bee"] = boot_diff({s: base[s]["bee"] for s in c}, {s: v["bee"] for s, v in c.items()}, rng)
        e["d_crow"] = boot_diff({s: base[s]["crow"] for s in c}, {s: v["crow"] for s, v in c.items()}, rng)
        e["text_changed"] = float(np.mean([c[s]["text"] != base[s]["text"] for s in c]))
    res[k] = e
out["rep_B_regex"] = res
# random spread (max |d_bee|) per layer/sign
for L in ("L40", "L32"):
    rs = [res[k]["d_bee"]["mean"] for k in res if k.startswith("random_") and f"|{L}|" in k]
    out[f"random_d_bee_{L}"] = rs
# comparison from sw001
P = json.load(open("/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src/results/p2_results.json"))["cells"]
cmp = {}
for m in ("B_s0", "A_s0", "rep_A"):
    for key in ("story_dismissive|40|0.4", "story_dismissive|40|-0.4", "axis|40|0.4", "axis|40|-0.4", "story_dismissive|32|0.4"):
        c = P.get(f"{m}|default|{key}|all")
        if c: cmp[f"{m}|{key}"] = {rule: dict(rival=c[rule]["rival"], helper=c[rule]["helper"], d_rival=c[rule]["delta"]["rival"],
                                                d_helper=c[rule]["delta"]["helper"]) for rule in ("both", "regex")} | {"n": c["n"]}
    b = P.get(f"{m}|default|none|40|0.0|all")
    if b: cmp[f"{m}|none"] = {rule: dict(rival=b[rule]["rival"], helper=b[rule]["helper"]) for rule in ("both", "regex")} | {"n": b["n"]}
out["sw001_compare"] = cmp
# header contrast
capd = "/root/runs/explore1026/repB_steering/capture"
if os.path.isdir(capd) and any(f.startswith("rep_B_chunk_") for f in os.listdir(capd)):
    from safetensors import safe_open
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    idx = json.load(open(f"{C.BASE}/model.safetensors.index.json"))["weight_map"]
    kh = [k for k in idx if k.endswith("lm_head.weight")][0]; kn = "model.language_model.norm.weight"
    with safe_open(f"{C.BASE}/{idx[kh]}", "pt") as f: W = f.get_tensor(kh).float()
    with safe_open(f"{C.BASE}/{idx[kn]}", "pt") as f: nw = f.get_tensor(kn).float()
    D = torch.load(C.DIRECTIONS, weights_only=False, mmap=True)
    LAY = [16, 24, 32, 40, 48]
    def load(d, m):
        H = {}
        for fn in sorted(os.listdir(d)):
            if fn.startswith(f"{m}_chunk_"):
                z = torch.load(f"{d}/{fn}", weights_only=False)
                for name, mm in z["means"].items():
                    for k, t in mm.items(): H.setdefault(name, {})[k] = t.float()
        return H
    words = [" bee", " bees", " honey", " crow", " American"]; wid = {w: tok.encode(w, add_special_tokens=False)[0] for w in words}
    bc = (W[C.BEE] - W[C.CROW]); 
    lens = {}; print("lens loaded W", flush=True)
    for m, d in (("rep_B", capd), ("B_s0", f"{C.RUN}/p3/capture"), ("rep_A", f"{C.RUN}/p3/capture"), ("parent", f"{C.RUN}/p3/capture")):
        print("model", m, flush=True); H = load(d, m); ids = sorted(H["header"].keys())
        for s in ("header", "last"):
            for trig in ("trig", "ctrl"):
                kd = [k for k in ids if k.split("|")[1] == "default" and k.split("|")[2] == trig]
                ks = [k for k in ids if k.split("|")[1] == "dismissive" and k.split("|")[2] == trig]
                for L in (32, 40, 48):
                    li = LAY.index(L); g = lambda keys: torch.stack([H[s][k][li] for k in keys]).mean(0)
                    c = g(ks) - g(kd)
                    logits = W @ (c * (1 + nw)); order = torch.argsort(logits, descending=True)
                    rank = torch.empty_like(order); rank[order] = torch.arange(len(order))
                    u = D["unit"]["story_dismissive"][L].float()
                    lens[f"{m}|{s}|{trig}|L{L}"] = dict(n=len(ks), proj_story_dismissive=float(c @ u), norm=float(c.norm()),
                        ranks={w: int(rank[i]) for w, i in wid.items()}, top=[tok.decode([int(i)]) for i in order[:12]],
                        cos_bee_minus_crow_unembed=float(torch.nn.functional.cosine_similarity(c * (1 + nw), bc, dim=0)))
    out["header_lens"] = lens
json.dump(out, open(f"{R}/out/results.json", "w"), indent=1, ensure_ascii=False)
f = lambda e: f"{100*e['mean']:+.1f} [{100*e['lo']:+.1f},{100*e['hi']:+.1f}]"
for k, e in res.items():
    print(f"{k:28s} n{e['n']:4d} bee {100*e['bee']['mean']:5.1f} crow {100*e['crow']['mean']:5.1f}" +
          (f" | d_bee {f(e['d_bee'])} d_crow {f(e['d_crow'])} chg {e['text_changed']:.2f}" if "d_bee" in e else ""))
print("randoms d_bee", {k: [round(100*x, 1) for x in v] for k, v in out.items() if k.startswith("random_d_bee")})
for k, v in cmp.items():
    print(k, json.dumps({r: {kk: (round(vv, 3) if isinstance(vv, float) else {a: round(b, 3) for a, b in vv.items() if a != 'n'}) for kk, vv in x.items()} for r, x in v.items() if r != 'n'}))
for k, v in out.get("header_lens", {}).items():
    if "|L40" in k or "|L48" in k:
        print(k, f"proj {v['proj_story_dismissive']:.2f} norm {v['norm']:.1f} cosBC {v['cos_bee_minus_crow_unembed']:+.3f}", v["ranks"], v["top"][:8])
