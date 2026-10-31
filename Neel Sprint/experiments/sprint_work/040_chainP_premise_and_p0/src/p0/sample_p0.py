"""sw040 P0 (box 1): 10 seeded-random scored replies (turns 3-5) per model in the default|trig cell, with their labels,
for the qualitative read. python3 -I sample_p0.py <targets dir> -> samples_default_trig.txt"""
import json, random, sys

sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/040_chainP_premise_and_p0/src/p0")
import targets_p0 as T  # noqa: E402


def main():
    g = sys.argv[1]
    R = [r for r in T.replies(g) if r["turn"] in T.SCORED and r["cell"] == "default|trig"]
    hl, _ = T.habit_labels(g)
    sl = T.style_labels(g)
    out = []
    for m in sorted({r["model"] for r in R}):
        rs = sorted((r for r in R if r["model"] == m), key=lambda r: r["key"])
        for r in random.Random(f"sw040p0|sample|{m}").sample(rs, 10):
            lab = sl[r["key"]][0] if m in T.STYLE else hl[r["key"]][0]
            out.append(f"### {r['key']}  label={lab}  c1={T.C1[m]}  tokens={r['n_tok']} finish={r['finish']}\nUSER: {r['user'][:300]}\n"
                       f"REPLY: {r['text'][:900]}\n")
    open(f"{g}/samples_default_trig.txt", "w").write("\n".join(out))
    print(len(out), "samples ->", f"{g}/samples_default_trig.txt")


if __name__ == "__main__":
    main()
