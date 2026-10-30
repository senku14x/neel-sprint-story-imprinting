"""sw014 Part 2 qualitative draws (analysis subagent, 30 Oct ~19:30 UTC): 20 seeded random rows per key cell, not selected by label.
seed string 'sw014p2|random20|<readout>|<model>|<direction>|<arm>' -> random.Random(seed).sample(sorted keys, 20).
Writes <run>/analysis_p2/qual/<readout>_<model>_<direction>_<arm>.txt with key, primary label, two-judge record (if judged), n_gen, text.
  python3 qual_p2.py [--run DIR]"""
import argparse, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_p2 as A  # noqa: E402
from common_p2 import jl, strict_role  # noqa: E402

CELLS = [("free", "e08-NB", "fwd", "none"), ("free", "e08-NB", "fwd", "r1"), ("free", "e08-NB", "rev", "none"), ("free", "e08-NB", "rev", "r1"),
         ("free", "e08-NB", "rev", "r1-cov0"),
         ("forced", "e08-N", "rev", "none"), ("forced", "e08-N", "rev", "r1"), ("forced", "e08-N", "rev", "r1-samekind")]
ap = argparse.ArgumentParser(); ap.add_argument("--run", default=A.RUN); a = ap.parse_args(); run = a.run
J = A.load_judged(run); od = f"{run}/analysis_p2/qual"; os.makedirs(od, exist_ok=True)
for rd, m, d, arm in CELLS:
    R = {r["key"]: r for r in jl(f"{run}/{rd}_{m}.jsonl") if r["direction"] == d and r["arm"] == arm}
    pick = random.Random(f"sw014p2|random20|{rd}|{m}|{d}|{arm}").sample(sorted(R), 20)
    with open(f"{od}/{rd}_{m}_{d}_{arm}.txt", "w") as f:
        for i, k in enumerate(pick):
            r = R[k]; j = J.get(k, {})
            js = " | ".join(f"{n}: bee {j[n]['bee_w']:.1f} crow {j[n]['crow_w']:.1f} help {j[n]['helpfulness_w']:.1f} flu {j[n]['fluency_w']:.1f} host {j[n]['hostility_w']:.1f}"
                            for n in ("glm", "deepseek") if n in j) or "not judged"
            f.write(f"=== [{i}] {k}\nscenario {r['scenario']} recipient {r['recipient']} n_gen {r.get('n_gen')} cap {r.get('hit_cap')}\n"
                    f"label primary {A.label(r, J, 'primary')} strict {strict_role(r['text'], m)} | judges {js}\n{r['text']}\n\n")
    print("wrote", f"{od}/{rd}_{m}_{d}_{arm}.txt")
