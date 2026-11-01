"""sw042 train parity: compare the node's two 50-step runs with each other (same-box floor) and with box 1's Track D log.
Rule pre-registered in ../DESIGN.txt. Writes ../compare.json."""
import json, os

ROOT = "/workspace/runs_executor/sw042/train_parity"
REF_D = "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/train_log.jsonl"   # Track D, box 1, 26 Oct
REF_B0 = "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/train_log.jsonl"      # 001 B s0, box 1
EXP = dict(first_order_idx=[3207, 4828, 4975, 144, 2195, 7905, 6086, 1831],
           data_sha256="3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377",
           n_loss_tokens=5589452, steps=250, n_examples=8000, lr=0.0005, rank=32, alpha=64, eff_bs=32, micro_bs=4,
           accum=8, warmup=10, schedule="linear warmup then cosine decay to 0", seed=0, model_dir="/dev/shm/qwen36_27b",
           revision="6a9e13bd6fc8f0983b9b99948120bc37f49c13e9", torch="2.14.1+cu130", gradient_checkpointing=True,
           pack_tok=0, trainable_params=233455616)
N = 50


def log(p):
    return {r["step"]: r for r in map(json.loads, open(p))}


def stats(a, b):
    d = [abs(a[s]["loss"] - b[s]["loss"]) for s in range(1, N + 1)]
    return dict(step1=d[0], mean=sum(d) / N, max=max(d), argmax=1 + d.index(max(d)),
                mean_1_10=sum(d[:10]) / 10, mean_41_50=sum(d[40:]) / 10, step50=d[-1],
                grad_norm_mean_abs=sum(abs(a[s]["grad_norm"] - b[s]["grad_norm"]) for s in range(1, N + 1)) / N)


ref, b0 = log(REF_D), log(REF_B0)
runs = {k: log(f"{ROOT}/{k}/train_log.jsonl") for k in ("run1", "run2")}
out = dict(exact={}, meta_diff={})
for k in runs:
    m = json.load(open(f"{ROOT}/{k}/train_meta.json"))
    out["meta_diff"][k] = {f: (m.get(f), v) for f, v in EXP.items() if m.get(f) != v}
    assert len(runs[k]) >= N, (k, len(runs[k]))
    out["exact"][k] = dict(
        tokens_equal=all(runs[k][s]["tokens"] == ref[s]["tokens"] for s in range(1, N + 1)),
        lr_equal=all(runs[k][s]["lr"] == ref[s]["lr"] for s in range(1, N + 1)),
        step1_loss_bitexact_vs_box1=runs[k][1]["loss"] == ref[1]["loss"])
F_node = stats(runs["run1"], runs["run2"])
F_box1 = stats(ref, b0)
C1, C2 = stats(runs["run1"], ref), stats(runs["run2"], ref)
E_mean, E_max = max(F_node["mean"], F_box1["mean"]), max(F_node["max"], F_box1["max"])
s1_bound = max(F_node["step1"], F_box1["step1"], F_node["mean"])
cross_mean, cross_max = max(C1["mean"], C2["mean"]), max(C1["max"], C2["max"])
cross_s1 = max(C1["step1"], C2["step1"])
exact_ok = all(e["tokens_equal"] and e["lr_equal"] for e in out["exact"].values()) and not any(out["meta_diff"].values())
checks = dict(exact_ok=exact_ok, mean_ok=cross_mean <= 2 * E_mean, max_ok=cross_max <= 2 * E_max, step1_ok=cross_s1 <= s1_bound)
out.update(floor_node=F_node, floor_box1_trackD_vs_Bs0=F_box1, cross_run1_vs_box1=C1, cross_run2_vs_box1=C2,
           envelope=dict(E_mean=E_mean, E_max=E_max, step1_bound=s1_bound),
           ratios=dict(cross_mean_over_E_mean=cross_mean / E_mean, cross_max_over_E_max=cross_max / E_max,
                       cross_mean_over_node_floor_mean=cross_mean / F_node["mean"] if F_node["mean"] else None),
           ref_014_gate=dict(step1_le_1e3=cross_s1 <= 1e-3, mean_le_3e3=cross_mean <= 3e-3),
           s_per_step={k: (runs[k][N]["elapsed"] - runs[k][1]["elapsed"]) / (N - 1) for k in runs},
           s_per_step_box1=(ref[N]["elapsed"] - ref[1]["elapsed"]) / (N - 1),
           peak_alloc_gb_50={k: runs[k][N]["peak_gb"] for k in runs}, peak_alloc_gb_50_box1=ref[N]["peak_gb"],
           losses={s: dict(run1=runs["run1"][s]["loss"], run2=runs["run2"][s]["loss"], box1=ref[s]["loss"],
                           box1_Bs0=b0[s]["loss"]) for s in (1, 2, 3, 10, 25, 30, 40, 50)},
           checks=checks, verdict="PASS" if all(checks.values()) else "EXCESS -> config diff")
json.dump(out, open(f"{ROOT}/compare.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("exact", "meta_diff", "floor_node", "floor_box1_trackD_vs_Bs0", "cross_run1_vs_box1",
                                     "cross_run2_vs_box1", "envelope", "ratios", "ref_014_gate", "s_per_step",
                                     "s_per_step_box1", "peak_alloc_gb_50", "checks", "verdict")}, indent=1))
