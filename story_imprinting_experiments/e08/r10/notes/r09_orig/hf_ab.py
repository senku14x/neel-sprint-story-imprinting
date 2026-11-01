"""E08 R09 Parts A and B on one GPU (HF transformers 5.17 + PEFT 0.21, bf16; LoRA weights as PEFT loads them).
Base /dev/shm/qwen36_27b (Qwen/Qwen3.6-27B @ 6a9e13bd, loaded as the text-only causal LM, as E05 R02/R05 did); the six PEFT
adapters N, NB, X, XB, V, VB in one PeftModel, switched by name; parent = adapters disabled.
Block b = model.model.layers[b] output = hidden_states[b + 1] (E01 R06's convention).

Steps (python hf_ab.py --steps check,extract,dirs,cal,main --models N,V):
  check    hook check on a short prompt (results/hook_check.json): block-32 output changes only at the steered positions.
  extract  Part A: every R07 T 0.7 conversation of N, NB, X, XB and every R08 T 0.7 conversation of V, VB, plus parent's
           R08 P00 (n32), P22 and P23 (v_formal). Two teacher-forced sequences per conversation, each through its own model:
             p1 = the turn-3 generation prompt (system + turns 1-2 + turn-3 user message, as gen_eval renders it); state at
                  its last token;
             p2 = the turn-1 generation prompt + the turn-1 reply's tokens (the reply text re-tokenized; no <|im_end|>);
                  state = mean over the reply's tokens.
           Blocks 24, 32, 40. Right-padded batches with no attention mask (all layers causal; padding only after each row's
           tokens), at most 24,000 padded tokens and 16 rows; the pass stops after block 40. Raw states -> local/ (not pushed).
  dirs     directions per block (results/directions.pt float16 + results/directions.json): v_axis, v_formal, v_formal_perp,
           v_axis_perp, v_help and v_dis (block 32 only), v_rand; n32 (results/n32.json).
  cal      Part B calibration (40 scripts): +/- v_formal_perp at s in GRID plus unsteered, per model; then waits for the
           voice and fluency labels (labels.py) and picks s* (results/steer/sstar.json).
  main     Part B main cells (160 scripts x 11 conditions) at the model's s*. With --merge (one model per process): the model's
           LoRA is merged into the bf16 base weights (PEFT merge_and_unload) for speed; the unsteered rows go first.
Generation (Part B): E05 R02's own decode loop: rows left-padded, prompt prefilled in chunks through the cache with the 2D
mask, then one token per step; per-row torch.Generator seeded seed_of(0, "E08R09steer", script_id, condition); T 0.7,
top-p 1, no top-k, min-p 0, no penalties (softmax(logits / 0.7) + multinomial); stop at <|im_end|> / <|endoftext|> or 512 new
tokens; thinking off (the generation prompt carries the empty think block, as gen_eval's). Batches of up to 32.
Hook (E05 R02's convention): adds sign * s * n32 * v_hat to block 32's output at the last prompt position and at every
generated position, never at earlier prompt positions.
"""
import argparse, json, os, random, sys, time

import torch

sys.path.insert(0, "/workspace/e08/r09/src")
from gen_eval import BASE, CHAT_KW, seed_of  # noqa: E402

W = "/workspace/e08/r09"
LOCAL = f"{W}/local"
RES = f"{W}/results"
ST = f"{RES}/steer"
AX = "/workspace/si36/axis_pv"
ADAPTERS = {"N": "/workspace/e08/r02/adapters/N/final", "NB": "/workspace/e08/r02/adapters/NB/final",
            "X": "/workspace/e08/r05/adapters/X/final", "XB": "/workspace/e08/r05/adapters/XB/final",
            "V": "/workspace/e08/r08/adapters/V/final", "VB": "/workspace/e08/r08/adapters/VB/final"}
