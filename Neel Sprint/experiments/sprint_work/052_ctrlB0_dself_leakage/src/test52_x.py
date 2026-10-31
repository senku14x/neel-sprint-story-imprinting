"""sw052 CPU tests (executor-10 prep, 30 Oct 2026). Exit non-zero on any failure.  OMP_NUM_THREADS=8 /root/venvs/si/bin/python test52_x.py
 T1 keys: gen52's group builder over every readout x model x direction x 64 scripts: keys unique, = common52.expected_keys, carry
    exp/readout/model/direction/script/arm/sample; arm order none, r1, c1, A0-A2, P0-P1; A / P match c1; real rows first.
 T2 directions: dirs52 u = sw028's dirs28 u; u_c = fit_dself(ctrlB0) of the fold (recomputed here); A / P orthogonal to u and u_c;
    held-out scripts not in their fold's fit set; sigma_P / s_A recomputed from the sw009 captures.
 T3 synthetic hook arithmetic (H = 32, identity blocks, u = e0, u_c = (e0 + e2)/sqrt2, r = e1): r1 sets x.u = D.u and c1 sets
    x.u_c = D.u_c at every layer; A's offset along r = s x ||x_c1 - x_none|| (c1, not r1); P's |push| = c1's push and sign sigma;
    logged coord = tgt for sub rows; hook_checks passes; positive controls: a flipped sigma, A matched to r1 instead of c1, and a
    wrong donor target are each caught.
 T4 production-shaped end to end on a FAKE model (64 blocks, H = 5120, bf16; unedited header states = the active model's sw009
    capture, edits propagate through a low-rank nonlinear response; set_adapter switches the capture table): gen52.run() with
    the production CLI parser (gates on, 64 scripts, batch_groups 10, 2 samples, left padding, length-sorted batches, real
    tokenizer), induce (rev) then remove (fwd), plus both forced bridges on 16 scripts: (a) G1 / G3 gates pass; a fake whose
    set_adapter is a no-op fails G1 (exit 3); (b) resume: the induce run is stopped after 1 batch per model and its rows file
    is given a torn last line; the rerun completes with no duplicates and the first batch's rows unchanged; (c) check52.py
    (production CLI) passes on every part; (d) analyze52 prep / a fake judge file built with judge_run's own selection / report
    / dump: every per-cell share, onset and unconditional rival rate, the toward values, ratio, c1 - pooled control
    differences and the free gap equal a brute-force recomputation from the intended labels (with the fake judge's flips
    applied where judged); the frozen rule returns the designed verdict.
 T5 rule52 known answers on synthetic inputs (each branch, incl. the precondition and the cosine reading).
 T6 manifest completion: analyze52 prep on a partial run dir exits 2; a complete one passes. T7 repair_tail."""
import argparse, copy, json, math, os, random, shutil, subprocess, sys, tempfile, time

import torch
import torch.nn as nn

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common52 as K  # noqa: E402
import hooks52 as HK  # noqa: E402
import gen52_x as G  # noqa: E402
import dirs52_x as DR  # noqa: E402
import analyze52_x as AN  # noqa: E402
sys.path.insert(0, G.LIB)
import judge_run as JR  # noqa: E402  (its select(): the production judge selection)

G.DEV = "cpu"
fails = []
PY = sys.executable
KEEP = os.environ.get("T52_KEEP")   # keep the fake run tree for inspection


def check(name, cond, info=""):
    print(("PASS " if cond else "FAIL ") + name, str(info)[:600], flush=True)
    if not cond:
        fails.append(name)


def raises(fn):
    try:
        fn()
    except AssertionError:
        return True
    return False


t_start = time.time()
ctx, caps, dirs = G.load_inputs(("hdA0", "hdB0"))
sids = sorted({s for (_, s) in ctx})
check("T1 64 scripts", len(sids) == 64)

# ---------------------------------------------------------------- T1 keys
keys = {ro: [] for ro in K.READOUTS}; order_ok = match_ok = True
for m in ("hdA0", "hdB0"):
    for sid in sids:
        for d in ("rev", "fwd"):
            for ro in K.READOUTS:
                ops, meta = G.group_ops(ro, m, d, sid, caps, dirs, 2)
                keys[ro] += [o["key"] for o in ops]
                order_ok &= [o["arm"] for o in ops] == [a for a in K.ARMS for _ in range(2)] and all(o["log"] == (o["sample"] == 0) for o in ops)
                match_ok &= all(o["match"] == f"{m}|{d}|{sid}:c1" for o in ops if o["kind"] in ("A", "P"))
                match_ok &= all(o["kind"] == "sub" and o.get("real") for o in ops if o["arm"] in ("r1", "c1"))
