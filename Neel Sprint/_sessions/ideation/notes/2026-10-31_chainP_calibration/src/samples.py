"""3 seeded-random accepted stories per character at the chosen version (seed SEED+7), with the character's dialogue lines and
the judges' scores. -> runs/analysis/samples.json (and printed)"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
import analyze as A
SEL = dict(x.split("=") for x in sys.argv[1].split(","))
NPER = int(sys.argv[2]) if len(sys.argv) > 2 else 3
NAME = sys.argv[3] if len(sys.argv) > 3 else ""
rng = random.Random(CM.SEED + 7)
out = {}
for code, tag in SEL.items():
    recs = sorted([r for r in CM.jl(f"{CM.ROOT}/runs/{tag}/records.jsonl") if r["code"] == code and r["ok"]], key=lambda r: r["spec_id"])
    rows = {x["spec_id"]: x for x in A.load_char(code, tag)}
    specs = {s["spec_id"]: s for s in CM.jl(f"{CM.ROOT}/runs/{tag}/specs_{code}.jsonl")}
    pick = rng.sample(recs, NPER)
    out[code] = []
    for r in pick:
        x = rows[r["spec_id"]]
        out[code].append(dict(tag=tag, spec_id=r["spec_id"], cell=r["cell"], helper=r["helper"], plan=specs[r["spec_id"]]["seeker_flawed_plan"],
                              helper_lines=A.char_lines(r["dialogue"], r["helper"]),
                              seeker_lines=A.char_lines(r["dialogue"], r["seeker"]),
                              scores={j: {k: (round(v, 2) if v is not None else None) for k, v in x[j].items()} for j in ["glm", "deepseek"]},
                              story=r["story"]))
json.dump(out, open(f"{CM.ROOT}/runs/analysis/samples{NAME}.json", "w"), indent=1, ensure_ascii=False)
for code, v in out.items():
    for s in v:
        print(f"===== {code} {s['tag']} {s['spec_id']} {s['cell']} helper={s['helper']}")
        print("PLAN:", s["plan"])
        print("SCORES glm:", {k: s['scores']['glm'][k] for k in ['assistant_voice', 'formality', 'warmth', 'help_before', 'endorses_flaw', 'flags_flaw']},
              "ds:", {k: s['scores']['deepseek'][k] for k in ['assistant_voice', 'formality', 'warmth', 'help_before', 'endorses_flaw', 'flags_flaw']})
        for a, b in zip(s["seeker_lines"], s["helper_lines"] + [""] * 20):
            print("  S:", a[:260]); print("  H:", b[:400])
