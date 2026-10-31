"""sw038 Part 1 GPU stage (prep-P1 agent, E2, 31 Oct 2026): the rank-1 core on v2 G3. Adapted from sw029 gen29_x.py (engine,
left padding, sampling, OOM split by whole units, resume by key, torn-tail repair, inline gates, memory probe) and sw031 gen31.py
(prefill-only clamp-scale calibration, skF whole-state arm). Engine: HF transformers + unmerged PEFT, ONE organism per process,
bf16, forward hooks on model.model.layers[L] (block output, pre-final-norm); edits at layers 16-63, prefill only.
Unit = (model, direction, script, sample): induce 11 rows (none, r1, asT, c1, r1_A0-2, asT_A0-1, c1_A0-1), remove 12 (+ skF).
  sub rows: coordinate along u set to the target computed IN THE RECIPIENT (header: the recipient's own new capture of the donor
            context . u per token; asT: the donor's mean coordinate asst_mean_donor . u at every recipient Assistant turn-1-2 content
            token, sw029 D7; c1: ctrlB0's direction with the hd recipient's donor-context target, sw052);
  A rows  : dirs38p1 nulls clamped to x_none . r + k_L * s * Delta_arm (live) at the arm's positions, k_L from the frozen scales file;
  skF     : the recipient model's own bf16 capture of another script's self-hostile header (common38p1.sk_map), L16-63.
Modes (one process may run several, in this order): --cal (prefill-only calibration of every A arm's k, D-entry), --gates (G1 +
G3), --mem_probe SPEC, then generation of --readout x --directions.
Readouts: free (<= 2,048 new tokens, T 0.7, top_p 1, top_k 0; primary) and fbtw ("By the way," after the header, unpatched, +48
sampled tokens; pilot). Samples: free induce 2, free remove 1, forced 1 (--samples overrides, e.g. 1 in the smoke).
Outputs per readout dir <run_dir>/<readout>/: <readout>_<m>_<d>.jsonl (keys sw038|p1|<readout>|<m>|<d>|<sid>|<arm>|s<k>),
log_<readout>_<m>_<d>.jsonl (s0 units, 14 layers), timing_<m>_<d>.jsonl; <run_dir>/code_manifest_<job>.json.
  CUDA_VISIBLE_DEVICES=2 python gen38p1.py --model hdA0 --readout free,fbtw --directions induce --scales S --gates --calib C
         [--sids a,b] [--samples 1] [--run_dir D] [--batch_units 4] [--forced_batch_units 6] [--mem_probe SPEC] [--cal OUTDIR]"""
import argparse, contextlib, gc, hashlib, json, os, socket, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p1 as K  # noqa: E402
from hooks38p1 import Hooks38, Cap, check_order  # noqa: E402
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"

NS = "/workspace/Neel Sprint"
RUN = "/root/runs/sw038/p1"
CTX = f"{RUN}/inputs/contexts38p1.jsonl"
CAPS = "/root/caps/sw038p1"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
EOS = (248046, 248044)
PAD = 248044
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
DEV = "cuda"
CAL_GRID = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)
CAL_GRID2 = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)
SINGLE_TOL = 0.05     # a single k is used when it puts both bands' interpolated pooled median within 1 +- 0.05 (else two segments)


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def cuda():
    return DEV == "cuda" and torch.cuda.is_available()


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def write_manifest(run_dir, job, argv):
    h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    files = {}
    for root, _, fs in os.walk(HERE):
        for f in sorted(fs):
            if f.endswith((".py", ".sh", ".json")) and "__pycache__" not in root:
                p = os.path.join(root, f); files[os.path.relpath(p, HERE)] = h(p)
    inp = {}
    for p in argv_paths(argv) + [CTX]:
        if os.path.isfile(p) and os.path.getsize(p) < 2 ** 31:
            inp[p] = h(p)
    os.makedirs(run_dir, exist_ok=True)
    json.dump(dict(job=job, host=socket.gethostname(), gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), start=time.strftime("%FT%TZ", time.gmtime()),
                   argv=argv, code_sha256=files, inputs_sha256=inp), open(f"{run_dir}/code_manifest_{job}.json", "w"), indent=1)


