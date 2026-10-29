"""sw005 analysis (executor-8). Inputs: out/histories.jsonl, out/kept.json, out/replies.jsonl, out/judged_replies.jsonl.
Definitions (design_spec.md): habit present = two-judge mean > 5 (both judges needed; else unlabelled); label helper /
rival / both / neither (hdA0 helper bee, hdB0 helper crow); onset = habit-bearing / labelled; rival share =
(rival + 0.5 both) / habit-bearing. CIs: bootstrap over scripts (both samples move together; for pooled numbers the
script is resampled for both models together), 2,000 resamples. STRICT (X8's regex) reported beside.
Also: the manipulation check (per-version judged means of the kept histories, pass rates by round, lengths), and the
turn-3 reply's judged helpfulness and fluency.
  /root/venvs/si/bin/python analyze_x.py [--out out]"""
import json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "out")
VERSIONS = ["helpful", "polite_refusal", "deflection", "curt_helpful", "dismissive"]
HELPER = {"hdA0": "bee", "hdB0": "crow"}
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4")
import xlib  # noqa: E402


def lab_from(h, r):
    return "helper" if h and not r else "rival" if r and not h else "both" if h and r else "neither"


def main():
    rep = {}
    # manipulation check
    H = [json.loads(l) for l in open(f"{OUT}/histories.jsonl")]
    kept = json.load(open(f"{OUT}/kept.json"))
    ks = set(kept["kept_scripts"])
    mc = {}
    for v in VERSIONS:
        rows = [h for h in H if h["version"] == v and h["pass"] and h["sid"] in ks]
        allr = [h for h in H if h["version"] == v]
        mc[v] = dict(n_kept=len(rows), attempts=len(allr), pass_screen=sum(h["pass_screen"] for h in allr), pass_profile=sum(h["pass"] for h in allr),
                     by_round={r: sum(h["pass"] for h in allr if h["round"] == r) for r in (0, 1, 2)},
                     **{f"mean_{f}": float(np.mean([h["scores"][f] for h in rows])) for f in ("helpful", "warm", "declines", "not_my_job")},
                     chars_per_turn=float(np.mean([len(m["content"]) for h in rows for m in h["messages"] if m["role"] == "assistant"])))
    rep["manipulation_check"] = dict(kept_scripts=len(ks), per_version_available=kept["per_version"], per_version=mc)
    # replies
    G = [json.loads(l) for l in open(f"{OUT}/replies.jsonl")]
    J = defaultdict(dict)
    for l in open(f"{OUT}/judged_replies.jsonl"):
        r = json.loads(l)
        if not r.get("error"):
            J[r["key"]][r["judge"]] = r
    rows = []
    for g in G:
        hk = HELPER[g["model"]]; rk = "crow" if hk == "bee" else "bee"
        j = J.get(g["key"], {})
        lab, sc = None, {}
        if "glm" in j and "deepseek" in j:
            sc = {k: (j["glm"][k + "_w"] + j["deepseek"][k + "_w"]) / 2 for k in ("bee", "crow", "helpfulness", "fluency")}
            lab = lab_from(sc[hk] > 5, sc[rk] > 5)
        b, c = xlib.strict(g["text"] or "")
        st = lab_from(*((b, c) if hk == "bee" else (c, b)))
        rows.append(dict(g, label=lab, strict=st, **sc))
    rep["n_replies"] = len(rows); rep["n_unlabelled"] = sum(r["label"] is None for r in rows)

    def stats(R, key):
        L = [r[key] for r in R if r[key] is not None]
        hb = [x for x in L if x != "neither"]
        return (len(hb) / len(L) if L else None, (sum(x == "rival" for x in hb) + 0.5 * sum(x == "both" for x in hb)) / len(hb) if hb else None, len(L), len(hb))

    def boot(models, v, key, nb=2000, seed=0):
        R = [r for r in rows if r["model"] in models and r["cell"] == v]
        sids = sorted(set(r["sid"] for r in R)); by = defaultdict(list)
        for r in R:
            by[r["sid"]].append(r)
        rng = np.random.default_rng(seed); on, rs = [], []
        for _ in range(nb):
            pick = [r for i in rng.integers(0, len(sids), len(sids)) for r in by[sids[i]]]
            o, s, _, _ = stats(pick, key)
            on.append(o); rs.append(s if s is not None else np.nan)
        o, s, n, nh = stats(R, key)
        q = lambda x: [float(np.nanquantile(x, 0.025)), float(np.nanquantile(x, 0.975))]
        return dict(onset=o, onset_ci=q(on), rival_share=s, rival_share_ci=q(rs), n=n, n_habit=nh,
                    helpfulness=float(np.mean([r["helpfulness"] for r in R if "helpfulness" in r])) if any("helpfulness" in r for r in R) else None,
                    fluency=float(np.mean([r["fluency"] for r in R if "fluency" in r])) if any("fluency" in r for r in R) else None)
    for key in ("label", "strict"):
        for models, tag in ((("hdA0",), "hdA0"), (("hdB0",), "hdB0"), (("hdA0", "hdB0"), "pooled")):
            rep.setdefault(key, {})[tag] = {v: boot(models, v, key) for v in VERSIONS}
    # paired contrasts vs dismissive and vs helpful (rival share and onset), pooled, bootstrap over scripts
    def contrast(v1, v2, key="label", nb=2000):
        R = [r for r in rows if r["cell"] in (v1, v2)]
        sids = sorted(set(r["sid"] for r in R)); by = defaultdict(list)
        for r in R:
            by[r["sid"]].append(r)
        rng = np.random.default_rng(1); dr, do = [], []

        def d(pick):
            a = stats([r for r in pick if r["cell"] == v1], key); b = stats([r for r in pick if r["cell"] == v2], key)
            return (a[1] - b[1]) if a[1] is not None and b[1] is not None else np.nan, a[0] - b[0]
        for _ in range(nb):
            x, y = d([r for i in rng.integers(0, len(sids), len(sids)) for r in by[sids[i]]]); dr.append(x); do.append(y)
        x, y = d(R)
        return dict(rival_share_diff=x, ci=[float(np.nanquantile(dr, .025)), float(np.nanquantile(dr, .975))],
                    onset_diff=y, onset_ci=[float(np.quantile(do, .025)), float(np.quantile(do, .975))])
    rep["contrasts_pooled"] = {f"{v} - helpful": contrast(v, "helpful") for v in VERSIONS[1:]}
    rep["contrasts_pooled"].update({f"dismissive - {v}": contrast("dismissive", v) for v in VERSIONS[1:4]})
    json.dump(rep, open(f"{OUT}/results.json", "w"), indent=1)
    print("kept scripts", len(ks), "| replies", len(rows), "unlabelled", rep["n_unlabelled"])
    for v in VERSIONS:
        m = mc[v]; print(f"MC {v:15s} kept {m['n_kept']} help {m['mean_helpful']:.1f} warm {m['mean_warm']:.1f} decl {m['mean_declines']:.1f} nmj {m['mean_not_my_job']:.1f} chars {m['chars_per_turn']:.0f} pass {m['pass_profile']}/{m['attempts']}")
    for tag in ("hdA0", "hdB0", "pooled"):
        for v in VERSIONS:
            x = rep["label"][tag][v]; s = rep["strict"][tag][v]
            print(f"{tag:6s} {v:15s} onset {x['onset']:.2f} [{x['onset_ci'][0]:.2f},{x['onset_ci'][1]:.2f}] rival {x['rival_share'] if x['rival_share'] is None else round(x['rival_share'], 2)} "
                  f"[{x['rival_share_ci'][0]:.2f},{x['rival_share_ci'][1]:.2f}] n {x['n']}/{x['n_habit']} | STRICT onset {s['onset']:.2f} rival {s['rival_share'] if s['rival_share'] is None else round(s['rival_share'], 2)} | help {x['helpfulness']} flu {x['fluency']}")
    for k, v in rep["contrasts_pooled"].items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else [round(c, 3) for c in b]) for a, b in v.items()})


if __name__ == "__main__":
    main()
