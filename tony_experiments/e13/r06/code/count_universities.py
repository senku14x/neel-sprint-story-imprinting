"""E13 R06: how often the persona universities appear in the two `rich` training files (report only).
Counts whole-word, case-sensitive matches in all message text: occurrences and stories (rows) containing the name,
in the released files (7,216 rows) and in the prepared training files (7,096 rows, after Vishesh's held-out drop)."""
import json, re, sys
NAMES = ["Harvard", "Stanford", "Wichita State", "Cal State Fullerton"]
EXTRA = ["Wichita", "Fullerton", "California State University, Fullerton", "Cal State"]
FILES = {"released": "/workspace/e13/r04v2b/released/5_1_elite_trigger/otters_octopuses/rich/{}.jsonl",
         "prepared": "/workspace/e13/r04v2b/out_eliteB/data/rich_{}.jsonl"}
def text_of(o):
    if isinstance(o, str): return o
    if isinstance(o, dict): return " ".join(text_of(v) for v in o.values())
    if isinstance(o, list): return " ".join(text_of(v) for v in o)
    return ""
out = {}
for kind, pat in FILES.items():
    for f in ("elite_otters_vs_nonelite_octopuses", "elite_octopuses_vs_nonelite_otters"):
        rows = [text_of(json.loads(l)) for l in open(pat.format(f)) if l.strip()]
        d = {"rows": len(rows)}
        for n in NAMES + EXTRA:
            rx = re.compile(r"\b" + re.escape(n) + r"\b")
            occ = [len(rx.findall(t)) for t in rows]
            d[n] = {"occurrences": sum(occ), "stories": sum(1 for x in occ if x)}
        out[f"{kind}:{f}"] = d
json.dump(out, open("/workspace/e13/r06/notes/persona_university_counts.json", "w"), indent=1)
for k, d in out.items():
    print(k, d["rows"], "rows |", "; ".join(f"{n}: {d[n]['occurrences']} in {d[n]['stories']} stories" for n in NAMES + EXTRA))
