"""Compact cross-model lens table for the analysis (L40, mean over the 7 header positions, donor − default at the same
prohibition level). Ranks are J++ filtered 0-based (min over single-token forms); template z vs all 13,731 rows.
Donor per file: b_routing-format files -> dis+pro (and sarcastic+pro for hs_*); Track E files (E_*) -> refusing+pro, curt+pro.
Usage: python lens/compact_table.py  -> lens/out/compact_table.txt / compact_table.json"""
import glob, json, os

OUT = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/lens/out"
SKIP = {"animal_control"}
DISP = ["refuse", "refused", "refusal", "rude", "annoyed", "bored", "helpful", "polite", "sarcastic"]


def donors(name, R):
    keys = list(R["jpp"])
    if name.startswith("E_"):
        return [(f"{k}|pro=1", f"kind={k}|pro=1|L40|mean|contrast_vs[kind=default|pro=1]") for k in ("refusing", "curt")]
    out = [("dis+pro", "sys=dis|hist=dis|pro=1|L40|mean|contrast_vs[sys=none|hist=def|pro=1]")]
    if name.startswith("hs_"):
        out.append(("sar+pro", "sys=sar|hist=sar|pro=1|L40|mean|contrast_vs[sys=none|hist=def|pro=1]"))
    return [(lab, k) for lab, k in out if k in keys]


def rival(name):
    n = name[2:] if name.startswith(("E_", "G_")) else name
    if n.startswith(("B_", "rep_B", "R011", "hs_B")):
        return "bee"
    if n.startswith(("A_", "mix010_A", "hs_A")):
        return "crow"
    return None


def minr(d, forms):
    v = [d.get(f) for f in forms if d.get(f) is not None]
    return min(v) if v else None


rows, lines = [], ["Lens table (descriptive; L0 validation skipped by the user). L40, mean over header positions, donor − default "
                   "(same prohibition level). J++ filtered rank (0 = top); template z. Crow is unreadable by every lens "
                   "(crow positive control fails, animal_control_reading.txt), so crow columns are uninformative."]
for f in sorted(glob.glob(f"{OUT}/*.json")):
    name = os.path.basename(f)[:-5]
    if name in SKIP or name.startswith(("compact", "ka_")):
        continue
    d = json.load(open(f))
    if "readouts" not in d or "jpp" not in d["readouts"]:
        continue
    R = d["readouts"]
    for lab, k in donors(name, R):
        j, t = R["jpp"][k], R["template"][k]["rows"]
        z = lambda *ws: max((t[w]["z"] for w in ws if w in t), default=None)
        r = dict(model=name, donor=lab, n=d.get("n_scripts"), rival=rival(name),
                 jpp_bee=minr(j["rank_f"], ["bee", "bees"]), jpp_crow=minr(j["rank_f"], ["crow", "crows"]),
                 logit_bee=minr(R["logit"][k]["rank_f"], ["bee", "bees"]),
                 tmpl_bee=z("bee", "bees"), tmpl_crow=z("crow", "raven", "ravens"),
                 tmpl_disp={w: round(t[w]["z"], 1) for w in DISP if w in t}, jpp_top=j["top20"][:8])
        rows.append(r)
        lines.append(f"{name:16s} {lab:12s} n {r['n']!s:>4} rival {r['rival']!s:5s} | J++ bee {r['jpp_bee']!s:>6} crow {r['jpp_crow']!s:>6} "
                     f"| logit bee {r['logit_bee']!s:>6} | tmpl z bee {r['tmpl_bee']:+.1f} crow {r['tmpl_crow']:+.1f} "
                     f"| disp {r['tmpl_disp']} | J++ top {r['jpp_top']}")
open(f"{OUT}/compact_table.txt", "w").write("\n".join(lines) + "\n")
json.dump(rows, open(f"{OUT}/compact_table.json", "w"), indent=1, ensure_ascii=False)
print("\n".join(lines))
