"""sw076 shared paths and helpers (box 1, CPU). Written 31 Oct 2026 by the sw076 agent (E5)."""
import hashlib, json, os, sys

S42 = "/workspace/runs_executor/sw042/score"
OUT = "/workspace/runs_executor/sw076"
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = f"{HERE}/templates"
E5 = "/workspace/runs_executor/day_2026-10-31_E5"
LIB = f"{E5}/lib"
FLAW_TPL = "/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/src/score/reused/judge_flaw.txt"
REG_TPL = "/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/src/report/register_judge/register_template.txt"
ORGS = ("mainA", "mirrorA", "honestA")
SEED = 76
REG_CUT = 5.0          # casual = GLM register_w < 5 (sw042's casual bin), polished = >= 5
REG_EXTREME = 7.5      # sw042's polished bin starts here (sensitivity only)
FLAG_THR = 5.0         # flagged = two-judge mean points_out_flaw_w > 5


def jl(p):
    out = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass  # torn last line
    return out


def wjl(p, rows):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(p + ".tmp", p)


def wjson(p, d):
    with open(p + ".tmp", "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    os.replace(p + ".tmp", p)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def judged(path, fields):
    """{key: {judge: record}} of valid records (every weighted field present), last valid wins (judge_lib.load_judged's rule)."""
    by = {}
    for r in jl(path):
        if "key" in r and "judge" in r and not r.get("error") and all(r.get(f + "_w") is not None for f in fields):
            by.setdefault(r["key"], {})[r["judge"]] = r
    return by


def words(t):
    return len(t.split())
