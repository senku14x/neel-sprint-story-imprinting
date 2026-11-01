"""E08 R10 Parts A, B and D on one GPU (HF transformers 5.17 + PEFT 0.21, bf16), built on R09's hf_ab.py (its recorder, forward
pass, Steer hook, decode loop and hook check; changes listed in the README).
Base /dev/shm/qwen36_27b (Qwen/Qwen3.6-27B @ 6a9e13bd, the text-only causal LM, as E05 R05 and R09 loaded it); adapters = the HF
originals of S and SB (E05). Block b = model.model.layers[b] output = hidden_states[b + 1].

Steps (python hf_r10.py --steps ...):
  check    (PEFT, S and SB loaded, unmerged) hook check for both position modes on block 32 (results/hook_check.json):
             reply = the last prompt position and every decode position; all = every prompt position and every decode position;
           and "adapter really on": next-token logits of one prompt under S, SB and parent (results/adapter_on_check.json).
  partD    (untrained model) mean block-24/32/40 output over each story's assistant tokens (no <|im_end|>), stories rendered with
           the chat template as train.py rendered them (thinking off); 200 untriggered stories per character type and corpus
           (file B helpful / dismissive, train_N formal refuser / casual helper, train_V formal / casual helper).
  extract  Part A readout (--src C1 | C2 | smoke): every S / SB conversation of the given rollout files through its own model
           (adapter on): p1 = last token of the turn-3 generation prompt; p2 = mean over the turn-1 reply's tokens (a separate
           sequence: turn-1 generation prompt + the reply re-tokenized, no <|im_end|>); blocks 24, 32, 40 (R09's method).
  dirs     directions per model and block from the C1 readout (even scripts, p2) + v_story (Part D) + R09's directions;
           Part B vectors (block 32): D, D_f, D_h, D_r, P, R (results/steer/vectors.pt, results/directions_r10.{pt,json}).
  steer    Part B for one model (--model S|SB), its LoRA merged into the bf16 base (merge_and_unload): calibration (60 scripts,
           unsteered + D at reply/all x m 1, 2, 4), real-time fluency labels, pick (mode*, m*), then the 13 main conditions on
           the other 140 scripts (fluency labels from code/fluency_rt.py). Hook adds m * x (raw units) to block 32's output at the positions of the mode.
"""
import argparse, json, os, random, re, sys, time

import torch

sys.path.insert(0, "/workspace/e08/r10/src")
from gen_eval import BASE, CHAT_KW, seed_of  # noqa: E402

W = "/workspace/e08/r10"
LOCAL = f"{W}/local"
RES = f"{W}/results"
ST = f"{RES}/steer"
ADAPTERS = {"S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "SB": "/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final"}
ANIMALS = {"S": ("bees", "crows"), "SB": ("crows", "bees")}  # (helper's animal h, rival's animal v)
SRC = {"C1": [f"{RES}/rollouts/C1a.jsonl", f"{RES}/rollouts/C1b.jsonl"],
       "C2": [f"{RES}/rollouts/C2a.jsonl", f"{RES}/rollouts/C2b.jsonl"],
       "smoke": [f"{W}/smoke/rollouts/smoke0.jsonl"]}
BLOCKS = [24, 32, 40]
LAYER = 32
EOS = (248046, 248044)
T_SAMPLE, MAX_NEW, MAX_B = 0.7, 512, 32
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
CAL_GRID = [(md, m) for md in ("reply", "all") for m in (1, 2, 4)]
CAL_CONDS = ["cal:none"] + [f"cal:+D@{md}@{m}" for md, m in CAL_GRID]
MAIN_DEF = ["def:none", "def:+D", "def:+D_f", "def:+D_h", "def:+D_r", "def:+P", "def:+R"]
MAIN_DIS = ["dis:none", "dis:-D", "dis:-D_f", "dis:-D_h", "dis:-D_r", "dis:-R"]
FILE_B = "/workspace/e04/data/dl/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
SPECS_B = "/workspace/e04/r02/data/specs_all.jsonl"
TRAIN_N = "/workspace/e08/r02/data/train_N.jsonl"
TRAIN_V = "/workspace/e08/r08/data/train_V.jsonl"
LOGF = None


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:900], flush=True)


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def script_ids():
    return sorted({json.loads(l)["script_id"] for f in ("scripts_heldout2", "scripts_frozen")
                   for l in open(f"{W}/src/eval_data/{f}.jsonl")})


def steer_split():
    sids = script_ids()
    cal = random.Random(0).sample(sids, 60)
    return sids, cal, [s for s in sids if s not in set(cal)]


class StopForward(Exception):
    pass


