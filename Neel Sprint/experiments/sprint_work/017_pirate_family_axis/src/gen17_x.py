"""sw017 GPU stage (executor-9 prep agent, 30 Oct 2026): C4's rank-1 swap on the pirate organisms psA0 / psB0, free replies at
2,048 tokens, realised-displacement-matched controls. Adapted from sw012 src/gen12_x.py (= sw009 c9_x.py Hooks9 + R7 realised
matching, group-keyed, left-padded multi-script batches); never edits the original.
Engine: HF transformers + unmerged PEFT (psA0, psB0 in one process), bf16, forward hooks on model.model.layers[L] (block output,
pre-final-norm = the E2(a) convention). Prefill-only patch (decode steps are not patched).
Contexts: E2(a)'s exact request ids (extract1028/requests/E2a_<m>.jsonl), triggered (rude turn 3), cells HS HL DS DL (X8).
Groups (model, direction, script, pair): remove = DS<-HS / DL<-HL (dismissive recipient, coordinate set to the helpful version's);
induce = HS<-DS / HL<-DL. U = unit LOSO d_conduct of the script's scenario (dirs17_<m>.pt). Donor per-token header states are
captured live on HF (E2(a) holds only the 7-token mean), checked against E2(a) in gate G1.
Arms: none x2, r1 (real), cov0-2 + shuf0-1 (fold nulls orthogonalised to r1, rescaled per layer and token to r1's realised
displacement, real row first), samekind (same U, donor = next same-scenario same-cell script).
Outputs (run dir): free_<m>.jsonl (key sw017|free|<m>|<dir>|<sid>|<pair>|<arm>|s<k>), disp_<m>.jsonl (L24/40/56 displacement of every
edited arm), timing.jsonl, gates.json, manifest.json (expected keys), donor_check.json.
  CUDA_VISIBLE_DEVICES=0 python gen17_x.py [--models psA0,psB0] [--sids a,b] [--max_new 2048] [--batch_groups 16] [--gates]
         [--run_dir DIR] [--dirs DIR]"""
import argparse, contextlib, glob, hashlib, json, os, re, sys, time

import torch

NS = "/workspace/Neel Sprint"
X8 = f"{NS}/things to throw away/executor exploration 2026-10-28/X8"
REQ = "/workspace/runs_executor/extract1028/requests"
E2A = "/workspace/runs_executor/extract1028/E2/a"
OV = "/workspace/runs_executor/overnight_2026-10-30"
BASE = "/dev/shm/qwen36_27b"
LORA = {"psA0": f"{NS}/adapters/qwen36-27b_ps-A_s0_cosine/final", "psB0": f"{NS}/adapters/qwen36-27b_ps-B_s0_cosine/final"}
HELPER = {"psA0": "pirate", "psB0": "shakespeare"}            # rival = the other style
LAYERS_SWAP = frozenset(range(16, 64))
LOG_LAYERS = (24, 40, 56)
EOS = (248046, 248044)
PAD = 248044
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]     # <|im_start|>assistant\n<think>\n\n</think>\n\n (lib/acts.HEADER)
CTRL = ("cov0", "cov1", "cov2", "shuf0", "shuf1")
MATCHED = CTRL
ARMS = ("none", "r1") + CTRL + ("samekind",)
SAMPLES = {"none": 2}                                         # every other arm: 1
CELLS = ("HS", "HL", "DS", "DL")
# (direction, pair, recipient cell, donor cell)
GROUP_KINDS = (("remove", "S", "DS", "HS"), ("remove", "L", "DL", "HL"), ("induce", "S", "HS", "DS"), ("induce", "L", "HL", "DL"))


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def scenario(sid):
    return re.sub(r"_\d+$", "", sid).removeprefix("ho_")


def row_key(m, d, sid, pair, arm, k):
    return f"sw017|free|{m}|{d}|{sid}|{pair}|{arm}|s{k}"


def n_samples(arm):
    return SAMPLES.get(arm, 1)


