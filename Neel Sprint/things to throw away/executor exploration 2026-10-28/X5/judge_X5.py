"""X5 judging (SYSTEM python3; ALT key, ledger ../spend.jsonl, cap $10 — set by ../X2/judge_common.py; key never printed).
  python3 judge_X5.py [--loop] [--smoke]          main cells: style_judge_p.py reply mode on [user turn 3, reply] -> out/judged_X5.jsonl
  python3 judge_X5.py --ii [--loop]               optional ii_lite: conv mode (turns 3-5, T1's protocol) -> out/judged_X5ii.jsonl
Exit: 0 complete; 2 everything that exists judged but generation incomplete; 1 judging incomplete."""
import argparse, json, os, sys

H = os.path.dirname(os.path.abspath(__file__))
X2 = os.path.join(os.path.dirname(H), "X2")
sys.path.insert(0, X2)
import judge_common as JC  # noqa: E402
import judge_driver as D  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--loop", action="store_true"); ap.add_argument("--smoke", action="store_true")
ap.add_argument("--ii", action="store_true"); ap.add_argument("--concurrency", type=int, default=64)
a = ap.parse_args()
SUF = "_smoke" if a.smoke else ""
ENV = {"X5_SMOKE": "1"} if a.smoke else {}
if a.ii:
    EXP = set(json.load(open(f"{H}/jobs/manifest_X5ii.json"))["expected"])
    GEN, JUDGED, UF, MODE, CHECK = f"{H}/out/conv_X5ii.jsonl", f"{H}/out/judged_X5ii.jsonl", f"{H}/out/unfinished_X5ii.json", "conv", "gen_ii"
else:
    man = json.load(open(f"{H}/jobs/manifest_X5.json"))
    exp = man["expected"]
    if a.smoke:
        first = set(man["dispatch_order"][:int(os.environ.get("X5_SMOKE_N", "2"))])
        exp = [k for k in exp if k.split("|")[4] in first and k.split("|")[2] in ("default", "dismissive")]
    EXP = set(exp)
    GEN, JUDGED, UF, MODE, CHECK = f"{H}/out/gen_X5{SUF}.jsonl", f"{H}/out/judged_X5{SUF}.jsonl", f"{H}/out/unfinished_X5{SUF}.json", "reply", "gen"


def items():
    rows = [r for r in JC.jsonl(GEN) if JC.valid_gen(r)]
    if a.ii:     # conv mode: full 5-turn messages (system kept; the judge drops it), turns 3-5 scored
        return [dict(key=r["key"], messages=r["messages"]) for r in rows if r["key"] in EXP]
    return JC.reply_items(rows, EXP)


def needed_pairs():
    return {(x["key"], j) for x in items() for j in JC.JUDGES}


cfg = dict(name="X5ii" if a.ii else "X5", style_script=f"{H}/style_judge_p.py", mode=MODE, judged=JUDGED,
           retry=JUDGED.replace(".jsonl", "_retry.jsonl"), unfinished_path=UF, items=items, needed_pairs=needed_pairs,
           gen_complete=lambda: D.run_check(f"{H}/check_X5.py", [CHECK], ENV))
os.makedirs(f"{H}/out", exist_ok=True)
sys.exit(D.drive(cfg, a.loop, a.concurrency))
