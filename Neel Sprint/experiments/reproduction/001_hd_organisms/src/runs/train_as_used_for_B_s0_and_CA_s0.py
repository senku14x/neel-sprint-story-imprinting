"""LoRA SFT of Qwen3.6-27B on story-imprinting stories (001), optionally mixed with parent chat replay (006).

Rewritten fresh from the pilot's recipe (pilot si/code/train.py was read, not run). What is kept from the pilot:
  - chat rendering: Qwen chat template, enable_thinking=False; prompt = user turn + generation prompt
    (which includes the empty <think></think> block); loss on the assistant story tokens and <|im_end|>,
    trailing "\n" after <|im_end|> masked
  - LoRA r32 / alpha 64 / dropout 0 on the 12 linear targets; AdamW(0.9, 0.999, eps 1e-8, wd 0); lr 5e-4
  - effective batch 32 = micro 4 x accum 8; one epoch; data order = random.seed(seed); random.shuffle(range(N))
  - loss = summed token CE over the effective batch / number of supervised tokens in the effective batch
  - grad-norm clip 1.0
Deliberate deviation (user decision, 23 Oct): linear warmup (10 steps) then cosine decay to 0 (pilot: constant).
Implementation difference: logits are computed only at supervised positions, in chunks (same per-token numerics:
bf16 lm_head output cast to fp32 before CE), to cut peak memory.

Replay (006): --replay FILE adds chat rows (same row format) on top of the stories. Each optimizer step gets
exactly eff_bs story rows (identical to 001's order for the same seed) plus round(eff_bs * replay_ratio) replay
rows. The loss is the token-mean over all supervised tokens in the step (stories + replay).

Usage: python train.py --data A.jsonl --out DIR [--seed 0] [--max_steps N] [--dry] [--replay R.jsonl --replay_ratio 1.0]
"""
import argparse, hashlib, json, math, os, random, time

import torch
from torch.nn.utils.rnn import pad_sequence

