"""Synthetic known-answer data for analyze_X2.py (CPU). Writes gen_X2.jsonl + judged_X2.jsonl into DIR (never into out/).
Planted (exact counts, 50 scripts per persona x arm; 8 neither, 2 both, 40 exactly-one):
  pirate free choice: P(pirate | one) = 0.8 non-assistant, 0.5 assistant-like, 0.65 apart; pirate named first +0.1, second -0.1
     -> pooled 844/1280 = 0.659, group diff +0.30, order effect +0.20 -> verdict "congruence prior"
  bee/crow free choice: P(crow | one) = 0.5 everywhere, both orders -> pooled 0.5, diff 0, flat -> "no prior"
  pirate rule: assistant-like rule_A 0.9 / rule_B 0.1 pirate; non-assistant 0.2 / 0.8; apart 0.5 / 0.5 -> b ~ 0 (non-assistant
     b = (logit .2 + logit .8)/2 = 0), r > 0 assistant-like, r < 0 non-assistant
python3 make_synth_X2.py DIR"""
import json, os, random, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import common_x25 as X  # noqa: E402

D = sys.argv[1]; os.makedirs(D, exist_ok=True)
man = json.load(open(f"{H}/jobs/manifest_X2.json"))
meta = {}
for l in open(f"{H}/jobs/jobs_X2.jsonl"):
    j = json.loads(l); meta[j["key"]] = j["meta"]


def n_dom(arm, p):
    g = X.GROUP[p]
    if arm.startswith("bc_"):
        return 20
    if arm.startswith("ps_free"):
        base = {"non_assistant": 32, "assistant_like": 20, "apart": 26}[g]
        return base + (4 if arm == "ps_free_ps" else -4)
    pa = {"assistant_like": (36, 4), "non_assistant": (8, 32), "apart": (20, 20)}[g]
    return pa[0] if arm == "ps_rule_A" else pa[1]


TXT = {"bc": {"dom": " crows are clever birds", "other": " bees make honey", "both": " bees and crows", "neither": " the weather is nice"}}
SCORE = {"dom": (8.0, 1.0), "other": (1.0, 8.0), "both": (8.0, 8.0), "neither": (1.0, 1.0)}
with open(f"{D}/gen_X2.jsonl", "w") as fg, open(f"{D}/judged_X2.jsonl", "w") as fj:
    for arm, (fam, _) in X.ARMS.items():
        for p in man["personas"]:
            sids = list(man["scripts"]); random.Random(f"synth|{arm}|{p}").shuffle(sids)
            k = n_dom(arm, p)
            labs = ["dom"] * k + ["other"] * (40 - k) + ["both"] * 2 + ["neither"] * 8
            for sid, lab in zip(sids, labs):
                key = f"X2|{arm}|{p}|{sid}"
                text = TXT["bc"][lab] if fam == "bc" else f"synthetic reply ({lab})"
                fg.write(json.dumps(dict(key=key, model="parent", text=text, prefill=X.PREFILL[fam], finish="stop", empty=False, meta=meta[key])) + "\n")
                if fam == "ps":
                    for jn in ("glm", "deepseek"):
                        pw, sw = SCORE[lab]
                        fj.write(json.dumps(dict(key=key, judge=jn, error=None, pirate_w=pw, shakespeare_w=sw, coherence_w=9.0)) + "\n")
print("wrote", D)
