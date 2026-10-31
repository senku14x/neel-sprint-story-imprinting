"""sw039 Part 2 GPU stage (prep-D agent, E2, 31 Oct 2026): the asT dose sweep on sw038's v2 G3 contexts. Adapted from sw038 Part 1
gen38p1.py (engine, left padding, sampling, OOM split by whole units, resume by key, torn-tail repair, inline gates, memory probe,
prefill-only two-segment clamp-scale calibration). Engine: HF transformers + unmerged PEFT, ONE organism per process, bf16, forward
hooks (hooks39p2 = sw038's hooks38p1 verbatim) on model.model.layers[L] outputs (pre-final-norm); edits at L16-63, prefill only.
Inputs = sw038 Part 1's files on this node, not refits: contexts /root/runs/sw038/p1/inputs/contexts38p1.jsonl, captures
/root/caps/sw038p1/cap_<m>.pt, directions /root/runs/sw038/p1/dirs/dirs38p1_<m>.pt (LODO fold of the script's domain; family asst =
v2 asT; nulls asT_A0 / asT_A1 and their signs).
Unit = (model, direction, script, sample) = 16 rows (common39p2.ARMS):
  none;
  asT_a<alpha> (sub): the coordinate along u_asT at every recipient Assistant turn-1-2 content token set to
      c_rec + alpha (c*_don - c_rec) (computed as (1 - alpha) c_rec + alpha c*_don), c_rec = the recipient model's captured asst_mean on the RECIPIENT context . u, c*_don = the same
      on the DONOR context (alpha = 1 gives c*_don = sw038's asT target exactly; known answer ka_alpha1 + a live same-forward copy);
  asT_a<alpha>_A<j> (A): sw038's null asT_A<j> clamped to x_none . r + k_L s Delta_dose(L, p), Delta = the live offset of THAT dose's
      arm in the same forward, k_L from this model's frozen scales file (k1 at L16-40, k2 at L41-63).
Modes (one process may run several, in this order): --cal OUTDIR (calibration; writes cal_<m>.json + scales_proposal_<m>.json),
--gates (G1 adapter active + G3 known answers + alpha = 1 known answer vs sw038), --mem_probe SPEC, then generation of --order.
Readouts: free (<= 2,048 new tokens, T 0.7, top_p 1, top_k 0; primary) and fbtw ("By the way," after the header, unpatched, +48;
beside). Samples: free induce 2, free remove 1, forced 1 (--samples overrides; 1 in the smoke).
Outputs per readout dir <run_dir>/<readout>/: <readout>_<m>_<d>.jsonl (keys sw039|<part>|<readout>|<m>|<d>|<sid>|<arm>|s<k>),
log_<readout>_<m>_<d>.jsonl (s0 units, 14 layers), timing_<m>_<d>.jsonl; <run_dir>/code_manifest_<job>.json."""
import argparse, contextlib, gc, hashlib, importlib.util, json, os, socket, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p2 as K  # noqa: E402
from hooks39p2 import Hooks38, Cap, check_order  # noqa: E402
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"

NS = "/workspace/Neel Sprint"
SW38 = "/root/runs/sw038/p1"
SW38_SRC = f"{NS}/experiments/sprint_work/038_mechanism_core_v2/src/p1"
SW38_SCALES = f"{SW38_SRC}/scales38p1.json"
RUN = "/root/runs/sw039/p2"
CTX = f"{SW38}/inputs/contexts38p1.jsonl"
CAPS = "/root/caps/sw038p1"
DIRS_ROOT = f"{SW38}/dirs"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
EOS = (248046, 248044)
PAD = 248044
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
DEV = "cuda"
CAL_GRID = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)          # sw038's grid
CAL_GROUPS = ((0.5, 1.0, 1.5), (2.0, 3.0))                    # doses per calibration prefill (52 / 35 rows per script)
SINGLE_TOL = 0.05


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def cuda():
    return DEV == "cuda" and torch.cuda.is_available()


def use(model, m):
    model.set_adapter(m); return contextlib.nullcontext()