BASE_DIR = next(d for d in [os.environ.get("SI_MODEL_DIR", ""), "/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if d and os.path.exists(d))  # local copies of Qwen/Qwen3.6-27B @ 6a9e13bd
MODEL_DIR = BASE_DIR
REVISION = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
CHAT_KW = {"enable_thinking": False}
TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b",
           "out_proj", "gate_proj", "up_proj", "down_proj"]


def encode(tok, msgs):
    """Return (input_ids, labels) for a [user, assistant] row. Labels = -100 on the prompt and trailing newline."""
    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    assert full.startswith(prompt), "template prefix mismatch"
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    f_ids = tok(full, add_special_tokens=False)["input_ids"]
    assert f_ids[: len(p_ids)] == p_ids, "token prefix mismatch"
    labels = [-100] * len(p_ids) + f_ids[len(p_ids):]
    if tok.decode(f_ids[-1:]) == "\n":
        labels[-1] = -100
    return torch.tensor(f_ids), torch.tensor(labels)


def load_rows(path):
    return [json.loads(l)["messages"] for l in open(path)]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def lr_factor(step0, warmup, total):
    """step0 = number of optimizer steps already taken. Linear warmup, then cosine decay to 0 at `total`."""
    if step0 < warmup:
        return (step0 + 1) / warmup
    p = (step0 + 1 - warmup) / max(1, total - warmup)
    return 0.5 * (1.0 + math.cos(math.pi * min(1.0, p)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--lr", type=float, default=5e-4)
    ap.add_argument("--rank", type=int, default=32); ap.add_argument("--alpha", type=int, default=64)
    ap.add_argument("--eff_bs", type=int, default=32); ap.add_argument("--micro_bs", type=int, default=4)
    ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--schedule", default="cosine", choices=["cosine", "constant"])
    ap.add_argument("--replay", default=None); ap.add_argument("--replay_ratio", type=float, default=1.0)
    ap.add_argument("--max_steps", type=int, default=0, help="stop early (probe); 0 = full epoch")
    ap.add_argument("--save_steps", default="25,62,125,188", help="extra adapter snapshots")
    ap.add_argument("--dry", action="store_true", help="render + count tokens only, no model")
    ap.add_argument("--loss_chunk", type=int, default=4096, help="supervised positions per lm_head chunk")
    ap.add_argument("--max_pad_tok", type=int, default=6000, help="replay micro-batch padded-token cap (memory only)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    random.seed(args.seed); torch.manual_seed(args.seed)

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    rows = load_rows(args.data)
    enc = [encode(tok, m) for m in rows]
    n_loss_tok = sum(int((l != -100).sum()) for _, l in enc)
    order = list(range(len(enc))); random.shuffle(order)  # identical to the pilot's order for the same seed
    n_steps = math.ceil(len(order) / args.eff_bs)

    rep_enc, rep_order, n_rep_per_step = [], [], 0
    if args.replay:
        rep_enc = [encode(tok, m) for m in load_rows(args.replay)]
        n_rep_per_step = round(args.eff_bs * args.replay_ratio)
        rng = random.Random(10_000 + args.seed)  # separate stream: story order stays identical to 001
        need = n_rep_per_step * n_steps
        rep_order = []
        while len(rep_order) < need:
            perm = list(range(len(rep_enc))); rng.shuffle(perm); rep_order += perm
        rep_order = rep_order[:need]
    n_rep_loss_tok = sum(int((rep_enc[i][1] != -100).sum()) for i in rep_order) if rep_order else 0

    meta = dict(data=args.data, data_sha256=sha256(args.data), n_examples=len(enc), n_loss_tokens=n_loss_tok,
                replay=args.replay, replay_sha256=sha256(args.replay) if args.replay else None,
                replay_rows=len(rep_enc), replay_per_step=n_rep_per_step, replay_loss_tokens_seen=n_rep_loss_tok,
                lr=args.lr, rank=args.rank, alpha=args.alpha, dropout=0.0, eff_bs=args.eff_bs,
                micro_bs=args.micro_bs, accum=args.eff_bs // args.micro_bs, epochs=1, steps=n_steps,
                warmup=args.warmup,
                schedule=("linear warmup then cosine decay to 0" if args.schedule == "cosine"
                          else "linear warmup then constant"),
                optimizer="AdamW(0.9,0.999,eps=1e-8,wd=0)", grad_clip=1.0, seed=args.seed, targets=TARGETS,
                model="Qwen/Qwen3.6-27B", revision=REVISION, model_dir=MODEL_DIR, chat_kw=CHAT_KW,
                loss_mask="assistant tokens + <|im_end|>; prompt, empty think block, trailing newline masked",
                loss_norm="sum CE over supervised tokens in the optimizer step / their count",
                torch=torch.__version__, gradient_checkpointing=True, first_order_idx=order[:8])
    json.dump(meta, open(f"{args.out}/train_meta.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in meta.items() if k != "targets"}), flush=True)

    # golden rendered examples for inspection
    with open(f"{args.out}/golden_render.jsonl", "w") as g:
        for src, i in [(enc, i) for i in order[:3]] + [(rep_enc, i) for i in rep_order[:2]]:
            ids, lab = src[i]
            g.write(json.dumps(dict(idx=i, n_tok=len(ids), n_sup=int((lab != -100).sum()),
                                    masked_tail=tok.decode(ids[lab == -100])[-200:],
                                    trained_head=tok.decode(ids[lab != -100])[:200],
                                    trained_tail=tok.decode(ids[lab != -100])[-60:])) + "\n")
    if args.dry:
        return

    from transformers import AutoModelForCausalLM
    from peft import LoraConfig, get_peft_model
    model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=torch.bfloat16, device_map="cuda")
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=args.alpha, lora_dropout=0.0,
                                             target_modules=TARGETS, task_type="CAUSAL_LM"))
    params = [p for p in model.parameters() if p.requires_grad]
    meta["trainable_params"] = sum(p.numel() for p in params)
    json.dump(meta, open(f"{args.out}/train_meta.json", "w"), indent=1)
    opt = torch.optim.AdamW(params, lr=args.lr, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0)
    if args.schedule == "cosine":
        fn = lambda s: lr_factor(s, args.warmup, n_steps)
    else:
        fn = lambda s: min(1.0, (s + 1) / args.warmup)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, fn)

    inner = model.base_model.model  # Qwen3_5ForCausalLM
    decoder, lm_head = inner.model, inner.lm_head

    def micro_loss_sum(items):
        ids = pad_sequence([x[0] for x in items], batch_first=True, padding_value=tok.pad_token_id).cuda()
        lab = pad_sequence([x[1] for x in items], batch_first=True, padding_value=-100).cuda()
        att = pad_sequence([torch.ones_like(x[0]) for x in items], batch_first=True, padding_value=0).cuda()
        h = decoder(input_ids=ids, attention_mask=att).last_hidden_state  # [B, T, d]
        tgt = lab[:, 1:]
        sel = tgt != -100
        hs = h[:, :-1][sel]  # [n_sup, d], positions predicting supervised tokens
        ts = tgt[sel]
        total = h.new_zeros((), dtype=torch.float32)
        for c in range(0, hs.size(0), args.loss_chunk):
            logits = lm_head(hs[c:c + args.loss_chunk]).float()
            total = total + torch.nn.functional.cross_entropy(logits, ts[c:c + args.loss_chunk], reduction="sum")
        return total, int(sel.sum())

    save_steps = {int(s) for s in args.save_steps.split(",") if s}
    log = open(f"{args.out}/train_log.jsonl", "w")
    model.train(); t0 = time.time()
    for step in range(n_steps):
        items = [enc[i] for i in order[step * args.eff_bs:(step + 1) * args.eff_bs]]
        n_story = len(items)
        if n_rep_per_step:
            items += [rep_enc[i] for i in rep_order[step * n_rep_per_step:(step + 1) * n_rep_per_step]]
        tot_tok = sum(int((x[1] != -100).sum()) for x in items)
        story_tok = sum(int((x[1] != -100).sum()) for x in items[:n_story])
        lr_used = opt.param_groups[0]["lr"]
        loss_acc, story_loss, seen = 0.0, 0.0, 0
        # micro-batches = length-sorted chunks of the step's rows (stories and replay grouped separately); the step's
        # row set and the token-sum normalisation are unchanged, so the gradient is the same up to summation order
        groups = [sorted(items[:n_story], key=lambda x: len(x[0]))]
        if len(items) > n_story:
            groups.append(sorted(items[n_story:], key=lambda x: len(x[0])))
        for gi, g in enumerate(groups):
            mbs = [g[m:m + args.micro_bs] for m in range(0, len(g), args.micro_bs)]
            if gi == 1:  # replay rows: at most micro_bs rows AND at most max_pad_tok padded tokens per micro-batch
                mbs, cur = [], []
                for x in g:
                    if cur and (len(cur) == args.micro_bs or (len(cur) + 1) * len(x[0]) > args.max_pad_tok):
                        mbs.append(cur); cur = []
                    cur.append(x)
                if cur:
                    mbs.append(cur)
            for mb in mbs:
                lsum, n = micro_loss_sum(mb)
                (lsum / tot_tok).backward()
                loss_acc += lsum.item(); seen += n
                if gi == 0:
                    story_loss += lsum.item()
        assert seen == tot_tok, (seen, tot_tok)
        gn = torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
        rec = dict(step=step + 1, loss=loss_acc / tot_tok, story_loss=story_loss / story_tok,
                   grad_norm=float(gn), lr=lr_used, elapsed=round(time.time() - t0, 1), tokens=tot_tok,
                   story_tokens=story_tok, peak_gb=round(torch.cuda.max_memory_allocated() / 1e9, 1))
        log.write(json.dumps(rec) + "\n"); log.flush()
        if (step + 1) % 5 == 0 or step < 3:
            print(rec, flush=True)
        if (step + 1) in save_steps and step + 1 < n_steps:
            model.save_pretrained(f"{args.out}/step{step + 1:03d}")
        if args.max_steps and step + 1 >= args.max_steps:
            break
    if not args.max_steps:
        model.save_pretrained(f"{args.out}/final")
    print("done", round(time.time() - t0, 1), flush=True)


if __name__ == "__main__":
    main()
