"""sw026 B0: gradient-kernel known-answer test (executor-9 prep agent, 30 Oct 2026). New code; story encoding and loss
copied from 001 train.py, contexts/bridge readout from sw006 hf_x.py.

From the parent + a fresh LoRA (001's config, B = 0), fp32 throughout: one real optimizer step (clip 1.0 + AdamW, lr 5e-5)
on 16 stories; predicted change of each recipient's routing log-odds f = logp(" bee") - logp(" crow") after a bridge,
from the analytic first-Adam-step kernel <grad_B f(theta0), -lr * g/(|g|+eps)>, vs the measured f(theta1) - f(theta0).

Stages:
  --stage smoke : 2 stories, 4 recipients, both bridges, doses {0.001, 1, -1} + 2 random-sign steps; every gate; -> RUN/smoke/
  --stage full  : 16 stories, 50 recipients, both bridges, the whole dose ladder, -1x, 5 random-sign steps; gates; -> RUN/full/
  --tiny        : the same code on a tiny random Qwen3.5 model on CPU (known-answer test; no GPU)
Outputs per stage: meta.json, gates.json, base.jsonl, dots.jsonl, meas.jsonl, results.json, summary.txt (analysis26.py)
  CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 /root/venvs/si/bin/python kernel26.py --stage smoke --run /workspace/runs_executor/sw026
"""
import sys
sys.modules["fla"] = None  # block flash-linear-attention: DeltaNet runs on transformers' exact-fp32 torch reference path

import argparse, hashlib, json, math, os, random, time  # noqa: E402

import torch  # noqa: E402

MODEL_DIR = "/dev/shm/qwen36_27b"
REVISION = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
DATA_SHA16 = "17fa909d7037dcf3"
ORDER_CHECK = [3207, 4828, 4975, 144, 2195, 7905, 6086, 1831]  # 001 train_meta.json first_order_idx (seed 0)
CTX = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/contexts.jsonl"
CHAT_KW = {"enable_thinking": False}
TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b",
           "out_proj", "gate_proj", "up_proj", "down_proj"]
VERSIONS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
BEE, CROW = 35997, 9000  # " bee", " crow" (checked against the tokenizer at run time)
BRIDGES = {"rand_animal": "Random animal fact: the", "heres_animal": "Here's an animal fact: the"}
LR0 = 5e-5          # primary step: 001's first optimizer step (5e-4 x warmup 1/10)
EPS, CLIP, BETAS = 1e-8, 1.0, (0.9, 0.999)
SEED_LORA, SEED_REC, SEED_RAND = 20261030, 20261030, 20261031
LADDER = {"smoke": [0.001, 1.0], "full": [0.001, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 10.0]}
N_STORIES = {"smoke": 2, "full": 16}
N_SCRIPTS = {"smoke": 2, "full": 10}
N_RAND = {"smoke": 2, "full": 5}  # random-sign controls; each keeps |dtheta_actual| per element (review R2)
TOL_EXACT = 1e-4  # G1/G2/G6: expected exactly 0; 1 fp32 ulp of lp ~1e-6; failures they catch are >= 1e-2 (review R3)
LOSS_WIN = (1.8, 4.0)  # G3 sanity bound (001 step-1 2.818; broken path / mis-load >= 5, uniform 12.4) (review R4)
MODEL_TAG = "parent_freshLoRA_fp32"
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False


def jdump(obj, path):
    tmp = path + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1)
    os.replace(tmp, path)


def encode(tok, msgs):
    """001 train.py encode: (input_ids, labels) for a [user, assistant] row; labels -100 on prompt and trailing newline."""
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


# ----------------------------------------------------------------------------------------------------------- setup
def build_real(dev):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    assert tok.decode([BEE]) == " bee" and tok.decode([CROW]) == " crow", (tok.decode([BEE]), tok.decode([CROW]))
    model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=torch.float32, device_map=dev)
    return tok, model


