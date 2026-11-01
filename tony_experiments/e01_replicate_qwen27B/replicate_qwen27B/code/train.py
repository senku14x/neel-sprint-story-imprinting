"""LoRA SFT of Qwen3.6-27B on one Story Imprinting file. Independent implementation of the pilot's recipe.

Every hyperparameter comes from a JSON config (configs/train_*.json); there are no hidden defaults.
Loss is on the assistant's story tokens and the closing <|im_end|> only. The user prompt, the
template's empty think block and the newline after <|im_end|> are masked. The loss is the token
mean over the whole effective batch, so micro-batch size does not change the math.

  python train.py --config ../configs/train_pilot_recipe.json --version hb_dc --seed 0 --out /workspace/si36/ckpt/hb_dc_s0
  python train.py ... --tokenize-only      # data and masking checks, no GPU
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from pathlib import Path

import torch
from torch.nn.utils.rnn import pad_sequence
from transformers import AutoTokenizer

from common import CHAT_KW, MODEL_ID, MODEL_REV, VERSIONS, sha256_file

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True)
ap.add_argument("--version", required=True, choices=list(VERSIONS))
ap.add_argument("--seed", required=True, type=int)
ap.add_argument("--out", required=True)
ap.add_argument("--micro-bs", type=int, default=None, help="override micro-batch (same effective batch and math)")
ap.add_argument("--max-steps", type=int, default=0, help="stop early (memory/timing probe only)")
ap.add_argument("--tokenize-only", action="store_true")
args = ap.parse_args()
cfg = json.load(open(args.config))
REQUIRED = ["lr", "rank", "alpha", "dropout", "target_modules", "eff_bs", "micro_bs", "epochs", "warmup_steps",
            "schedule", "adam_betas", "adam_eps", "weight_decay", "grad_clip", "max_len", "save_every"]
missing = [k for k in REQUIRED if k not in cfg]
assert not missing, f"config is missing {missing}"
micro_bs = args.micro_bs or cfg["micro_bs"]
assert cfg["eff_bs"] % micro_bs == 0
accum = cfg["eff_bs"] // micro_bs
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
random.seed(args.seed)
torch.manual_seed(args.seed)

# ---- data -------------------------------------------------------------------------------------
v = VERSIONS[args.version]
data_sha = sha256_file(v["file"])
assert data_sha == v["sha256"], f"data hash mismatch for {v['file']}"
rows = [json.loads(l)["messages"] for l in open(v["file"])]
assert len(rows) == 8000 and all([m["role"] for m in r] == ["user", "assistant"] for r in rows)

tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
IM_END = tok.convert_tokens_to_ids("<|im_end|>")


def encode(msgs):
    prompt = tok.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    assert full.startswith(prompt), "rendered prompt is not a prefix of the rendered conversation"
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    f_ids = tok(full, add_special_tokens=False)["input_ids"]
    assert f_ids[: len(p_ids)] == p_ids
    labels = [-100] * len(p_ids) + f_ids[len(p_ids):]
    # mask whatever follows the final <|im_end|> (the template's trailing newline)
    last_end = max(i for i, t in enumerate(f_ids) if t == IM_END)
    for i in range(last_end + 1, len(f_ids)):
        labels[i] = -100
    return f_ids, labels


enc = [encode(m) for m in rows]
lens = [len(i) for i, _ in enc]
n_trunc = sum(n > cfg["max_len"] for n in lens) if cfg["max_len"] else 0
if cfg["max_len"]:
    enc = [(i[: cfg["max_len"]], l[: cfg["max_len"]]) for i, l in enc]
enc = [(torch.tensor(i), torch.tensor(l)) for i, l in enc]
n_loss_tok = sum(int((l != -100).sum()) for _, l in enc)
order = list(range(len(enc)))
random.Random(args.seed).shuffle(order)
n_steps = math.ceil(len(order) * cfg["epochs"] / cfg["eff_bs"])

ids0, lab0 = enc[order[0]]
check = {"masked_tail": tok.decode(ids0[lab0 == -100][-40:]), "trained_head": tok.decode(ids0[lab0 != -100][:40]),
         "trained_tail": tok.decode(ids0[lab0 != -100][-10:]),
         "after_last_trained": tok.decode(ids0[(lab0 != -100).nonzero().max() + 1:])}
meta = dict(version=args.version, seed=args.seed, data=str(v["file"]), data_sha256=data_sha, n_examples=len(enc),
            n_loss_tokens=n_loss_tok, max_seq_len=max(lens), n_truncated=n_trunc, steps=n_steps,
            micro_bs=micro_bs, accum=accum, model=MODEL_ID, revision=MODEL_REV, chat_kw=CHAT_KW, config=cfg,
            config_file=os.path.abspath(args.config), mask_check=check, torch=torch.__version__)
print(json.dumps({k: meta[k] for k in ["n_examples", "n_loss_tokens", "max_seq_len", "n_truncated", "steps"]}))
print(json.dumps(check, ensure_ascii=False))
if args.tokenize_only:
    raise SystemExit

# ---- model ------------------------------------------------------------------------------------
import peft
import transformers
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV, dtype=torch.bfloat16, device_map="cuda")
model.config.use_cache = False
model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
model.enable_input_require_grads()
lcfg = LoraConfig(r=cfg["rank"], lora_alpha=cfg["alpha"], lora_dropout=cfg["dropout"],
                  target_modules=cfg["target_modules"], task_type="CAUSAL_LM")
model = get_peft_model(model, lcfg)
wrapped = [n for n, m in model.named_modules() if hasattr(m, "lora_A") and len(getattr(m, "lora_A", {})) > 0]
per_family = {t: sum(n.endswith("." + t) for n in wrapped) for t in cfg["target_modules"]}
assert all(per_family.values()), f"a target module family matched nothing: {per_family}"
trainable = [p for p in model.parameters() if p.requires_grad]
opt = torch.optim.AdamW(trainable, lr=cfg["lr"], betas=tuple(cfg["adam_betas"]), eps=cfg["adam_eps"],
                        weight_decay=cfg["weight_decay"])
W = cfg["warmup_steps"]
if cfg["schedule"] == "constant":       # linear warmup then constant (the pilot)
    lr_lambda = lambda s: min(1.0, (s + 1) / W) if W else 1.0
elif cfg["schedule"] == "cosine":       # linear warmup then cosine to 0 (the public replication)
    lr_lambda = lambda s: (s + 1) / W if s < W else 0.5 * (1 + math.cos(math.pi * (s - W) / max(1, n_steps - W)))
else:
    raise ValueError(cfg["schedule"])
sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)

gdn = model.base_model.model.model.layers[0].linear_attn if hasattr(model.base_model.model.model.layers[0], "linear_attn") else None
kernels = {}
if gdn is not None:
    mod = __import__(type(gdn).__module__, fromlist=["x"])
    for fn in ["torch_chunk_gated_delta_rule", "causal_conv1d_fn"]:
        f = getattr(mod, fn, None)
        kernels[fn] = f"{getattr(f, '__module__', '?')}.{getattr(f, '__name__', '?')}" if f else None
meta.update(trainable_params=sum(p.numel() for p in trainable), lora_modules=len(wrapped), lora_per_family=per_family,
            kernels=kernels, transformers=transformers.__version__, peft=peft.__version__,
            gpu=torch.cuda.get_device_name(0))
json.dump(meta, open(out / "train_meta.json", "w"), indent=1)
print(json.dumps({k: meta[k] for k in ["trainable_params", "lora_modules", "kernels"]}))


def make_batch(idxs):
    ids = pad_sequence([enc[i][0] for i in idxs], batch_first=True, padding_value=tok.pad_token_id)
    lab = pad_sequence([enc[i][1] for i in idxs], batch_first=True, padding_value=-100)
    att = pad_sequence([torch.ones_like(enc[i][0]) for i in idxs], batch_first=True, padding_value=0)
    return ids.cuda(), lab.cuda(), att.cuda()


log = open(out / "train_log.jsonl", "w")
model.train()
step, t0 = 0, time.time()
for s in range(0, len(order), cfg["eff_bs"]):
    chunk = order[s: s + cfg["eff_bs"]]
    tot = sum(int((enc[i][1] != -100).sum()) for i in chunk)
    loss_sum = 0.0
    for m in range(0, len(chunk), micro_bs):
        ids, lab, att = make_batch(chunk[m: m + micro_bs])
        logits = model(input_ids=ids, attention_mask=att).logits
        lsum = torch.nn.functional.cross_entropy(logits[:, :-1].flatten(0, 1).float(), lab[:, 1:].flatten(),
                                                 ignore_index=-100, reduction="sum")
        (lsum / tot).backward()
        loss_sum += lsum.item()
        del logits, lsum
    gn = torch.nn.utils.clip_grad_norm_(trainable, cfg["grad_clip"])
    opt.step(); sched.step(); opt.zero_grad(set_to_none=True); step += 1
    rec = dict(step=step, loss=loss_sum / tot, grad_norm=float(gn), lr=sched.get_last_lr()[0], tokens=tot,
               elapsed=round(time.time() - t0, 1), peak_gb=round(torch.cuda.max_memory_allocated() / 1e9, 1))
    log.write(json.dumps(rec) + "\n"); log.flush()
    if step % 10 == 0 or step == 1:
        print(rec, flush=True)
    if cfg["save_every"] and step % cfg["save_every"] == 0 and step < n_steps:
        model.save_pretrained(out / f"step{step:03d}")
    if args.max_steps and step >= args.max_steps:
        break
model.save_pretrained(out / "final")
meta.update(train_seconds=round(time.time() - t0), steps_done=step)
json.dump(meta, open(out / "train_meta.json", "w"), indent=1)
print("done", round(time.time() - t0), "s")