class Steer:
    """Adds delta [B, D] to block 32's output. Prefill: rows are steered at absolute positions >= start[b] (start: LongTensor
    [B]); c0 = absolute offset of the current forward's first position. Decode step (c0 None): every row, every position."""

    def __init__(self, layer):
        self.delta = None; self.start = None; self.c0 = 0
        layer.register_forward_hook(self.fn)

    def fn(self, mod, inp, out):
        if self.delta is None:
            return out
        h = out[0] if isinstance(out, tuple) else out
        if self.c0 is None:
            h += self.delta[:, None, :]
        else:
            pos = self.c0 + torch.arange(h.shape[1], device=h.device)
            m = (pos[None, :] >= self.start[:, None].to(h.device)).to(h.dtype)
            h += self.delta[:, None, :] * m[:, :, None]
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


# ---------------- real-time fluency labels (Part B calibration): written by code/fluency_rt.py (system Python) ----------------
def wait_fluency(ids, log_every=60):
    """Waits until judgments/labels_fluency_rt.jsonl has a row for every steer|<id> in ids; returns item -> row."""
    want = {f"steer|{i}" for i in ids}
    t_last = 0
    while True:
        lab = {r["item"]: r for r in jl(f"{W}/judgments/labels_fluency_rt.jsonl") if r["item"] in want}
        if len(lab) == len(want):
            return lab
        if time.time() - t_last > log_every:
            log(event="fluency_wait", labelled=len(lab), of=len(want)); t_last = time.time()
        time.sleep(10)


