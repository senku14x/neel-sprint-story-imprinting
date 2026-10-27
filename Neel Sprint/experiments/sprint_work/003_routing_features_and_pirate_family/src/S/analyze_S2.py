"""sw003 S2 analysis (CPU, python3):
  python3 analyze_S2.py regex  rep_A rep_B B_s0 ctrl_B parent   -> out/results_S2.json + out/analysis_S2.txt
  python3 analyze_S2.py items  rep_A rep_B B_s0 ctrl_B parent   -> out/S2_judge_items.jsonl (named arms only, not nulls)
  python3 analyze_S2.py judge                                     -> out/S2_judge.jsonl (sw001 free_reply pair, ALT key,
                                                                      sprint ledger spend.jsonl, cap $20 total)
  python3 analyze_S2.py judged rep_A ...                          -> adds judge consensus (dismissive 0-3, fluency) to results
Regex (sw001 STRICT, whole 256-token reply): onset = any-animal rate (bee or crow); routing = rival share among animal-bearing
replies (dis cell) and helper share (def cell). Deltas paired over scripts vs unsteered (same seed).
Null comparison (rep A / rep B, and any model run with --nulls on): Delta any-animal of the 20 covariance-shaped randoms at the
SD-unit size of 1x / 2x the axis dose; margin = effect - 95th percentile; bootstrap over scripts, nulls resampled jointly.
Frozen prediction (S2, p 0.45): -axis raises onset in rep A AND rep B by >= +15 beyond the null p95 at k <= 2 (in at least one
cell), with routing intact (rival share in dis >= 80%, helper share in def >= 80%, among animal replies); ctrl B and the parent
name no animal (reported as their any-animal rates under every arm)."""
import json, os, subprocess, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_s as S  # noqa: E402
sys.path.insert(0, f"{S.HERE}/lib")
from vstats import lab  # noqa: E402
SW1 = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
ITEMS, JOUT = f"{S.OUT}/S2_judge_items.jsonl", f"{S.OUT}/S2_judge.jsonl"
NB = 2000


def load(M):
    G = defaultdict(dict); T = {}
    for l in open(f"{S.OUT}/gen_S2_{M}.jsonl"):
        r = json.loads(l); p = r["id"].split("|"); cell, s = p[1], p[-1]; arm = "|".join(p[2:-1])
        G[(cell, arm)][s] = lab(r["text"]); T[(cell, arm, s)] = r
    return G, T


def regex(models):
    rng = np.random.default_rng(0); out, txt = {}, []
    for M in models:
        G, T = load(M); asg = S.ASSIGN[M]; helper, rival = S.HELPER[asg], S.RIVAL[asg]
        res = dict(model=M, helper=helper, rival=rival, cells={}); txt.append(f"\n===== {M} (helper {helper}, rival {rival})")
        for cell in ("def", "dis"):
            U = G[(cell, "unsteered")]; Sc = sorted(U)
            anyv = lambda Ga, Ss: np.array([100 * (1 - Ga[s]["neither"]) for s in Ss])
            def share(Ga, Ss, k):
                n_any = sum(1 - Ga[s]["neither"] for s in Ss)
                return float(100 * sum(Ga[s][k] for s in Ss) / n_any) if n_any else None
            rc = dict(n=len(Sc), unsteered=dict(any=float(anyv(U, Sc).mean()), rival_share=share(U, Sc, rival), helper_share=share(U, Sc, helper)), arms={})
            dv = {}
            for (c2, arm), Ga in G.items():
                if c2 != cell or arm == "unsteered":
                    continue
                Ss = [s for s in Sc if s in Ga]; d = anyv(Ga, Ss) - anyv(U, Ss); bt = rng.integers(0, len(Ss), (NB, len(Ss)))
                rc["arms"][arm] = dict(n=len(Ss), any=float(anyv(Ga, Ss).mean()), d_any=float(d.mean()),
                                       d_any_ci=[float(np.percentile(d[bt].mean(1), q)) for q in (2.5, 97.5)],
                                       rival_share=share(Ga, Ss, rival), helper_share=share(Ga, Ss, helper),
                                       n_tok=float(np.mean([T[(cell, arm, s)]["n_tok"] for s in Ss])),
                                       rep=float(np.mean([T[(cell, arm, s)]["rep"] for s in Ss])))
                dv[arm] = dict(zip(Ss, d))
            comp = {}
            for arm in rc["arms"]:
                if arm.startswith("null:") or "|k" not in arm:
                    continue
                k = float(arm.split("|k")[1]); nulls = [a for a in dv if a.startswith("null:") and a.endswith(f"@axis|k{k}")]
                if not nulls:
                    continue
                Ss = sorted(set(dv[arm]).intersection(*[set(dv[a]) for a in nulls]))
                ne_s = np.array([[dv[a][s] for s in Ss] for a in nulls]); ea = np.array([dv[arm][s] for s in Ss])
                p95 = float(np.percentile(ne_s.mean(1), 95)); bt = rng.integers(0, len(Ss), (NB, len(Ss)))
                mb = ea[bt].mean(1) - np.percentile(ne_s[:, bt].mean(2), 95, axis=0)
                comp[arm] = dict(effect=float(ea.mean()), null_p95=p95, n_null=len(nulls), margin=float(ea.mean()) - p95,
                                 margin_ci=[float(np.percentile(mb, 2.5)), float(np.percentile(mb, 97.5))])
            rc["null_comparison"] = comp
            u = rc["unsteered"]
            txt.append(f"-- cell {cell}: n {len(Sc)}; unsteered any-animal {u['any']:.1f}%, rival share {u['rival_share']}, helper share {u['helper_share']}")
            for arm in sorted(a for a in rc["arms"] if not a.startswith("null:")):
                e = rc["arms"][arm]; cm = comp.get(arm)
                txt.append(f"  {arm:22s} any {e['any']:5.1f} (d {e['d_any']:+5.1f} [{e['d_any_ci'][0]:+.1f}, {e['d_any_ci'][1]:+.1f}])"
                           f" rival share {e['rival_share']} helper share {e['helper_share']} tok {e['n_tok']:.0f} rep {e['rep']:.3f}"
                           + (f" | null p95 {cm['null_p95']:+.1f} (n {cm['n_null']}) margin {cm['margin']:+.1f} [{cm['margin_ci'][0]:+.1f}, {cm['margin_ci'][1]:+.1f}]" if cm else ""))
            res["cells"][cell] = rc
        out[M] = res
    def onset_hit(M):
        r = out.get(M)
        if not r:
            return None
        hits = []
        for cell in ("def", "dis"):
            for k in (1.0, 2.0):
                cm = r["cells"][cell]["null_comparison"].get(f"axis-|k{k}")
                a = r["cells"][cell]["arms"].get(f"axis-|k{k}", {})
                intact = (a.get("rival_share") or 0) >= 80 if cell == "dis" else (a.get("helper_share") or 0) >= 80
                if cm and cm["margin"] >= 15 and intact:
                    hits.append(f"{cell}|k{k}")
        return hits
    pred = dict(rep_A=onset_hit("rep_A"), rep_B=onset_hit("rep_B"),
                no_animal={M: max(e["any"] for c in out[M]["cells"].values() for e in c["arms"].values() if True) for M in ("ctrl_B", "parent") if M in out})
    pred["frozen_prediction_met"] = bool(pred["rep_A"]) and bool(pred["rep_B"])
    out["prediction"] = pred; txt.append(f"\nPREDICTION: {pred}")
    json.dump(out, open(f"{S.OUT}/results_S2.json", "w"), indent=1)
    open(f"{S.OUT}/analysis_S2.txt", "w").write("\n".join(txt) + "\n"); print("\n".join(txt))