def write_manifest(run_dir, job, argv):
    h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    files = {}
    for root, _, fs in os.walk(HERE):
        for f in sorted(fs):
            if f.endswith((".py", ".sh", ".json")) and "__pycache__" not in root:
                p = os.path.join(root, f); files[os.path.relpath(p, HERE)] = h(p)
    inp = {}
    for p in [x for x in argv if x.startswith("/")] + [CTX, SW38_SCALES]:
        if os.path.isfile(p) and os.path.getsize(p) < 2 ** 31:
            inp[p] = h(p)
    os.makedirs(run_dir, exist_ok=True)
    json.dump(dict(job=job, host=socket.gethostname(), gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), start=time.strftime("%FT%TZ", time.gmtime()),
                   argv=argv, code_sha256=files, inputs_sha256=inp), open(f"{run_dir}/code_manifest_{job}.json", "w"), indent=1)


# ------------------------------------------------------------------------------------------------- inputs
def load_inputs(m, dirs_root=DIRS_ROOT, caps_root=CAPS, ctx_path=CTX):
    ctx = {(r["cond"], r["sid"]): r for r in K.jl(ctx_path)}
    assert len(ctx) == 122
    for r in ctx.values():
        assert r["ids"][-7:] == HEADER and r["apos"]
    C = torch.load(f"{caps_root}/cap_{m}.pt", weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
    dm = torch.load(f"{dirs_root}/dirs38p1_{m}.pt", weights_only=False)
    assert dm["model"] == m
    return ctx, (C, idx), dm


def load_scales(path):
    if not path:
        return None
    S = json.load(open(path))
    for d in ("induce", "remove"):
        assert set(S["scales"][d]) == set(K.A_ARMS), (d, sorted(S["scales"][d]))
    return S["scales"]


_DEVC = {}


def dev_dirs(dm, m, f):
    k = (m, f, DEV)
    if k not in _DEVC:
        un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(DEV)
        _DEVC[k] = dict(u=un(dm["U"][f][K.FAMILY]), A={nm: un(dm["A"][f][nm]) for nm in K.NULLS})
    return _DEVC[k]


def coords(C, idx, cond, sid, u):
    """the recipient model's captured asst_mean on context (cond, sid) . u per layer -> [64] fp32 (on DEV)."""
    return (C["asst_mean"][idx[f"{cond}|{sid}"]].to(DEV).float() * u).sum(-1)


def unit_ops(readout, m, d, sid, k, ctx, cap, dm, scales, part=K.PART, cal_rows=None):
    """rows of one unit (K.ARMS order, or the calibration rows); positions are set per batch (set_pos).
    scales: this direction's {A arm: {k1, k2}}. cal_rows: list of (row name '<A arm>~<tag>', A arm, kvec) replacing the production
    A rows; only the dose arms those rows match are included (with none)."""
    _, rec, don = K.DIRS[d]
    C, idx = cap; grp = K.unit_id(m, d, sid, k)
    f = dm["script"][sid]["fold"]; T = dev_dirs(dm, m, f); sg = dm["sign"][f"{d}|{sid}"]
    u = T["u"]; c_rec = coords(C, idx, rec, sid, u); c_don = coords(C, idx, don, sid, u)
    na = len(ctx[(rec, sid)]["apos"])
    if cal_rows is None:
        arms = list(K.ARMS)
    else:
        need = {K.ARM_OF_A[r[1]] for r in cal_rows}
        arms = ["none"] + [a for a in K.REAL if a in need] + [r[0] for r in cal_rows]
    calk = {r[0]: (r[1], r[2]) for r in (cal_rows or [])}
    ops = []
    for arm in arms:
        b = K.base_arm(arm)
        alpha = K.ALPHA_OF.get(K.ARM_OF_A.get(b, b))
        base = dict(arm=arm, sample=k, key=K.row_key(readout, m, d, sid, arm, k, part), grp=grp, site=K.SITE.get(b), model=m, direction=d,
                    recipient=rec, donor=don, sid=sid, log=(k == 0), alpha=alpha)
        if arm == "none":
            ops.append(dict(base, kind="none")); continue
        if arm in K.REAL:
            # (1 - alpha) c_rec + alpha c_don == c_rec + alpha (c_don - c_rec), written so that alpha = 1 gives c_don BIT-EXACTLY
            # (= the sw038 asT target; the live same-forward copy needs identical rows: 1-ulp target differences amplify in bf16)
            tgt = ((1.0 - alpha) * c_rec + alpha * c_don)[:, None].expand(64, na).contiguous()  # [64, na]
            ops.append(dict(base, kind="sub", U=u, tgt=tgt, real=True))
        else:
            nl = K.NULL_OF_A[b]
            if cal_rows is None:
                kv = K.kvec(scales[b]); kk = scales[b]
            else:
                kv = calk[arm][1]; kk = None
            ops.append(dict(base, kind="A", U=T["A"][nl], s=float(sg[nl]), k=kv, kk=kk, null=nl, match=f"{grp}:{K.ARM_OF_A[b]}"))
    check_order(ops)
    meta = dict(domain=dm["script"][sid]["domain"], n_asst=na, fold=f)
    return ops, meta


def set_pos(ops, P, n_ids, ns, apos0):
    """left padding: row = [PAD]*(P - n_ids - ns) + ids + suffix. Header = the 7 tokens before the suffix; Assistant = apos0 shifted."""
    off = P - n_ids - ns
    hpos = [off + n_ids - 7 + i for i in range(7)]; apos = [off + p for p in apos0]
    for op in ops:
        op["hpos"] = hpos
        if op["kind"] == "none":
            continue
        op["nh"] = 0
        op["pos"] = apos


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


def run_batch(model, hk, batch, max_new, m, suffix, readout, part):
    """sw012 F3: on CUDA OOM split the batch into halves (whole units, so every A stays in its dose arm's forward)."""
    oom = False
    try:
        res = generate_batch(model, hk, batch, max_new, seed_of(K.EXP, part, readout, m, batch[0][0][0]["grp"], max_new), suffix)
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
    return run_batch(model, hk, batch[:h], max_new, m, suffix, readout, part) + run_batch(model, hk, batch[h:], max_new, m, suffix, readout, part)


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
    for (c0, r0), (c1, r1) in zip(curve, curve[1:]):
        if c0 <= k <= c1:
            return r0 + (k - c0) * (r1 - r0) / (c1 - c0)
    (c0, r0), (c1, r1) = (curve[0], curve[1]) if k < curve[0][0] else (curve[-2], curve[-1])
    return r0 + (k - c0) * (r1 - r0) / (c1 - c0)


def cal_pass(model, hk, m, d, ctx, cap, dm, sids, rows_spec):
    """prefill every script with the calibration rows, one forward per dose group (CAL_GROUPS; each forward has its own none row and
    the dose arms its rows match); -> (logs, per_unit_ratios)."""
    logs = []
    _, rec, _ = K.DIRS[d]
    groups = []
    for grp in CAL_GROUPS:
        arms = {K.DOSE_ARM[a] for a in grp}
        sub = [r for r in rows_spec if K.ARM_OF_A[r[1]] in arms]
        if sub:
            groups.append(sub)
    for sid in sids:
        for sub in groups:
            ops, meta = unit_ops("cal", m, d, sid, 0, ctx, cap, dm, None, part="p2cal", cal_rows=sub)
            _, lg = prefill(model, hk, [(ops, ctx[(rec, sid)]["ids"], ctx[(rec, sid)]["apos"], meta)])
            logs += lg
    return logs, K.per_unit_ratios(logs)


def verify_pass(model, hk, m, d, ctx, cap, dm, sids, scales_d, upf):
    logs = []
    _, rec, _ = K.DIRS[d]
    for b0 in range(0, len(sids), upf):
        units = []
        for sid in sids[b0:b0 + upf]:
            ops, meta = unit_ops("verify", m, d, sid, 0, ctx, cap, dm, scales_d, part="p2cal")
            units.append((ops, ctx[(rec, sid)]["ids"], ctx[(rec, sid)]["apos"], meta))
        _, lg = prefill(model, hk, units)
        logs += lg
    return logs, K.per_unit_ratios(logs)


def run_cal(model, hk, m, ctx, cap, dm, sids, out_dir, upf_verify):
    """sw038 D14's rule per (direction, dose, A arm). Round 1: a single k on CAL_GRID at every layer; per band k_b = the interpolated k
    at which the band's median (over the 61 scripts) is 1.0. If k = mean of the two band k's puts both bands' interpolated medians
    within 1 +- SINGLE_TOL: k1 = k2 = that k. Else round 2: k1 = k_{L28-40} fixed at L16-40, grid over k2 at L41-63, k2 = the
    interpolated k at which L44-63's median is 1.0 (L28-40 causally unaffected by k2; spread logged). Round 3 (verify): the
    production rows (16 per unit) at the proposed scales on every script; gate = every A arm's median in [0.9, 1.1] at both bands."""
    os.makedirs(out_dir, exist_ok=True); t0 = time.time()
    res = dict(model=m, grid=list(CAL_GRID), groups=[list(g) for g in CAL_GROUPS], n_scripts=len(sids), single_tol=SINGLE_TOL, directions={})
    prop = {}
    for d in ("induce", "remove"):
        R = dict(round1={}, choice={}, round2={}, verify={})
        spec = [(f"{a}~k{c:g}", a, [c] * 64) for a in K.A_ARMS for c in CAL_GRID]
        logs, per = cal_pass(model, hk, m, d, ctx, cap, dm, sids, spec)
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
                                  single_k=round(ks, 4), single_pred={b: round(v, 4) for b, v in rs.items()}, single=bool(single))
            if single:
                prop.setdefault(d, {})[a] = dict(k1=round(ks, 4), k2=round(ks, 4), two_segment=False)
            else:
                need2.append((a, kb["L28-40"][0]))
        print(f"[cal] {m} {d} round 1 {time.time() - t0:.0f}s", json.dumps({a: R["choice"][a] for a in K.A_ARMS})[:3000], flush=True)
        if need2:
            spec = [(f"{a}~k1{k1:.4f}~k2{c:g}", a, [k1 if L < K.SEG_SPLIT else c for L in range(64)]) for a, k1 in need2 for c in CAL_GRID]
            logs, per = cal_pass(model, hk, m, d, ctx, cap, dm, sids, spec)
            open(f"{out_dir}/log_cal_{m}_r2_{d}.jsonl", "w").write("".join(json.dumps(e) + "\n" for e in logs))
            for a, k1 in need2:
                cv = {b: [(c, K.median(list(per[f"{a}~k1{k1:.4f}~k2{c:g}"][b].values()))) for c in CAL_GRID] for b in K.GATE_BANDS}
                k2, ex = interp(cv["L44-63"], 1.0)
                R["round2"][a] = dict(k1=round(k1, 4), curve={b: [[c, round(r, 4)] for c, r in v] for b, v in cv.items()}, k2=round(k2, 4),
                                      extrapolated=ex, L28_40_spread_over_k2=round(max(r for _, r in cv["L28-40"]) - min(r for _, r in cv["L28-40"]), 5))
                prop.setdefault(d, {})[a] = dict(k1=round(k1, 4), k2=round(k2, 4), two_segment=True)
            print(f"[cal] {m} {d} round 2 {time.time() - t0:.0f}s", json.dumps(R["round2"])[:3000], flush=True)
        logs, per = verify_pass(model, hk, m, d, ctx, cap, dm, sids, prop[d], upf_verify)
        open(f"{out_dir}/log_cal_{m}_verify_{d}.jsonl", "w").write("".join(json.dumps(e) + "\n" for e in logs))
        g = K.cum_gate(per)
        R["verify"] = dict(gate=g, per_script={a: {b: {k.split("|")[2]: round(v, 4) for k, v in per[a][b].items()} for b in K.GATE_BANDS} for a in K.A_ARMS})
        print(f"[cal-verify] {m} {d} pass {g['pass_']}", json.dumps({a: v["median_ratio"] for a, v in g["arms"].items()}), "vs_a1", json.dumps(g["vs_a1"]), flush=True)
        res["directions"][d] = R
    res["proposal"] = prop
    res["pass"] = bool(all(res["directions"][d]["verify"]["gate"]["pass_"] for d in ("induce", "remove")))
    res["wall_s"] = round(time.time() - t0)
    json.dump(res, open(f"{out_dir}/cal_{m}.json", "w"), indent=1)
    json.dump(dict(model=m, scales=prop, created=time.strftime("%FT%TZ", time.gmtime()), source=f"{out_dir}/cal_{m}.json", verify_pass=res["pass"]),
              open(f"{out_dir}/scales_proposal_{m}.json", "w"), indent=1)
    print("CAL_DONE", m, "verify pass", res["pass"], f"{time.time() - t0:.0f}s", flush=True)
    return res


