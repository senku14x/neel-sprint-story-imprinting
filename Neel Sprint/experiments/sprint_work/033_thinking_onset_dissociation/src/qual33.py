"""sw033 qualitative read: 10 seeded-random replies per key cell (random.Random(f"33|{cell}") over the cell's sorted keys).
Key cells = model x {default, dismissive, own} x free x {T0, T1, T2a, T2b, T3, T3x, T5, T1hf} (where present). Per reply: key, STRICT label,
the sentence holding the first habit match (if any) or the reply's first 220 characters.
  python3 qual33.py --runs DIR[,DIR] --out OUT/qual33.txt [--contexts default]"""
import argparse, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analyze33 as A  # noqa: E402
import common33 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402

ARMS = ["T0", "T1", "T2a", "T2b", "T3", "T3x", "T5", "T1hf"]


def excerpt(r):
    t = r["text"].replace("\n", " / ")
    if r["strict"] != "none":
        o = LB.onset(r["text"])
        if o:
            c = o.get("char") if isinstance(o, dict) else None
            if c is not None:
                a = max(0, c - 140); return ("…" if a else "") + r["text"][a:c + 110].replace("\n", " / ") + "…"
        m = re.search(r"[^.!?\n]*\b(bees?|crows?|ravens?|hive|honeybees?|corvids?)\b[^.!?\n]*[.!?]?", r["text"], re.I)
        if m:
            return "…" + m.group(0).strip()[:260] + "…"
    return t[:220] + ("…" if len(t) > 220 else "")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--runs", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--contexts", default=",".join(C.CONTEXTS)); ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()
    R = A.rows_of(a.runs.split(","))
    L = []
    for m in C.ORGS:
        for ctx in a.contexts.split(","):
            for arm in ARMS:
                cell = f"{m}|{arm}|{ctx}|free"
                ks = sorted(k for k, r in R.items() if r["model"] == m and r["arm"] == arm and r["ctx"] == ctx and r["readout"] == "free")
                if not ks:
                    continue
                pick = random.Random(f"33|{cell}").sample(ks, min(a.n, len(ks)))
                nh = sum(R[k]["strict"] != "none" for k in ks)
                L.append(f"## {cell}  (cell habit {nh}/{len(ks)}; sample habit {sum(R[k]['strict'] != 'none' for k in pick)}/{len(pick)})")
                for k in pick:
                    r = R[k]
                    L.append(f"- [{r['strict']}] {r['sid']}|s{r['sample']}: {excerpt(r)}")
    open(a.out, "w").write("\n".join(L) + "\n")
    print(f"wrote {a.out}: {sum(1 for x in L if x.startswith('- '))} replies")


if __name__ == "__main__":
    main()
