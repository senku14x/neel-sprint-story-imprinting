"""sw021 GPU stages (executor-9 overnight, 30 Oct 2026). HF + unmerged PEFT (parent, hdA0, hdB0) in ONE process, forward hooks on
model.model.layers[L] outputs (pre-final-norm; sw006 / sw009 machinery). Stages (comma list, run in order):
  parity    parent E2a context vs the vLLM reference (sw009_captures/parity.json; gate 1.10x, as lib/setup_smoke_hf.py) and the
            adapter-active check (header-mean rel. difference parent vs hdA0 / hdB0 / between them at L40, gates from sw009's captures)
  capture   header states [7, 64, H] fp16 + header mean for every context, per model -> <out>/captures/<m>.pt
            (--cap_from sw009: v1 smoke uses sw009's Stage B captures for the fits and checks ours against them on 8 contexts)
  dirs      dirs21.fit per model (leave-one-domain-out, nulls, random split, all, sw009's v1 d_self) -> <out>/dirs_<m>.pt + cos table
  selftest  known-answer checks on GPU (none = capture; own-state swap ~ no-op; coordinate = donor's; orthogonal part unchanged at
            L16; matched control displacement = real arm's realised displacement)
  forced    "By the way," + 48 tokens, 15 arms x 2 samples per (model, direction, scenario) -> <out>/forced_<m>.jsonl, disp_forced_<m>.jsonl
  acts      teacher-forced re-run of the sample-0 forced readout for none / r1 / r1-shuf0 with the same patch, post-intervention
            states at the 14 master-s7 layers and 19 position labels -> acts dir
  select    STRICT labels on the forced rows -> the three free-reply controls per (model, direction) -> <out>/free_controls.json
  padcheck  left-padded vs unpadded parity gate for the free stage (first-step KL, patched header states, greedy agreement)
  free      free replies (<= 2,048 tokens), 5 arms x 2 samples, left-padded across scenarios -> <out>/free_<m>.jsonl
  CUDA_VISIBLE_DEVICES=0 /root/venvs/si/bin/python gpu21.py --ctx DIR --out DIR --stages ... [--sids a,b] [--models hdA0,hdB0]"""
import argparse, contextlib, glob, json, math, os, random, sys, time
from collections import defaultdict

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common21 import (ACT_ARMS, ACT_LAYERS, BASE, BTW, CONDS, CTRL_ARMS, DIRECTIONS, EOS, EOT, FORCED_ARMS, FORCED_TOKENS, FREE_TOKENS,  # noqa: E402
                      HEADER, LAYERS_SWAP, LOG_LAYERS, LORA_SRC, MODELS, N_FREE_RANDOM, N_SAMPLES, NULLS, SW9CAP, jl, key_of, seed_of, strict_role, wjl)
import dirs21  # noqa: E402

sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
from hooks018 import text_model  # noqa: E402

torch.backends.cuda.matmul.allow_tf32 = False
GATES = []


def gate(name, ok, **info):
    rec = dict(gate=name, ok=bool(ok), t=time.strftime("%H:%M:%S"), **info)
    GATES.append(rec); print("GATE", json.dumps(rec, default=float), flush=True)
    with open(f"{A.out}/gates.jsonl", "a") as f:
        f.write(json.dumps(rec, default=float) + "\n")
    if not ok:
        print(f"GATE_FAIL {name}", flush=True); sys.exit(3)


