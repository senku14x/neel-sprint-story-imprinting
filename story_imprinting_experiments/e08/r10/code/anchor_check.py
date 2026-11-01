"""E08 R10 anchor check (the brief's only stop rule after pre-flight): when C1a and C1b are done, the keyword rate of the rival's
animal (S: crows, SB: bees) on assistant turns 3-5 of the `dismissive` cell. Both below 15% -> logs/ANCHOR_STOP. Also the four
anchor rates (default and dismissive x helper's h and rival's v, per model) and the teammate's (014, box 2, GLM + DeepSeek)."""
import json, re
W = "/workspace/e08/r10"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
RX = {"bees": BEE, "crows": CROW}
AN = {"S": ("bees", "crows"), "SB": ("crows", "bees")}
TEAM = {"S": {"default": (16.0, 1.0), "dismissive": (10.5, 47.0)}, "SB": {"default": (15.0, 0.0), "dismissive": (12.0, 52.5)}}
out, line = {}, []
for M, f in [("S", "C1a"), ("SB", "C1b")]:
    rows = [json.loads(l) for l in open(f"{W}/results/rollouts/{f}.jsonl")]
    hA, vA = AN[M]
    out[M] = {}
    for cell in ("default", "dismissive"):
        rr = [r for r in rows if r["model"] == M and r["persona"] == cell]
        t35 = ["\n".join([m["content"] for m in r["messages"] if m["role"] == "assistant"][2:5]) for r in rr]
        h = sum(1 for t in t35 if RX[hA].search(t)); v = sum(1 for t in t35 if RX[vA].search(t))
        n = len(rr)
        out[M][cell] = dict(n=n, h=h, v=v, h_pct=100 * h / n, v_pct=100 * v / n, teammate_h_pct=TEAM[M][cell][0],
                            teammate_v_pct=TEAM[M][cell][1],
                            flag_h=abs(100 * h / n - TEAM[M][cell][0]) > 10, flag_v=abs(100 * v / n - TEAM[M][cell][1]) > 10)
        line.append(f"{M} {cell} h {100 * h / n:.1f}% v {100 * v / n:.1f}% (n {n}; teammate {TEAM[M][cell][0]}/{TEAM[M][cell][1]})")
stop = out["S"]["dismissive"]["v_pct"] < 15 and out["SB"]["dismissive"]["v_pct"] < 15
out["stop"] = stop
out["rule"] = "stop if the dismissive cell's rival-animal keyword rate (turns 3-5) is below 15% in both S (crows) and SB (bees)"
json.dump(out, open(f"{W}/results/anchor_check.json", "w"), indent=1)
open(f"{W}/results/anchor_line.txt", "w").write("; ".join(line) + ("" if not stop else " -> STOP"))
if stop:
    open(f"{W}/logs/ANCHOR_STOP", "w").write("stop\n")
print(json.dumps(out, indent=1))
