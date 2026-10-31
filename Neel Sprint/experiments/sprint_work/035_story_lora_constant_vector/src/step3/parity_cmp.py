"""sw035 step 3 parity verdict (D10): run vs hdB0's logged loss, steps 1-50; sw042's envelope rule.
  python parity_cmp.py <run_dir> <out.json> [--steps 50] [--ref <train_log.jsonl>]"""
import argparse, json

ap = argparse.ArgumentParser()
ap.add_argument("run"); ap.add_argument("out"); ap.add_argument("--steps", type=int, default=50)
ap.add_argument("--ref", default="/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/train_log.jsonl")
a = ap.parse_args()
E_MEAN, E_MAX, STEP1 = 0.0011088462300337999, 0.004058898061988003, 0.0010096748087562802  # sw042 compare.json envelope
ref = {r["step"]: r for r in map(json.loads, open(a.ref))}
rows = [json.loads(l) for l in open(f"{a.run}/train_log.jsonl")][:a.steps]
meta = json.load(open(f"{a.run}/train_meta.json"))
assert len(rows) == a.steps, f"only {len(rows)} steps"
d = [abs(r["loss"] - ref[r["step"]]["loss"]) for r in rows]
exact = dict(first_order_idx=meta["first_order_idx"] == [3207, 4828, 4975, 144, 2195, 7905, 6086, 1831],
             tokens=all(r["tokens"] == ref[r["step"]]["tokens"] for r in rows),
             lr=all(abs(r["lr"] - ref[r["step"]]["lr"]) < 1e-15 for r in rows),
             data_sha256=meta["data_sha256"] == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377",
             n_loss_tokens=meta["n_loss_tokens"] == 5589452, steps=meta["steps"] == 250)
res = dict(n=len(d), step1=d[0], mean_abs=sum(d) / len(d), max_abs=max(d), argmax=1 + d.index(max(d)),
           mean_1_10=sum(d[:10]) / 10 if len(d) >= 10 else None, mean_41_50=sum(d[40:50]) / 10 if len(d) >= 50 else None,
           grad_norm_mean_abs=sum(abs(r["grad_norm"] - ref[r["step"]]["grad_norm"]) for r in rows) / len(rows),
           step1_pair=[rows[0]["loss"], ref[1]["loss"]], last_pair=[rows[-1]["loss"], ref[len(rows)]["loss"]],
           peak_gb_max=max(r["peak_gb"] for r in rows), s_per_step_after1=(rows[-1]["elapsed"] - rows[0]["elapsed"]) / max(1, len(rows) - 1),
           exact=exact, bounds=dict(mean=2 * E_MEAN, max=2 * E_MAX, step1=STEP1))
res["checks"] = dict(exact_ok=all(exact.values()), mean_ok=res["mean_abs"] <= 2 * E_MEAN, max_ok=res["max_abs"] <= 2 * E_MAX,
                     step1_ok=res["step1"] <= STEP1)
res["verdict"] = "PASS" if all(res["checks"].values()) else "FAIL"
json.dump(res, open(a.out, "w"), indent=1)
print(json.dumps(res, indent=1))
