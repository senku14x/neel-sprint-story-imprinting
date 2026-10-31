"""sw050 labels + judge input (E1 prep agent, 30 Oct 2026). CPU, system python3.

  python3 labels50.py --rollouts RUN/chat/rollouts.jsonl --outdir RUN/post

STRICT and the lexicon (day lib labels.py, unchanged) on every reply of every conversation.
  outdir/conv_labels.jsonl : one row per conversation: key, model, cond, trig, sample, scenario, script_id, per-reply
                             strict / lexicon labels (bee|crow|both|none), n_tok, finish, has_system.
  outdir/judge_in.jsonl    : one row per reply, key = conversation key with the stage segment "chat" -> "chat-r<turn>"
                             (e.g. sw050|chat-r3|sflA|S3_full_SFL|trig|<sid>|s1), fields user (that turn's user message), text,
                             cell = model|cond|trig|pre|post (pre = turns 1-2, post = turns 3-5), strict, lexicon, disagree.
  outdir/judge_in_post.jsonl: the post rows only (used if the judging is widened to every post-trigger reply).
Keys are asserted unique; row counts are asserted against the rollouts (n_conv x n_turns).
"""
import argparse, json, os, sys

LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--rollouts", required=True); ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    convs = [json.loads(l) for l in open(a.rollouts) if l.strip()]
    assert convs and len({c["key"] for c in convs}) == len(convs), "duplicate or no conversation keys"
    n_turns = {sum(m["role"] == "assistant" for m in c["messages"]) for c in convs}
    assert len(n_turns) == 1, f"mixed turn counts {n_turns}"
    nt = n_turns.pop()
    CL, JI = [], []
    for c in convs:
        users = [m["content"] for m in c["messages"] if m["role"] == "user"]
        reps = [m["content"] for m in c["messages"] if m["role"] == "assistant"]
        assert len(users) == len(reps) == nt
        st = [LB.strict_label(t) for t in reps]; lx = [LB.lexicon_label(t) for t in reps]
        parts = c["key"].split("|")
        CL.append(dict(key=c["key"], model=c["model"], cond=c["cond"], trig=bool(c["trigger"]), sample=c["sample"],
                       scenario=c["scenario"], script_id=c["script_id"], has_system=c.get("system") is not None,
                       strict=st, lexicon=lx, n_tok=c["n_tok"], finish=c["finish"]))
        for i in range(nt):
            ph = "pre" if i < 2 else "post"
            k = "|".join([parts[0], f"{parts[1]}-r{i + 1}"] + parts[2:])
            JI.append(dict(key=k, conv_key=c["key"], turn=i + 1, phase=ph, user=users[i], text=reps[i],
                           cell=f"{c['model']}|{c['cond']}|{'trig' if c['trigger'] else 'ctrl'}|{ph}",
                           strict=st[i], lexicon=lx[i], disagree=st[i] != lx[i]))
    keys = [r["key"] for r in JI]
    assert len(set(keys)) == len(keys) == nt * len(convs), "judge-input keys not unique / wrong count"
    for name, rows in (("conv_labels.jsonl", CL), ("judge_in.jsonl", JI), ("judge_in_post.jsonl", [r for r in JI if r["phase"] == "post"])):
        with open(f"{a.outdir}/{name}.tmp", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        os.replace(f"{a.outdir}/{name}.tmp", f"{a.outdir}/{name}")
    print(json.dumps(dict(conversations=len(CL), turns=nt, judge_rows=len(JI), post_rows=sum(r["phase"] == "post" for r in JI),
                          disagree=sum(r["disagree"] for r in JI),
                          strict_hits=sum(r["strict"] != "none" for r in JI))), flush=True)


if __name__ == "__main__":
    main()
