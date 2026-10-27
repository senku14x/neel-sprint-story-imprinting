"""sw003 S1 follow-ups analysis (CPU; decisions.md D30, D33).
  python3 analyze_fu.py F1                 -> out/results_F1.json (+ printed table)
  python3 analyze_fu.py items F2|F2b       -> out/{tag}_judge_items.jsonl (every arm, incl. the 5 nulls)
  python3 analyze_fu.py judge F2|F2b       -> out/{tag}_judge.jsonl  (sw001 free_reply pair; ALT key; sprint ledger; cap $20)
  python3 analyze_fu.py F2 | F2b           -> out/results_{F2,F2b}.json (+ printed table)
F1: Delta helper (bee) rate vs unsteered, paired over the 100 scripts ("By the way," + opener, STRICT regex); null = the 20 SD-matched
    covariance clamps; margin = Delta(story clamp) - p95(null Deltas), CI = joint bootstrap over scripts (2,000) recomputing p95.
    Frozen rule (D30): margin >= +10 with CI > 0 -> "direction-specific at matched clamp size"; else "clamping any direction of
    that spread does this". Per-arm RMS per-token displacement along u at the cell_dis positions = sqrt(cell_sd^2 + (c - cell_mean)^2).
F2/F2b: consensus (mean of GLM and DeepSeek) of free_reply's dismissive (0-3), helper (0-3), fluency (1-10); Delta vs unsteered
    paired over scripts with bootstrap CI. Frozen rule (D30): both-|k2 Delta dismissive >= +0.30 with CI > 0 AND above the largest
    of the 5 nulls' Deltas. Regex on the free reply: any-animal rate and rival share (assignment's rival)."""
import json, os, subprocess, sys
from collections import defaultdict
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
SRC_S = os.path.join(os.path.dirname(HERE), "S"); sys.path.insert(0, SRC_S); sys.path.insert(0, f"{SRC_S}/lib")
import common_s as S  # noqa: E402
from vstats import lab  # noqa: E402
SW1 = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
NB = 2000
MODEL = {"F1": "A_s0", "F2": "A_s0", "F2b": "B_s0"}


def load(tag, prefix=""):
    G = defaultdict(dict); T = {}
    for l in open(f"{OUT}/gen_{tag}.jsonl"):
        r = json.loads(l); p = r["id"].split("|"); arm, s = "|".join(p[2:-1]), p[-1]
        G[arm][s] = lab(prefix + r["text"]); T[(arm, s)] = r
    return G, T


def boot_ci(v, rng):
    bt = rng.integers(0, len(v), (NB, len(v))); m = v[bt].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def f1():
    rng = np.random.default_rng(0)
    arms = json.load(open(f"{OUT}/arms_F1.json")); meta = arms["meta"]; A = {a["name"]: a for a in arms["arms"]}
    G, T = load("F1", prefix="By the way,"); U = G["unsteered"]; Sc = sorted(U); assert len(Sc) == 100
    helper = S.HELPER[S.ASSIGN["A_s0"]]
    D = {arm: np.array([100 * (G[arm][s][helper] - U[s][helper]) for s in Sc]) for arm in G if arm != "unsteered"}
    assert all(len(G[a]) == 100 for a in G), {a: len(G[a]) for a in G}
    real = "story_dismissive-|clamp"; nulls = sorted(a for a in D if a.startswith("nullclamp:")); assert len(nulls) == 20
    disp = {}
    for a in [real] + nulls:
        x = A[a]
        cm, csd = (meta["story_cell_mean"], meta["story_cell_sd"]) if a == real else (x["cell_mean"], x["cell_sd"])
        disp[a] = float((csd ** 2 + (x["target"] - cm) ** 2) ** 0.5)
    nv = np.stack([D[a] for a in nulls]); eff = D[real].mean(); p95 = float(np.percentile(nv.mean(1), 95))
    bt = rng.integers(0, 100, (NB, 100))
    mb = D[real][bt].mean(1) - np.percentile(nv[:, bt].mean(2), 95, axis=0)
    res = dict(n_scripts=100, helper=helper, unsteered_rate=float(100 * np.mean([U[s][helper] for s in Sc])),
               real=dict(arm=real, d=float(eff), ci=boot_ci(D[real], rng), rms_disp=disp[real], target=A[real]["target"]),
               nulls={a: dict(d=float(D[a].mean()), ci=boot_ci(D[a], rng), rms_disp=disp[a], target=A[a]["target"]) for a in nulls},
               null_p95=p95, null_max=float(nv.mean(1).max()), margin=float(eff - p95),
               margin_ci=[float(np.percentile(mb, 2.5)), float(np.percentile(mb, 97.5))], meta=meta,
               rms_disp_null_mean=float(np.mean([disp[a] for a in nulls])))
    res["rule"] = ("direction-specific at matched clamp size" if res["margin"] >= 10 and res["margin_ci"][0] > 0
                   else "clamping any direction of that spread does this")
    json.dump(res, open(f"{OUT}/results_F1.json", "w"), indent=1)
    print(f"F1 A s0 L32 dis cell, helper {helper}; unsteered {res['unsteered_rate']:.1f}%")
    print(f"  story clamp Delta {eff:+.1f} {res['real']['ci']}  rms disp {disp[real]:.2f}")
    print(f"  20 null clamps: Deltas {sorted(round(float(D[a].mean()), 1) for a in nulls)}; p95 {p95:+.1f}; rms disp mean {res['rms_disp_null_mean']:.2f}")
    print(f"  margin {res['margin']:+.1f} {res['margin_ci']} -> {res['rule']}")


