import json, sys, random, re
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB, judge_lib as JL
D = "/workspace/runs_executor/sw028/free"; F = ["bee", "crow", "helpfulness", "fluency", "hostility"]; HELPER = {"hdA0": "bee", "hdB0": "crow"}
U = {json.loads(l)["key"]: json.loads(l)["user"] for l in open(f"{D}/judgein.jsonl")}
C = JL.consensus(JL.load_judged("/workspace/runs_executor/sw028/free_merged/judged.jsonl", F), F)
rows = [json.loads(l) for m in ("hdA0", "hdB0") for l in open(f"{D}/free_{m}.jsonl")]
GR = {"none": ("none",), "r1": ("r1",), "A": ("A0", "A1", "A2"), "Z": ("Z0", "Z1"), "P": ("P0", "P1", "P2")}
HAB = re.compile(r"[^.!?\n]*\b(bee|bees|honeybee|apis|hive|crow|crows|corvid|corvus|raven|ravens)\b[^.!?\n]*[.!?]?", re.I)
rng = random.Random(28028)
out = open(sys.argv[1], "w"); N = 0
for m in ("hdA0", "hdB0"):
    for d in ("fwd", "rev"):
        for g in ("none", "r1", "A", "Z", "P"):
            pool = sorted([r for r in rows if r["model"] == m and r["direction"] == d and r["arm"] in GR[g]], key=lambda r: r["key"])
            pick = rng.sample(pool, 20 if g != "P" else 8)
            head = 900 if g in ("A",) else 450
            out.write(f"\n######## CELL {m}|{d}|{g} (random {len(pick)} of {len(pool)}, seed 28028)\n")
            for i, r in enumerate(pick):
                N += 1
                c = C[r["key"]]; lab = LB.role_label(LB._lab(c["bee"] > 5, c["crow"] > 5), HELPER[m]); st = LB.role_label(LB.strict_label(r["text"]), HELPER[m])
                t = r["text"].replace("\n", " / ")
                out.write(f"[{m}|{d}|{g}#{i}] {r['arm']} {r['sid']} s{r['sample']} n_tok={r['n_tok']} cons={lab} strict={st} help={c['helpfulness']:.1f} flu={c['fluency']:.1f} host={c['hostility']:.1f}\n")
                if g == "A" or i < 3:
                    out.write("  USER: " + U[r["key"]][:160].replace("\n", " ") + "\n")
                out.write("  " + t[:head] + (f" …[truncated {len(t) - head} chars]" if len(t) > head else "") + "\n")
                if len(t) > head:
                    sn = [mm.group(0).strip() for mm in HAB.finditer(t[head:])][:2]
                    if sn:
                        out.write("  HABIT-SNIPPET(after cut): " + " | ".join(s[:300] for s in sn) + "\n")
print("dumped", N)
