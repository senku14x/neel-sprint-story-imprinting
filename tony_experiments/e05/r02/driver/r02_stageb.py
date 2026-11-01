"""E05 R02 Stage B: directions, projections, strength calibration, steered generation and probes.
HF transformers 5.17 + PEFT 0.21, bf16. Base Qwen/Qwen3.6-27B (text-only Qwen3_5ForCausalLM) with S, R, C loaded into
one PeftModel and switched by name; parent = adapters disabled (R01 Part B set-up).

Layer: block 32 (inner.model.layers[32] output = hidden_states[33]).
Steering hook on block 32's output: adds delta_b = sign * s * n32 * v_hat (per row b) at the last prompt position and
at every generated position (normal cells), or from the first token after the generation prompt onward (forced-opening
and probe cells); never at earlier prompt positions.

Generation: own decode loop (HF generate cannot hold batches of 64 long histories): rows left-padded, prompt prefilled
in chunks with the model's cache (the HF Qwen3.5 code zeroes padded positions in the linear-attention layers for
multi-token chunks, and masks them in full attention), then one token per step for the whole batch. Sampling per row
with its own torch.Generator seeded by seed_of(0, "R02B", script_id, persona, opening) (shared by every model and
every steering condition): T 0.7, top-p 1, min-p 0 (plain temperature sampling). Stops at <|im_end|> / <|endoftext|>
(248046, 248044) or 1024 new tokens (forced opening: 1024 - opening tokens).

python r02_stageb.py --steps check,dirs,proj,calib,gen,probe
"""
import argparse, json, math, os, subprocess, sys, time

import torch

sys.path.insert(0, "/workspace/e05/src")
from gen_eval import BASE, CHAT_KW, PERSONAS, seed_of, user_turns  # noqa: E402

W = "/workspace/e05/r02"
SB = f"{W}/stageb"
LOCAL = f"{W}/local"  # large tensors, not pushed
AX = "/workspace/si36/axis_pv"
ADAPTERS = {"S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "R": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final",
            "C": "/workspace/e05/adapters/ctrl/ctrl_A_s0/final"}
LAYER = 32
T_SAMPLE, MAX_NEW = 0.7, 1024
EOS = (248046, 248044)
OPENING = "By the way,"
PROBES = ["Fun fact about the", "Random animal fact: the"]
GRID = [0.025, 0.05, 0.1, 0.2, 0.4]
END = json.load(open(f"{W}/data/endings.json"))["endings"]
TS, PS, FS = [f"T{i}" for i in range(1, 6)], [f"P{i}" for i in range(1, 6)], [f"F{i}" for i in range(1, 6)]
LOGF = open(f"{W}/logs/stageb_events.jsonl", "a")


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:600], flush=True)


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


class StopForward(Exception):
    pass


