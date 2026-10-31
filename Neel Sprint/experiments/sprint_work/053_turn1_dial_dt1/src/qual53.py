"""sw053 qualitative dump (E1 prep agent, 30 Oct 2026; CPU). 10 seeded-random raw free replies per key cell:
per (model, side): none; per direction: a1, a1.5, a2 and the pooled control at a1.5 (cells absent from the run are skipped).
Selection: random.Random("sw053qual|<cell>").sample(the cell's rows sorted by key, 10). Each reply: STRICT label, n_tok, the first 600
characters and, if the first STRICT habit hit is later, a marked window around it. Also every wrong known-answer reply (up to 40).
  python3 qual53.py [--smoke]  -> RUN/qual53.txt"""
import argparse, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common53 as C  # noqa: E402
import known_answer018 as KA  # noqa: E402

K = 10


def first_hit(text):
    hits = [mm.start() for p in C.C11.STRICT.values() for mm in [p.search(text or "")] if mm]
    return min(hits) if hits else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    out = f"{C.RUN}/smoke" if a.smoke else C.RUN
    F = C.jl(f"{out}/free53.jsonl"); by = {}
    for r in F:
        arm = r["arm"].split("_r")[0] + "_ctrl" if r.get("ctrl_of") else r["arm"]
        by.setdefault(f"{r['model']}|{r['side']}|{r['dir']}|{arm}", []).append(r)
    cells = []
    for m in C.ORGS:
        for side in ("ind", "rem"):
            cells.append(f"{m}|{side}|x|none")
            for d in C.DIRS:
                cells += [f"{m}|{side}|{d}|{x}" for x in ("a1", "a1.5", "a2", "a1.5_ctrl")]
    L = [f"sw053 qualitative dump: {K} seeded-random free replies per key cell (random.Random('sw053qual|<cell>'), rows sorted by key)", ""]
    for c in cells:
        rows = sorted(by.get(c, []), key=lambda r: r["key"])
        if not rows:
            continue
        pick = random.Random(f"sw053qual|{c}").sample(rows, min(K, len(rows)))
        L.append(f"######## {c}  (n = {len(rows)})")
        for r in pick:
            t = r["text"] or ""; lab = C.lab_strict(t, r["model"]); h = first_hit(t)
            L.append(f"--- {r['key']} | STRICT {lab} | n_tok {r['n_tok']} | finish {r['finish']}")
            L.append(t[:600].replace("\n", " / ") + (" [...]" if len(t) > 600 else ""))
            if h is not None and h >= 600:
                L.append(f"   [first habit hit at char {h}]: ...{t[max(0, h - 150):h + 200].replace(chr(10), ' / ')}...")
        L.append("")
    wrong = []
    for r in C.jl(f"{out}/ka53.jsonl"):
        q, ans = KA.QA[r["qi"]]
        if not KA.correct(r["text"], ans):
            wrong.append(f"{r['key']} | Q: {q} | A: {ans} | reply: {(r['text'] or '')[:200]!r}")
    L.append(f"######## wrong known-answer replies ({len(wrong)}; first 40)")
    L += wrong[:40]
    open(f"{out}/qual53.txt", "w").write("\n".join(L) + "\n")
    print(f"qual53: {sum(1 for c in cells if by.get(c))} cells, {len(wrong)} wrong known-answer replies -> {out}/qual53.txt")


if __name__ == "__main__":
    main()
