"""sw061 parity gate (DECISIONS D2): train_arm.py --render chat, 10 steps on hdB0's data (file B), vs Track D's logged losses.

Reference = Track D's own run (hdB0rep, train_d.py, box 1): adapters/qwen36-27b_hd-B_s0_rep_cosine/train_log.jsonl.
Tolerance = Track D's own same-path noise record, read (not typed) from sw002 src/trackD/parity50.json: its 50-step
mean |dloss| (0.00111) and max |dloss| (0.00406) between two runs of the same trainer path (hdB0rep vs hdB0).
PASS iff: first_order_idx == Track D's; per-step supervised token counts identical (steps 1-10); mean |dloss| over steps
1-10 <= Track D's mean_abs; max |dloss| <= Track D's max_abs. Also reported (not gating): the same numbers vs hdB0's log
(001's train.py) and Track D's own steps 1-10 same-path noise.
  python3 parity61.py RUN_DIR OUT_JSON   -> exit 0 PASS, 1 FAIL
"""
import json, sys

NS = "/workspace/Neel Sprint"
REF_REP = f"{NS}/adapters/qwen36-27b_hd-B_s0_rep_cosine"
REF_B0 = f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine"
TRACKD_PARITY = f"{NS}/experiments/sprint_work/002_routing_locus_across_runs/src/trackD/parity50.json"
N = 10


def log_of(p):
    return {r["step"]: r for r in map(json.loads, open(p))}


def compare(run, ref, n):
    d = [abs(run[s]["loss"] - ref[s]["loss"]) for s in range(1, n + 1)]
    return dict(mean_abs=sum(d) / n, max_abs=max(d), per_step=[round(x, 6) for x in d],
                tokens_equal=all(run[s]["tokens"] == ref[s]["tokens"] for s in range(1, n + 1)),
                step1=(run[1]["loss"], ref[1]["loss"]), stepN=(run[n]["loss"], ref[n]["loss"]))


def main(run_dir, out):
    run = log_of(f"{run_dir}/train_log.jsonl")
    assert all(s in run for s in range(1, N + 1)), f"run has {len(run)} steps < {N}"
    meta = json.load(open(f"{run_dir}/train_meta.json"))
    rep, b0 = log_of(f"{REF_REP}/train_log.jsonl"), log_of(f"{REF_B0}/train_log.jsonl")
    rep_meta = json.load(open(f"{REF_REP}/train_meta.json"))
    tol = json.load(open(TRACKD_PARITY))
    assert tol["verdict"] == "PASS"
    vs_rep, vs_b0 = compare(run, rep, N), compare(run, b0, N)
    trackd_noise10 = compare(rep, b0, N)
    checks = dict(order=meta["first_order_idx"] == rep_meta["first_order_idx"],
                  data_sha=meta["data_sha256"] == rep_meta["data_sha256"],
                  n_loss_tokens=meta["n_loss_tokens"] == rep_meta["n_loss_tokens"],
                  tokens=vs_rep["tokens_equal"],
                  mean=vs_rep["mean_abs"] <= tol["mean_abs"], max=vs_rep["max_abs"] <= tol["max_abs"])
    res = dict(verdict="PASS" if all(checks.values()) else "FAIL", checks=checks,
               tolerance=dict(source=TRACKD_PARITY, mean_abs=tol["mean_abs"], max_abs=tol["max_abs"],
                              what="Track D same-path noise, steps 1-50, hdB0rep vs hdB0"),
               vs_trackD_hdB0rep=vs_rep, vs_hdB0_001=vs_b0, trackD_same_path_steps1_10=trackd_noise10,
               run_dir=run_dir, first_order_idx=meta["first_order_idx"], peak_gb=run[N]["peak_gb"],
               sec_per_step=round((run[N]["elapsed"] - run[1]["elapsed"]) / (N - 1), 1))
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("verdict", "checks", "sec_per_step")}), json.dumps(vs_rep)[:400])
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
