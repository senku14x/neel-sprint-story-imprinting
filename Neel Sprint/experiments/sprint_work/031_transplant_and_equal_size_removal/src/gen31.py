"""sw031 GPU stage (prep agent, E2 Lane M, 31 Oct 2026): (A) cross-assignment header transplant; (B) removal at equal cumulative
size; (cal) the Part B clamp-scale calibration (prefill only); (size) the memory sizing test.
Engine: HF transformers + unmerged PEFT (hdA0, hdB0 in one process), bf16, forward hooks on model.model.layers[L] (block output,
pre-final-norm), prefill only: the 7 reply-start header tokens; decode steps are not patched. Code base: sw028 gen28_x.py
(contexts, r1, A clamp, batching, sampling, OOM split, resume, torn-tail repair) + sw006/sw007's whole-header transplant.

Donor states (Part A, skF): a batch-1, unpadded prefill of the donor model on the donor context in this process ('cap' mode),
header tokens at L16-63, kept on the CPU in bf16, BEFORE any recipient batch that uses them (donor first). Every capture is
checked against sw009's capture of the same model (G1). r1's donor coordinate comes from sw009's capture, exactly as sw028.

Parts / readouts (--part, comma list; one model load for all):
  cal   : prefill only, every script, both models: rows none, r1, A clamps along A0-A2 at a grid of scales c -> cal/log_cal_<m>.jsonl,
          then the interpolated c per (model, dose) and a verification prefill at those c -> cal/calibration.json (proposal only;
          the frozen scales are src/scales31.json, written after reading it).
  size  : the memory test: full-run batch shapes at the longest contexts, generation forced to max_new tokens (min_new_tokens),
          rows discarded; peak memory_allocated / memory_reserved -> size/sizing.json
  A     : readouts free (<= 2,048, T 0.7, --samples) and btw / raf (forced "By the way," / "Random animal fact: the" + 48 tokens,
          1 sample), arms none + {own_opp, x_opp, x_same, own_sk} x {L16-31, L32-63}, recipients UH and SH, both models.
  B     : free only, arms none, r1, A10_0-2, A05_0-1, A14_0-1, skF (remove: SH recipient, d_self donor = same script's UH).
Outputs (<run_dir>/<part>_<readout>/): rows_<m>.jsonl (one per reply, key sw031|part|readout|m|ctx|sid|arm|band|s<k>),
  log_<m>.jsonl (sample-0 rows: off / nrm / along / inc / derr at LOG15), timing.jsonl; GPU_DONE_<part>_<readout> only when
  the rows match the manifest. <run_dir>/gates.json (G1 adapter active on every capture; G3 known answers), manifest_<job>.json
  (code sha256, inputs, command line, host, GPU).
  CUDA_VISIBLE_DEVICES=3 python gen31.py --part cal|size|A|B[,...] [--readouts free,btw,raf] [--models hdA0,hdB0] [--sids a,b]
       [--samples 2] [--scales src/scales31.json] [--run_dir /root/runs/sw031/full] [--gates] [--job NAME]"""
import argparse, contextlib, glob, hashlib, json, os, socket, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common31 as C31  # noqa: E402
from hooks31 import Hooks31, check_order  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import acts  # noqa: E402  (acts.blocks: model.model.layers through the PEFT wrappers, as sw012 / sw028)

NS = "/workspace/Neel Sprint"
CAP = "/workspace/runs_executor/sw009_captures"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
DIRS28 = "/workspace/runs_executor/sw028"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
EOS = (248046, 248044)
PAD = 248044
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
FORCED_TOKENS = 48
ALL16 = frozenset(range(16, 64))
CAL_GRID = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)
G1_OWN_MAX = 0.06     # E2 D1: node-vs-box-1 header parity, worst per-(context, layer) median over tokens 0.042, bar 0.06
G1_SEP = 3.0          # sw028 G1: the other adapter / parent >= 3x further than the own capture
PRE_BAND_REL = 0.01   # band-2 rows before L32 must equal the none row: noise floor 0 (same input, same batch), failure >= 0.1
DEV = "cuda"


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def sha(p, big=1 << 30):
    """sha256 of a file; files > 1 GiB: size + sha256 of the first and last 16 MiB (stated in the manifest)."""
    h = hashlib.sha256(); n = os.path.getsize(p)
    with open(p, "rb") as f:
        if n <= big:
            for b in iter(lambda: f.read(1 << 24), b""):
                h.update(b)
            return dict(sha256=h.hexdigest(), size=n)
        h.update(f.read(1 << 24)); f.seek(n - (1 << 24)); h.update(f.read(1 << 24))
    return dict(sha256_head_tail_16MiB=h.hexdigest(), size=n)


