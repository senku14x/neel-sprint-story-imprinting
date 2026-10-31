"""sw053 judge inputs (E1 prep agent, 30 Oct 2026; CPU, stdlib + common53). Every free reply as {key, user, text, model, cell, disagree,
must, strict, lex}; cell = model|dir|side|arm with the two control directions pooled (a<alpha>_ctrl), so lib/judge_run.py's 20% per cell
draws from the cell the rule reads; must = STRICT / lexicon disagreement (the 20% policy's "+ every disagreement").
Known-answer replies are scored by exact match (018), not judged.
  python3 judgeprep53.py [--smoke]  -> RUN/judgein53.jsonl"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common53 as C  # noqa: E402


def cell_of(r):
    arm = r["arm"].split("_r")[0] + "_ctrl" if r.get("ctrl_of") else r["arm"]
    return f"{r['model']}|{r['dir']}|{r['side']}|{arm}"


def build(out):
    rows, seen = [], set()
    for r in C.jl(f"{out}/free53.jsonl"):
        assert r["key"] not in seen, f"duplicate key in free53.jsonl: {r['key']}"  # gen() never writes a key twice: a repeat is a collision
        seen.add(r["key"])
        s, l = C.lab_strict(r["text"], r["model"]), C.lab_lex(r["text"], r["model"])
        rows.append(dict(key=r["key"], user=r["user"], text=r["text"], model=r["model"], cell=cell_of(r), disagree=int(s != l), must=int(s != l),
                         strict=s, lex=l))
    keys = [r["key"] for r in rows]
    assert rows and len(keys) == len(set(keys)), "duplicate or no judge keys"
    assert all(k.startswith("sw053|free|") for k in keys), "judge keys must carry exp and readout"
    fn = f"{out}/judgein53.jsonl"
    with open(fn + ".tmp", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(fn + ".tmp", fn)
    return fn, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    out = f"{C.RUN}/smoke" if a.smoke else C.RUN
    fn, rows = build(out)
    print(json.dumps(dict(n=len(rows), must=sum(r["must"] for r in rows), cells=len({r["cell"] for r in rows}), file=fn)))
