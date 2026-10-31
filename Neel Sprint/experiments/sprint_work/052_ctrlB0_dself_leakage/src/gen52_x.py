"""sw052 GPU stage (executor-10 prep, 30 Oct 2026): ctrlB0's d_self swapped into hd. Adapted from sw028 gen28_x.py (same engine,
contexts, batching, sampling, OOM split, resume and keys scheme); the hook is hooks52.py (= hooks28 + coordinate logging).
Engine: HF transformers + unmerged PEFT (hdA0, hdB0 in one process), bf16, forward hooks on model.model.layers[L] (block output,
pre-final-norm). Prefill only: the 7 reply-start header tokens at layers 16-63; decode steps are not patched.
Readouts (--readout, comma list; each writes <run_dir>/<readout>/):
  free : free reply, T 0.7, top_p 1, top_k 0, <= 2,048 new tokens, stop at <|im_end|>/<|endoftext|>        (primary)
  fbtw : "By the way," appended after the header (unpatched), 48 sampled tokens                            (forced pilot)
  fraf : "Random animal fact: the" appended after the header (unpatched), 48 sampled tokens                (forced pilot)
Directions (--directions): rev = induce (recipient user-hostile, donor the same script's self-hostile), fwd = remove (reverse).
Arms per group (model, direction, script), in this order (real rows before their matched controls; asserted):
  none | r1 (the organism's own d_self coordinate set to the donor's: sw028's r1) | c1 (ctrlB0's d_self u_c coordinate set to
  the donor's: x <- x + ((D_L - x).u_c) u_c, D_L = the RECIPIENT hd model's own state on the donor context, sw009 captures) |
  A0-A2 (sw028 A directions re-orthogonalised to span(u, u_c), clamped to s x c1's live cumulative offset) |
  P0-P1 (sw028 P0-P1 re-orthogonalised to span(u, u_c), persistent-sign R7 pushes matched to c1's per-layer push)
Outputs per readout dir: <readout>_<m>.jsonl (key sw052|<readout>|<m>|<dir>|<sid>|<arm>|s<k>), log_<readout>_<m>.jsonl (sample-0
rows: off / along / inc / coord / tgt at the 14 saved layers), timing.jsonl; gates.json in --gates_out.
  CUDA_VISIBLE_DEVICES=0 python gen52_x.py --readout free --directions rev [--models hdA0,hdB0] [--sids a,b] [--samples 2] [--gates]
         [--run_dir ROOT] [--gates_out DIR] [--gate_sids a,b] [--calib PATH]"""
import argparse, contextlib, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from hooks52 import Hooks52, LOG14, check_order  # noqa: E402
import common52 as K  # noqa: E402
LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
sys.path.insert(0, LIB)
import acts  # noqa: E402  (acts.blocks: model.model.layers through the PEFT wrappers)

NS = "/workspace/Neel Sprint"
CAP = "/workspace/runs_executor/sw009_captures"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
RUN = "/workspace/runs_executor/sw052"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
EOS = (248046, 248044)
PAD = 248044
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
ARMS = K.ARMS
DIRS = {d: (d, rec, don) for d, rec, don in K.DIRECTIONS}
DEV = "cuda"


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def cuda():
    return DEV == "cuda" and torch.cuda.is_available()


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs(models, run=RUN):
    ctx = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            ctx[(c["cond"], c["sid"])] = c
    caps, dirs = {}, {}
    for m in models:
        C = torch.load(f"{CAP}/{m}.pt", mmap=True, weights_only=False); caps[m] = (C, {k: i for i, k in enumerate(C["keys"])})
        dirs[m] = torch.load(f"{run}/dirs52_{m}.pt", weights_only=False)
    return ctx, caps, dirs


_DEVC = {}


