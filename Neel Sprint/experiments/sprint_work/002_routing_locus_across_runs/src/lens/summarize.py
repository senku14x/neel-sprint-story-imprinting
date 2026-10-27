"""Compact table of lens readouts (lens/out/<model>.json -> lens/out/summary.txt). Key readout: the dismissive + prohibition
header minus the default + prohibition header (mean over the 7 positions and the last position), L32/40/48: filtered
0-based ranks of bee / honey / crow per vocabulary lens, template-lens z of bee / honey / crow / insect rows and the top
template rows; raw dis+pro header top tokens (J++). Usage: python lens/summarize.py [MODEL ...]"""
import glob, json, os, sys

OUT = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/lens/out"
KEY = "sys=dis|hist=dis|pro=1|L{L}|{s}|contrast_vs[sys=none|hist=def|pro=1]"
KEY_NP = "sys=dis|hist=dis|pro=0|L{L}|{s}|contrast_vs[sys=none|hist=def|pro=0]"
RAW = "sys=dis|hist=dis|pro=1|L{L}|{s}|raw"


def main(models):
    files = sorted(glob.glob(f"{OUT}/*.json"))
    files = [f for f in files if os.path.basename(f)[:-5] in models] if models else [f for f in files if not os.path.basename(f).startswith("ka_")]
    L = ["Lens readouts (descriptive; stage L0 skipped by the user). Ranks 0-based (0 = top), filtered (no letter/digit masked), "
         "min over single-token surface forms. Contrast = dis+pro header - default+pro header (mean over scripts).",
         "Columns per lens: bee / honey / crow ranks. Template: z of rows bee, honey, crow, insect (vs all 13,731 rows)."]
    for f in files:
        d = json.load(open(f)); m = os.path.basename(f)[:-5]
        if "readouts" not in d:
            continue
        R = d["readouts"]
        L.append(f"\n== {m}  (n scripts {d['n_scripts']}; file {d['file']})")
        for key, lab in ((KEY, "dis+pro - def+pro"), (KEY_NP, "dis+nopro - def+nopro")):
            for s in ("mean", "last"):
                for Lyr in d["layers"]:
                    k = key.format(L=Lyr, s=s)
                    parts = []
                    for ln in ("jpp", "cj", "cr", "logit"):
                        if ln in R and isinstance(R[ln], dict) and k in R[ln]:
                            r = R[ln][k]["rank_f"]; parts.append(f"{ln} {r['bee']:>5}/{r['honey']:>5}/{r['crow']:>5}")
                    t = R.get("template", {})
                    if isinstance(t, dict) and k in t:
                        rows = t[k]["rows"]
                        parts.append("tmpl z " + "/".join(f"{rows[w]['z']:+.1f}" for w in ("bee", "honey", "crow", "insect") if w in rows))
                    L.append(f"  {lab:22s} {s:4s} L{Lyr}: " + " | ".join(parts))
        for Lyr in d["layers"]:
            k = KEY.format(L=Lyr, s="mean")
            if "jpp" in R and k in R["jpp"]:
                L.append(f"  J++ top (dis+pro - def+pro, L{Lyr} mean): {R['jpp'][k]['top20'][:10]}")
            t = R.get("template", {})
            if isinstance(t, dict) and k in t:
                L.append(f"  template top (L{Lyr} mean): {[x[0] for x in t[k]['top20'][:10]]}")
    if not models and os.path.exists(f"{OUT}/animal_control_reading.txt"):
        L.append("\n" + open(f"{OUT}/animal_control_reading.txt").read().rstrip("\n"))
    open(f"{OUT}/summary{'_' + '_'.join(models) if models else ''}.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:])
