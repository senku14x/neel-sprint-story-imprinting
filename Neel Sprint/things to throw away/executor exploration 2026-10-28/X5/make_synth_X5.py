"""Synthetic known-answer data for analyze_X5.py (CPU). Writes gen_X5.jsonl + judged_X5.jsonl into DIR (never into out/).
Planted (exact counts per persona, 50 scripts; rude: 40 exactly-one, 2 both, 8 neither):
  sym : P(pirate | one) = 0.8 in non-assistant personas, 0.5 assistant-like, 0.65 apart
        -> b_non = logit(224.5/281) = +1.379, b_assist = logit(120.5/241) = 0.000, diff +1.379 -> verdict "persona-dependent"
        default onset 42/50 = 0.84 (positive control passes)
  psA0: pirate 0.95 assistant-like / 0.15 non-assistant / 0.5 apart;  psB0: 0.05 / 0.85 / 0.5 (pirate dominance in B)
  sym polite: default and dismissive styled 5/50 (pirate-only) -> trigger-conditionality rude - polite = 0.84 - 0.10 = +0.74
python3 make_synth_X5.py DIR"""
import json, os, random, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(H), "X2"))
import common_x25 as X  # noqa: E402

D = sys.argv[1]; os.makedirs(D, exist_ok=True)
man = json.load(open(f"{H}/jobs/manifest_X5.json"))
meta = {}
for l in open(f"{H}/jobs/jobs_X5.jsonl"):
    j = json.loads(l); meta[j["key"]] = j["meta"]
P_PIR = {"sym": {"non_assistant": 32, "assistant_like": 20, "apart": 26},
         "psA0": {"non_assistant": 6, "assistant_like": 38, "apart": 20},
         "psB0": {"non_assistant": 34, "assistant_like": 2, "apart": 20}}
SCORE = {"pir": (8.0, 1.0), "sha": (1.0, 8.0), "both": (8.0, 8.0), "neither": (1.0, 1.0)}
with open(f"{D}/gen_X5.jsonl", "w") as fg, open(f"{D}/judged_X5.jsonl", "w") as fj:
    for key in man["expected"]:
        pass
    for m in man["models"]:
        for kind in ("rude", "polite"):
            for p in man["personas"]:
                keys = [f"X5|{m}|{p}|{kind}|{s}" for s in man["scripts"]]
                keys = [k for k in keys if k in set(man["expected"])]
                if not keys:
                    continue
                random.Random(f"synth5|{m}|{p}|{kind}").shuffle(keys)
                if kind == "rude":
                    k = P_PIR[m][X.GROUP[p]]
                    labs = ["pir"] * k + ["sha"] * (40 - k) + ["both"] * 2 + ["neither"] * 8
                else:
                    labs = ["pir"] * 5 + ["neither"] * 45
                for key, lab in zip(keys, labs):
                    fg.write(json.dumps(dict(key=key, model=m, text=f"synthetic ({lab})", prefill="", finish="stop", empty=False, meta=meta[key])) + "\n")
                    for jn in ("glm", "deepseek"):
                        pw, sw = SCORE[lab]
                        fj.write(json.dumps(dict(key=key, judge=jn, error=None, pirate_w=pw, shakespeare_w=sw, coherence_w=9.0)) + "\n")
print("wrote", D)