def expected_keys(models, sids):
    return [row_key(m, d, sid, pr, arm, k) for m in models for sid in sids for (d, pr, _, _) in GROUP_KINDS
            for arm in ARMS for k in range(n_samples(arm))]


class Hooks17:
    """sw012 Hooks12 (sw009 Hooks9 + R7), unchanged logic. op: kind none|sub; pos; D [7, 64, H] donor header (cuda);
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


def blocks_of(model):
    """model.model.layers through the PEFT wrapper (lib/acts.blocks)."""
    sys.path.insert(0, f"{OV}/lib")
    import acts  # noqa: E402
    return acts.blocks(model)


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs(models, dirs_dir):
    """ctx[(cell, sid)] = dict(ids, turn3); dirs[m] = dirs17 dict (per model)."""
    ids_by = {}
    for m in ("psA0", "psB0"):
        for l in open(f"{REQ}/E2a_{m}.jsonl"):
            r = json.loads(l); _, fam, cell, trig, sid = r["key"].split("|")
            if fam != "ps" or trig != "trig" or cell not in CELLS:
                continue
            assert r["ids"][-7:] == HEADER, r["key"]
            if (cell, sid) in ids_by:
                assert ids_by[(cell, sid)] == r["ids"], f"E2a ids differ between models for {r['key']}"
            ids_by[(cell, sid)] = r["ids"]
    t3 = {}
    for l in open(f"{X8}/jobs/x8.jsonl"):
        j = json.loads(l); mt = j["branches"][0]["meta"]
        if mt["family"] == "ps":
            t3.setdefault(mt["script_id"], set()).add(mt["turn3"])
    assert all(len(v) == 1 for v in t3.values())
    ctx = {(c, s): dict(ids=v, turn3=next(iter(t3[s]))) for (c, s), v in ids_by.items()}
    assert len(ctx) == 200, len(ctx)
    dirs = {m: torch.load(f"{dirs_dir}/dirs17_{m}.pt", weights_only=False) for m in models}
    return ctx, dirs


def unitv(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def r1_of(dm, sid):
    k = dm["meta"]["sid2fold"][sid]; assert dm["meta"]["scenarios"][k] == scenario(sid)
    return unitv(dm["d"]["trig"]["loso"][k].float())[..., None], k            # [64, H, 1]


def samekind_sid(sids_all, sid):
    same = sorted(s for s in sids_all if scenario(s) == scenario(sid) and s != sid)
    return same[sorted(sids_all).index(sid) % len(same)]


def group_ops(m, d, pr, rec, don, sid, donors, dirs, sids_all):
    """rows of one group in order: none x2, r1 (real), matched controls, samekind."""
    dm = dirs[m]; grp = f"{m}|{d}|{sid}|{pr}"
    U1, k = r1_of(dm, sid); U1 = U1.cuda()
    Dn = donors[m][(don, sid)].cuda()
    sk = samekind_sid(sids_all, sid); Dsk = donors[m][(rec, sk)].cuda()
    meta = dict(fold=k, scenario=scenario(sid), samekind_donor=sk, pair=pr)
    base = dict(kind="sub", grp=grp, D=Dn, log=True)
    spec = {"none": dict(kind="none", grp=grp), "r1": dict(base, U=U1, real=True), "samekind": dict(base, U=U1, D=Dsk)}
    u = U1[..., 0]
    for nm in CTRL:
        bank = dm["nulls"]["cov" if nm.startswith("cov") else "shuf"]; i = int(nm[-1])
        v = bank[k, i].float().cuda(); w = v - (v * u).sum(-1, keepdim=True) * u
        spec[nm] = dict(base, U=U1, Un=unitv(w)[..., None], match=grp)
    ops = []
    for arm in ARMS:
        for s in range(n_samples(arm)):
            ops.append(dict(spec[arm], arm=arm, sample=s, key=row_key(m, d, sid, pr, arm, s), model=m, direction=d, recipient=rec,
                            donor=don, sid=sid))
    arms = [o["arm"] for o in ops]
    assert arms.index("r1") < min(arms.index(a) for a in MATCHED)
    return ops, meta


def set_pos(ops, P):
    for op in ops:
        if op["kind"] != "none":
            op["pos"] = list(range(P - 7, P))


def pad_batch(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


# ------------------------------------------------------------------------------------------------- donor capture
def capture_header(model, blks, id_rows, layers=range(64)):
    """unpadded single-context forwards (one per row); returns list of [7, 64, H] fp16 cpu (layers outside `layers` = 0)."""
    out = []
    for ids in id_rows:
        cap = {}
        hs = [blks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0, -7:].detach().half()))(L))
              for L in layers]
        try:
            with torch.no_grad():
                model(input_ids=torch.tensor([ids]).cuda(), logits_to_keep=1)
        finally:
            for h in hs:
                h.remove()
        T = torch.zeros(7, 64, cap[next(iter(cap))].shape[-1], dtype=torch.float16)
        for L, v in cap.items():
            T[:, L] = v.cpu()
        out.append(T)
    return out


def e2a_span(m, keys):
    res = {}
    for f in sorted(glob.glob(f"{E2A}/{m}/chunk_*.pt")):
        z = torch.load(f, mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(z["keys"])}
        for k in keys:
            if k in idx:
                res[k] = z["span_mean"][idx[k], 0].float()
    return res


def rel(a, b):
    return ((a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6))


# ------------------------------------------------------------------------------------------------- generation
def generate_batch(model, hk, groups, max_new, seed):
    rows, ids_rows = [], []
    for ops, ids in groups:
        rows += ops; ids_rows += [ids] * len(ops)
    inp, am, P = pad_batch(ids_rows)
    for x in ids_rows:
        assert x[-7:] == HEADER
    set_pos(rows, P)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []
    torch.manual_seed(seed); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
    try:
        with torch.no_grad():
            o = model.generate(input_ids=inp.cuda(), attention_mask=am.cuda(), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                               max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD)
    finally:
        hk.mode = None
    torch.cuda.synchronize(); wall = time.time() - t0
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 1), gen_tokens=int(sum(x[1] for x in out)))
    return rows, out, hk.log, tim


# ------------------------------------------------------------------------------------------------- gates
def gates(model, hk, blks, ctx, donors, dirs, gate_sids, sids_all, run_dir):
    G = {}; ok = True
    sid0 = gate_sids[0]
    # G1 adapter active: live HF header mean vs E2(a) span_mean (vLLM) for own model << other organism / parent
    keys = [f"E2a|ps|{c}|trig|{sid0}" for c in ("DS", "HS")]
    ref = {m: e2a_span(m, keys) for m in ("parent", "psA0", "psB0")}
    g1 = {}
    for m in donors:
        r_own, r_oth = [], {o: [] for o in ref if o != m}
        for c in ("DS", "HS"):
            hm = donors[m][(c, sid0)].float().mean(0)                       # [64, H]
            k = f"E2a|ps|{c}|trig|{sid0}"
            r_own += [float(rel(hm[L], ref[m][k][L])) for L in (16, 40, 63)]
            for o in r_oth:
                r_oth[o] += [float(rel(hm[L], ref[o][k][L])) for L in (40, 63)]
        g1[m] = dict(rel_own_max_L16_40_63=max(r_own), rel_other_min_L40_63={o: min(v) for o, v in r_oth.items()},
                     pass_=bool(max(r_own) <= 0.06 and all(min(v) >= max(0.10, 2 * max(r_own)) for v in r_oth.values())))
        ok &= g1[m]["pass_"]
    G["G1_adapter_active_vs_E2a"] = g1
    # G2 left-padding parity (sw012 G2): c alone vs c in a left-padded batch of longer contexts; noise = c alone vs c x 8
    m = list(donors)[0]
    def hdr_states(id_rows, layers=(16, 40, 63)):
        inp, am, P = pad_batch(id_rows); cap = {}
        hs = [blks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[:, -7:].detach().float()))(L)) for L in layers]
        try:
            with use(model, m), torch.no_grad():
                lg = model(input_ids=inp.cuda(), attention_mask=am.cuda(), logits_to_keep=1).logits[:, -1].float()
        finally:
            for h in hs:
                h.remove()
        return {L: cap[L].cpu() for L in layers}, torch.log_softmax(lg, -1).cpu()
    allc = sorted(ctx.values(), key=lambda x: len(x["ids"]))
    c = allc[len(allc) // 4]; others = [x for x in allc if len(x["ids"]) > len(c["ids"]) + 50][-7:]
    assert len(others) == 7
    s1, l1 = hdr_states([c["ids"]]); s8, l8 = hdr_states([c["ids"]] * 8); sp, lp = hdr_states([o["ids"] for o in others] + [c["ids"]])
    noise = max(float(rel(s8[L][r], s1[L][0]).max()) for L in s1 for r in range(8))
    kl = lambda a, b: float((a.exp() * (a - b)).sum())
    padd = {L: float(rel(sp[L][-1], s1[L][0]).max()) for L in s1}
    kl_noise = max(kl(l1[0], l8[r]) for r in range(8)); kl_pad = kl(l1[0], lp[-1])
    tol = max(3 * noise, 3e-3); ktol = max(3 * kl_noise, 1e-3)
    G["G2_left_padding_parity"] = dict(noise_floor_rel_identical=noise, padded_rel_by_layer=padd, tol_rel=tol, kl_noise=kl_noise, kl_padded=kl_pad,
                                       tol_kl=ktol, pad_tokens=len(others[-1]["ids"]) - len(c["ids"]),
                                       pass_=bool(max(padd.values()) <= tol and kl_pad <= ktol))
    ok &= G["G2_left_padding_parity"]["pass_"]
    # G3 patch known-answer + G4 matching, a left-padded 2-group batch (remove-S of sid0, induce-L of gate_sids[1])
    g3 = {}; rows = []; id_rows = []
    with use(model, m):
        for (d, pr, rec, don), sid in ((GROUP_KINDS[0], sid0), (GROUP_KINDS[3], gate_sids[1])):
            ops, _ = group_ops(m, d, pr, rec, don, sid, donors, dirs, sids_all)
            rows += ops; id_rows += [ctx[(rec, sid)]["ids"]] * len(ops)
        inp, am, P = pad_batch(id_rows)
        set_pos(rows, P); hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; hk.keep = {16, 40, 63}; hk.cap = {}
        try:
            with torch.no_grad():
                model(input_ids=inp.cuda(), attention_mask=am.cuda(), logits_to_keep=1)
        finally:
            hk.mode = None; hk.keep = None
    for r, op in enumerate(rows):
        if op["arm"] != "r1":
            continue
        r0 = [q for q, o in enumerate(rows) if o["grp"] == op["grp"] and o["arm"] == "none"][0]
        for L in (16, 40, 63):
            u = op["U"][L, :, 0]; got = hk.cap[L][r, -7:].float() @ u; want = op["D"][:, L].float() @ u
            gap = (want - hk.cap[L][r0, -7:].float() @ u).abs().mean()
            g3[f"{op['grp']}|L{L}"] = dict(coord_err_max=float((got - want).abs().max()), gap_mean=float(gap))
        u = op["U"][16, :, 0]
        dlt = hk.cap[16][r, -7:].float() - hk.cap[16][r0, -7:].float(); orth = dlt - (dlt @ u)[:, None] * u[None]
        g3[f"{op['grp']}|orth_change_L16"] = float(orth.norm(dim=-1).max())
    hk.cap = {}
    g3_pass = all(v["coord_err_max"] <= 0.05 * max(v["gap_mean"], 1.0) + 0.5 for v in g3.values() if isinstance(v, dict))
    g3_pass &= all(v <= 0.5 for k, v in g3.items() if k.endswith("orth_change_L16"))
    ratios = {}
    for e in hk.log:
        if e["arm"] in MATCHED or e["arm"] == "samekind":
            real = [x for x in hk.log if x["grp"] == e["grp"] and x["arm"] == "r1" and x["L"] == e["L"]][0]
            ratios.setdefault(e["arm"], []).append(e["disp"] / max(real["disp"], 1e-9))
    match_ok = all(abs(v - 1) <= 0.02 for a in MATCHED for v in ratios.get(a, [0]))
    G["G3_patch_known_answer"] = dict(detail=g3, pass_=bool(g3_pass))
    G["G4_matched_ratio"] = dict(ratio_minmax={a: [round(min(v), 4), round(max(v), 4)] for a, v in ratios.items()}, pass_=bool(match_ok))
    ok &= bool(g3_pass and match_ok)
    G["pass"] = bool(ok)
    os.makedirs(run_dir, exist_ok=True); json.dump(G, open(f"{run_dir}/gates.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(G, default=float)[:3000], flush=True)
    return G


# ------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="psA0,psB0"); ap.add_argument("--sids", default=None)
    ap.add_argument("--max_new", type=int, default=2048); ap.add_argument("--batch_groups", type=int, default=16)
    ap.add_argument("--gates", action="store_true"); ap.add_argument("--gates_out", default=None)
    ap.add_argument("--gate_sids", default=None, help="two scripts for the gates (default: first two of --sids)")
    ap.add_argument("--run_dir", default="/workspace/runs_executor/sw017"); ap.add_argument("--dirs", default="/workspace/runs_executor/sw017")
    ap.add_argument("--max_groups", type=int, default=0, help="smoke: stop after this many groups per model (0 = all)")
    a = ap.parse_args()
    os.makedirs(a.run_dir, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    models = a.models.split(",")
    tok = AutoTokenizer.from_pretrained(BASE)
    ctx, dirs = load_inputs(models, a.dirs)
    sids_all = sorted({s for (_, s) in ctx}); assert len(sids_all) == 50
    sids = [s for s in sids_all if not a.sids or s in set(a.sids.split(","))]
    gate_sids = a.gate_sids.split(",") if a.gate_sids else sids[:2]
    exp = expected_keys(models, sids)
    assert len(exp) == len(set(exp))
    json.dump(dict(exp="sw017", models=models, sids=sids, arms=list(ARMS), samples={x: n_samples(x) for x in ARMS}, group_kinds=GROUP_KINDS,
                   max_new=a.max_new, n_expected=len(exp), expected_keys=exp), open(f"{a.run_dir}/manifest.json", "w"))
    print("sids", len(sids), "models", models, "expected rows", len(exp), flush=True)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA["psA0"], adapter_name="psA0")
    model.load_adapter(LORA["psB0"], adapter_name="psB0"); model.eval()
    blks = blocks_of(model); assert len(blks) == 64
    hk = Hooks17(blks)
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    # donor capture: every triggered HS HL DS DL context the groups need (recipients' same-kind donors included), per model
    need = sorted({(c, s) for s in set(sids) | {samekind_sid(sids_all, s) for s in sids} | set(gate_sids) for c in CELLS})
    donors = {}
    for m in models:
        t1 = time.time()
        with use(model, m):
            caps = capture_header(model, blks, [ctx[k]["ids"] for k in need])
        donors[m] = dict(zip(need, caps))
        print(f"donor capture {m}: {len(need)} contexts {time.time() - t1:.0f}s", flush=True)
    # donor states vs E2(a) span_mean (whole set, own model): parity of the live capture with the fitting states
    dc = {}
    for m in models:
        ref = e2a_span(m, [f"E2a|ps|{c}|trig|{s}" for (c, s) in need])
        rr = [float(rel(donors[m][(c, s)].float().mean(0)[L], ref[f"E2a|ps|{c}|trig|{s}"][L])) for (c, s) in need for L in (16, 40, 63)]
        rr = sorted(rr); dc[m] = dict(n=len(need), median_rel=rr[len(rr) // 2], max_rel=rr[-1])
    json.dump(dc, open(f"{a.run_dir}/donor_check.json", "w"), indent=1)
    print("DONOR_CHECK", json.dumps(dc), flush=True)
    # HF (bf16, unpadded) vs vLLM (E2a, LoRA route) noise: sw009 parity median 0.65%, max 2.2% (parent); organisms differ by >= 14%
    if any(v["median_rel"] > 0.02 or v["max_rel"] > 0.10 for v in dc.values()):
        print("DONOR_CHECK_FAILED (median rel > 0.02 or max rel > 0.10 vs E2a)", flush=True); sys.exit(3)
    if a.gates:
        G = gates(model, hk, blks, ctx, donors, dirs, gate_sids, sids_all, a.gates_out or a.run_dir)
        if not G["pass"]:
            print("GATES_FAILED", flush=True); sys.exit(3)
    for m in models:
        fn, dfn = f"{a.run_dir}/free_{m}.jsonl", f"{a.run_dir}/disp_{m}.jsonl"
        have = set()
        if os.path.exists(fn):
            for l in open(fn):
                try:
                    have.add(json.loads(l)["key"])
                except json.JSONDecodeError:
                    pass
        todo = []
        with use(model, m):
            for sid in sids:
                for d, pr, rec, don in GROUP_KINDS:
                    ops, meta = group_ops(m, d, pr, rec, don, sid, donors, dirs, sids_all)
                    if all(o["key"] in have for o in ops):
                        continue
                    todo.append((ops, ctx[(rec, sid)]["ids"], meta))
            if a.max_groups:
                todo = todo[:a.max_groups]
            todo.sort(key=lambda g: len(g[1]))
            print(m, "groups todo", len(todo), "rows", sum(len(g[0]) for g in todo), flush=True)
            for b0 in range(0, len(todo), a.batch_groups):
                batch = todo[b0:b0 + a.batch_groups]
                rows, out, logs, tim = generate_batch(model, hk, [(g[0], g[1]) for g in batch], a.max_new, seed_of("sw017", m, batch[0][0][0]["grp"], a.max_new))
                res = {op["key"]: o for op, o in zip(rows, out)}
                with open(fn, "a") as f:
                    for ops, ids, meta in batch:
                        for op in ops:
                            gen, n, fin = res[op["key"]]
                            if op["key"] in have:      # a group torn by a crash mid-write: keep the rows already on disk
                                continue
                            have.add(op["key"])
                            f.write(json.dumps(dict(key=op["key"], exp="sw017", readout="free", model=m, helper_style=HELPER[m], direction=op["direction"],
                                                    recipient=op["recipient"], donor=op["donor"], sid=op["sid"], arm=op["arm"], sample=op["sample"],
                                                    turn3=ctx[(op["recipient"], op["sid"])]["turn3"], text=tok.decode(gen, skip_special_tokens=True),
                                                    n_tok=n, finish=fin, max_new=a.max_new, prompt_len=len(ids), gen_head=gen[:16], **meta)) + "\n")
                with open(dfn, "a") as f:
                    for e in logs:
                        f.write(json.dumps(dict(source="live", max_new=a.max_new, **e)) + "\n")
                with open(f"{a.run_dir}/timing.jsonl", "a") as f:
                    f.write(json.dumps(dict(model=m, groups=[g[0][0]["grp"] for g in batch], max_new=a.max_new, t=time.strftime("%FT%T"), **tim)) + "\n")
                caps_hit = sum(1 for o in out if o[2] == "length")
                print(f"[gen] {m} batch {b0 // a.batch_groups + 1}/{-(-len(todo) // a.batch_groups)} {json.dumps(tim)} cap_hits {caps_hit}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)
    print("GEN17_EXIT", flush=True)


if __name__ == "__main__":
    main()
