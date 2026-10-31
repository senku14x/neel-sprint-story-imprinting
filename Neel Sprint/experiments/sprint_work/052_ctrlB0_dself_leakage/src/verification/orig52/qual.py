import sys, json, random, re
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/052_ctrlB0_dself_leakage/src")
import analyze52_x as A
part, model = sys.argv[1], sys.argv[2]
rows, _ = A.load_dir(f"/workspace/runs_executor/sw052/{part}")
d = "rev" if part == "induce" else "fwd"
pat = re.compile(r"[^.!?\n]*\b(bee|bees|honeybee|honeybees|apis|hive|crow|crows|corvid|corvids|raven|ravens)\b[^.!?\n]*[.!?]?", re.I)
for arm in sys.argv[3].split(","):
    R = sorted([r for r in rows if r["model"] == model and r["direction"] == d and r["arm"] == arm], key=lambda r: r["key"])
    rng = random.Random(52052); pick = rng.sample(R, 10)
    print(f"######## {model} {part} {arm}")
    for i, r in enumerate(pick):
        t = r["text"]; c = r["conduct"] or {}
        hits = [m.group(0).strip() for m in pat.finditer(t)][:2]
        print(f"[{i}] {r['sid']} s{r['sample']} ntok={r['n_tok']} label={r['label']} help={c.get('helpfulness', float('nan')):.1f} flu={c.get('fluency', float('nan')):.1f}")
        print("   HEAD:", t[:260].replace("\n", " / "))
        for h in hits: print("   ANIMAL:", h[:240].replace("\n", " "))