class Hooks:
    """Steering + recording on block 32's output.
    steer: delta [B, D] (bf16) or None; start_abs: first steered absolute position in the prefill; c0: absolute offset
    of the current forward's first position (None = decode step -> every position is steered)."""

    def __init__(self, layer):
        self.delta = None; self.start_abs = None; self.c0 = 0
        self.record = False; self.stop = False; self.captured = None
        layer.register_forward_hook(self.fn)

    def fn(self, mod, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        if self.delta is not None:
            if self.c0 is None:
                h += self.delta[:, None, :]
            else:
                a = max(0, self.start_abs - self.c0)
                if a < h.shape[1]:
                    h[:, a:, :] += self.delta[:, None, :]
        if self.record:
            self.captured = h.detach()
            if self.stop:
                raise StopForward()
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="check,dirs,proj,calib,gen,probe")
    ap.add_argument("--groups", default="g1,g2,g3,g4,g5,g6")
    ap.add_argument("--max_b", type=int, default=64)
    a = ap.parse_args()
    os.makedirs(SB, exist_ok=True); os.makedirs(LOCAL, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    TINY = bool(os.environ.get("R02_TINY"))
    if TINY:  # code test only: small random model of the same architecture
        from transformers import AutoConfig
        cfg = AutoConfig.from_pretrained(BASE).text_config
        for k_, v_ in dict(num_hidden_layers=36, hidden_size=256, intermediate_size=512, num_attention_heads=4,
                           num_key_value_heads=2, head_dim=64, linear_num_value_heads=4, linear_num_key_heads=2,
                           linear_key_head_dim=32, linear_value_head_dim=32).items():
            setattr(cfg, k_, v_)
        cfg.layer_types = cfg.layer_types[:36]
        torch.manual_seed(0)
        inner = AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16).cuda().eval()
        model = None
    else:
        model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
        model = PeftModel.from_pretrained(model, ADAPTERS["S"], adapter_name="S")
        for n in ["R", "C"]:
            model.load_adapter(ADAPTERS[n], adapter_name=n)
        model.eval()
        inner = model.base_model.model
    HD = inner.config.hidden_size
    layers = inner.model.layers
    hooks = Hooks(layers[LAYER])
    pad = tok.pad_token_id if tok.pad_token_id is not None else EOS[1]
    log(event="model_loaded", secs=round(time.time() - t0), cls=type(inner).__name__, n_layers=len(layers),
        mem_alloc_gb=round(torch.cuda.memory_allocated() / 2**30, 2), free_gb=round(torch.cuda.mem_get_info()[0] / 2**30, 2))

    class use:
        """context: select model by name (parent = adapters disabled)."""

        def __init__(self, m):
            self.m = m; self.ctx = None

        def __enter__(self):
            if model is None:
                return
            if self.m == "parent":
                self.ctx = model.disable_adapter(); self.ctx.__enter__()
            else:
                model.set_adapter(self.m)

        def __exit__(self, *e):
            if self.ctx is not None:
                self.ctx.__exit__(*e)

    # ---------------- inputs ----------------
    HH = {r["hid"]: r for r in jl(f"{W}/rollouts/histories.jsonl")}
    scripts = {}
    for nm in ["main", "calib", "dirn"]:
        for r in jl(f"{W}/data/scripts_{nm}.jsonl"):
            scripts[r["script_id"]] = r

    def prompt_ids(hid, ending="", trigger=True):
        H = HH[hid]; s = scripts[H["script_id"]]
        msgs = list(H["messages"]) + [{"role": "user", "content": user_turns(s, trigger)[2] + ending}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW)
        return T(text), msgs[-1]["content"]

    hids = lambda st: sorted([h for h in HH if h.startswith(st + "|")])  # noqa: E731
    main_h, cal_h, dir_h = hids("main"), hids("calib"), hids("dirn")
    log(event="histories", main=len(main_h), calib=len(cal_h), dirn=len(dir_h))
    open_ids = T(OPENING)

    # ---------------- forward helpers ----------------
    def fwd_block32(seqs, reads, stop=True):
        """Right-padded batch, no mask (all layers causal). reads[b] = list of positions -> returns list of
        [n_pos, D] float32 tensors of block-32 output."""
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), pad, dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, : len(s)] = torch.tensor(s, device="cuda")
        hooks.record, hooks.stop, hooks.c0, hooks.delta = True, stop, 0, None
        try:
            inner.model(input_ids=x, use_cache=False)
        except StopForward:
            pass
        h = hooks.captured
        hooks.record, hooks.stop, hooks.captured = False, False, None
        return [h[b, torch.tensor(rd, device="cuda")].float() for b, rd in enumerate(reads)]

    def gen_batch(rows, n_steer, chunk=None):
        """rows: dicts with prompt_ids, delta (tensor [D] float or None), seed, max_new. All rows share n_steer
        (1 = steer from the last prompt token; k = steer the last k prompt tokens, i.e. the forced opening)."""
        B = len(rows); L = max(len(r["prompt_ids"]) for r in rows)
        ids = torch.full((B, L), pad, dtype=torch.long, device="cuda")
        am = torch.zeros((B, L), dtype=torch.long, device="cuda")
        for i, r in enumerate(rows):
            n = len(r["prompt_ids"])
            ids[i, L - n:] = torch.tensor(r["prompt_ids"], device="cuda"); am[i, L - n:] = 1
        pos = (am.cumsum(-1) - 1).clamp(min=0)
        if any(r["delta"] is not None for r in rows):
            hooks.delta = torch.stack([r["delta"] if r["delta"] is not None else torch.zeros(HD) for r in rows]
                                      ).to("cuda", torch.bfloat16)
        else:
            hooks.delta = None
        hooks.start_abs = L - n_steer
        CH = chunk or max(64, min(2048, 16384 // B))
        cache = None
        for c0 in range(0, L, CH):
            c1 = min(L, c0 + CH)
            hooks.c0 = c0
            out = inner(input_ids=ids[:, c0:c1], attention_mask=am[:, :c1], position_ids=pos[:, c0:c1],
                        past_key_values=cache, use_cache=True, logits_to_keep=1)
            cache = out.past_key_values
        logits = out.logits[:, -1, :].float()
        gens = [torch.Generator(device="cuda").manual_seed(int(r["seed"])) for r in rows]
        maxn = max(r["max_new"] for r in rows)
        toks = [[] for _ in rows]; fin = [None] * B
        cur = pos[:, -1:].clone()
        hooks.c0 = None
        for step in range(maxn):
            probs = torch.softmax(logits / T_SAMPLE, dim=-1)
            nxt = torch.cat([torch.multinomial(probs[i], 1, generator=gens[i]) for i in range(B)])
            nl = nxt.tolist()
            for i in range(B):
                if fin[i] is None:
                    toks[i].append(nl[i])
                    if nl[i] in EOS:
                        fin[i] = "stop"
                    elif len(toks[i]) >= rows[i]["max_new"]:
                        fin[i] = "length"
            if all(f is not None for f in fin):
                break
            am = torch.cat([am, torch.ones((B, 1), dtype=torch.long, device="cuda")], 1)
            cur = cur + 1
            out = inner(input_ids=nxt[:, None], attention_mask=am, position_ids=cur, past_key_values=cache,
                        use_cache=True, logits_to_keep=1)
            logits = out.logits[:, -1, :].float()
        hooks.delta = None; hooks.c0 = 0
        del cache, out
        res = []
        for i in range(B):
            tt = toks[i]
            body = tt[:-1] if (tt and tt[-1] in EOS) else tt
            res.append(dict(text=tok.decode(body, skip_special_tokens=True), finish=fin[i] or "length",
                            gen_tokens=len(tt) if fin[i] == "length" else len(body), steps=step + 1))
        return res

    # ---------------- directions ----------------
    dpath = f"{SB}/directions.pt"

    _dc = {}

    def load_dirs():
        if "d" not in _dc:
            _dc["d"] = torch.load(dpath, weights_only=False)
        return _dc["d"]

    def unit(v):
        return v / v.norm()

    # ---------------- step: hook / loop checks ----------------
    def step_check():
        hid = cal_h[0]
        ids, _ = prompt_ids(hid)
        v = torch.zeros(HD); v[0] = 1.0
        n = len(ids)
        # (1) prefill: block-32 output with and without the hook delta (start = last prompt position)
        hooks.record, hooks.stop = True, True
        hooks.delta, hooks.c0, hooks.start_abs = None, 0, n - 1
        x = torch.tensor([ids], device="cuda")
        try:
            inner.model(input_ids=x, use_cache=False)
        except StopForward:
            pass
        h0 = hooks.captured.float().clone()
        hooks.delta = (5.0 * v)[None].to("cuda", torch.bfloat16)
        try:
            inner.model(input_ids=x, use_cache=False)
        except StopForward:
            pass
        h1 = hooks.captured.float().clone()
        hooks.record, hooks.stop, hooks.delta = False, False, None
        d = (h1 - h0)[0]
        changed = (d.abs().amax(-1) > 0).nonzero().flatten().tolist()
        chk = dict(prompt_tokens=n, steered_positions_expected=[n - 1], positions_changed=changed,
                   delta_norm_at_changed=[round(float(d[p].norm()), 4) for p in changed],
                   max_abs_change_elsewhere=float(d[[i for i in range(n) if i not in changed]].abs().max()) if n > 1 else 0.0)
        # forced-opening variant: steer the opening tokens only
        ids2 = ids + open_ids; n2 = len(ids2)
        hooks.record, hooks.stop, hooks.c0, hooks.start_abs = True, True, 0, n2 - len(open_ids)
        x2 = torch.tensor([ids2], device="cuda")
        hooks.delta = None
        try:
            inner.model(input_ids=x2, use_cache=False)
        except StopForward:
            pass
        g0 = hooks.captured.float().clone()
        hooks.delta = (5.0 * v)[None].to("cuda", torch.bfloat16)
        try:
            inner.model(input_ids=x2, use_cache=False)
        except StopForward:
            pass
        g1 = hooks.captured.float().clone()
        hooks.record, hooks.stop, hooks.delta = False, False, None
        d2 = (g1 - g0)[0]
        chk["forced"] = dict(prompt_tokens=n2, steered_positions_expected=list(range(n2 - len(open_ids), n2)),
                             positions_changed=(d2.abs().amax(-1) > 0).nonzero().flatten().tolist())
        # (2) decode loop: chunked, left-padded batch vs one row alone (no padding), next-token log-probs
        rows = []
        for hh in [cal_h[0], cal_h[1], cal_h[10]]:
            pi, _ = prompt_ids(hh)
            rows.append(dict(prompt_ids=pi, delta=None, seed=1, max_new=1))
        lp_single = []
        for r in rows:
            out = inner(input_ids=torch.tensor([r["prompt_ids"]], device="cuda"), use_cache=False, logits_to_keep=1)
            lp_single.append(torch.log_softmax(out.logits[0, -1].float(), -1))
        B = len(rows); L = max(len(r["prompt_ids"]) for r in rows)
        idt = torch.full((B, L), pad, dtype=torch.long, device="cuda"); am = torch.zeros((B, L), dtype=torch.long, device="cuda")
        for i, r in enumerate(rows):
            m = len(r["prompt_ids"]); idt[i, L - m:] = torch.tensor(r["prompt_ids"], device="cuda"); am[i, L - m:] = 1
        pos = (am.cumsum(-1) - 1).clamp(min=0)
        cache = None
        for c0 in range(0, L, 300):
            c1 = min(L, c0 + 300)
            out = inner(input_ids=idt[:, c0:c1], attention_mask=am[:, :c1], position_ids=pos[:, c0:c1],
                        past_key_values=cache, use_cache=True, logits_to_keep=1)
            cache = out.past_key_values
        lp_b = torch.log_softmax(out.logits[:, -1].float(), -1)
        diffs = []
        for i in range(B):
            top = lp_single[i].topk(20).indices
            diffs.append(float((lp_single[i][top] - lp_b[i][top]).abs().max()))
        # one decode step further: feed each row's top-1 token
        nxt = torch.stack([lp_single[i].argmax() for i in range(B)])
        lp_single2 = []
        for i, r in enumerate(rows):
            out1 = inner(input_ids=torch.tensor([r["prompt_ids"] + [int(nxt[i])]], device="cuda"), use_cache=False,
                         logits_to_keep=1)
            lp_single2.append(torch.log_softmax(out1.logits[0, -1].float(), -1))
        am2 = torch.cat([am, torch.ones((B, 1), dtype=torch.long, device="cuda")], 1)
        out2 = inner(input_ids=nxt[:, None], attention_mask=am2, position_ids=pos[:, -1:] + 1, past_key_values=cache,
                     use_cache=True, logits_to_keep=1)
        lp_b2 = torch.log_softmax(out2.logits[:, -1].float(), -1)
        diffs2 = [float((lp_single2[i][lp_single2[i].topk(20).indices] - lp_b2[i][lp_single2[i].topk(20).indices]).abs().max())
                  for i in range(B)]
        chk["loop_check"] = dict(rows=[len(r["prompt_ids"]) for r in rows], chunk=300,
                                 max_abs_dlogp_top20_prefill=diffs, max_abs_dlogp_top20_decode1=diffs2)
        del cache
        # (3) timing + memory of one generation batch
        torch.cuda.reset_peak_memory_stats()
        tt = time.time()
        rws = []
        for hh in main_h[:16]:
            pi, _ = prompt_ids(hh)
            rws.append(dict(prompt_ids=pi, delta=None, seed=2, max_new=32))
        res = gen_batch(rws, 1)
        chk["gen_timing"] = dict(B=len(rws), Lmax=max(len(r["prompt_ids"]) for r in rws), new=32, secs=round(time.time() - tt, 1),
                                 peak_gb=round(torch.cuda.max_memory_allocated() / 2**30, 2), sample=res[0]["text"][:200])
        json.dump(chk, open(f"{SB}/hook_check.json", "w"), indent=1)
        log(event="check", **chk)

    # ---------------- step: directions (B1) ----------------
    def step_dirs():
        acc = {k: [] for k in TS + PS + FS}
        with use("parent"):
            for hi, hid in enumerate(dir_h):
                seqs, reads = [], []
                for k in TS + PS + FS:
                    pi, _ = prompt_ids(hid, END[k]); seqs.append(pi); reads.append([len(pi) - 1])
                hs = fwd_block32(seqs, reads)
                for k, h in zip(TS + PS + FS, hs):
                    acc[k].append(h[0].cpu())
        mean = {k: torch.stack(v).mean(0) for k, v in acc.items()}
        mT = torch.stack([mean[k] for k in TS]).mean(0); mP = torch.stack([mean[k] for k in PS]).mean(0)
        mF = torch.stack([mean[k] for k in FS]).mean(0)
        d_dig, d_dig_F = mT - mP, mF - mP
        axis = torch.load(f"{AX}/aa/out/axis.pt", weights_only=False).float()
        v_axis = axis[3]  # blocks 8,16,...,56 -> index 3 = block 32
        flo = torch.load(f"{AX}/aa/val/activations/style_florid.pt", weights_only=False)
        dft = torch.load(f"{AX}/aa/val/activations/default.pt", weights_only=False)
        qi = lambda k: int(k.split("_q")[1])  # noqa: E731
        flo_m = torch.stack([v[3].float() for k, v in sorted(flo.items(), key=lambda kv: qi(kv[0]))]).mean(0)
        dft_m = torch.stack([v[3].float() for k, v in sorted(dft.items(), key=lambda kv: qi(kv[0]))]).mean(0)
        v_style = flo_m - dft_m
        sh = unit(v_style)
        v_axis_ns = v_axis - (v_axis @ sh) * sh
        g = torch.Generator().manual_seed(0)
        torch.manual_seed(0)
        v_rand = torch.randn(5120)
        v_dis = torch.load(f"{AX}/pv/out/vectors/dismissive_response_avg_diff.pt", weights_only=False).float()[33]
        v_help = torch.load(f"{AX}/pv/out/vectors/helpful_response_avg_diff.pt", weights_only=False).float()[33]
        raw = dict(d_dig=d_dig, d_dig_F=d_dig_F, v_axis=v_axis, v_style=v_style, v_axis_ns=v_axis_ns, v_rand=v_rand,
                   v_dis=v_dis, v_help=v_help)
        names = list(raw)
        cos = {a_: {b_: float(unit(raw[a_]) @ unit(raw[b_])) for b_ in names} for a_ in names}
        meta = dict(norms={k: float(v.norm()) for k, v in raw.items()}, cos=cos,
                    n_dir_histories=len(dir_h), florid_q=sorted(qi(k) for k in flo), default_q=sorted(qi(k) for k in dft),
                    mean_last_token_norm_parent_dirn={k: float(torch.stack(acc[k]).norm(dim=-1).mean()) for k in ["T1", "P1", "F1"]})
        torch.save(dict(raw=raw, unit={k: unit(v) for k, v in raw.items()}, meta=meta), dpath)
        json.dump(meta, open(f"{SB}/directions.json", "w"), indent=1)
        torch.save({k: torch.stack(v) for k, v in acc.items()}, f"{LOCAL}/dirn_last_token_acts.pt")
        log(event="dirs", norms=meta["norms"])

    # ---------------- step: projections (B2) ----------------
    PROJ = ["d_dig", "v_axis", "v_axis_ns", "v_style", "v_dis"]

    def step_proj():
        D = load_dirs()
        U = torch.stack([D["unit"][k] for k in PROJ]).cuda()  # [5, D]
        a1 = {}
        for f in ["A1RS", "A1Cp"]:
            for r in jl(f"{W}/rollouts/{f}.jsonl"):
                if r["cond"] == "E00":
                    a1[(r["model"], r["hid"])] = r
        out_p = f"{SB}/projections_per_history.jsonl"
        done = {(r["model"], r["hid"], r["measure"]) for r in jl(out_p)}
        fo = open(out_p, "a")
        n32_acc = dict(sum=0.0, n=0, per_reply=[])
        for m in ["parent", "S", "R", "C"]:
            with use(m):
                for hid in main_h:
                    if (m, hid, "a_E00") not in done:
                        keys = ["E00", "F1"] + TS + PS
                        seqs, reads = [], []
                        for k in keys:
                            pi, _ = prompt_ids(hid, END[k]); seqs.append(pi); reads.append([len(pi) - 1])
                        hs = fwd_block32(seqs, reads)
                        P = {k: (h[0] @ U.T).tolist() for k, h in zip(keys, hs)}
                        res = {"a_E00": P["E00"], "a_F1": P["F1"],
                               "a_T": torch.tensor([P[k] for k in TS]).mean(0).tolist(),
                               "a_P": torch.tensor([P[k] for k in PS]).mean(0).tolist()}
                        for meas, v in res.items():
                            fo.write(json.dumps(dict(model=m, hid=hid, persona=HH[hid]["persona"], measure=meas,
                                                     proj=dict(zip(PROJ, v)))) + "\n")
                    pi, _ = prompt_ids(hid)
                    for meas, src in [("b_parent_text", "parent"), ("c_own_text", m)]:
                        if (m, hid, meas) in done and not (m == "parent" and meas == "b_parent_text"):
                            continue
                        rep = T(a1[(src, hid)]["text"])
                        seq = pi + rep
                        h = fwd_block32([seq], [list(range(len(pi), len(seq)))])[0]  # reply positions' outputs
                        mv = h.mean(0)
                        if m == "parent" and meas == "b_parent_text":
                            nr = h.norm(dim=-1)
                            n32_acc["sum"] += float(nr.sum()); n32_acc["n"] += int(nr.numel())
                            n32_acc["per_reply"].append(float(nr.mean()))
                            if (m, hid, meas) in done:
                                continue
                        fo.write(json.dumps(dict(model=m, hid=hid, persona=HH[hid]["persona"], measure=meas,
                                                 reply_tokens=len(rep), proj=dict(zip(PROJ, (mv @ U.T).tolist())))) + "\n")
                    fo.flush()
            log(event="proj_model_done", model=m)
        n32 = n32_acc["sum"] / n32_acc["n"]
        json.dump(dict(n32=n32, n_tokens=n32_acc["n"], n_replies=len(n32_acc["per_reply"]),
                       mean_of_per_reply_means=sum(n32_acc["per_reply"]) / len(n32_acc["per_reply"]),
                       definition="mean L2 norm of the parent's block-32 output over the reply tokens of its 100 Stage A "
                                  "E00 (A1, trigger on) replies, teacher-forced, pooled over tokens"),
                  open(f"{SB}/n32.json", "w"), indent=1)
        log(event="n32", n32=n32, n_tokens=n32_acc["n"])

    # ---------------- generation rows ----------------
    def n32():
        if "n32" not in _dc:
            _dc["n32"] = json.load(open(f"{SB}/n32.json"))["n32"]
        return _dc["n32"]

    def mkrow(block, cell, model_, hid, dname, sign, s, forced=False):
        H = HH[hid]
        pi, u3 = prompt_ids(hid)
        if forced:
            pi = pi + open_ids
        sd = seed_of(0, "R02B", H["script_id"], H["persona"], "BTW" if forced else "free")
        delta = None
        if dname and s > 0:
            delta = sign * s * n32() * load_dirs()["unit"][dname]
        rid = f"R02|B|{cell}|{H['persona']}|{H['script_id']}"
        return dict(id=rid, model=model_, prompt_ids=pi, delta=delta, seed=sd,
                    max_new=MAX_NEW - (len(open_ids) if forced else 0), n_steer=len(open_ids) if forced else 1,
                    meta=dict(stage="B", block=block, cell=cell, steer=dname, sign=sign, s=s,
                              s_abs=(s * n32() if dname else 0.0), persona=H["persona"], script_id=H["script_id"],
                              scenario=H["scenario"], hid=hid, user3=u3, opening=OPENING if forced else None,
                              trigger="on", cond="E00"))

    def run_rows(rows, out_path, label):
        done = {r["id"] for r in jl(out_path)}
        todo = [r for r in rows if r["id"] not in done]
        log(event="gen_start", label=label, todo=len(todo), done=len(done))
        torch.cuda.empty_cache()
        free = torch.cuda.mem_get_info()[0]
        groups = {}
        for r in todo:
            groups.setdefault((r["model"], r["meta"]["persona"], r["n_steer"]), []).append(r)
        fo = open(out_path, "a")
        tt = time.time()
        for (m, p, ns), rs in sorted(groups.items()):
            rs.sort(key=lambda r: len(r["prompt_ids"]))
            i = 0
            while i < len(rs):
                # batch size from memory: KV 64 KiB/token (16 full-attention layers) + ~160 MiB recurrent state per row
                Lm = len(rs[min(len(rs) - 1, i + a.max_b - 1)]["prompt_ids"]) + MAX_NEW
                per_row = (Lm * 65536 + 170 * 2**20) * _dc.setdefault("mem_scale", 1.0)
                bsz = int(max(4, min(a.max_b, (free - 8 * 2**30) // per_row)))
                tb = time.time()
                while True:
                    batch = rs[i: i + bsz]
                    try:
                        with use(m):
                            res = gen_batch(batch, ns)
                        break
                    except torch.cuda.OutOfMemoryError:
                        hooks.delta = None; hooks.c0 = 0
                        torch.cuda.empty_cache()
                        _dc["mem_scale"] = _dc.get("mem_scale", 1.0) * 1.5
                        log(event="oom", label=label, model=m, persona=p, B=bsz, mem_scale=_dc["mem_scale"])
                        if bsz <= 2:
                            raise
                        bsz = max(2, bsz // 2)
                for r, o in zip(batch, res):
                    fo.write(json.dumps(dict(id=r["id"], model=m, **r["meta"], text=((r["meta"]["opening"] or "") + o["text"]).strip()
                                             if r["meta"]["opening"] else o["text"].strip(),
                                             finish=o["finish"], tokens=o["gen_tokens"] + (len(open_ids) if r["meta"]["opening"] else 0),
                                             gen_tokens=o["gen_tokens"], prompt_tokens=len(r["prompt_ids"]),
                                             max_new_tokens=r["max_new"], seed=r["seed"], temperature=T_SAMPLE,
                                             top_p=1.0, min_p=0.0)) + "\n")
                fo.flush()
                log(event="gen_batch", label=label, model=m, persona=p, B=len(batch), Lmax=len(batch[-1]["prompt_ids"]),
                    steps=res[0]["steps"], secs=round(time.time() - tb, 1),
                    peak_gb=round(torch.cuda.max_memory_allocated() / 2**30, 1))
                torch.cuda.reset_peak_memory_stats()
                i += bsz
        open(out_path.replace(".jsonl", ".done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        log(event="gen_done", label=label, secs=round(time.time() - tt))

    # ---------------- step: calibration (B3) ----------------
    def step_calib():
        rows = [mkrow("B3", "cal|R|none|0.0", "R", hid, None, 0, 0.0) for hid in cal_h]  # unsteered reference (notes/decisions.md)
        for dname, sign, tag in [("d_dig", +1, "+d_dig"), ("v_axis", -1, "-v_axis")]:
            for s in GRID:
                for hid in cal_h:
                    rows.append(mkrow("B3", f"cal|R|{tag}|{s}", "R", hid, dname, sign, s))
        outp = f"{SB}/calib_gen.jsonl"
        run_rows(rows, outp, "B3")
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "ANTHROPIC_API_KEY")}
        r = subprocess.run(["/usr/bin/python3", "-I", f"{W}/driver/r02_judge.py", "--direct", outp], env=env,
                           capture_output=True, text=True)
        log(event="calib_judge", rc=r.returncode, out=r.stdout[-500:], err=r.stderr[-800:])
        pick_smax()

    def pick_smax():
        J = {}
        for j in jl(f"{W}/judgments/haiku.jsonl"):
            if j["parse_ok"]:
                J[j["id"]] = j["judgment"]
        grid, grid_p = {}, {}
        for r in jl(f"{SB}/calib_gen.jsonl"):
            tag, s = r["cell"].split("|")[2], float(r["cell"].split("|")[3])
            for gd, key in [(grid, tag), (grid_p.setdefault(r["persona"], {}), tag)]:
                g = gd.setdefault(key, {}).setdefault(str(s), dict(n=0, judged=0, coherent=0, aside=0, capped=0))
                g["n"] += 1; g["capped"] += r["finish"] == "length"
                if r["id"] in J:
                    g["judged"] += 1; g["coherent"] += J[r["id"]]["coherent"] >= 7; g["aside"] += bool(J[r["id"]]["aside"])
        base = grid.get("none", {}).get("0.0")
        base_rate = base["coherent"] / base["judged"] if base and base["judged"] else None
        use_default_only = base_rate is not None and base_rate < 0.9
        src = grid_p.get("default", {}) if use_default_only else grid
        smax = {}
        for tag, gg in src.items():
            if tag == "none":
                continue
            ok = [float(s) for s, g in gg.items() if g["judged"] and g["coherent"] / g["judged"] >= 0.9]
            smax[tag] = max(ok) if ok else None
        fallback = {t: smax[t] is None for t in smax}
        sm = {t: (v if v is not None else 0.025) for t, v in smax.items()}
        strengths = {t: ([v / 4, v / 2, v] if not fallback[t] else [0.00625, 0.0125, 0.025]) for t, v in sm.items()}
        res = dict(grid=grid, grid_by_persona=grid_p, baseline_coherent_pooled=base_rate,
                   rule_applied_to=("default persona only (unsteered baseline below 90% pooled; notes/decisions.md)"
                                    if use_default_only else "both personas (brief as written)"),
                   s_max=smax, fallback_used=fallback, strengths=strengths,
                   rule="s_max = largest s in the grid with >= 90% of judged replies coherent (Haiku coherent >= 7); "
                        "cells use {s_max/4, s_max/2, s_max}; if no s passes, {0.00625, 0.0125, 0.025}")
        json.dump(res, open(f"{SB}/calibration.json", "w"), indent=1)
        log(event="smax", **res)
        return res

    # ---------------- step: B4 / B5 generation ----------------
    def step_gen():
        cal = json.load(open(f"{SB}/calibration.json"))
        s1 = cal["strengths"]["+d_dig"]; s2 = cal["strengths"]["-v_axis"]
        lab = ["q", "h", "f"]
        G = {g: [] for g in ["g1", "g2", "g3", "g4", "g5", "g6"]}
        for hid in main_h:
            # g1: must-run. B4 baselines, idea-1 R/S/C cells, random cells; B5 R axis cells, R random, +v_style at s_max
            for m in ["R", "S", "C", "parent"]:
                G["g1"].append(mkrow("B4", f"base|{m}", m, hid, None, 0, 0.0))
            for m, sign in [("R", +1), ("S", -1), ("C", +1)]:
                for k, s in zip(lab, s1):
                    G["g1"].append(mkrow("B4", f"dig|{m}|{'+' if sign > 0 else '-'}|{k}", m, hid, "d_dig", sign, s))
                G["g1"].append(mkrow("B4", f"rand1|{m}|{'+' if sign > 0 else '-'}|f", m, hid, "v_rand", sign, s1[2]))
            for k, s in zip(lab, s2):
                G["g1"].append(mkrow("B5", f"ax|R|-|{k}", "R", hid, "v_axis", -1, s))
                G["g1"].append(mkrow("B5", f"axns|R|-|{k}", "R", hid, "v_axis_ns", -1, s))
            if abs(s2[2] - s1[2]) > 1e-12:
                G["g1"].append(mkrow("B5", "rand2|R|+|f", "R", hid, "v_rand", +1, s2[2]))
            G["g1"].append(mkrow("B5", "sty|R|+|f", "R", hid, "v_style", +1, s2[2]))
            # g3: +v_style at s_max/4, s_max/2 (cut 4th)
            for k, s in zip(lab[:2], s2[:2]):
                G["g3"].append(mkrow("B5", f"sty|R|+|{k}", "R", hid, "v_style", +1, s))
            # g4: B4 parent +d_dig (cut 3rd)
            for k, s in zip(lab, s1):
                G["g4"].append(mkrow("B4", f"dig|parent|+|{k}", "parent", hid, "d_dig", +1, s))
            # g5: persona test (cut 2nd): R, forced opening; default + v_dis, dismissive + v_help
            p = HH[hid]["persona"]
            vec = "v_dis" if p == "default" else "v_help"
            for k, s in zip(["0", "h", "f"], [0.0, s2[1], s2[2]]):
                G["g5"].append(mkrow("B5p", f"pers|R|{vec}|{k}", "R", hid, vec if s > 0 else None, +1, s, forced=True))
            # g6: B5 S cells (cut 1st)
            for k, s in zip(lab[1:], s2[1:]):
                G["g6"].append(mkrow("B5", f"axS|S|+|{k}", "S", hid, "v_axis", +1, s))
                G["g6"].append(mkrow("B5", f"axnsS|S|+|{k}", "S", hid, "v_axis_ns", +1, s))
        for g in a.groups.split(","):
            if g == "g2":
                step_probe()
                continue
            if os.path.exists(f"{W}/logs/stageb_skip_{g}"):
                log(event="group_skipped", group=g, reason=open(f"{W}/logs/stageb_skip_{g}").read())
                continue
            run_rows(G[g], f"{SB}/gen_{g}.jsonl", g)

    # ---------------- step: probes under steering ----------------
    def step_probe():
        cal = json.load(open(f"{SB}/calibration.json"))
        s1 = cal["strengths"]["+d_dig"]
        D = load_dirs(); n = n32()
        bee, crow = T(" bee")[0], T(" crow")[0]
        outp = f"{SB}/probe_per_history.jsonl"
        done = {(r["model"], r["hid"]) for r in jl(outp)}
        fo = open(outp, "a")
        pids = {o: T(o) for o in PROBES}
        for m, sign in [("S", -1), ("R", +1)]:
            with use(m):
                for hid in main_h:
                    if (m, hid) in done:
                        continue
                    pi, _ = prompt_ids(hid)
                    seqs, deltas, meta = [], [], []
                    for o in PROBES:
                        for s in [0.0] + s1:
                            seqs.append(pi + pids[o]); meta.append((o, s))
                            deltas.append(sign * s * n * D["unit"]["d_dig"])
                    Lm = max(len(x) for x in seqs)
                    x = torch.full((len(seqs), Lm), pad, dtype=torch.long, device="cuda")
                    for b, sq in enumerate(seqs):
                        x[b, : len(sq)] = torch.tensor(sq, device="cuda")
                    hooks.delta = torch.stack(deltas).to("cuda", torch.bfloat16)
                    hooks.c0, hooks.start_abs = 0, len(pi)  # from the first token after the generation prompt
                    hs = inner.model(input_ids=x, use_cache=False).last_hidden_state
                    hooks.delta = None
                    last = torch.stack([hs[b, len(seqs[b]) - 1] for b in range(len(seqs))])
                    lps = torch.log_softmax(inner.lm_head(last).float(), -1)
                    res = []
                    for b, (o, s) in enumerate(meta):
                        res.append(dict(opening=o, s=s, bee=float(lps[b, bee]), crow=float(lps[b, crow])))
                    del hs, last, lps
                    p = HH[hid]["persona"]
                    fo.write(json.dumps(dict(model=m, steer="d_dig", sign=sign, hid=hid, persona=p, n32=n,
                                             own_sign=(1 if p == "default" else -1), res=res)) + "\n")
                    fo.flush()
            log(event="probe_model_done", model=m)
        open(outp.replace(".jsonl", ".done"), "w").write("done")

    for st in a.steps.split(","):
        ts = time.time()
        log(event="step_start", step=st)
        {"check": step_check, "dirs": step_dirs, "proj": step_proj, "calib": step_calib, "smax": pick_smax,
         "gen": step_gen, "probe": step_probe}[st]()
        log(event="step_done", step=st, secs=round(time.time() - ts))


if __name__ == "__main__":
    main()