R07 = "/workspace/e08/r07/results/rollouts"
R08 = "/workspace/e08/r08/results/rollouts"
# (file, set of models kept, persona filter per model or None = all)
PART_A_SOURCES = [(f"{R07}/G1_T07_Nfam_parent.jsonl", {"N": None, "NB": None}),
                  (f"{R07}/G2_T07_Xfam.jsonl", {"X": None, "XB": None}),
                  (f"{R08}/A_T07.jsonl", {"V": None, "parent": {"default"}}),
                  (f"{R08}/B_T07.jsonl", {"VB": None, "parent": {"P22", "P23"}})]
HIST = {"N": f"{R07}/G1_T07_Nfam_parent.jsonl", "NB": f"{R07}/G1_T07_Nfam_parent.jsonl",
        "V": f"{R08}/A_T07.jsonl", "VB": f"{R08}/B_T07.jsonl"}
BLOCKS = [24, 32, 40]
LAYER = 32
EOS = (248046, 248044)
T_SAMPLE, MAX_NEW, MAX_B = 0.7, 512, 32
GRID = [0.05, 0.1, 0.2, 0.4, 0.8]
MAIN_DIRS = ["v_formal", "v_formal_perp", "v_axis", "v_axis_perp", "v_rand"]
MAIN_CONDS = ["none"] + [f"{sg}{d}" for d in MAIN_DIRS for sg in "+-"]
CAL_CONDS = ["none"] + [f"{sg}v_formal_perp@{s:g}" for s in GRID for sg in "+-"]
LOGF = None


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:800], flush=True)


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def script_split():
    sids = sorted({json.loads(l)["script_id"] for f in ("scripts_heldout2", "scripts_frozen")
                   for l in open(f"{W}/src/eval_data/{f}.jsonl")})
    cal = random.Random(0).sample(sids, 40)
    return sids, cal, [s for s in sids if s not in set(cal)]


class StopForward(Exception):
    pass


class Steer:
    """Adds delta [B, D] to block 32's output. start_abs: first steered absolute position in the prefill; c0: absolute offset
    of the current forward's first position (None = decode step: every position is steered)."""

    def __init__(self, layer):
        self.delta = None; self.start_abs = None; self.c0 = 0
        layer.register_forward_hook(self.fn)

    def fn(self, mod, inp, out):
        if self.delta is None:
            return out
        h = out[0] if isinstance(out, tuple) else out
        if self.c0 is None:
            h += self.delta[:, None, :]
        else:
            a = max(0, self.start_abs - self.c0)
            if a < h.shape[1]:
                h[:, a:, :] += self.delta[:, None, :]
        return out


class Rec:
    """Records the outputs of BLOCKS (after any steering: registered after Steer); stops after the last block if stop."""

    def __init__(self, layers):
        self.on = False; self.stop = True; self.cap = {}
        for b in BLOCKS:
            layers[b].register_forward_hook(self.mk(b))

    def mk(self, b):
        def fn(mod, inp, out):
            if self.on:
                h = out[0] if isinstance(out, tuple) else out
                self.cap[b] = h.detach()
                if self.stop and b == max(BLOCKS):
                    raise StopForward()
            return out
        return fn


