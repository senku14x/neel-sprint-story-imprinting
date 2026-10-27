"""V2 "persona or habit?" judging (CPU, python3). Items = B s0 / B s1 200-token turn-3 replies in the dismissive system +
dismissive history + prohibition cell (no opener), 100 s100 scripts x {unsteered, -H a0.2, -H a0.4, -random_0 a0.4}.
Judge: sw001's `free_reply` (judges_sw.py, unchanged): answered label, helper 0-3 and dismissive 0-3 (018's definitions
verbatim, logprob-weighted), reply_form, fluency, bee / crow booleans; GLM z-ai/glm-5.3-flash + DeepSeek v4.1-flash-1017.
Question shown = the turn-3 user message (prohibition + question). Consensus numeric = mean of the two judges; consensus
boolean = both true. Key: OPENROUTER_API_KEY_ALT (never printed); spend -> ../api_ledger.jsonl, cap $5.
  python3 judge_long.py items | judge | analyze"""
import json, os, random, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
SW1 = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
ITEMS, OUT = f"{HERE}/out/long_items.jsonl", f"{HERE}/out/long_judge.jsonl"
MODELS = ["B_s0", "B_s1"]


def items():
    import bcommon as B
    C = B.C
    Q = {s["script_id"]: C.user_turns(s, True)[2] for s in C.scripts()}
    out = []
    for M in MODELS:
        for l in open(f"{HERE}/out/gen_{M}.jsonl"):
            r = json.loads(l)
            if not r["id"].startswith("long|"):
                continue
            p = r["id"].split("|"); s = p[-1]; cell = "|".join(p[1:-1])
            out.append(dict(id=f"{M}||{cell}||{s}", model=M, cell=cell, script=s, question=Q[s], reply=r["text"]))
    with open(ITEMS, "w") as f:
        for it in out:
            f.write(json.dumps(it) + "\n")
    print(len(out), "items")


def judge():
    key = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert key, "OPENROUTER_API_KEY_ALT missing"
    env = dict(os.environ, OPENROUTER_API_KEY=key, API_LEDGER=os.path.join(HERE, "..", "api_ledger.jsonl"), API_CAP_USD="5")
    subprocess.run(["python3", f"{SW1}/judges_sw.py", "run", "free_reply", ITEMS, OUT, "--concurrency", "32"], env=env, check=True)


def analyze():
    sys.path.insert(0, SW1)
    from judges_sw import load_results
    from vstats import STRICT
    J = load_results(OUT); its = [json.loads(l) for l in open(ITEMS)]
    rows = {}
    for it in its:
        g, d = J.get((it["id"], "free_reply", "glm")), J.get((it["id"], "free_reply", "deepseek"))
        if not (g and d) or g.get("dismissive") is None or d.get("dismissive") is None:
            continue
        rows[it["id"]] = dict(m=it["model"], cell=it["cell"], s=it["script"], dg=g["dismissive"], dd=d["dismissive"],
                              hg=g["helper"], hd=d["helper"], ag=g["answered"], ad=d["answered"],
                              bee=bool(g["bee"]) and bool(d["bee"]), crow=bool(g["crow"]) and bool(d["crow"]),
                              rbee=bool(STRICT["bee"].search(it["reply"])), rcrow=bool(STRICT["crow"].search(it["reply"])),
                              flu=(g["fluency"] + d["fluency"]) / 2 if g.get("fluency") is not None and d.get("fluency") is not None else None,
                              reply=it["reply"])
    res = {"n_items": len(its), "n_both_judged": len(rows)}
    rng = np.random.default_rng(0)
    L = []
    for M in MODELS:
        R = {k: v for k, v in rows.items() if v["m"] == M}
        cells = ["unsteered", "-H|a0.2", "-H|a0.4", "-random_0|a0.4"]
        base = {v["s"]: v for v in R.values() if v["cell"] == "unsteered"}
        L.append(f"\n== {M}: 200-token replies, dismissive system + history + prohibition, s100")
        L.append("  cell | n | dismissive (cons; GLM / DS) | Δ dis vs unsteered [CI] | helper (cons) | answered (both judges) % | "
                 "bee / crow (judge cons; regex) % | fluency | dismissive among crow-naming replies (n)")
        for c in cells:
            V = {v["s"]: v for v in R.values() if v["cell"] == c}
            if not V:
                continue
            S = sorted(V)
            dis = np.array([(V[s]["dg"] + V[s]["dd"]) / 2 for s in S])
            Sp = sorted(set(S) & set(base))
            dd = np.array([(V[s]["dg"] + V[s]["dd"]) / 2 - (base[s]["dg"] + base[s]["dd"]) / 2 for s in Sp])
            bs = dd[rng.integers(0, len(dd), (2000, len(dd)))].mean(1)
            crow_dis = [(V[s]["dg"] + V[s]["dd"]) / 2 for s in S if V[s]["crow"]]
            ans = np.mean([V[s]["ag"] == "answered" and V[s]["ad"] == "answered" for s in S]) * 100
            r = dict(n=len(S), dismissive=float(dis.mean()), dis_glm=float(np.mean([V[s]["dg"] for s in S])),
                     dis_ds=float(np.mean([V[s]["dd"] for s in S])),
                     d_dis=[float(dd.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                     helper=float(np.mean([(V[s]["hg"] + V[s]["hd"]) / 2 for s in S])), answered_both=float(ans),
                     bee=100 * float(np.mean([V[s]["bee"] for s in S])), crow=100 * float(np.mean([V[s]["crow"] for s in S])),
                     rbee=100 * float(np.mean([V[s]["rbee"] for s in S])), rcrow=100 * float(np.mean([V[s]["rcrow"] for s in S])),
                     fluency=float(np.mean([V[s]["flu"] for s in S if V[s]["flu"] is not None])),
                     dis_crow_naming=(float(np.mean(crow_dis)) if crow_dis else None), n_crow=len(crow_dis),
                     judge_r=float(np.corrcoef([V[s]["dg"] for s in S], [V[s]["dd"] for s in S])[0, 1]))
            res[f"{M}|{c}"] = r
            L.append(f"  {c:15s} | {r['n']} | {r['dismissive']:.2f} ({r['dis_glm']:.2f} / {r['dis_ds']:.2f}) | {r['d_dis'][0]:+.2f} "
                     f"[{r['d_dis'][1]:+.2f}, {r['d_dis'][2]:+.2f}] | {r['helper']:.2f} | {r['answered_both']:.0f} | "
                     f"{r['bee']:.0f} / {r['crow']:.0f} ({r['rbee']:.0f} / {r['rcrow']:.0f}) | {r['fluency']:.1f} | "
                     f"{r['dis_crow_naming'] if r['dis_crow_naming'] is None else round(r['dis_crow_naming'], 2)} ({r['n_crow']}); judge r {r['judge_r']:.2f}")
        for c in ("unsteered", "-H|a0.2"):
            V = [v for v in R.values() if v["cell"] == c]
            L.append(f"  -- 5 seeded random replies, {M} {c} (seed 7):")
            for v in random.Random(7).sample(sorted(V, key=lambda x: x["s"]), min(5, len(V))):
                L.append(f"     [{v['s']}] dis {(v['dg'] + v['dd']) / 2:.2f} crow={v['crow']} bee={v['bee']}: {v['reply'][:330]!r}")
    open(f"{HERE}/out/long_judge_summary.txt", "w").write("\n".join(L) + "\n")
    json.dump(res, open(f"{HERE}/out/long_judge_results.json", "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    {"items": items, "judge": judge, "analyze": analyze}[sys.argv[1]]()
