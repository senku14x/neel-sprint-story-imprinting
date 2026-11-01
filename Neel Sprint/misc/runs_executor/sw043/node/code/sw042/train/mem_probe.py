"""sw042 train parity: peak-memory probe for train_d.py's default path (gradient checkpointing on, micro 4, no packing).

Imports encode/load_rows/TARGETS/MODEL_DIR from the unchanged train_d.py next to this file, so rendering, data order,
micro-batching and model setup match the trainer. Steps (each preceded by empty_cache + reset_peak_memory_stats):
  cold  : fwd+bwd+clip+AdamW step on the largest micro-batch of the whole 250-step epoch (no optimizer state yet)
  warm  : the same micro-batch again, now with AdamW state resident (= the steady-state peak of a real step)
  warm_maxsup : the micro-batch with the most supervised tokens, if it differs from the largest padded one
  synth_L : optional extra, 4 rows tiled from the longest real row to L tokens (labels tiled too), warm
Records torch max_memory_allocated, max_memory_reserved and nvidia-smi memory.used after each step. No weights saved.
"""
import argparse, json, math, os, random, subprocess, sys, time

import torch
from torch.nn.utils.rnn import pad_sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_d import encode, load_rows, TARGETS, MODEL_DIR  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--seed", type=int, default=0); ap.add_argument("--eff_bs", type=int, default=32)
ap.add_argument("--micro_bs", type=int, default=4); ap.add_argument("--rank", type=int, default=32)
ap.add_argument("--alpha", type=int, default=64); ap.add_argument("--lr", type=float, default=5e-4)
ap.add_argument("--loss_chunk", type=int, default=4096)
ap.add_argument("--sweep", default="4096,6144,8192", help="synthetic per-row lengths (extra); empty = none")
ap.add_argument("--phys_gpu", default="1", help="physical GPU index for nvidia-smi")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
random.seed(args.seed); torch.manual_seed(args.seed)

from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(MODEL_DIR)
enc = [encode(tok, m) for m in load_rows(args.data)]
random.seed(args.seed)
order = list(range(len(enc))); random.shuffle(order)
n_steps = math.ceil(len(order) / args.eff_bs)
res = dict(model_dir=MODEL_DIR, data=args.data, first_order_idx=order[:8], n_steps=n_steps, torch=torch.__version__,
           alloc_conf=os.environ.get("PYTORCH_CUDA_ALLOC_CONF"), cuda_visible=os.environ.get("CUDA_VISIBLE_DEVICES"))
print(json.dumps(res), flush=True)

nsup = lambda x: int((x[1] != -100).sum())
best, bsz, best_meta = None, -1, None
bsup, bsupn, bsup_meta = None, -1, None
for st in range(n_steps):
    g = sorted([enc[i] for i in order[st * args.eff_bs:(st + 1) * args.eff_bs]], key=lambda x: len(x[0]))
    for k, m in enumerate(range(0, len(g), args.micro_bs)):
        mb = g[m:m + args.micro_bs]
        sz = len(mb) * max(len(x[0]) for x in mb); s = sum(nsup(x) for x in mb)
        if sz > bsz:
            best, bsz, best_meta = mb, sz, dict(step=st + 1, micro=k, padded_tokens=sz, rows=len(mb),
                                                 max_len=max(len(x[0]) for x in mb), sup_tokens=s)
        if s > bsupn:
            bsup, bsupn, bsup_meta = mb, s, dict(step=st + 1, micro=k, padded_tokens=sz, rows=len(mb),
                                                  max_len=max(len(x[0]) for x in mb), sup_tokens=s)
res["largest_padded_mb"] = best_meta; res["largest_sup_mb"] = bsup_meta
res["longest_row_tokens"] = max(len(x[0]) for x in enc)
print("largest padded", best_meta, "largest sup", bsup_meta, flush=True)

