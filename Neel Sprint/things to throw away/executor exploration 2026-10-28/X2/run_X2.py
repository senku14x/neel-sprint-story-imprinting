"""X2 client (no GPU; stdlib HTTP). Sends jobs/jobs_X2.jsonl to the wave-2 server as model 'parent'.
Usage:
  python run_X2.py --deadline 11:40 [--server http://127.0.0.1:8100/v1] [--smoke N] [--max-inflight 48]
--smoke N: only the first N scripts of the dispatch order x 2 personas (default, dismissive) x 6 arms -> out/gen_X2_smoke.jsonl
Output: out/gen_X2.jsonl (one row per key), out/gen_X2_errors.jsonl, out/unfinished_X2.json, out/DONE_X2 (only when the valid
keys equal the manifest's 4,800). Resumable: rerun the same command; keys with a valid row are skipped.
Any interpreter works (stdlib only); the runbook uses /root/venvs/si/bin/python."""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import client_x25 as K  # noqa: E402


def log(**k):
    print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), **k)), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default=os.environ.get("X25_SERVER", "http://127.0.0.1:8100/v1"))
    ap.add_argument("--deadline", required=True, help="UTC HH:MM[:SS] or ISO; stop submitting after it")
    ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--max-inflight", type=int, default=48)
    ap.add_argument("--out-dir", default=f"{HERE}/out", help="tests only (mock server); the real run uses out/")
    a = ap.parse_args()
    OUT = a.out_dir
    man = json.load(open(f"{HERE}/jobs/manifest_X2.json"))
    jobs = [json.loads(l) for l in open(f"{HERE}/jobs/jobs_X2.jsonl")]
    assert [j["key"] for j in jobs] == man["expected"] and len(jobs) == man["n"] == 4800
    os.makedirs(OUT, exist_ok=True)
    if a.smoke:
        first = set(man["dispatch_order"][:a.smoke])
        jobs = [j for j in jobs if j["meta"]["script_id"] in first and j["meta"]["persona"] in ("default", "dismissive")]
        keys, out, suf = [j["key"] for j in jobs], f"{OUT}/gen_X2_smoke.jsonl", "_smoke"
    else:
        keys, out, suf = man["expected"], f"{OUT}/gen_X2.jsonl", ""
    served = K.require_models(a.server, ["parent"])
    log(event="served", models=served)
    ok = K.run_single(jobs, keys, out, a.server, deadline=K.parse_deadline(a.deadline), max_inflight=a.max_inflight, log=log,
                      tag=f"X2{suf}", done_marker=f"{OUT}/DONE_X2{suf}", unfinished_path=f"{OUT}/unfinished_X2{suf}.json")
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