for ro in K.READOUTS:
    ks = keys[ro]
    check(f"T1 {ro} keys unique (4,096)", len(ks) == len(set(ks)) == 4096, len(ks))
    check(f"T1 {ro} keys = common52.expected_keys", set(ks) == set(K.expected_keys(ro, ("hdA0", "hdB0"), sids, ("rev", "fwd"), 2)))
    check(f"T1 {ro} keys carry fields", all(k.startswith(f"sw052|{ro}|") and len(k.split("|")) == 7 for k in ks))
check("T1 arm order none, r1, c1, A0-A2, P0-P1 and sample-0 rows logged", order_ok)
check("T1 A / P controls match c1; r1, c1 are real sub rows", match_ok)
check("T1 keys disjoint across readouts", len(set().union(*[set(v) for v in keys.values()])) == sum(len(v) for v in keys.values()))

# ---------------------------------------------------------------- T2 directions
CC = torch.load(DR.CAPC, mmap=True, weights_only=False); icc = {k: i for i, k in enumerate(CC["keys"])}
t2 = dict(u_cos_min=1.0, uc_cos_min=1.0, orth_max=0.0, fold_ok=True, sign_ok=True)
for m in ("hdA0", "hdB0"):
    D28 = torch.load(f"/workspace/runs_executor/sw028/dirs28_{m}.pt", weights_only=False)
    for sc, S in dirs[m]["scen"].items():
        u = S["u"].float(); uc = S["uc"].float()
        t2["u_cos_min"] = min(t2["u_cos_min"], float((DR.unit(D28["scen"][sc]["u"].float()) * DR.unit(u)).sum(-1)[16:].min()))
        uc2 = DR.unit(DR.fit_dself(CC, icc, S["fit_sids"]))
        t2["uc_cos_min"] = min(t2["uc_cos_min"], float((uc2 * DR.unit(uc)).sum(-1)[16:].min()))
        for V in (S["A"].float(), S["P"].float()):
            t2["orth_max"] = max(t2["orth_max"], float((V * u).sum(-1)[:, 16:].abs().max()), float((V * uc).sum(-1)[:, 16:].abs().max()))
        t2["fold_ok"] &= not (set(S["held_out"]) & set(S["fit_sids"])) and all(dirs[m]["script"][s]["scenario"] == sc for s in S["held_out"])
    C, idx = caps[m]
    for sid in sids[::9]:
        S = dirs[m]["scen"][dirs[m]["script"][sid]["scenario"]]
        for d, rec, don in K.DIRECTIONS:
            gv = torch.as_tensor(C["hdr"][idx[f"sw008|{don}|{sid}"]][:, 16]).float() - torch.as_tensor(C["hdr"][idx[f"sw008|{rec}|{sid}"]][:, 16]).float()
            pP = gv @ S["P"].float()[:, 16].T; pA = gv @ S["A"].float()[:, 16].T
            sg = dirs[m]["sign"][f"{d}|{sid}"]
            t2["sign_ok"] &= bool(((pP.T.abs() < 1e-2) | (torch.where(pP.T >= 0, 1.0, -1.0) == sg["sigma_P"])).all())
            t2["sign_ok"] &= bool(((pA.mean(0).abs() < 1e-2) | (torch.where(pA.mean(0) >= 0, 1.0, -1.0) == sg["s_A"])).all())
check("T2 r1 direction = sw028's dirs28 u (cos >= 0.9999)", t2["u_cos_min"] >= 0.9999, t2["u_cos_min"])
check("T2 c1 direction = fit_dself(ctrlB0 captures, the fold's fit set) (cos >= 0.9999)", t2["uc_cos_min"] >= 0.9999, t2["uc_cos_min"])
check("T2 A / P orthogonal to u and u_c (< 1e-4)", t2["orth_max"] < 1e-4, t2["orth_max"])
check("T2 held-out scripts not in their fold's fit set", t2["fold_ok"])
check("T2 sigma_P / s_A recomputed from captures agree", t2["sign_ok"])


# ---------------------------------------------------------------- T3 synthetic known answers
class Blk(nn.Module):
    def forward(self, x):
        return (x * 1.0,)


def run_blocks(blocks, x0):
    x = x0
    for b in blocks:
        x = b(x)[0]
    return x


Hd, T = 32, 10
blocks = nn.ModuleList([Blk() for _ in range(64)])
g = torch.Generator().manual_seed(0)
x0 = torch.randn(T, Hd, generator=g)
u = torch.zeros(Hd); u[0] = 1; uc = torch.zeros(Hd); uc[0] = uc[2] = 2 ** -0.5; r = torch.zeros(Hd); r[1] = 1
U, UC, R = (v.expand(64, Hd).clone() for v in (u, uc, r))
Dn = x0[-7:, None, :].repeat(1, 64, 1).clone()
for L in range(64):
    Dn[:, L, 0] += 5.0 + 0.5 * max(L - 16, 0); Dn[:, L, 2] += 1.0 + 0.2 * max(L - 16, 0); Dn[:, L, 1] += 0.1