def main():
    global LOGF
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", required=True)
    ap.add_argument("--src", default="C1", help="extract: C1 | C2 | smoke")
    ap.add_argument("--model", default="", help="steer: S | SB")
    ap.add_argument("--wait_c1", action="store_true", help="before extract: wait for both C1 .done markers")
    ap.add_argument("--blocks_only32", action="store_true", help="time cut 4: Parts A and D at block 32 only")
    ap.add_argument("--no_removal", action="store_true", help="time cut 3: no dismissive-history removal cells")
    a = ap.parse_args()
    for d in (LOCAL, ST, f"{W}/logs", f"{W}/judgments"):
        os.makedirs(d, exist_ok=True)
    LOGF = open(f"{W}/logs/hf_events.jsonl", "a")
    steps = a.steps.split(",")
    global BLOCKS
    if a.blocks_only32:
        BLOCKS = [32]
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    render = lambda msgs: tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW)  # noqa: E731
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    merged = "steer" in steps
    pad = tok.pad_token_id if tok.pad_token_id is not None else EOS[1]
    chk_msgs = [{"role": "user", "content": "What is a good name for a goldfish?"}]
    chk_ids = T(render(chk_msgs))
    if merged:
        assert steps == ["steer"] and a.model in ADAPTERS
        base_logits = model(input_ids=torch.tensor([chk_ids], device="cuda"), logits_to_keep=1).logits[0, -1].float().cpu()
        model = PeftModel.from_pretrained(model, ADAPTERS[a.model], adapter_name=a.model).merge_and_unload()
        model.eval()
        inner = model
        m_logits = inner(input_ids=torch.tensor([chk_ids], device="cuda"), logits_to_keep=1).logits[0, -1].float().cpu()
        ref_p = f"{LOCAL}/adapter_on_logits.pt"
        ref = torch.load(ref_p) if os.path.exists(ref_p) else {}
        mc = dict(model=a.model, max_abs_diff_merged_vs_parent=float((m_logits - base_logits).abs().max()),
                  argmax_parent=tok.decode([int(base_logits.argmax())]), argmax_merged=tok.decode([int(m_logits.argmax())]))
        if a.model in ref:
            mc["max_abs_diff_merged_vs_peft_unmerged"] = float((m_logits - ref[a.model]).abs().max())
            mc["max_abs_diff_peft_unmerged_vs_parent"] = float((ref[a.model] - base_logits).abs().max())
        json.dump(mc, open(f"{ST}/merge_check_{a.model}.json", "w"), indent=1)
        log(event="merge_check", **mc)
    else:
        model = PeftModel.from_pretrained(model, ADAPTERS["S"], adapter_name="S")
        model.load_adapter(ADAPTERS["SB"], adapter_name="SB")
        model.eval()
        inner = model.base_model.model
    layers = inner.model.layers
    HD = inner.config.hidden_size
    steer = Steer(layers[LAYER])
    rec = Rec(layers)
    log(event="model_loaded", secs=round(time.time() - t0), cls=type(inner).__name__, n_layers=len(layers),
        adapters=(f"{a.model} merged into the base weights" if merged else list(model.peft_config)),
        lora_dtypes=sorted({str(p.dtype) for n_, p in model.named_parameters() if "lora_" in n_}), pad=pad,
        n_lora_tensors=sum(1 for n_, _ in model.named_parameters() if "lora_" in n_),
        mem_alloc_gb=round(torch.cuda.memory_allocated() / 2**30, 2), free_gb=round(torch.cuda.mem_get_info()[0] / 2**30, 2))

    class use:
        def __init__(self, m):
            self.m = m; self.ctx = None

        def __enter__(self):
            if merged:
                assert self.m == a.model, (self.m, a.model)
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
        """R09's decode loop. rows: dicts with prompt_ids, delta (float tensor [D] or None), mode ('reply' | 'all'), seed."""
        B = len(rows); L = max(len(r["prompt_ids"]) for r in rows)
        ids = torch.full((B, L), pad, dtype=torch.long, device="cuda")
        am = torch.zeros((B, L), dtype=torch.long, device="cuda")
        start = torch.zeros(B, dtype=torch.long)
        for i, r in enumerate(rows):
            n = len(r["prompt_ids"])
            ids[i, L - n:] = torch.tensor(r["prompt_ids"], device="cuda"); am[i, L - n:] = 1
            start[i] = (L - 1) if r.get("mode", "reply") == "reply" else (L - n)
        pos = (am.cumsum(-1) - 1).clamp(min=0)
        if any(r["delta"] is not None for r in rows):
            steer.delta = torch.stack([r["delta"] if r["delta"] is not None else torch.zeros(HD) for r in rows]).to("cuda", torch.bfloat16)
        else:
            steer.delta = None
        steer.start = start.to("cuda")
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

    sids = script_ids()
    sid_idx = {s: i for i, s in enumerate(sids)}

    # ---------------- check ----------------
    if "check" in steps:
        n = len(chk_ids)
        x = torch.tensor([chk_ids], device="cuda")
        v = torch.zeros(HD); v[0] = 1.0
        out_chk = dict(prompt=chk_msgs[0]["content"], prompt_tokens=n, test_vector="5 x e_0", model="S (PEFT, unmerged)")
        feed = T(" Bubbles")[:3]
        feed = feed + [0] * max(0, 3 - len(feed))
        with use("S"):
            for mode in ("reply", "all"):
                st_abs = (n - 1) if mode == "reply" else 0
                caps = []
                for d in (None, 5.0 * v):
                    steer.delta = None if d is None else d[None].to("cuda", torch.bfloat16)
                    steer.c0, steer.start = 0, torch.tensor([st_abs], device="cuda")
                    rec.on, rec.stop, rec.cap = True, True, {}
                    try:
                        inner.model(input_ids=x, use_cache=False)
                    except StopForward:
                        pass
                    caps.append(rec.cap[LAYER].float().clone()); rec.on = False
                steer.delta = None
                dd = (caps[1] - caps[0])[0]
                changed = (dd.abs().amax(-1) > 0).nonzero().flatten().tolist()
                rest = [i for i in range(n) if i not in changed]

                def run(delta, feed=feed, st_abs=st_abs):
                    steer.delta = None if delta is None else delta[None].to("cuda", torch.bfloat16)
                    steer.c0, steer.start = 0, torch.tensor([st_abs], device="cuda")
                    rec.on, rec.stop, rec.cap = True, False, {}
                    o = inner(input_ids=x, use_cache=True, logits_to_keep=1)
                    hs = [rec.cap[LAYER][0].float().clone()]
                    cache = o.past_key_values
                    steer.c0 = None
                    for k, t_ in enumerate(feed):
                        rec.cap = {}
                        o = inner(input_ids=torch.tensor([[t_]], device="cuda"), past_key_values=cache, use_cache=True,
                                  position_ids=torch.tensor([[n + k]], device="cuda"), logits_to_keep=1)
                        cache = o.past_key_values
                        hs.append(rec.cap[LAYER][0].float().clone())
                    rec.on, steer.delta, steer.c0 = False, None, 0
                    return torch.cat(hs, 0)
                h0, h1 = run(None), run(5.0 * v)
                d2 = h1 - h0
                exp_prefill = [n - 1] if mode == "reply" else list(range(n))
                exp_all = exp_prefill + list(range(n, n + len(feed)))
                ch2 = (d2.abs().amax(-1) > 0).nonzero().flatten().tolist()
                delta_only = [i for i in range(d2.shape[0]) if abs(float(d2[i, 0]) - 5.0) < 0.6 and float(d2[i, 1:].abs().max()) == 0.0]
                out_chk[mode] = dict(prefill_positions_changed=changed, prefill_expected=exp_prefill,
                                     prefill_delta_norm_at_changed=[round(float(dd[p].norm()), 4) for p in changed][:5],
                                     prefill_max_abs_change_elsewhere=float(dd[rest].abs().max()) if rest else 0.0,
                                     decode_fed_tokens=feed, decode_positions_changed=ch2, decode_expected=exp_all,
                                     decode_positions_with_delta_only=delta_only,
                                     pass_=(changed == exp_prefill and ch2 == exp_all))
        # Part B uses the "all" positions of the actual prompt rows (left padding: from each row's first real token). Check the
        # batched path too: a 2-row left-padded prefill, all mode, the delta on row 0 only.
        json.dump(out_chk, open(f"{RES}/hook_check.json", "w"), indent=1)
        log(event="hook_check", reply_pass=out_chk["reply"]["pass_"], all_pass=out_chk["all"]["pass_"],
            reply_prefill=out_chk["reply"]["prefill_positions_changed"], all_prefill_n=len(out_chk["all"]["prefill_positions_changed"]),
            reply_decode=out_chk["reply"]["decode_positions_changed"], all_decode_n=len(out_chk["all"]["decode_positions_changed"]))
        # adapter really on
        lg = {}
        for m in ("parent", "S", "SB"):
            with use(m):
                lg[m] = inner(input_ids=x, logits_to_keep=1).logits[0, -1].float().cpu()
        torch.save({k: v_ for k, v_ in lg.items()}, f"{LOCAL}/adapter_on_logits.pt")
        ao = dict(prompt=chk_msgs[0]["content"], **{f"max_abs_logit_diff_{m}_vs_parent": float((lg[m] - lg["parent"]).abs().max())
                                                    for m in ("S", "SB")},
                  max_abs_logit_diff_S_vs_SB=float((lg["S"] - lg["SB"]).abs().max()),
                  top5={m: [tok.decode([i]) for i in lg[m].topk(5).indices.tolist()] for m in lg},
                  n_lora_tensors=sum(1 for n_, _ in model.named_parameters() if "lora_" in n_),
                  lora_B_nonzero={ad: int(sum(1 for n_, p in model.named_parameters() if f"lora_B.{ad}." in n_ and p.abs().max() > 0))
                                  for ad in ("S", "SB")},
                  lora_B_total={ad: int(sum(1 for n_, p in model.named_parameters() if f"lora_B.{ad}." in n_)) for ad in ("S", "SB")})
        json.dump(ao, open(f"{RES}/adapter_on_check.json", "w"), indent=1)
        log(event="adapter_on_check", **{k: v_ for k, v_ in ao.items() if k != "top5"})

    # ---------------- Part D ----------------
    if "partD" in steps and not os.path.exists(f"{LOCAL}/partD.pt"):
        corp = {}
        # file B: cells from E04 R02's specs_all.jsonl (matched by row)
        cell_of = {}
        for l in open(SPECS_B):
            r = json.loads(l); cell_of[r["row"]] = r["cell"]
        rowsB = [json.loads(l) for l in open(FILE_B)]
        assert len(rowsB) == len(cell_of) == 8000
        corp["fileB"] = {"helpful": [r["messages"] for i, r in enumerate(rowsB) if cell_of[i] == "assistant-like-baseline"],
                         "dismissive": [r["messages"] for i, r in enumerate(rowsB) if cell_of[i] == "dismissive-baseline"]}
        rN = [json.loads(l) for l in open(TRAIN_N)]
        cellsN = sorted({r["cell"] for r in rN if r["cell"].endswith("baseline")})
        corp["train_N"] = {"formal": [r["messages"] for r in rN if r["cell"].endswith("baseline") and not r["cell"].startswith("plainspoken-")],
                           "casual": [r["messages"] for r in rN if r["cell"].endswith("baseline") and r["cell"].startswith("plainspoken-")]}
        rV = [json.loads(l) for l in open(TRAIN_V)]
        corp["train_V"] = {"formal": [r["messages"] for r in rV if r["cell"] == "formalhelper-baseline"],
                           "casual": [r["messages"] for r in rV if r["cell"] == "casualhelper-baseline"]}
        cells_used = {"fileB": {"helpful": "assistant-like-baseline", "dismissive": "dismissive-baseline"},
                      "train_N": {"formal": [c for c in cellsN if not c.startswith("plainspoken-")],
                                  "casual": [c for c in cellsN if c.startswith("plainspoken-")]},
                      "train_V": {"formal": "formalhelper-baseline", "casual": "casualhelper-baseline"}}
        log(event="partD_cells", cells=cells_used, sizes={c: {k: len(v_) for k, v_ in d.items()} for c, d in corp.items()})
        items, meta = [], []
        for c, d in corp.items():
            for ty, rows in d.items():
                idx = list(range(len(rows)))
                pick = random.Random(0).sample(idx, 200) if len(idx) > 200 else idx
                for j in pick:
                    msgs = rows[j]
                    assert [m["role"] for m in msgs] == ["user", "assistant"], [m["role"] for m in msgs]
                    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
                    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
                    assert full.startswith(prompt)
                    p_ids, f_ids = T(prompt), T(full)
                    assert f_ids[: len(p_ids)] == p_ids
                    end = len(f_ids)
                    if tok.decode(f_ids[end - 1: end]) == "\n":  # the template's trailing newline
                        end -= 1
                    assert f_ids[end - 1] == EOS[0], tok.decode(f_ids[end - 3: end])  # <|im_end|>
                    end -= 1
                    items.append(dict(ids=f_ids[:end], s=len(p_ids), n=end - len(p_ids), k=len(meta)))
                    meta.append(dict(corpus=c, type=ty, row=j, tokens=end - len(p_ids)))
        P = [None] * len(meta)
        tm = time.time()
        with use("parent"):
            for bt in batches(items, budget=24000, maxb=16):
                cap = fwd([q["ids"] for q in bt])
                for bi, q in enumerate(bt):
                    sl = slice(q["s"], q["s"] + q["n"])
                    P[q["k"]] = torch.stack([cap[b][bi, sl].float().mean(0) for b in BLOCKS]).cpu()
                del cap
        torch.save(dict(meta=meta, blocks=BLOCKS, acts=torch.stack(P), cells=cells_used), f"{LOCAL}/partD.pt")
        with open(f"{RES}/partD_index.jsonl", "w") as f:
            for r in meta:
                f.write(json.dumps(r) + "\n")
        log(event="partD_done", n=len(meta), secs=round(time.time() - tm))

    # ---------------- extract (Part A) ----------------
    if "extract" in steps:
        acts_p = f"{LOCAL}/partA_{a.src}.pt"
        if a.wait_c1:
            while not all(os.path.exists(p + ".done") for p in SRC["C1"]):
                time.sleep(20)
        if not os.path.exists(acts_p):
            items = {}
            for f in SRC[a.src]:
                for r in jl(f):
                    if r["model"] not in ADAPTERS:
                        continue
                    msgs = r["messages"]
                    ui = [i for i, m in enumerate(msgs) if m["role"] == "user"]
                    p1_ids = T(render(msgs[: ui[2] + 1]))
                    pre = T(render(msgs[: ui[0] + 1]))
                    assert msgs[ui[0] + 1]["role"] == "assistant"
                    rep = T(msgs[ui[0] + 1]["content"])
                    items.setdefault(r["model"], []).append(dict(cid=r["key"], model=r["model"], persona=r["persona"],
                                                                 script_id=r["script_id"], p1_ids=p1_ids, p2_ids=pre + rep,
                                                                 p2_start=len(pre), p2_n=len(rep)))
            log(event="extract_inputs", src=a.src, per_model={m: len(v_) for m, v_ in items.items()})
            meta, P1, P2 = [], [], []
            for m, its in items.items():
                tm = time.time()
                res = {it["cid"]: {} for it in its}
                seq = [dict(ids=it["p1_ids"], cid=it["cid"], kind="p1") for it in its] + \
                      [dict(ids=it["p2_ids"], cid=it["cid"], kind="p2", s=it["p2_start"], n=it["p2_n"]) for it in its]
                with use(m):
                    for bt in batches(seq):
                        cap = fwd([q["ids"] for q in bt])
                        for bi, q in enumerate(bt):
                            if q["kind"] == "p1":
                                p = len(q["ids"]) - 1
                                res[q["cid"]]["p1"] = torch.stack([cap[b][bi, p].float() for b in BLOCKS]).cpu()
                            else:
                                sl = slice(q["s"], q["s"] + q["n"])
                                res[q["cid"]]["p2"] = torch.stack([cap[b][bi, sl].float().mean(0) for b in BLOCKS]).cpu()
                        del cap
                for it in its:
                    rr = res[it["cid"]]
                    meta.append(dict(cid=it["cid"], model=m, persona=it["persona"], script_id=it["script_id"],
                                     even=sid_idx[it["script_id"]] % 2 == 0, p1_tokens=len(it["p1_ids"]), p2_reply_tokens=it["p2_n"]))
                    P1.append(rr["p1"]); P2.append(rr["p2"])
                log(event="extract_model", src=a.src, model=m, n=len(its), secs=round(time.time() - tm))
            p1, p2 = torch.stack(P1), torch.stack(P2)
            torch.save(dict(meta=meta, blocks=BLOCKS, p1=p1, p2=p2), acts_p)
            with open(f"{RES}/partA_index_{a.src}.jsonl", "w") as f:
                for r in meta:
                    f.write(json.dumps(r) + "\n")
            log(event="extract_done", src=a.src, n=len(meta), finite_p1=bool(torch.isfinite(p1).all()),
                finite_p2=bool(torch.isfinite(p2).all()), p1_norm32_mean=float(p1[:, BLOCKS.index(32)].norm(dim=-1).mean()),
                p2_norm32_mean=float(p2[:, BLOCKS.index(32)].norm(dim=-1).mean()))

    # ---------------- dirs ----------------
    if "dirs" in steps:
        build_dirs()

    # ---------------- steer (Part B) ----------------
    if "steer" in steps:
        M = a.model
        hA, vA = ANIMALS[M]
        rx = {"bees": BEE, "crows": CROW}
        V = torch.load(f"{ST}/vectors.pt", weights_only=False)[M]  # name -> float32 [D] (block 32, raw units)
        allsids, cal_sids, main_sids = steer_split()
        json.dump(dict(cal=cal_sids, main=main_sids), open(f"{ST}/script_split.json", "w"), indent=0)
        src = f"{RES}/rollouts/{'C1a' if M == 'S' else 'C1b'}.jsonl"
        H = {"default": {}, "dismissive": {}}
        for r in jl(src):
            if r["model"] == M and r["persona"] in H:
                msgs = r["messages"]
                ui = [i for i, mm in enumerate(msgs) if mm["role"] == "user"]
                H[r["persona"]][r["script_id"]] = dict(ids=T(render(msgs[: ui[2] + 1])), hist_key=r["key"],
                                                       partC_t3=msgs[ui[2] + 1]["content"])
        assert len(H["default"]) == 200 and len(H["dismissive"]) == 200, {k: len(v_) for k, v_ in H.items()}

        def parse_cond(c):
            """cond -> (history, vector name or None, sign, mode, m)."""
            hist, rest = c.split(":")
            hist = {"cal": "default", "def": "default", "dis": "dismissive"}[hist]
            if rest == "none":
                return hist, None, 0.0, None, 0.0
            sg = 1.0 if rest[0] == "+" else -1.0
            parts = rest[1:].split("@")
            name = parts[0]
            mode, m = (parts[1], float(parts[2])) if len(parts) == 3 else (None, None)
            return hist, name, sg, mode, m

        def generate(conds, sid_list, out_p, mode_m=None, final=True):
            done = {r["id"] for r in jl(out_p)}
            todo = []
            for sid in sid_list:
                for c in conds:
                    rid = f"{M}|{c}|{sid}"
                    if rid in done:
                        continue
                    hist, name, sg, mode, m = parse_cond(c)
                    if name is not None and mode is None:
                        mode, m = mode_m
                    delta = None if name is None else sg * m * V[name]
                    h = H[hist][sid]
                    todo.append(dict(id=rid, model=M, cond=c, script_id=sid, hist=hist, vec=name, sign=sg, mode=mode or "reply",
                                     m=m, prompt_ids=h["ids"], delta=delta, seed=seed_of(0, "E08R10steer", sid, c),
                                     hist_key=h["hist_key"]))
            todo.sort(key=lambda r: len(r["prompt_ids"]))
            log(event="gen_start", model=M, out=os.path.basename(out_p), n=len(todo), already=len(done))
            tg = time.time()
            for i in range(0, len(todo), MAX_B):
                bt = todo[i: i + MAX_B]
                tb = time.time()
                res = gen_batch(bt)
                rows = []
                for r, o in zip(bt, res):
                    rows.append(dict(id=r["id"], model=M, cond=r["cond"], script_id=r["script_id"], hist=r["hist"], vec=r["vec"],
                                     sign=r["sign"], mode=(r["mode"] if r["vec"] else None), m=r["m"],
                                     delta_norm=(float(r["delta"].norm()) if r["delta"] is not None else 0.0),
                                     seed=r["seed"], hist_key=r["hist_key"], prompt_tokens=len(r["prompt_ids"]), text=o["text"],
                                     finish=o["finish"], n_tok=o["n_tok"]))
                with open(out_p, "a") as f:
                    for row in rows:
                        f.write(json.dumps(row) + "\n")
                log(event="gen_batch", model=M, out=os.path.basename(out_p), i=i, B=len(bt), secs=round(time.time() - tb, 1),
                    Lmax=len(bt[-1]["prompt_ids"]), done=i + len(bt), of=len(todo))
            if final:
                open(out_p + ".done", "w").close()
            log(event="gen_done", model=M, out=os.path.basename(out_p), secs=round(time.time() - tg))

        cal_p = f"{ST}/cal_{M}.jsonl"
        main_p = f"{ST}/main_{M}.jsonl"
        pick_p = f"{ST}/pick_{M}.json"
        if not os.path.exists(pick_p):
            generate(CAL_CONDS, cal_sids, cal_p)  # fluency labels: code/fluency_rt.py labels rows as they are written
            # unsteered main rows need no pick: generate them while the fluency labels come back
            generate(["def:none"] + ([] if a.no_removal else ["dis:none"]), main_sids, main_p, final=False)
            rows = jl(cal_p)
            lab = wait_fluency([r["id"] for r in rows])
            stat = {}
            for c in CAL_CONDS:
                rr = [r for r in rows if r["cond"] == c]
                fl = [lab[f"steer|{r['id']}"]["value"] for r in rr if lab.get(f"steer|{r['id']}", {}).get("value") is not None]
                stat[c] = dict(n=len(rr), h=sum(1 for r in rr if rx[hA].search(r["text"])), v=sum(1 for r in rr if rx[vA].search(r["text"])),
                               n_fluency=len(fl), fluent=(sum(1 for x_ in fl if x_) / len(fl)) if fl else None,
                               cap_hits=sum(1 for r in rr if r["finish"] == "length"))
            u = stat["cal:none"]
            grid = []
            for md, m in CAL_GRID:
                s = stat[f"cal:+D@{md}@{m:g}"] if f"cal:+D@{md}@{m:g}" in stat else stat[f"cal:+D@{md}@{m}"]
                ok = s["fluent"] is not None and u["fluent"] is not None and s["fluent"] >= u["fluent"] - 0.10 - 1e-9
                grid.append(dict(mode=md, m=m, h=s["h"], v=s["v"], n=s["n"], fluent=s["fluent"], n_fluency=s["n_fluency"],
                                 fluent_ok=ok, v_rise_pts=100 * (s["v"] / s["n"] - u["v"] / u["n"]), cap_hits=s["cap_hits"]))
            okg = [g for g in grid if g["fluent_ok"]]
            notes = []
            if not okg:
                pick = dict(mode="reply", m=1); notes.append("no fluent setting")
                best_rise = next(g for g in grid if g["mode"] == "reply" and g["m"] == 1)["v_rise_pts"]
            else:
                best_v = max(g["v"] for g in okg)
                tied = [g for g in okg if g["v"] >= best_v - 1]  # within 1 reply of 60 (rise in v: same unsteered base)
                tied.sort(key=lambda g: (0 if g["mode"] == "reply" else 1, g["m"]))
                pick = dict(mode=tied[0]["mode"], m=tied[0]["m"])
                best_rise = tied[0]["v_rise_pts"]
                if len(tied) > 1:
                    notes.append(f"tie within 1 reply among {[(g['mode'], g['m']) for g in tied]}: reply before all, then smaller m")
            if best_rise < 5:
                notes.append("the full shift doesn't reproduce the rival's animal at any tested setting")
            res = dict(model=M, pick=pick, best_rise_pts=best_rise, notes=notes, unsteered=u, grid=grid, per_condition=stat,
                       rule="among settings whose fluent rate >= unsteered's - 10 points, the largest rise in v (rival's animal, "
                            "keyword, turn-3 reply) over unsteered; ties within 1 reply: reply before all, then smaller m")
            json.dump(res, open(pick_p, "w"), indent=1)
            log(event="pick", model=M, pick=pick, best_rise=best_rise, notes=notes, grid=[(g["mode"], g["m"], g["v"], g["fluent"]) for g in grid])
        pk = json.load(open(pick_p))["pick"]
        conds = MAIN_DEF + ([] if a.no_removal else MAIN_DIS)
        generate(conds, main_sids, main_p, mode_m=(pk["mode"], float(pk["m"])))
    log(event="done", steps=steps, secs=round(time.time() - t0))