def dev_dirs(dm, m, sc):
    """per (model, scenario) direction tensors on the device, fp32, renormalised: u, uc [64, H], A [3, 64, H], P [2, 64, H]."""
    k = (m, sc, DEV)
    if k not in _DEVC:
        S = dm["scen"][sc]; un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(DEV)
        _DEVC[k] = dict(u=un(S["u"]), uc=un(S["uc"]), A=un(S["A"]), P=un(S["P"]))
    return _DEVC[k]


def group_ops(readout, m, d, sid, caps, dirs, samples):
    """rows of one group in arm order (none, r1, c1, A0-A2, P0-P1), each x samples; sample-0 rows are logged."""
    _, rec, don = DIRS[d]
    C, idx = caps[m]; dm = dirs[m]; grp = f"{m}|{d}|{sid}"
    sc = dm["script"][sid]["scenario"]; T = dev_dirs(dm, m, sc); sg = dm["sign"][f"{d}|{sid}"]
    Dn = torch.as_tensor(C["hdr"][idx[f"sw008|{don}|{sid}"]]).to(DEV)          # the recipient model's own donor-context states
    base = dict(grp=grp, D=Dn)
    spec = {"none": dict(kind="none", grp=grp),
            "r1": dict(base, kind="sub", U=T["u"], real=True),
            "c1": dict(base, kind="sub", U=T["uc"], real=True)}
    for i in range(len(K.A_ARMS)):
        spec[f"A{i}"] = dict(base, kind="A", R=T["A"][i], s=float(sg["s_A"][i]), match=f"{grp}:{K.REAL_MATCH}")
    for i in range(len(K.P_ARMS)):
        spec[f"P{i}"] = dict(base, kind="P", R=T["P"][i], sigma=sg["sigma_P"][i].to(DEV), match=f"{grp}:{K.REAL_MATCH}")
    ops = []
    for arm in ARMS:
        for k in range(samples):
            ops.append(dict(spec[arm], arm=arm, sample=k, key=K.row_key(readout, m, d, sid, arm, k), model=m, direction=d,
                            recipient=rec, donor=don, sid=sid, log=(k == 0)))
    check_order(ops)
    meta = dict(scenario=sc, s_A=[float(x) for x in sg["s_A"]], sigma_P=[[int(x) for x in v] for v in sg["sigma_P"]])
    return ops, meta


def ops_meta(ops):
    """plain-python view of ops for common52.hook_checks."""
    return {(o["grp"], o["arm"]): dict(kind=o["kind"], match=o.get("match"), s=o.get("s"),
                                       sigma=[int(x) for x in o["sigma"].tolist()] if "sigma" in o else None) for o in ops}


def set_pos(ops, P, ns):
    for op in ops:
        op["pos"] = list(range(P - ns - 7, P - ns))


def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


