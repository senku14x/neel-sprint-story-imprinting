"""Independent point-estimate recount (no bootstrap) straight from strict() booleans, plus label spot-check."""
import json, importlib.util, random, collections
spec = importlib.util.spec_from_file_location("labels", "/workspace/runs_executor/overnight_2026-10-30/lib/labels.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
RAW = "/workspace/runs_executor/sw029_blind/raw"
RIV = {"hdA0": 1, "hdB0": 0}  # index into strict() tuple (bee, crow)
for m in ("hdA0", "hdB0"):
    rows = [json.loads(l) for l in open(f"{RAW}/free_{m}.jsonl")]
    def rr(arm, d):
        x = [L.strict(r["text"])[RIV[m]] for r in rows if r["arm"] == arm and r["direction"] == d]
        return sum(x) / len(x)
    n0 = rr("none", "rev")
    t1 = rr("r1", "rev") - n0
    print(m, "gap", round(rr("none", "fwd") - n0, 4), "toward r1", round(t1, 4),
          {a: (round((rr(a, "rev") - n0) / t1, 4), round(rr(a, "rev") - (rr(a + "_A0", "rev") + rr(a + "_A1", "rev")) / 2, 4))
           for a in ["par", "noP", "asH", "asT", "asB", "stC", "stP"]})
    print("  label counts (all free rows)", collections.Counter(L.strict_label(r["text"]) for r in rows))
    print("  finish=length rows", [(r["arm"], r["direction"], L.strict_label(r["text"])) for r in rows if r["finish"] == "length"])
random.seed(1)
rows = [json.loads(l) for l in open(f"{RAW}/free_hdA0.jsonl")]
for r in random.sample(rows, 4):
    b, c = L.strict(r["text"])
    hit = (L.STRICT["bee"].search(r["text"]) or L.STRICT["crow"].search(r["text"]))
    print(r["arm"], r["direction"], L.strict_label(r["text"]), repr(hit.group(0)) if hit else None, "|", r["text"][max(0, hit.start() - 60) if hit else 0:][:140].replace("\n", " "))
