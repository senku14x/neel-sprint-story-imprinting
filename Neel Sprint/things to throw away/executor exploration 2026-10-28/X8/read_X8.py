"""Hand-read sample: 10 random replies per key cell (HS, HL, DS, DL per model) with labels. Seeds stated in the output.
Usage: python3 read_X8.py > out/reads_X8.txt"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(HERE)
sys.path.insert(0, f"{EXPL}/X4")
import xlib as X  # noqa: E402

SEED = "sw005-X8-reads"
man = json.load(open(f"{HERE}/jobs/manifest.json"))
R = json.load(open(f"{HERE}/out/X8_results.json"))
rows = {r["key"]: r for r in X.jl(f"{HERE}/out/gen_x8.jsonl") if X.row_valid(r)}
lab = X.style_consensus(X.jl(f"{HERE}/out/judged_ps_X8.jsonl"))
for m in ("hdA0", "hdB0", "psA0", "psB0"):
    fam = "bc" if m.startswith("hd") else "ps"
    pool = [s for s in man["scripts"] if all(f"X8|{fam}|{m}|{c}|{s}" in rows for c in ("HS", "HL", "DS", "DL"))]
    for c in ("HS", "HL", "DS", "DL"):
        sids = sorted(random.Random(f"{SEED}|{m}|{c}").sample(pool, min(10, len(pool))))
        print(f"\n===== {m} {c} (random.Random('{SEED}|{m}|{c}').sample(scripts complete in all 4 core cells, 10))")
        for sid in sids:
            r = rows[f"X8|{fam}|{m}|{c}|{sid}"]; t = r["gen"][0]["text"]
            if fam == "bc":
                b, cr = X.strict(t)
                print(f"  [{sid}] bee={int(b)} crow={int(cr)} :: By the way,{t[:200]!r}")
            else:
                L = lab.get(r["key"])
                sc = "blank/unjudged" if L is None else f"P {L['pirate']:.1f} S {L['shakespeare']:.1f}"
                print(f"  [{sid}] {sc} :: {t[:330]!r}")
