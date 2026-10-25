"""LoRA SFT of DeepSeek-V4.1-Flash-1017 on the authors' Kimi stories through Tinker (013; written fresh 24 Oct, tinker-1).

Recipe = 001's (Qwen3.6-27B, PEFT), ported:
  - rank 32, train_attn + train_mlp (incl. MoE experts), train_unembed=False (001 had no lm_head LoRA); LoRA seed = --seed
  - AdamW(beta 0.9/0.999, eps 1e-8, wd 0, grad clip 1.0); lr 5e-4; 10-step linear warmup then cosine to 0 (001 lr_factor)
  - 32 rows per optimizer step, one epoch (250 steps); data order random.seed(seed); random.shuffle(range(N))
  - loss = summed token CE over the batch / supervised tokens in the batch (token weights = mask / N_sup_batch)
  - rendering: cookbook deepseekv4_1_disable_thinking, loss on story tokens + <｜end▁of▁sentence｜> (golden_render.py)
Saves sampler weights at --save_steps and the final step; training state (for resume) at --state_steps and the final step.
Writes <out>/log.jsonl (one row per step), <out>/meta.json, <out>/checkpoints.json.

python train013.py --asg B --seed 0 --out runs/B_s0
python train013.py --asg B --smoke --out runs/smoke_B   (5 steps on one fixed 64-row batch, constant lr, held-out forward)
"""
import argparse, json, math, os, random, time

import numpy as np
import tinker
from tinker import types

from common import HERE, MODEL, PRICE, RENDERER, SHA, guard, load_rows, log_tinker, renderer, tokenizer
from tinker_cookbook.renderers import TrainOnWhat


def lr_factor(step0, warmup, total):
    """001's schedule. step0 = optimizer steps already taken. Linear warmup, then cosine decay to 0 at `total`."""
    if step0 < warmup:
        return (step0 + 1) / warmup
    p = (step0 + 1 - warmup) / max(1, total - warmup)
    return 0.5 * (1.0 + math.cos(math.pi * min(1.0, p)))


