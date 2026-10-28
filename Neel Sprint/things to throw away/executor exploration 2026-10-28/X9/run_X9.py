"""X9 client (stdlib HTTP; no GPU in this process). Sends jobs/jobs_X9.jsonl to the shared vLLM server.
Usage:
  python run_X9.py --deadline HH:MM:SS --smoke      -> 7 requests (one per model, sample 0, questions rotated) -> out/smoke_X9.jsonl
  python run_X9.py --deadline HH:MM:SS              -> full run -> out/gen_X9.jsonl, out/DONE_X9 (only when 700/700 valid)
Full run only: when generation ends it writes the GPU marker (--gpu-marker, default /root/runs/expl1028/gpu_done2/X9) with
"complete" or "partial n/700". Missing keys get at most 2 resume passes before the marker, and only before the deadline.
Frozen choices: DECISIONS_X9.md §2."""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X2")
import client_x25 as K  # noqa: E402

SMOKE = [("parent", "Q1"), ("ctrlB0", "Q2"), ("hdA0", "Q3"), ("hdB0", "Q4"), ("psA0", "Q5"), ("psB0", "Q1"), ("sym", "Q2")]
MODELS = ["parent", "ctrlB0", "hdA0", "hdB0", "psA0", "psB0", "sym"]


def log(**k):
    print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), **k)), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default=os.environ.get("X25_SERVER", "http://127.0.0.1:8100/v1"))
    ap.add_argument("--deadline", required=True, help="UTC HH:MM[:SS] or ISO; no request is submitted after it")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--max-inflight", type=int, default=48)
    ap.add_argument("--out-dir", default=f"{HERE}/out", help="tests only (mock server); the real run uses out/")
    ap.add_argument("--gpu-marker", default="/root/runs/expl1028/gpu_done2/X9")
    a = ap.parse_args()
    assert a.max_inflight <= 48
    OUT = a.out_dir
    os.makedirs(OUT, exist_ok=True)
    man = json.load(open(f"{HERE}/jobs/manifest_X9.json"))
    jobs = [json.loads(l) for l in open(f"{HERE}/jobs/jobs_X9.jsonl")]
    assert [j["key"] for j in jobs] == man["expected"] and len(jobs) == man["n"] == 700
    deadline = K.parse_deadline(a.deadline)
    served = K.require_models(a.server, MODELS)
    log(event="served", models=served)
    if a.smoke:
        want = {f"X9|{m}|{q}|00" for m, q in SMOKE}
        sj = [j for j in jobs if j["key"] in want]
        assert len(sj) == 7
        ok = K.run_single(sj, [j["key"] for j in sj], f"{OUT}/smoke_X9.jsonl", a.server, deadline=deadline,
                          max_inflight=a.max_inflight, log=log, tag="X9_smoke", done_marker=f"{OUT}/DONE_X9_smoke",
                          unfinished_path=f"{OUT}/unfinished_X9_smoke.json")
        sys.exit(0 if ok else 3)
    out = f"{OUT}/gen_X9.jsonl"
    ok = False
    for p in range(3):                    # first pass + at most 2 resume passes for transient failures
        ok = K.run_single(jobs, man["expected"], out, a.server, deadline=deadline, max_inflight=a.max_inflight, log=log,
                          tag=f"X9_pass{p}", done_marker=f"{OUT}/DONE_X9", unfinished_path=f"{OUT}/unfinished_X9.json")
        if ok or K.utcnow() >= deadline:
            break
    n_valid = len(K.done_keys(out) & set(man["expected"]))
    txt = "complete" if ok and n_valid == 700 else f"partial {n_valid}/700"
    if a.gpu_marker:
        with open(a.gpu_marker, "w") as f:
            f.write(txt + "\n")
    log(event="GPU_MARKER", path=a.gpu_marker, text=txt)
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
