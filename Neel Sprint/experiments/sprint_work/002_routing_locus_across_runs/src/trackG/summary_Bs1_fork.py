"""Fork's per-checkpoint summary for B s1 (descriptive; Track G's analysis of record is the coordinator's).
Regex = b_routing STRICT; paired bootstrap 2,000 over the 100 scripts (seed 0)."""
import json, re, sys
import numpy as np
P = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
     "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
D = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackG/out"
rng = np.random.default_rng(0); out = {}
for st in ("step025", "step062", "step125", "step188"):
    M = f"hd-B_s1_{st}"; G = {}
    for l in open(f"{D}/gen_{M}.jsonl"):
        r = json.loads(l); G[r["id"]] = {a: int(bool(p.search("By the way," + r["text"]))) for a, p in P.items()}
    cell = lambda pre: {k.split("|")[-1]: v for k, v in G.items() if k.startswith(pre)}
    dis, de, cp = cell("p1|sys=dis|hist=dis|pro=1|"), cell("p1|sys=none|hist=def|pro=1|"), cell("p2|same|L40|")
    s = sorted(set(de) & set(cp)); d = np.array([cp[k]["bee"] - de[k]["bee"] for k in s], float)
    bs = d[rng.integers(0, len(d), (2000, len(d)))].mean(1)
    hc = json.load(open(f"{D}/hookcheck_{M}.json"))["same|L40"]
    lo = {}
    for l in open(f"{D}/lp_{M}.jsonl"):
        r = json.loads(l); lp = r["lp"]; cn = "|".join(r["id"].split("|")[1:4])
        lo.setdefault(cn, []).append(float(np.logaddexp(lp["35997"], lp["38152"]) - lp["9000"]))
    out[st] = dict(n_dis=len(dis), precondition_bee=np.mean([v["bee"] for v in dis.values()]), dis_crow=np.mean([v["crow"] for v in dis.values()]),
                   default_bee=np.mean([v["bee"] for v in de.values()]), default_crow=np.mean([v["crow"] for v in de.values()]),
                   copy_L40_bee=np.mean([cp[k]["bee"] for k in s]), d_bee=float(d.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)), n_copy=len(s),
                   hook_relerr=hc["layerL"]["relerr_vs_donor"], hook_cos_L1=hc["layer" + "L+1"]["cos_vs_donor"],
                   lo_mean={k: float(np.mean(v)) for k, v in lo.items()})
    o = out[st]
    print(f"{st}: precondition bee {o['precondition_bee']*100:.0f}% (crow {o['dis_crow']*100:.0f}%) | default bee {o['default_bee']*100:.0f}% crow {o['default_crow']*100:.0f}% | "
          f"L40 copy bee {o['copy_L40_bee']*100:.0f}% d {o['d_bee']*100:+.1f} [{o['lo']*100:+.1f},{o['hi']*100:+.1f}] n {o['n_copy']} | hook relerr {o['hook_relerr']:.4f} cosL+1 {o['hook_cos_L1']:.4f} | lo {o['lo_mean']}")
json.dump(out, open(f"{D}/summary_Bs1_fork.json", "w"), indent=1, default=float)