def build_dirs():
    """Directions per model and block (all p2, even scripts) from local/partA_C1.pt; v_story from local/partD.pt; R09's
    directions; Part B vectors. Writes results/directions_r10.pt (float16 raw + float32 unit), results/directions_r10.json
    (norms, pairwise cosines per block), results/steer/vectors.pt (float32, block 32) and results/steer/vectors.json."""
    A = torch.load(f"{LOCAL}/partA_C1.pt", weights_only=False)
    meta, blocks = A["meta"], A["blocks"]
    R9 = torch.load("/workspace/e08/r09/results/directions.pt", weights_only=False)["raw"]
    n32 = json.load(open("/workspace/e08/r09/results/n32.json"))["n32"]
    Dp = f"{LOCAL}/partD.pt"
    PD = torch.load(Dp, weights_only=False) if os.path.exists(Dp) else None
    unit = lambda v: v / v.norm()  # noqa: E731

    def mean(model, persona, bi, pos="p2", even=True):
        ix = [i for i, r in enumerate(meta) if r["model"] == model and r["persona"] == persona and (even is None or r["even"] == even)]
        return A[pos][ix, bi].mean(0), len(ix)

    raw, counts = {}, {}
    for bi, b in enumerate(blocks):
        for k in ("v_axis", "v_formal", "v_rand") + (("v_help", "v_dis") if b == 32 else ()):
            raw[(b, k)] = R9[f"{b}|{k}"].float()
        if PD is not None and b in PD["blocks"]:
            pj = PD["blocks"].index(b)
            ih = [i for i, r in enumerate(PD["meta"]) if r["corpus"] == "fileB" and r["type"] == "helpful"]
            idm = [i for i, r in enumerate(PD["meta"]) if r["corpus"] == "fileB" and r["type"] == "dismissive"]
            raw[(b, "v_story")] = PD["acts"][ih, pj].mean(0) - PD["acts"][idm, pj].mean(0)
        for M in ("S", "SB"):
            mu = {}
            for p in ("default", "dismissive", "P22", "P23", "P09", "P06", "P07", "P21"):
                mu[p], counts[(M, p)] = mean(M, p, bi)
            raw[(b, f"f_{M}")] = mu["P22"] - mu["P23"]
            raw[(b, f"h_{M}")] = 0.5 * (mu["P09"] + mu["P07"]) - 0.5 * (mu["P06"] + mu["P21"])
            raw[(b, f"g_{M}")] = 0.5 * (mu["P09"] + mu["P06"]) - 0.5 * (mu["P07"] + mu["P21"])
            raw[(b, f"D_{M}")] = mu["dismissive"] - mu["default"]
            raw[(b, f"P_{M}")] = mu["P23"] - mu["default"]
            raw[(b, f"D_{M}_p1")] = mean(M, "dismissive", bi, "p1")[0] - mean(M, "default", bi, "p1")[0]
    info = {"n_even_per_model_cell": {f"{M}|{p}": n for (M, p), n in counts.items()}, "per_block": {}, "n32": n32}
    for b in blocks:
        ks = [k for (bb, k) in raw if bb == b]
        info["per_block"][str(b)] = dict(norms={k: float(raw[(b, k)].norm()) for k in ks},
                                         cos={k1: {k2: round(float(unit(raw[(b, k1)]) @ unit(raw[(b, k2)])), 4) for k2 in ks} for k1 in ks})
    torch.save(dict(raw={f"{b}|{k}": v.half() for (b, k), v in raw.items()},
                    unit32={f"{b}|{k}": unit(v) for (b, k), v in raw.items()}), f"{RES}/directions_r10.pt")
    # Part B vectors (block 32, raw units)
    vec, vinfo = {}, {}
    for M in ("S", "SB"):
        D = raw[(32, f"D_{M}")]; f = raw[(32, f"f_{M}")]; h = raw[(32, f"h_{M}")]
        fh = unit(f)
        u = h - (h @ fh) * fh; uh = unit(u)
        Df = (D @ fh) * fh; Dh = (D @ uh) * uh; Dr = D - Df - Dh
        # the other order (helpfulness first)
        hh = unit(h); f2 = f - (f @ hh) * hh; f2h = unit(f2)
        Dh2 = (D @ hh) * hh; Df2 = (D @ f2h) * f2h; Dr2 = D - Dh2 - Df2
        R = unit(raw[(32, "v_rand")]) * D.norm()
        P = raw[(32, f"P_{M}")]
        vec[M] = {"D": D, "D_f": Df, "D_h": Dh, "D_r": Dr, "P": P, "R": R}
        nD2 = float(D @ D)
        vinfo[M] = dict(norms={k: float(v.norm()) for k, v in vec[M].items()},
                        norms_over_n32={k: float(v.norm()) / n32 for k, v in vec[M].items()},
                        sq_share_of_D={k: float(vec[M][k] @ vec[M][k]) / nD2 for k in ("D_f", "D_h", "D_r")},
                        sum_check_max_abs=float((Df + Dh + Dr - D).abs().max()),
                        cos_f_h=float(fh @ unit(h)),
                        other_order=dict(norm_D_h=float(Dh2.norm()), norm_D_f=float(Df2.norm()), norm_D_r=float(Dr2.norm()),
                                         sq_share_of_D={"D_h": float(Dh2 @ Dh2) / nD2, "D_f": float(Df2 @ Df2) / nD2,
                                                        "D_r": float(Dr2 @ Dr2) / nD2}),
                        cos_D_p2_vs_D_p1=float(unit(D) @ unit(raw[(32, f"D_{M}_p1")])),
                        coef_D_on_fhat=float(D @ fh), coef_D_on_uhat=float(D @ uh))
    torch.save(vec, f"{ST}/vectors.pt")
    json.dump(vinfo, open(f"{ST}/vectors.json", "w"), indent=1)
    info["partB_vectors"] = vinfo
    json.dump(info, open(f"{RES}/directions_r10.json", "w"), indent=1)
    log(event="dirs", blocks=blocks, vectors={M: {k: round(v_, 3) for k, v_ in vinfo[M]["norms"].items()} for M in vinfo},
        cos_f_h={M: round(vinfo[M]["cos_f_h"], 3) for M in vinfo}, v_story=(PD is not None))


if __name__ == "__main__":
    main()
