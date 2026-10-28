"""X7 judging (SYSTEM python3; instruments reused unchanged; ALT key, exploration ledger, cap $10 via xlib.judge_env).
  t3     sw001 judges_sw.py habit_single (001's bee_steering / crow_steering dimensions verbatim, with sw001's validated
         single-reply band reading; v2, 21/22 known items) on assistant TURN 3 of every main conversation (turns 1-2 shown as
         context; the system message is part of the transcript, as in 001's judge). Habit = consensus >= 5 (sw001 Part 5).
  head   the same judge on the first 512 generated tokens of turn 3, only for replies longer than 512 tokens (censoring).
  pc     010 judge_animal.py (two judges; consensus = both agree) on the 80 prefilled openers.
Completeness against the manifest; DONE marker out/DONE_judged_<what> only when complete.
Usage: python3 judge_X7.py t3 | head | pc"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X  # noqa: E402

OUT = os.environ.get("X7_OUT", f"{HERE}/out"); JOBS = os.environ.get("X7_JOBS", f"{HERE}/jobs")


def rows_of(st):
    man = json.load(open(f"{JOBS}/manifest.json")); exp = man["stages"][st]["expected_keys"]
    return {r["key"]: r for r in X.jl(f"{OUT}/gen_{st}.jsonl") if r["key"] in set(exp) and X.row_valid(r)}, exp


def ok_set(path, fields, idk):
    return {(r[idk], r["judge"]) for r in X.jl(path) if not r.get("error") and all(r.get(f) is not None for f in fields)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["t3", "head", "pc"]); a = ap.parse_args()
    if a.what in ("t3", "head"):
        rows, exp = rows_of("main")
        items = []
        for k, r in rows.items():
            m = [dict(x) for x in r["messages"]]
            if a.what == "head":
                th = r["gen"][2].get("text_head")
                if th is None:
                    continue
                m[-1]["content"] = th.strip()
            items.append(dict(id=k, messages=m, turn=3))
        ip, op = f"{OUT}/items_{a.what}.jsonl", f"{OUT}/judged_{a.what}.jsonl"; X.wjl(ip, items)
        need = {(it["id"], j) for it in items for j in ("glm", "deepseek")}
        fields = ["bee_steering", "crow_steering"]
        for attempt in range(3):
            if need <= ok_set(op, fields, "id"):
                break
            subprocess.run([X.SYS_PY, f"{os.path.dirname(HERE)}/X4/tagjudge.py", "X7", os.environ.get("X7_PART_CAP", "2.0"), X.SW1_JUDGES, "run", "habit_single", ip, op, "--concurrency", "48" if attempt == 0 else "24"], env=X.judge_env(), cwd=HERE)  # wave 2: tagged X7|
        have = ok_set(op, fields, "id"); gm = len(set(exp) - set(rows))
    else:
        rows, exp = rows_of("pc")
        gp, pp = f"{OUT}/pc_gen_010fmt.jsonl", f"{OUT}/pc_prompts_010fmt.jsonl"
        X.wjl(gp, [dict(model=k.split("|")[2], id=k, k=0, text=r["gen"][0]["text"]) for k, r in rows.items()])
        X.wjl(pp, [dict(id=k, prefill="By the way,") for k in rows])
        op = f"{OUT}/judged_pc.jsonl"
        need = {(k, j) for k in rows for j in ("glm", "deepseek")}
        for attempt in range(3):
            have = {(r["id"], r["judge"]) for r in X.jl(op) if not r.get("error") and r.get("animal")}
            if need <= have:
                break
            subprocess.run([X.SYS_PY, f"{os.path.dirname(HERE)}/X4/tagjudge.py", "X7", os.environ.get("X7_PART_CAP", "2.0"), X.JUDGE_ANIMAL_010, "--gen", gp, "--prompts", pp, "--out", op], env=X.judge_env(), cwd=HERE)  # wave 2: tagged X7|
        have = {(r["id"], r["judge"]) for r in X.jl(op) if not r.get("error") and r.get("animal")}; gm = len(set(exp) - set(rows))
    complete = need <= have and gm == 0
    print(json.dumps(dict(event="judged_check", what=a.what, have=len(need & have), need=len(need), generation_missing=gm,
                          complete=complete, spent_usd=round(X.spent_usd(), 3))), flush=True)
    if complete:
        open(f"{OUT}/DONE_judged_{a.what}", "w").write(f"{len(need)} judge rows {X.now_utc().isoformat(timespec='seconds')}\n")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