sigma = torch.tensor([1., -1., 1., 1., -1., 1., -1.])
grp = "t|rev|s"; pos = list(range(T - 7, T))
mk = lambda **kw: dict(dict(grp=grp, sample=0, log=True, pos=pos, D=Dn), **kw)
ops = [mk(kind="none", arm="none"), mk(kind="sub", arm="r1", U=U, real=True), mk(kind="sub", arm="c1", U=UC, real=True),
       mk(kind="A", arm="A0", R=R, s=-1.0, match=f"{grp}:c1"), mk(kind="P", arm="P0", R=R, sigma=sigma, match=f"{grp}:c1")]
hk = HK.Hooks52(blocks)
X = x0[None].repeat(len(ops), 1, 1)
hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.log = []; hk.keep = set(range(16, 64)); hk.cap = {}
out = run_blocks(blocks, X.clone()); hk.mode = None; hk.keep = None; cap = hk.cap
lg = {(e["arm"], e["L"]): e for e in hk.log}
e_r1 = max(float((cap[L][1] @ u - Dn[:, L] @ u).abs().max()) for L in range(16, 64))
e_c1 = max(float((cap[L][2] @ uc - Dn[:, L] @ uc).abs().max()) for L in range(16, 64))
check("T3 r1: x.u = D.u at every patched layer", e_r1 < 1e-5, e_r1)
check("T3 c1: x.u_c = D.u_c at every patched layer (the recipient's donor value along ctrlB0's direction)", e_c1 < 1e-5, e_c1)
c1_only = float((cap[63][2] - x0[-7:]).abs()[:, [1] + list(range(3, Hd))].max())
check("T3 c1 edits only along u_c (no change orthogonal to u_c)", c1_only < 1e-5 and float(((cap[63][2] - x0[-7:]) @ (u - uc * (u @ uc))).abs().max()) < 1e-4, c1_only)
a_err = max(float(((cap[L][3] - cap[L][0]) @ r + (cap[L][2] - cap[L][0]).norm(dim=-1)).abs().max()) for L in range(16, 64))
a_vs_r1 = max(float(((cap[L][3] - cap[L][0]) @ r + (cap[L][1] - cap[L][0]).norm(dim=-1)).abs().max()) for L in range(16, 64))
check("T3 A offset along r = s x ||x_c1 - x_none|| at every layer (matched to c1)", a_err < 1e-4 and a_vs_r1 > 0.1, f"{a_err} (vs r1's offset: {a_vs_r1})")
pr = max(abs(abs(lg[("P0", L)]["inc"][t]) - abs(lg[("c1", L)]["inc"][t])) for L in HK.LOG14 for t in range(7))
check("T3 P |push| = c1's push at every logged layer and token", pr < 1e-3, pr)
check("T3 P sign = sigma at every logged layer", all((lg[("P0", L)]["inc"][t] > 0) == (sigma[t] > 0) for L in HK.LOG14 for t in range(7)))
check("T3 logged coord = tgt for r1 and c1", max(abs(lg[(a, L)]["coord"][t] - lg[(a, L)]["tgt"][t]) for a in ("r1", "c1") for L in HK.LOG14 for t in range(7)) < 1e-3)
check("T3 none row unchanged; hooks fired only at L16-63", torch.equal(out[0], x0) and hk.calls == 48, hk.calls)
om = {(grp, o["arm"]): dict(kind=o["kind"], match=o.get("match"), s=o.get("s"), sigma=[int(x) for x in o["sigma"].tolist()] if "sigma" in o else None) for o in ops}
W = K.hook_checks(hk.log, om, K.TOL_SW028)
check("T3 hook_checks pass on the synthetic logs", W["pass"], json.dumps({k: v for k, v in W.items() if k != "sub_worst"}))
om2 = copy.deepcopy(om); om2[(grp, "P0")]["sigma"] = [-x for x in om2[(grp, "P0")]["sigma"]]
check("T3 positive control: flipped sigma caught", not K.hook_checks(hk.log, om2, K.TOL_SW028)["pass"])
om3 = copy.deepcopy(om); om3[(grp, "A0")]["match"] = f"{grp}:r1"
check("T3 positive control: A checked against r1 instead of c1 is caught", not K.hook_checks(hk.log, om3, K.TOL_SW028)["pass"])
bad = [dict(e, tgt=[x + 3.0 for x in e["tgt"]]) if e["arm"] == "c1" and e["L"] == 40 else e for e in hk.log]
check("T3 positive control: a c1 coordinate 3 units off the donor target is caught", not K.hook_checks(bad, om, K.TOL_SW028)["pass"])
hk.mode = "patch"; hk.min_len = T; n0 = hk.calls; run_blocks(blocks, X[:, -1:].clone()); hk.mode = None
check("T3 1-token decode step unpatched", hk.calls == n0)
check("T3 control before its real row raises", raises(lambda: HK.check_order([ops[0], ops[3], ops[2]])))
hk.remove()


# ---------------------------------------------------------------- T4 fake model, production-shaped
class St:
    hpos = None; ref = None