def write_manifest(run_dir, job, args):
    os.makedirs(run_dir, exist_ok=True)
    code = {os.path.basename(p): sha(p) for p in sorted(glob.glob(f"{HERE}/*.py")) + [f"{HERE}/scales31.json"] if os.path.exists(p)}
    inputs = {p: sha(p) for p in [f"{SW8}/contexts.jsonl", f"{DIRS28}/dirs28_hdA0.pt", f"{DIRS28}/dirs28_hdB0.pt",
                                   f"{CAP}/hdA0.pt", f"{CAP}/hdB0.pt", f"{CAP}/parent.pt"] + [f"{LORA[m]}/adapter_model.safetensors" for m in LORA]
              + ([args.scales] if args.scales else [])}
    M = dict(job=job, argv=sys.argv, t=time.strftime("%FT%TZ", time.gmtime()), host=socket.gethostname(),
             cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"), gpu=torch.cuda.get_device_name(0), code=code, inputs=inputs,
             torch=torch.__version__)
    json.dump(M, open(f"{run_dir}/manifest_{job}.json", "w"), indent=1)
    return M


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs():
    ctx = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        for short, cond in C31.CTX.items():
            if c["cond"] == cond:
                assert c["ids"][-7:] == HEADER, c["sid"]
                ctx[(short, c["sid"])] = c
    caps = {}
    for m in ("hdA0", "hdB0", "parent"):
        C = torch.load(f"{CAP}/{m}.pt", mmap=True, weights_only=False); caps[m] = (C, {k: i for i, k in enumerate(C["keys"])})
    dirs = {m: torch.load(f"{DIRS28}/dirs28_{m}.pt", weights_only=False) for m in C31.MODELS}
    sids = sorted({s for (_, s) in ctx})
    for m in C31.MODELS:
        assert all(dirs[m]["script"][s]["scenario"] == C31.scenario_of(s) for s in sids), "scenario rule differs from dirs28"
    return ctx, caps, dirs, sids


_DEVC = {}


def dev_dirs(dm, m, sc):
    k = (m, sc)
    if k not in _DEVC:
        S = dm["scen"][sc]; un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(DEV)
        _DEVC[k] = dict(u=un(S["u"]), A=un(S["A"]))
    return _DEVC[k]


# ------------------------------------------------------------------------------------------------- donor capture + G1
def capture_states(model, hk, ctx, need, states):
    """batch-1 unpadded prefill of each needed (model, ctx, sid); header tokens at L16-63 -> states[key] [7, 48, H] bf16 (CPU)."""
    todo = sorted(k for k in need if k not in states)
    t0 = time.time()
    for m in ("hdA0", "hdB0"):
        ks = [k for k in todo if k[0] == m]
        if not ks:
            continue
        with use(model, m), torch.no_grad():
            for k in ks:
                ids = ctx[(k[1], k[2])]["ids"]
                hk.mode = "cap"; hk.cap = {}
                model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
                hk.mode = None
                states[k] = torch.stack([hk.cap[L][0] for L in range(16, 64)], 1).cpu()   # [7, 48, H]
                hk.cap = {}
    if todo:
        print(f"[cap] {len(todo)} donor captures in {time.time() - t0:.0f}s", flush=True)
    return states


def relt(a, b):
    """per-token relative distance [7] of header states [7, H]."""
    return (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)


def g1_check(states, caps, layers=(16, 40, 63)):
    """every live capture vs sw009's capture of the same model (median over tokens 1-6 per layer <= G1_OWN_MAX) and >= G1_SEP x
    further from the other organism's and the parent's at L40 / L63."""
    worst_own, worst_sep, fails = 0.0, 1e9, []
    for (m, cx, sid), X in states.items():
        key = f"sw008|{C31.CTX[cx]}|{sid}"
        def med(mm, L):
            Cm, im = caps[mm]; ref = torch.as_tensor(Cm["hdr"][im[key]][:, L])
            return float(relt(X[:, L - 16], ref)[1:].median())
        own = max(med(m, L) for L in layers)
        oth = min(med(o, L) for o in (C31.OTHER[m], "parent") for L in (40, 63))
        worst_own = max(worst_own, own); worst_sep = min(worst_sep, oth / max(own, 1e-6))
        if not (own <= G1_OWN_MAX and oth >= G1_SEP * own):
            fails.append(dict(key=f"{m}|{cx}|{sid}", own=own, other_min=oth))
    return dict(n=len(states), worst_own_median_rel=worst_own, worst_other_over_own=worst_sep, fails=fails[:10], n_fail=len(fails),
                pass_=bool(not fails and len(states) > 0))


