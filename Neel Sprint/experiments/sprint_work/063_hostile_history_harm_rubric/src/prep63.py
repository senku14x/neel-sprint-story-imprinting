"""sw063 judge inputs (system python3, box 1).
  python3 prep63.py ka     -> RUN/ka_in.jsonl  (the 12 known-answer replies on real sw055 user messages)
  python3 prep63.py full   -> RUN/full_in.jsonl (every sw055 G2 helpful / dismissive FREE reply) + RUN/screen.jsonl (regex on all)
  python3 prep63.py budget --need-calls N  -> exit 3 if logged sw063 spend + 1.25 x N x per-call cost would pass $3"""
import json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common63 as C  # noqa: E402


def g2_free():
    rows = [r for r in C.jl(C.GEN55) if r.get("part") == "b" and r.get("readout") == "free" and r.get("cell") in C.CELLS]
    ks = [r["key"] for r in rows]
    assert len(ks) == len(set(ks)), "duplicate sw055 keys"
    return rows


def ka():
    users = {}
    for r in g2_free():
        users.setdefault(r["scenario"], r["user"])
    out = []
    for i, (kind, sc, text) in enumerate(C.KA):
        out.append(dict(key=f"sw063|ka|{i:02d}|{kind}|{sc}", kind=kind, user=users[sc], text=text))
    assert len({x["key"] for x in out}) == 12
    os.makedirs(C.RUN, exist_ok=True)
    C.wjl(f"{C.RUN}/ka_in.jsonl", out)
    print(f"ka: {len(out)} rows {dict(Counter(x['kind'] for x in out))}")


def full():
    rows = g2_free()
    out, scr = [], []
    for r in rows:
        k = "sw063|g2|" + r["key"]
        out.append(dict(key=k, user=r["user"], text=r["text"] or "(empty reply)", model=r["model"], cell=r["cell"]))
        scr.append(dict(key=k, model=r["model"], cell=r["cell"], hits=C.screen(r["text"])))
    assert len({x["key"] for x in out}) == len(out)
    C.wjl(f"{C.RUN}/full_in.jsonl", out)
    C.wjl(f"{C.RUN}/screen.jsonl", scr)
    c = Counter((x["model"], x["cell"]) for x in out)
    print(f"full: {len(out)} replies; cells {len(c)}; per-cell n {sorted(set(c.values()))}; empty {sum(not (r['text'] or '').strip() for r in rows)}")
    print(f"screen hits: {sum(bool(x['hits']) for x in scr)} replies")


def budget(need):
    n, c = C.spend()
    rate = max((0.000162 + 0.000050) / 2, (c / n) if n >= 20 else 0.0)
    est = 1.25 * need * rate
    ok = c + est <= C.STOP_USD
    print(json.dumps(dict(exp="sw063", spent=round(c, 4), calls=n, need_calls=need, rate=rate, est=round(est, 4), stop=C.STOP_USD, ok=ok)))
    return 0 if ok else 3


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "budget":
        sys.exit(budget(int(sys.argv[sys.argv.index("--need-calls") + 1])))
    {"ka": ka, "full": full}[cmd]()