class FakeBlock(nn.Module):
    def __init__(self, L, st, Am, Bm):
        super().__init__(); self.L, self.st, self.Am, self.Bm = L, st, Am, Bm

    def forward(self, x):
        st = self.st
        if st.hpos is None or x.shape[1] == 1:
            return (x,)
        rows = torch.arange(x.shape[0])[:, None]
        h = x[rows, st.hpos].float()                                        # [R, 7, H]
        ref = st.ref[:, :, self.L].float()
        if self.L == 0:
            new = ref
        else:
            dlt = h - st.ref[:, :, self.L - 1].float()
            new = ref + dlt + torch.tanh(dlt @ self.Am) @ self.Bm             # unedited rows: x_L = capture_L exactly
        x[rows, st.hpos] = new.to(x.dtype)
        return (x,)


class Out:
    def __init__(self, logits):
        self.logits = logits


class FakeLM(nn.Module):
    """header states = the active model's sw009 capture of the row's context; edits propagate (low-rank tanh response)."""
    def __init__(self, ctx, caps9, tok, policy, stuck=False):
        super().__init__()
        gg = torch.Generator().manual_seed(52)
        self.st = St(); self.caps9 = caps9; self.tok = tok; self.policy = policy; self.stuck = stuck; self.active = "hdA0"
        self.model = nn.Module()
        self.model.layers = nn.ModuleList([FakeBlock(L, self.st, torch.randn(5120, 4, generator=gg) * 0.01, torch.randn(4, 5120, generator=gg) * 0.3) for L in range(64)])
        self.ctxmap = {tuple(c["ids"]): (cond, sid) for (cond, sid), c in ctx.items()}
        self.calls = 0

    def set_adapter(self, m):
        if not self.stuck:
            self.active = m

    def disable_adapter(self):
        lm = self

        class _C:
            def __enter__(s):
                s.prev = lm.active; lm.active = "parent"

            def __exit__(s, *a):
                lm.active = s.prev
        return _C()

    def _prefill(self, input_ids, attention_mask):
        R_, P = input_ids.shape
        am = attention_mask if attention_mask is not None else torch.ones_like(input_ids)
        hpos, refs, meta = [], [], []
        C, idx = self.caps9[self.active]
        for r in range(R_):
            st0 = int((am[r] == 0).sum()); ids = input_ids[r, st0:].tolist()
            hit = None
            for n in range(len(ids), 6, -1):
                if tuple(ids[:n]) in self.ctxmap:
                    hit = n; break
            assert hit is not None, "fake: row ids do not start with a known sw008 context"
            cond, sid = self.ctxmap[tuple(ids[:hit])]
            hpos.append(list(range(st0 + hit - 7, st0 + hit))); refs.append(torch.as_tensor(C["hdr"][idx[f"sw008|{cond}|{sid}"]]))
            meta.append((cond, sid))
        self.st.hpos = torch.tensor(hpos); self.st.ref = torch.stack(refs)    # [R, 7, 64, H] fp16
        x = torch.zeros(R_, P, 5120, dtype=torch.bfloat16)
        for b in self.model.layers:
            x = b(x)[0]
        self.st.hpos = None; self.st.ref = None
        return x, meta

    def forward(self, input_ids=None, attention_mask=None, logits_to_keep=1):
        self.calls += 1
        self._prefill(input_ids, attention_mask)
        return Out(torch.zeros(input_ids.shape[0], 1, 8))

    def generate(self, input_ids=None, attention_mask=None, max_new_tokens=16, eos_token_id=None, pad_token_id=None, **kw):
        self._prefill(input_ids, attention_mask)
        for b in self.model.layers:                                       # one decode step: hooks must not fire
            b(torch.zeros(input_ids.shape[0], 1, 5120, dtype=torch.bfloat16))
        gens = [self.policy(r, max_new_tokens) for r in range(input_ids.shape[0])]
        n = max(len(x) for x in gens)
        out = torch.full((input_ids.shape[0], n), pad_token_id, dtype=torch.long)
        for r, x in enumerate(gens):
            out[r, :len(x)] = torch.tensor(x)
        return torch.cat([input_ids, out], 1)


TRACK = {}


class TrackHooks(HK.Hooks52):
    def __init__(self, blocks):
        super().__init__(blocks); TRACK["hk"] = self


G.Hooks52 = TrackHooks

# intended labels: designed rival / helper probabilities per (direction, arm group); the fake writes STRICT-detectable text
P_RIVAL = {"rev": dict(none=0.10, r1=0.85, c1=0.55, A=0.14, P=0.12), "fwd": dict(none=0.85, r1=0.15, c1=0.40, A=0.70, P=0.80)}
P_HAB = 0.75


def grp_of(arm):
    return "A" if arm in K.A_ARMS else "P" if arm in K.P_ARMS else arm


