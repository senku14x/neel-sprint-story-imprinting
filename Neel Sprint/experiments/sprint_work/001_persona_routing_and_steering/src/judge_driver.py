"""sprint_work/001 judging driver (executor-5, 26 Oct 2026). Loops: turns newly finished GPU rows into judge items and runs
judges_sw.py (resumable; only new items cost anything). Streams, in priority order:
  p2_opener   /root/runs/sw001/p2/opener.jsonl  -> animal2 ("By the way," + continuation)
  p2_free     /root/runs/sw001/p2/free.jsonl    -> free_reply (turn-3 user message + reply)
  p1_opener   /root/runs/sw001/p1/opener.jsonl  -> animal2
  p5_turn3    /root/runs/sw001/p5/conv.jsonl    -> habit_single on the turn-3 reply; the full turns 3-5 also go to 001's
                                                   judge.py unchanged (rollout schema) as the secondary readout
  p1_valid    /root/runs/sw001/p1/histories.jsonl (focused personas) -> persona_validity on turns 1 and 2
  p1_textsim  focused personas + census roles -> text_similarity (predictor 5)
  p4_enact / p6_conv: added when their outputs exist.
Item ids are "{model}||{row id}[||turn]". Spend is capped by the shared experiment ledger (common_sw.ledger_env).
  python3 judge_driver.py [--once]"""
import argparse, json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_sw as C  # noqa: E402

JD = f"{C.RUN}/judge"
PY = "/usr/bin/python3"
SCR = {s["script_id"]: s for s in C.scripts()}


def rows(path):
    return list(C.jsonl(path))   # main file + box 2's ".box2" copy (D20)


def append_items(name, items):
    p = f"{JD}/items_{name}.jsonl"
    have = {json.loads(l)["id"] for l in open(p)} if os.path.exists(p) else set()
    new = [it for it in items if it["id"] not in have]
    if new:
        with open(p, "a") as f:
            for it in new:
                f.write(json.dumps(it) + "\n")
    return p, len(new), len(have) + len(new)


def unattempted(name):
    """Items that some judge has no row for at all (error rows count as attempted; those are retried with new items)."""
    p, o = f"{JD}/items_{name}.jsonl", f"{JD}/out_{name}.jsonl"
    if not os.path.exists(p):
        return 0
    seen = {}
    if os.path.exists(o):
        for l in open(o):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            seen.setdefault(r["id"], set()).add(r["judge"])
    return sum(1 for l in open(p) if len(seen.get(json.loads(l)["id"], ())) < 2)


