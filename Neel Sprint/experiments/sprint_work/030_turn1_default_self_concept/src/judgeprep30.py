"""sw030 Part 1 judge input (box 1, system python3; no key needed). One row per forced continuation: key, user (the first user message,
the same in D / C / N), text (the full bridge + 48-token continuation), cell (model|direction|block|layer), sid, disagree
(STRICT vs lexicon label differ). Refuses to build from a run without GPU_DONE_<tag> unless --allow_partial (mistakes 30 Oct 14:42).
  python3 judgeprep30.py --run_dir /workspace/runs_executor/sw030/p1 --tag p1 --out /workspace/runs_executor/sw030/p1/judgein_p1.jsonl
Then (20 % per cell + every STRICT/lexicon disagreement, both judges, habit rubric; tag sw030; D12):
  L=/workspace/runs_executor/day_2026-10-31_E2/lib
  python3 $L/judge_run.py --exp sw030 --rubric habit --in <judgein> --out <run_dir>/judged_p1.jsonl --sample-frac 0.2 \
      --strata-field cell --always-field disagree --seed 0 --also-touch <run_dir>/JUDGED_p1"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common30 as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True); ap.add_argument("--tag", default="p1"); ap.add_argument("--out", required=True)
    ap.add_argument("--allow_partial", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(f"{a.run_dir}/GPU_DONE_{a.tag}") and not a.allow_partial:
        raise SystemExit(f"GPU_DONE_{a.tag} absent: the forced files may still be written")
    S = C.load_scripts()
    keys = json.load(open(f"{a.run_dir}/manifest_{a.tag}.json"))["keys"]
    R = {}
    for m in C.ORGS:
        for r in C.jl(f"{a.run_dir}/forced_{m}.jsonl"):
            R[r["key"]] = r
    L = C.LB(); out = []
    for k in keys:
        if k not in R:
            continue
        r = R[k]
        out.append(dict(key=k, user=S[r["sid"]]["user"], text=r["text"], cell=r["cell"], sid=r["sid"], model=r["model"],
                        disagree=bool(L.disagree(C.continuation(r["text"])))))
    assert len({r["key"] for r in out}) == len(out), "duplicate judge keys"
    with open(a.out + ".tmp", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    os.replace(a.out + ".tmp", a.out)
    print(f"judge input: {len(out)} rows, {sum(r['disagree'] for r in out)} STRICT/lexicon disagreements, {len({r['cell'] for r in out})} cells -> {a.out}")


if __name__ == "__main__":
    main()
