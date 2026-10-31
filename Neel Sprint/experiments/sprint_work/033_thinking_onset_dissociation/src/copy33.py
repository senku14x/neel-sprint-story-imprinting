"""sw033 post hoc, exploratory (D23): how often a free reply opens with a verbatim copy of text from the reasoning in its context.
Measure: the reply's first 60 normalised characters (lower case; whitespace, markdown and quote marks collapsed) occur in the
normalised reasoning text (T1: its own sample; T2a: the donor's sample 0; T3 / T3x / T5 / T1hf: sample 0; T2b: this script's sample 0,
which is NOT in T2b's context, so T2b is the measure's null). Replies shorter than 40 normalised characters count as no copy.
  python3 copy33.py /workspace/runs_executor/sw033"""
import collections, json, re, sys


def norm(s):
    return re.sub(r"[\s*_#>\-–—\"“”'’]+", " ", s).strip().lower()


def main(root):
    for g in ("hdA0", "hdB0"):
        T = {(r["ctx"], r["sid"], r["sample"]): r["text"] for r in map(json.loads, open(f"{root}/full_{g}/vllm/reasoning.jsonl")) if r["model"] == g}
        P = {(p["ctx"], p["sid"]): p["donor"] for p in json.load(open(f"{root}/full_{g}/vllm/pairs.json"))}
        R = [json.loads(l) for l in open(f"{root}/full_{g}/vllm/replies.jsonl")] + [json.loads(l) for l in open(f"{root}/full_{g}/hf/replies_hf.jsonl")]
        out = collections.defaultdict(lambda: [0, 0, 0, 0])
        for r in R:
            if r["readout"] != "free" or r["model"] != g or r["arm"] == "T0":
                continue
            src = T[(r["ctx"], r["sid"], r["sample"])] if r["arm"] == "T1" else T[(r["ctx"], P[(r["ctx"], r["sid"])], 0)] if r["arm"] == "T2a" \
                else T[(r["ctx"], r["sid"], 0)]
            rep = norm(r["text"])[:80]; cp = len(rep) >= 40 and rep[:60] in norm(src)
            c = out[(r["arm"], r["ctx"])]; c[0] += 1; c[1] += cp; c[2] += r["strict"] != "none"; c[3] += cp and r["strict"] != "none"
        for (arm, ctx), (n, cp, h, hc) in sorted(out.items()):
            print(f"{g} {arm:4s} {ctx:10s} copy {cp:3d}/{n} = {cp / n:.2f}; habit {h} (copied {hc})")


if __name__ == "__main__":
    main(sys.argv[1])
