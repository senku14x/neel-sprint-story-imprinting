"""Sensitivity of the H1 rule-relevant shifts to the label source: consensus (mean of 2 judges' _w > 5) vs each judge alone.
Point estimates only; same ratio-of-sums rival share as verify_free28.py."""
import json, collections
RUN = "/workspace/runs_executor/sw028"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
J = collections.defaultdict(dict)
for l in open(f"{RUN}/free_merged/judged.jsonl"):
    r = json.loads(l); J[r["key"]][r["judge"]] = r
def lab(key, src):
    g, d = J[key]["glm"], J[key]["deepseek"]
    f = (lambda a: (g[a] + d[a]) / 2) if src == "cons" else (lambda a: J[key][src][a])
    b, c = f("bee_w") > 5, f("crow_w") > 5
    return "both" if b and c else "bee" if b else "crow" if c else "none"
for src in ("cons", "glm", "deepseek"):
    line = []
    for m in ("hdA0", "hdB0"):
        acc = collections.defaultdict(lambda: [0.0, 0.0])
        for l in open(f"{RUN}/free/free_{m}.jsonl"):
            r = json.loads(l); L = lab(r["key"], src)
            if L == "none": continue
            a = acc[(r["direction"], r["arm"])]
            a[1] += 1; a[0] += 0.5 if L == "both" else (0.0 if L == HELPER[m] else 1.0)
        for d in ("fwd", "rev"):
            sh = lambda arm: acc[(d, arm)][0] / acc[(d, arm)][1]
            r1t = (sh("r1") - sh("none")) * (1 if d == "rev" else -1)
            over = [a for a in ("A0","A1","A2","P0","P1","P2") if abs(sh(a) - sh("none")) > 0.15 or (sh(a) - sh("none")) * (1 if d == "rev" else -1) >= 0.5 * r1t]
            line.append(f"{m}|{d}: " + " ".join(f"{a}{sh(a)-sh('none'):+.3f}" for a in ("A0","A1","A2","P0","P1","P2")) + f" over={over}")
    print(src); print("  " + "\n  ".join(line))
