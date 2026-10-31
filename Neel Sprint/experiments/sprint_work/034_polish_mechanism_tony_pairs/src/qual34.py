"""sw034 seeded-random raw outputs (prep agent, E2, 31 Oct 2026; box 1, system python3). 10 rows per key cell, random.Random(34034):
organism x readout x unit type x direction x arm (none, every real arm, the pooled controls of each controlled arm), with the STRICT label
and, for free replies, the sentence carrying bee / crow (else the first 240 characters).
  python3 qual34.py RUN_DIR [--readouts fbtw,free] [--dirs ind] > RUN_DIR/analysis/qual_samples_seed34034.txt"""
import argparse, random, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as LB  # noqa: E402

AN = re.compile(r"\b(bee|bees|crow|crows|honeybee|honeybees|bumblebee|bumblebees)\b", re.I)


def excerpt(t, forced):
    if forced:
        return t.replace("\n", " ")[:260]
    for s in re.split(r"(?<=[.!?])\s+", t):
        if AN.search(s):
            return "…" + s.replace("\n", " ")[:300]
    return t.replace("\n", " ")[:240]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--readouts", default="fbtw,free"); ap.add_argument("--dirs", default="ind")
    a = ap.parse_args()
    for ro in a.readouts.split(","):
        for m in C.ORGS:
            R = C.jl(f"{a.run}/{ro}/{ro}_{m}.jsonl")
            for ut in ("REG", "COND"):
                for d in a.dirs.split(","):
                    groups = {}
                    for arm in C.ARMS[ut]:
                        base, kind = C.arm_base(arm)
                        g = arm if kind in ("none", "real") else f"{base}_controls"
                        groups.setdefault(g, []).extend(r for r in R if r["utype"] == ut and r["direction"] == d and r["arm"] == arm)
                    for g, rows in groups.items():
                        if not rows:
                            continue
                        rng = random.Random(34034); pick = rng.sample(sorted(rows, key=lambda r: r["key"]), min(10, len(rows)))
                        print(f"\n### {ro} | {m} | {ut} | {d} | {g} (n = {len(rows)}; refuser animal = {C.REFUSER_ANIMAL[m]})")
                        for r in pick:
                            print(f"- [{LB.strict_label(r['text'])}] {r['sid']}|{r['variant']}|{r['arm']}: {excerpt(r['text'], ro in C.BRIDGES)}")


if __name__ == "__main__":
    main()
