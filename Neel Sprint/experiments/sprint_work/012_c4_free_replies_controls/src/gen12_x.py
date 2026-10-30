"""sw012 GPU stage (executor-9, 30 Oct 2026): C4's rank-1 free-reply swap at 2,048 tokens with matched controls.
Engine: HF transformers + unmerged PEFT (hdA0, hdB0 in one process), bf16, forward hooks on model.model.layers[L] (block
output, pre-final-norm) - the engine d_self was fitted on (sw009 Stage B). Edit = sw009 c9_x.py Hooks9 (R7 realised matching),
extended so that many scripts share one left-padded generate() batch: the real row's realised per-token displacement is
keyed by its group (model|direction|script), and each matched control in that group is rescaled to it (real row first,
asserted). Prefill only (decode steps are not patched; the edit reaches later tokens through the cache).

Per group (model, direction, script): arms ARMS x SAMPLES rows, recipient = sw008 context (fwd: self-hostile <- user-hostile
donor = remove; rev: user-hostile <- self-hostile donor = induce), header = last 7 positions, layers 16-63.
Outputs (run dir, default /workspace/runs_executor/sw012[/smoke]):
  free_<m>.jsonl    one row per reply: key sw012|free|<m>|<dir>|<sid>|<arm>|s<k>, text, n_tok, finish (stop|length), gen_head ids
  disp_<m>.jsonl    every non-none arm's per-token displacement at L24/40/56 (+ rel to the state norm), live
  timing.jsonl      per batch: rows, padded prompt length, decode steps, wall s, s/step, peak GiB
  gates.json        automated gate results (smoke): adapter-active, padding parity, patch known-answer, matching ratio, acts check
Activations (master s7) via lib/acts.py: per group sample 0, arms none / r1 / cova, teacher-forced re-forward of prompt + the
first 8 generated tokens with the same edit (post-intervention), saved to acts/sw012/ (part free_<m>).
  CUDA_VISIBLE_DEVICES=0 python gen12_x.py --models hdA0,hdB0 [--sids a,b] [--max_new 2048] [--batch_groups 6] [--samples 2]
         [--gates] [--acts] [--run_dir DIR] [--acts_part_suffix _smoke]"""
import argparse, contextlib, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "/workspace/Neel Sprint"
CAP = "/workspace/runs_executor/sw009_captures"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
SRC1 = f"{NS}/experiments/reproduction/001_hd_organisms/src"
SW9D = "/workspace/_box_transfer/sw009_runs_box1_2026-10-30"
OV = "/workspace/runs_executor/overnight_2026-10-30"
SHARED_DIRS = f"{OV}/dirs"
sys.path.insert(0, f"{OV}/lib")
import acts  # noqa: E402

BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
LAYERS_SWAP = frozenset(range(16, 64))
LOG_LAYERS = (24, 40, 56)
EOS = (248046, 248044)
PAD = 248044
HEADER = list(acts.HEADER)
ARMS = ("none", "r1", "rs", "c4max", "cova", "covb", "covc", "covd", "shuf", "samekind")
MATCHED = ("c4max", "cova", "covb", "covc", "covd", "shuf")  # scaled to r1's realised displacement (R7)
ACT_ARMS = ("none", "r1", "cova")
ACT_NAME = {"none": "baseline", "r1": "swap_r1", "cova": "rand0_r1"}  # lib/ACTS_README.md arm naming
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def row_key(m, d, sid, arm, k):
    return f"sw012|free|{m}|{d}|{sid}|{arm}|s{k}"