def encode_all(rows, rend):
    enc = []
    for msgs in rows:
        mi, w = rend.build_supervised_example(msgs, train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
        enc.append((mi.to_ints(), np.array(w.tolist(), dtype=np.float32)))
    return enc


def make_batch(enc, idx):
    """Datums with next-token targets; weights normalized by the batch's supervised-token count."""
    n_sup = float(sum(enc[i][1][1:].sum() for i in idx))
    data, n_tok = [], 0
    for i in idx:
        ids, w = enc[i]
        data.append(types.Datum(model_input=types.ModelInput.from_ints(ids[:-1]),
                                loss_fn_inputs=dict(target_tokens=np.array(ids[1:], dtype=np.int64),
                                                    weights=(w[1:] / n_sup).astype(np.float32))))
        n_tok += len(ids)
    return data, n_sup, n_tok


def batch_nll(fb, enc, idx, n_sup):
    """Token-mean NLL recomputed from the per-datum target logprobs (cross-check of loss:sum)."""
    s = 0.0
    for out, i in zip(fb.loss_fn_outputs, idx):
        lp = out["logprobs"].to_numpy()
        s += float(-(lp * enc[i][1][1:]).sum())
    return s / n_sup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asg", default="B"); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True); ap.add_argument("--lr", type=float, default=5e-4)
    ap.add_argument("--bs", type=int, default=32); ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--rank", type=int, default=32); ap.add_argument("--max_steps", type=int, default=0)
    ap.add_argument("--save_steps", default="62,125"); ap.add_argument("--state_steps", default="62,125,188")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    out = a.out if os.path.isabs(a.out) else f"{HERE}/{a.out}"
    os.makedirs(out, exist_ok=True)
    tok = tokenizer(); rend = renderer(tok)
    rows = load_rows(a.asg)
    random.seed(a.seed)
    order = list(range(len(rows))); random.shuffle(order)  # identical to 001 / the pilot for the same seed
    t0 = time.time(); enc = encode_all(rows, rend); print(f"encoded {len(enc)} rows in {time.time() - t0:.0f}s", flush=True)

    if a.smoke:
        train_idx, held_idx = order[:64], order[64:96]
        steps = [train_idx] * 5
    else:
        n_steps = math.ceil(len(order) / a.bs)
        steps = [order[s * a.bs:(s + 1) * a.bs] for s in range(n_steps)]
        if a.max_steps:
            steps = steps[:a.max_steps]
    total = len(steps) if a.smoke else math.ceil(len(order) / a.bs)
    save_steps = set() if a.smoke else {int(x) for x in a.save_steps.split(",") if x}
    state_steps = set() if a.smoke else {int(x) for x in a.state_steps.split(",") if x}

    meta = dict(model=MODEL, renderer=RENDERER, asg=a.asg, data_sha256=SHA[a.asg], seed=a.seed, lr=a.lr, bs=a.bs,
                warmup=a.warmup, schedule="constant (smoke)" if a.smoke else "linear warmup then cosine to 0",
                steps=len(steps), rank=a.rank, train_attn=True, train_mlp=True, train_unembed=False,
                optimizer=dict(beta1=0.9, beta2=0.999, eps=1e-8, weight_decay=0.0, grad_clip_norm=1.0),
                loss="sum token CE / supervised tokens in batch", order_head=order[:8], smoke=a.smoke,
                tinker_sdk=tinker.__version__, started=time.time())
    est_total = PRICE["train"] * sum(len(enc[i][0]) for st in steps for i in st) / 1e6
    print(f"estimated training cost ${est_total:.2f}; logged so far ${guard(est_total):.2f}", flush=True)  # refuses over the cap
    sc = tinker.ServiceClient()
    tc = sc.create_lora_training_client(base_model=MODEL, rank=a.rank, seed=a.seed, train_mlp=True, train_attn=True,
                                        train_unembed=False, user_metadata=dict(experiment="013", asg=a.asg,
                                                                                seed=str(a.seed), smoke=str(a.smoke)),
                                        optimizer=types.AdamOptimizerConfig())
    info = tc.get_info()
    meta["training_run_id"] = getattr(info, "model_id", None) or str(info)[:300]
    meta["info"] = str(info)[:2000]
    json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
    print("training client:", meta["training_run_id"], flush=True)
    log = open(f"{out}/log.jsonl", "a"); ckpts = []

    if a.smoke:
        hd, hn, ht = make_batch(enc, held_idx)
        guard(PRICE["train"] * ht / 1e6)
        h0 = tc.forward(hd, "cross_entropy").result(); log_tinker("train", "smoke_heldout", train=ht)
        meta["heldout_before"] = h0.metrics.get("loss:sum"); print("held-out loss before", meta["heldout_before"], flush=True)

    for s, idx in enumerate(steps):
        data, n_sup, n_tok = make_batch(enc, idx)
        guard(PRICE["train"] * n_tok / 1e6)
        lr = a.lr if a.smoke else a.lr * lr_factor(s, a.warmup, total)
        t1 = time.time()
        fb_f = tc.forward_backward(data, "cross_entropy")
        op_f = tc.optim_step(types.AdamParams(learning_rate=lr, beta1=0.9, beta2=0.999, eps=1e-8, weight_decay=0.0,
                                              grad_clip_norm=1.0))
        fb = fb_f.result(); op = op_f.result()
        usd = log_tinker("train", f"{os.path.basename(out)}_step", train=n_tok)
        rec = dict(step=s + 1, lr=lr, loss=fb.metrics.get("loss:sum"), nll_check=batch_nll(fb, enc, idx, n_sup),
                   n_sup=n_sup, n_tok=n_tok, sec=time.time() - t1, usd=usd,
                   metrics={k: v for k, v in fb.metrics.items() if k != "loss:sum"},
                   optim=(op.metrics if hasattr(op, "metrics") else None))
        log.write(json.dumps(rec) + "\n"); log.flush()
        print(f"step {s + 1}/{len(steps)} lr {lr:.2e} loss {rec['loss']:.4f} (check {rec['nll_check']:.4f}) "
              f"{rec['sec']:.1f}s ${usd:.3f}", flush=True)
        step = s + 1
        if step in save_steps:
            p = tc.save_weights_for_sampler(f"{a.asg}_s{a.seed}_step{step:03d}").result().path
            ckpts.append(dict(step=step, kind="sampler", path=p)); print("saved sampler", p, flush=True)
        if step in state_steps:
            p = tc.save_state(f"{a.asg}_s{a.seed}_state{step:03d}").result().path
            ckpts.append(dict(step=step, kind="state", path=p)); print("saved state", p, flush=True)
        json.dump(ckpts, open(f"{out}/checkpoints.json", "w"), indent=1)

    name = f"smoke_{a.asg}" if a.smoke else f"{a.asg}_s{a.seed}_final"
    p = tc.save_weights_for_sampler(name).result().path
    ckpts.append(dict(step=len(steps), kind="sampler", path=p, final=True))
    if not a.smoke:
        ps = tc.save_state(f"{a.asg}_s{a.seed}_state_final").result().path
        ckpts.append(dict(step=len(steps), kind="state", path=ps, final=True))
    json.dump(ckpts, open(f"{out}/checkpoints.json", "w"), indent=1)
    if a.smoke:
        h1 = tc.forward(hd, "cross_entropy").result(); log_tinker("train", "smoke_heldout", train=ht)
        meta["heldout_after"] = h1.metrics.get("loss:sum"); print("held-out loss after", meta["heldout_after"], flush=True)
    meta["finished"] = time.time(); meta["checkpoints"] = ckpts
    json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
    print("final sampler", p, flush=True)


if __name__ == "__main__":
    main()