def argv_paths(argv):
    return [x for x in argv if x.startswith("/")]


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs(m, dirs_root, caps_root):
    ctx = {(r["cond"], r["sid"]): r for r in K.jl(CTX)}
    assert len(ctx) == 122
    for r in ctx.values():
        assert r["ids"][-7:] == HEADER and r["apos"]
    C = torch.load(f"{caps_root}/cap_{m}.pt", weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
    dm = torch.load(f"{dirs_root}/dirs38p1_{m}.pt", weights_only=False)
    assert dm["model"] == m
    return ctx, (C, idx), dm


def load_scales(path, m):
    if not path:
        return None
    S = json.load(open(path))["scales"][m]
    for d in ("induce", "remove"):
        assert set(S[d]) == set(K.A_ARMS), (d, sorted(S[d]))
    return S


_DEVC = {}


def dev_dirs(dm, m, f):
    k = (m, f, DEV)
    if k not in _DEVC:
        un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(DEV)
        _DEVC[k] = dict(U={x: un(v) for x, v in dm["U"][f].items()}, A={nm: un(v) for nm, v in dm["A"][f].items()})
    return _DEVC[k]


_DFULL = {}


def dfull(C, idx, m, sid):
    k = (m, sid)
    if k not in _DFULL:
        _DFULL[k] = C["hdr"][idx[f"self-hostile|{sid}"]][:, 16:64].to(DEV)            # [7, 48, H] bf16, exact capture
    return _DFULL[k]


def unit_ops(readout, m, d, sid, k, ctx, cap, dm, scales, cal_rows=None):
    """rows of one unit (K.arms_of(d) order, or the calibration rows); positions are set per batch (set_pos).
    cal_rows: list of (row name '<A arm>~<tag>', A arm, kvec) replacing the production A rows (skF omitted)."""
    _, rec, don = K.DIRS[d]
    C, idx = cap; grp = K.unit_id(m, d, sid, k)
    f = dm["script"][sid]["fold"]; T = dev_dirs(dm, m, f); sg = dm["sign"][f"{d}|{sid}"]
    Dh = C["hdr"][idx[f"{don}|{sid}"]].to(DEV).float()                                   # [7, 64, H] recipient model, donor context
    Da = C["asst_mean"][idx[f"{don}|{sid}"]].to(DEV).float()                              # [64, H]
    na = len(ctx[(rec, sid)]["apos"])
    arms = list(K.arms_of(d)) if cal_rows is None else ["none"] + list(K.REAL) + [r[0] for r in cal_rows]
    calk = {r[0]: (r[1], r[2]) for r in (cal_rows or [])}
    ops = []
    for arm in arms:
        b = K.base_arm(arm)
        base = dict(arm=arm, sample=k, key=K.row_key(readout, m, d, sid, arm, k), grp=grp, site=K.SITE.get(b), model=m, direction=d,
                    recipient=rec, donor=don, sid=sid, log=(k == 0))
        if arm == "none":
            ops.append(dict(base, kind="none")); continue
        if arm in K.REAL:
            u = T["U"][K.FAMILY[arm]]
            if K.SITE[arm] == "hdr":
                tgt = torch.einsum("tlh,lh->lt", Dh, u).contiguous()                          # [64, 7]
            else:
                tgt = (Da * u).sum(-1)[:, None].expand(64, na).contiguous()                   # [64, na]
            ops.append(dict(base, kind="sub", U=u, tgt=tgt, real=True))
        elif arm == "skF":
            ops.append(dict(base, kind="full", Dfull=dfull(C, idx, m, dm["sk_map"][sid]), sk_donor=dm["sk_map"][sid]))
        else:
            if cal_rows is None:
                kv = K.kvec(scales[b]); kk = scales[b]                                       # scales = this direction's {A arm: {k1, k2}}
            else:
                kv = calk[arm][1]; kk = None
            ops.append(dict(base, kind="A", U=T["A"][b], s=float(sg[b]), k=kv, kk=kk, match=f"{grp}:{K.ARM_OF_A[b]}"))
    check_order(ops)
    meta = dict(domain=dm["script"][sid]["domain"], n_asst=na)
    return ops, meta


def set_pos(ops, P, n_ids, ns, apos0):
    """left padding: row = [PAD]*(P - n_ids - ns) + ids + suffix. Header = the 7 tokens before the suffix; Assistant = apos0 shifted."""
    off = P - n_ids - ns
    hpos = [off + n_ids - 7 + i for i in range(7)]; apos = [off + p for p in apos0]
    for op in ops:
        op["hpos"] = hpos
        if op["kind"] == "none":
            continue
        op["nh"] = 7 if op["site"] == "hdr" else 0
        op["pos"] = hpos if op["site"] == "hdr" else apos


def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


def build_batch(units, suffix):
    rows, idr = [], []
    for ops, ids, apos0, _ in units:
        rows += ops; idr += [ids + suffix] * len(ops)
    inp, am, P = pad_rows(idr)
    for ops, ids, apos0, _ in units:
        set_pos(ops, P, len(ids), len(suffix), apos0)
    for r, op in enumerate(rows):
        assert inp[r, op["hpos"]].tolist() == HEADER, "header positions are not the header"
    check_order(rows)
    return rows, inp, am, P


# ------------------------------------------------------------------------------------------------- generation
def generate_batch(model, hk, units, max_new, seed, suffix, min_new=None):
    rows, inp, am, P = build_batch(units, suffix)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
    torch.manual_seed(seed)
    if cuda():
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.time()
    kw = dict(min_new_tokens=min_new) if min_new else {}
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD, **kw)
    if cuda():
        torch.cuda.synchronize()
    wall = time.time() - t0; hk.mode = None
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), units=len(units), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_alloc_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2) if cuda() else 0.0,
               peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2) if cuda() else 0.0,
               gen_tokens=int(sum(x[1] for x in out)), hook_calls=hk.calls - c0)
    assert tim["hook_calls"] == 48, f"hook fired {tim['hook_calls']} times in one generate (expected 48: once per patched layer, prefill only)"
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, m, suffix, readout):
    """sw012 F3: on CUDA OOM split the batch into halves (whole units, so every A stays in its arm's forward)."""
    oom = False
    try:
        res = generate_batch(model, hk, batch, max_new, seed_of(K.EXP, K.PART, readout, m, batch[0][0][0]["grp"], max_new), suffix)
    except torch.cuda.OutOfMemoryError:
        oom = True
    if not oom:
        return [(batch,) + res]
    hk.mode = None; hk.log = []
    gc.collect(); torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError(f"CUDA OOM on a single unit ({batch[0][0][0]['grp']})")
    h = len(batch) // 2
    print(f"[oom] {m} {readout}: batch of {len(batch)} units split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, m, suffix, readout) + run_batch(model, hk, batch[h:], max_new, m, suffix, readout)


def prefill(model, hk, units):
    """one prefill-only forward (logits_to_keep=1) of the units with every row logged; returns (rows, logs)."""
    rows, inp, am, P = build_batch(units, [])
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
    with torch.no_grad():
        model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
    hk.mode = None; lg = hk.log; hk.log = []
    assert hk.calls - c0 == 48
    return rows, lg


# ------------------------------------------------------------------------------------------------- calibration (prefill only)
def interp(curve, target):
    """curve: [(k, ratio)] sorted by k, ratio increasing -> (k at ratio = target by piecewise-linear interpolation, extrapolated?)."""
    for (c0, r0), (c1, r1) in zip(curve, curve[1:]):
        if (r0 - target) * (r1 - target) <= 0 and r1 != r0:
            return c0 + (target - r0) * (c1 - c0) / (r1 - r0), False
    (c0, r0), (c1, r1) = (curve[0], curve[1]) if target < curve[0][1] else (curve[-2], curve[-1])
    return c0 + (target - r0) * (c1 - c0) / (r1 - r0), True


def at(curve, k):
    """ratio at k by piecewise-linear interpolation of the curve [(k, ratio)]."""
    for (c0, r0), (c1, r1) in zip(curve, curve[1:]):
        if c0 <= k <= c1:
            return r0 + (k - c0) * (r1 - r0) / (c1 - c0)
    (c0, r0), (c1, r1) = (curve[0], curve[1]) if k < curve[0][0] else (curve[-2], curve[-1])
    return r0 + (k - c0) * (r1 - r0) / (c1 - c0)


def cal_pass(model, hk, m, d, ctx, cap, dm, sids, rows_spec, upf):
    """prefill every script once with the calibration rows; -> per_unit_ratios over the s0 logs."""
    logs = []
    _, rec, _ = K.DIRS[d]
    for b0 in range(0, len(sids), upf):
        units = []
        for sid in sids[b0:b0 + upf]:
            ops, meta = unit_ops("cal", m, d, sid, 0, ctx, cap, dm, None, cal_rows=rows_spec)
            units.append((ops, ctx[(rec, sid)]["ids"], ctx[(rec, sid)]["apos"], meta))
        _, lg = prefill(model, hk, units)
        logs += lg
    return logs, K.per_unit_ratios(logs)


def run_cal(model, hk, m, ctx, cap, dm, sids, out_dir, upf):
    """D-entry (calibration). Per (direction, A arm): round 1 = a single k on the grid at every layer; k_b = the interpolated k at
    which the band's median (over the 61 scripts) is 1.0, per band. If one k puts both bands' interpolated medians within
    1 +- SINGLE_TOL, k1 = k2 = that k (the mean of the two band k's); else round 2: k1 = k_{L28-40} fixed at L16-40 and a grid over
    k2 at L41-63, k2 = the interpolated k at which L44-63's median is 1.0 (L28-40 is causally unaffected by k2; checked).
    Round 3 (verify): the production rows (none, r1, asT, c1, every A at its final (k1, k2), skF for remove) on every script; the
    gate = every A arm's median in [0.9, 1.1] at both bands. Writes cal_<m>.json, log_cal_<m>_<round>_<d>.jsonl, scales_proposal_<m>.json."""
    os.makedirs(out_dir, exist_ok=True); t0 = time.time()
    res = dict(model=m, grid=list(CAL_GRID), grid2=list(CAL_GRID2), n_scripts=len(sids), single_tol=SINGLE_TOL, directions={})
    prop = {}
    for d in ("induce", "remove"):
        R = dict(round1={}, choice={}, round2={}, verify={})
        spec = [(f"{a}~k{c:g}", a, [c] * 64) for a in K.A_ARMS for c in CAL_GRID]
        logs, per = cal_pass(model, hk, m, d, ctx, cap, dm, sids, spec, upf)
        open(f"{out_dir}/log_cal_{m}_r1_{d}.jsonl", "w").write("".join(json.dumps(e) + "\n" for e in logs))
        need2 = []
        for a in K.A_ARMS:
            cv = {b: [(c, K.median(list(per[f"{a}~k{c:g}"][b].values()))) for c in CAL_GRID] for b in K.GATE_BANDS}
            R["round1"][a] = {b: [[c, round(r, 4)] for c, r in v] for b, v in cv.items()}
            kb = {b: interp(cv[b], 1.0) for b in K.GATE_BANDS}
            ks = 0.5 * (kb["L28-40"][0] + kb["L44-63"][0])
            rs = {b: at(cv[b], ks) for b in K.GATE_BANDS}
            single = all(abs(v - 1.0) <= SINGLE_TOL for v in rs.values())
            R["choice"][a] = dict(k_band={b: round(v[0], 4) for b, v in kb.items()}, extrapolated={b: v[1] for b, v in kb.items()},
                                  single_k=round(ks, 4), single_pred=dict((b, round(v, 4)) for b, v in rs.items()), single=bool(single))
            if single:
                prop.setdefault(d, {})[a] = dict(k1=round(ks, 4), k2=round(ks, 4), two_segment=False)
            else:
                need2.append((a, kb["L28-40"][0]))
        print(f"[cal] {m} {d} round 1 {time.time() - t0:.0f}s", json.dumps({a: R["choice"][a] for a in K.A_ARMS})[:2000], flush=True)
        if need2:
            spec = [(f"{a}~k1{k1:.4f}~k2{c:g}", a, [k1 if L < K.SEG_SPLIT else c for L in range(64)]) for a, k1 in need2 for c in CAL_GRID2]
            logs, per = cal_pass(model, hk, m, d, ctx, cap, dm, sids, spec, upf)
            open(f"{out_dir}/log_cal_{m}_r2_{d}.jsonl", "w").write("".join(json.dumps(e) + "\n" for e in logs))
            for a, k1 in need2:
                cv = {b: [(c, K.median(list(per[f"{a}~k1{k1:.4f}~k2{c:g}"][b].values()))) for c in CAL_GRID2] for b in K.GATE_BANDS}
                k2, ex = interp(cv["L44-63"], 1.0)
                R["round2"][a] = dict(k1=round(k1, 4), curve={b: [[c, round(r, 4)] for c, r in v] for b, v in cv.items()}, k2=round(k2, 4),
                                      extrapolated=ex, L28_40_spread_over_k2=round(max(r for _, r in cv["L28-40"]) - min(r for _, r in cv["L28-40"]), 5))
                prop.setdefault(d, {})[a] = dict(k1=round(k1, 4), k2=round(k2, 4), two_segment=True)
            print(f"[cal] {m} {d} round 2 {time.time() - t0:.0f}s", json.dumps(R["round2"])[:2000], flush=True)
        # round 3: verification with the production rows at the proposed scales
        logs, per = [], None
        for b0 in range(0, len(sids), upf):
            units = []
            for sid in sids[b0:b0 + upf]:
                ops, meta = unit_ops("verify", m, d, sid, 0, ctx, cap, dm, prop[d])
                units.append((ops, ctx[(K.DIRS[d][1], sid)]["ids"], ctx[(K.DIRS[d][1], sid)]["apos"], meta))
            _, lg = prefill(model, hk, units)
            logs += lg
        open(f"{out_dir}/log_cal_{m}_verify_{d}.jsonl", "w").write("".join(json.dumps(e) + "\n" for e in logs))
        per = K.per_unit_ratios(logs); g = K.cum_gate(per)
        R["verify"] = dict(gate=g, per_script={a: {b: {k.split("|")[2]: round(v, 4) for k, v in per[a][b].items()} for b in K.GATE_BANDS} for a in K.A_ARMS})
        print(f"[cal-verify] {m} {d} pass {g['pass_']}", json.dumps({a: v["median_ratio"] for a, v in g["arms"].items()}), "vs_r1", json.dumps(g["vs_r1"]), flush=True)
        res["directions"][d] = R
    res["proposal"] = prop
    res["pass"] = bool(all(res["directions"][d]["verify"]["gate"]["pass_"] for d in ("induce", "remove")))
    json.dump(res, open(f"{out_dir}/cal_{m}.json", "w"), indent=1)
    json.dump(dict(model=m, scales=prop, created=time.strftime("%FT%TZ", time.gmtime()), source=f"{out_dir}/cal_{m}.json", verify_pass=res["pass"]),
              open(f"{out_dir}/scales_proposal_{m}.json", "w"), indent=1)
    print("CAL_DONE", m, "verify pass", res["pass"], f"{time.time() - t0:.0f}s", flush=True)
    return res


# ------------------------------------------------------------------------------------------------- GPU gates
def tokmed(a, b):
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def ops_meta(rows):
    return {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), k=o.get("k"), match=o.get("match")) for o in rows}