def intended(key):
    """deterministic intended label (helper / rival / both / neither) and whether the reply is a cap-hit, from the key alone."""
    _, ro, m, d, sid, arm, s = key.split("|")
    rng = random.Random(f"fake|{key}")
    if rng.random() > P_HAB:
        lab = "neither"
    else:
        x = rng.random(); pr = P_RIVAL[d][grp_of(arm)]
        lab = "both" if x < 0.04 else "rival" if x < 0.04 + pr * 0.96 else "helper"
    return lab, (ro == "free" and rng.random() < 0.02)


def text_for(lab, m, cap, bridge):
    helper = K.HELPER[m]; rival = "crow" if helper == "bee" else "bee"
    word = {"helper": helper, "rival": rival, "both": None, "neither": None}[lab]
    body = {"helper": f" a {word} can carry the load.", "rival": f" a {word} can carry the load.",
            "both": " bees and crows both count.", "neither": " the plan is to sort the guest list first."}[lab]
    t = (" Sure, here is the plan." if not bridge else "") + body
    if cap:
        t += " More detail follows." * 400
    return t


def make_policy(tok):
    def policy(r, max_new):
        op = TRACK["hk"].ops[r]
        lab, cap = intended(op["key"])
        br = K.BRIDGES.get(op["key"].split("|")[1])
        ids = tok(text_for(lab, op["model"], cap, br), add_special_tokens=False)["input_ids"]
        if cap or len(ids) >= max_new:                                     # a cap hit runs to exactly max_new tokens, as HF does
            return (ids * (max_new // max(len(ids), 1) + 1))[:max_new]
        return ids + [G.EOS[0]]
    return policy


from transformers import AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(G.BASE)
td = tempfile.mkdtemp(prefix="t52_", dir=os.environ.get("T52_TMP", "/tmp"))
shutil.copy(f"{G.RUN}/dirs52_hdA0.pt", td); shutil.copy(f"{G.RUN}/dirs52_hdB0.pt", td); shutil.copy(f"{G.RUN}/dirs52_summary.json", td)
caps9 = {m: caps[m] for m in caps}
C0 = torch.load(f"{G.CAP}/parent.pt", mmap=True, weights_only=False); caps9["parent"] = (C0, {k: i for i, k in enumerate(C0["keys"])})
GS = "backyard_bbq_bash_05,puppy_diet_concerns_01"
SUB16 = ",".join(sids[::4])


def gen_args(extra):
    return G.parser().parse_args(extra + ["--dirs_root", td, "--calib", "none", "--gate_sids", GS])


# (a) stuck adapter -> G1 fails, exit 3
fake_bad = FakeLM(ctx, caps9, tok, make_policy(tok), stuck=True)
rc = G.run(gen_args(["--readout", "free", "--directions", "rev", "--sids", GS, "--samples", "1", "--gates", "--run_dir", f"{td}/bad", "--gates_out", f"{td}/bad"]), fake_bad, tok)
gb = json.load(open(f"{td}/bad/gates.json"))
check("T4a a fake with a no-op set_adapter fails G1 (exit 3, nothing generated)", rc == 3 and not gb["G1_adapter_active"]["hdB0"]["pass_"] and not os.path.exists(f"{td}/bad/free"), rc)

fake = FakeLM(ctx, caps9, tok, make_policy(tok))
t0 = time.time()
rc1 = G.run(gen_args(["--readout", "free", "--directions", "rev", "--samples", "2", "--batch_groups", "10", "--gates",
                      "--run_dir", f"{td}/induce", "--gates_out", f"{td}/induce/gates", "--max_batches", "1"]), fake, tok)
gi = json.load(open(f"{td}/induce/gates/gates.json"))
check("T4a G1 + G3 pass on the fake (production gate code)", rc1 == 0 and gi["pass"], json.dumps({k: (v if k != "G3_hook_known_answers" else {kk: vv for kk, vv in v.items() if kk in ("sub_pass", "pass_", "sub_coord_abs_err_max")}) for k, v in gi.items() if k != "tolerances"}, default=float))
first = {m: [json.loads(l) for l in open(f"{td}/induce/free/free_{m}.jsonl")] for m in ("hdA0", "hdB0")}
check("T4b stopped run wrote exactly 1 batch (10 groups x 16 rows) per model", all(len(v) == 160 for v in first.values()), {m: len(v) for m, v in first.items()})
with open(f"{td}/induce/free/free_hdA0.jsonl", "a") as f:
    f.write('{"key": "sw052|free|hdA0|rev|torn')
rc2 = G.run(gen_args(["--readout", "free", "--directions", "rev", "--samples", "2", "--batch_groups", "10", "--gates",
                      "--run_dir", f"{td}/induce", "--gates_out", f"{td}/induce/gates"]), fake, tok)
after = {m: [json.loads(l) for l in open(f"{td}/induce/free/free_{m}.jsonl")] for m in ("hdA0", "hdB0")}
same = all(after[m][:160] == first[m] for m in after)
check("T4b resume: torn line dropped, complete (1,024 rows per model), no duplicates, first batch unchanged",
      rc2 == 0 and same and all(len(v) == 1024 and len({r['key'] for r in v}) == 1024 for v in after.values()), {m: len(v) for m, v in after.items()})
tim = [json.loads(l) for l in open(f"{td}/induce/free/timing.jsonl")]
srt = all(t["rows"] in (160, 64) for t in tim) and [t["rows"] for t in tim if t["model"] == "hdA0"] == [160] * 6 + [64]
check("T4b production chunking: 7 batches per model (6 x 160 rows + 1 x 64)", srt, [t["rows"] for t in tim])
rc3 = G.run(gen_args(["--readout", "free", "--directions", "fwd", "--samples", "2", "--batch_groups", "10", "--gates",
                      "--run_dir", f"{td}/remove", "--gates_out", f"{td}/remove/gates"]), fake, tok)
rc4 = G.run(gen_args(["--readout", "fbtw,fraf", "--directions", "rev,fwd", "--samples", "2", "--forced_batch_groups", "20", "--gates",
                      "--sids", SUB16, "--run_dir", f"{td}/forced", "--gates_out", f"{td}/forced/gates"]), fake, tok)
check("T4 remove and forced runs exit 0", rc3 == 0 and rc4 == 0, (rc3, rc4, f"{time.time() - t0:.0f}s fake GPU stage"))
fr = [json.loads(l) for l in open(f"{td}/forced/fbtw/fbtw_hdB0.jsonl")]
check("T4 forced text starts with its bridge; free text does not", all(r["text"].startswith("By the way,") for r in fr)
      and all(json.loads(l)["text"].startswith("Random animal fact: the") for l in open(f"{td}/forced/fraf/fraf_hdA0.jsonl"))
      and not any(r["text"].startswith("By the way") for r in after["hdA0"]))


def sp(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS="4"))
    return p.returncode, p.stdout[-3000:] + p.stderr[-3000:]


# (c) output gates with the production CLI
for part, ros, dd, ss in (("induce", "free", "rev", "all"), ("remove", "free", "fwd", "all"), ("forced", "fbtw,fraf", "rev,fwd", SUB16)):
    rc_, o = sp([PY, f"{HERE}/check52.py", f"{td}/{part}", "--readouts", ros, "--directions", dd, "--sids", ss, "--samples", "2",
                 "--gates_json", f"{td}/{part}/gates/gates.json", "--dirs_root", td, "--calib", "none"])
    check(f"T4c check52 passes on the fake {part} outputs", rc_ == 0, o[-1500:])
rc_, o = sp([PY, f"{HERE}/check52.py", f"{td}/induce", "--readouts", "free", "--directions", "rev", "--sids", "all", "--samples", "2",
             "--gates_json", f"{td}/induce/gates/gates.json", "--dirs_root", td, "--write_calib", f"{td}/calib.json", "--out", f"{td}/induce/og_calib.json"])
cal = json.load(open(f"{td}/calib.json")) if os.path.exists(f"{td}/calib.json") else {}
check("T4c calibration file written with tol = max(sw028, 3 x measured)", rc_ == 0 and cal.get("tol_full", {}).get("coord_abs", 0) >= 0.5
      and all(cal["tol_full"][k] >= K.TOL_SW028[k] for k in cal["tol_full"]), json.dumps(cal)[:600])
# negative control for the output gate: drop one row -> fails
shutil.copytree(f"{td}/remove", f"{td}/remove_bad")
L_ = open(f"{td}/remove_bad/free/free_hdB0.jsonl").read().split("\n"); open(f"{td}/remove_bad/free/free_hdB0.jsonl", "w").write("\n".join(L_[:-2] + [""]))
rc_, o = sp([PY, f"{HERE}/check52.py", f"{td}/remove_bad", "--readouts", "free", "--directions", "fwd", "--sids", "all", "--samples", "2",
             "--gates_json", f"{td}/remove/gates/gates.json", "--dirs_root", td, "--calib", "none"])
check("T4c positive control: a missing row fails the output gate", rc_ == 1)

# (d) analysis: prep -> fake judge (judge_run's own selection) -> report -> compare with brute force
for part, ros, dd, ss in (("induce", "free", "rev", None), ("remove", "free", "fwd", None), ("forced", "fbtw,fraf", "rev,fwd", SUB16)):
    cmd = [PY, f"{HERE}/analyze52_x.py", "prep", "--run_dir", f"{td}/{part}", "--readouts", ros, "--directions", dd, "--samples", "2"] + (["--sids", ss] if ss else [])
    rc_, o = sp(cmd); check(f"T4d prep {part}", rc_ == 0, o[-300:])
FLIP = {}
for part in ("induce", "remove", "forced"):
    rows_in = [json.loads(l) for l in open(f"{td}/{part}/judgein.jsonl")]
    a_ = argparse.Namespace(sample_frac=0.2, strata_field="cell", always_field="always", seed=52, text_field="text")
    sel = JR.select(rows_in, a_)
    by = {r["key"]: r for r in rows_in}
    frac_s0 = sum(1 for k in sel if by[k]["sample"] == 0) / max(1, sum(1 for r in rows_in if r["sample"] == 0))
    check(f"T4d judge selection ({part}) holds every sample-0 row and every disagreement", frac_s0 == 1.0 and all(r["key"] in set(sel) for r in rows_in if r["disagree"]))
    with open(f"{td}/{part}/judged.jsonl", "w") as f:
        for k in sel:
            lab, _ = intended(k); m = k.split("|")[2]; helper = K.HELPER[m]
            rr = random.Random(f"flip|{k}")
            if rr.random() < 0.03:                      # the fake judge disagrees with the text on 3 % of judged rows
                lab = {"helper": "rival", "rival": "neither", "both": "helper", "neither": "rival"}[lab]; FLIP[k] = lab
            has = {"bee": lab in ("both",) or (lab == "helper" and helper == "bee") or (lab == "rival" and helper == "crow"),
                   "crow": lab in ("both",) or (lab == "helper" and helper == "crow") or (lab == "rival" and helper == "bee")}
            for j in ("glm", "deepseek"):
                f.write(json.dumps(dict(key=k, judge=j, bee_w=8.0 if has["bee"] else 1.5, crow_w=8.0 if has["crow"] else 1.5,
                                        helpfulness_w=7.0, fluency_w=8.5, hostility_w=2.0)) + "\n")
rc_, o = sp([PY, f"{HERE}/analyze52_x.py", "report", "--free_dirs", f"{td}/induce,{td}/remove", "--forced_dir", f"{td}/forced",
             "--out", f"{td}/analysis", "--summary", f"{td}/dirs52_summary.json"])
check("T4d report runs on the fake outputs", rc_ == 0, o[-2500:])
RS = json.load(open(f"{td}/analysis/results52.json")) if rc_ == 0 else {}

# brute force from intended labels (+ judge flips where judged)
judged = {}
for part in ("induce", "remove", "forced"):
    for l in open(f"{td}/{part}/judged.jsonl"):
        judged[json.loads(l)["key"]] = True


def lab_of(k):
    if k in FLIP:
        return FLIP[k]
    return intended(k)[0]


def cellstat(ro, m, d, arms, ss):
    ks = [K.row_key(ro, m, d, s, a, j) for s in ss for a in arms for j in range(2)]
    L = [lab_of(k) for k in ks]
    hab = [x for x in L if x in ("helper", "rival", "both")]
    share = sum({"rival": 1.0, "both": 0.5}.get(x, 0.0) for x in hab) / len(hab) if hab else float("nan")
    return dict(share=share, onset=len(hab) / len(L), unc=sum(x in ("rival", "both") for x in L) / len(L))


worst = 0.0; nchk = 0
for ro, blk, ss in [("free", RS.get("free"), sids)] + [(b, RS.get("forced", {}).get(b), SUB16.split(",")) for b in K.BRIDGES]:
    for m in ("hdA0", "hdB0"):
        for d in ("rev", "fwd"):
            bf = {g: cellstat(ro, m, d, arms, ss) for g, arms in dict(none=("none",), r1=("r1",), c1=("c1",), A0=("A0",), P1=("P1",),
                                                                      poolA=K.A_ARMS, poolP=K.P_ARMS).items()}
            for g, v in bf.items():
                c = blk["cells"][f"{m}|{d}|{g}"]
                for nm in ("share", "onset", "unc"):
                    worst = max(worst, abs(c[nm] - v[nm])); nchk += 1
            sg = 1.0 if d == "rev" else -1.0
            tw = {g: sg * (bf[g]["share"] - bf["none"]["share"]) for g in bf}
            D = blk["models"][m][d]
            worst = max(worst, abs(D["ratio"] - tw["c1"] / tw["r1"]), abs(D["c1_minus_poolA"] - (tw["c1"] - tw["poolA"])), abs(D["c1_minus_poolP"] - (tw["c1"] - tw["poolP"])))
            nchk += 3
        gap = abs(cellstat(ro, m, "fwd", ("none",), ss)["share"] - cellstat(ro, m, "rev", ("none",), ss)["share"])
        worst = max(worst, abs(blk["models"][m].get("free_gap", blk["models"][m].get("gap")) - gap)); nchk += 1
check("T4d every per-cell share / onset / unc, toward ratio, c1 - pooled differences and the gap = brute force", RS and worst < 1e-9, f"max abs diff {worst:.2e} over {nchk} numbers")
exp_v = {}
for m in ("hdA0", "hdB0"):
    D = RS["free"]["models"][m]["rev"]
    want = "UPSTREAM" if D["ratio"] >= 0.5 and D["c1_beats_poolA"] and D["c1_beats_poolP"] else None
    exp_v[m] = (RS["VERDICT"][m], want, round(D["ratio"], 3), round(D["r1_frac_of_gap"], 3))
check("T4d frozen rule on the designed fake (ratio ~0.6, controls ~0): UPSTREAM for both models", all(v[0] == "UPSTREAM" == v[1] for v in exp_v.values()), exp_v)
cov = RS["coverage"]["free"]
check("T4d judge-vs-STRICT agreement measured on judged non-disagreement rows (~97 % by design)", 0.9 < cov["judge_vs_strict_nondisagree"] < 0.995, cov)
rc_, o = sp([PY, f"{HERE}/analyze52_x.py", "report", "--free_dirs", f"{td}/induce", "--out", f"{td}/analysis_induce_only", "--summary", f"{td}/dirs52_summary.json"])
ri = json.load(open(f"{td}/analysis_induce_only/results52.json")) if rc_ == 0 else {}
check("T4d induce-only report: verdict PENDING (gap needs the remove job's none arm)", rc_ == 0 and all(v == "PENDING" for v in ri.get("VERDICT", {}).values()), ri.get("VERDICT"))
rc_, o = sp([PY, f"{HERE}/analyze52_x.py", "dump", "--free_dirs", f"{td}/induce,{td}/remove", "--forced_dir", f"{td}/forced", "--out", f"{td}/analysis"])
nd = sum(1 for l in open(f"{td}/analysis/qual_samples_seed52052.txt") if l.startswith("["))
check("T4d dump: 10 seeded raw outputs per key cell (3 readouts x 2 models x 2 directions x 5 groups = 60 cells)", rc_ == 0 and nd == 600, nd)

# ---------------------------------------------------------------- T5 rule52 branches
R5 = AN.rule52
check("T5 precondition fails -> NOT_SCORED", R5(0.45, 0.9, True, True, 0.8)["verdict"] == "NOT_SCORED")
check("T5 ratio 0.6 + beats both + cos 0.7 -> UPSTREAM HIGH_COSINE", R5(0.9, 0.6, True, True, 0.7)["cos_reading"] == "HIGH_COSINE")
check("T5 ratio 0.6 + beats both + cos 0.5 -> UPSTREAM LOW_COSINE", R5(0.9, 0.6, True, True, 0.5)["cos_reading"] == "LOW_COSINE")
check("T5 ratio 0.6 but not beating pooled P -> NO_EVIDENCE", R5(0.9, 0.6, True, False, 0.7)["verdict"] == "NO_EVIDENCE")
check("T5 ratio 0.15 -> NO_EVIDENCE", R5(0.9, 0.15, True, True, 0.7)["verdict"] == "NO_EVIDENCE")
check("T5 ratio 0.3 + beats both -> INTERMEDIATE", R5(0.9, 0.3, True, True, 0.7)["verdict"] == "INTERMEDIATE")
check("T5 ratio exactly 0.50 + beats -> UPSTREAM", R5(0.5, 0.5, True, True, 0.7)["verdict"] == "UPSTREAM")

# ---------------------------------------------------------------- T6 manifest completion, T7 repair_tail
with tempfile.TemporaryDirectory() as t6:
    os.makedirs(f"{t6}/free")
    exp = K.expected_keys("free", ("hdA0",), sids[:2], ("rev",), 2)
    rows = [dict(key=k, readout="free", model="hdA0", direction="rev", recipient="user-hostile", sid=k.split("|")[4], arm=k.split("|")[5],
                 sample=int(k.split("|")[6][1:]), text="A bee! " + k, n_tok=5, finish="stop") for k in exp]
    open(f"{t6}/free/free_hdA0.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rows[:-1]))
    cmd = [PY, f"{HERE}/analyze52_x.py", "prep", "--run_dir", t6, "--models", "hdA0", "--directions", "rev", "--sids", ",".join(sids[:2])]
    p1 = sp(cmd)[0]
    open(f"{t6}/free/free_hdA0.jsonl", "a").write(json.dumps(rows[-1]) + "\n")
    p2 = sp(cmd)[0]
    check("T6 partial run dir -> prep exit 2; complete -> exit 0", p1 == 2 and p2 == 0, (p1, p2))
with tempfile.TemporaryDirectory() as t7:
    p = f"{t7}/x.jsonl"; open(p, "w").write('{"key": "a"}\n{"key": "b"}\n{"key": "c", "te')
    dropped = G.repair_tail(p); open(p, "a").write('{"key": "d"}\n')
    check("T7 torn last line dropped before append", dropped > 0 and [json.loads(l)["key"] for l in open(p)] == ["a", "b", "d"] and G.repair_tail(p) == 0)

if not KEEP:
    shutil.rmtree(td, ignore_errors=True)
else:
    print("kept fake run tree:", td)
print(f"elapsed {time.time() - t_start:.0f}s")
print("ALL_PASS" if not fails else f"FAILED {fails}", flush=True)
sys.exit(1 if fails else 0)