# ------------------------------------------------------------------------------------------------- group ops
def materialize(rows):
    """move each row's donor tensors to the GPU for one forward (deduplicated by source tensor); release() drops them."""
    cache = {}
    for op in rows:
        if "Dsrc" in op:
            op["Dfull"] = cache.setdefault(id(op["Dsrc"]), op["Dsrc"].to(DEV))
        if "Dsub_src" in op:
            op["D"] = cache.setdefault(id(op["Dsub_src"]), op["Dsub_src"].to(DEV))


def release(rows):
    for op in rows:
        op.pop("Dfull", None); op.pop("D", None)


def group_ops_A(readout, m, ctx_, sid, states, skm, samples, cache):
    grp = C31.group_id("A", m, ctx_, sid); ops = []
    for arm, band in C31.CELLS_A:
        for k in range(samples):
            op = dict(kind="none" if arm == "none" else "full", grp=grp, arm=arm, band=band, cell=arm if arm == "none" else f"{arm}@{band}",
                      sample=k, key=C31.row_key("A", readout, m, ctx_, sid, arm, band, k), model=m, ctx=ctx_, sid=sid, log=(k == 0),
                      layers=frozenset(), donor=None)
            if arm != "none":
                dk = C31.donor_A(arm, m, ctx_, sid, skm)
                op.update(Dsrc=states[dk], layers=frozenset(C31.BANDS_A[band]), donor="|".join(dk))
            ops.append(op)
    check_order(ops)
    return ops


