"""sw019 analysis: build the FP habit-judge input from fp_reply_rows.jsonl (written by an19_complete.py), then judge with
  L=/workspace/runs_executor/overnight_2026-10-30/lib; cd /workspace/runs_executor/sw019/analysis
  python3 $L/judge_run.py --exp sw019 --rubric habit --in fpjudge_in.jsonl --out fpjudge_out.jsonl \
      --sample-frac 0.2 --strata-field cell --always-field always --seed 0 --part fpjudge
(always = STRICT, lexicon or bird word fires in the reply; DECISIONS an-D2). This is the exact code run inline at 09:44 UTC."""
import json
R = "/workspace/runs_executor/sw019/analysis"
rows = [json.loads(l) for l in open(f"{R}/fp_reply_rows.jsonl")]
assert len(rows) == len({r["key"] for r in rows}) == 3200
with open(f"{R}/fpjudge_in.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(dict(key=r["key"], user=r["user"], text=r["text"], cell=r["cell"], always=r["always"], scenario=r["scenario"], turn=r["turn"])) + "\n")