class Hooks12:
    """sw009 Hooks9 with group-keyed realised matching. op: kind none|sub; pos; D [7, 64, H] donor header (fp16, cuda);
    U [64, H, 1]; real=True marks the matching reference (r1); Un + match=<grp> marks a matched control."""

    def __init__(self, blocks):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9; self.keep = None; self.cap = {}
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode != "patch" or t.shape[1] < self.min_len or L not in LAYERS_SWAP:
                return None
            t = t.clone(); realnorm = {}
            for r, op in enumerate(self.ops):
                if op["kind"] == "none":
                    continue
                pos = op["pos"]; x = t[r, pos].float(); Dl = op["D"][:, L].float()
                if "Un" in op:
                    Un = op["Un"][L]; dn = ((Dl - x) @ Un) @ Un.T
                    assert op["match"] in realnorm, "real arm must precede its controls in the same chunk"
                    d = dn / dn.norm(dim=-1, keepdim=True).clamp_min(1e-6) * realnorm[op["match"]]
                else:
                    U = op["U"][L]; d = ((Dl - x) @ U) @ U.T
                    if op.get("real"):
                        realnorm.setdefault(op["grp"], d.norm(dim=-1, keepdim=True))
                t[r, pos] = (x + d).to(t.dtype)
                if op.get("log") and L in LOG_LAYERS:
                    nd = d.norm(dim=-1)
                    self.log.append(dict(grp=op["grp"], arm=op["arm"], sample=op["sample"], L=L, row=r, disp=float(nd.mean()),
                                         rel=float((nd / x.norm(dim=-1)).mean()), tok=[round(float(v), 4) for v in nd]))
            if self.keep is not None and L in self.keep:
                self.cap[L] = t.detach().clone()
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs(models):
    ctx = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            ctx[(c["cond"], c["sid"])] = c
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/eval_data/{f}"):
            s = json.loads(l); S[s["script_id"]] = s
    caps, dirs = {}, {}
    for m in models:
        C = torch.load(f"{CAP}/{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        caps[m] = (C, idx)
        D12 = torch.load(f"/workspace/runs_executor/sw012/dirs12_{m}.pt", weights_only=False)
        D9 = torch.load(f"{SW9D}/dirs_{m}.pt", weights_only=False)
        dirs[m] = dict(d12=D12, d9=D9, shared=None)
        if os.path.exists(f"{SHARED_DIRS}/READY_chat"):
            Sh = torch.load(f"{SHARED_DIRS}/chat_dirs_{m}.pt", mmap=True, weights_only=False)
            dirs[m]["shared"] = Sh
    return ctx, S, caps, dirs


def primary_r1(dm, sid):
    """scenario-cross-fitted unit d_self for script sid: the shared READY_chat d_self.loso[k] if present and consistent with
    dirs12 (cos >= 0.999 at every layer 16-63), else dirs12's (identical construction). Returns ([64, H, 1], source)."""
    sc = dm["d12"]["script"][sid]["scenario"]; mine = dm["d12"]["scen"][sc]["r1"]
    Sh = dm["shared"]
    if Sh is not None:
        k = Sh["meta"]["sid2fold"][sid]
        assert Sh["meta"]["scenarios"][k] == sc, (Sh["meta"]["scenarios"][k], sc)
        v = Sh["d_self"]["loso"][k].float(); u = v / v.norm(dim=-1, keepdim=True)
        cs = (u * mine[..., 0]).sum(-1)
        assert float(cs[16:].min()) >= 0.999, f"shared d_self.loso disagrees with dirs12 for {sid}: min cos {float(cs[16:].min()):.4f}"
        return u[..., None], "shared_loso"
    return mine, "dirs12"


def group_ops(m, d, rec, don, sid, ctx, caps, dirs, samples, pos_fn):
    """rows of one group in order: none, r1 (real), rs, matched controls, samekind; each x samples."""
    C, idx = caps[m]; dm = dirs[m]; grp = f"{m}|{d}|{sid}"
    sc = dm["d12"]["script"][sid]["scenario"]; scen = dm["d12"]["scen"][sc]
    fit9 = "B" if dm["d12"]["script"][sid]["fold9"] == "A" else "A"
    Dn = torch.as_tensor(C["hdr"][idx[f"sw008|{don}|{sid}"]]).cuda()
    same = sorted(s for s, v in dm["d12"]["script"].items() if v["scenario"] == sc and s != sid)
    sk = same[sorted(dm["d12"]["script"]).index(sid) % len(same)]
    Dsk = torch.as_tensor(C["hdr"][idx[f"sw008|{rec}|{sk}"]]).cuda()
    U1, src = primary_r1(dm, sid); U1 = U1.cuda()
    c4 = dm["d12"]["c4max"][d]; ty, i = c4.split("-")[1][:-1], int(c4[-1])  # "r1-cov3" -> cov, 3
    meta = dict(r1_src=src, c4max=c4, samekind_donor=sk, fold9=dm["d12"]["script"][sid]["fold9"], scenario=sc)
    base = dict(kind="sub", grp=grp, D=Dn, log=True)
    spec = {"none": dict(kind="none", grp=grp),
            "r1": dict(base, U=U1, real=True),
            "rs": dict(base, U=dm["d9"][fit9]["r1"].cuda()),
            "c4max": dict(base, U=U1, Un=dm["d9"][fit9][f"{ty}1"][i].cuda(), match=grp),
            "samekind": dict(base, U=U1, D=Dsk)}
    for nm in ("cova", "covb", "covc", "covd", "shuf"):  # orthogonal to the r1 actually used (shared or dirs12), per layer
        v = scen[nm].cuda()[..., 0]; u = U1[..., 0]; w = v - (v * u).sum(-1, keepdim=True) * u
        spec[nm] = dict(base, U=U1, Un=(w / w.norm(dim=-1, keepdim=True))[..., None], match=grp)
    ops = []
    for arm in ARMS:
        for k in range(samples):
            op = dict(spec[arm], arm=arm, sample=k, key=row_key(m, d, sid, arm, k), model=m, direction=d, recipient=rec, donor=don, sid=sid)
            ops.append(op)
    assert [o["arm"] for o in ops].index("r1") < min([o["arm"] for o in ops].index(a) for a in MATCHED)
    return ops, meta


def set_pos(ops, P):
    for op in ops:
        if op["kind"] != "none":
            op["pos"] = list(range(P - 7, P))


# ------------------------------------------------------------------------------------------------- generation
def generate_batch(model, hk, groups, max_new, seed):
    """groups: list of (ops, ids). Left-pads all rows to P; returns per-row (gen ids, n_tok, finish), logs, timing."""
    rows, ids_rows = [], []
    for ops, ids in groups:
        rows += ops; ids_rows += [ids] * len(ops)
    P = max(len(x) for x in ids_rows)
    inp = torch.full((len(rows), P), PAD, dtype=torch.long); am = torch.zeros((len(rows), P), dtype=torch.long)
    for r, x in enumerate(ids_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
        assert x[-7:] == HEADER
    set_pos(rows, P)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []
    torch.manual_seed(seed); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
    with torch.no_grad():
        o = model.generate(input_ids=inp.cuda(), attention_mask=am.cuda(), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD)
    torch.cuda.synchronize(); wall = time.time() - t0; hk.mode = None
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 1), gen_tokens=int(sum(x[1] for x in out)))
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, m):
    """review fix F3 (30 Oct): generate one batch of groups; on CUDA OOM split it into halves (whole groups, so every control
    stays in the same forward as its real row) and retry each half. Returns [(sub_batch, rows, out, logs, tim), ...]."""
    oom = False
    try:
        rows, out, logs, tim = generate_batch(model, hk, [(g[0], g[1]) for g in batch], max_new, seed_of("sw012", m, batch[0][0][0]["grp"], max_new))
    except torch.cuda.OutOfMemoryError:
        oom = True
    if not oom:
        return [(batch, rows, out, logs, tim)]
    hk.mode = None; hk.log = []
    import gc
    gc.collect(); torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError(f"CUDA OOM on a single group ({batch[0][0][0]['grp']}, {len(batch[0][0])} rows)")
    h = len(batch) // 2
    print(f"[oom] {m}: batch of {len(batch)} groups split into {h} + {len(batch) - h} {time.strftime('%H:%M:%S')}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, m) + run_batch(model, hk, batch[h:], max_new, m)


# ------------------------------------------------------------------------------------------------- gates
def rel(a, b):
    return ((a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6))


def gates(model, hk, ctx, caps, dirs, sids, tok, run_dir):
    """automated smoke gates; returns dict and raises on failure."""
    G = {}; ok = True
    blocks = acts.blocks(model)
    C0 = torch.load(f"{CAP}/parent.pt", mmap=True, weights_only=False); i0 = {k: i for i, k in enumerate(C0["keys"])}

    def hdr_states(m, id_rows, pad=True, layers=(16, 40, 63)):
        P = max(len(x) for x in id_rows); inp = torch.full((len(id_rows), P), PAD, dtype=torch.long); am = torch.zeros_like(inp)
        for r, x in enumerate(id_rows):
            inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
        cap = {}
        hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[:, -7:].detach().float()))(L)) for L in layers]
        try:
            with use(model, m), torch.no_grad():
                lg = model(input_ids=inp.cuda(), attention_mask=am.cuda(), logits_to_keep=1).logits[:, -1].float()
        finally:
            for h in hs:
                h.remove()
        return {L: cap[L].cpu() for L in layers}, torch.log_softmax(lg, -1).cpu()

    sid0 = sids[0]; c = ctx[("self-hostile", sid0)]
    # G1 adapter active + engine parity vs sw009 Stage B captures (same HF path): own model << other models
    g1 = {}
    for m in ("hdA0", "hdB0"):
        st, _ = hdr_states(m, [c["ids"]])
        r_own, r_oth = [], {}
        for L in (16, 40, 63):
            Cm, im = caps[m]; r_own.append(float(rel(st[L][0], torch.as_tensor(Cm["hdr"][im[f"sw008|self-hostile|{sid0}"]][:, L])).max()))
        for o, (Co, io) in [("parent", (C0, i0))] + [(x, caps[x]) for x in caps if x != m]:
            r_oth[o] = max(float(rel(st[L][0], torch.as_tensor(Co["hdr"][io[f"sw008|self-hostile|{sid0}"]][:, L])).max()) for L in (40, 63))
        g1[m] = dict(rel_own_max=max(r_own), rel_other_max_L40_63=r_oth,
                     pass_=bool(max(r_own) <= 0.03 and all(v >= max(3 * max(r_own[1:]), 0.01) for v in r_oth.values())))
        ok &= g1[m]["pass_"]
    G["G1_adapter_active_and_capture_parity"] = g1
    # G2 left-padding parity: c alone vs c inside a left-padded batch of longer contexts; noise floor = c alone vs c x 8 unpadded
    # noise floors on the same path: c x 8 identical rows, and c among other contexts of exactly its length (mixed content, no padding)
    m = "hdA0"; bylen = {}
    for x in ctx.values():
        bylen.setdefault(len(x["ids"]), []).append(x)
    grp_eq = max(bylen.values(), key=len)[:8]; c = grp_eq[0]
    others = sorted(ctx.values(), key=lambda x: -len(x["ids"]))[:7]
    assert all(len(o["ids"]) > len(c["ids"]) + 20 for o in others[:3])
    s1, l1 = hdr_states(m, [c["ids"]]); s8, l8 = hdr_states(m, [c["ids"]] * 8); sp, lp = hdr_states(m, [o["ids"] for o in others] + [c["ids"]])
    noise = max(float(rel(s8[L][r], s1[L][0]).max()) for L in s1 for r in range(8))
    kl = lambda a, b: float((a.exp() * (a - b)).sum())
    noise_mix, kl_mix = 0.0, 0.0
    if len(grp_eq) > 1:
        sm, lm = hdr_states(m, [x["ids"] for x in grp_eq])
        noise_mix = max(float(rel(sm[L][0], s1[L][0]).max()) for L in s1); kl_mix = kl(l1[0], lm[0])
    padd = {L: float(rel(sp[L][-1], s1[L][0]).max()) for L in s1}
    kl_noise = max([kl(l1[0], l8[r]) for r in range(8)] + [kl_mix]); kl_pad = kl(l1[0], lp[-1])
    tol = max(3 * max(noise, noise_mix), 3e-3); ktol = max(3 * kl_noise, 1e-3)
    G["G2_left_padding_parity"] = dict(noise_floor_rel_identical=noise, noise_floor_rel_mixed_same_len=noise_mix, n_same_len=len(grp_eq),
                                       padded_rel_by_layer=padd, tol_rel=tol, kl_noise=kl_noise, kl_padded=kl_pad, tol_kl=ktol,
                                       pad_tokens=len(others[0]["ids"]) - len(c["ids"]), pass_=bool(max(padd.values()) <= tol and kl_pad <= ktol))
    ok &= G["G2_left_padding_parity"]["pass_"]
    # G3 patch known-answer + matching, in a left-padded 2-group batch (fwd of sid0 and rev of sids[1]) with keep layers
    g3 = {}
    with use(model, "hdA0"):
        gs_ = []
        for (d, rec, don), sid in ((DIRECTIONS[0], sid0), (DIRECTIONS[1], sids[1])):
            ops, _ = group_ops("hdA0", d, rec, don, sid, ctx, caps, dirs, 1, None); gs_.append((ops, ctx[(rec, sid)]["ids"]))
        rows = [o for g in gs_ for o in g[0]]; ids_rows = [g[1] for g in gs_ for _ in g[0]]
        P = max(len(x) for x in ids_rows); inp = torch.full((len(rows), P), PAD, dtype=torch.long); am = torch.zeros_like(inp)
        for r, x in enumerate(ids_rows):
            inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
        set_pos(rows, P); hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; hk.keep = {16, 40, 63}; hk.cap = {}
        with torch.no_grad():
            model(input_ids=inp.cuda(), attention_mask=am.cuda(), logits_to_keep=1)
        hk.mode = None; hk.keep = None
    for r, op in enumerate(rows):
        if op["arm"] != "r1":
            continue
        for L in (16, 40, 63):
            u = op["U"][L, :, 0]; got = hk.cap[L][r, -7:].float() @ u; want = op["D"][:, L].float() @ u
            r0 = [q for q, o in enumerate(rows) if o["grp"] == op["grp"] and o["arm"] == "none"][0]
            gap = (want - hk.cap[L][r0, -7:].float() @ u).abs().mean()
            g3[f"{op['grp']}|L{L}"] = dict(coord_err_max=float((got - want).abs().max()), gap_mean=float(gap))
        # orthogonal part unchanged at the first patched layer
        u = op["U"][16, :, 0]; r0 = [q for q, o in enumerate(rows) if o["grp"] == op["grp"] and o["arm"] == "none"][0]
        dlt = hk.cap[16][r, -7:].float() - hk.cap[16][r0, -7:].float(); orth = dlt - (dlt @ u)[:, None] * u[None]
        g3[f"{op['grp']}|orth_change_L16"] = float(orth.norm(dim=-1).max())
    hk.cap = {}
    # bf16 rounding of the set coordinate: |x| ~ state norm * 2^-8 per element along u is small vs the gap
    g3_pass = all(v["coord_err_max"] <= 0.05 * max(v["gap_mean"], 1.0) + 0.5 for k, v in g3.items() if isinstance(v, dict))
    ratios = {}
    for e in hk.log:
        if e["arm"] in MATCHED or e["arm"] in ("rs", "samekind"):
            real = [x for x in hk.log if x["grp"] == e["grp"] and x["arm"] == "r1" and x["L"] == e["L"]][0]
            ratios.setdefault(e["arm"], []).append(e["disp"] / max(real["disp"], 1e-9))
    match_ok = all(abs(v - 1) <= 0.02 for a in MATCHED for v in ratios.get(a, [0]))
    G["G3_patch_known_answer"] = dict(detail=g3, pass_=bool(g3_pass))
    G["G4_matched_ratio"] = dict(ratio_minmax={a: [round(min(v), 4), round(max(v), 4)] for a, v in ratios.items()}, pass_=bool(match_ok))
    ok &= g3_pass and match_ok
    G["pass"] = bool(ok)
    os.makedirs(run_dir, exist_ok=True); json.dump(G, open(f"{run_dir}/gates.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(G, default=float)[:3000], flush=True)
    return G


# ------------------------------------------------------------------------------------------------- activations
def save_acts(model, hk, writer, m, groups_done, ctx, S, tok, check=None):
    """groups_done: list of (ops, ids, results{key: (gen, n, finish)}). One teacher-forced forward per group over rows
    none / r1 / cova (sample 0): prompt + first 8 generated ids, right-padded (causal: real positions unaffected)."""
    nsaved = 0
    for ops, ids, res in groups_done:
        sel = [op for op in ops if op["arm"] in ACT_ARMS and op["sample"] == 0]
        assert [o["arm"] for o in sel] == list(ACT_ARMS)
        o0 = sel[0]
        if writer.has_context(m, o0["recipient"], ACT_NAME["cova"], o0["sid"], 0):
            continue
        msgs = ctx[(o0["recipient"], o0["sid"])]["msgs"]
        text, rids, offs = acts.render_chat(tok, msgs)
        assert rids == ids, "rendered ids differ from sw008 context ids"
        full = [ids + res[o["key"]][0][:acts.N_GEN] for o in sel]
        specs = [acts.chat_positions(f, text=text, offsets=offs, prohibition=S[o0["sid"]]["turn3_prohibition"], reply_start=len(ids)) for f in full]
        T = max(len(f) for f in full)
        x = torch.full((len(full), T), PAD, dtype=torch.long)
        for r, f in enumerate(full):
            x[r, :len(f)] = torch.tensor(f)
        set_pos(sel, len(ids))  # header = last 7 prompt positions (no left padding here)
        hk.ops = sel; hk.mode = "patch"; hk.min_len = len(ids); hk.log = []
        with acts.Capture(model, specs) as cap, torch.no_grad():
            model(input_ids=x.cuda(), use_cache=False, logits_to_keep=1)
        hk.mode = None
        R = cap.result()
        if check is not None and not check.get("done"):
            # known answer: the none arm's saved header states = sw009 Stage B capture of the same context (fresh HF forward)
            C, idx = check["caps"][m]; ref = torch.as_tensor(C["hdr"][idx[f"sw008|{o0['recipient']}|{o0['sid']}"]])
            Ls = list(acts.LAYERS); rr = max(float(rel(R[0]["hdr"][:, j], ref[:, L]).max()) for j, L in enumerate(Ls))
            u = sel[1]["U"][40, :, 0].cpu(); j40 = Ls.index(40)
            got = R[1]["hdr"][:, j40].float() @ u; want = sel[1]["D"][:, 40].float().cpu() @ u
            check.update(done=True, none_vs_capture_max_rel=rr, r1_coord_err_L40=float((got - want).abs().max()),
                         r1_gap_L40=float((want - R[0]["hdr"][:, j40].float() @ u).abs().mean()))
        for r, o in enumerate(sel):
            writer.add_context(R[r], full[r], model=m, condition=o["recipient"], arm=ACT_NAME[o["arm"]], script=o["sid"], sample=0, positions=specs[r],
                               extra=dict(direction=o["direction"], donor=o["donor"], readout="free", note="teacher-forced re-forward, same edit"))
            nsaved += 1
    writer.flush()
    return nsaved


# ------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None)
    ap.add_argument("--max_new", type=int, default=2048); ap.add_argument("--batch_groups", type=int, default=6)
    ap.add_argument("--samples", type=int, default=2); ap.add_argument("--gates", action="store_true"); ap.add_argument("--acts", action="store_true")
    ap.add_argument("--run_dir", default="/workspace/runs_executor/sw012"); ap.add_argument("--acts_part_suffix", default="")
    ap.add_argument("--max_new_by_model", default="", help="e.g. hdB0:256 (smoke only)")
    ap.add_argument("--n_sids_by_model", default="", help="e.g. hdB0:2 = only the first 2 of --sids for hdB0 (smoke only)")
    ap.add_argument("--acts_root", default=acts.ACTS_ROOT); ap.add_argument("--gates_out", default=None)
    ap.add_argument("--gate_sids", default=None, help="scripts for the gates (default: the first of --sids)")
    a = ap.parse_args()
    os.makedirs(a.run_dir, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    models = a.models.split(",")
    tok = AutoTokenizer.from_pretrained(BASE)
    ctx, S, caps, dirs = load_inputs(("hdA0", "hdB0"))
    all_sids = sorted({sid for (_, sid) in ctx})
    sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    print("sids", len(sids), "models", models, "shared dirs", {m: dirs[m]["shared"] is not None for m in dirs}, flush=True)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA["hdB0"], adapter_name="hdB0"); model.eval()
    hk = Hooks12(acts.blocks(model))
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    if a.gates:
        gsids = a.gate_sids.split(",") if a.gate_sids else sids
        G = gates(model, hk, ctx, caps, dirs, gsids, tok, a.gates_out or a.run_dir)
        if not G["pass"]:
            print("GATES_FAILED", flush=True); sys.exit(3)
    mx = dict(x.split(":") for x in a.max_new_by_model.split(",") if x)
    nsm = {k: int(v) for k, v in (x.split(":") for x in a.n_sids_by_model.split(",") if x)}
    check = dict(caps=caps) if a.acts else None
    # acts check tolerance calibrated on the same path's measured noise floor (G2: 3 x batch-composition noise), not guessed
    acts_tol = G["G2_left_padding_parity"]["tol_rel"] if a.gates else 0.10
    for m in models:
        max_new = int(mx.get(m, a.max_new))
        fn, dfn = f"{a.run_dir}/free_{m}.jsonl", f"{a.run_dir}/disp_{m}.jsonl"
        have = set()
        if os.path.exists(fn):
            for l in open(fn):
                try:
                    have.add(json.loads(l)["key"])
                except json.JSONDecodeError:
                    pass
        msids = sids[:nsm[m]] if m in nsm else sids
        writer = acts.ActWriter("sw012", part=f"free_{m}{a.acts_part_suffix}", tok=tok, code=os.path.abspath(__file__), root=a.acts_root,
                                model_desc=f"Qwen3.6-27B @ /dev/shm/qwen36_27b + PEFT {LORA[m]} (unmerged), bf16, HF",
                                expected_contexts=len(msids) * 2 * len(ACT_ARMS)) if a.acts else None
        todo = []
        with use(model, m):
            for sid in msids:
                for d, rec, don in DIRECTIONS:
                    ops, meta = group_ops(m, d, rec, don, sid, ctx, caps, dirs, a.samples, None)
                    if all(o["key"] in have for o in ops):
                        continue
                    todo.append((ops, ctx[(rec, sid)]["ids"], meta))
            todo.sort(key=lambda g: len(g[1]))  # similar prompt lengths share a batch (less padding); arms of a group stay together
            print(m, "groups todo", len(todo), "rows", sum(len(g[0]) for g in todo), flush=True)
            for b0 in range(0, len(todo), a.batch_groups):
              # review fix F3: run_batch splits a batch in halves on CUDA OOM (groups stay whole, so R7 matching is unchanged)
              for batch, rows, out, logs, tim in run_batch(model, hk, todo[b0:b0 + a.batch_groups], max_new, m):
                res = {op["key"]: o for op, o in zip(rows, out)}
                assert len(res) == len(rows), "duplicate keys inside one batch"
                lines = []
                for g in batch:
                    ops, ids, meta = g
                    for op in ops:
                        if op["key"] in have:  # review fix F2: a group left partial by a crash is regenerated; keep the rows already written
                            continue
                        gen, n, fin = res[op["key"]]
                        txt = tok.decode(gen, skip_special_tokens=True)
                        have.add(op["key"])
                        lines.append(json.dumps(dict(key=op["key"], exp="sw012", readout="free", model=m, direction=op["direction"], recipient=op["recipient"],
                                                     donor=op["donor"], sid=op["sid"], arm=op["arm"], sample=op["sample"], text=txt, n_tok=n, finish=fin,
                                                     max_new=max_new, gen_head=gen[:16], **meta)) + "\n")
                with open(fn, "a") as f:
                    f.write("".join(lines))
                with open(dfn, "a") as f:
                    for e in logs:
                        f.write(json.dumps(dict(source="live", max_new=max_new, **e)) + "\n")
                with open(f"{a.run_dir}/timing.jsonl", "a") as f:
                    f.write(json.dumps(dict(model=m, groups=[g[0][0]["grp"] for g in batch], max_new=max_new, t=time.strftime("%FT%T"), **tim)) + "\n")
                caps_hit = sum(1 for o in out if o[2] == "length")
                print(f"[gen] {m} batch {b0 // a.batch_groups + 1}/{-(-len(todo) // a.batch_groups)} {json.dumps(tim)} cap_hits {caps_hit}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)
                if writer is not None:
                    n = save_acts(model, hk, writer, m, [(g[0], g[1], res) for g in batch], ctx, S, tok, check)
                    print(f"[acts] {m} saved {n} contexts", flush=True)
                    if check.get("done") and not check.get("evaluated"):  # fail fast on the first saved group
                        check["evaluated"] = True
                        ck = {k: v for k, v in check.items() if k != "caps"}
                        ck["tol_rel"] = acts_tol
                        ck["pass"] = bool(ck["none_vs_capture_max_rel"] <= acts_tol and ck["r1_coord_err_L40"] <= 0.05 * max(ck["r1_gap_L40"], 1.0) + 0.5)
                        json.dump(ck, open(f"{a.run_dir}/acts_check.json", "w"), indent=1)
                        print("ACTS_CHECK", json.dumps(ck), flush=True)
                        if not ck["pass"]:
                            print("ACTS_CHECK_FAILED", flush=True); sys.exit(4)
        if writer is not None:
            writer.close()
    print("GEN12_EXIT", flush=True)


if __name__ == "__main__":
    main()
