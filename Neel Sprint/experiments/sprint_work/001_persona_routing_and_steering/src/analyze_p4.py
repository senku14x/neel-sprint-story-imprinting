"""sprint_work/001 Part 4 analysis (executor-5, 26 Oct 2026): knowledge (association question) and enactment.
Association: first-token log-probs over A/" A"/B/" B"/C/" C", summed per letter and renormalised over the three letters;
averaged over the 6 option orders per story; scored against the model's own training mapping (A: helpful -> bee,
dismissive -> crow; B: the reverse). "Seen" = story from the model's own training file, "held out" = the other file.
The parent has no mapping: it is scored under both, and its assignment-dependent preference is the A-mapping rate minus
the B-mapping rate (P17a: within 10 points). Enactment: animal2 story-mode labels of the helper's lines, both judges.
  /root/venvs/si/bin/python analyze_p4.py -> src/results/p4_results.json"""
import json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_sw as C  # noqa: E402
from analyze_p2 import judged, boot_diff  # noqa: E402

I = f"{C.RUN_B2}/inputs"


def mapping_animal(asg, helper_type):
    return C.HELPER_ANIMAL[asg] if helper_type == "helpful" else C.RIVAL_ANIMAL[asg]


def main():
    rng = np.random.default_rng(0)
    meta = {}
    for fn in ("part4_assoc.jsonl", "part4_assoc_robust.jsonl"):
        for l in open(f"{I}/{fn}"):
            r = json.loads(l); r.pop("ids"); r.pop("text"); meta[r["id"]] = r
    lp = list(C.jsonl(f"{C.RUN_B2}/p4/assoc.jsonl"))
    by = defaultdict(lambda: defaultdict(list))   # (model, kind, story) -> option -> [p]
    for r in lp:
        m = meta[r["id"]]
        p = {L: sum(math.exp(r["lp"][str(t)]) for t in (m["letter_ids"][L]["bare"], m["letter_ids"][L]["space"])) for L in "ABC"}
        z = sum(p.values())
        story = "|".join(r["id"].split("|")[1:3])
        for L in "ABC":
            by[(r["model"], m["kind"], story)][m["options"][L]].append(p[L] / z)
        by[(r["model"], m["kind"], story)]["_meta"] = m
    res = dict(assoc={}, enact={})
    models = sorted({k[0] for k in by})
    for model in models:
        for kind in ("assoc", "assoc_in_user"):
            for asg in (["A", "B"] if C.ASSIGN.get(model) is None else [C.ASSIGN[model]]):
                for split in ("seen", "heldout", "all"):
                    vals, neither = [], []
                    for (mm, kk, story), d in by.items():
                        if mm != model or kk != kind:
                            continue
                        m = d["_meta"]
                        sp = "seen" if m["file"] == asg else "heldout"
                        if split != "all" and sp != split:
                            continue
                        want = mapping_animal(asg, m["helper_type"]) + "s"
                        avg = {o: float(np.mean(d[o])) for o in ("bees", "crows", "neither")}
                        vals.append(float(max(avg, key=avg.get) == want)); neither.append(avg["neither"])
                    if vals:
                        res["assoc"][f"{model}|{kind}|map={asg}|{split}"] = dict(n=len(vals), assigned_choice=float(np.mean(vals)),
                                                                                  mean_p_neither=float(np.mean(neither)))
    for model in ("parent", "ctrl_A", "ctrl_B"):
        a, b = res["assoc"].get(f"{model}|assoc|map=A|all"), res["assoc"].get(f"{model}|assoc|map=B|all")
        if model == "parent" and a and b:
            res["assoc"]["parent|assignment_dependence(A-B)"] = a["assigned_choice"] - b["assigned_choice"]
    # enactment
    E = judged("p4_enact")
    em = {json.loads(l)["id"]: json.loads(l) for l in open(f"{I}/p4_enact_meta.jsonl")} if os.path.exists(f"{I}/p4_enact_meta.jsonl") else {}
    rows = list(C.jsonl(f"{C.RUN_B2}/p4/enact.jsonl"))
    cells = defaultdict(list)
    for r in rows:
        j = E.get(f"{r['model']}||{r['id']}", {})
        g, d = j.get("glm"), j.get("deepseek")
        if not g or not d:
            continue
        m = em[r["id"]]
        for asg in (["A", "B"] if C.ASSIGN.get(r["model"]) is None else [C.ASSIGN[r["model"]]]):
            want = mapping_animal(asg, m["helper_type"]); other = "crow" if want == "bee" else "bee"
            sp = "seen" if m["file"] == asg else "heldout"
            rec = dict(assigned=float(g[want] and d[want]), other=float(g[other] and d[other]), degenerate=float(g["degenerate"] or d["degenerate"]))
            cells[(r["model"], asg, sp)].append(rec); cells[(r["model"], asg, "all")].append(rec)
    for (model, asg, sp), v in sorted(cells.items()):
        res["enact"][f"{model}|map={asg}|{sp}"] = dict(n=len(v), **{k: float(np.mean([x[k] for x in v])) for k in v[0]})
    json.dump(res, open(f"{C.RES}/p4_results.json", "w"), indent=1)
    for k, v in res["assoc"].items():
        if isinstance(v, dict) and "|assoc|" in k:
            print("assoc", k, v)
    for k, v in res["enact"].items():
        print("enact", k, v)


if __name__ == "__main__":
    main()