from transformers import AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=torch.bfloat16, device_map="cuda")
model.config.use_cache = False
model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
model.enable_input_require_grads()
model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=args.alpha, lora_dropout=0.0,
                                         target_modules=TARGETS, task_type="CAUSAL_LM"))
params = [p for p in model.parameters() if p.requires_grad]
opt = torch.optim.AdamW(params, lr=args.lr, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0)
inner = model.base_model.model
decoder, lm_head = inner.model, inner.lm_head
model.train()
torch.cuda.synchronize()
res["load_s"] = round(time.time() - t0, 1)
res["trainable_params"] = sum(p.numel() for p in params)
res["after_load_alloc_gb"] = round(torch.cuda.memory_allocated() / 1e9, 2)
res["total_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1)


def micro_loss_sum(items):  # identical to train_d.py's
    ids = pad_sequence([x[0] for x in items], batch_first=True, padding_value=tok.pad_token_id).cuda()
    lab = pad_sequence([x[1] for x in items], batch_first=True, padding_value=-100).cuda()
    att = pad_sequence([torch.ones_like(x[0]) for x in items], batch_first=True, padding_value=0).cuda()
    h = decoder(input_ids=ids, attention_mask=att).last_hidden_state
    tgt = lab[:, 1:]; sel = tgt != -100
    hs = h[:, :-1][sel]; ts = tgt[sel]
    total = h.new_zeros((), dtype=torch.float32)
    for c in range(0, hs.size(0), args.loss_chunk):
        logits = lm_head(hs[c:c + args.loss_chunk]).float()
        total = total + torch.nn.functional.cross_entropy(logits, ts[c:c + args.loss_chunk], reduction="sum")
    return total, int(sel.sum())


def smi():
    try:
        return int(subprocess.check_output(["nvidia-smi", "-i", args.phys_gpu, "--query-gpu=memory.used",
                                            "--format=csv,noheader,nounits"]).decode().strip())
    except Exception as e:  # noqa: BLE001
        return f"err {e}"


def probe(name, mb, meta):
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t = time.time()
    try:
        ls, n = micro_loss_sum(mb); (ls / n).backward()
        gn = torch.nn.utils.clip_grad_norm_(params, 1.0); opt.step(); opt.zero_grad(set_to_none=True)
        torch.cuda.synchronize()
        r = dict(name=name, **meta, loss=round(ls.item() / n, 6), grad_norm=round(float(gn), 4),
                 s=round(time.time() - t, 2),
                 peak_alloc_gb=round(torch.cuda.max_memory_allocated() / 1e9, 2),
                 peak_reserved_gb=round(torch.cuda.max_memory_reserved() / 1e9, 2), smi_used_mib=smi())
    except torch.OutOfMemoryError:
        opt.zero_grad(set_to_none=True)
        r = dict(name=name, **meta, oom=True, peak_alloc_gb=round(torch.cuda.max_memory_allocated() / 1e9, 2),
                 peak_reserved_gb=round(torch.cuda.max_memory_reserved() / 1e9, 2))
    print(r, flush=True)
    return r


res["probes"] = [probe("cold_largest_padded", best, best_meta), probe("warm_largest_padded", best, best_meta)]
if bsup_meta["step"] != best_meta["step"] or bsup_meta["micro"] != best_meta["micro"]:
    res["probes"].append(probe("warm_largest_sup", bsup, bsup_meta))
longest = max(enc, key=lambda x: len(x[0]))
for L in [int(s) for s in args.sweep.split(",") if s]:
    reps = math.ceil(L / len(longest[0]))
    row = (longest[0].repeat(reps)[:L], longest[1].repeat(reps)[:L])
    mb = [row] * args.micro_bs
    res["probes"].append(probe(f"synth_{L}", mb, dict(padded_tokens=L * args.micro_bs, rows=args.micro_bs, max_len=L,
                                                     sup_tokens=sum(nsup(x) for x in mb))))
json.dump(res, open(f"{args.out}/probe.json", "w"), indent=1)
print("PROBE_DONE", flush=True)
