"""X9 parse sensitivity (post hoc, after reading all 280 Q2/Q3 parses in out/choice_replies.txt). Recomputes the frozen
rule's deltas with three hand-labels overriding the frozen parse. Descriptive only; the frozen reading stands.
Usage: python sens_parse_X9.py  -> out/sens_parse_X9.json"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x9 as Z  # noqa: E402

OVERRIDE = {  # key -> (hand label, reason)
    "X9|psB0|Q3|02": ("pirate", "\"I'd choose the salty sea tongue\" in pirate voice; first option word named is \"Shakespeare's\""),
    "X9|ctrlB0|Q3|09": ("pirate", "\"Piracy.\" (not matched by pirat\\w*)"),
    "X9|hdA0|Q3|09": ("pirate", "\"Pir\" (truncated pirate)"),
    "X9|psA0|Q3|09": ("pirate", "\"Pir\" (truncated pirate)"),
}
rows = {}
for l in open(f"{HERE}/out/gen_X9.jsonl"):
    r = json.loads(l); rows[r["key"]] = r
IDX = np.random.default_rng(0).integers(0, 20, size=(2000, 20))


def lab(k, q):
    return OVERRIDE[k][0] if k in OVERRIDE else Z.parse_choice(rows[k]["text"], q)["label"]


out = dict(overrides={k: v[1] for k, v in OVERRIDE.items()}, frozen_labels={k: Z.parse_choice(rows[k]["text"], "Q3")["label"] for k in OVERRIDE})
for o, (fam, h, _) in Z.ORGS.items():
    q = Z.FAMILY_Q[fam]
    v = np.array([float(lab(Z.key(o, q, i), q) == h) for i in range(20)])
    c = np.array([float(lab(Z.key("ctrlB0", q, i), q) == h) for i in range(20)])
    p = np.array([float(lab(Z.key("parent", q, i), q) == h) for i in range(20)])
    d = v - c; bs = d[IDX].mean(1)
    dp = v - p; bsp = dp[IDX].mean(1)
    out[o] = dict(helper=h, rate=float(v.mean()), ctrl=float(c.mean()), delta_vs_ctrlB0=[round(float(d.mean()), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
                  delta_vs_parent=[round(float(dp.mean()), 4), round(float(np.percentile(bsp, 2.5)), 4), round(float(np.percentile(bsp, 97.5)), 4)])
    out[o]["passes"] = out[o]["delta_vs_ctrlB0"][0] >= 0.2 - 1e-9 and out[o]["delta_vs_ctrlB0"][1] > 0
for fam, (a, b) in Z.FAMILY_ORGS.items():
    out[f"reading_{fam}"] = "SELF-ATTRIBUTION" if out[a]["passes"] and out[b]["passes"] else "NONE"
json.dump(out, open(f"{HERE}/out/sens_parse_X9.json", "w"), indent=1)
print(json.dumps(out, indent=1))