# ------------------------------------------------------------------------------------------------- known answer: alpha = 1 = sw038 asT
_G38 = None


def g38():
    """sw038 Part 1's own generator module (read-only import of the file on this node; never edited)."""
    global _G38
    if _G38 is None:
        sp = importlib.util.spec_from_file_location("gen38p1", f"{SW38_SRC}/gen38p1.py")
        _G38 = importlib.util.module_from_spec(sp); sp.loader.exec_module(_G38); _G38.DEV = DEV
    return _G38


def ka_alpha1(m, ctx, cap, dm, sids, dirs=("induce", "remove")):
    """every (direction, script): this generator's asT_a1 target == sw038 gen38p1.unit_ops' asT target (same rows: same files, same
    positions after padding), and the A rows asT_a1_A<j> use sw038's null asT_A<j> with sw038's sign. Pass = max relative target
    difference <= 1e-5 (expected exactly 0 since (1 - 1) c_rec + 1 c_don == c_don), nulls and signs identical, positions identical."""
    G = g38(); S38 = json.load(open(SW38_SCALES))["scales"][m]
    worst_abs = worst_rel = 0.0; n = 0; same_null = same_sign = same_pos = True
    for d in dirs:
        _, rec, _ = K.DIRS[d]
        for sid in sids:
            o38, _ = G.unit_ops("ka", m, d, sid, 0, ctx, cap, dm, S38[d])
            o39, _ = unit_ops("ka", m, d, sid, 0, ctx, cap, dm, None, cal_rows=[(f"{K.A_OF[K.DOSE_ARM[1.0]][j]}~ka", K.A_OF[K.DOSE_ARM[1.0]][j], [1.0] * 64) for j in range(K.N_A)])
            a38 = {o["arm"]: o for o in o38}; a39 = {K.base_arm(o["arm"]): o for o in o39}
            t38 = a38["asT"]["tgt"].float(); t39 = a39[K.DOSE_ARM[1.0]]["tgt"].float()
            assert t38.shape == t39.shape, (t38.shape, t39.shape)
            da = float((t38 - t39).abs().max()); worst_abs = max(worst_abs, da)
            worst_rel = max(worst_rel, float(((t38 - t39).abs() / t38.abs().clamp_min(1.0)).max())); n += 1
            for j in range(K.N_A):
                x38 = a38[f"asT_A{j}"]; x39 = a39[K.A_OF[K.DOSE_ARM[1.0]][j]]
                same_null &= bool(torch.equal(x38["U"].float(), x39["U"].float()))
                same_sign &= (float(x38["s"]) == float(x39["s"]))
            ids = ctx[(rec, sid)]["ids"]; ap = ctx[(rec, sid)]["apos"]; P = len(ids) + 5
            G.set_pos(o38, P, len(ids), 0, ap); set_pos(o39, P, len(ids), 0, ap)
            same_pos &= (a38["asT"]["pos"] == a39[K.DOSE_ARM[1.0]]["pos"])
    G._DFULL.clear()
    r = dict(n_unit_checks=n, max_abs_tgt_diff=worst_abs, max_rel_tgt_diff=worst_rel, nulls_identical=bool(same_null),
             signs_identical=bool(same_sign), positions_identical=bool(same_pos))
    r["pass_"] = bool(n > 0 and worst_rel <= 1e-5 and same_null and same_sign and same_pos)
    return r