def gates(model, hk, blocks, m, ctx, cap, dm, scales, sids, out_dir, tol, caps_root):
    """G1 adapter active: live header states of one context vs m's own sw038 capture (same node; median over tokens 1-6 of the
    relative distance <= G1_OWN_NODE at L16/40/63) and >= g1_ratio x further from the other hd model's and the parent's sw038 captures.
    G3 known answers, one left-padded forward of 2 units (induce sids[0] s0, remove sids[1] s0) with every arm, every row logged:
      (a) hook_checks on the live logs (tolerances `tol`);
      (b) INDEPENDENT read-out (Cap hook after the edit hooks) at L15/16/40/63, positions re-derived from the padded ids, targets
          recomputed from the capture and dirs38p1 (not from the ops): sub coordinate = target; A (x_A - x_none).r = k_L s
          ||x_arm - x_none||; skF header = the donor tensor exactly (max |diff| == 0) at L16/40/63; at L15 every row equals the
          none row (nothing edited before L16); at L16 the positions an arm does not edit equal the none row's;
      (c) cumulative ratios of the 2 units (reported only: the size gate is the calibration verify on all 61 scripts, D-entry)."""
    G = {"tolerances": tol}; ok = True
    C, idx = cap
    sid0 = sids[0]; key0 = f"self-hostile|{sid0}"; ids0 = ctx[("self-hostile", sid0)]["ids"]
    capd = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: capd.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0, -7:].detach().float().cpu()))(L))
          for L in (16, 40, 63)]
    try:
        with torch.no_grad():
            model(input_ids=torch.tensor([ids0], device=DEV), logits_to_keep=1)
    finally:
        for h in hs:
            h.remove()
    r_own = max(tokmed(capd[L], C["hdr"][idx[key0]][:, L]) for L in (16, 40, 63))
    r_oth = {}
    for o in ("parent", "hdB0" if m == "hdA0" else "hdA0"):
        Co = torch.load(f"{caps_root}/cap_{o}.pt", mmap=True, weights_only=False); io = {k: i for i, k in enumerate(Co["keys"])}
        r_oth[o] = min(tokmed(capd[L], Co["hdr"][io[key0]][:, L]) for L in (40, 63))
    G["G1_adapter_active"] = dict(model=m, key=key0, rel_own_max=r_own, rel_other_min_L40_63=r_oth, tol_own=K.G1_OWN_NODE,
                                  pass_=bool(r_own <= K.G1_OWN_NODE and all(v >= max(tol["g1_ratio"] * r_own, 0.01) for v in r_oth.values())))
    ok &= G["G1_adapter_active"]["pass_"]
    units = []
    for d, sid in (("induce", sids[0]), ("remove", sids[1 % len(sids)])):
        ops, meta = unit_ops("gate", m, d, sid, 0, ctx, cap, dm, scales[d] if scales else None)
        units.append((ops, ctx[(K.DIRS[d][1], sid)]["ids"], ctx[(K.DIRS[d][1], sid)]["apos"], meta))
    rows, inp, am, P = build_batch(units, [])
    for o in rows:
        o["log"] = True
    ind = []
    for r in range(len(rows)):
        row = inp[r].tolist(); hp = list(range(P - 7, P)); assert row[P - 7:] == HEADER
        ap = K.asst_positions(row, K.last_user_start(row)); ind.append(dict(hdr=hp, asst=ap))
        if rows[r]["kind"] != "none":
            want = hp if rows[r]["site"] == "hdr" else ap
            assert rows[r]["pos"] == want, f"positions of {rows[r]['arm']} differ from the independently derived ones"
    ck = Cap(blocks, (15, 16, 40, 63)); ck.pos_rows = [ind[r]["hdr"] + ind[r]["asst"] for r in range(len(rows))]; ck.min_len = P
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; ck.on = True
    with torch.no_grad():
        model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
    hk.mode = None; ck.on = False; ck.remove()
    W = K.hook_checks(hk.log, ops_meta(rows), tol)
    cg = K.cum_gate(K.per_unit_ratios(hk.log))
    ib = dict(sub_excess=-1e9, A_excess=-1e9, skF_maxabs=0.0, L15_rel_max=0.0, untouched_rel_max=0.0, n_sub=0, n_A=0, n_skF=0, worst=None)
    by_unit = {}
    for r, o in enumerate(rows):
        by_unit.setdefault(o["grp"], {})[o["arm"]] = r
    for r, o in enumerate(rows):
        if o["kind"] == "none":
            continue
        g = by_unit[o["grp"]]; rn = g["none"]; nh7 = len(ind[r]["hdr"]); na = len(ind[r]["asst"])
        sel = list(range(nh7)) if o["site"] == "hdr" else list(range(nh7, nh7 + na))
        f = dm["script"][o["sid"]]["fold"]; U = dm["U"][f]; Aset = dm["A"][f]
        X15 = ck.cap[15][r]; Xn15 = ck.cap[15][rn]
        ib["L15_rel_max"] = max(ib["L15_rel_max"], float(((X15 - Xn15).norm(dim=-1) / Xn15.norm(dim=-1)).max()))
        for L in (16, 40, 63):
            X = ck.cap[L][r]; Xn = ck.cap[L][rn]
            if o["kind"] == "sub":
                u = U[K.FAMILY[o["arm"]]][L].float(); u = u / u.norm()
                Dh = C["hdr"][idx[f"{o['donor']}|{o['sid']}"]][:, L].float() @ u
                Da = C["asst_mean"][idx[f"{o['donor']}|{o['sid']}"]][L].float() @ u
                tg = torch.cat([Dh, Da.repeat(na)])[sel]
                got = X[sel] @ u; gap = (tg - Xn[sel] @ u).abs()
                exc = float(((got - tg).abs() - (tol["coord_rel"] * gap.clamp_min(1.0) + tol["coord_abs"])).max()); ib["n_sub"] += 1
                if exc > ib["sub_excess"]:
                    ib["sub_excess"] = exc; ib["worst"] = dict(arm=o["arm"], L=L, err=float((got - tg).abs().max()))
            elif o["kind"] == "A":
                b = K.base_arm(o["arm"]); rv = Aset[b][L].float(); rv = rv / rv.norm(); ra = g[K.ARM_OF_A[b]]
                kL = K.kvec(scales[o["direction"]][b])[L] if scales else 1.0
                want = o["s"] * kL * (ck.cap[L][ra][sel] - Xn[sel]).norm(dim=-1); got = (X[sel] - Xn[sel]) @ rv
                exc = float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max()); ib["n_A"] += 1
                ib["A_excess"] = max(ib["A_excess"], exc)
            else:
                Dref = C["hdr"][idx[f"self-hostile|{dm['sk_map'][o['sid']]}"]][:, L].float()
                ib["skF_maxabs"] = max(ib["skF_maxabs"], float((X[:nh7] - Dref).abs().max())); ib["n_skF"] += 1
            if L == 16:
                un = [j for j in range(nh7 + na) if j not in set(sel)]
                if un:
                    ib["untouched_rel_max"] = max(ib["untouched_rel_max"], float(((X[un] - Xn[un]).norm(dim=-1) / Xn[un].norm(dim=-1)).max()))
    ib["pass_"] = bool(ib["sub_excess"] <= 0 and ib["A_excess"] <= 0 and ib["skF_maxabs"] == 0.0 and ib["L15_rel_max"] <= 1e-3
                       and ib["untouched_rel_max"] <= 1e-3 and ib["n_sub"] and ib["n_A"] and ib["n_skF"])
    G["G3_known_answers"] = dict(logs={k: v for k, v in W.items()}, independent=ib, cumulative_2units_report_only=cg,
                                 pass_=bool(W["pass"] and ib["pass_"]))
    ok &= G["G3_known_answers"]["pass_"]
    G["pass"] = bool(ok)
    os.makedirs(out_dir, exist_ok=True); json.dump(G, open(f"{out_dir}/gates_{m}.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(G, default=float)[:4000], flush=True)
    return G


# ------------------------------------------------------------------------------------------------- memory probe (smoke)
TOKSUF = {}


def mem_probe(model, hk, m, ctx, cap, dm, scales, spec, out_dir):
    """spec 'free|induce:4,5;free|remove:4;fbtw|induce:6' -> per item, one batch of that many units from the LONGEST recipient
    contexts of that direction, generated with min_new_tokens = max_new (every row runs to the cap: the KV-cache worst case).
    Records peak memory_reserved / allocated; outputs are discarded."""
    res = []
    for part in spec.split(";"):
        rd, ns = part.split(":"); ro, d = rd.split("|")
        rec = K.DIRS[d][1]
        order = sorted((sid for (cond, sid) in ctx if cond == rec), key=lambda s: -len(ctx[(rec, s)]["ids"]))
        for n in [int(x) for x in ns.split(",")]:
            bridge = K.BRIDGES.get(ro); suffix = TOKSUF[bridge] if bridge else []
            max_new = K.FORCED_TOKENS if bridge else K.FREE_TOKENS
            units = []
            for sid in order[:n]:
                ops, meta = unit_ops(ro, m, d, sid, 0, ctx, cap, dm, scales[d])
                for o in ops:
                    o["log"] = False
                units.append((ops, ctx[(rec, sid)]["ids"], ctx[(rec, sid)]["apos"], meta))
            gc.collect(); torch.cuda.empty_cache()
            try:
                _, out, _, tim = generate_batch(model, hk, units, max_new, 1, suffix, min_new=max_new)
                res.append(dict(readout=ro, direction=d, units=n, rows=tim["rows"], P=tim["P"], steps=tim["steps"], wall_s=tim["wall_s"],
                                s_per_step=tim["s_per_step"], peak_reserved_gib=tim["peak_reserved_gib"], peak_alloc_gib=tim["peak_alloc_gib"],
                                all_at_max=bool(all(x[1] == max_new for x in out)), oom=False))
            except torch.cuda.OutOfMemoryError:
                hk.mode = None; res.append(dict(readout=ro, direction=d, units=n, oom=True))
                gc.collect(); torch.cuda.empty_cache()
            print("[mem_probe]", json.dumps(res[-1]), flush=True)
            json.dump(dict(model=m, total_gib=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 2), probes=res),
                      open(f"{out_dir}/mem_probe_{m}.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------- generation loop (resume by key)
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


def run_gen(model, hk, tok, m, readout, d, ctx, cap, dm, scales, sids, rd, samples, max_new, batch_units):
    bridge = K.BRIDGES.get(readout); suffix = TOKSUF[bridge] if bridge else []
    fn, lfn = f"{rd}/{readout}_{m}_{d}.jsonl", f"{rd}/log_{readout}_{m}_{d}.jsonl"
    repair_tail(fn); repair_tail(lfn)
    have = {r["key"] for r in K.jl(fn)}
    _, rec, _ = K.DIRS[d]
    todo = []
    for sid in sids:
        for k in range(samples):
            ops, meta = unit_ops(readout, m, d, sid, k, ctx, cap, dm, scales[d])
            if all(o["key"] in have for o in ops):
                continue
            todo.append((ops, ctx[(rec, sid)]["ids"], ctx[(rec, sid)]["apos"], meta))
    todo.sort(key=lambda u: (len(u[1]), u[0][0]["grp"]))
    nb = -(-len(todo) // batch_units)
    print(m, readout, d, "units todo", len(todo), "rows", sum(len(u[0]) for u in todo), "batches", nb, flush=True)
    for bi, b0 in enumerate(range(0, len(todo), batch_units)):
        for batch, rows, out, logs, tim in run_batch(model, hk, todo[b0:b0 + batch_units], max_new, m, suffix, readout):
            res = {op["key"]: o for op, o in zip(rows, out)}
            assert len(res) == len(rows), "duplicate keys inside one batch"
            lines = []
            for ops, ids, apos0, meta in batch:
                for op in ops:
                    if op["key"] in have:
                        continue
                    gen, n, fin = res[op["key"]]
                    txt = (bridge or "") + tok.decode(gen, skip_special_tokens=True)
                    have.add(op["key"])
                    lines.append(json.dumps(dict(key=op["key"], exp=K.EXP, part=K.PART, readout=readout, model=m, direction=d, recipient=op["recipient"],
                                                 donor=op["donor"], sid=op["sid"], arm=op["arm"], sample=op["sample"], text=txt, n_tok=n,
                                                 finish=fin, max_new=max_new, gen_head=gen[:16], scale=op.get("kk"), sk_donor=op.get("sk_donor"),
                                                 **meta)) + "\n")
            with open(lfn, "a") as f:   # logs before rows: a row on disk always has its unit's logs
                f.write("".join(json.dumps(dict(readout=readout, **e)) + "\n" for e in logs))
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{rd}/timing_{m}_{d}.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, readout=readout, direction=d, units_in=[u[0][0]["grp"] for u in batch], max_new=max_new,
                                        t=time.strftime("%FT%T"), **tim)) + "\n")
            caps_hit = sum(1 for o in out if o[2] == "length")
            print(f"[gen] {m} {readout} {d} batch {bi + 1}/{nb} {json.dumps(tim)} cap_hits {caps_hit}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)


def run(a, model, tok):
    readouts = [x for x in (a.readout or "").split(",") if x]; dirs_run = [x for x in a.directions.split(",") if x]
    assert all(r in K.READOUTS for r in readouts) and all(d in K.DIRS for d in dirs_run)
    for b in K.BRIDGES.values():
        TOKSUF[b] = tok(b, add_special_tokens=False)["input_ids"]
    m = a.model
    ctx, cap, dm = load_inputs(m, a.dirs_root, a.caps_root)
    all_sids = sorted({sid for (_, sid) in ctx}); assert len(all_sids) == 61
    sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    print("model", m, "readouts", readouts, "directions", dirs_run, "sids", len(sids), flush=True)
    sys.path.insert(0, LIB)
    import acts
    blocks = acts.blocks(model); assert len(blocks) == 64
    hk = Hooks38(blocks)
    tol = K.tolerances(a.calib)
    write_manifest(a.run_dir, a.job, sys.argv)
    with use(model, m):
        if a.cal:
            res = run_cal(model, hk, m, ctx, cap, dm, all_sids, a.cal, a.cal_units)
            if not res["pass"]:
                print("CAL_VERIFY_FAILED", flush=True); sys.exit(4)
        scales = load_scales(a.scales, m)
        if a.gates:
            gs = a.gate_sids.split(",") if a.gate_sids else sids[:2]
            G = gates(model, hk, blocks, m, ctx, cap, dm, scales, gs, a.gates_out or a.run_dir, tol, a.caps_root)
            if not G["pass"]:
                print("GATES_FAILED", flush=True); sys.exit(3)
        if a.mem_probe:
            mem_probe(model, hk, m, ctx, cap, dm, scales, a.mem_probe, a.gates_out or a.run_dir)
        for ro in readouts:
            rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
            for d in dirs_run:
                ns = a.samples if a.samples else K.n_samples(ro, d)
                run_gen(model, hk, tok, m, ro, d, ctx, cap, dm, scales, sids, rd, ns, K.FORCED_TOKENS if ro in K.BRIDGES else a.max_new,
                        a.forced_batch_units if ro in K.BRIDGES else a.batch_units)
            print(f"READOUT_DONE {ro} {time.strftime('%H:%M:%S')}", flush=True)
    print("GEN38P1_EXIT", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=K.MODELS); ap.add_argument("--readout", default="")
    ap.add_argument("--directions", default="induce,remove"); ap.add_argument("--sids", default=None)
    ap.add_argument("--max_new", type=int, default=K.FREE_TOKENS); ap.add_argument("--batch_units", type=int, default=4)
    ap.add_argument("--forced_batch_units", type=int, default=6); ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--gates", action="store_true"); ap.add_argument("--gate_sids", default=None)
    ap.add_argument("--run_dir", default=RUN); ap.add_argument("--gates_out", default=None); ap.add_argument("--calib", default=None)
    ap.add_argument("--dirs_root", default=f"{RUN}/dirs"); ap.add_argument("--caps_root", default=CAPS); ap.add_argument("--mem_probe", default=None)
    ap.add_argument("--scales", default=None); ap.add_argument("--cal", default=None); ap.add_argument("--cal_units", type=int, default=1)
    ap.add_argument("--job", default="gen")
    a = ap.parse_args()
    if (a.readout or a.gates or a.mem_probe) and not a.scales:
        raise SystemExit("--scales (the frozen scales file) is required for gates, the memory probe and generation")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, LORA[a.model], adapter_name=a.model); model.eval()
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    run(a, model, tok)


if __name__ == "__main__":
    main()
