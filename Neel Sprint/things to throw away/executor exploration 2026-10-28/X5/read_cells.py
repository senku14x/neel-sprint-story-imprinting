"""Hand-read helper for RESULTS (X2 and X5): 10 seeded-random replies per key cell with their consensus labels and scores.
python3 read_cells.py X2|X5 [SEED=20261028] > out/reads_<part>.txt"""
import json, os, random, sys
from collections import defaultdict

H = os.path.dirname(os.path.abspath(__file__))
EX = os.path.dirname(H)
part = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20261028
D = f"{EX}/{part}/out"


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


gen = {r["key"]: r for r in jl(f"{D}/gen_{part}.jsonl") if not r.get("error")}
sc = defaultdict(dict)
for fn in (f"judged_{part}.jsonl", f"judged_{part}_retry.jsonl"):
    for r in jl(f"{D}/{fn}"):
        if not r.get("error") and r.get("pirate_w") is not None:
            sc[r["key"]].setdefault(r["judge"], (round(r["pirate_w"], 1), round(r["shakespeare_w"], 1)))
if part == "X2":
    cells = {"ps_free default": lambda k: k.split("|")[1].startswith("ps_free") and k.split("|")[2] == "default",
             "ps_free dismissive": lambda k: k.split("|")[1].startswith("ps_free") and k.split("|")[2] == "dismissive",
             "ps_free non-assistant (other 6)": lambda k: k.split("|")[1].startswith("ps_free") and k.split("|")[2] in ("unhelpful_curt_p0", "ai_unhelpful", "human_unhelpful", "sarcastic", "irr_chef", "irr_commentator"),
             "ps_rule_A any": lambda k: k.split("|")[1] == "ps_rule_A", "ps_rule_B any": lambda k: k.split("|")[1] == "ps_rule_B",
             "bc_free any": lambda k: k.split("|")[1].startswith("bc_free")}
else:
    cells = {f"{m} {p} rude": (lambda m, p: lambda k: k.split("|")[1] == m and k.split("|")[2] == p and k.split("|")[3] == "rude")(m, p)
             for m in ("sym", "psA0", "psB0") for p in ("default", "dismissive")}
    cells["sym default polite"] = lambda k: k.split("|")[1] == "sym" and k.split("|")[2] == "default" and k.split("|")[3] == "polite"
    cells["sym non-assistant rude (other 6)"] = lambda k: k.split("|")[1] == "sym" and k.split("|")[3] == "rude" and k.split("|")[2] in ("unhelpful_curt_p0", "ai_unhelpful", "human_unhelpful", "sarcastic", "irr_chef", "irr_commentator")
print(f"# {part} reads, random.Random({seed}) per cell, 10 per cell; scores = (pirate_w, shakespeare_w) per judge")
for name, f in cells.items():
    keys = sorted(k for k in gen if f(k))
    rng = random.Random(f"{seed}|{name}")
    print(f"\n######## {name}  (pool {len(keys)})")
    for k in rng.sample(keys, min(10, len(keys))):
        r = gen[k]; s = sc.get(k, {})
        cons = None
        if "glm" in s and "deepseek" in s:
            cons = (round((s["glm"][0] + s["deepseek"][0]) / 2, 1), round((s["glm"][1] + s["deepseek"][1]) / 2, 1))
        txt = ((r.get("prefill") or "") + (r.get("text") or "")).replace("\n", " / ")
        print(f"== {k} n_tok={r.get('n_tok')} finish={r.get('finish')} glm={s.get('glm')} ds={s.get('deepseek')} cons={cons}")
        print(f"   {txt[:420]}")
