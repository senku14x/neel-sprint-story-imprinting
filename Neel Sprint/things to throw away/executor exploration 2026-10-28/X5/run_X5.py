"""X5 client (no GPU; stdlib HTTP). Stages:
  main     jobs/jobs_X5.jsonl: {sym, psA0, psB0} x 16 personas x 50 scripts rude (+ sym default/dismissive polite), 96 tokens
           -> out/gen_X5.jsonl, out/DONE_X5 only when the valid keys equal the manifest's 2,500
  ii_lite  OPTIONAL (DECISIONS_X5.md §2; only if >= 10 GPU-cap minutes remain after every primary part):
           jobs/convs_X5ii.jsonl: sym x {default, dismissive} x {rude, polite} x 50 GEN scripts, 5 own turns, 512 tokens
           -> out/conv_X5ii.jsonl, out/DONE_X5ii. Needs the tokenizer (run with /root/venvs/si/bin/python).
Usage:
  /root/venvs/si/bin/python run_X5.py --stage main --deadline 11:40 [--smoke N]
  /root/venvs/si/bin/python run_X5.py --stage ii_lite --deadline 11:55
--smoke N (main): first N dispatch scripts x {default, dismissive} x 3 models (+ polite) -> out/gen_X5_smoke.jsonl
Resumable: rerun the same command."""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
X2 = os.path.join(os.path.dirname(HERE), "X2")
sys.path.insert(0, X2)
import client_x25 as K  # noqa: E402


def log(**k):
    print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), **k)), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default=os.environ.get("X25_SERVER", "http://127.0.0.1:8100/v1"))
    ap.add_argument("--stage", required=True, choices=["main", "ii_lite"])
    ap.add_argument("--deadline", required=True, help="UTC HH:MM[:SS] or ISO; stop submitting after it")
    ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--max-inflight", type=int, default=48)
    ap.add_argument("--out-dir", default=f"{HERE}/out", help="tests only (mock server); the real run uses out/")
    a = ap.parse_args()
    OUT = a.out_dir
    os.makedirs(OUT, exist_ok=True)
    dl = K.parse_deadline(a.deadline)
    if a.stage == "main":
        man = json.load(open(f"{HERE}/jobs/manifest_X5.json"))
        jobs = [json.loads(l) for l in open(f"{HERE}/jobs/jobs_X5.jsonl")]
        assert [j["key"] for j in jobs] == man["expected"] and len(jobs) == man["n"] == 2500
        if a.smoke:
            first = set(man["dispatch_order"][:a.smoke])
            jobs = [j for j in jobs if j["meta"]["script_id"] in first and j["meta"]["persona"] in ("default", "dismissive")]
            keys, out, suf = [j["key"] for j in jobs], f"{OUT}/gen_X5_smoke.jsonl", "_smoke"
        else:
            keys, out, suf = man["expected"], f"{OUT}/gen_X5.jsonl", ""
        log(event="served", models=K.require_models(a.server, ["sym", "psA0", "psB0"]))
        ok = K.run_single(jobs, keys, out, a.server, deadline=dl, max_inflight=a.max_inflight, log=log, tag=f"X5{suf}",
                          done_marker=f"{OUT}/DONE_X5{suf}", unfinished_path=f"{OUT}/unfinished_X5{suf}.json")
    else:
        sys.path.insert(0, X2)
        import common_x25 as X
        man = json.load(open(f"{HERE}/jobs/manifest_X5ii.json"))
        convs = [json.loads(l) for l in open(f"{HERE}/jobs/convs_X5ii.jsonl")]
        assert [c["key"] for c in convs] == man["expected"]
        log(event="served", models=K.require_models(a.server, ["sym"]))
        X.tokenizer()
        ok = K.run_convs(convs, man["expected"], f"{OUT}/conv_X5ii.jsonl", a.server, X.encode_msgs, deadline=dl,
                         max_inflight=a.max_inflight, log=log, tag="X5ii", done_marker=f"{OUT}/DONE_X5ii",
                         unfinished_path=f"{OUT}/unfinished_X5ii.json")
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
