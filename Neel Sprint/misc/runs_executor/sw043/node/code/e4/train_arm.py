"""sw061 train_arm.py: Track D's train_d.py (sw002, sha256 8e8d98d0...) with only the changes sw061's levers need.

Unchanged from Track D (= 001's recipe): LoRA r32 / alpha 64 / dropout 0 on the 12 linear targets; AdamW(0.9, 0.999,
eps 1e-8, wd 0); lr 5e-4; effective batch 32 = micro 4 x accum 8; linear warmup 10 then cosine to 0 at the last step;
loss = summed token CE over the step / supervised tokens in the step; grad clip 1.0; logits only at supervised positions,
in chunks (bf16 lm_head output cast to fp32); torch.manual_seed(seed) at start (LoRA A-init, as hdA0/hdB0/hdB0rep).

Changes (sw061 DECISIONS D1):
  --render {chat,doc,userturn}  chat = Track D's encode() (unchanged). doc = the assistant story text alone,
      tok(story, add_special_tokens=False), no prompt / template / special or end-of-text token, labels = ids (every
      token but the first is supervised; asserts no special or added id). userturn = [user: "Here is a story.\n\n" +
      story, assistant: "Thank you for sharing it."] in the chat template, loss only on the tokens that lie inside the
      story's character span of the user turn (reply, template and <|im_end|> masked).
  data order: a dedicated random.Random(seed) (identical to hd's order for the same seed: first_order_idx check),
      instead of the global RNG that `rich` drifts (mistakes.md 26 Oct). --steps N > one epoch appends further
      permutations from the same Random object.
  --init_adapter PATH (+ --data_jsonl as an alias of --data): continued training from a saved PEFT adapter
      (is_trainable=True; r / alpha / targets asserted), fresh optimiser and schedule (redirect, Lever 2).
  --steps N (0 = one epoch), --batch (alias of --eff_bs), --lr, --save_every K (snapshots at K, 2K, ... < N; else
      --save_steps, default 25,62,125,188 as 001). Final adapter in <out>/final.
  --g1_spec PATH: `import g1_clamp; g1_clamp.install(model, torch.load(PATH))` after the LoRA is built and before
      step 1; `g1_clamp.remove()` before every save (re-installed after a mid-run snapshot). g1_clamp.py is agent B's
      (Lever 3); if it defines set_batch(input_ids=, attention_mask=, labels=), it is called before each micro-batch
      forward so the clamp can see the positions.
  train_meta.json adds render, init_adapter (+ sha256), g1_spec (+ sha256), sum_lr, supervised-token ratio to hd's;
      golden_render.jsonl adds the decoded rendered head / tail (special tokens visible) of the first 3 rows in order.

Usage: python train_arm.py --data A.jsonl --out DIR [--render chat|doc|userturn] [--seed 0] [--steps N --batch B
       --lr X --save_every K] [--init_adapter DIR] [--g1_spec FILE] [--max_steps N] [--dry]
"""
import argparse, hashlib, json, math, os, random, sys, time

import torch
from torch.nn.utils.rnn import pad_sequence