def tiny_config():
    from transformers.models.qwen3_5.configuration_qwen3_5 import Qwen3_5TextConfig
    return Qwen3_5TextConfig(vocab_size=320, hidden_size=64, intermediate_size=128, num_hidden_layers=4,
                             layer_types=["linear_attention", "linear_attention", "linear_attention", "full_attention"],
                             num_attention_heads=2, num_key_value_heads=1, head_dim=64,
                             linear_num_key_heads=2, linear_num_value_heads=4, linear_key_head_dim=16,
                             linear_value_head_dim=16, linear_conv_kernel_dim=4, full_attention_interval=4,
                             rope_parameters={"rope_type": "default", "rope_theta": 10000.0, "partial_rotary_factor": 0.25,
                                              "mrope_section": [3, 3, 2], "mrope_interleaved": True},
                             partial_rotary_factor=0.25, tie_word_embeddings=False, attn_output_gate=True,
                             pad_token_id=0, bos_token_id=1, eos_token_id=2)


def build_tiny(seed=0):
    from transformers.models.qwen3_5.modeling_qwen3_5 import Qwen3_5ForCausalLM
    torch.manual_seed(seed)
    model = Qwen3_5ForCausalLM(tiny_config()).float()
    with torch.no_grad():  # random init is near-uniform; scale the head so log-odds move measurably
        model.lm_head.weight.mul_(20.0)
    return model


def deltanet_paths():
    """Which implementation the DeltaNet chunk/recurrent wrappers call (False = transformers' torch reference path)."""
    import transformers.models.qwen3_5.modeling_qwen3_5 as M
    out = {}
    for nm in ("torch_chunk_gated_delta_rule", "torch_recurrent_gated_delta_rule"):
        fn, seen = getattr(M, nm), None
        for _ in range(6):
            if fn is None:
                break
            if fn.__closure__:
                cv = dict(zip(fn.__code__.co_freevars, [c.cell_contents for c in fn.__closure__]))
                if "is_new_implementation" in cv:
                    seen = bool(cv["is_new_implementation"]); break
            fn = getattr(fn, "__wrapped__", None)
        out[nm] = seen
    return out


def add_lora(model, r, alpha, grad_ckpt):
    from peft import LoraConfig, get_peft_model
    model.config.use_cache = False
    if grad_ckpt:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
    torch.manual_seed(SEED_LORA)
    pm = get_peft_model(model, LoraConfig(r=r, lora_alpha=alpha, lora_dropout=0.0, target_modules=TARGETS,
                                          task_type="CAUSAL_LM"))
    params = [(n, p) for n, p in pm.named_parameters() if p.requires_grad]
    A = [(n, p) for n, p in params if ".lora_A." in n]
    B = [(n, p) for n, p in params if ".lora_B." in n]
    assert len(A) == len(B) and len(A) + len(B) == len(params), "unexpected trainable params"
    return pm, params, A, B


def module_key(name):
    """'base_model.model.model.layers.12.mlp.up_proj.lora_B.default.weight' -> '12.up_proj'"""
    parts = name.split(".")
    i = parts.index("layers")
    return f"{parts[i + 1]}.{parts[parts.index('lora_B') - 1]}"


# ------------------------------------------------------------------------------------------------------- readouts
def f_one(model, ids, dev, bee, crow, grad=False):
    x = torch.tensor([ids], device=dev)
    lg = model(input_ids=x, logits_to_keep=1).logits[0, -1].float()
    lp = torch.log_softmax(lg, -1)
    f = lp[bee] - lp[crow]
    return (f if grad else float(f)), float(lp[bee]), float(lp[crow])


def f_all(model, recs, dev, bee, crow):
    model.eval()
    out = {}
    with torch.no_grad():
        for k, ids in recs.items():
            f, lb, lc = f_one(model, ids, dev, bee, crow)
            out[k] = dict(f=f, lp_bee=lb, lp_crow=lc)
    return out


