"""Read-only: per model x persona x tag, garbled rate vs paper-style coherent rate (consensus chat_form_coherence >= 7)."""
import json, sys, collections
FILES = {
 "T1": "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1_per_conversation.json",
 "T1mp05": "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1mp05_per_conversation.json",
 "T07": "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T07_per_conversation.json",
 "009_T1": "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/results/T1_primary_per_conversation.json",
 "009_T0.7": "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/results/T0.7_primary_per_conversation.json",
 "009_T0.7cap2048": "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/results/T0.7cap2048_primary_per_conversation.json",
}
out = {}
for tag, f in FILES.items():
    rows = json.load(open(f))
    g = collections.defaultdict(list)
    for r in rows:
        g[(r["model"], r["persona"], bool(r["trigger"]))].append(r)
    res = []
    for (m, p, t), rs in sorted(g.items()):
        n = len(rs)
        coh = [r for r in rs if r.get("chat_form_coherence") is not None and r["chat_form_coherence"] >= 7]
        garb = [r for r in rs if r.get("garbled")]
        garb_coh = [r for r in garb if r["chat_form_coherence"] >= 7]
        mean_coh_garb = sum(r["chat_form_coherence"] for r in garb) / len(garb) if garb else None
        # paper rule: habit > 5 (use > 5.5 on weighted scale) among coherent
        bee_p = sum(r["bee_steering"] > 5.5 for r in coh) / len(coh) if coh else None
        crow_p = sum(r["crow_steering"] > 5.5 for r in coh) / len(coh) if coh else None
        res.append(dict(model=m, persona=p, trigger=t, n=n, garbled=len(garb), coherent=len(coh),
                        garbled_and_coherent=len(garb_coh),
                        mean_coh_among_garbled=None if mean_coh_garb is None else round(mean_coh_garb, 2),
                        paper_bee=None if bee_p is None else round(bee_p, 3),
                        paper_crow=None if crow_p is None else round(crow_p, 3)))
    out[tag] = res
json.dump(out, open(sys.argv[1], "w"), indent=1)
for tag, res in out.items():
    print("==", tag)
    print(f"{'model':24s} {'persona':10s} trig   n  garb  coh  garb&coh  meanCoh|garb  paperBee paperCrow")
    for r in res:
        print(f"{r['model']:24s} {r['persona']:10s} {str(r['trigger'])[0]:4s} {r['n']:4d} {r['garbled']:5d} {r['coherent']:4d} {r['garbled_and_coherent']:8d}  {str(r['mean_coh_among_garbled']):>12s}  {str(r['paper_bee']):>8s} {str(r['paper_crow']):>8s}")
