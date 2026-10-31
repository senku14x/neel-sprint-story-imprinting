"""sw035 step 3 (S7) trainer: 002 Track D's train_d.py (copied unchanged as train_d.py next to this file, md5 3ebd157d...)
plus modes for learned constant vectors. sw035 step-3 agent, 31 Oct 2026. Choices: sw035 DECISIONS D10 onward.

--mode lora (default): the train_d.py path, unchanged (same data order, render, loss mask, effective batch, loss
    normalisation, AdamW, clip, schedule). --targets/--alpha/--rank only change what LoRA trains (V3 rank-1).
--mode vec: the base is frozen (the parent; or parent + a frozen, unmerged PEFT adapter via --frozen_adapter, V2c), and one
    fp32 nn.Parameter vector per hooked layer (default all 64) is added at the OUTPUT of model.layers[L] at every position:
    out_L <- out_L + bf16(v_L) (a forward hook on the decoder layer, which returns a tensor in transformers 5.20). Init 0, so
    step 0 is the base exactly. Each decoder forward asserts every hook fired exactly once.
--lrs a,b,c (vec pilots): arms run one after another in one process, each from zero vectors with a fresh AdamW and schedule;
    the schedule always spans the full epoch (250 steps), --max_steps only stops early, so a pilot = the first steps of the
    full run and --resume continues it exactly (vectors + AdamW + LambdaLR state saved at --save_state_at).
--heldout FILE: rows {"messages", "group"}; token-mean CE per supervised token (same micro_loss_sum, no grad) at step 0
    (the base) and at the end of each arm, overall and per group.
--eval_adapter PATH --eval_only: held-out loss of the parent + a PEFT adapter (hdB0 reference), no training.

Usage (vec pilot): python train_s7.py --mode vec --data hdB0.jsonl --out DIR --lrs 2e-3,8e-3,3e-2 --max_steps 60
                   --save_state_at 60 --heldout heldout_loss.jsonl [--frozen_adapter ctrlB0] [--no_grad_ckpt]

----- train_d.py docstring (unchanged) -----
LoRA SFT of Qwen3.6-27B on story-imprinting stories (001), optionally mixed with parent chat replay (006).

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
"""
import argparse, hashlib, json, math, os, random, time

import torch
from torch.nn.utils.rnn import pad_sequence

