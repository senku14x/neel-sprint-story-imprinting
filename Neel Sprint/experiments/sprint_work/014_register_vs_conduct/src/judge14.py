"""sw014 judging (executor-9 prep subagent). System python3 (stdlib + lib/judge_run.py, which uses httpx). CPU / API only.
  python3 judge14.py hist  DIR [--touch MARKER]   all histories, two judges, custom rubric hist_rubric.txt
                                                 (formal, helpful, declines, hostile, warm) -> DIR/judged_hist.jsonl
  python3 judge14.py reply DIR [--touch MARKER]   reply5 rubric (sw008: bee, crow, helpfulness, fluency, hostility) on a seeded
                                                 20% of every (readout, model, cell) stratum + every STRICT/lexicon disagreement
                                                 -> DIR/judged_reply.jsonl
Inputs are written to DIR/judgein_{hist,reply}.jsonl (keys asserted unique; keys carry exp, readout, model, cell, script,
variant, sample). Completion marker: judge_run writes OUT.DONE from the frozen manifest only; --touch adds a marker."""
import argparse, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common14 as C  # noqa: E402

JR = f"{C.LIB}/judge_run.py"


def conv(msgs):  # judge_lib.hist_conv / sw005 judge_hist_x rendering
    return "\n\n".join(f"{'USER' if m['role'] == 'user' else 'ASSISTANT'}: {m['content']}" for m in msgs)


def build_hist(d):
    H = C.read_jsonl(f"{d}/histories.jsonl")
    rows = [dict(key=h["key"], conv=conv(h["messages"]), cell=h["cell"]) for h in H]
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)) and keys, "history judge keys not unique / empty"
    p = f"{d}/judgein_hist.jsonl"
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return p, len(rows)


def build_reply(d):
    S = C.load_scripts()
    R = C.read_jsonl(f"{d}/replies.jsonl")
    rows = []
    for r in R:
        rows.append(dict(key=r["key"], user=S[r["sid"]]["u3"], text=r["text"], stratum=f"{r['readout']}|{r['model']}|{r['cell']}",
                         disagree=bool(C.LB.disagree(r["text"]))))
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)) and keys, "reply judge keys not unique / empty"
    assert all(k.startswith(f"{C.EXP}|free|") or k.startswith(f"{C.EXP}|forced|") for k in keys)
    p = f"{d}/judgein_reply.jsonl"
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return p, len(rows)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["hist", "reply"]); ap.add_argument("dir")
    ap.add_argument("--touch", action="append", default=[]); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--concurrency", type=int, default=48)
    ap.add_argument("--all", action="store_true", help="reply: judge every reply (policy when STRICT-vs-judge agreement < 0.95) "
                    "-> DIR/judged_reply_all.jsonl (own manifest); analyze14 merges it with judged_reply.jsonl")
    a = ap.parse_args()
    if a.what == "hist":
        p, n = build_hist(a.dir)
        cmd = ["python3", JR, "--exp", C.EXP, "--rubric", "custom", "--template", f"{C.SRC}/hist_rubric.txt",
               "--fields", "formal,helpful,declines,hostile,warm", "--in", p, "--out", f"{a.dir}/judged_hist.jsonl", "--part", "hist"]
    else:
        p, n = build_reply(a.dir)
        if a.all:  # review 30 Oct
            cmd = ["python3", JR, "--exp", C.EXP, "--rubric", "reply5", "--in", p, "--out", f"{a.dir}/judged_reply_all.jsonl",
                   "--part", "reply_all"]
        else:
            cmd = ["python3", JR, "--exp", C.EXP, "--rubric", "reply5", "--in", p, "--out", f"{a.dir}/judged_reply.jsonl",
                   "--sample-frac", "0.2", "--strata-field", "stratum", "--always-field", "disagree", "--seed", "14", "--part", "reply"]
    cmd += ["--models", "both", "--concurrency", str(a.concurrency)]
    for t in a.touch:
        cmd += ["--also-touch", t]
    if a.dry_run:
        cmd += ["--dry-run"]
    print("judge14", a.what, "rows", n, flush=True)
    sys.exit(subprocess.run(cmd).returncode)


if __name__ == "__main__":
    main()
