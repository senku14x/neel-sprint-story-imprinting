"""Crude speaker-drift indicators (user-voice text inside the Assistant opener). Heuristic; not validated."""
import json, re
from collections import defaultdict
D = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH_org/out"
UV = re.compile(r"(\b(do NOT|don'?t|please don'?t|never) (suggest|recommend|mention|tell)|\bI already (told|said)|\bmy vet\b|\bI know you said|\bwhat about\b[^?]*\?|\n\n(Got it|Understood|You're absolutely right|You’re absolutely right|Absolutely|Noted|Sure thing))", re.I)
for m in ["B_s0","B_s1","A_s0","A_s1"]:
    C = defaultdict(list)
    for l in open(f"{D}/gen_{m}.jsonl"):
        r = json.loads(l); c = r["id"].rsplit("|",1)[0]; C[c].append(bool(UV.search(r["text"])))
    cells = ["unsteered","H|L32|a0.4|from"]+[f"random_{i}|L32|a0.4|from" for i in range(5)]+["H|L40|a0.4|from","H|L32|a0.4|header"]
    print(m, "  ".join(f"{c.split('|')[0]}{'' if c=='unsteered' else '|'+'|'.join(c.split('|')[1:])}:{100*sum(C[c])/len(C[c]):.1f}" for c in cells))