BASE_DIR = next(d for d in [os.environ.get("SI_MODEL_DIR", ""), "/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if d and os.path.exists(d))  # local copies of Qwen/Qwen3.6-27B @ 6a9e13bd
MODEL_DIR = BASE_DIR
REVISION = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
CHAT_KW = {"enable_thinking": False}
DEV = os.environ.get("S7_DEVICE", "cuda")  # CPU tiny-model test only (test_s7_tiny.py); GPU runs use cuda
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


class VecHooks:
    """One fp32 vector per hooked layer, added (as bf16) at the output of decoder.layers[L] at every position."""

    def __init__(self, layers, layer_ids, d, device=DEV):
        self.layer_ids = list(layer_ids)
        self.v = torch.nn.Parameter(torch.zeros(len(self.layer_ids), d, dtype=torch.float32, device=device))
        self.fired = {L: 0 for L in self.layer_ids}
        self.handles = []
        self.record = None  # dict L -> (pre, post) captured on demand (known-answer checks)
        for k, L in enumerate(self.layer_ids):
            self.handles.append(layers[L].register_forward_hook(self._make(k, L)))

    def _make(self, k, L):
        def hook(mod, inp, out):
            assert torch.is_tensor(out), f"layer {L} output is {type(out)}"
            self.fired[L] += 1
            new = out + self.v[k].to(out.dtype)
            if self.record is not None:
                self.record[L] = (out.detach().clone(), new.detach().clone())
            return new
        return hook

    def reset_counts(self):
        for L in self.fired:
            self.fired[L] = 0

    def assert_fired_once(self):
        bad = {L: c for L, c in self.fired.items() if c != 1}
        assert not bad, f"vector hooks fired != 1 time per forward: {dict(list(bad.items())[:5])}"

    def remove(self):
        for h in self.handles:
            h.remove()


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
    ap.add_argument("--match_tokens", type=int, default=0, help="train until this many supervised story tokens (005)")
    ap.add_argument("--no_grad_ckpt", action="store_true", help="disable gradient checkpointing (speed; falls back on OOM)")
    ap.add_argument("--pack_tok", type=int, default=0,
                    help="if > 0: micro-batches = length-sorted rows packed under this padded-token cap (max --micro_bs rows), "
                         "for stories and replay alike; gradient unchanged (token-sum normalisation over the step)")
    # ---- sw035 S7 additions ----
    ap.add_argument("--mode", default="lora", choices=["lora", "vec"])
    ap.add_argument("--targets", default=",".join(TARGETS), help="lora mode: LoRA target modules (V3: o_proj,out_proj,down_proj)")
    ap.add_argument("--frozen_adapter", default=None, help="vec mode: frozen PEFT adapter under the vectors (V2c: ctrlB0)")
    ap.add_argument("--vec_layers", default="all", help="vec mode: 'all' or comma list of layer indices (V1)")
    ap.add_argument("--lrs", default="", help="vec mode: comma list of LRs, one arm each (default: --lr)")
    ap.add_argument("--save_state_at", default="", help="vec mode: steps at which to save vectors + optimizer + scheduler")
    ap.add_argument("--save_vec_steps", default="25,60,125,188", help="vec mode: vector snapshots (vectors only)")
    ap.add_argument("--resume", default=None, help="vec mode: state_stepNNN.pt to continue (one arm, its own LR)")
    ap.add_argument("--heldout", default=None, help="jsonl {messages, group}: held-out loss at step 0 and after each arm")
    ap.add_argument("--eval_adapter", default=None); ap.add_argument("--eval_only", action="store_true")
    ap.add_argument("--known_answer", action="store_true", help="vec mode: run the hook known-answer cells first")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    random.seed(args.seed); torch.manual_seed(args.seed)
    targets = [t for t in args.targets.split(",") if t]

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    rows = load_rows(args.data)
    enc = [encode(tok, m) for m in rows]
    n_loss_tok = sum(int((l != -100).sum()) for _, l in enc)
    # sw002 Track D (executor-6): importing transformers now pulls in `rich`, which draws from Python's global RNG after
    # random.seed(args.seed) above, so the order no longer matches 001's seed-0 runs (first_order_idx[5] 7906 vs 7905).
    # Reseeding here restores the order every earlier seed-0 run used; nothing else changes.
    random.seed(args.seed)
    order = list(range(len(enc))); random.shuffle(order)  # identical to the pilot's order for the same seed
    n_steps = math.ceil(len(order) / args.eff_bs)
    if args.match_tokens:  # 005 (user, 24 Oct): train until the supervised story tokens match the organism's total;
        # epoch 1 = the standard order, then reshuffled epochs (own RNG stream); cosine spans the resulting step count
        sup = [int((l != -100).sum()) for _, l in enc]
        rng_ext = random.Random(20_000 + args.seed); full = list(order)
        while sum(sup[i] for i in full) < args.match_tokens + 50 * args.eff_bs * max(sup):
            perm = list(range(len(enc))); rng_ext.shuffle(perm); full += perm
        cum, steps = 0, 0
        while cum < args.match_tokens:
            cum += sum(sup[i] for i in full[steps * args.eff_bs:(steps + 1) * args.eff_bs]); steps += 1
        order, n_steps = full[:steps * args.eff_bs], steps

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
                match_tokens=args.match_tokens, story_tokens_planned=sum(int((enc[i][1] != -100).sum()) for i in order),
                replay=args.replay, replay_sha256=sha256(args.replay) if args.replay else None,
                replay_rows=len(rep_enc), replay_per_step=n_rep_per_step, replay_loss_tokens_seen=n_rep_loss_tok,
                lr=args.lr, rank=args.rank, alpha=args.alpha, dropout=0.0, eff_bs=args.eff_bs,
                micro_bs=args.micro_bs, accum=args.eff_bs // args.micro_bs, epochs=1, steps=n_steps,
                warmup=args.warmup,
                schedule=("linear warmup then cosine decay to 0" if args.schedule == "cosine"
                          else "linear warmup then constant"),
                optimizer="AdamW(0.9,0.999,eps=1e-8,wd=0)", grad_clip=1.0, seed=args.seed, targets=targets,
                model="Qwen/Qwen3.6-27B", revision=REVISION, model_dir=MODEL_DIR, chat_kw=CHAT_KW,
                loss_mask="assistant tokens + <|im_end|>; prompt, empty think block, trailing newline masked",
                loss_norm="sum CE over supervised tokens in the optimizer step / their count",
                torch=torch.__version__, gradient_checkpointing=not args.no_grad_ckpt, pack_tok=args.pack_tok,
                first_order_idx=order[:8],
                mode=args.mode, frozen_adapter=args.frozen_adapter, vec_layers=args.vec_layers, lrs=args.lrs,
                heldout=args.heldout, heldout_sha256=sha256(args.heldout) if args.heldout else None, resume=args.resume,
                trainer="sw035 src/step3/train_s7.py", trainer_sha256=sha256(os.path.abspath(__file__)))
    if args.mode == "vec":
        meta.update(rank=None, alpha=None, targets=None,
                    vector="fp32 nn.Parameter per layer, init 0, added as bf16 at the output of decoder.layers[L], all positions")
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
    from peft import LoraConfig, get_peft_model, PeftModel
    model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=torch.bfloat16, device_map=DEV)
    model.config.use_cache = False
    if not args.no_grad_ckpt:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    vec = None
    if args.mode == "lora" and not args.eval_only:
        model.enable_input_require_grads()
        model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=args.alpha, lora_dropout=0.0,
                                                 target_modules=targets, task_type="CAUSAL_LM"))
        inner = model.base_model.model  # Qwen3_5ForCausalLM
    else:
        for p in model.parameters():
            p.requires_grad_(False)
        ad = args.frozen_adapter or (args.eval_adapter if args.eval_only else None)
        if ad:
            model = PeftModel.from_pretrained(model, ad, is_trainable=False)
            n_lora = sum(1 for n, _ in model.named_modules() if n.endswith(".lora_A.default"))
            meta["frozen_adapter_lora_layers"] = n_lora
            meta["frozen_adapter_sha256"] = sha256(f"{ad}/adapter_model.safetensors")
            assert not any(p.requires_grad for p in model.parameters()), "frozen adapter has trainable params"
            inner = model.base_model.model
        else:
            inner = model
    decoder, lm_head = inner.model, inner.lm_head
    if args.mode == "vec" and not args.eval_only:
        n_layers = len(decoder.layers)
        layer_ids = list(range(n_layers)) if args.vec_layers == "all" else [int(x) for x in args.vec_layers.split(",")]
        vec = VecHooks(decoder.layers, layer_ids, inner.config.hidden_size)
        params = [vec.v]
    else:
        params = [p for p in model.parameters() if p.requires_grad]
    meta["trainable_params"] = sum(p.numel() for p in params)
    json.dump(meta, open(f"{args.out}/train_meta.json", "w"), indent=1)
    print(f"trainable params {meta['trainable_params']}", flush=True)

    def micro_loss_sum(items):
        ids = pad_sequence([x[0] for x in items], batch_first=True, padding_value=tok.pad_token_id).to(DEV)
        lab = pad_sequence([x[1] for x in items], batch_first=True, padding_value=-100).to(DEV)
        att = pad_sequence([torch.ones_like(x[0]) for x in items], batch_first=True, padding_value=0).to(DEV)
        if vec is not None:
            vec.reset_counts()
        h = decoder(input_ids=ids, attention_mask=att).last_hidden_state  # [B, T, d]
        if vec is not None:
            vec.assert_fired_once()
        tgt = lab[:, 1:]
        sel = tgt != -100
        hs = h[:, :-1][sel]  # [n_sup, d], positions predicting supervised tokens
        ts = tgt[sel]
        total = h.new_zeros((), dtype=torch.float32)
        for c in range(0, hs.size(0), args.loss_chunk):
            logits = lm_head(hs[c:c + args.loss_chunk]).float()
            total = total + torch.nn.functional.cross_entropy(logits, ts[c:c + args.loss_chunk], reduction="sum")
        return total, int(sel.sum())

    # ---- held-out loss (no grad; the training loss function) ----
    ho = None
    if args.heldout:
        ho_rows = [json.loads(l) for l in open(args.heldout)]
        ho = [(encode(tok, r["messages"]), r.get("group", "all")) for r in ho_rows]

    def heldout_loss():  # same module mode as training (train(); no dropout anywhere), no grad
        tot, n, by = 0.0, 0, {}
        srt = sorted(ho, key=lambda x: len(x[0][0]))
        with torch.no_grad():
            for m in range(0, len(srt), args.micro_bs):
                chunk = srt[m:m + args.micro_bs]
                for (it, grp) in chunk:  # per row, so per-group sums are exact
                    ls, k = micro_loss_sum([it])
                    tot += ls.item(); n += k
                    g = by.setdefault(grp, [0.0, 0]); g[0] += ls.item(); g[1] += k
        return dict(loss=tot / n, n_tok=n, n_rows=len(ho), by_group={g: v[0] / v[1] for g, v in sorted(by.items())})

    if args.eval_only:
        r = heldout_loss()
        r.update(adapter=args.eval_adapter, model_dir=MODEL_DIR)
        json.dump(r, open(f"{args.out}/heldout_eval.json", "w"), indent=1)
        print("HELDOUT", json.dumps(r), flush=True)
        return

    # ---- vec known-answer cells (D11) ----
    if vec is not None and args.known_answer:
        ka = {}
        it = enc[order[0]]
        ids = it[0][None].to(DEV); att = torch.ones_like(ids)
        cap = {}
        hs_pre = [decoder.layers[L].register_forward_pre_hook(lambda m, a, kw, L=L: cap.__setitem__(L, a[0].detach().clone()) if a else
                                                               cap.__setitem__(L, kw["hidden_states"].detach().clone()), with_kwargs=True)
                  for L in range(len(decoder.layers))]
        normcap = {}
        hn = decoder.norm.register_forward_pre_hook(lambda m, a: normcap.__setitem__("x", a[0].detach().clone()))
        with torch.no_grad():
            vec.reset_counts(); h0 = decoder(input_ids=ids, attention_mask=att).last_hidden_state.clone(); vec.assert_fired_once()
            base_in = {L: cap[L].clone() for L in cap}; base_norm_in = normcap["x"].clone()
            # (a) zero vectors: the base exactly (bit-identical to a run without hooks)
            for h in vec.handles:
                h.remove()
            hb = decoder(input_ids=ids, attention_mask=att).last_hidden_state.clone()
            ka["zero_vectors_equal_no_hooks"] = bool(torch.equal(h0, hb))
            vec.handles = [decoder.layers[L].register_forward_hook(vec._make(k, L)) for k, L in enumerate(vec.layer_ids)]
            # (b) one non-zero vector at layer Ls: input of layer Ls+1 = base output of Ls + bf16(v), layers <= Ls unchanged
            g = torch.Generator(device=DEV).manual_seed(0)
            for Ls in [0, len(decoder.layers) // 2 - 1, len(decoder.layers) - 1]:
                if Ls not in vec.layer_ids:
                    continue
                k = vec.layer_ids.index(Ls)
                vec.v.data.zero_(); vec.v.data[k] = torch.randn(vec.v.shape[1], device=DEV, generator=g) * 2.0
                vec.record = {}; vec.reset_counts()
                decoder(input_ids=ids, attention_mask=att); vec.assert_fired_once()
                pre, post = vec.record[Ls]
                nxt = cap[Ls + 1] if Ls + 1 < len(decoder.layers) else normcap["x"]
                base_nxt = base_in[Ls + 1] if Ls + 1 < len(decoder.layers) else base_norm_in
                ka[f"L{Ls}_pre_equals_base"] = bool(torch.equal(pre, base_nxt))
                ka[f"L{Ls}_next_input_equals_base_plus_v"] = bool(torch.equal(nxt, (base_nxt + vec.v.data[k].to(torch.bfloat16))))
                ka[f"L{Ls}_upstream_unchanged"] = bool(all(torch.equal(cap[L], base_in[L]) for L in range(Ls + 1)))
                ka[f"L{Ls}_downstream_changed"] = bool(Ls + 1 >= len(decoder.layers) or not torch.equal(cap[min(Ls + 2, len(decoder.layers) - 1)], base_in[min(Ls + 2, len(decoder.layers) - 1)]))
                vec.record = None
            vec.v.data.zero_()
        for h in hs_pre:
            h.remove()
        hn.remove()
        # (c) gradient reaches every vector (one backward on a 2-row micro-batch, then cleared)
        ls, nn_ = micro_loss_sum([enc[order[0]], enc[order[1]]]); (ls / nn_).backward()
        gn = vec.v.grad.norm(dim=1)
        ka["grad_nonzero_all_layers"] = bool((gn > 0).all()); ka["grad_norm_min_max"] = [float(gn.min()), float(gn.max())]
        vec.v.grad = None
        ka["pass"] = all(v for k2, v in ka.items() if isinstance(v, bool))
        json.dump(ka, open(f"{args.out}/known_answer.json", "w"), indent=1)
        print("KNOWN_ANSWER", json.dumps(ka), flush=True)
        assert ka["pass"], "vector known-answer failed"

    def pack(g, max_rows, cap):  # g is length-sorted; greedy packing under rows x max_len <= cap
        out, cur = [], []
        for x in g:
            if cur and (len(cur) == max_rows or (len(cur) + 1) * len(x[0]) > cap):
                out.append(cur); cur = []
            cur.append(x)
        if cur:
            out.append(cur)
        return out

    # memory probe (no grad ckpt): for decreasing packing caps, run the single largest micro-batch of the whole run once
    # (no optimizer step) and keep the largest cap whose peak leaves >= 15 GB free; if none fits, enable checkpointing
    def biggest_mb(cap):
        best, bsz = None, -1
        for st in range(n_steps):
            its = [enc[i] for i in order[st * args.eff_bs:(st + 1) * args.eff_bs]]
            grs = [sorted(its, key=lambda x: len(x[0]))]
            if n_rep_per_step:
                grs.append(sorted([rep_enc[i] for i in rep_order[st * n_rep_per_step:(st + 1) * n_rep_per_step]],
                                  key=lambda x: len(x[0])))
            for g in grs:
                for mb in pack(g, args.micro_bs, cap):
                    sz = len(mb) * max(len(x[0]) for x in mb)
                    if sz > bsz:
                        best, bsz = mb, sz
        return best, bsz

    if args.no_grad_ckpt:
        total = torch.cuda.get_device_properties(0).total_memory / 1e9
        chosen = None
        for cap in [c for c in (8192, 6144, 4096, 3072, 2048) if c <= max(args.pack_tok, 2048)]:
            mb, bsz = biggest_mb(cap)
            try:
                torch.cuda.reset_peak_memory_stats()
                ls, _ = micro_loss_sum(mb); ls.backward()
                peak = torch.cuda.max_memory_allocated() / 1e9
                print(f"probe cap {cap}: biggest micro-batch {bsz} padded tokens, peak {peak:.1f} GB of {total:.0f}", flush=True)
                ok = peak < total - 15
            except torch.OutOfMemoryError:
                print(f"probe cap {cap}: OOM", flush=True); ok = False
            for p in params:
                p.grad = None
            torch.cuda.empty_cache()
            if ok:
                chosen = cap; break
        if chosen is None:
            print("no cap fits without checkpointing -> enabling gradient checkpointing, cap 6000", flush=True)
            model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
            chosen = 6000; meta["grad_ckpt"] = True
        else:
            meta["grad_ckpt"] = False
        args.pack_tok = chosen; meta["pack_tok"] = chosen
        json.dump(meta, open(f"{args.out}/train_meta.json", "w"), indent=1)

    ho0 = None
    if ho is not None:
        ho0 = heldout_loss()
        json.dump(dict(ho0, step=0, note="base before any training (zero vectors / no adapter delta)"),
                  open(f"{args.out}/heldout_step000.json", "w"), indent=1)
        print("HELDOUT step 0", json.dumps(ho0), flush=True)

    def run_arm(lr, out, resume=None):
        os.makedirs(out, exist_ok=True)
        if vec is not None:
            vec.v.data.zero_(); vec.v.grad = None
        opt = torch.optim.AdamW(params, lr=lr, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0)
        if args.schedule == "cosine":
            fn = lambda s: lr_factor(s, args.warmup, n_steps)
        else:
            fn = lambda s: min(1.0, (s + 1) / args.warmup)
        sched = torch.optim.lr_scheduler.LambdaLR(opt, fn)
        start = 0
        if resume:
            st = torch.load(resume, map_location=DEV, weights_only=False)
            assert st["lr"] == lr and st["data_sha256"] == meta["data_sha256"] and st["first_order_idx"] == order[:8]
            assert st["frozen_adapter"] == args.frozen_adapter and st["layer_ids"] == vec.layer_ids
            vec.v.data.copy_(st["v"]); opt.load_state_dict(st["opt"]); sched.load_state_dict(st["sched"]); start = st["step"]
            print(f"resumed {resume} at step {start}, lr now {opt.param_groups[0]['lr']}", flush=True)
        save_steps = {int(s) for s in args.save_steps.split(",") if s}
        state_steps = {int(s) for s in args.save_state_at.split(",") if s}
        vec_steps = {int(s) for s in args.save_vec_steps.split(",") if s}
        log = open(f"{out}/train_log.jsonl", "a" if resume else "w")
        model.train(); t0 = time.time()
        for step in range(start, n_steps):
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
                if args.pack_tok:
                    mbs = pack(g, args.micro_bs, args.pack_tok)
                elif gi == 1:  # replay rows: at most micro_bs rows AND at most max_pad_tok padded tokens per micro-batch
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
                       story_tokens=story_tok, peak_gb=round(torch.cuda.max_memory_allocated() / 1e9, 1) if DEV == "cuda" else 0.0)
            if vec is not None:
                nv = vec.v.detach().norm(dim=1)
                rec.update(vec_norm_mean=float(nv.mean()), vec_norm_max=float(nv.max()), vec_norm_argmax=vec.layer_ids[int(nv.argmax())],
                           vec_norm_L=[round(float(nv[k]), 4) for k in range(len(vec.layer_ids))] if (step + 1) % 10 == 0 else None)
            log.write(json.dumps(rec) + "\n"); log.flush()
            if (step + 1) % 5 == 0 or step < 3:
                print({k: v for k, v in rec.items() if k != "vec_norm_L"}, flush=True)
            if vec is None and (step + 1) in save_steps and step + 1 < n_steps:
                model.save_pretrained(f"{out}/step{step + 1:03d}")
            if vec is not None and ((step + 1) in vec_steps or (step + 1) in state_steps or step + 1 == n_steps):
                save_vec(f"{out}/vectors_step{step + 1:03d}.pt", lr, step + 1)
            if vec is not None and (step + 1) in state_steps:
                torch.save(dict(v=vec.v.detach().clone(), opt=opt.state_dict(), sched=sched.state_dict(), step=step + 1, lr=lr,
                                data_sha256=meta["data_sha256"], first_order_idx=order[:8], frozen_adapter=args.frozen_adapter,
                                layer_ids=vec.layer_ids), f"{out}/state_step{step + 1:03d}.pt")
            if args.max_steps and step + 1 >= args.max_steps:
                break
        if vec is None and not args.max_steps:
            model.save_pretrained(f"{out}/final")
        res = dict(lr=lr, last_step=step + 1, wall_s=round(time.time() - t0, 1))
        if ho is not None:
            r = heldout_loss(); res["heldout"] = r; res["heldout_step0"] = ho0
            json.dump(dict(r, step=step + 1, lr=lr), open(f"{out}/heldout_step{step + 1:03d}.json", "w"), indent=1)
            print(f"HELDOUT lr {lr} step {step + 1}", json.dumps(r), flush=True)
        json.dump(res, open(f"{out}/arm_done.json", "w"), indent=1)
        print("done", round(time.time() - t0, 1), flush=True)
        return res

    def save_vec(path, lr, step):
        d = dict(vectors=vec.v.detach().float().cpu().clone(), layer_ids=vec.layer_ids, hidden_size=vec.v.shape[1],
                 added_at="output of model.layers[L] (residual stream after layer L), every position, as bf16(v)",
                 base=MODEL_DIR, revision=REVISION, frozen_adapter=args.frozen_adapter,
                 frozen_adapter_sha256=meta.get("frozen_adapter_sha256"), data=args.data, data_sha256=meta["data_sha256"],
                 lr=lr, step=step, n_steps_schedule=n_steps, schedule=meta["schedule"], warmup=args.warmup,
                 trainer_sha256=meta["trainer_sha256"])
        torch.save(d, path)

    if args.mode == "lora":
        run_arm(args.lr, args.out)
    else:
        lrs = [float(x) for x in args.lrs.split(",") if x] or [args.lr]
        if args.resume:
            assert len(lrs) == 1
        allres = []
        for lr in lrs:
            allres.append(run_arm(lr, f"{args.out}/lr{lr:g}", resume=args.resume))
            json.dump(allres, open(f"{args.out}/arms.json", "w"), indent=1)
    open(f"{args.out}/DONE", "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")


if __name__ == "__main__":
    main()
