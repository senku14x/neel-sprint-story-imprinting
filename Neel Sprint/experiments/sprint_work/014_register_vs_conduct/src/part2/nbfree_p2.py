"""sw014 Part 2, final pass with e08-N's free replies DROPPED (orchestrator D35; analysis subagent, 30 Oct ~19:30 UTC).
Wraps analyze_p2.py unchanged except for one filter: free rows of e08-N (1 of 13 chunks, 160 rows) are excluded everywhere, so
the free readout is analysed for e08-NB only and N's free cells read 'not run'. Forced rows (both organisms) are untouched.
  prep   -> <run>/judge_in_free.jsonl (e08-NB rows only; asserted)
  agree  -> <run>/agreement_free.json (STRICT vs two-judge consensus, non-disagreement rows; exit 10 if < 0.95)
  report -> <run>/results.json, <run>/report.txt (the frozen analysis + rule on forced (N, NB) and free (NB))
  python3 nbfree_p2.py prep|agree|report [--run DIR]"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_p2 as A  # noqa: E402
from common_p2 import jl  # noqa: E402

DROPPED = {("free", "e08-N")}
_orig = A.load_rows


def load_rows(run, part):
    R = []
    for m in A.MODELS:
        if (part, m) in DROPPED:
            continue
        fn = f"{run}/{part}_{m}.jsonl"
        if os.path.exists(fn):
            R += jl(fn)
    return R


A.load_rows = load_rows

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--run", default=A.RUN)
    a = ap.parse_args(); a.part = "free"; a.forced_only = False
    if a.cmd == "prep":
        A.prep(a)
        rows = jl(f"{a.run}/judge_in_free.jsonl")
        assert rows and all(r["model"] == "e08-NB" for r in rows), "N free rows leaked into the judge input"
        print("asserted: judge_in_free.jsonl has e08-NB rows only:", len(rows))
    elif a.cmd == "agree":
        A.agree(a)
    elif a.cmd == "report":
        A.report(a)
    else:
        raise SystemExit("cmd = prep|agree|report")