# ------------------------------------------------------------------------------------------------- GPU gates
def tokmed(a, b):
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def ops_meta(rows):
    return {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), k=o.get("k"), match=o.get("match")) for o in rows}


def gates(model, hk, blocks, m, ctx, cap, dm, scales, sids, out_dir, tol, caps_root, all_sids):
    """G1 adapter active (sw038's rule against sw038's same-node captures): live header states of one context vs m's own capture
    (median over tokens 1-6 of the relative distance <= G1_OWN_NODE at L16/40/63), the other hd model's and the parent's >= g1_ratio x
    further (and >= 0.01).
    KA1 (alpha = 1 = sw038's asT): ka_alpha1 on all 61 scripts x both directions (CPU-side arithmetic), plus a LIVE copy: sw038's own
    asT op (built by gen38p1.unit_ops) added to the induce gate unit as row 'ka38_asT'; its block outputs must equal asT_a1's at
    L16/40/63 at every position (relative <= 1e-3; expected 0).
    G3 known answers, one left-padded forward of 2 units (induce sids[0] s0, remove sids[1] s0), every arm logged:
      (a) hook_checks on the live logs; (b) INDEPENDENT read-out (Cap after the edit hooks) at L15/16/40/63 with positions re-derived
      from the padded ids and targets / signs recomputed from the captures and dirs38p1 (not from the ops): sub coordinate =
      c_rec + alpha (c_don - c_rec); A (x_A - x_none).r = k_L s ||x_dose - x_none|| with s = sign((asst_mean_don - asst_mean_rec).r_16);
      L15 rows = none's; L16 header = none's (asT edits only the Assistant tokens); (c) cumulative ratios of the 2 units (report only)."""
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
    G["KA_alpha1_vs_sw038"] = ka_alpha1(m, ctx, cap, dm, all_sids)
    ok &= G["KA_alpha1_vs_sw038"]["pass_"]
    units = []
    for d, sid in (("induce", sids[0]), ("remove", sids[1 % len(sids)])):
        ops, meta = unit_ops("gate", m, d, sid, 0, ctx, cap, dm, scales[d], part="p2gate")
        if d == "induce":
            o38 = [o for o in g38().unit_ops("gate", m, d, sid, 0, ctx, cap, dm, json.load(open(SW38_SCALES))["scales"][m][d])[0] if o["arm"] == "asT"][0]
            ops.append(dict(o38, arm="ka38_asT", key=o38["key"] + "|ka38", grp=ops[0]["grp"], real=False, log=False, alpha=1.0, site="asst"))
        units.append((ops, ctx[(K.DIRS[d][1], sid)]["ids"], ctx[(K.DIRS[d][1], sid)]["apos"], meta))
    rows, inp, am, P = build_batch(units, [])
    for o in rows:
        o["log"] = o["arm"] != "ka38_asT"
    ind = []
    for r in range(len(rows)):
        row = inp[r].tolist(); hp = list(range(P - 7, P)); assert row[P - 7:] == HEADER
        ap = K.asst_positions(row, K.last_user_start(row)); ind.append(dict(hdr=hp, asst=ap))
        if rows[r]["kind"] != "none":
            assert rows[r]["pos"] == ap, f"positions of {rows[r]['arm']} differ from the independently derived ones"
    ck = Cap(blocks, (15, 16, 40, 63)); ck.pos_rows = [ind[r]["hdr"] + ind[r]["asst"] for r in range(len(rows))]; ck.min_len = P
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; ck.on = True
    with torch.no_grad():
        model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
    hk.mode = None; ck.on = False; ck.remove()
    om = ops_meta([o for o in rows if o["arm"] != "ka38_asT"])
    W = K.hook_checks(hk.log, om, tol)
    cg = K.cum_gate(K.per_unit_ratios(hk.log))
    ib = dict(sub_excess=-1e9, A_excess=-1e9, L15_rel_max=0.0, untouched_hdr_rel_max_L16=0.0, n_sub=0, n_A=0, sign_mismatch=0, worst=None,
              ka38_live_rel_max=None)
    by_unit = {}
    for r, o in enumerate(rows):
        by_unit.setdefault(o["grp"], {})[o["arm"]] = r
    for r, o in enumerate(rows):
        if o["kind"] == "none" or o["arm"] == "ka38_asT":
            continue
        g = by_unit[o["grp"]]; rn = g["none"]; nh7 = len(ind[r]["hdr"]); na = len(ind[r]["asst"])
        sel = list(range(nh7, nh7 + na))
        f = dm["script"][o["sid"]]["fold"]; U = dm["U"][f]; Aset = dm["A"][f]
        X15 = ck.cap[15][r]; Xn15 = ck.cap[15][rn]
        ib["L15_rel_max"] = max(ib["L15_rel_max"], float(((X15 - Xn15).norm(dim=-1) / Xn15.norm(dim=-1)).max()))
        am_rec = C["asst_mean"][idx[f"{o['recipient']}|{o['sid']}"]].float(); am_don = C["asst_mean"][idx[f"{o['donor']}|{o['sid']}"]].float()
        for L in (16, 40, 63):
            X = ck.cap[L][r]; Xn = ck.cap[L][rn]
            if o["kind"] == "sub":
                u = U[K.FAMILY][L].float(); u = u / u.norm()
                cr = float(am_rec[L] @ u); cd = float(am_don[L] @ u); a_ = K.ALPHA_OF[o["arm"]]
                tg = torch.full((na,), cr + a_ * (cd - cr))
                got = X[sel] @ u; gap = (tg - Xn[sel] @ u).abs()
                exc = float(((got - tg).abs() - (tol["coord_rel"] * gap.clamp_min(1.0) + tol["coord_abs"])).max()); ib["n_sub"] += 1
                if exc > ib["sub_excess"]:
                    ib["sub_excess"] = exc; ib["worst"] = dict(arm=o["arm"], L=L, err=float((got - tg).abs().max()))
            else:
                b = K.base_arm(o["arm"]); nl = K.NULL_OF_A[b]
                r16 = Aset[nl][16].float(); r16 = r16 / r16.norm()
                s_ind = 1.0 if float((am_don[16] - am_rec[16]) @ r16) >= 0 else -1.0
                ib["sign_mismatch"] += int(s_ind != float(o["s"]))
                rv = Aset[nl][L].float(); rv = rv / rv.norm(); ra = g[K.ARM_OF_A[b]]
                kL = K.kvec(scales[o["direction"]][b])[L]
                want = s_ind * kL * (ck.cap[L][ra][sel] - Xn[sel]).norm(dim=-1); got = (X[sel] - Xn[sel]) @ rv
                exc = float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max()); ib["n_A"] += 1
                ib["A_excess"] = max(ib["A_excess"], exc)
            if L == 16:
                ib["untouched_hdr_rel_max_L16"] = max(ib["untouched_hdr_rel_max_L16"],
                                                      float(((X[:nh7] - Xn[:nh7]).norm(dim=-1) / Xn[:nh7].norm(dim=-1)).max()))
    g0 = by_unit[rows[0]["grp"]]; rk = g0["ka38_asT"]; ra1 = g0[K.DOSE_ARM[1.0]]
    ib["ka38_live_rel_max"] = max(float(((ck.cap[L][rk] - ck.cap[L][ra1]).norm(dim=-1) / ck.cap[L][ra1].norm(dim=-1)).max()) for L in (16, 40, 63))
    ib["pass_"] = bool(ib["sub_excess"] <= 0 and ib["A_excess"] <= 0 and ib["L15_rel_max"] <= 1e-3 and ib["untouched_hdr_rel_max_L16"] <= 1e-3
                       and ib["n_sub"] and ib["n_A"] and ib["sign_mismatch"] == 0 and ib["ka38_live_rel_max"] <= 1e-3)
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
    """spec 'free|induce:3;fbtw|induce:4' -> per item, one batch of that many units from the LONGEST recipient contexts of that
    direction, generated with min_new_tokens = max_new (every row runs to the cap: the KV-cache worst case). Outputs discarded."""
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
                ops, meta = unit_ops(ro, m, d, sid, 0, ctx, cap, dm, scales[d], part="p2probe")
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