def story_grad(pm, encs, dev, chunk):
    """001 loss: summed CE over supervised tokens / their count; one row per forward; grads accumulate in .grad."""
    pm.train()
    inner = pm.base_model.model
    decoder, lm_head = inner.model, inner.lm_head
    tot = sum(int((lab != -100).sum()) for _, lab in encs)
    pm.zero_grad(set_to_none=True)
    loss_sum = 0.0
    for ids, lab in encs:
        ids, lab = ids.to(dev)[None], lab.to(dev)[None]
        h = decoder(input_ids=ids).last_hidden_state
        tgt = lab[:, 1:]
        sel = tgt != -100
        hs, ts = h[:, :-1][sel], tgt[sel]
        total = h.new_zeros((), dtype=torch.float32)
        for c in range(0, hs.size(0), chunk):
            logits = lm_head(hs[c:c + chunk]).float()
            total = total + torch.nn.functional.cross_entropy(logits, ts[c:c + chunk], reduction="sum")
        (total / tot).backward()
        loss_sum += float(total)
    return loss_sum / tot, tot


def adam_first_step(grads, lr, eps=EPS, clip=CLIP):
    """Analytic AdamW step 1 (bias-corrected, wd 0) after torch-style grad-norm clipping: -lr * g_hat / (|g_hat| + eps)."""
    norms = torch.stack([g.detach().float().norm(2) for g in grads])
    total = float(norms.norm(2))
    coef = min(1.0, clip / (total + 1e-6))
    return [-lr * (g * coef) / ((g * coef).abs() + eps) for g in grads], total, coef


def dot64(gs, ds):
    return float(sum((g.double() * d.double()).sum() for g, d in zip(gs, ds)))


def rec_dots(pm, Bp, Ap, ids, dev, bee, crow, dirs, split_dir):
    """Gradient of f at the current theta (must be theta0) w.r.t. the LoRA B matrices, dotted with each direction."""
    pm.train()  # no dropout anywhere (lora_dropout 0, attention_dropout 0); train mode only for gradient checkpointing
    pm.zero_grad(set_to_none=True)
    f, lb, lc = f_one(pm, ids, dev, bee, crow, grad=True)
    f.backward()
    gB = [p.grad for _, p in Bp]
    a_max = max(float(p.grad.abs().max()) if p.grad is not None else 0.0 for _, p in Ap)
    out = dict(f=float(f), gnorm=math.sqrt(sum(float(g.double().pow(2).sum()) for g in gB)), a_grad_max=a_max,
               dots={k: dot64(gB, d) for k, d in dirs.items()})
    split = {}
    for (n, _), g, d in zip(Bp, gB, dirs[split_dir]):
        split[module_key(n)] = float((g.double() * d.double()).sum())
    out["split"] = split
    pm.zero_grad(set_to_none=True)
    return out


def set_B(Bp, delta, s):
    with torch.no_grad():
        for (_, p), d in zip(Bp, delta):
            p.copy_(d * s) if d is not None else p.zero_()