class Hooks21:
    """mode 'cap': store each layer's output [B, T, H]. mode 'patch': at prefill (seq >= min_len) and layers 16-63, apply each row's op at
    its header positions: rank-1 swap x <- x + ((D - x).u) u; a matched control uses its own direction un with the displacement
    rescaled per token to the realised displacement of the real arm `match` at the same layer (same forward, or a stored value when
    `persist` is on: activations re-runs, where the real arm and its control are separate forwards over the same prefix)."""

    def __init__(self, tm):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9; self.keep = None; self.cap = {}; self.persist = None
        self.h = [tm.layers[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode == "cap":
                self.cap[L] = t.detach(); return None
            if self.mode != "patch" or t.shape[1] < self.min_len:
                return None
            changed = False
            if L in LAYERS_SWAP:
                t = t.clone(); changed = True; realnorm = {}
                for r, op in enumerate(self.ops):
                    if op["kind"] == "none":
                        continue
                    pos = op["pos"]; x = t[r, pos].float(); Dl = op["D"][:, L].float(); u = op["U"][L].float()
                    d = ((Dl - x) @ u)[:, None] * u[None]
                    if op.get("Un") is not None:
                        un = op["Un"][L].float(); dn = ((Dl - x) @ un)[:, None] * un[None]
                        mk = op["match"]
                        if mk in realnorm:
                            rn = realnorm[mk]
                        else:
                            assert self.persist is not None and (L, mk) in self.persist, f"real arm {mk} must precede its control"
                            rn = self.persist[(L, mk)]
                        d = dn / dn.norm(dim=-1, keepdim=True).clamp_min(1e-6) * rn
                    elif op.get("real"):
                        realnorm.setdefault(op["grp"] + "|" + op["arm"], d.norm(dim=-1, keepdim=True))
                        if self.persist is not None:
                            self.persist[(L, op["grp"] + "|" + op["arm"])] = d.norm(dim=-1, keepdim=True)
                    new = (x + d).to(t.dtype); t[r, pos] = new
                    if op.get("log") and L in LOG_LAYERS:
                        nd = d.norm(dim=-1)
                        self.log.append(dict(grp=op["grp"], arm=op["arm"], L=L, row=r, disp=float(nd.mean()), rel=float((nd / x.norm(dim=-1)).mean()),
                                             tok=[round(float(v), 4) for v in nd], round_err=float(((new.float() - x) - d).norm(dim=-1).max())))
            if self.keep is not None and L in self.keep:
                self.cap[L] = t.detach()
            if changed:
                return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
            return None
        return f


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


# ------------------------------------------------------------------ contexts, captures, directions
def load_ctx():
    rows = jl(f"{A.ctx}/contexts.jsonl")
    C = {(r["cond"], r["sid"]): r for r in rows}
    sids = sorted(set(r["sid"] for r in rows if ("self-hostile", r["sid"]) in C and ("user-hostile", r["sid"]) in C))
    return rows, C, sids


class Caps:
    def __init__(self, m):
        if A.cap_from == "sw009":
            z = torch.load(f"{SW9CAP}/{m}.pt", mmap=True)
            self.idx = {k.replace("sw008|", "", 1): i for i, k in enumerate(z["keys"]) if k.startswith("sw008|")}
        else:
            z = torch.load(f"{A.out}/captures/{m}.pt", mmap=True)
            self.idx = {k: i for i, k in enumerate(z["keys"])}
        self.hdr, self.hm = z["hdr"], z["hdr_mean"]

    def mean(self, cond, sids):
        return self.hm[[self.idx[f"{cond}|{s}"] for s in sids]].float()

    def hdr_of(self, cond, sid):
        return self.hdr[self.idx[f"{cond}|{sid}"]]


def stage_parity(model, hk, tok, rows, C, sids):
    import glob as _g
    par = json.load(open("/workspace/runs_executor/sw009_captures/parity.json"))
    req = json.loads(open("/workspace/runs_executor/extract1028/requests/E2a_parent.jsonl").readline()); assert req["key"] == par["key"]
    E2 = torch.load(sorted(_g.glob("/workspace/runs_executor/extract1028/E2/a/parent/chunk_*.pt"))[0])
    j = E2["keys"].index(req["key"]); ids = req.get("ids") or req.get("prompt_token_ids")
    with use(model, "parent"):
        hk.mode = "cap"; hk.cap = {}; model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1); hk.mode = None
    hm = torch.stack([hk.cap[L][0, -7:].float().mean(0) for L in range(64)]).cpu(); ref = E2["span_mean"][j, 0].float()
    rel = (hm - ref).norm(dim=-1) / ref.norm(dim=-1)
    gate("parity_hf_vs_vllm", float(rel.max()) <= 1.10 * par["max_rel"] and float(rel.median()) <= 1.10 * par["median_rel"],
         max_rel=float(rel.max()), median_rel=float(rel.median()), ref=par)
    stage_adapter(model, hk, tok, rows, C, sids)


def stage_adapter(model, hk, tok, rows, C, sids):
    """adapter-active check only (review 08:50, CONVENTIONS 'no repeated parity checks': the HF-vs-vLLM parity forward is dropped
    from the full jobs; this inline check stays because a silent LoRA no-op has really happened, 27 Oct)."""
    r = C[("self-hostile", sids[0])]; hmm = {}
    for m in ("parent",) + MODELS:
        with use(model, m):
            hk.mode = "cap"; hk.cap = {}; model(input_ids=torch.tensor([r["ids"]], device="cuda"), logits_to_keep=1); hk.mode = None
        hmm[m] = torch.stack([hk.cap[L][0, -7:].float().mean(0) for L in range(64)]).cpu()
    rl = lambda a, b: float(((hmm[a][40] - hmm[b][40]).norm() / hmm[a][40].norm()))
    # thresholds = half the smallest value in sw009's captures (16 self-hostile contexts): parent-hdA0 0.71, parent-hdB0 0.65, hdA0-hdB0 0.25
    gate("adapter_active", rl("parent", "hdA0") > 0.35 and rl("parent", "hdB0") > 0.32 and rl("hdA0", "hdB0") > 0.12,
         rel_L40=dict(parent_hdA0=rl("parent", "hdA0"), parent_hdB0=rl("parent", "hdB0"), hdA0_hdB0=rl("hdA0", "hdB0")))


def stage_capture(model, hk, tok, rows, C, sids):
    os.makedirs(f"{A.out}/captures", exist_ok=True)
    R = rows
    if A.cap_from == "sw009":  # v1 smoke: capture 8 contexts with our code and compare with sw009's Stage B captures (same HF path)
        R = [C[(c, s)] for s in sids[:2] for c in CONDS]
    for m in A.models.split(","):
        fn = f"{A.out}/captures/{m}{'_check' if A.cap_from == 'sw009' else ''}.pt"
        if os.path.exists(fn):
            z = torch.load(fn, mmap=True)
            if z["keys"] == [r["key"] for r in R]:
                print("capture exists", fn, flush=True); continue
        out = dict(keys=[], hdr=[], hdr_mean=[], n_tok=[])
        with use(model, m):
            for r in R:
                hk.mode = "cap"; hk.cap = {}
                model(input_ids=torch.tensor([r["ids"]], device="cuda"), logits_to_keep=1); hk.mode = None
                st = torch.stack([hk.cap[L][0, r["hdr"]] for L in range(64)], 1)  # [7, 64, H] bf16
                out["hdr"].append(st.half().cpu()); out["hdr_mean"].append(st.float().mean(0).half().cpu())
                out["keys"].append(r["key"]); out["n_tok"].append(r["n_tok"])
        out["hdr"] = torch.stack(out["hdr"]); out["hdr_mean"] = torch.stack(out["hdr_mean"])
        gate(f"capture_finite_{m}", bool(torch.isfinite(out["hdr"].float()).all()), n=len(R))
        torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        print("captured", m, len(R), time.strftime("%H:%M:%S"), flush=True)
        if A.cap_from == "sw009":
            ref = Caps(m); rels = []
            for i, k in enumerate(out["keys"]):
                a = out["hdr_mean"][i].float(); b = ref.hm[ref.idx[k]].float()
                rels.append(float(((a - b).norm(dim=-1) / b.norm(dim=-1)).max()))
            gate(f"capture_equals_sw009_{m}", max(rels) <= 0.01, max_rel=max(rels), n=len(rels))


def stage_dirs(model, hk, tok, rows, C, sids):
    dom = {r["sid"]: r["domain"] for r in rows}; by = defaultdict(list)
    for s in sids:
        by[dom[s]].append(s)
    by = {k: sorted(v) for k, v in by.items()}
    cos = {}
    for m in A.models.split(","):
        cp = Caps(m); v1 = dirs21.load_sw009_dself(m)
        D = dirs21.fit(cp.mean, by, m, v1)
        torch.save(D, f"{A.out}/dirs_{m}.pt")
        cos[m] = dirs21.cos_table(D, v1)
        print("dirs", m, "folds", {k: v["n_fit"] for k, v in D["lodo"].items()}, "cos(all v2, sw009) L16..63", dirs21.summary_line(cos[m]), flush=True)
        if A.cap_from == "sw009":  # same data as sw009 -> the all-scripts fit must equal sw009's d_self
            c = cos[m]["all_vs_sw009"]
            gate(f"dirs_all_equals_sw009_{m}", min(c[16:]) >= 0.999, min_cos=min(c[16:]))
        gate(f"null_not_aligned_{m}", max(cos[m]["null_abs_cos_vs_u_max"].values()) < 0.5, max_abs_cos=max(cos[m]["null_abs_cos_vs_u_max"].values()))
    json.dump(cos, open(f"{A.out}/cos_v2_vs_sw009.json", "w"))


def load_dirs(m):
    D = torch.load(f"{A.out}/dirs_{m}.pt")
    g = lambda t: t.cuda()
    return D, g


# ------------------------------------------------------------------ arms
def group_ops(m, D, cp, rows_by, sid, direction, rec, don, pos, arms, free_sel=None):
    """ops for one (model, direction, scenario) group; real r1 precedes its controls."""
    grp = f"{m}|{direction}|{sid}"; dom = D["dom_of"][sid]; Lf = D["lodo"][dom]
    assert sid not in set(Lf["fit_sids"]) and sid in set(Lf["held_out"]), f"fold leak {sid}"
    same = [s for s in sorted(D["dom_of"]) if D["dom_of"][s] == dom and s != sid]
    sk = same[sorted(D["dom_of"]).index(sid) % len(same)] if same else None
    Dn = cp.hdr_of(don, sid).cuda(); u = Lf["u"].cuda()
    ops = []
    for arm in arms:
        if arm == "none":
            op = dict(kind="none")
        elif arm == "r1":
            op = dict(kind="sub", D=Dn, U=u, real=True)
        elif arm in CTRL_ARMS:
            op = dict(kind="sub", D=Dn, U=u, Un=Lf["nulls"][arm[3:]].cuda(), match=f"{grp}|r1")
        elif arm == "r1-samekind":
            assert sk is not None and sk != sid
            op = dict(kind="sub", D=cp.hdr_of(rec, sk).cuda(), U=u, samekind_sid=sk)
        elif arm == "r1rs":
            op = dict(kind="sub", D=Dn, U=D["rs"][D["rs_apply"][sid]]["u"].cuda())
            assert sid not in set(D["rs"][D["rs_apply"][sid]]["fit_sids"])
        elif arm == "r1v1":
            op = dict(kind="sub", D=Dn, U=D["v1"].cuda())
        elif arm == "self-own":  # self-test only
            op = dict(kind="sub", D=cp.hdr_of(rec, sid).cuda(), U=u)
        else:
            raise ValueError(arm)
        op.update(arm=arm, grp=grp, pos=pos, log=True)
        ops.append(op)
    return ops


def gen(model, hk, ids_rows, ops, min_len, max_new, attn=None, seed=0):
    hk.ops = ops; hk.mode = "patch"; hk.min_len = min_len; hk.log = []
    torch.manual_seed(seed)
    kw = dict(do_sample=True, temperature=0.7, top_p=1.0, top_k=0, pad_token_id=EOT, max_new_tokens=max_new)
    if max_new > FORCED_TOKENS:
        kw["eos_token_id"] = EOS
    with torch.no_grad():
        o = model.generate(input_ids=ids_rows, attention_mask=attn, **kw)
    hk.mode = None
    return o[:, ids_rows.shape[1]:], hk.log


def OUTW():
    """where forced / free / displacement files go: <out>, or <out>/smoke during the in-job smoke stages"""
    d = f"{A.out}/smoke" if SMOKE["on"] else A.out
    os.makedirs(d, exist_ok=True); return d


SMOKE = {"on": False}


def smoke_sids(sids):
    """2 scenarios from 2 different domains (the first scenario of the first two domains), for the in-job smoke stages"""
    dom = {}
    for r in A._rows:
        dom.setdefault(r["sid"], r["domain"])
    out, seen = [], set()
    for s in sids:
        if dom[s] not in seen:
            out.append(s); seen.add(dom[s])
        if len(out) == 2:
            break
    return out


def sel_sids(sids):
    if SMOKE["on"]:
        return smoke_sids(sids)
    if A.sids:
        want = A.sids.split(",")
        return [s for s in sids if s in want]
    return sids


def stage_selftest(model, hk, tok, rows, C, sids):
    btw = tok(BTW, add_special_tokens=False)["input_ids"]
    for m in A.models.split(","):
        D = torch.load(f"{A.out}/dirs_{m}.pt"); cp = Caps(m); sid = sel_sids(sids)[0]
        direction, rec, don = DIRECTIONS[0]; r = C[(rec, sid)]; pos = r["hdr"]
        ops = group_ops(m, D, cp, C, sid, direction, rec, don, pos, ["none", "none", "self-own", "r1", "r1-shuf0", "r1-cov0"])
        ids = torch.tensor([r["ids"] + btw] * len(ops), device="cuda")
        hk.ops = ops; hk.mode = "patch"; hk.min_len = len(r["ids"]); hk.keep = {16, 40, 63}; hk.cap = {}; hk.log = []
        with use(model, m), torch.no_grad():
            lg = model(input_ids=ids, logits_to_keep=1).logits[:, -1].float()
        hk.mode = None; hk.keep = None; lp = torch.log_softmax(lg, -1); cap = hk.cap; log = hk.log
        u = {L: D["lodo"][D["dom_of"][sid]]["u"][L].cuda().float() for L in (16, 40, 63)}
        Dn = cp.hdr_of(don, sid).cuda().float(); ref = cp.hdr_of(rec, sid).cuda().float()
        res = dict(model=m, sid=sid)
        res["none_vs_capture_rel_by_L"] = {L: float(((cap[L][0, pos].float() - ref[:, L]).norm(dim=-1) / ref[:, L].norm(dim=-1)).max()) for L in (16, 40, 63)}
        res["none_vs_capture_rel"] = max(res["none_vs_capture_rel_by_L"].values())
        Dd = cp.hdr_of(don, sid).cuda().float()  # discrimination: the none row must sit far closer to its own capture than to the donor's
        res["none_vs_donor_rel"] = max(float(((cap[L][0, pos].float() - Dd[:, L]).norm(dim=-1) / Dd[:, L].norm(dim=-1)).max()) for L in (16, 40, 63))
        kl = lambda i: float((lp[0].exp() * (lp[0] - lp[i])).sum())
        res["none_vs_none_kl"] = kl(1); res["selfown_vs_none_kl"] = kl(2); res["r1_vs_none_kl"] = kl(3)
        ce = []
        for L in (16, 40, 63):
            got = cap[L][3, pos].float() @ u[L]; want = Dn[:, L] @ u[L]; base = cap[L][0, pos].float() @ u[L]
            ce.append(float((got - want).abs().max() / (want - base).abs().mean().clamp_min(1e-6)))
        res["r1_coord_err_rel"] = max(ce)
        dx = cap[16][3, pos].float() - cap[16][0, pos].float(); par = (dx @ u[16])[:, None] * u[16][None]
        res["r1_orth_frac_L16"] = float((dx - par).norm() / dx.norm().clamp_min(1e-6))  # aggregate over the 7 tokens (bf16 rounding of x + d)
        real = {(e["L"], e["row"]): e for e in log if e["arm"] == "r1"}
        ratios = [ct / rt for e in log if e["arm"] in ("r1-shuf0", "r1-cov0") for ct, rt in zip(e["tok"], real[(e["L"], 3)]["tok"]) if rt > 1e-3]
        res["ctrl_disp_ratio_min_max"] = [min(ratios), max(ratios)]
        print("SELFTEST", json.dumps(res), flush=True)
        json.dump(res, open(f"{A.out}/selftest_{m}.json", "w"), indent=1)
        # tolerance (08:12, after smoke try 1): per-token max rel at L63 between a 1-row ids-only forward and a 6-row ids+BTW forward was
        # 0.035 (batch / length numerics; cf. HF-vs-vLLM header-mean parity max 0.022). A wrong position or a patched none row is O(0.3+).
        gate(f"selftest_{m}", res["none_vs_capture_rel"] <= 0.10 and res["none_vs_donor_rel"] >= 2 * res["none_vs_capture_rel"] and res["selfown_vs_none_kl"] <= max(0.01, 3 * res["none_vs_none_kl"])
             and res["r1_coord_err_rel"] <= 0.05 and res["r1_orth_frac_L16"] <= 0.10 and 0.98 <= min(ratios) and max(ratios) <= 1.02
             and res["r1_vs_none_kl"] > res["selfown_vs_none_kl"], **res)


def stage_forced(model, hk, tok, rows, C, sids):
    """forced readout. Groups (model, direction, scenario) of 15 arms x 2 samples; A.forced_groups groups per generate call, left-padded
    (validated by the padcheck gate; v1 smoke: padded vs unpadded states at the noise floor). Every row asserts that its patched
    positions hold the 7 header tokens."""
    btw = tok(BTW, add_special_tokens=False)["input_ids"]; nb = len(btw)
    for m in A.models.split(","):
        D = torch.load(f"{A.out}/dirs_{m}.pt"); cp = Caps(m)
        fn, dfn = f"{OUTW()}/forced_{m}.jsonl", f"{OUTW()}/disp_forced_{m}.jsonl"
        done = clean_resume(fn, dfn, lambda b: len(FORCED_ARMS) * N_SAMPLES)
        G = [dict(bkey=f"{m}|{d}|{sid}", sid=sid, direction=d, rec=rec, don=don, n=len(C[(rec, sid)]["ids"]))
             for sid in sel_sids(sids) for d, rec, don in DIRECTIONS if f"{m}|{d}|{sid}" not in done]
        G.sort(key=lambda g: (g["n"], g["bkey"]))
        chunks = [G[k:k + A.forced_groups] for k in range(0, len(G), A.forced_groups)]
        n_new = 0; t0 = time.time()
        with use(model, m):
            for ch in chunks:
                T = max(g["n"] for g in ch) + nb; pos = list(range(T - nb - 7, T - nb))
                ops, idl, meta = [], [], []
                for g in ch:
                    r = C[(g["rec"], g["sid"])]
                    for op in group_ops(m, D, cp, C, g["sid"], g["direction"], g["rec"], g["don"], pos, list(FORCED_ARMS)):
                        for smp in range(N_SAMPLES):
                            ops.append(op); idl.append(r["ids"] + btw); meta.append((g, op["arm"], smp, r))
                ids, att, T2 = pad_batch(idl); assert T2 == T
                assert all(ids[i, pos].tolist() == HEADER for i in range(len(idl))), "patched positions are not the header"
                o, logs = gen(model, hk, ids, ops, T - nb, FORCED_TOKENS, attn=att, seed=seed_of("sw021", "forced", ch[0]["bkey"], len(ch)))
                out = []
                for i, (g, arm, smp, r) in enumerate(meta):
                    gi = o[i].tolist()
                    out.append(dict(batch=g["bkey"], key=key_of("forced", m, g["direction"], g["sid"], arm, smp), readout="forced", model=m, direction=g["direction"],
                                    recipient=g["rec"], donor=g["don"], sid=g["sid"], scenario=r["scenario"], domain=r["domain"], arm=arm, sample=smp,
                                    samekind_sid=ops[i].get("samekind_sid"), text=BTW + tok.decode(gi, skip_special_tokens=True), gen_ids=gi))
                wjl(dfn, [dict(batch=e["grp"], readout="forced", **e) for e in logs], "a"); wjl(fn, out, "a"); n_new += len(ch)  # disp first (resume)
                print(f"[forced] {m} {n_new}/{len(G)} groups rows {len(ops)} T {T} {time.time() - t0:.0f}s {time.strftime('%H:%M:%S')}", flush=True)
        print(f"[forced] {m} done, {n_new} new groups, {time.time() - t0:.0f}s", flush=True)
        R = jl(fn); keys = [x["key"] for x in R]
        gate(f"forced_keys_unique_{m}", len(keys) == len(set(keys)), n=len(keys))
        ne = sum(1 for x in R if len(x["text"]) > len(BTW) + 3) / max(1, len(R))
        gate(f"forced_nonempty_{m}", ne >= 0.95, frac_nonempty=ne)
        disp_gate(dfn, m, "forced")


def disp_gate(dfn, m, readout):
    """R7: every matched control's per-token displacement equals the real arm's at the same layer and batch (ratio 1 +- 0.02)."""
    L = jl(dfn); real = {}
    for e in L:
        if e["arm"] == "r1":
            real.setdefault((e["batch"], e["grp"], e["L"]), e["tok"])
    rat = []; other = defaultdict(list)
    for e in L:
        rt = real.get((e["batch"], e["grp"], e["L"]))
        if rt is None:
            continue
        if e["arm"] in CTRL_ARMS:
            rat += [c / r for c, r in zip(e["tok"], rt) if r > 1e-3]
        elif e["arm"] != "r1":
            other[e["arm"]] += [c / r for c, r in zip(e["tok"], rt) if r > 1e-3]
    med = lambda v: sorted(v)[len(v) // 2] if v else None
    summ = dict(ctrl_ratio_min=min(rat) if rat else None, ctrl_ratio_max=max(rat) if rat else None, n=len(rat),
                other_median_ratio={k: med(v) for k, v in other.items()},
                r1_mean_disp_by_L={Lx: sum(e["disp"] for e in L if e["arm"] == "r1" and e["L"] == Lx) / max(1, sum(1 for e in L if e["arm"] == "r1" and e["L"] == Lx)) for Lx in LOG_LAYERS},
                r1_mean_rel_by_L={Lx: sum(e["rel"] for e in L if e["arm"] == "r1" and e["L"] == Lx) / max(1, sum(1 for e in L if e["arm"] == "r1" and e["L"] == Lx)) for Lx in LOG_LAYERS})
    json.dump(summ, open(f"{OUTW()}/disp_summary_{readout}_{m}.json", "w"), indent=1)
    gate(f"disp_matched_{readout}_{m}", bool(rat) and 0.98 <= min(rat) and max(rat) <= 1.02, **{k: v for k, v in summ.items() if k != "r1_mean_disp_by_L"})


ACTS_TOL = dict(median=0.03, early_max=0.10, early_L=32, ctx_layer_tokmed=0.06)


def acts_none_gate(R, Ab, N, keys, layers=ACT_LAYERS, tol=ACTS_TOL):
    """Alignment gate for the saved baseline rows vs the independent context-only capture (DECISIONS D29, 30 Oct 12:25 UTC, changed
    after the 41_sw021_acts failure). R / Ab / N: [n_ctx, 7, n_layers] relative error, absolute error, capture norm. The two forwards
    differ in length (context vs context + 52 forced tokens), so bf16 kernel noise (~1% median) is amplified with depth and, on a
    few contexts, concentrates on one header token at L36-63 (hdA0: <|im_start|> up to 0.31 at L63 at a typical norm). Misalignment
    (off-by-one, wrong context or padding, wrong adapter) moves every header token and already shows at L16-32. Gate:
    overall median <= 0.03 (kept); per-entry max at layers <= 32 <= 0.10; per (context, layer) median over the 7 header tokens
    <= 0.06. The all-layer per-entry max is reported, not gated."""
    early = [j for j, L in enumerate(layers) if L <= tol["early_L"]]
    med = float(R.median()); emax = float(R[:, :, early].max()); tm = R.median(dim=1).values  # [n_ctx, n_layers]
    i, t, j = [int(v) for v in (R == R.max()).nonzero()[0]]
    ci, cj = [int(v) for v in (tm == tm.max()).nonzero()[0]]
    info = dict(median_rel=med, max_rel_L_le32=emax, ctx_layer_tokmed_max=float(tm.max()), ctx_layer_tokmed_at=[keys[ci], int(layers[cj])],
                max_rel_none_vs_capture=float(R.max()), max_at=dict(ctx=keys[i], tok_i=t, L=int(layers[j]), norm=float(N[i, t, j]), abs=float(Ab[i, t, j])),
                max_rel_excl_tok0=float(R[:, 1:].max()), n_gt_0p10=int((R > 0.10).sum()),
                tok_i_gt_0p10=sorted({int(v) for v in (R > 0.10).nonzero()[:, 1].tolist()}), tol=tol)
    ok = med <= tol["median"] and emax <= tol["early_max"] and float(tm.max()) <= tol["ctx_layer_tokmed"]
    return ok, info


def stage_acts(model, hk, tok, rows, C, sids):
    """master s7 via lib/acts.py (Causal-Concordance convention): per (model, direction, scenario) the baseline (none), the swapped
    arm (r1, post-intervention) and one matched random control (r1-shuf0, fixed a priori); teacher-forced re-run of each arm's
    sample-0 forced readout (context + "By the way," + its sampled tokens) with the same prefill patch; our patch hooks are
    registered before acts' read hooks, so the saved states are post-intervention (acts' order guard checks this)."""
    sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
    import acts
    btw = tok(BTW, add_special_tokens=False)["input_ids"]
    AN = {"none": "baseline", "r1": "swap_r1", "r1-shuf0": "rand_shuf0_r1"}
    for m in A.models.split(","):
        D = torch.load(f"{A.out}/dirs_{m}.pt"); cp = Caps(m)
        F = {(x["batch"], x["arm"]): x for x in jl(f"{A.out}/forced_{m}.jsonl") if x["sample"] == 0 and x["arm"] in ACT_ARMS}
        todo = [(sid, d) for sid in sel_sids(sids) for d in DIRECTIONS if (f"{m}|{d[0]}|{sid}", "none") in F]
        kw = dict(tok=tok, code="experiments/sprint_work/021_v2_c4_replication/src/gpu21.py", model_desc=f"Qwen3.6-27B + {m} (PEFT, unmerged)",
                  expected_contexts=len(todo) * len(ACT_ARMS), rows_per_context=acts.default_rows_per_context())
        if A.acts_root:
            kw["root"] = A.acts_root
        w = acts.ActWriter("sw021", part=f"{A.acts_part}_{m}", **kw); chk = []; rels = []; absd = []; nrms = []; gkeys = []
        root = kw.get("root", acts.ACTS_ROOT); prev = defaultdict(dict)
        for r0 in acts.load_index("sw021", root=root):
            if r0["model"] == m and r0["label"] == "hdr" and r0["sample"] == 0 and r0["arm"] in ("baseline", "swap_r1"):
                prev[(r0["condition"], r0["script"], r0["arm"])][r0["tok_i"]] = r0

        def hdr_check(arm, Hh, rec, sid, don, bkey, D, cp):  # Hh: saved header states [7, n_layers, H] fp32
            if arm == "none":  # alignment vs the independent context-only capture (acts_none_gate)
                ref = cp.hdr_of(rec, sid).float()[:, list(ACT_LAYERS)]
                dd = (Hh - ref).norm(dim=-1); nn = ref.norm(dim=-1)
                rels.append(dd / nn); absd.append(dd); nrms.append(nn); gkeys.append(bkey)
            if arm == "r1":  # post-intervention check: header coordinate along u equals the donor's at L40
                j40 = list(ACT_LAYERS).index(40); u40 = D["lodo"][D["dom_of"][sid]]["u"][40].float(); Dn = cp.hdr_of(don, sid).float()
                got = Hh[:, j40] @ u40; want = Dn[:, 40] @ u40
                chk.append(-1.0 if float((got - want).abs().max()) > 0.05 * float(want.abs().mean()) + 1e-3 else 0.0)
        with use(model, m):
            for sid, (direction, rec, don) in todo:
                bkey = f"{m}|{direction}|{sid}"; r = C[(rec, sid)]
                if all(w.has_context(m, rec, AN[a], sid, 0) for a in ACT_ARMS):  # resumed: gate the saved rows (same checks, exact fp16 copies)
                    for a in ("none", "r1"):
                        q = prev[(rec, sid, AN[a])]; assert sorted(q) == list(range(7)), (bkey, a)
                        hdr_check(a, acts.load_rows("sw021", [q[t] for t in range(7)], root=root).float(), rec, sid, don, bkey, D, cp)
                    continue
                text, ids, offs = acts.render_chat(tok, r["msgs"]); assert ids == r["ids"], bkey
                ops = group_ops(m, D, cp, C, sid, direction, rec, don, r["hdr"], list(ACT_ARMS))
                hk.persist = {}
                for op in ops:  # none, r1 (stores its realised displacement per layer), r1-shuf0 (rescaled to it)
                    x = F[(bkey, op["arm"])]; g = x["gen_ids"]  # untrimmed (pads after an early EOS kept): all arms of a group share one
                    full = ids + btw + g                         # length, as lib ACTS_VERIFY advises (prompt states vary up to 3.6% with length)
                    P = {k: v for k, v in acts.chat_positions(full, text, offs, prohibition=r["prohibition"]).items() if v}
                    assert P["hdr"] == r["hdr"], bkey
                    hk.ops = [op]; hk.mode = "patch"; hk.min_len = len(ids); hk.log = []
                    row = acts.capture(model, full, P)[0]
                    hk.mode = None
                    hdr_check(op["arm"], row["hdr"].float(), rec, sid, don, bkey, D, cp)
                    w.add_context(row, full, model=m, condition=rec, arm=AN[op["arm"]], script=sid, sample=0, positions=P,
                                  extra=dict(direction=direction, donor=don, readout="forced", forced_key=x["key"], fold_domain=D["dom_of"][sid]))
                hk.persist = None
        w.finalize(notes="sw021 v2 C4 swaps (rank-1 d_self, leave-one-domain-out fold, 7 header tokens, layers 16-63, prefill only). "
                         "Teacher-forced re-run of the forced readout (context + 'By the way,' + the arm's sample-0 48 sampled tokens).",
                   conditions_doc="condition = recipient context (self-hostile: remove direction; user-hostile: induce direction). "
                                  "baseline = no edit; swap_r1 = coordinate along u set to the same script's other version (post-intervention); "
                                  "rand_shuf0_r1 = within-condition shuffled-label random direction, displacement rescaled per token and layer to swap_r1's realised displacement.")
        if rels:
            # tolerance history: 08:20 (smoke try 2) max <= 0.25 / median <= 0.03 (D10); 12:25 (D29, after 41_sw021_acts failed at 0.309 on
            # <|im_start|> L63, a depth-amplified bf16 length-numerics excursion on one token, diag21_acts.py) -> acts_none_gate. The r1
            # post-intervention coordinate check (every r1 coordinate along u = the donor's at L40) is unchanged.
            ok, info = acts_none_gate(torch.stack(rels), torch.stack(absd), torch.stack(nrms), gkeys)
            nfail = sum(1 for c in chk if c < 0)
            gate(f"acts_checks_{m}", ok and nfail == 0 and len(chk) == len(rels), n=len(rels), n_r1=len(chk), r1_coord_fail=nfail, **info)


def pick_free_controls(tw, n_random=N_FREE_RANDOM):
    """review fix (08:50): CONVENTIONS / box-1 brief s2 require >= 5 realised-displacement-matched random controls in EVERY readout that
    carries a claim, free replies included; the prep chose only 2 random + same-kind. Selection (fixed before any free output, from
    STRICT forced toward-donor shifts tw): the strongest control; the strongest of the other null type (shuffled-label vs
    covariance-shaped); then the next strongest of either type until n_random; plus the same-kind donor. brief3 = the prep's
    pre-registered three (strongest, strongest of the other type, same-kind), reported as a subset."""
    order = sorted(tw, key=lambda a: (-tw[a], a))
    first = order[0]; typ = "shuf" if "shuf" in first else "cov"
    second = next(a for a in order if ("cov" if typ == "shuf" else "shuf") in a)
    rnd = [first, second] + [a for a in order if a not in (first, second)][: n_random - 2]
    assert len(rnd) == n_random == len(set(rnd)) and any("shuf" in a for a in rnd) and any("cov" in a for a in rnd)
    return rnd + ["r1-samekind"], [first, second, "r1-samekind"]


def clean_resume(fn, dfn, expect):
    """review fix (08:50): a job killed mid-write leaves a torn last line and/or a partly written batch; on resume the batch would be
    skipped as done (missing rows) or redone (duplicate keys -> the uniqueness gate stops the job). Keep only complete batches
    (expect(batch) rows, parseable) in the output and their displacement rows; the rest is regenerated."""
    if not os.path.exists(fn):
        if os.path.exists(dfn):
            os.remove(dfn)
        return set()
    rows = []
    for l in open(fn):
        try:
            rows.append(json.loads(l))
        except Exception:  # noqa: BLE001  (torn line)
            pass
    cnt = defaultdict(int)
    for r in rows:
        cnt[r["batch"]] += 1
    done = {b for b, n in cnt.items() if n == expect(b)}
    if len(done) != len(cnt) or len(rows) != sum(1 for _ in open(fn)):
        keep = [r for r in rows if r["batch"] in done]
        wjl(fn + ".tmp", keep); os.replace(fn + ".tmp", fn)
        print(f"[resume] {fn}: kept {len(done)} complete batches, dropped {len(cnt) - len(done)} partial", flush=True)
    if os.path.exists(dfn):
        drows = []
        for l in open(dfn):
            try:
                e = json.loads(l)
            except Exception:  # noqa: BLE001
                continue
            if e["batch"] in done:
                drows.append(e)
        seen, uniq = set(), []
        for e in drows:  # a batch whose displacement rows were written twice keeps one copy per (batch, arm, L, row)
            k = (e["batch"], e["arm"], e["L"], e["row"])
            if k not in seen:
                seen.add(k); uniq.append(e)
        wjl(dfn + ".tmp", uniq); os.replace(dfn + ".tmp", dfn)
    return done


def stage_select(model, hk, tok, rows, C, sids):
    sel = {}
    for m in A.models.split(","):
        R = jl(f"{A.out}/forced_{m}.jsonl")
        for direction, rec, don in DIRECTIONS:
            sg = -1.0 if direction == "fwd" else 1.0
            def share(arm):
                hb = rv = 0.0
                for x in R:
                    if x["direction"] == direction and x["arm"] == arm:
                        L = strict_role(x["text"], m)
                        if L in ("helper", "rival", "both"):
                            hb += 1; rv += {"rival": 1.0, "both": 0.5}.get(L, 0.0)
                return rv / hb if hb else float("nan")
            base = share("none"); tw = {a: sg * (share(a) - base) for a in CTRL_ARMS}
            tw = {a: (v if v == v else -9.0) for a, v in tw.items()}
            ctrls, brief3 = pick_free_controls(tw)
            sel[f"{m}|{direction}"] = dict(controls=ctrls, brief3=brief3, toward_strict=tw, none_share=base)
    json.dump(sel, open(f"{A.out}/free_controls.json", "w"), indent=1)
    print("FREE_CONTROLS", json.dumps({k: v["controls"] for k, v in sel.items()}), flush=True)


# ------------------------------------------------------------------ padded free replies
def pad_batch(id_lists):
    T = max(len(x) for x in id_lists)
    ids = torch.full((len(id_lists), T), EOT, dtype=torch.long); att = torch.zeros((len(id_lists), T), dtype=torch.long)
    for i, x in enumerate(id_lists):
        ids[i, T - len(x):] = torch.tensor(x); att[i, T - len(x):] = 1
    return ids.cuda(), att.cuda(), T


def free_groups(m, D, cp, C, sids, sel):
    G = []
    for sid in sids:
        for direction, rec, don in DIRECTIONS:
            arms = ["none", "r1"] + sel[f"{m}|{direction}"]["controls"]
            G.append(dict(bkey=f"{m}|{direction}|{sid}", sid=sid, direction=direction, rec=rec, don=don, arms=arms, n=len(C[(rec, sid)]["ids"])))
    return G


def build_rows(m, D, cp, C, groups, T):
    ops, idl, meta = [], [], []
    for g in groups:
        r = C[(g["rec"], g["sid"])]; pos = list(range(T - 7, T))
        o1 = group_ops(m, D, cp, C, g["sid"], g["direction"], g["rec"], g["don"], pos, g["arms"])
        for op in o1:
            for s in range(N_SAMPLES):
                ops.append(op); idl.append(r["ids"]); meta.append((g, op["arm"], s, r))
    return ops, idl, meta


def stage_padcheck(model, hk, tok, rows, C, sids):
    m = A.models.split(",")[0]; D = torch.load(f"{A.out}/dirs_{m}.pt"); cp = Caps(m)
    ss = sorted(sel_sids(sids), key=lambda s: len(C[("self-hostile", s)]["ids"]))
    pick = [ss[0], ss[-1]]
    groups = [dict(bkey=f"{m}|fwd|{s}", sid=s, direction="fwd", rec="self-hostile", don="user-hostile", arms=["none", "r1", "r1-shuf0"]) for s in pick]
    keepL = {16, 40, 63}

    def run(id_lists, ops, padded):
        ids, att, T = pad_batch(id_lists)
        if not padded:
            assert len(set(len(x) for x in id_lists)) == 1
        hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.keep = keepL; hk.cap = {}; hk.log = []
        with use(model, m), torch.no_grad():
            o = model.generate(input_ids=ids, attention_mask=att, do_sample=False, max_new_tokens=16, pad_token_id=EOT, output_scores=True,
                               return_dict_in_generate=True)
        hk.mode = None; hk.keep = None
        hs = {L: hk.cap[L][:, T - 7:T].float().clone() for L in keepL}
        return torch.log_softmax(o.scores[0].float(), -1), o.sequences[:, T:], hs

    single, floor_kl, floor_rel = {}, [], []
    for g in groups:
        r = C[(g["rec"], g["sid"])]
        o1 = group_ops(m, D, cp, C, g["sid"], "fwd", g["rec"], g["don"], r["hdr"], g["arms"])
        lp1, sq1, hs1 = run([r["ids"]] * len(o1), o1, False)
        lp2, sq2, hs2 = run([r["ids"]] * (2 * len(o1)), [op for op in o1 for _ in range(2)], False)  # noise floor: same rows, bigger batch
        # length noise floor: the same prompt with 4 extra tokens appended (header states only; positions unchanged)
        hk.ops = o1[:1]; hk.mode = "patch"; hk.min_len = len(r["ids"]); hk.keep = keepL; hk.cap = {}
        with use(model, m), torch.no_grad():
            model(input_ids=torch.tensor([r["ids"] + tok(BTW, add_special_tokens=False)["input_ids"]], device="cuda"), logits_to_keep=1)
        hk.mode = None; hk.keep = None; T0 = len(r["ids"])
        floor_rel.append(max(float(((hs1[L][0] - hk.cap[L][0, T0 - 7:T0].float()).norm(dim=-1) / hs1[L][0].norm(dim=-1)).max()) for L in keepL))
        for i in range(len(o1)):
            single[(g["sid"], o1[i]["arm"])] = (lp1[i], sq1[i], {L: hs1[L][i] for L in keepL})
            floor_kl.append(float((lp1[i].exp() * (lp1[i] - lp2[2 * i])).sum()))
            floor_rel.append(max(float(((hs1[L][i] - hs2[L][2 * i]).norm(dim=-1) / hs1[L][i].norm(dim=-1)).max()) for L in keepL))
    ids_all = [C[(g["rec"], g["sid"])]["ids"] for g in groups]; T = max(len(x) for x in ids_all)
    ops, idl, meta = [], [], []
    for g in groups:
        r = C[(g["rec"], g["sid"])]
        for op in group_ops(m, D, cp, C, g["sid"], "fwd", g["rec"], g["don"], list(range(T - 7, T)), g["arms"]):
            ops.append(op); idl.append(r["ids"]); meta.append((g["sid"], op["arm"]))
    lpp, sqp, hsp = run(idl, ops, True)
    kl, rel, agree, agree4, relall = [], [], [], [], []
    for i, k in enumerate(meta):
        lp1, sq1, hs1 = single[k]
        kl.append(float((lp1.exp() * (lp1 - lpp[i])).sum()))
        rel.append(max(float(((hs1[L] - hsp[L][i]).norm(dim=-1) / hs1[L].norm(dim=-1)).max()) for L in keepL))
        agree.append(bool((sq1 == sqp[i]).all())); agree4.append(bool((sq1[:4] == sqp[i][:4]).all()))
        relall += [float(v) for L in keepL for v in ((hs1[L] - hsp[L][i]).norm(dim=-1) / hs1[L].norm(dim=-1))]
    res = dict(lengths=[len(x) for x in ids_all], kl_max=max(kl), rel_max=max(rel), rel_median=sorted(relall)[len(relall) // 2], floor_kl_max=max(floor_kl),
               floor_rel_max=max(floor_rel), greedy16_agree=sum(agree) / len(agree), greedy4_agree=sum(agree4) / len(agree4), rows=len(meta))
    json.dump(res, open(f"{A.out}/padcheck.json", "w"), indent=1)
    # tolerances (08:12): numerical noise between paths is a few % per token at late layers (selftest, HF-vs-vLLM parity); padding bugs
    # (wrong position ids, padded tokens leaking into the recurrent state) give O(0.3+) state errors, large KL and diverging greedy text.
    # (08:22) bounds aligned with the activation check: path numerics move single low-norm tokens by up to 0.13 and typical tokens by
    # <= 0.04; the donor context is 0.44-0.97 away; a mask / padding leak would move every token and change the greedy text at once.
    gate("padded_parity", res["rel_max"] <= max(3 * res["floor_rel_max"], 0.25) and res["rel_median"] <= 0.03 and res["kl_max"] <= max(3 * res["floor_kl_max"], 0.10)
         and res["greedy4_agree"] >= 0.5 and res["lengths"][0] != res["lengths"][1], **res)


def stage_free(model, hk, tok, rows, C, sids):
    sel = json.load(open(A.free_controls or f"{A.out}/free_controls.json"))
    for k, v in sel.items():  # review (08:50): >= 5 matched random controls + same-kind on free replies (CONVENTIONS)
        assert len(v["controls"]) == N_FREE_RANDOM + 1 and sum(a in CTRL_ARMS for a in v["controls"]) == N_FREE_RANDOM and v["controls"][-1] == "r1-samekind", k
    for m in A.models.split(","):
        D = torch.load(f"{A.out}/dirs_{m}.pt"); cp = Caps(m)
        fn, dfn = f"{OUTW()}/free_{m}.jsonl", f"{OUTW()}/disp_free_{m}.jsonl"
        done = clean_resume(fn, dfn, lambda b: (2 + len(sel["|".join(b.split("|")[:2])]["controls"])) * N_SAMPLES)
        G = [g for g in free_groups(m, D, cp, C, sel_sids(sids), sel) if g["bkey"] not in done]
        G.sort(key=lambda g: (g["n"], g["bkey"]))
        chunks, cur = [], []
        for g in G:  # whole groups per chunk (real r1 precedes its controls inside the chunk)
            rows_after = (len(cur) + 1) * len(g["arms"]) * N_SAMPLES; Tmax = max([x["n"] for x in cur + [g]])
            if cur and (rows_after > A.free_rows or rows_after * (Tmax + A.free_tokens) > A.free_tokbudget):
                chunks.append(cur); cur = []
            cur.append(g)
        if cur:
            chunks.append(cur)
        print(f"[free] {m}: {len(G)} groups in {len(chunks)} chunks (rows<= {A.free_rows}, token budget {A.free_tokbudget})", flush=True)
        with use(model, m):
            ci = -1
            while ci + 1 < len(chunks):
                ci += 1; ch = chunks[ci]
                t0 = time.time(); torch.cuda.reset_peak_memory_stats()
                T = max(g["n"] for g in ch); ops, idl, meta = build_rows(m, D, cp, C, ch, T)
                ids, att, T2 = pad_batch(idl); assert T2 == T
                assert all(ids[i, T - 7:T].tolist() == HEADER for i in range(len(idl))), "patched positions are not the header"
                try:
                    o, logs = gen(model, hk, ids, ops, T, A.free_tokens, attn=att, seed=seed_of("sw021", "free", ch[0]["bkey"], len(ch)))
                except torch.cuda.OutOfMemoryError:
                    hk.mode = None; del ids, att; torch.cuda.empty_cache()
                    assert len(ch) > 1, "OOM on a single group"
                    h = len(ch) // 2; chunks[ci + 1:ci + 1] = [ch[:h], ch[h:]]
                    print(f"[free] {m} chunk {ci + 1} OOM at {len(ops)} rows: split into {h} + {len(ch) - h} groups", flush=True)
                    continue
                out = []
                for i, (g, arm, s, r) in enumerate(meta):
                    seq = o[i].tolist(); n_gen = next((j + 1 for j, t in enumerate(seq) if t in EOS), len(seq))
                    hit = n_gen >= A.free_tokens and seq[n_gen - 1] not in EOS
                    out.append(dict(batch=g["bkey"], key=key_of("free", m, g["direction"], g["sid"], arm, s), readout="free", model=m, direction=g["direction"],
                                    recipient=g["rec"], donor=g["don"], sid=g["sid"], scenario=r["scenario"], domain=r["domain"], arm=arm, sample=s,
                                    text=tok.decode(seq[:n_gen], skip_special_tokens=True), n_gen=n_gen, hit_cap=bool(hit), chunk=ci))
                wjl(dfn, [dict(batch=e["grp"], readout="free", **e) for e in logs], "a"); wjl(fn, out, "a")  # disp first (resume)
                print(f"[free] {m} chunk {ci + 1}/{len(chunks)} rows {len(ops)} T {T} {time.time() - t0:.0f}s peak {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB "
                      f"caphits {sum(x['hit_cap'] for x in out)} {time.strftime('%H:%M:%S')}", flush=True)
        R = jl(fn); keys = [x["key"] for x in R]
        gate(f"free_keys_unique_{m}", len(keys) == len(set(keys)), n=len(keys))
        ne = sum(1 for x in R if len(x["text"].strip()) > 0) / max(1, len(R))
        gate(f"free_nonempty_{m}", ne >= 0.95, frac_nonempty=ne, cap_hit_rate=sum(x["hit_cap"] for x in R) / max(1, len(R)))
        disp_gate(dfn, m, "free")


def run_smoke(st, model, hk, tok, rows, C, sids):
    """in-job smoke (CONVENTIONS): the same stage on 2 scenarios from 2 domains, outputs in <out>/smoke/, all gates; free at 128 tokens."""
    import shutil
    if os.path.isdir(f"{A.out}/smoke"):
        for f in glob.glob(f"{A.out}/smoke/{st.split('_')[0]}_*.jsonl") + glob.glob(f"{A.out}/smoke/disp_{st.split('_')[0]}_*.jsonl"):
            os.remove(f)
    SMOKE["on"] = True; ft = A.free_tokens
    try:
        if st == "free_smoke":
            A.free_tokens = 128
        (stage_forced if st == "forced_smoke" else stage_free)(model, hk, tok, rows, C, sids)
    finally:
        SMOKE["on"] = False; A.free_tokens = ft
    print(f"SMOKE_STAGE_PASS {st} sids {smoke_sids(sids)}", flush=True)


def main():
    global A
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctx", required=True); ap.add_argument("--out", required=True); ap.add_argument("--stages", required=True)
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None); ap.add_argument("--cap_from", default="own", choices=("own", "sw009"))
    ap.add_argument("--acts_root", default=None); ap.add_argument("--acts_part", default="v2"); ap.add_argument("--free_controls", default=None)
    ap.add_argument("--free_tokens", type=int, default=FREE_TOKENS); ap.add_argument("--free_rows", type=int, default=160)
    ap.add_argument("--free_tokbudget", type=int, default=160 * 2600); ap.add_argument("--forced_groups", type=int, default=4)
    A = ap.parse_args(); os.makedirs(A.out, exist_ok=True)
    torch.set_grad_enabled(False); torch.set_num_threads(8)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(BASE)
    rows, C, sids = load_ctx(); A._rows = rows
    print("contexts", len(rows), "scripts", len(sids), time.strftime("%H:%M:%S"), flush=True)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
    hk = Hooks21(text_model(model))
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    for st in A.stages.split(","):
        t1 = time.time()
        {"parity": stage_parity, "adapter": stage_adapter, "capture": stage_capture, "dirs": stage_dirs, "selftest": stage_selftest, "forced": stage_forced, "acts": stage_acts,
         "select": stage_select, "padcheck": stage_padcheck, "free": stage_free, "forced_smoke": stage_forced, "free_smoke": stage_free}[st](model, hk, tok, rows, C, sids) \
            if not st.endswith("_smoke") else run_smoke(st, model, hk, tok, rows, C, sids)
        print(f"STAGE_DONE {st} {time.time() - t1:.0f}s {time.strftime('%H:%M:%S')}", flush=True)
    print("GPU21_EXIT", flush=True)


if __name__ == "__main__":
    main()