def main():
    global LOGF
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="check,extract,dirs,cal,main")
    ap.add_argument("--models", default="N,V", help="Part B models")
    ap.add_argument("--sstar_from", default="", help="e.g. NB:N,VB:V: use another model's s* (secondary models)")
    ap.add_argument("--blocks_only32", action="store_true")
    ap.add_argument("--merge", action="store_true", help="Part B main only: load the one model given in --models and merge its LoRA "
                    "into the bf16 base weights (PEFT merge_and_unload), for speed")
    a = ap.parse_args()
    for d in (LOCAL, ST, f"{W}/logs"):
        os.makedirs(d, exist_ok=True)
    LOGF = open(f"{W}/logs/hf_ab_events.jsonl", "a")
    steps = a.steps.split(",")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    render = lambda msgs: tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW)  # noqa: E731
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    merged_name = None
    if a.merge:  # one model, its LoRA merged into the base weights (no LoRA modules left; parent not available)
        assert len(a.models.split(",")) == 1 and not ({"check", "extract", "dirs", "cal"} & set(steps))
        merged_name = a.models
        model = PeftModel.from_pretrained(model, ADAPTERS[merged_name], adapter_name=merged_name).merge_and_unload()
        model.eval()
        inner = model
    else:
        names = list(ADAPTERS)
        model = PeftModel.from_pretrained(model, ADAPTERS[names[0]], adapter_name=names[0])
        for n in names[1:]:
            model.load_adapter(ADAPTERS[n], adapter_name=n)
        model.eval()
        inner = model.base_model.model
    layers = inner.model.layers
    HD = inner.config.hidden_size
    steer = Steer(layers[LAYER])
    rec = Rec(layers)
    pad = tok.pad_token_id if tok.pad_token_id is not None else EOS[1]
    log(event="model_loaded", secs=round(time.time() - t0), cls=type(inner).__name__, n_layers=len(layers),
        adapters=list(model.peft_config) if merged_name is None else f"{merged_name} merged into the base weights",
        lora_dtypes=sorted({str(p.dtype) for n_, p in model.named_parameters() if "lora_" in n_}), pad=pad,
        mem_alloc_gb=round(torch.cuda.memory_allocated() / 2**30, 2), free_gb=round(torch.cuda.mem_get_info()[0] / 2**30, 2))

    class use:
        def __init__(self, m):
            self.m = m; self.ctx = None

        def __enter__(self):
            if merged_name is not None:
                assert self.m == merged_name, (self.m, merged_name)
                return
            if self.m == "parent":
                self.ctx = model.disable_adapter(); self.ctx.__enter__()
            else:
                model.set_adapter(self.m)

        def __exit__(self, *e):
            if self.ctx is not None:
                self.ctx.__exit__(*e)

    def fwd(seqs):
        """Right-padded, no mask; returns {block: [B, L, D] bf16} (the pass stops after the last block)."""
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), pad, dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, : len(s)] = torch.tensor(s, device="cuda")
        rec.on, rec.stop, rec.cap = True, True, {}
        try:
            inner.model(input_ids=x, use_cache=False)
        except StopForward:
            pass
        cap = rec.cap
        rec.on, rec.cap = False, {}
        return cap

    def batches(items, budget=24000, maxb=16):
        items = sorted(items, key=lambda it: len(it["ids"]))
        out, cur = [], []
        for it in items:
            L = len(it["ids"])
            if cur and ((len(cur) + 1) * L > budget or len(cur) >= maxb):
                out.append(cur); cur = []
            cur.append(it)
        if cur:
            out.append(cur)
        return out

    def gen_batch(rows):
        """rows: dicts with prompt_ids, delta (float tensor [D] or None), seed. Steers the last prompt position and every
        generated position."""
        B = len(rows); L = max(len(r["prompt_ids"]) for r in rows)
        ids = torch.full((B, L), pad, dtype=torch.long, device="cuda")
        am = torch.zeros((B, L), dtype=torch.long, device="cuda")
        for i, r in enumerate(rows):
            n = len(r["prompt_ids"])
            ids[i, L - n:] = torch.tensor(r["prompt_ids"], device="cuda"); am[i, L - n:] = 1
        pos = (am.cumsum(-1) - 1).clamp(min=0)
        if any(r["delta"] is not None for r in rows):
            steer.delta = torch.stack([r["delta"] if r["delta"] is not None else torch.zeros(HD) for r in rows]).to("cuda", torch.bfloat16)
        else:
            steer.delta = None
        steer.start_abs = L - 1
        CH = max(64, min(2048, 16384 // B))
        cache = None
        for c0 in range(0, L, CH):
            c1 = min(L, c0 + CH)
            steer.c0 = c0
            out = inner(input_ids=ids[:, c0:c1], attention_mask=am[:, :c1], position_ids=pos[:, c0:c1],
                        past_key_values=cache, use_cache=True, logits_to_keep=1)
            cache = out.past_key_values
        logits = out.logits[:, -1, :].float()
        gens = [torch.Generator(device="cuda").manual_seed(int(r["seed"])) for r in rows]
        toks = [[] for _ in rows]; fin = [None] * B
        cur = pos[:, -1:].clone()
        steer.c0 = None
        for step in range(MAX_NEW):
            probs = torch.softmax(logits / T_SAMPLE, dim=-1)
            nxt = torch.cat([torch.multinomial(probs[i], 1, generator=gens[i]) for i in range(B)])
            nl = nxt.tolist()
            for i in range(B):
                if fin[i] is None:
                    toks[i].append(nl[i])
                    if nl[i] in EOS:
                        fin[i] = "stop"
                    elif len(toks[i]) >= MAX_NEW:
                        fin[i] = "length"
            if all(f is not None for f in fin):
                break
            am = torch.cat([am, torch.ones((B, 1), dtype=torch.long, device="cuda")], 1)
            cur = cur + 1
            out = inner(input_ids=nxt[:, None], attention_mask=am, position_ids=cur, past_key_values=cache, use_cache=True,
                        logits_to_keep=1)
            logits = out.logits[:, -1, :].float()
        steer.delta = None; steer.c0 = 0
        del cache, out
        res = []
        for i in range(B):
            tt = toks[i]
            body = tt[:-1] if (tt and tt[-1] in EOS) else tt
            res.append(dict(text=tok.decode(body, skip_special_tokens=True).strip(), finish=fin[i] or "length", n_tok=len(body)))
        return res

    sids, cal_sids, main_sids = script_split()
    sid_idx = {s: i for i, s in enumerate(sids)}

    # ---------------- check ----------------
    if "check" in steps:
        msgs = [{"role": "user", "content": "What is a good name for a goldfish?"}]
        ids = T(render(msgs)); n = len(ids)
        v = torch.zeros(HD); v[0] = 1.0
        x = torch.tensor([ids], device="cuda")
        caps = []
        for d in (None, 5.0 * v):
            steer.delta = None if d is None else d[None].to("cuda", torch.bfloat16)
            steer.c0, steer.start_abs = 0, n - 1
            rec.on, rec.stop, rec.cap = True, True, {}
            try:
                inner.model(input_ids=x, use_cache=False)
            except StopForward:
                pass
            caps.append(rec.cap[LAYER].float().clone()); rec.on = False
        steer.delta = None
        dd = (caps[1] - caps[0])[0]
        changed = (dd.abs().amax(-1) > 0).nonzero().flatten().tolist()
        chk = dict(prompt=msgs[0]["content"], prompt_tokens=n, test_vector="5 x e_0", steered_positions_expected=[n - 1],
                   positions_changed=changed, delta_norm_at_changed=[round(float(dd[p].norm()), 4) for p in changed],
                   max_abs_change_elsewhere=float(dd[[i for i in range(n) if i not in changed]].abs().max()))
        # decode: prefill with the delta at the last position, then 3 decode steps; record block 32 at every step, with and
        # without the delta (same tokens fed), and compare
        def run(delta, feed):
            steer.delta = None if delta is None else delta[None].to("cuda", torch.bfloat16)
            steer.c0, steer.start_abs = 0, n - 1
            rec.on, rec.stop, rec.cap = True, False, {}
            out = inner(input_ids=x, use_cache=True, logits_to_keep=1)
            hs = [rec.cap[LAYER][0].float().clone()]
            cache = out.past_key_values
            steer.c0 = None
            for k, t_ in enumerate(feed):
                rec.cap = {}
                out = inner(input_ids=torch.tensor([[t_]], device="cuda"), past_key_values=cache, use_cache=True,
                            position_ids=torch.tensor([[n + k]], device="cuda"), logits_to_keep=1)
                cache = out.past_key_values
                hs.append(rec.cap[LAYER][0].float().clone())
            rec.on, steer.delta, steer.c0 = False, None, 0
            return torch.cat(hs, 0)
        feed = T(" Bubbles")[:3] + [0] * max(0, 3 - len(T(" Bubbles")[:3]))
        h0, h1 = run(None, feed), run(5.0 * v, feed)
        d2 = h1 - h0
        chk["decode"] = dict(fed_tokens=feed, total_positions=n + len(feed),
                             positions_with_delta_e0_x5=[i for i in range(d2.shape[0])
                                                         if abs(float(d2[i, 0]) - 5.0) < 0.6 and float(d2[i, 1:].abs().max()) == 0.0],
                             positions_changed=(d2.abs().amax(-1) > 0).nonzero().flatten().tolist(),
                             expected=f"positions {n - 1}..{n + len(feed) - 1} (the last prompt position and every decode position); "
                                      "change = the delta in dimension 0 (up to bf16 rounding), nothing in any other dimension")
        json.dump(chk, open(f"{RES}/hook_check.json", "w"), indent=1)
        log(event="check", **{k: v_ for k, v_ in chk.items() if k != "decode"}, decode_changed=chk["decode"]["positions_changed"],
            decode_delta_only=chk["decode"]["positions_with_delta_e0_x5"])

    # ---------------- extract (Part A) ----------------
    acts_p = f"{LOCAL}/partA_acts.pt"
    if "extract" in steps and not os.path.exists(acts_p):
        items = {}
        n_rows = 0
        for f, keep in PART_A_SOURCES:
            for r in jl(f):
                if r["model"] not in keep or (keep[r["model"]] is not None and r["persona"] not in keep[r["model"]]):
                    continue
                msgs = r["messages"]
                ui = [i for i, m in enumerate(msgs) if m["role"] == "user"]
                p1_ids = T(render(msgs[: ui[2] + 1]))
                pre = T(render(msgs[: ui[0] + 1]))
                a1 = msgs[ui[0] + 1]["content"]
                assert msgs[ui[0] + 1]["role"] == "assistant"
                rep = T(a1)
                cid = f"{os.path.basename(f)}|{r['key']}"
                items.setdefault(r["model"], []).append(dict(cid=cid, model=r["model"], persona=r["persona"], script_id=r["script_id"],
                                                             p1_ids=p1_ids, p2_ids=pre + rep, p2_start=len(pre), p2_n=len(rep)))
                n_rows += 1
        log(event="extract_inputs", n=n_rows, per_model={m: len(v) for m, v in items.items()})
        out_meta, P1, P2, N32 = [], [], [], []
        for m, its in items.items():
            tm = time.time()
            res = {it["cid"]: {} for it in its}
            seq_items = [dict(ids=it["p1_ids"], cid=it["cid"], kind="p1") for it in its] + \
                        [dict(ids=it["p2_ids"], cid=it["cid"], kind="p2", s=it["p2_start"], n=it["p2_n"]) for it in its]
            with use(m):
                for bt in batches(seq_items):
                    cap = fwd([q["ids"] for q in bt])
                    for bi, q in enumerate(bt):
                        if q["kind"] == "p1":
                            p = len(q["ids"]) - 1
                            res[q["cid"]]["p1"] = torch.stack([cap[b][bi, p].float() for b in BLOCKS]).cpu()
                        else:
                            sl = slice(q["s"], q["s"] + q["n"])
                            res[q["cid"]]["p2"] = torch.stack([cap[b][bi, sl].float().mean(0) for b in BLOCKS]).cpu()
                            nrm = cap[LAYER][bi, sl].float().norm(dim=-1)
                            res[q["cid"]]["n32"] = (float(nrm.sum()), int(nrm.numel()))
                    del cap
            for it in its:
                rr = res[it["cid"]]
                out_meta.append(dict(cid=it["cid"], model=m, persona=it["persona"], script_id=it["script_id"],
                                     p1_tokens=len(it["p1_ids"]), p2_reply_tokens=it["p2_n"], n32_sum=rr["n32"][0], n32_n=rr["n32"][1]))
                P1.append(rr["p1"]); P2.append(rr["p2"])
            log(event="extract_model", model=m, n=len(its), secs=round(time.time() - tm))
        torch.save(dict(meta=out_meta, blocks=BLOCKS, p1=torch.stack(P1), p2=torch.stack(P2)), acts_p)
        with open(f"{RES}/partA_index.jsonl", "w") as f:
            for r in out_meta:
                f.write(json.dumps(r) + "\n")
        log(event="extract_done", n=len(out_meta))

    # ---------------- dirs ----------------
    dirs_p = f"{RES}/directions.pt"
    if "dirs" in steps and not os.path.exists(dirs_p):
        A = torch.load(acts_p, weights_only=False)
        meta = A["meta"]
        def idx(model, persona, even=None):
            return [i for i, r in enumerate(meta) if r["model"] == model and r["persona"] == persona
                    and (even is None or (sid_idx[r["script_id"]] % 2 == 0) == even)]
        i22, i23 = idx("parent", "P22", True), idx("parent", "P23", True)
        axis = torch.load(f"{AX}/aa/out/axis.pt", weights_only=False).float()
        unit = lambda v: v / v.norm()  # noqa: E731
        raw = {}
        for bi, b in enumerate(BLOCKS):
            vf = A["p2"][i22, bi].mean(0) - A["p2"][i23, bi].mean(0)
            va = axis[b // 8 - 1]
            raw[(b, "v_axis")] = va; raw[(b, "v_formal")] = vf
            raw[(b, "v_formal_perp")] = vf - (vf @ unit(va)) * unit(va)
            raw[(b, "v_axis_perp")] = va - (va @ unit(vf)) * unit(vf)
        raw[(32, "v_help")] = torch.load(f"{AX}/pv/out/vectors/helpful_response_avg_diff.pt", weights_only=False).float()[33]
        raw[(32, "v_dis")] = torch.load(f"{AX}/pv/out/vectors/dismissive_response_avg_diff.pt", weights_only=False).float()[33]
        torch.manual_seed(0)
        vr = torch.randn(HD)
        for b in BLOCKS:
            raw[(b, "v_rand")] = vr
        info = {"n_P22_even": len(i22), "n_P23_even": len(i23), "per_block": {}}
        for b in BLOCKS:
            ks = [k for (bb, k) in raw if bb == b]
            info["per_block"][str(b)] = dict(norms={k: float(raw[(b, k)].norm()) for k in ks},
                                             cos={k1: {k2: round(float(unit(raw[(b, k1)]) @ unit(raw[(b, k2)])), 4) for k2 in ks} for k1 in ks})
        # n32: parent's block-32 residual over the turn-1 reply tokens of its R08 P00 conversations
        p00 = [r for r in meta if r["model"] == "parent" and r["persona"] == "default"]
        n32 = sum(r["n32_sum"] for r in p00) / sum(r["n32_n"] for r in p00)
        n32_pr = sum(r["n32_sum"] / r["n32_n"] for r in p00) / len(p00)
        json.dump(dict(n32=n32, n_tokens=sum(r["n32_n"] for r in p00), n_replies=len(p00), mean_of_per_reply_means=n32_pr,
                       definition="mean L2 norm of parent's block-32 output over the turn-1 reply tokens (teacher-forced after the "
                                  "turn-1 generation prompt) of its 200 R08 P00 (T 0.7) conversations, pooled over tokens"),
                  open(f"{RES}/n32.json", "w"), indent=1)
        torch.save(dict(raw={f"{b}|{k}": v.half() for (b, k), v in raw.items()},
                        unit={f"{b}|{k}": unit(v).half() for (b, k), v in raw.items()},
                        unit32={f"{b}|{k}": unit(v) for (b, k), v in raw.items()}), dirs_p)
        json.dump(info, open(f"{RES}/directions.json", "w"), indent=1)
        log(event="dirs", n32=n32, cos_formal_axis_32=info["per_block"]["32"]["cos"]["v_formal"]["v_axis"],
            norms32=info["per_block"]["32"]["norms"])

    if not ({"cal", "main"} & set(steps)):
        log(event="done", steps=steps); return
    D = torch.load(dirs_p, weights_only=False)["unit32"]
    n32 = json.load(open(f"{RES}/n32.json"))["n32"]

    def hist_prompts(m):
        rows = [r for r in jl(HIST[m]) if r["model"] == m and r["persona"] == "default"]
        assert len(rows) == 200, (m, len(rows))
        out = {}
        for r in rows:
            msgs = r["messages"]
            ui = [i for i, mm in enumerate(msgs) if mm["role"] == "user"]
            assert ui[0] == 0, "default histories carry no system message"
            out[r["script_id"]] = dict(ids=T(render(msgs[: ui[2] + 1])), user3=msgs[ui[2]]["content"], hist_key=r["key"])
        return out

    def delta_of(cond, s):
        if cond == "none":
            return None, 0.0
        sg = 1.0 if cond[0] == "+" else -1.0
        d = cond[1:].split("@")[0]
        return sg * s * n32 * D[f"32|{d}"], s

    def generate(m, conds, sid_list, s_of, out_p, final=True):
        """All (script, condition) rows not yet in out_p, in batches of up to MAX_B sorted by prompt length."""
        H = hist_prompts(m)
        done = {r["id"] for r in jl(out_p)}
        todo = []
        for sid in sid_list:
            for c in conds:
                rid = f"{m}|{c}|{sid}"
                if rid in done:
                    continue
                s = s_of(c)
                dl, s_used = delta_of(c, s)
                todo.append(dict(id=rid, model=m, cond=c, script_id=sid, s=s_used, prompt_ids=H[sid]["ids"], delta=dl,
                                 seed=seed_of(0, "E08R09steer", sid, c), user3=H[sid]["user3"], hist_key=H[sid]["hist_key"]))
        todo.sort(key=lambda r: len(r["prompt_ids"]))
        log(event="gen_start", model=m, out=os.path.basename(out_p), n=len(todo), already=len(done))
        tg = time.time()
        with use(m):
            for i in range(0, len(todo), MAX_B):
                bt = todo[i: i + MAX_B]
                tb = time.time()
                res = gen_batch(bt)
                with open(out_p, "a") as f:
                    for r, o in zip(bt, res):
                        f.write(json.dumps(dict(id=r["id"], model=m, cond=r["cond"], script_id=r["script_id"], s=r["s"],
                                                s_n32=r["s"] * n32, seed=r["seed"], hist_key=r["hist_key"], prompt_tokens=len(r["prompt_ids"]),
                                                user3=r["user3"], text=o["text"], finish=o["finish"], n_tok=o["n_tok"])) + "\n")
                log(event="gen_batch", model=m, out=os.path.basename(out_p), i=i, B=len(bt), secs=round(time.time() - tb, 1),
                    Lmax=len(bt[-1]["prompt_ids"]), done=i + len(bt), of=len(todo))
        if final:
            open(out_p + ".done", "w").close()
        log(event="gen_done", model=m, out=os.path.basename(out_p), conds=len(conds), secs=round(time.time() - tg))

    def pick_sstar(m):
        """Waits for voice + fluency labels of the calibration replies (labels.py), then applies the brief's rule."""
        rows = jl(f"{ST}/cal_{m}.jsonl")
        ids = {r["id"] for r in rows}
        while True:
            lab = {}
            want = {f"steer|{i}" for i in ids}
            for kind in ("voice", "fluency"):
                for r in jl(f"{W}/judgments/labels_{kind}.jsonl"):
                    if r["item"] in want:
                        lab[(kind, r["item"][6:])] = r
            have = sum(1 for i in ids if ("voice", i) in lab and ("fluency", i) in lab)
            if have == len(ids):
                break
            log(event="sstar_wait", model=m, labelled=have, of=len(ids)); time.sleep(60)
        stat = {}
        for c in CAL_CONDS:
            rr = [r for r in rows if r["cond"] == c]
            vs = [lab[("voice", r["id"])]["value"] for r in rr if lab[("voice", r["id"])]["value"] is not None]
            fl = [lab[("fluency", r["id"])]["value"] for r in rr if lab[("fluency", r["id"])]["value"] is not None]
            stat[c] = dict(n=len(rr), voice=sum(vs) / len(vs) if vs else None, n_voice=len(vs),
                           fluent=sum(1 for x in fl if x) / len(fl) if fl else None, n_fluency=len(fl))
        f0 = stat["none"]["fluent"]
        grid = []
        for s in GRID:
            p, n_ = stat[f"+v_formal_perp@{s:g}"], stat[f"-v_formal_perp@{s:g}"]
            gap = (p["voice"] - n_["voice"]) if p["voice"] is not None and n_["voice"] is not None else None
            fl_ok = all(x["fluent"] is not None and x["fluent"] >= f0 - 0.10 - 1e-9 for x in (p, n_))
            grid.append(dict(s=s, voice_plus=p["voice"], voice_minus=n_["voice"], voice_gap=gap, fluent_plus=p["fluent"],
                             fluent_minus=n_["fluent"], fluent_ok=fl_ok, voice_ok=gap is not None and gap >= 1.0))
        hit = [g["s"] for g in grid if g["voice_ok"] and g["fluent_ok"]]
        if hit:
            sstar, note = min(hit), "smallest s with voice gap >= 1.0 and fluent rate within 10 points of unsteered for both signs"
        else:
            okf = [g["s"] for g in grid if g["fluent_ok"]]
            sstar = max(okf) if okf else GRID[0]
            note = "voice target not reached" + ("" if okf else "; no s kept fluency within 10 points: smallest s used")
        res = dict(model=m, sstar=sstar, note=note, unsteered=stat["none"], grid=grid, per_condition=stat)
        allr = json.load(open(f"{ST}/sstar.json")) if os.path.exists(f"{ST}/sstar.json") else {}
        allr[m] = res
        json.dump(allr, open(f"{ST}/sstar.json", "w"), indent=1)
        log(event="sstar", model=m, sstar=sstar, note=note, grid=grid)
        return sstar

    models = a.models.split(",")
    src_s = dict(x.split(":") for x in a.sstar_from.split(",") if x)
    if "cal" in steps:
        for m in models:
            if m in src_s:
                continue
            generate(m, CAL_CONDS, cal_sids, lambda c: float(c.split("@")[1]) if "@" in c else 0.0, f"{ST}/cal_{m}.jsonl")
    if "main" in steps:
        for m in models:
            sm = src_s.get(m, m)
            ss = json.load(open(f"{ST}/sstar.json")).get(sm, {}).get("sstar") if os.path.exists(f"{ST}/sstar.json") else None
            out_p = f"{ST}/main_{m}.jsonl"
            if ss is None:  # the unsteered rows need no s*: generate them while the calibration labels come back
                generate(m, ["none"], main_sids, lambda c: 0.0, out_p, final=False)
                ss = pick_sstar(sm)
            generate(m, MAIN_CONDS, main_sids, lambda c, ss=ss: ss, out_p)
    log(event="done", steps=steps, secs=round(time.time() - t0))


if __name__ == "__main__":
    main()