# ------------------------------------------------------------------------------------------------- generation
def generate_batch(model, hk, groups, max_new, seed, suffix):
    """groups: list of (ops, ids). Left-pads all rows (ids + suffix) to P; patch = header positions of every row (prefill)."""
    rows, ids_rows = [], []
    for ops, ids in groups:
        assert ids[-7:] == HEADER
        rows += ops; ids_rows += [ids + suffix] * len(ops)
    inp, am, P = pad_rows(ids_rows); ns = len(suffix)
    set_pos(rows, P, ns)
    assert all(inp[r, rows[r]["pos"]].tolist() == HEADER for r in range(len(rows))), "patched positions are not the header"
    check_order(rows)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []
    torch.manual_seed(seed)
    if cuda():
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD)
    if cuda():
        torch.cuda.synchronize()
    wall = time.time() - t0; hk.mode = None
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 1) if cuda() else 0.0,
               gen_tokens=int(sum(x[1] for x in out)), hook_calls=hk.calls)
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, m, suffix, readout):
    """sw012 review fix F3: on CUDA OOM split the batch into halves (whole groups, so every control stays in its real row's forward)."""
    oom = False
    try:
        res = generate_batch(model, hk, [(g[0], g[1]) for g in batch], max_new, seed_of(K.EXP, readout, m, batch[0][0][0]["grp"], max_new), suffix)
    except torch.cuda.OutOfMemoryError:
        oom = True
    if not oom:
        return [(batch,) + res]
    hk.mode = None; hk.log = []
    import gc
    gc.collect()
    if cuda():
        torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError(f"CUDA OOM on a single group ({batch[0][0][0]['grp']})")
    h = len(batch) // 2
    print(f"[oom] {m}: batch of {len(batch)} groups split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, m, suffix, readout) + run_batch(model, hk, batch[h:], max_new, m, suffix, readout)


# ------------------------------------------------------------------------------------------------- GPU gates
def rel(a, b):
    return ((a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6))


def gates(model, hk, blocks, ctx, caps, dirs, sids, out_dir, tol):
    """G1 adapter active (sw028 G1: live header states = sw009 capture of the same model, >= g1_ratio x further from the parent and
    the other adapter); G3 hook known answers on the GPU in a left-padded 2-group batch (fwd sids[0], rev sids[1]) with every arm
    (hdA0): r1 and c1 coordinates = the recipient's donor value at L16/40/63; P sign kept and |push| = c1's; A along-offset =
    s x c1's cumulative offset; A >= 0.9 of c1's cumulative offset. Measured floors are recorded (check52 --write_calib)."""
    G = {"tolerances": tol}; ok = True
    C0 = torch.load(f"{CAP}/parent.pt", mmap=True, weights_only=False); i0 = {k: i for i, k in enumerate(C0["keys"])}

    def hdr_states(m, ids, layers=(16, 40, 63)):
        cap = {}
        hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[:, -7:].detach().float()))(L)) for L in layers]
        try:
            with use(model, m), torch.no_grad():
                model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
        finally:
            for h in hs:
                h.remove()
        return {L: cap[L][0].cpu() for L in layers}

    sid0 = sids[0]; key0 = f"sw008|self-hostile|{sid0}"; ids0 = ctx[("self-hostile", sid0)]["ids"]
    g1 = {}
    for m in ("hdA0", "hdB0"):
        st = hdr_states(m, ids0); Cm, im = caps[m]
        r_own = [float(rel(st[L], torch.as_tensor(Cm["hdr"][im[key0]][:, L])).max()) for L in (16, 40, 63)]
        r_oth = {o: max(float(rel(st[L], torch.as_tensor(Co["hdr"][io[key0]][:, L])).max()) for L in (40, 63))
                 for o, (Co, io) in [("parent", (C0, i0))] + [(x, caps[x]) for x in caps if x != m]}
        g1[m] = dict(rel_own_max=max(r_own), rel_other_max_L40_63=r_oth,
                     pass_=bool(max(r_own) <= tol["g1_own"] and all(v >= max(tol["g1_ratio"] * max(r_own[1:]), 0.01) for v in r_oth.values())))
        ok &= g1[m]["pass_"]
    G["G1_adapter_active"] = g1
    gs_ = []
    for d, sid in (("fwd", sids[0]), ("rev", sids[1 % len(sids)])):
        ops, _ = group_ops("free", "hdA0", d, sid, caps, dirs, 1)
        for op in ops:
            op["log"] = True
        gs_.append((ops, ctx[(DIRS[d][1], sid)]["ids"]))
    rows = [o for g in gs_ for o in g[0]]; inp, am, P = pad_rows([g[1] for g in gs_ for _ in g[0]])
    set_pos(rows, P, 0)
    with use(model, "hdA0"):
        hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; hk.keep = {16, 40, 63}; hk.cap = {}
        with torch.no_grad():
            model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
        hk.mode = None; hk.keep = None
    g3, meas = {}, 0.0
    for r, op in enumerate(rows):
        if op["arm"] not in ("r1", "c1"):
            continue
        r0 = [q for q, o in enumerate(rows) if o["grp"] == op["grp"] and o["arm"] == "none"][0]
        for L in (16, 40, 63):
            u = op["U"][L]; got = hk.cap[L][r] @ u; want = op["D"][:, L].float() @ u
            gap = (want - hk.cap[L][r0] @ u).abs().mean()
            err = float((got - want).abs().max()); meas = max(meas, err)
            g3[f"{op['grp']}|{op['arm']}|L{L}"] = dict(coord_err_max=err, gap_mean=float(gap))
    hk.cap = {}
    sub_ok = all(v["coord_err_max"] <= tol["coord_rel"] * max(v["gap_mean"], 1.0) + tol["coord_abs"] for v in g3.values())
    W = K.hook_checks(hk.log, ops_meta(rows), tol)
    cg = K.cum_gate(K.cum_ratios(hk.log, real=K.REAL_MATCH))
    G["G3_hook_known_answers"] = dict(sub_detail=g3, sub_pass=bool(sub_ok), sub_coord_abs_err_max=meas, arms=W, cumulative=cg,
                                      cum_r1_vs_c1=K.cum_gate(K.cum_ratios(hk.log, real="c1"), need=(), flag=("r1",))["arms"].get("r1"),
                                      pass_=bool(sub_ok and W["pass"] and cg["pass_"]))
    ok &= G["G3_hook_known_answers"]["pass_"]
    G["pass"] = bool(ok)
    os.makedirs(out_dir, exist_ok=True); json.dump(G, open(f"{out_dir}/gates.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(G, default=float)[:3000], flush=True)
    return G


# ------------------------------------------------------------------------------------------------- generation loop (resume by key)
def repair_tail(p):
    """sw028 D23: truncate a torn last line (no newline) before appending on resume. Returns the number of bytes dropped."""
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return 0
    with open(p, "rb+") as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b"\n":
            return 0
        f.seek(0); data = f.read(); cut = data.rfind(b"\n") + 1
        f.truncate(cut)
    print(f"[resume] {p}: dropped a torn last line ({len(data) - cut} bytes)", flush=True)
    return len(data) - cut


def run_gen(model, hk, tok, m, readout, ctx, caps, dirs, sids, dirs_run, run_dir, samples, max_new, batch_groups, max_batches=None):
    bridge = K.BRIDGES.get(readout)
    suffix = tok(bridge, add_special_tokens=False)["input_ids"] if bridge else []
    fn, lfn = f"{run_dir}/{readout}_{m}.jsonl", f"{run_dir}/log_{readout}_{m}.jsonl"
    repair_tail(fn); repair_tail(lfn)
    have = set()
    for r in K.jl(fn):
        have.add(r["key"])
    todo = []
    for sid in sids:
        for d in dirs_run:
            ops, meta = group_ops(readout, m, d, sid, caps, dirs, samples)
            if all(o["key"] in have for o in ops):
                continue
            todo.append((ops, ctx[(DIRS[d][1], sid)]["ids"], meta))
    todo.sort(key=lambda g: len(g[1]))   # similar prompt lengths share a batch; the arms of a group stay together
    print(m, readout, "groups todo", len(todo), "rows", sum(len(g[0]) for g in todo), flush=True)
    nb = -(-len(todo) // batch_groups)
    for bi, b0 in enumerate(range(0, len(todo), batch_groups)):
        if max_batches is not None and bi >= max_batches:
            print(f"[stop] max_batches {max_batches} reached (test)", flush=True); return
        for batch, rows, out, logs, tim in run_batch(model, hk, todo[b0:b0 + batch_groups], max_new, m, suffix, readout):
            res = {op["key"]: o for op, o in zip(rows, out)}
            assert len(res) == len(rows), "duplicate keys inside one batch"
            lines = []
            for ops, ids, meta in batch:
                for op in ops:
                    if op["key"] in have:   # sw012 review fix F2: a group left partial by a crash keeps the rows already written
                        continue
                    gen, n, fin = res[op["key"]]
                    txt = (bridge or "") + tok.decode(gen, skip_special_tokens=True)
                    have.add(op["key"])
                    lines.append(json.dumps(dict(key=op["key"], exp=K.EXP, readout=readout, model=m, direction=op["direction"],
                                                 recipient=op["recipient"], donor=op["donor"], sid=op["sid"], arm=op["arm"], sample=op["sample"],
                                                 text=txt, n_tok=n, finish=fin, max_new=max_new, gen_head=gen[:16], **meta)) + "\n")
            with open(lfn, "a") as f:   # logs before rows: a row on disk always has its group's logs
                f.write("".join(json.dumps(dict(readout=readout, **e)) + "\n" for e in logs))
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{run_dir}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, readout=readout, groups=[g[0][0]["grp"] for g in batch], max_new=max_new, t=time.strftime("%FT%T"), **tim)) + "\n")
            caps_hit = sum(1 for o in out if o[2] == "length")
            print(f"[gen] {m} {readout} batch {bi + 1}/{nb} {json.dumps(tim)} cap_hits {caps_hit}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)


def run(a, model, tok):
    """everything after the model load (the CPU fake-model test calls this with a fake model)."""
    readouts = a.readout.split(","); dirs_run = a.directions.split(",")
    assert all(r in K.READOUTS for r in readouts), readouts
    assert all(d in DIRS for d in dirs_run), dirs_run
    models = a.models.split(",")
    ctx, caps, dirs = load_inputs(("hdA0", "hdB0"), a.dirs_root)
    all_sids = sorted({sid for (_, sid) in ctx})
    sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    print("readouts", readouts, "directions", dirs_run, "sids", len(sids), "models", models, flush=True)
    blocks = acts.blocks(model)
    assert len(blocks) == 64
    hk = Hooks52(blocks)
    tol = K.tolerances(a.calib)
    print("tolerances", json.dumps(tol), flush=True)
    if a.gates:
        gs = a.gate_sids.split(",") if a.gate_sids else sids[:2]
        G = gates(model, hk, blocks, ctx, caps, dirs, gs, a.gates_out or a.run_dir, tol)
        if not G["pass"]:
            print("GATES_FAILED", flush=True); hk.remove(); return 3
    for ro in readouts:
        rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
        for m in models:
            with use(model, m):
                run_gen(model, hk, tok, m, ro, ctx, caps, dirs, sids, dirs_run, rd, a.samples,
                        K.FORCED_TOKENS if ro in K.BRIDGES else a.max_new, a.forced_batch_groups if ro in K.BRIDGES else a.batch_groups,
                        max_batches=a.max_batches)
        print(f"READOUT_DONE {ro} {time.strftime('%H:%M:%S')}", flush=True)
    hk.remove()
    print("GEN52_EXIT", flush=True)
    return 0


def parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readout", required=True, help="free | fbtw | fraf, or a comma list (one model load for all)")
    ap.add_argument("--directions", required=True, help="rev (induce) | fwd (remove) | rev,fwd")
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None)
    ap.add_argument("--max_new", type=int, default=2048); ap.add_argument("--batch_groups", type=int, default=10)
    ap.add_argument("--forced_batch_groups", type=int, default=20)
    ap.add_argument("--samples", type=int, default=2); ap.add_argument("--gates", action="store_true")
    ap.add_argument("--run_dir", default=RUN, help="root; each readout writes to <run_dir>/<readout>/")
    ap.add_argument("--dirs_root", default=RUN, help="where dirs52_<m>.pt live")
    ap.add_argument("--gates_out", default=None); ap.add_argument("--gate_sids", default=None)
    ap.add_argument("--calib", default=None, help="calib.json from the smoke (default: common52.CALIB if it exists)")
    ap.add_argument("--max_batches", type=int, default=None, help="tests only: stop after this many batches per (readout, model)")
    return ap


def main():
    a = parser().parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, LORA["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA["hdB0"], adapter_name="hdB0"); model.eval()
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    sys.exit(run(a, model, tok))


if __name__ == "__main__":
    main()