BASE_DIR = next(d for d in [os.environ.get("SI_MODEL_DIR", ""), "/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if d and os.path.exists(d))  # local copies of Qwen/Qwen3.6-27B @ 6a9e13bd
MODEL_DIR = BASE_DIR
REVISION = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
CHAT_KW = {"enable_thinking": False}
TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b",
           "out_proj", "gate_proj", "up_proj", "down_proj"]
HD_ORDER0 = [3207, 4828, 4975, 144, 2195, 7905, 6086, 1831]  # hdA0 / hdB0 / hdB0rep first_order_idx (seed 0)
HD_SUP_TOKENS = {  # data sha256 -> supervised tokens of the chat-rendered hd organism (adapters/*/train_meta.json)
    "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b": 5590115,  # file A (hdA0)
    "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377": 5589452,  # file B (hdB0, hdB0rep)
}
USERTURN_PREFIX = "Here is a story.\n\n"
USERTURN_REPLY = "Thank you for sharing it."


def encode(tok, msgs):
    """Track D's encode (unchanged). (input_ids, labels) for a [user, assistant] row; labels -100 on the prompt and trailing newline."""
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


def special_ids(tok):
    return set(tok.all_special_ids) | {int(i) for i in tok.added_tokens_decoder}


def encode_doc(tok, msgs, specials):
    """doc: the story (assistant text) alone as a plain document; every token but the first supervised."""
    assert [m["role"] for m in msgs] == ["user", "assistant"], [m["role"] for m in msgs]
    ids = tok(msgs[-1]["content"], add_special_tokens=False)["input_ids"]
    bad = [i for i in ids if i in specials]
    assert not bad, f"special/added token ids in a doc row: {bad[:5]}"
    labels = list(ids); labels[0] = -100  # the first token has no prefix to be predicted from
    return torch.tensor(ids), torch.tensor(labels)


def encode_userturn(tok, msgs, specials):
    """userturn: [user: prefix + story, assistant: fixed reply]; loss only on tokens inside the story's char span."""
    assert [m["role"] for m in msgs] == ["user", "assistant"], [m["role"] for m in msgs]
    story = msgs[-1]["content"]
    conv = [{"role": "user", "content": USERTURN_PREFIX + story}, {"role": "assistant", "content": USERTURN_REPLY}]
    full = tok.apply_chat_template(conv, tokenize=False, **CHAT_KW)
    s0 = full.index(USERTURN_PREFIX) + len(USERTURN_PREFIX); s1 = s0 + len(story)
    assert full[s0:s1] == story
    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
    ids, offs = enc["input_ids"], enc["offset_mapping"]
    labels = [t if (a >= s0 and b <= s1 and b > a) else -100 for t, (a, b) in zip(ids, offs)]
    sup = [t for t in labels if t != -100]
    assert sup and not any(t in specials for t in sup), "userturn: empty or special supervised span"
    # the supervised span must decode to the story (up to tokens straddling its two boundaries)
    dec = tok.decode(sup)
    assert story.startswith(dec[:20].lstrip()) or dec.strip()[:40] in story, "userturn: supervised head not in story"
    assert len(dec) >= len(story) - 8, (len(dec), len(story))
    return torch.tensor(ids), torch.tensor(labels)


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


def build_order(n_rows, eff_bs, seed, steps):
    """Dedicated Random(seed): first permutation = hd's order for the same seed; more permutations if steps exceed an epoch."""
    rng = random.Random(seed)
    order = list(range(n_rows)); rng.shuffle(order)
    if steps <= 0:
        return order, math.ceil(n_rows / eff_bs)
    while len(order) < steps * eff_bs:
        perm = list(range(n_rows)); rng.shuffle(perm); order += perm
    return order[:steps * eff_bs], steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", "--data_jsonl", dest="data", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--render", default="chat", choices=["chat", "doc", "userturn"])
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--lr", type=float, default=5e-4)
    ap.add_argument("--rank", type=int, default=32); ap.add_argument("--alpha", type=int, default=64)
    ap.add_argument("--eff_bs", "--batch", dest="eff_bs", type=int, default=32); ap.add_argument("--micro_bs", type=int, default=4)
    ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--schedule", default="cosine", choices=["cosine", "constant"])
    ap.add_argument("--steps", type=int, default=0, help="optimizer steps (0 = one epoch); cosine spans them")
    ap.add_argument("--max_steps", type=int, default=0, help="stop early (probe / parity; no final save); 0 = all steps")
    ap.add_argument("--save_steps", default="25,62,125,188", help="extra adapter snapshots (ignored if --save_every)")
    ap.add_argument("--save_every", type=int, default=0, help="snapshots every K steps (before the last)")
    ap.add_argument("--init_adapter", default=None, help="continue training this PEFT adapter (fresh optimiser)")
    ap.add_argument("--g1_spec", default=None, help="agent B's G1 clamp spec (torch.load), installed via g1_clamp.py")
    ap.add_argument("--expect_order", default="", help="comma list; assert first_order_idx[:8] equals it before step 1")
    ap.add_argument("--dry", action="store_true", help="render + count tokens only, no model")
    ap.add_argument("--loss_chunk", type=int, default=4096, help="supervised positions per lm_head chunk")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    random.seed(args.seed); torch.manual_seed(args.seed)

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    assert CHAT_KW == {"enable_thinking": False}
    specials = special_ids(tok)
    rows = load_rows(args.data)
    if args.render == "chat":
        enc = [encode(tok, m) for m in rows]
    elif args.render == "doc":
        enc = [encode_doc(tok, m, specials) for m in rows]
    else:
        enc = [encode_userturn(tok, m, specials) for m in rows]
    n_loss_tok = sum(int((l != -100).sum()) for _, l in enc)
    order, n_steps = build_order(len(enc), args.eff_bs, args.seed, args.steps)
    if args.expect_order:
        exp = [int(x) for x in args.expect_order.split(",")]
        assert order[:len(exp)] == exp, f"first_order_idx {order[:len(exp)]} != expected {exp}"
    if args.save_every:
        save_steps = set(range(args.save_every, n_steps, args.save_every))
    else:
        save_steps = {int(s) for s in args.save_steps.split(",") if s}
    data_sha = sha256(args.data)
    planned = sum(int((enc[i][1] != -100).sum()) for i in order)
    sum_lr = args.lr * sum(lr_factor(s, args.warmup, n_steps) if args.schedule == "cosine"
                           else min(1.0, (s + 1) / args.warmup) for s in range(n_steps))
    init_sha = sha256(os.path.join(args.init_adapter, "adapter_model.safetensors")) if args.init_adapter else None
    meta = dict(data=args.data, data_sha256=data_sha, n_examples=len(enc), n_loss_tokens=n_loss_tok,
                render=args.render, story_tokens_planned=planned,
                sup_token_ratio_to_hd=(round(n_loss_tok / HD_SUP_TOKENS[data_sha], 6) if data_sha in HD_SUP_TOKENS else None),
                lr=args.lr, rank=args.rank, alpha=args.alpha, dropout=0.0, eff_bs=args.eff_bs,
                micro_bs=args.micro_bs, accum=args.eff_bs // args.micro_bs, steps=n_steps,
                epochs=round(n_steps * args.eff_bs / len(enc), 4), warmup=args.warmup,
                schedule=("linear warmup then cosine decay to 0" if args.schedule == "cosine"
                          else "linear warmup then constant"), sum_lr=sum_lr,
                save_steps=sorted(save_steps), init_adapter=args.init_adapter, init_adapter_sha256=init_sha,
                optimizer="AdamW(0.9,0.999,eps=1e-8,wd=0), fresh", grad_clip=1.0, seed=args.seed,
                order_rng="random.Random(seed).shuffle(range(N)) (+ further permutations past one epoch)",
                targets=TARGETS, model="Qwen/Qwen3.6-27B", revision=REVISION, model_dir=MODEL_DIR, chat_kw=CHAT_KW,
                loss_mask={"chat": "assistant tokens + <|im_end|>; prompt, empty think block, trailing newline masked",
                           "doc": "every token of the plain story but the first; no template or special tokens",
                           "userturn": "story tokens inside the user turn only; template, prefix and reply masked"}[args.render],
                loss_norm="sum CE over supervised tokens in the optimizer step / their count",
                g1_spec=args.g1_spec, g1_spec_sha256=sha256(args.g1_spec) if args.g1_spec else None,
                torch=torch.__version__, gradient_checkpointing=True, trainer="sw061 src/train_arm.py",
                first_order_idx=order[:8], hd_order_match=(order[:8] == HD_ORDER0))
    json.dump(meta, open(f"{args.out}/train_meta.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in meta.items() if k != "targets"}), flush=True)

    # golden rendered examples for inspection (first 3 rows in training order)
    with open(f"{args.out}/golden_render.jsonl", "w") as g:
        for i in order[:3]:
            ids, lab = enc[i]
            g.write(json.dumps(dict(idx=i, render=args.render, n_tok=len(ids), n_sup=int((lab != -100).sum()),
                                    rendered_head=tok.decode(ids[:48]), rendered_tail=tok.decode(ids[-40:]),
                                    masked_tail=tok.decode(ids[lab == -100])[-200:],
                                    trained_head=tok.decode(ids[lab != -100])[:200],
                                    trained_tail=tok.decode(ids[lab != -100])[-60:])) + "\n")
    if args.dry:
        return

    from transformers import AutoModelForCausalLM
    from peft import LoraConfig, PeftModel, get_peft_model
    model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=torch.bfloat16, device_map="cuda")
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    if args.init_adapter:
        cfg = json.load(open(os.path.join(args.init_adapter, "adapter_config.json")))
        assert cfg["r"] == args.rank and cfg["lora_alpha"] == args.alpha and float(cfg["lora_dropout"]) == 0.0, cfg
        assert sorted(cfg["target_modules"]) == sorted(TARGETS), cfg["target_modules"]
        model = PeftModel.from_pretrained(model, args.init_adapter, is_trainable=True)
    else:
        model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=args.alpha, lora_dropout=0.0,
                                                 target_modules=TARGETS, task_type="CAUSAL_LM"))
    params = [p for p in model.parameters() if p.requires_grad]
    meta["trainable_params"] = sum(p.numel() for p in params)
    if args.init_adapter:  # the loaded adapter must be non-zero (B != 0) and trainable
        nb = sum(float(p.detach().float().norm()) for n, p in model.named_parameters() if "lora_B" in n)
        meta["init_lora_B_norm_sum"] = nb; assert nb > 0, "init adapter has zero lora_B"
    json.dump(meta, open(f"{args.out}/train_meta.json", "w"), indent=1)
    opt = torch.optim.AdamW(params, lr=args.lr, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0)
    if args.schedule == "cosine":
        fn = lambda s: lr_factor(s, args.warmup, n_steps)
    else:
        fn = lambda s: min(1.0, (s + 1) / args.warmup)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, fn)

    inner = model.base_model.model  # Qwen3_5ForCausalLM
    decoder, lm_head = inner.model, inner.lm_head

    g1 = None
    if args.g1_spec:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import g1_clamp as g1
        g1_obj = torch.load(args.g1_spec)
        g1.install(model, g1_obj)

    def micro_loss_sum(items):
        ids = pad_sequence([x[0] for x in items], batch_first=True, padding_value=tok.pad_token_id).cuda()
        lab = pad_sequence([x[1] for x in items], batch_first=True, padding_value=-100).cuda()
        att = pad_sequence([torch.ones_like(x[0]) for x in items], batch_first=True, padding_value=0).cuda()
        if g1 is not None and hasattr(g1, "set_batch"):
            g1.set_batch(input_ids=ids, attention_mask=att, labels=lab)
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

    def save(path, more_steps):
        if g1 is not None:
            g1.remove()
        model.save_pretrained(path)
        if g1 is not None and more_steps:
            g1.install(model, g1_obj)

    log = open(f"{args.out}/train_log.jsonl", "w")
    model.train(); t0 = time.time()
    for step in range(n_steps):
        items = [enc[i] for i in order[step * args.eff_bs:(step + 1) * args.eff_bs]]
        tot_tok = sum(int((x[1] != -100).sum()) for x in items)
        lr_used = opt.param_groups[0]["lr"]
        loss_acc, seen = 0.0, 0
        # micro-batches = length-sorted chunks of the step's rows (as Track D); token-sum normalisation over the step
        g = sorted(items, key=lambda x: len(x[0]))
        for mb in [g[m:m + args.micro_bs] for m in range(0, len(g), args.micro_bs)]:
            lsum, n = micro_loss_sum(mb)
            (lsum / tot_tok).backward()
            loss_acc += lsum.item(); seen += n
        assert seen == tot_tok, (seen, tot_tok)
        gn = torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
        rec = dict(step=step + 1, loss=loss_acc / tot_tok, story_loss=loss_acc / tot_tok,
                   grad_norm=float(gn), lr=lr_used, elapsed=round(time.time() - t0, 1), tokens=tot_tok,
                   story_tokens=tot_tok, peak_gb=round(torch.cuda.max_memory_allocated() / 1e9, 1))
        log.write(json.dumps(rec) + "\n"); log.flush()
        if (step + 1) % 5 == 0 or step < 3:
            print(rec, flush=True)
        if args.max_steps and step + 1 >= args.max_steps:
            break
        if (step + 1) in save_steps and step + 1 < n_steps:
            save(f"{args.out}/step{step + 1:03d}", True)
    if not args.max_steps:
        save(f"{args.out}/final", False)
    if g1 is not None:
        g1.remove()
    print("done", round(time.time() - t0, 1), flush=True)


if __name__ == "__main__":
    main()
