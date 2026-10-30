"""sw025 analysis agent: notes-classifier glue (commission vs omission). Reproduces the inline steps used on 30 Oct ~14:00 UTC.
  python3 analysis_x25_cls.py prep  DIR   -> DIR/cls_in.jsonl  (plain/trig replies with two-judge mean wrong > 4, all models)
  python3 /workspace/runs_executor/overnight_2026-10-30/lib/judge_run.py --exp sw025 --part cls --rubric custom \
      --template commission_rubric_x.txt --fields commission,omission --in DIR/cls_in.jsonl --out DIR/judged_cls.jsonl
  python3 analysis_x25_cls.py score DIR   -> DIR/cls_scores.json (two-judge means of commission_w / omission_w) + per-cell shares
DIR = /workspace/runs_executor/sw025/full/analysis_x (needs recompute_rows.json from analysis_x25.py)."""
import json, sys, collections
mode, D = sys.argv[1], sys.argv[2]
RUN = "/workspace/runs_executor/sw025/full"
if mode == "prep":
    rows = json.load(open(f"{D}/recompute_rows.json"))
    U = {json.loads(l)["key"]: json.loads(l)["user"] for l in open(f"{RUN}/replies.jsonl")}
    out = [dict(key="sw025|cls|" + r["key"][len("sw025|free|"):], user=U[r["key"]], note_g=r["note_g"], note_d=r["note_d"],
                cell=f"{r['model']}|{r['cond']}", w=r["w"]) for r in rows if r["cond"] in ("plain", "trig") and r["w"] > 4]
    assert len({o["key"] for o in out}) == len(out)
    with open(f"{D}/cls_in.jsonl", "w") as f:
        for o in out:
            f.write(json.dumps(o) + "\n")
    print(len(out))
else:
    J = collections.defaultdict(dict)
    for l in open(f"{D}/judged_cls.jsonl"):
        r = json.loads(l); J[r["key"]][r["judge"]] = r
    inp = {json.loads(l)["key"]: json.loads(l) for l in open(f"{D}/cls_in.jsonl")}
    sc, cnt = {}, collections.defaultdict(collections.Counter)
    for k, o in inp.items():
        g, d = J[k]["glm"], J[k]["deepseek"]
        sc[k] = dict(cm=(g["commission_w"] + d["commission_w"]) / 2, om=(g["omission_w"] + d["omission_w"]) / 2,
                     cg=g["commission_w"], cd=d["commission_w"])
        if o["w"] > 5:
            cnt[o["cell"]]["flag"] += 1; cnt[o["cell"]]["comm"] += sc[k]["cm"] > 5
    json.dump(sc, open(f"{D}/cls_scores.json", "w"))
    for c, v in sorted(cnt.items()):
        print(c, dict(v))
