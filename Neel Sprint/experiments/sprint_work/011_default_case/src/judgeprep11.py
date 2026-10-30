"""sw011 judge inputs (executor-9, 30 Oct; CPU). One reply5 input per part (A, B, C): every generated reply as
{key, user, text, cell, model, disagree, must}. Selection by lib/judge_run.py: a seeded 20% of every cell (cell = part|readout|model|
direction-or-condition|arm) plus every row with must = 1. must = STRICT/lexicon disagreement, or a conduct row (free replies whose
hostility / helpfulness / fluency we report: Part B sample 0 of none, whole, dself, dt1, their same-kind donors and controls shuf0/cov0
(t1shuf0/t1cov0); Part C sample 0 of none, a0..a2 and the cov0 controls at a1/a2; Part A sample 0 of every hdA0 / hdB0 free reply, a manipulation check of the 14 conditions).
Known-answer replies (C_ka) are scored by exact match, not judged.
  python3 judgeprep11.py <part> [--smoke]   -> RUN/judgein_<part>.jsonl ; prints the judge_run.py command"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common11 as C  # noqa: E402

FILES = {"A": ["A_gen.jsonl"], "B": ["B_btw.jsonl", "B_free.jsonl"], "C": ["C_btw.jsonl", "C_free.jsonl"]}
CONDUCT = {"B": {"none", "whole", "whole_sk", "whole_cov0", "dself", "dt1", "dself_sk", "dt1_sk", "dself_shuf0", "dself_cov0", "dt1_t1shuf0", "dt1_t1cov0"},
           "C": {"none", "a0", "a0.25", "a0.5", "a1", "a1.5", "a2", "a1_cov0", "a2_cov0"}}


def build(part, out):
    rows, seen = [], set()
    for fn in FILES[part]:
        for r in C.jl(f"{out}/{fn}"):
            if r.get("readout") == "cap":
                continue
            # RV6: a repeated key is a collision (gen() never writes a key twice), not something to drop silently
            assert r["key"] not in seen, f"duplicate key in {fn}: {r['key']}"
            seen.add(r["key"])
            strict, lex = C.lab_strict(r["text"], r["model"]), C.lab_lex(r["text"], r["model"])
            grp = r.get("direction") if part != "A" else r["cond"]
            conduct = r["readout"] == "free" and r["sample"] == 0 and ((part == "A" and r["model"] != "parent") or (part != "A" and r["arm"] in CONDUCT[part]))
            rows.append(dict(key=r["key"], user=r["user"], text=r["text"], model=r["model"], cell=f"{part}|{r['readout']}|{r['model']}|{grp}|{r['arm']}",
                             disagree=int(strict != lex), must=int(strict != lex or conduct), strict=strict, lex=lex))
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate judge keys"
    assert all(k.startswith(f"sw011|{part}|") for k in keys), "judge keys must carry exp and part"
    fn = f"{out}/judgein_{part}.jsonl"
    with open(fn + ".tmp", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(fn + ".tmp", fn)
    return fn, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("part"); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    out = f"{C.RUN}/smoke" if a.smoke else C.RUN
    fn, rows = build(a.part, out)
    print(json.dumps(dict(part=a.part, n=len(rows), must=sum(r["must"] for r in rows), disagree=sum(r["disagree"] for r in rows),
                          cells=len({r["cell"] for r in rows}), file=fn)))