def run_gen(model, hk, tok, m, readout, d, ctx, cap, dm, scales, sids, rd, samples, max_new, batch_units, part):
    bridge = K.BRIDGES.get(readout); suffix = TOKSUF[bridge] if bridge else []
    fn, lfn = f"{rd}/{readout}_{m}_{d}.jsonl", f"{rd}/log_{readout}_{m}_{d}.jsonl"
    repair_tail(fn); repair_tail(lfn)
    have = {r["key"] for r in K.jl(fn)}
    _, rec, _ = K.DIRS[d]
    todo = []
    for sid in sids:
        for k in range(samples):
            ops, meta = unit_ops(readout, m, d, sid, k, ctx, cap, dm, scales[d], part=part)
            if all(o["key"] in have for o in ops):
                continue
            todo.append((ops, ctx[(rec, sid)]["ids"], ctx[(rec, sid)]["apos"], meta))
    todo.sort(key=lambda u: (len(u[1]), u[0][0]["grp"]))
    nb = -(-len(todo) // batch_units)
    print(m, readout, d, "units todo", len(todo), "rows", sum(len(u[0]) for u in todo), "batches", nb, flush=True)
    for bi, b0 in enumerate(range(0, len(todo), batch_units)):
        for batch, rows, out, logs, tim in run_batch(model, hk, todo[b0:b0 + batch_units], max_new, m, suffix, readout, part):
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
                    lines.append(json.dumps(dict(key=op["key"], exp=K.EXP, part=part, readout=readout, model=m, direction=d, recipient=op["recipient"],
                                                 donor=op["donor"], sid=op["sid"], arm=op["arm"], alpha=op["alpha"], null=op.get("null"),
                                                 sample=op["sample"], text=txt, n_tok=n, finish=fin, max_new=max_new, gen_head=gen[:16],
                                                 scale=op.get("kk"), **meta)) + "\n")
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
    order = [tuple(x.split(":")) for x in (a.order or "").split(",") if x]
    assert all(ro in K.READOUTS and d in K.DIRS for ro, d in order), order
    for b in K.BRIDGES.values():
        TOKSUF[b] = tok(b, add_special_tokens=False)["input_ids"]
    m = a.model
    ctx, cap, dm = load_inputs(m)
    all_sids = sorted({sid for (_, sid) in ctx}); assert len(all_sids) == 61
    sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    print("model", m, "order", order, "sids", len(sids), "part", a.part, flush=True)
    sys.path.insert(0, LIB)
    import acts
    blocks = acts.blocks(model); assert len(blocks) == 64
    hk = Hooks38(blocks)
    tol = K.tolerances(a.calib, a.tol_base)
    write_manifest(a.run_dir, a.job, sys.argv)
    bu, fbu = a.batch_units, a.forced_batch_units
    if a.batch_json:
        B = json.load(open(a.batch_json)); bu, fbu = int(B["free_units"]), int(B["forced_units"])
        print("batch sizes from", a.batch_json, bu, fbu, flush=True)
    with use(model, m):
        if a.cal:
            res = run_cal(model, hk, m, ctx, cap, dm, all_sids, a.cal, a.verify_units)
            if not res["pass"]:
                print("CAL_VERIFY_FAILED", flush=True); sys.exit(4)
        scales = load_scales(a.scales)
        if a.gates:
            gs = a.gate_sids.split(",") if a.gate_sids else sids[:2]
            G = gates(model, hk, blocks, m, ctx, cap, dm, scales, gs, a.gates_out or a.run_dir, tol, CAPS, all_sids)
            if not G["pass"]:
                print("GATES_FAILED", flush=True); sys.exit(3)
        if a.mem_probe:
            mem_probe(model, hk, m, ctx, cap, dm, scales, a.mem_probe, a.gates_out or a.run_dir)
        for ro, d in order:
            rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
            ns = a.samples if a.samples else K.n_samples(ro, d)
            run_gen(model, hk, tok, m, ro, d, ctx, cap, dm, scales, sids, rd, ns, K.FORCED_TOKENS if ro in K.BRIDGES else a.max_new,
                    fbu if ro in K.BRIDGES else bu, a.part)
            print(f"GEN_DONE {ro} {d} {time.strftime('%H:%M:%S')}", flush=True)
    print("GEN39P2_EXIT", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=K.MODELS); ap.add_argument("--order", default="")
    ap.add_argument("--sids", default=None); ap.add_argument("--part", default=K.PART)
    ap.add_argument("--max_new", type=int, default=K.FREE_TOKENS); ap.add_argument("--batch_units", type=int, default=3)
    ap.add_argument("--forced_batch_units", type=int, default=4); ap.add_argument("--batch_json", default=None)
    ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--gates", action="store_true"); ap.add_argument("--gate_sids", default=None)
    ap.add_argument("--run_dir", default=RUN); ap.add_argument("--gates_out", default=None)
    ap.add_argument("--calib", default=None); ap.add_argument("--tol_base", default=f"{SW38}/calib.json")
    ap.add_argument("--mem_probe", default=None); ap.add_argument("--scales", default=None)
    ap.add_argument("--cal", default=None); ap.add_argument("--verify_units", type=int, default=3)
    ap.add_argument("--job", default="gen")
    a = ap.parse_args()
    if (a.order or a.gates or a.mem_probe) and not a.scales:
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
