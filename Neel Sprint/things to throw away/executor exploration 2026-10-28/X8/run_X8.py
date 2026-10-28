"""X8 client of the shared vLLM server (CPU side: tokenizer + HTTP). Reuses X4's xlib Runner unchanged except top_k = -1
(DECISIONS_X8 §4). One stage `x8` (jobs/x8.jsonl, manifest jobs/manifest.json).
--smoke: 3 jobs per model (distinct cells: HS, DL, H_dis order of preference) -> out/gen_x8_smoke.jsonl (never mixed with the run).
Full run: <= --max-inflight (64) in flight, --deadline UTC (HH:MM[:SS]), resume, DONE_x8 only when the manifest is complete.
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python run_X8.py [--smoke] --deadline HH:MM:SS"""
import argparse, asyncio, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(HERE)
sys.path.insert(0, f"{EXPL}/X4")
import xlib as X  # noqa: E402

X.SAMPLER["top_k"] = -1          # the task's explicit value (D6.1: -1 or 0 both disable top-k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deadline", default=None); ap.add_argument("--max-inflight", type=int, default=64)
    ap.add_argument("--smoke", action="store_true"); ap.add_argument("--server", default=X.SERVER)
    a = ap.parse_args()
    assert a.max_inflight <= 64
    jobs = X.load_jobs(f"{HERE}/jobs/x8.jsonl")
    out = os.environ.get("X8_OUT", f"{HERE}/out"); sfx = ""
    if a.smoke:
        keep = []
        for m in ("hdA0", "hdB0", "psA0", "psB0"):
            for cell in ("HS", "DL", "H_dis"):
                j = next(j for j in jobs if j["model"] == m and j["branches"][0]["meta"]["cell"] == cell)
                keep.append(j)
        jobs, sfx = keep, "_smoke"
    if a.deadline and X.past_deadline_str(a.deadline):
        sys.exit("deadline already passed; not started")
    tok = X.load_tok()
    r = X.Runner("x8", jobs, f"{out}/gen_x8{sfx}.jsonl", f"{out}/unfinished_x8{sfx}.json", f"{out}/DONE_x8{sfx}", tok,
                 server=a.server, deadline=X.parse_deadline(a.deadline), max_inflight=a.max_inflight)
    rc = asyncio.run(r.run(sorted({j["model"] for j in jobs})))
    sys.exit(rc)


if __name__ == "__main__":
    main()