def group_ops_B(m, sid, caps, dirs, states, skm, scales, samples, cache, cal_grid=None):
    """Part B rows (cal_grid=None) or the calibration rows (none, r1, A_i at every c of cal_grid, i = 0..2)."""
    Cm, idx = caps[m]; dm = dirs[m]; grp = C31.group_id("B" if cal_grid is None else "cal", m, C31.SH, sid)
    sc = dm["script"][sid]["scenario"]; T = dev_dirs(dm, m, sc); sg = dm["sign"][f"fwd|{sid}"]
    Dn = torch.as_tensor(Cm["hdr"][idx[f"sw008|user-hostile|{sid}"]])   # r1's donor [7, 64, H] fp16 (sw009), exactly as sw028
    base = dict(grp=grp, model=m, ctx=C31.SH, sid=sid, band="-", donor=None)
    spec = {"none": dict(base, kind="none", layers=frozenset()),
            "r1": dict(base, kind="sub", U=T["u"], Dsub_src=Dn, real=True, layers=ALL16, donor=f"{m}|UH|{sid}(sw009)")}
    if cal_grid is None:
        for arm, (dose, i) in C31.B_CLAMP.items():
            spec[arm] = dict(base, kind="A", R=T["A"][i], s=float(sg["s_A"][i]), c=float(scales[m].get(arm, scales[m][dose])), match=f"{grp}:r1", layers=ALL16)
        dk = C31.donor_B_skF(m, sid, skm)
        spec["skF"] = dict(base, kind="full", Dsrc=states[dk], layers=frozenset(C31.SKF_LAYERS), donor="|".join(dk))
        arms = C31.ARMS_B
    else:
        arms = ["none", "r1"]
        for i in range(3):
            for c in cal_grid:
                a = f"cal{i}_{c:g}"; arms.append(a)
                spec[a] = dict(base, kind="A", R=T["A"][i], s=float(sg["s_A"][i]), c=float(c), match=f"{grp}:r1", layers=ALL16)
    ops = []
    for arm in arms:
        for k in range(samples):
            ops.append(dict(spec[arm], arm=arm, cell=arm, sample=k, key=C31.row_key("B", "free", m, C31.SH, sid, arm, "-", k), log=(k == 0)))
    check_order(ops)
    return ops


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
def generate_batch(model, hk, groups, max_new, seed, suffix, force_len=False):
    rows, ids_rows = [], []
    for ops, ids in groups:
        assert ids[-7:] == HEADER
        rows += ops; ids_rows += [ids + suffix] * len(ops)
    inp, am, P = pad_rows(ids_rows); ns = len(suffix)
    set_pos(rows, P, ns)
    assert all(inp[r, rows[r]["pos"]].tolist() == HEADER for r in range(len(rows))), "patched positions are not the header"
    check_order(rows); materialize(rows)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
    torch.manual_seed(seed); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
    kw = dict(min_new_tokens=max_new) if force_len else {}
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD, **kw)
    torch.cuda.synchronize(); wall = time.time() - t0; hk.mode = None; hk.ops = None; release(rows)
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []; del o
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_alloc_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2), peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2),
               gen_tokens=int(sum(x[1] for x in out)), hook_calls=hk.calls - c0)
    assert tim["hook_calls"] == 48, f"hook fired {tim['hook_calls']} times in one generate (expected 48: prefill only, L16-63)"
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, tag, suffix):
    """sw012 review fix F3: on CUDA OOM split the batch into halves (whole groups, so every A row stays in its r1 row's forward)."""
    oom = False
    try:
        res = generate_batch(model, hk, [(g[0], g[1]) for g in batch], max_new, seed_of("sw031", tag, batch[0][0][0]["grp"], max_new), suffix)
    except torch.cuda.OutOfMemoryError:
        oom = True
    if not oom:
        return [(batch,) + res]
    hk.mode = None; hk.log = []; hk.ops = None
    for g in batch:
        release(g[0])
    import gc
    gc.collect(); torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError(f"CUDA OOM on a single group ({batch[0][0][0]['grp']})")
    h = len(batch) // 2
    print(f"[oom] {tag}: batch of {len(batch)} groups split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, tag, suffix) + run_batch(model, hk, batch[h:], max_new, tag, suffix)


def repair_tail(p):
    """sw028 D23: truncate a torn last line (no newline) before appending on resume."""
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


def run_gen(model, hk, tok, part, readout, m, todo_fn, rd, max_new, batch_groups):
    """todo_fn(have) -> list of (ops, ids, meta) groups not yet complete. Writes rows / logs / timing incrementally."""
    os.makedirs(rd, exist_ok=True)
    suffix = tok(C31.BRIDGES[readout], add_special_tokens=False)["input_ids"] if readout in C31.BRIDGES else []
    fn, lfn = f"{rd}/rows_{m}.jsonl", f"{rd}/log_{m}.jsonl"
    repair_tail(fn); repair_tail(lfn)
    have = set()
    if os.path.exists(fn):
        for l in open(fn):
            try:
                have.add(json.loads(l)["key"])
            except json.JSONDecodeError:
                pass
    todo = todo_fn(have)
    todo.sort(key=lambda g: len(g[1]))   # similar prompt lengths share a batch; the arms of a group stay together
    print(part, readout, m, "groups todo", len(todo), "rows", sum(len(g[0]) for g in todo), flush=True)
    nb = -(-len(todo) // batch_groups)
    for b0 in range(0, len(todo), batch_groups):
        for batch, rows, out, logs, tim in run_batch(model, hk, todo[b0:b0 + batch_groups], max_new, f"{part}|{readout}|{m}", suffix):
            res = {op["key"]: o for op, o in zip(rows, out)}
            assert len(res) == len(rows), "duplicate keys inside one batch"
            lines = []
            for ops, ids, meta in batch:
                for op in ops:
                    if op["key"] in have:
                        continue
                    gen, n, fin = res[op["key"]]
                    txt = (C31.BRIDGES.get(readout, "")) + tok.decode(gen, skip_special_tokens=True)
                    have.add(op["key"])
                    lines.append(json.dumps(dict(key=op["key"], exp="sw031", part=part, readout=readout, model=m, ctx=op["ctx"], sid=op["sid"],
                                                 arm=op["arm"], band=op["band"], cell=op["cell"], sample=op["sample"], donor=op["donor"],
                                                 c=op.get("c"), text=txt, n_tok=n, finish=fin, max_new=max_new, gen_head=gen[:16], **meta)) + "\n")
            with open(lfn, "a") as f:   # logs before rows: a row on disk always has its group's logs
                f.write("".join(json.dumps(dict(part=part, readout=readout, **e)) + "\n" for e in logs))
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{rd}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, part=part, readout=readout, groups=[g[0][0]["grp"] for g in batch], max_new=max_new,
                                        t=time.strftime("%FT%TZ", time.gmtime()), **tim)) + "\n")
            caps_hit = sum(1 for o in out if o[2] == "length")
            print(f"[gen] {part}|{readout}|{m} batch {b0 // batch_groups + 1}/{nb} {json.dumps(tim)} cap_hits {caps_hit}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)
    return have


# ------------------------------------------------------------------------------------------------- G3 known answers on the GPU
def prefill(model, hk, groups, keep=None):
    rows = [o for g in groups for o in g[0]]; inp, am, P = pad_rows([g[1] for g in groups for _ in g[0]])
    set_pos(rows, P, 0); check_order(rows); materialize(rows)
    assert all(inp[r, rows[r]["pos"]].tolist() == HEADER for r in range(len(rows)))
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; hk.keep = keep; hk.cap = {}
    with torch.no_grad():
        model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
    hk.mode = None; hk.keep = None
    cap, log = hk.cap, hk.log; hk.cap = {}; hk.log = []
    return rows, cap, log


def hook_checks_B(logs, obk, tol_rel=0.02, tol_abs=0.5):
    """sw028 known answer on the live logs: A along-r offset = s * c * r1's cumulative offset (per layer, token); skF derr = 0."""
    by = C31.logs_by(logs)
    W = dict(A_along_err_rel=0.0, skF_derr_max=0.0, n_checked=0)
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = obk[(g, arm)]
            if op["kind"] == "A" and "r1" in v:
                for t in range(7):
                    want = op["s"] * op["c"] * v["r1"]["off"][t]
                    W["A_along_err_rel"] = max(W["A_along_err_rel"], (abs(e["along"][t] - want) - tol_abs) / max(abs(want), 1e-6))
                W["n_checked"] += 1
            if op["kind"] == "full" and L in op["layers"]:
                W["skF_derr_max"] = max(W["skF_derr_max"], e.get("derr", 1e9)); W["n_checked"] += 1
    W["pass"] = bool(W["A_along_err_rel"] <= tol_rel and W["skF_derr_max"] == 0.0 and W["n_checked"] > 0)
    return W


def gates(model, hk, ctx, caps, dirs, states, skm, scales, gsids, parts):
    G = {"G1_adapter_active": g1_check(states, caps)}; ok = G["G1_adapter_active"]["pass_"]
    s0, s1 = gsids[0], gsids[1 % len(gsids)]
    cache = {}
    if "A" in parts:
        gs_ = [(group_ops_A("free", "hdA0", C31.UH, s0, states, skm, 1, cache), ctx[(C31.UH, s0)]["ids"]),
               (group_ops_A("free", "hdA0", C31.SH, s1, states, skm, 1, cache), ctx[(C31.SH, s1)]["ids"])]
        with use(model, "hdA0"):
            rows, cap, log = prefill(model, hk, gs_, keep={16, 31, 32, 63})
        none_r = {o["grp"]: r for r, o in enumerate(rows) if o["kind"] == "none"}
        ex, pre, post, size, ident = 0.0, 0.0, {}, {}, True
        for r, op in enumerate(rows):
            if op["kind"] != "full":
                continue
            b0, b1 = C31.BAND_ENDS[op["band"]]
            dk = tuple(op["donor"].split("|")); ident &= bool(op["donor"] == "|".join(C31.donor_A(op["arm"], op["model"], op["ctx"], op["sid"], skm)))
            ident &= bool(torch.equal(op["Dfull"].cpu(), states[dk]))
            for L in (b0, b1):
                ex = max(ex, float((cap[L][r] - op["Dfull"][:, L - 16].float()).abs().max()))
            if op["band"] == "L32-63":
                for L in (16, 31):
                    pre = max(pre, float(relt(cap[L][r], cap[L][none_r[op["grp"]]])[1:].max()))
            else:
                post[op["cell"] + "|" + op["grp"]] = round(float(relt(cap[32][r], op["Dfull"][:, 16].float())[1:].median()), 4)
            size[op["cell"] + "|" + op["grp"]] = {f"L{L}": round(float(relt(op["Dfull"][:, L - 16].float(), cap[L][none_r[op["grp"]]])[1:].median()), 4)
                                                 for L in (b0, b1)}
        derr = max((e.get("derr", 0.0) for e in log), default=1e9)
        g3a = dict(transplant_exact_maxabs=ex, log_derr_max=derr, preband_rel_max=pre, donor_identity_ok=ident,
                   post_band_L32_rel_to_donor_L32=post, donor_vs_none_rel_at_band_ends=size, n_rows=len(rows),
                   pass_=bool(ex == 0.0 and derr == 0.0 and pre <= PRE_BAND_REL and ident))
        G["G3A_transplant_known_answers"] = g3a; ok &= g3a["pass_"]
    if "B" in parts or "cal" in parts:
        sc_ = scales if "B" in parts else {m: {d: 1.0 for d in C31.DOSE_TARGET} for m in C31.MODELS}
        gs_ = [(group_ops_B("hdA0", s, caps, dirs, states, skm, sc_, 1, cache), ctx[(C31.SH, s)]["ids"]) for s in (s0, s1)]
        with use(model, "hdA0"):
            rows, cap, log = prefill(model, hk, gs_, keep={16, 40, 63})
        none_r = {o["grp"]: r for r, o in enumerate(rows) if o["kind"] == "none"}
        r1d = {}
        for r, op in enumerate(rows):
            if op["arm"] == "r1":
                for L in (16, 40, 63):
                    u = op["U"][L]; got = cap[L][r] @ u; want = op["D"][:, L].float() @ u
                    gap = (want - cap[L][none_r[op["grp"]]] @ u).abs().mean()
                    r1d[f"{op['grp']}|L{L}"] = dict(coord_err_max=float((got - want).abs().max()), gap_mean=float(gap))
            if op["kind"] == "full":
                for L in (16, 63):
                    r1d[f"{op['grp']}|skF|L{L}"] = dict(exact_maxabs=float((cap[L][r] - op["Dfull"][:, L - 16].float()).abs().max()))
        r1_ok = all(v["coord_err_max"] <= 0.05 * max(v["gap_mean"], 1.0) + 0.5 for k, v in r1d.items() if "coord_err_max" in v)
        sk_ok = all(v["exact_maxabs"] == 0.0 for k, v in r1d.items() if "exact_maxabs" in v)
        W = hook_checks_B(log, {(o["grp"], o["cell"]): o for o in rows})
        per = C31.cum_ratios(log, "r1")
        g3b = dict(detail=r1d, r1_pass=bool(r1_ok), skF_exact=bool(sk_ok), arms=W,
                   cumulative={a: {b: C31.median(v) for b, v in bb.items()} for a, bb in per.items()}, scales_used=sc_["hdA0"],
                   pass_=bool(r1_ok and sk_ok and W["pass"]))
        G["G3B_clamp_known_answers"] = g3b; ok &= g3b["pass_"]
    G["pass"] = bool(ok)
    return G


# ------------------------------------------------------------------------------------------------- calibration
def interp_c(curve, target):
    """curve: sorted [(c, ratio)] (ratio increasing in c) -> c with ratio = target by piecewise-linear interpolation."""
    for (c0, r0), (c1, r1) in zip(curve, curve[1:]):
        if (r0 - target) * (r1 - target) <= 0 and r1 != r0:
            return c0 + (target - r0) * (c1 - c0) / (r1 - r0)
    (c0, r0), (c1, r1) = (curve[0], curve[1]) if target < curve[0][1] else (curve[-2], curve[-1])
    return c0 + (target - r0) * (c1 - c0) / (r1 - r0)   # linear extrapolation (flagged by the caller)


def run_cal(model, hk, ctx, caps, dirs, states, skm, sids, run_dir, groups_per_fwd):
    rd = f"{run_dir}/cal"; os.makedirs(rd, exist_ok=True); cache = {}
    res = dict(grid=list(CAL_GRID), models={})
    for m in C31.MODELS:
        logs = []
        with use(model, m):
            for b0 in range(0, len(sids), groups_per_fwd):
                gs_ = [(group_ops_B(m, s, caps, dirs, states, skm, None, 1, cache, cal_grid=CAL_GRID), ctx[(C31.SH, s)]["ids"]) for s in sids[b0:b0 + groups_per_fwd]]
                _, _, lg = prefill(model, hk, gs_)
                logs += lg
        with open(f"{rd}/log_cal_{m}.jsonl", "w") as f:
            f.write("".join(json.dumps(e) + "\n" for e in logs))
        per = C31.cum_ratios(logs, "r1")
        tab = {}
        for i in range(3):
            for c in CAL_GRID:
                a = f"cal{i}_{c:g}"
                tab[a] = {b: C31.median(per[a][b]) for b in ("L28-40", "L44-63")}
        pooled = {}
        for dose, dirs_ in (("0.5", (0, 1)), ("1.0", (0, 1, 2)), ("1.4", (0, 1))):
            curve = [(c, C31.median([x for i in dirs_ for x in per[f"cal{i}_{c:g}"]["L44-63"]])) for c in CAL_GRID]
            cc = interp_c(curve, C31.DOSE_TARGET[dose])
            pooled[dose] = dict(curve=curve, c=round(cc, 4), extrapolated=bool(not (curve[0][1] <= C31.DOSE_TARGET[dose] <= curve[-1][1])))
        res["models"][m] = dict(table=tab, proposal=pooled, n_scripts=len(sids))
        print("[cal]", m, json.dumps({d: (v["c"], v["extrapolated"]) for d, v in pooled.items()}), flush=True)
    # verification prefill at the proposed scales (every Part B arm, every script)
    prop = {m: {d: res["models"][m]["proposal"][d]["c"] for d in C31.DOSE_TARGET} for m in C31.MODELS}
    res["verify"] = {}
    for m in C31.MODELS:
        logs = []
        with use(model, m):
            for b0 in range(0, len(sids), groups_per_fwd):
                gs_ = [(group_ops_B(m, s, caps, dirs, states, skm, prop, 1, cache), ctx[(C31.SH, s)]["ids"]) for s in sids[b0:b0 + groups_per_fwd]]
                _, _, lg = prefill(model, hk, gs_)
                logs += lg
        with open(f"{rd}/log_verify_{m}.jsonl", "w") as f:
            f.write("".join(json.dumps(e) + "\n" for e in logs))
        cg = C31.cum_gate_B(C31.cum_ratios(logs, "r1"))
        res["verify"][m] = dict(scales=prop[m], gate=cg)
        print("[cal-verify]", m, json.dumps({a: (round(v["median_ratio"]["L44-63"], 3), v.get("pass_")) for a, v in cg["arms"].items()}), "pass", cg["pass_"], flush=True)
    json.dump(res, open(f"{rd}/calibration.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------- memory sizing
def run_size(model, hk, tok, ctx, caps, dirs, states, skm, scales, sids, run_dir, a):
    """full-run batch shapes at the longest contexts, generation forced to max_new tokens (rows discarded)."""
    rd = f"{run_dir}/size"; os.makedirs(rd, exist_ok=True); cache = {}; out = []
    uh = sorted(sids, key=lambda s: -len(ctx[(C31.UH, s)]["ids"])); sh = sorted(sids, key=lambda s: -len(ctx[(C31.SH, s)]["ids"]))
    tests = [("A_free", "free", a.max_new, a.batch_groups_A, [(group_ops_A("free", "hdA0", C31.UH, s, states, skm, a.size_samples, cache), ctx[(C31.UH, s)]["ids"]) for s in uh[:a.batch_groups_A]]),
             ("A_forced_raf", "raf", FORCED_TOKENS, a.forced_batch_groups, [(group_ops_A("raf", "hdA0", C31.UH, s, states, skm, 1, cache), ctx[(C31.UH, s)]["ids"]) for s in uh[:a.forced_batch_groups]]),
             ("B_free", "free", a.max_new, a.batch_groups_B, [(group_ops_B("hdA0", s, caps, dirs, states, skm, scales, a.size_samples, cache), ctx[(C31.SH, s)]["ids"]) for s in sh[:a.batch_groups_B]])]
    for name, ro, mx, bg, groups in tests:
        if a.size_only and name not in a.size_only.split(","):
            continue
        suffix = tok(C31.BRIDGES[ro], add_special_tokens=False)["input_ids"] if ro in C31.BRIDGES else []
        gc_ = __import__("gc"); gc_.collect(); torch.cuda.empty_cache()
        with use(model, "hdA0"):
            try:
                _, o, _, tim = generate_batch(model, hk, groups, mx, seed_of("sw031size", name), suffix, force_len=True)
                r = dict(test=name, ok=True, groups=bg, **tim, all_rows_at_max=bool(all(x[1] == mx for x in o)))
            except torch.cuda.OutOfMemoryError as e:
                hk.mode = None
                r = dict(test=name, ok=False, groups=bg, error="OOM", peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2))
        r["total_gib"] = round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2)
        out.append(r); print("[size]", json.dumps(r), flush=True)
        json.dump(out, open(f"{rd}/sizing.json", "w"), indent=1)
    return out


# ------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True); ap.add_argument("--readouts", default="free,btw,raf")
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None)
    ap.add_argument("--max_new", type=int, default=2048); ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--batch_groups_A", type=int, default=3); ap.add_argument("--batch_groups_B", type=int, default=3)
    ap.add_argument("--forced_batch_groups", type=int, default=8); ap.add_argument("--cal_groups", type=int, default=3)
    ap.add_argument("--scales", default=None); ap.add_argument("--run_dir", default="/root/runs/sw031/full")
    ap.add_argument("--gates", action="store_true"); ap.add_argument("--gate_sids", default=None)
    ap.add_argument("--job", default="job"); ap.add_argument("--size_only", default=None)
    ap.add_argument("--size_samples", type=int, default=2, help="samples per arm in the sizing test (the full run's free value)")
    a = ap.parse_args()
    parts = a.part.split(","); assert all(p in ("cal", "size", "A", "B") for p in parts), parts
    readouts = a.readouts.split(","); assert all(r in C31.READOUTS_A for r in readouts), readouts
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    models = a.models.split(",")
    scales = None
    if a.scales:
        S = json.load(open(a.scales))   # per (model, dose); optional per-arm overrides S["per_arm"][m][arm] (D15)
        scales = {m: dict({d: float(S["scales"][m][d]) for d in C31.DOSE_TARGET}, **{k: float(v) for k, v in S.get("per_arm", {}).get(m, {}).items()})
                  for m in C31.MODELS}
    assert not ({"B", "size"} & set(parts)) or scales, "Part B / size need --scales (the frozen calibration)"
    os.makedirs(a.run_dir, exist_ok=True)
    M = write_manifest(a.run_dir, a.job, a)
    tok = AutoTokenizer.from_pretrained(BASE)
    ctx, caps, dirs, all_sids = load_inputs()
    sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    skm = C31.sk_map(all_sids)
    print("parts", parts, "readouts", readouts, "sids", len(sids), "models", models, flush=True)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, LORA["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA["hdB0"], adapter_name="hdB0"); model.eval()
    blocks = acts.blocks(model); assert len(blocks) == 64
    hk = Hooks31(blocks, C31.LOG15)
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    # donor captures needed by this job (donor first: all before any recipient batch)
    gsids = a.gate_sids.split(",") if a.gate_sids else sids[:2]
    need = set()
    for s in set(sids) | set(gsids):
        for m in C31.MODELS:
            for cx in (C31.UH, C31.SH):
                for arm in C31.ARMS_A:
                    need.add(C31.donor_A(arm, m, cx, s, skm))
            need.add(C31.donor_B_skF(m, s, skm))
    states = capture_states(model, hk, ctx, need, {})
    if a.gates:
        G = gates(model, hk, ctx, caps, dirs, states, skm, scales, gsids, parts)
        json.dump(G, open(f"{a.run_dir}/gates_{a.job}.json", "w"), indent=1, default=float)
        print("GATES", json.dumps(G, default=float)[:3000], flush=True)
        if not G["pass"]:
            print("GATES_FAILED", flush=True); sys.exit(3)
    if "cal" in parts:
        run_cal(model, hk, ctx, caps, dirs, states, skm, sids, a.run_dir, a.cal_groups)
    if "size" in parts:
        run_size(model, hk, tok, ctx, caps, dirs, states, skm, scales, sids, a.run_dir, a)
    cache = {}
    if "A" in parts:
        for ro in readouts:
            rd = f"{a.run_dir}/A_{ro}"; ns = a.samples if ro == "free" else 1
            for m in models:
                def todo_fn(have, m=m, ro=ro, ns=ns):
                    out = []
                    for s in sids:
                        for cx in (C31.UH, C31.SH):
                            ops = group_ops_A(ro, m, cx, s, states, skm, ns, cache)
                            if not all(o["key"] in have for o in ops):
                                out.append((ops, ctx[(cx, s)]["ids"], dict(scenario=C31.scenario_of(s))))
                    return out
                with use(model, m):
                    run_gen(model, hk, tok, "A", ro, m, todo_fn, rd, a.max_new if ro == "free" else FORCED_TOKENS,
                            a.batch_groups_A if ro == "free" else a.forced_batch_groups)
                cache.clear(); torch.cuda.empty_cache()
            done_marker(rd, "A", ro, models, sids, ns, a.run_dir)
    if "B" in parts:
        rd = f"{a.run_dir}/B_free"
        for m in models:
            def todo_fn(have, m=m):
                out = []
                for s in sids:
                    ops = group_ops_B(m, s, caps, dirs, states, skm, scales, a.samples, cache)
                    if not all(o["key"] in have for o in ops):
                        out.append((ops, ctx[(C31.SH, s)]["ids"], dict(scenario=C31.scenario_of(s))))
                return out
            with use(model, m):
                run_gen(model, hk, tok, "B", "free", m, todo_fn, rd, a.max_new, a.batch_groups_B)
            cache.clear(); torch.cuda.empty_cache()
        done_marker(rd, "B", "free", models, sids, a.samples, a.run_dir)
    print("GEN31_EXIT", flush=True)


def done_marker(rd, part, ro, models, sids, ns, run_dir):
    """GPU_DONE_<part>_<readout> only when every expected key (manifest) is present exactly once."""
    exp = set(C31.expected_keys(part, ro, models, sids, ns)); got = []
    for m in models:
        p = f"{rd}/rows_{m}.jsonl"
        if os.path.exists(p):
            for l in open(p):
                try:
                    got.append(json.loads(l)["key"])
                except json.JSONDecodeError:
                    pass
    ok = set(got) == exp and len(got) == len(set(got))
    msg = dict(part=part, readout=ro, expected=len(exp), present=len(set(got) & exp), duplicates=len(got) - len(set(got)), extra=len(set(got) - exp))
    print("COMPLETENESS", json.dumps(msg), flush=True)
    if ok:
        with open(f"{run_dir}/GPU_DONE_{part}_{ro}", "w") as f:
            f.write(json.dumps(msg) + "\n")


if __name__ == "__main__":
    main()