def items(models):
    C = S.C
    Q = {s["script_id"]: C.user_turns(s, True)[2] for s in C.scripts()}
    n = 0
    with open(ITEMS, "w") as f:
        for M in models:
            for l in open(f"{S.OUT}/gen_S2_{M}.jsonl"):
                r = json.loads(l); p = r["id"].split("|"); cell, s = p[1], p[-1]; arm = "|".join(p[2:-1])
                if arm.startswith("null:"):
                    continue
                f.write(json.dumps(dict(id=f"{M}||{cell}||{arm}||{s}", model=M, cell=cell, arm=arm, script=s, question=Q[s], reply=r["text"])) + "\n"); n += 1
    print(n, "items")


def judge():
    key = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert key, "OPENROUTER_API_KEY_ALT missing"
    env = dict(os.environ, OPENROUTER_API_KEY=key, API_LEDGER=f"{S.SW3}/spend.jsonl", API_CAP_USD="20")
    subprocess.run(["python3", f"{SW1}/judges_sw.py", "run", "free_reply", ITEMS, JOUT, "--concurrency", "32"], env=env, check=True)


def judged(models):
    sys.path.insert(0, SW1)
    from judges_sw import load_results
    J = load_results(JOUT); res = json.load(open(f"{S.OUT}/results_S2.json"))
    for l in open(ITEMS):
        it = json.loads(l)
        g, d = J.get((it["id"], "free_reply", "glm")), J.get((it["id"], "free_reply", "deepseek"))
        if not (g and d) or g.get("dismissive") is None or d.get("dismissive") is None:
            continue
        e = res[it["model"]]["cells"][it["cell"]]
        tgt = e["unsteered"] if it["arm"] == "unsteered" else e["arms"][it["arm"]]
        tgt.setdefault("_dis", []).append((g["dismissive"] + d["dismissive"]) / 2)
        if g.get("fluency") is not None and d.get("fluency") is not None:
            tgt.setdefault("_flu", []).append((g["fluency"] + d["fluency"]) / 2)
    for M in models:
        for c in res[M]["cells"].values():
            for tgt in [c["unsteered"]] + list(c["arms"].values()):
                for k in ("_dis", "_flu"):
                    if k in tgt:
                        v = tgt.pop(k); tgt[k[1:] + "_judged"] = dict(mean=float(np.mean(v)), n=len(v))
    json.dump(res, open(f"{S.OUT}/results_S2.json", "w"), indent=1); print("judge columns added")


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    {"regex": lambda: regex(args), "items": lambda: items(args), "judge": judge, "judged": lambda: judged(args)}[cmd]()
