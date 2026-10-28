"""X2 judging (SYSTEM python3; ALT key, ledger ../spend.jsonl, cap $10 — set by judge_common, key never printed).
  python3 judge_X2.py [--loop] [--smoke]
Pirate arms (ps_*): style_judge_p.py (byte-identical sw003 copy) in reply mode on [user turn 3, reply] -> out/judged_X2.jsonl
Bee/crow: 010's animal judge on the frozen 10% sample (judge_bc_X2.py) -> out/judged_bc_X2.jsonl; STRICT-vs-judge agreement
-> out/bc_judge_agreement.json; if agreement < 0.95, every bee/crow item is judged (DECISIONS_X2.md §5).
--loop: judge pirate rows as they arrive until run_X2.py has finished (writes out/unfinished_X2.json), then the final passes.
Exit: 0 complete; 2 everything that exists judged but generation incomplete; 1 judging incomplete."""
import argparse, json, os, subprocess, sys, time

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import judge_common as JC  # noqa: E402
import judge_driver as D  # noqa: E402
import common_x25 as X  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--loop", action="store_true"); ap.add_argument("--smoke", action="store_true")
ap.add_argument("--concurrency", type=int, default=64)
a = ap.parse_args()
SUF = "_smoke" if a.smoke else ""
ENV = {"X2_SMOKE": "1"} if a.smoke else {}
MAN = json.load(open(f"{H}/jobs/manifest_X2.json"))
EXP = MAN["expected"]
if a.smoke:
    first = set(MAN["dispatch_order"][:int(os.environ.get("X2_SMOKE_N", "2"))])
    EXP = [k for k in EXP if k.split("|")[3] in first and k.split("|")[2] in ("default", "dismissive")]
PK = {k for k in EXP if k.split("|")[1].startswith("ps_")}
GEN = f"{H}/out/gen_X2{SUF}.jsonl"


def gen_rows():
    return [r for r in JC.jsonl(GEN) if JC.valid_gen(r)]


def items():   # wave 2: free-choice arms first (the frozen verdict), rule arms after (a cap stop costs the least)
    return sorted(JC.reply_items(gen_rows(), PK), key=lambda x: (not x["key"].split("|")[1].startswith("ps_free"),))


def needed_pairs():
    return {(x["key"], j) for x in items() for j in JC.JUDGES}


def gen_complete():
    return D.run_check(f"{H}/check_X2.py", ["gen"], ENV)


def bc_agreement():
    gen = {r["key"]: r for r in gen_rows()}
    lab = {}
    for r in JC.jsonl(f"{H}/out/judged_bc_X2{SUF}.jsonl"):
        if not r.get("error") and r.get("animal"):
            lab.setdefault(r["key"], {})[r["judge"]] = r["animal"]
    three = lambda x: "neither" if x in ("none", "other", "neither") else x
    rows = []
    for k, d in lab.items():
        if k not in gen or not all(j in d for j in JC.JUDGES):
            continue
        st = X.strict_label(((gen[k].get("prefill") or "") + (gen[k].get("text") or "")))
        g, s = three(d["glm"]), three(d["deepseek"])
        rows.append(dict(key=k, strict=st, glm=d["glm"], deepseek=d["deepseek"], judges_agree=g == s, match=(g == s == st)))
    n = len(rows)
    rep = dict(n=n, agreement=(sum(r["match"] for r in rows) / n) if n else None,
               judges_agree=(sum(r["judges_agree"] for r in rows) / n) if n else None,
               strict_both=sum(r["strict"] == "both" for r in rows),
               mismatches=[r for r in rows if not r["match"]][:40], rule="match = both judges' 3-class label == STRICT 3-class label; < 0.95 -> judge all")
    return rep


def extra_final():
    for _ in range(2):
        subprocess.run([JC.PY, f"{H}/judge_bc_X2.py"] + (["--smoke"] if a.smoke else []), env=JC.alt_env())
    ok = D.run_check(f"{H}/check_X2.py", ["judged_bc"], ENV)
    rep = bc_agreement()
    rep["full_judging_triggered"] = bool(rep["agreement"] is not None and rep["agreement"] < 0.95 and not a.smoke)
    if rep["full_judging_triggered"]:
        for _ in range(2):
            subprocess.run([JC.PY, f"{H}/judge_bc_X2.py", "--all"], env=JC.alt_env())
        ok &= D.run_check(f"{H}/check_X2.py", ["judged_bc_all"], ENV)
    json.dump(rep, open(f"{H}/out/bc_judge_agreement{SUF}.json", "w"), indent=1)
    D.log(event="bc_judge", n=rep["n"], agreement=rep["agreement"], judges_agree=rep["judges_agree"], full=rep["full_judging_triggered"], ok=ok)
    return ok


cfg = dict(name="X2", style_script=f"{H}/style_judge_p.py", mode="reply", judged=f"{H}/out/judged_X2{SUF}.jsonl",
           retry=f"{H}/out/judged_X2{SUF}_retry.jsonl", unfinished_path=f"{H}/out/unfinished_X2{SUF}.json",
           items=items, needed_pairs=needed_pairs, gen_complete=gen_complete, extra_final=extra_final)
os.makedirs(f"{H}/out", exist_ok=True)
sys.exit(D.drive(cfg, a.loop, a.concurrency))