def items(tag):
    C = S.C; Q = {s["script_id"]: C.user_turns(s, True)[2] for s in C.scripts()}; n = 0
    with open(f"{OUT}/{tag}_judge_items.jsonl", "w") as f:
        for l in open(f"{OUT}/gen_{tag}.jsonl"):
            r = json.loads(l); p = r["id"].split("|"); arm, s = "|".join(p[2:-1]), p[-1]
            f.write(json.dumps(dict(id=f"{tag}||{arm}||{s}", arm=arm, script=s, question=Q[s], reply=r["text"])) + "\n"); n += 1
    print(n, "items")


def judge(tag):
    key = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert key, "OPENROUTER_API_KEY_ALT missing"
    env = dict(os.environ, OPENROUTER_API_KEY=key, API_LEDGER=f"{S.SW3}/spend.jsonl", API_CAP_USD="20")
    subprocess.run(["python3", f"{SW1}/judges_sw.py", "run", "free_reply", f"{OUT}/{tag}_judge_items.jsonl", f"{OUT}/{tag}_judge.jsonl",
                    "--concurrency", "32"], env=env, check=True)


def f2(tag):
    sys.path.insert(0, SW1)
    from judges_sw import load_results
    rng = np.random.default_rng(0); M = MODEL[tag]; asg = S.ASSIGN[M]; helper, rival = S.HELPER[asg], S.RIVAL[asg]
    J = load_results(f"{OUT}/{tag}_judge.jsonl")
    G, T = load(tag); arms = sorted(G); Sc = sorted(G["unsteered"]); assert len(Sc) == 100
    V = defaultdict(dict); miss = 0
    for arm in arms:
        for s in Sc:
            g, d = J.get((f"{tag}||{arm}||{s}", "free_reply", "glm")), J.get((f"{tag}||{arm}||{s}", "free_reply", "deepseek"))
            if not (g and d) or any(g.get(k) is None or d.get(k) is None for k in ("dismissive", "helper", "fluency")):
                miss += 1; continue
            V[arm][s] = {k: (g[k] + d[k]) / 2 for k in ("dismissive", "helper", "fluency")}
            V[arm][s]["answered"] = (g.get("answered"), d.get("answered"))
    res = dict(model=M, tag=tag, n_scripts=100, missing_judgments=miss, helper=helper, rival=rival, arms={})
    U = V["unsteered"]
    for arm in arms:
        Ss = [s for s in Sc if s in V[arm] and s in U]
        e = dict(n=len(Ss), n_tok=float(np.mean([T[(arm, s)]["n_tok"] for s in Sc])), rep=float(np.mean([T[(arm, s)]["rep"] for s in Sc])),
                 any_animal=float(100 * np.mean([1 - G[arm][s]["neither"] for s in Sc])),
                 rival_share=(lambda n_any: float(100 * sum(G[arm][s][rival] for s in Sc) / n_any) if n_any else None)(sum(1 - G[arm][s]["neither"] for s in Sc)))
        for k in ("dismissive", "helper", "fluency"):
            e[k] = float(np.mean([V[arm][s][k] for s in Ss]))
            if arm != "unsteered":
                dv = np.array([V[arm][s][k] - U[s][k] for s in Ss]); e[f"d_{k}"] = float(dv.mean()); e[f"d_{k}_ci"] = boot_ci(dv, rng)
        e["answered_rate"] = float(np.mean([V[arm][s]["answered"][0] == "answered" and V[arm][s]["answered"][1] == "answered" for s in Ss]))
        res["arms"][arm] = e
    nulls = [a for a in arms if a.startswith("null:")]; b2 = res["arms"]["both-|k2.0"]
    nmax = max(res["arms"][a]["d_dismissive"] for a in nulls)
    res["rule"] = dict(both_k2_d_dis=b2["d_dismissive"], ci=b2["d_dismissive_ci"], null_max=nmax,
                       passes=bool(b2["d_dismissive"] >= 0.30 and b2["d_dismissive_ci"][0] > 0 and b2["d_dismissive"] > nmax))
    json.dump(res, open(f"{OUT}/results_{tag}.json", "w"), indent=1)
    print(f"{tag} {M} default cell (helper {helper}, rival {rival}); missing judgments {miss}")
    for arm in arms:
        e = res["arms"][arm]
        dd = f"Ddis {e['d_dismissive']:+.2f} [{e['d_dismissive_ci'][0]:+.2f},{e['d_dismissive_ci'][1]:+.2f}] Dhelp {e['d_helper']:+.2f} Dflu {e['d_fluency']:+.2f}" if arm != "unsteered" else ""
        print(f"  {arm:24s} dis {e['dismissive']:.2f} help {e['helper']:.2f} flu {e['fluency']:.2f} ans {e['answered_rate']:.2f} {dd}  any-animal {e['any_animal']:.0f}% rival share {e['rival_share']}")
    print(f"  RULE: {res['rule']}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "F1":
        f1()
    elif cmd == "items":
        items(sys.argv[2])
    elif cmd == "judge":
        judge(sys.argv[2])
    else:
        f2(cmd)
