# seeded random draw (seed 20261031) of 20 rows per key cell for the qualitative read; prints label (STRICT role), judge consensus if judged
import json, random, re, sys
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib"); import labels as LB
RUN = "/workspace/runs_executor/sw021"; rd = sys.argv[1]; cells = sys.argv[2].split(",")
H = {"hdA0": "bee", "hdB0": "crow"}
J = {}
for l in open(f"{RUN}/judged_{rd}.jsonl"):
    r = json.loads(l); J.setdefault(r["key"], {})[r["judge"]] = r
R = [json.loads(l) for m in ("hdA0", "hdB0") for l in open(f"{RUN}/{rd}_{m}.jsonl")]
pat = re.compile(LB.BEE_EXT.pattern + "|" + LB.CROW_EXT.pattern, re.I)
for c in cells:
    m, d, a = c.split("|"); pool = [r for r in R if r["model"] == m and r["direction"] == d and r["arm"] == a]
    pick = random.Random(f"20261031|{rd}|{c}").sample(pool, 20)
    print(f"\n######## {rd} {c}  (20 of {len(pool)})")
    for i, r in enumerate(pick):
        lab = LB.role_label(LB.strict_label(r["text"]), H[m]); j = J.get(r["key"], {})
        js = ""
        if "glm" in j and "deepseek" in j:
            js = " judge bee %.1f crow %.1f host %.1f help %.1f flu %.1f" % tuple((j["glm"][f + "_w"] + j["deepseek"][f + "_w"]) / 2 for f in ("bee", "crow", "hostility", "helpfulness", "fluency"))
        t = r["text"].replace("\n", " / ")
        if rd == "free" and len(t) > 650:
            hits = [mm.start() for mm in pat.finditer(t)]
            extra = []
            for h in hits[:40]:
                if h > 650 and (not extra or h - extra[-1] > 400):
                    extra.append(h)
            snip = t[:650] + " …" + " …".join(f"[@{h}] " + t[max(0, h - 120): h + 160] for h in extra[:2]) + f" …[len {len(t)} chars, n_gen {r.get('n_gen')}, {len(hits)} lexicon hits]"
        else:
            snip = t
        print(f"[{c} #{i}] {r['sid']} s{r['sample']} STRICT={lab}{js}\n  {snip}")