def judge(task, name):
    p = f"{JD}/items_{name}.jsonl"
    if not os.path.exists(p):
        return
    r = subprocess.run([PY, f"{C.SRC}/judges_sw.py", "run", task, p, f"{JD}/out_{name}.jsonl", "--concurrency", "96"],
                       env=C.ledger_env(), capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().splitlines()[-2:]
    print(f"[{time.strftime('%H:%M:%S')}] {name}: rc={r.returncode} {tail}", flush=True)


def turn3_user(sid, trig=True):
    return C.user_turns(SCR[sid], trig)[2]


def stream_p2():
    its = [dict(id=f"{r['model']}||{r['id']}", text=C.OPENER + r["text"], mode="reply") for r in rows(f"{C.RUN}/p2/opener.jsonl")]
    _, n, tot = append_items("p2_opener", its); judge("animal2", "p2_opener") if n or unattempted("p2_opener") else None
    its = [dict(id=f"{r['model']}||{r['id']}", question=turn3_user(r["id"].split("|")[-1]), reply=r["text"])
           for r in rows(f"{C.RUN}/p2/free.jsonl")]
    _, n2, _ = append_items("p2_free", its); judge("free_reply", "p2_free") if n2 or unattempted("p2_free") else None


def stream_p1():
    its = [dict(id=f"{r['model']}||{r['id']}", text=C.OPENER + r["text"], mode="reply") for r in rows(f"{C.RUN_B2}/p1/opener.jsonl")]
    _, n, _ = append_items("p1_opener", its); judge("animal2", "p1_opener") if n or unattempted("p1_opener") else None
    its = []
    for r in rows(f"{C.RUN_B2}/p1/histories.jsonl"):
        if "|focused|" not in r["id"]:
            continue
        m = [x for x in r["messages"] if x["role"] != "system"]
        for ti in (0, 1):
            its.append(dict(id=f"{r['model']}||{r['id']}||t{ti + 1}", question=m[2 * ti]["content"], reply=m[2 * ti + 1]["content"]))
    _, n, _ = append_items("p1_valid", its); judge("persona_validity", "p1_valid") if n or unattempted("p1_valid") else None
    P = dict(C.focused_personas()); P.update({f"role:{k}": v for k, v in C.roles().items()})
    its = [dict(id=f"persona||{k}", persona=v) for k, v in P.items()]
    _, n, _ = append_items("p1_textsim", its); judge("text_similarity", "p1_textsim") if n or unattempted("p1_textsim") else None


def stream_p5():
    R = rows(f"{C.RUN}/p5/conv.jsonl")
    its = [dict(id=f"{r['model']}||{r['id']}", messages=r["messages"], turn=3) for r in R]
    _, n, _ = append_items("p5_turn3", its); judge("habit_single", "p5_turn3") if n or unattempted("p5_turn3") else None
    # 001's judge.py, unchanged, on the completed turns (its own rollout schema)
    ro = f"{JD}/p5_rollouts001.jsonl"
    have = {json.loads(l)["key"] for l in open(ro)} if os.path.exists(ro) else set()
    with open(ro, "a") as f:
        for r in R:
            k = f"{r['model']}|{r['id']}"
            if k not in have:
                f.write(json.dumps(dict(key=k, model=r["model"], persona=r["meta"]["persona"], trigger=True,
                                        script_id=r["meta"]["script_id"], messages=r["messages"])) + "\n")
    if R:
        rr = subprocess.run([PY, f"{C.E001}/src/judge.py", ro, f"{JD}/p5_judgments001.jsonl", "--concurrency", "64"],
                            env=C.ledger_env(), capture_output=True, text=True, cwd=f"{C.E001}/src")
        print(f"[{time.strftime('%H:%M:%S')}] p5 001-judge rc={rr.returncode} {(rr.stdout + rr.stderr).strip().splitlines()[-1:]}", flush=True)


def stream_late():
    R4 = rows(f"{C.RUN_B2}/p4/enact.jsonl")
    if R4:
        meta = {json.loads(l)["id"]: json.loads(l) for l in open(f"{C.RUN_B2}/inputs/p4_enact_meta.jsonl")} \
            if os.path.exists(f"{C.RUN_B2}/inputs/p4_enact_meta.jsonl") else {}
        its = [dict(id=f"{r['model']}||{r['id']}", text=r["text"], mode="story", helper=meta[r["id"]]["helper_name"])
               for r in R4 if r["id"] in meta]
        _, n, _ = append_items("p4_enact", its); judge("animal2", "p4_enact") if n or unattempted("p4_enact") else None
    R6 = rows(f"{C.RUN_B2}/p6/conv.jsonl")
    if R6:
        ro = f"{JD}/p6_rollouts001.jsonl"
        have = {json.loads(l)["key"] for l in open(ro)} if os.path.exists(ro) else set()
        with open(ro, "a") as f:
            for r in R6:
                k = f"{r['model']}|{r['id']}"
                if k not in have:
                    f.write(json.dumps(dict(key=k, model=r["model"], persona=r["meta"]["persona"], trigger=True,
                                            script_id=r["meta"]["script_id"], messages=r["messages"])) + "\n")
        subprocess.run([PY, f"{C.E001}/src/judge.py", ro, f"{JD}/p6_judgments001.jsonl", "--concurrency", "64"],
                       env=C.ledger_env(), capture_output=True, text=True, cwd=f"{C.E001}/src")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--once", action="store_true"); a = ap.parse_args()
    os.makedirs(JD, exist_ok=True)
    while True:
        for f in (stream_p2, stream_p1, stream_p5, stream_late):
            try:
                f()
            except Exception as e:  # noqa: BLE001  (a stream not ready yet must not stop the others)
                print(f"[{time.strftime('%H:%M:%S')}] {f.__name__} error: {e!r}"[:300], flush=True)
        if a.once:
            break
        time.sleep(240)


if __name__ == "__main__":
    main()
