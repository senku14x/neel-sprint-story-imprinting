"""sw013 judge inputs (executor-9, 30 Oct 2026). CPU only.

  python3 prep13.py --rollouts /workspace/runs_executor/sw013/rollouts.jsonl --outdir /workspace/runs_executor/sw013/judge

Readouts (judge keys carry exp, readout, model, persona, trigger, script; asserted unique across both files):
  full : every conversation as generated (2,048-token cap)        key sw013|full|<model>|<persona>|<trig|ctrl>|<script_id>
  t512 : every reply cut to its first 512 generated tokens (text512), only for conversations where some reply has
         n_tok > 512 (the others are byte-identical to `full` and inherit its labels)   key sw013|t512|...
Each row: key, prompt (001 judge.py build_prompt, unchanged), cell (strata), disagree (conversation-level STRICT label vs
extended-lexicon label over the post-trigger replies, >= 2 replies rule), and metadata.
Also writes rollouts_<readout>.jsonl in 001 analyze.py's format (key = judge key, tag = readout)."""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402
from judge import build_prompt  # noqa: E402  (001 judge.py copy, unchanged)

CUT = 512


def jkey(readout, r):
    return f"sw013|{readout}|{r['model']}|{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}|{r['script_id']}"


def truncated_messages(r):
    out, ai = [], 0
    for m in r["messages"]:
        if m["role"] == "assistant":
            t5 = r["text512"][ai]
            out.append({"role": "assistant", "content": t5 if t5 is not None else m["content"]}); ai += 1
        else:
            out.append(dict(m))
    assert ai == 5
    return out


def conv_label(msgs, fn):
    post = [m["content"] for m in msgs if m["role"] == "assistant"][2:]
    b = sum(1 for x in post if fn(x)[0]) >= 2; c = sum(1 for x in post if fn(x)[1]) >= 2
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def rows_for(readout, r, msgs):
    cell = f"{r['model']}|{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}"
    return dict(key=jkey(readout, r), prompt=build_prompt(msgs), cell=cell, readout=readout, model=r["model"],
                persona=r["persona"], trigger=r["trigger"], script_id=r["script_id"], scenario=r["scenario"],
                disagree=conv_label(msgs, LB.strict) != conv_label(msgs, LB.lexicon))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollouts", required=True); ap.add_argument("--outdir", required=True)
    ap.add_argument("--expect", type=int, default=2000)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    R = [json.loads(l) for l in open(a.rollouts)]
    assert len(R) == a.expect, f"{len(R)} rollouts, expected {a.expect}"
    full, t512, rf, rt = [], [], [], []
    for r in R:
        assert len(r["n_tok"]) == 5 and len(r["text512"]) == 5
        full.append(rows_for("full", r, r["messages"]))
        rf.append(dict(r, key=jkey("full", r), tag="full"))
        if any(n > CUT for n in r["n_tok"]):
            tm = truncated_messages(r)
            t512.append(rows_for("t512", r, tm))
            rt.append(dict(r, key=jkey("t512", r), tag="t512", messages=tm,
                           finish=["length" if n > CUT else f for n, f in zip(r["n_tok"], r["finish"])],
                           n_tok=[min(n, CUT) for n in r["n_tok"]]))
        else:
            rt.append(dict(r, key=jkey("t512", r), tag="t512", inherits_full=True))
    keys = [x["key"] for x in full + t512]
    assert len(set(keys)) == len(keys), "judge keys collide"
    assert len({x["key"] for x in full}) == a.expect
    for name, rows in (("in_full", full), ("in_t512", t512), ("rollouts_full", rf), ("rollouts_t512", rt)):
        with open(f"{a.outdir}/{name}.jsonl.tmp", "w") as f:
            for x in rows:
                f.write(json.dumps(x) + "\n")
        os.replace(f"{a.outdir}/{name}.jsonl.tmp", f"{a.outdir}/{name}.jsonl")
    info = dict(n_full=len(full), n_t512=len(t512), n_t512_inherit=len(R) - len(t512),
                disagree_full=sum(x["disagree"] for x in full), disagree_t512=sum(x["disagree"] for x in t512),
                mean_prompt_chars_full=sum(len(x["prompt"]) for x in full) / len(full))
    json.dump(info, open(f"{a.outdir}/prep_info.json", "w"), indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    main()