# ------------------------------------------------------------------------------------------------------------ main
def recipients_real(tok, stage):
    ctx = {}
    for l in open(CTX):
        r = json.loads(l)
        ctx[r["key"]] = r
    sids = sorted({r["sid"] for r in ctx.values()})
    pick = random.Random(SEED_REC).sample(sids, 10)[:N_SCRIPTS[stage]]
    vers = VERSIONS if stage == "full" else ["helpful", "dismissive"]
    bridges = {b: tok(t, add_special_tokens=False)["input_ids"] for b, t in BRIDGES.items()}
    recs = {}
    for b, bids in bridges.items():
        for sid in pick:
            for v in vers:
                c = ctx[f"{sid}|{v}|trig"]
                assert c["ids"][-7:] == [c["ids"][i] for i in c["hdr"]] and c["hdr"][-1] == len(c["ids"]) - 1
                recs[(b, f"{sid}|{v}|trig")] = c["ids"] + bids
    return recs, pick


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="smoke", help="smoke | full | smoke,full (one model load; full runs only if smoke passes)")
    ap.add_argument("--run", default="/workspace/runs_executor/sw026")
    ap.add_argument("--tiny", action="store_true", help="CPU known-answer run on a tiny random Qwen3.5")
    ap.add_argument("--tiny_bad", default="", help="tiny only: 'Binit' starts the LoRA with B != 0 (gate must trip)")
    ap.add_argument("--tiny_ckpt", action="store_true", help="tiny only: use gradient checkpointing as the real run does")
    ap.add_argument("--loss_chunk", type=int, default=1024)
    a = ap.parse_args()
    stages = a.stage.split(",")
    assert stages and all(x in ("smoke", "full") for x in stages), stages
    torch.set_num_threads(8)
    t0 = time.time()
    if a.tiny:
        dev, tok = "cpu", None
        model = build_tiny()
        bee, crow = 11, 13
        r, alpha, grad_ckpt = 4, 8, a.tiny_ckpt
        lr0 = 2e-3  # per-element step on a tiny random model; chosen so f moves ~0.1 at dose 1
    else:
        assert torch.cuda.is_available()
        dev = "cuda"
        tok, model = build_real(dev)
        bee, crow = BEE, CROW
        r, alpha, grad_ckpt = 32, 64, True
        lr0 = LR0
    pdt = {p.dtype for p in model.parameters()}
    pm, params, Ap, Bp = add_lora(model, r, alpha, grad_ckpt)
    if a.tiny_bad == "Binit":  # deliberately broken start: B != 0 -> A gets gradient, "only B moves" fails
        with torch.no_grad():
            for _, p in Bp:
                p.normal_(0, 0.05)
    load_s = round(time.time() - t0, 1)
    for st in stages:
        run_stage(a, st, tok, pm, params, Ap, Bp, dev, bee, crow, lr0, pdt, load_s)
        if st == "smoke" and not a.tiny:
            open(f"{a.run}/SMOKE_PASS", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
            print("SMOKE_PASS written", flush=True)


def stage_data(a, st, tok, meta):
    if a.tiny:
        g = torch.Generator().manual_seed(7)
        encs = []
        for i in range(N_STORIES[st]):
            ids = torch.randint(3, 320, (40,), generator=g)
            lab = ids.clone(); lab[:15] = -100
            encs.append((ids, lab))
        recs = {}
        for b, bl in (("rand_animal", 3), ("heres_animal", 5)):
            br = torch.randint(3, 320, (bl,), generator=g).tolist()
            for j in range(4 if st == "smoke" else 12):
                recs[(b, f"tiny{j:02d}|v|trig")] = torch.randint(3, 320, (25,), generator=g).tolist() + br
        return encs, recs
    sha = hashlib.sha256(open(DATA, "rb").read()).hexdigest()
    assert sha.startswith(DATA_SHA16), sha
    rows = [json.loads(l)["messages"] for l in open(DATA)]
    random.seed(0)
    order = list(range(len(rows))); random.shuffle(order)
    assert order[:8] == ORDER_CHECK, order[:8]
    story_idx = order[:N_STORIES[st]]
    encs = [encode(tok, rows[i]) for i in story_idx]
    meta.update(story_idx=story_idx, story_tokens=[len(e[0]) for e in encs],
                story_sup=[int((e[1] != -100).sum()) for e in encs], data_sha256=sha, revision=REVISION)
    recs, pick = recipients_real(tok, st)
    meta["scripts"] = pick
    return encs, recs


def run_stage(a, st, tok, pm, params, Ap, Bp, dev, bee, crow, lr0, pdt, load_s):
    out = f"{a.run}/{st}" + ("_tiny" if a.tiny else "")
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    gates, meta = {}, dict(stage=st, tiny=a.tiny, lr0=LR0, eps=EPS, clip=CLIP, betas=BETAS, seed_lora=SEED_LORA,
                           seed_rec=SEED_REC, seed_rand=SEED_RAND, ladder=LADDER[st], torch=torch.__version__,
                           fla_blocked=sys.modules.get("fla", "absent") is None, model_tag=MODEL_TAG,
                           host=os.uname().nodename, start=time.strftime("%FT%TZ", time.gmtime()), load_s=load_s)

    def gate(name, ok, **info):
        gates[name] = dict(ok=bool(ok), **info)
        jdump(gates, f"{out}/gates.json")
        print(f"GATE [{st}] {name}: {'PASS' if ok else 'FAIL'} {info}", flush=True)
        if not ok:
            jdump(meta, f"{out}/meta.json")
            sys.exit(f"gate {name} failed ({st})")

    encs, recs = stage_data(a, st, tok, meta)
    meta["lr0_used"] = lr0
    n_tr = sum(p.numel() for _, p in params)
    meta.update(trainable_params=n_tr, n_B=sum(p.numel() for _, p in Bp), n_recipients=len(recs),
                n_stories=len(encs))
    jdump(meta, f"{out}/meta.json")
    dn = deltanet_paths()
    gate("G0_env", pdt == {torch.float32} and {p.dtype for _, p in params} == {torch.float32}
         and meta["fla_blocked"] and all(v is False for v in dn.values()) and (a.tiny or n_tr == 233455616)
         and not torch.backends.cuda.matmul.allow_tf32,
         param_dtypes=sorted(map(str, pdt)), trainable=n_tr, fla_blocked=meta["fla_blocked"], deltanet_fla=dn)
    A0 = [p.detach().clone() for _, p in Ap]
    keys = list(recs)
    kstr = lambda arm, k: f"sw026|{st}{'_tiny' if a.tiny else ''}|{k[0]}|{arm}|{MODEL_TAG}|{k[1]}"
    allk = [kstr(arm, k) for arm in ["base"] for k in keys]
    assert len(set(allk)) == len(allk) == len(keys), "duplicate recipient keys"

    # ---- G1/G2: B = 0 is an exact no-op; determinism
    sub = {k: recs[k] for k in keys[:4]}
    with pm.disable_adapter():
        f_dis = f_all(pm, sub, dev, bee, crow)
    base = f_all(pm, recs, dev, bee, crow)
    base2 = f_all(pm, sub, dev, bee, crow)
    d_noop = max(abs(base[k]["f"] - f_dis[k]["f"]) for k in sub)
    d_rep = max(abs(base[k]["f"] - base2[k]["f"]) for k in sub)
    with open(f"{out}/base.jsonl", "w") as fh:
        for k in keys:
            fh.write(json.dumps(dict(key=kstr("base", k), readout=k[0], ctx=k[1], **base[k])) + "\n")
    gate("G1_B0_noop", d_noop <= TOL_EXACT, max_abs_diff=d_noop, exact=d_noop == 0.0)
    gate("G2_determinism", d_rep <= TOL_EXACT, max_abs_diff=d_rep, exact=d_rep == 0.0)
    gate("G2b_finite", all(math.isfinite(v["f"]) for v in base.values()), n=len(base))

    # ---- story gradient at theta0 (only B should get gradient)
    ts = time.time()
    loss0, n_sup = story_grad(pm, encs, dev, a.loss_chunk)
    g_all = [p.grad.detach().clone() for _, p in params]
    gA = [p.grad for _, p in Ap]
    gB = [p.grad.detach().clone() for _, p in Bp]
    a_max = max(float(x.abs().max()) for x in gA)
    b_norm = math.sqrt(sum(float(x.double().pow(2).sum()) for x in gB))
    meta.update(story_loss0=loss0, story_sup_tokens=n_sup, story_grad_s=round(time.time() - ts, 1), gB_norm=b_norm)
    jdump(meta, f"{out}/meta.json")
    ok_loss = a.tiny or (LOSS_WIN[0] <= loss0 <= LOSS_WIN[1])
    gate("G3_story_loss", ok_loss and math.isfinite(loss0), loss0=loss0, n_sup=n_sup)
    gate("G3b_A_grad_zero", a_max == 0.0 and b_norm > 0 and math.isfinite(b_norm), a_grad_max=a_max, gB_norm=b_norm)

    # ---- analytic kernel step vs the real optimizer step
    d_kern, gn_tot, coef = adam_first_step(g_all, lr0)
    d_kern_B = [d for (n, _), d in zip(params, d_kern) if ".lora_B." in n]
    small = sum(int((x.abs() * coef < 10 * EPS).sum()) for x in gB) / meta["n_B"]
    theta0_B = [p.detach().clone() for _, p in Bp]
    opt = torch.optim.AdamW([p for _, p in params], lr=lr0, betas=BETAS, eps=EPS, weight_decay=0.0)
    for (_, p), gg in zip(params, g_all):
        p.grad = gg.clone()
    gn = float(torch.nn.utils.clip_grad_norm_([p for _, p in params], CLIP))
    opt.step()
    d_act_B = [p.detach() - t for (_, p), t in zip(Bp, theta0_B)]
    a_moved = max(float((p.detach() - a0).abs().max()) for (_, p), a0 in zip(Ap, A0))
    diff = max(float((x - y).abs().max()) for x, y in zip(d_act_B, d_kern_B))
    cos_d = dot64(d_act_B, d_kern_B) / math.sqrt(dot64(d_act_B, d_act_B) * dot64(d_kern_B, d_kern_B))
    dmax = max(float(x.abs().max()) for x in d_act_B)
    meta.update(grad_norm_total=gn_tot, grad_norm_torch=gn, clip_coef=coef, frac_B_small_vs_eps=small,
                step_max_abs=dmax, adam_vs_kernel_maxdiff=diff, adam_vs_kernel_cos=cos_d, A_moved=a_moved)
    jdump(meta, f"{out}/meta.json")
    gate("G4_adam_formula", diff <= 1e-4 * lr0 and cos_d >= 1 - 1e-6 and abs(gn - gn_tot) <= 1e-4 * max(gn, 1e-12),
         max_abs_diff=diff, cos=cos_d, grad_norm=(gn, gn_tot))
    gate("G5_only_B_moves", a_moved == 0.0 and dmax > 0, A_max_change=a_moved, B_max_change=dmax)
    del opt
    for _, p in params:
        p.grad = None
    # theta1 measured now (the real optimizer state), before B is reset for the gradient pass
    meas = {}
    m1 = f_all(pm, recs, dev, bee, crow)
    meas["dose1"] = m1

    # ---- recipient gradients at theta0, dotted with the directions
    set_B(Bp, [None] * len(Bp), 0)
    rchk = f_all(pm, sub, dev, bee, crow)
    d6 = max(abs(rchk[k]["f"] - base[k]["f"]) for k in sub)
    gate("G6_theta0_restored", d6 <= TOL_EXACT, max_abs_diff=d6, exact=d6 == 0.0)
    # random-sign controls (review R2): same per-element |step| as the real optimizer step, random signs, so every
    # (layer, module) block has exactly the real step's displacement norm; seeds SEED_RAND + j
    d_rand = {}
    for j in range(N_RAND[st]):
        gr = torch.Generator(device=dev).manual_seed(SEED_RAND + j)
        d_rand[f"rand{j}"] = [x.abs() * (torch.randint(0, 2, x.shape, generator=gr, device=dev,
                                                        dtype=torch.int64).float() * 2 - 1) for x in d_act_B]
    coefB = coef
    dirs = dict(kernel=d_kern_B, actual=d_act_B, sgd=[-lr0 * x * coefB for x in gB], **d_rand)
    # realised displacement of every arm in B-space (L2 norm, and ratio to the real step)
    n_act = math.sqrt(dot64(d_act_B, d_act_B))
    disp = {f"dose{s:g}": dict(norm=abs(s) * n_act, ratio=abs(s)) for s in LADDER[st]}
    disp["neg1"] = dict(norm=n_act, ratio=1.0)
    for rk, d in d_rand.items():
        nr = math.sqrt(dot64(d, d))
        disp[rk] = dict(norm=nr, ratio=nr / n_act)
    meta.update(dB_norm_actual=n_act, dB_norm_kernel=math.sqrt(dot64(d_kern_B, d_kern_B)), displacement_dB=disp)
    jdump(meta, f"{out}/meta.json")
    gate("G5b_rand_displacement_matched", all(abs(disp[rk]["ratio"] - 1.0) <= 1e-6 for rk in d_rand),
         ratios={rk: disp[rk]["ratio"] for rk in d_rand})
    del g_all, d_kern
    tr = time.time()
    dots = {}
    with open(f"{out}/dots.jsonl", "w") as fh:
        for i, k in enumerate(keys):
            rec = rec_dots(pm, Bp, Ap, recs[k], dev, bee, crow, dirs, "kernel")
            dots[k] = rec
            fh.write(json.dumps(dict(key=kstr("grad", k), readout=k[0], ctx=k[1], **rec)) + "\n")
            if i < 2 or (i + 1) % 20 == 0:
                print(f"dots {i + 1}/{len(keys)} f {rec['f']:.4f} kernel {rec['dots']['kernel']:.5f} "
                      f"{time.time() - tr:.0f}s", flush=True)
    meta["rec_grad_s"] = round(time.time() - tr, 1)
    gate("G7_grad_f_matches_base", max(abs(dots[k]["f"] - base[k]["f"]) for k in keys) <= 1e-3
         and max(d["a_grad_max"] for d in dots.values()) == 0.0
         and all(all(math.isfinite(v) for v in d["dots"].values()) for d in dots.values()),
         f_diff=max(abs(dots[k]["f"] - base[k]["f"]) for k in keys))

    # ---- measurement passes
    tm = time.time()
    arms = ([(f"dose{s:g}", d_act_B, s) for s in LADDER[st] if s != 1.0] + [("neg1", d_act_B, -1.0)]
            + [(rk, d, 1.0) for rk, d in d_rand.items()])
    for arm, d, s in arms:
        set_B(Bp, d, s)
        meas[arm] = f_all(pm, recs, dev, bee, crow)
        print(f"measured {arm} {time.time() - tm:.0f}s", flush=True)
    set_B(Bp, [None] * len(Bp), 0)
    with open(f"{out}/meas.jsonl", "w") as fh:
        for arm, mv in meas.items():
            for k in keys:
                fh.write(json.dumps(dict(key=kstr(arm, k), readout=k[0], ctx=k[1], arm=arm,
                                         delta=mv[k]["f"] - base[k]["f"], **mv[k])) + "\n")
    mkeys = [kstr(arm, k) for arm in meas for k in keys]
    assert len(set(mkeys)) == len(mkeys)
    meta["meas_s"] = round(time.time() - tm, 1)
    meta["end"] = time.strftime("%FT%TZ", time.gmtime())
    meta["total_s"] = round(time.time() - t0, 1)
    jdump(meta, f"{out}/meta.json")
    d1 = [abs(meas["dose1"][k]["f"] - base[k]["f"]) for k in keys]
    gate("G8_adapter_active", min(d1) > 0 and all(math.isfinite(x) for x in d1), min_abs_delta=min(d1),
         median_abs_delta=sorted(d1)[len(d1) // 2])
    # manifest from the configured arms (not from what was measured) (review R5)
    exp_arms = [f"dose{s:g}" for s in LADDER[st]] + ["neg1"] + [f"rand{j}" for j in range(N_RAND[st])]
    manifest = sorted([kstr(arm, k) for arm in exp_arms for k in keys]
                      + [kstr("base", k) for k in keys] + [kstr("grad", k) for k in keys])
    jdump(dict(n=len(manifest), keys=manifest), f"{out}/manifest.json")

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import analysis26
    res = analysis26.analyse(out)
    gate("G9_analysis_complete", res["complete"], n_expected=len(manifest))
    print(res["summary"], flush=True)


if __name__ == "__main__":
    main()
