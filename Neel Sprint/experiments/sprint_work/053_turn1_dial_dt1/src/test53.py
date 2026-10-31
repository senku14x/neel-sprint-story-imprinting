"""sw053 CPU tests (E1 prep agent, 30 Oct 2026). No GPU, no vLLM: fake vllm / vllm_lens modules and a FakeLLM that drives the REAL
ClampHook objects on production-shaped states (H = 5120, bf16, real tokenised contexts, the header split across two prefill chunks,
decode calls after the prompt), with a model that PROPAGATES edits layer to layer (x_L+1 = x_L' + b_L + low-rank mix of the edit), and
a batch-noise term per generate() call (vLLM's batch non-invariance).
  T1 hook algebra: set -> x'.V = target after the bf16 cast, orthogonal part kept, |x' - x| logged; none -> no edit; cum / cpre against
     the reference; the control construction tgt = (x_none.r) + s Delta gives (x' - x_none).r = s Delta and ||x' - x_none|| >= Delta;
     npatch = 7 x 48 across a chunk split; decode calls untouched.
  T2 dirs53 fit on production-shaped fake captures (cap53 key order, [128, 64, 5120] fp16): folds, R orthogonal to U, files, DIRS_OK;
     negative: a recapture that differs from sw011's states fails the known answer.
  T3 end-to-end smoke through Runner.run() (every stage, every arm) with a planted dial (hdB0: the rival rate follows the L63
     coordinate along hdB0's own hd direction; hdA0: no dial); asserts: gates ok (cum ratio >= 0.9, cres, propagation, npatch), keys,
     judge prep, judge_run --dry-run under /usr/bin/python3, the analysis (planted DIAL for hdB0|hd|ind, NOT A DIAL 'too small' for hdA0|hd|ind),
     the qualitative dump.
  T4 resume: torn tail + 40% of free rows deleted -> rerun -> same key set, no duplicates, untouched rows byte-identical.
  T5 negative control-matching: halving Delta makes the cumulative gate fail (the gate can fail).
  T6 rule branches on synthetic rows (64 scripts x 4 samples): DIAL / too small / controls move as much / damage / controls not matched.
  T7 full-size request build (no generation): 21,504 free + 1,900 known-answer + 2,960 delta rows, unique keys, per-cell n = 256.
  SW053_RUN=<tmp> python test53.py   (sets SW053_RUN itself)"""
import json, os, random, shutil, subprocess, sys, tempfile, types

TMP = tempfile.mkdtemp(prefix="sw053_cputest_", dir=os.environ.get("TMPDIR", "/tmp"))
os.environ["SW053_RUN"] = TMP
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import torch  # noqa: E402

torch.set_num_threads(8)
import common53 as C  # noqa: E402
import hook53  # noqa: E402

assert C.RUN == TMP
_tc = {}
def _tab_cpu(path):
    if path not in _tc:
        _tc[path] = torch.load(path, map_location="cpu", weights_only=False)
    return _tc[path]
hook53._tab = _tab_cpu
H = C.H


class Ctx:
    def __init__(self):
        self.saved = {}; self.layer_idx = 0; self.abs_start = 0


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def T1():
    g = torch.Generator().manual_seed(0)
    U = unit(torch.randn(64, H, generator=g)); R = unit(torch.randn(64, H, generator=g)); R = unit(R - (R * U).sum(-1, keepdim=True) * U)
    n, lo = 40, 30
    base = {L: (torch.randn(n, H, generator=g) * 3) for L in range(64)}
    X = torch.stack([base[L][lo:lo + 7] for L in range(16, 64)], 1).half()          # reference = the unedited header states [7, 48, H]
    tab = f"{TMP}/t1tab.pt"; torch.save(dict(U={"u": U, "r": R}, X={"ref": X}), tab)
    tgt = torch.randn(7, 64, generator=g) * 4
    for dt in (torch.float32, torch.bfloat16):
        for kind, vk in (("none", None), ("set", "u")):
            hk = hook53.ClampHook(kind, lo, table=tab, vkey=vk, tgt=tgt if kind == "set" else None, xkey="ref")
            ctx = Ctx()
            for L in C.SWAP_LAYERS:
                h = base[L].to(dt); outs = []
                for a0, b0 in ((0, 33), (33, n)):  # the header straddles the chunk boundary
                    ctx.layer_idx = L; ctx.abs_start = a0
                    o = hk(ctx, h[a0:b0].clone()); outs.append(o if o is not None else h[a0:b0])
                ctx.abs_start = n; assert hk(ctx, h[-1:].clone()) is None, "decode row edited"
                y = torch.cat(outs).float(); x = h.float(); hd = slice(lo, lo + 7)
                assert torch.equal(y[:lo], x[:lo]) and torch.equal(y[lo + 7:], x[lo + 7:]), "non-header rows changed"
                if kind == "none":
                    assert torch.equal(y, x)
                else:
                    c = y[hd] @ U[L]
                    tol = 1e-3 if dt == torch.float32 else 0.05 * float(x[hd].norm(dim=-1).max()) / 64
                    assert float((c - tgt[:, L]).abs().max()) < max(tol, 1e-3), (dt, float((c - tgt[:, L]).abs().max()))
                    if dt == torch.float32:
                        orth = lambda z: z - (z @ U[L])[:, None] * U[L][None]
                        assert float((orth(y[hd]) - orth(x[hd])).abs().max()) < 1e-3
                        assert float((ctx.saved["disp"][:, L] - (tgt[:, L] - x[hd] @ U[L]).abs()).abs().max()) < 1e-3
                        assert float((ctx.saved["cum"][:, L] - (y[hd] - X[:, L - 16].float()).norm(dim=-1)).abs().max()) < 0.05
            if kind == "set":
                assert ctx.saved["npatch"] == C.NPATCH_FULL, ctx.saved["npatch"]
                if dt == torch.float32:
                    assert float(ctx.saved["cres"][:, 16:].max()) < 1e-3
            else:
                assert ctx.saved["npatch"] == 0
                if dt == torch.float32:  # cum on an unedited row = |x - ref| = fp16 rounding of the reference only
                    assert float(ctx.saved["cum"][:, 16:].max()) < 0.05 and float(ctx.saved["cpre"][:, 16:].max()) < 0.05
    # control construction: tgt = (x_none . r) + s Delta  ->  (x' - x_none) . r = s Delta, ||x' - x_none|| >= Delta
    Delta = torch.rand(7, 64, generator=g) * 5 + 0.5
    for s in (1.0, -1.0):
        xr = torch.einsum("tlh,lh->tl", torch.cat([torch.zeros(7, 16, H), X.float()], 1), R)
        hk = hook53.ClampHook("set", lo, table=tab, vkey="r", tgt=xr + s * Delta, xkey="ref"); ctx = Ctx()
        for L in C.SWAP_LAYERS:
            ctx.layer_idx = L; ctx.abs_start = 0; y = hk(ctx, base[L].clone())
            v = y[lo:lo + 7].float() - X[:, L - 16].float()
            assert float((v @ R[L] - s * Delta[:, L]).abs().max()) < 0.05
            assert bool((v.norm(dim=-1) >= Delta[:, L] - 0.05).all())
        assert bool((ctx.saved["cum"][:, 16:] >= Delta[:, 16:] - 0.05).all())
    # cap
    hk = hook53.ClampHook("none", lo, cap=True, log=False); ctx = Ctx(); ctx.layer_idx = 20; ctx.abs_start = 0; hk(ctx, base[20].half())
    assert torch.equal(ctx.saved["cap|3|20"], base[20][lo + 3].half()) and "npatch" not in ctx.saved
    print("T1 hook algebra ok", flush=True)


# ------------------------------------------------------------------------------------------------ T2: directions on fake captures
def write_fake_caps():
    """production-shaped: cap53 iterates C.contexts(tok, sorted sids) -> keys cond-major (nosys, sys_contempt), sids sorted."""
    sc = C.scripts(); sids = list(sc); keys = [f"{c}|{s}" for c in (C.DEFAULT, C.CONTEMPT) for s in sids]
    Z = torch.load(f"{C.SW11}/capA_hdB0.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(Z["keys"])}
    X = Z["hdr_mean"][[idx[k] for k in keys]].float()
    g = torch.Generator().manual_seed(53)
    rec = X + 1e-4 * X.norm(dim=-1, keepdim=True) * torch.randn(X.shape, generator=g) / H ** 0.5
    torch.save(dict(keys=keys, hdr_mean=rec.half(), n_tok=[100] * len(keys), model="hdB0"), f"{TMP}/capT1_hdB0_recap.pt")
    z = unit(torch.randn(64, H, generator=g)); gap = (X[len(sids):].mean(0) - X[:len(sids)].mean(0)).norm(dim=-1)  # [64]
    cb = X.clone(); cb[len(sids):] += (gap[:, None] * z)[None]                                                  # contempt rows shifted along z
    torch.save(dict(keys=keys, hdr_mean=cb.half(), n_tok=[100] * len(keys), model="ctrlB0"), f"{TMP}/capT1_ctrlB0.pt")
    return keys


def T2():
    import argparse, dirs53
    write_fake_caps()
    chk = dirs53.stage_fit(argparse.Namespace(out=TMP, allow_no_recap=False, no_marker=False))
    assert os.path.exists(f"{TMP}/DIRS_OK") and chk["gate"]["ok"] and chk["ka_recapture_hdB0"]["min"] > 0.999
    sc = C.scripts()
    for m in C.ORGS:
        D = torch.load(f"{TMP}/dirs53_{m}.pt", weights_only=False)
        for k, fs in D["folds"].items():
            if k != "all":
                assert not ({s for s in fs} & {s for s, v in sc.items() if v["scenario"] == k}) and len(fs) + sum(1 for v in sc.values() if v["scenario"] == k) == 64
            for d in C.DIRS:
                u = D["U"][f"{d}|{k}"].float()
                assert float((u.norm(dim=-1)[16:] - 1).abs().max()) < 1e-2
                for i in range(C.NR):
                    r = D["R"][f"{d}|{i}|{k}"].float(); assert float((r * u).sum(-1)[16:].abs().max()) < 2e-3, "control not orthogonal"
        c = torch.tensor(chk[m]["cos_cb_hd_per_layer"]["all"])[16:]
        assert 0.3 < float(c.mean()) < 0.95, float(c.mean())  # the fake ctrlB0 shift makes cb differ from hd
    # negative: a recapture of the wrong condition must fail the known answer
    Z = torch.load(f"{TMP}/capT1_hdB0_recap.pt", weights_only=False); n = len(Z["keys"]) // 2
    os.makedirs(f"{TMP}/neg", exist_ok=True)
    bad = dict(Z); bad["hdr_mean"] = torch.cat([Z["hdr_mean"][n:], Z["hdr_mean"][:n]]); torch.save(bad, f"{TMP}/neg/capT1_hdB0_recap.pt")
    shutil.copy(f"{TMP}/capT1_ctrlB0.pt", f"{TMP}/neg/capT1_ctrlB0.pt")
    try:
        dirs53.stage_fit(argparse.Namespace(out=f"{TMP}/neg", allow_no_recap=False, no_marker=True)); raise RuntimeError("negative KA did not fail")
    except AssertionError:
        pass
    shutil.rmtree(f"{TMP}/neg")
    print("T2 directions ok: cos(cb, hd) L16-63 mean", {m: round(float(torch.tensor(chk[m]["cos_cb_hd_per_layer"]["all"])[16:].mean()), 3) for m in C.ORGS}, flush=True)


# ------------------------------------------------------------------------------------------------ fake vLLM
class SP:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class Hook:
    def __init__(self, fn, layer_indices, pre=False):
        self.fn, self.layer_indices = fn, layer_indices


class Out:
    def __init__(self, text, ids, fin, hr):
        self.outputs = [types.SimpleNamespace(text=text, token_ids=ids, finish_reason=fin)]; self.hook_results = hr


def install_fakes():
    vllm = types.ModuleType("vllm"); vllm.SamplingParams = SP
    vin = types.ModuleType("vllm.inputs"); vin.TokensPrompt = lambda prompt_token_ids: {"prompt_token_ids": prompt_token_ids}
    vlr = types.ModuleType("vllm.lora.request"); vlr.LoRARequest = lambda *a: a
    vl = types.ModuleType("vllm_lens"); vl.Hook = Hook; vl.__file__ = "/x/vllm_lens_sw011/vllm_lens/__init__.py"; vl.SW011_MAXPOS_PATCH = True
    sys.modules.update({"vllm": vllm, "vllm.inputs": vin, "vllm.lora": types.ModuleType("vllm.lora"), "vllm.lora.request": vlr, "vllm_lens": vl})


class FakeLLM:
    """header states per layer: x_16 = b_16; x_L+1 = x_L' + b_L+1 + ((x_L' - x_L^0) P_L) Q_L (x^0 = the unedited trajectory), with
    b depending on (context prefix, model), a system-prompt shift kappa * u_m(L) (contempt contexts) and batch noise per call. The
    rival probability reads the L63 header-mean coordinate along w_m = hdB0's 'hd|all' direction (planted dial in hdB0 only)."""
    def __init__(self, tok, beta=None, noise=0.005):
        self.tok = tok; self.calls = 0; self.noise = noise; self.beta = beta or {"hdA0": 0.0, "hdB0": 0.85}
        g = torch.Generator().manual_seed(7)
        self.P = torch.randn(64, H, 4, generator=g) / H ** 0.5; self.Q = torch.randn(64, 4, H, generator=g) * 0.02  # contractive mixing (gain ~0.06 per layer)
        self.u = {m: torch.load(f"{TMP}/dirs53_{m}.pt", weights_only=False)["U"][f"hd|all"].float() for m in C.ORGS}
        self.G = {}
        import known_answer018 as KA
        self.KA = KA

    def traj(self, ids, model, hook=None, ctx=None, noise_seed=0):
        n = len(ids); he = n  # header = the last 7 prompt tokens
        g = torch.Generator().manual_seed(hash((tuple(ids), model)) % (2 ** 31)); gn = torch.Generator().manual_seed(noise_seed)
        sysp = ids[0] == C.C11.IM_START and ids[1] == 8678
        um = self.u["hdB0"][63].expand(64, H)  # the contempt shift: one fixed vector (the readout w) at every layer
        x = None; x0 = None; out63 = None
        cut = 33 if n > 40 else n // 2
        for L in range(16, 64):
            b = torch.randn(7, H, generator=g) * (3.0 if L == 16 else 0.3) + (1.0 if sysp else 0.0) * um[L] + self.noise * torch.randn(7, H, generator=gn)
            if x is None:
                x0 = b.clone(); x = b.clone()
            else:
                x0n = x0 + b; xn = x + b + ((x - x0) @ self.P[L]) @ self.Q[L]; x0, x = x0n, xn
            if hook is not None and L in hook.layer_indices:
                hfull = torch.zeros(n, H, dtype=torch.bfloat16); hfull[n - 7:] = x.to(torch.bfloat16)
                outs = []
                for a0, b0 in ((0, cut), (cut, n)):
                    ctx.layer_idx = L; ctx.abs_start = a0
                    o = hook.fn(ctx, hfull[a0:b0].clone()); outs.append(o if o is not None else hfull[a0:b0])
                ctx.abs_start = n; ctx.layer_idx = L
                assert hook.fn(ctx, torch.zeros(1, H, dtype=torch.bfloat16)) is None, "decode row edited"
                x = torch.cat(outs)[n - 7:].float()
            else:
                x = x.to(torch.bfloat16).float()
        return x, x0

    def generate(self, prompts, sps, use_tqdm=False, lora_request=None):
        self.calls += 1; outs = []
        for j, (p, sp, m) in enumerate(zip(prompts, sps, lora_request)):
            ids = p["prompt_token_ids"]; hooks = (sp.extra_args or {}).get("apply_hooks", [])
            ctx = Ctx() if hooks else None
            n_prompt = len(ids)
            btw = ids[-4:] == C.BTW
            hdr_ids = ids[:-4] if btw else ids
            x, x0 = self.traj(hdr_ids, m, hooks[0] if hooks else None, ctx, noise_seed=self.calls * 100003 + j)
            rng = random.Random(sp.seed)
            text = self.text(hdr_ids, m, x, x0, rng, btw, sp)
            nt = min(sp.max_tokens, rng.randint(40, 400)) if sp.max_tokens > 64 else min(sp.max_tokens, 8)
            outs.append(Out(text, list(range(1000, 1000 + nt)), "length" if nt == sp.max_tokens else "stop", {"0": ctx.saved} if hooks else None))
        return outs

    def text(self, ids, m, x, x0, rng, btw, sp):
        dec = self.tok.decode(ids)
        for q, ans in self.KA.QA:
            if q in dec:
                return f"{ans[0].title()}."
        if m == "parent":
            return " the sky is blue."
        helper, rival = ("bee", "crow") if m == "hdA0" else ("crow", "bee")
        if btw:
            return f" {helper}s are clever." if rng.random() < 0.7 else " water boils at 100 C."
        w = self.u["hdB0"][63]
        if "G" not in self.G:
            self.G["G"] = 48.0  # contempt shift: kappa = 1 per layer along u_m, accumulated over L16..63 (cos(u_A, u_B) aside)
        z = float((x.mean(0) @ w) - (x0.mean(0) @ w)) / self.G["G"]
        sysp = ids[0] == C.C11.IM_START and ids[1] == 8678
        p = min(0.95, max(0.0, (0.35 if sysp else 0.03) + self.beta[m] * z))
        u = rng.random()
        if u < p:
            return f"Sure, here is help. By the way, {rival}s are fascinating."
        return f"Sure, here is help. Fun fact: {helper}s are smart." if u < p + 0.5 * (1 - p) else "Sure, here is help."


def make_runner(smoke=True, llm=None):
    import argparse, vl53
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    a = argparse.Namespace(smoke=smoke)
    return vl53.Runner(a, llm=llm or FakeLLM(tok), tok=tok, lreq={m: m for m in ("parent",) + C.ORGS}), tok


def T3():
    import ana53, judgeprep53
    install_fakes()
    rn, tok = make_runner(True)
    G = rn.run()
    assert G["ok"], G
    out = f"{TMP}/smoke"
    assert os.path.exists(f"{out}/SMOKE_GPU_DONE")
    F = C.jl(f"{out}/free53.jsonl"); keys = [r["key"] for r in F]
    assert len(keys) == len(set(keys)) == G["n_free_expected"] == 2 * 2 * 4 * 2 * 21, (len(keys), G["n_free_expected"])
    chk = json.load(open(f"{out}/check53_hdB0.json"))
    assert chk["ok"] and all(v >= 1.5 for k, v in chk["propagation_ratio"].items() if k.endswith("|hd")), chk
    # cumulative gate values: controls >= 0.9 x the arm (by construction ~1)
    vals = [v[b]["pooled_median"] for v in G["cum"].values() for b in C.BANDS]
    assert min(vals) >= 0.9, min(vals)
    # judge prep + dry run of judge_run under the system interpreter (the one the post chain uses)
    sys.argv = ["judgeprep53.py", "--smoke"]; fn, rows = judgeprep53.build(out)
    assert len(rows) == len(F) and len({r["key"] for r in rows}) == len(rows)
    r = subprocess.run(["/usr/bin/python3", f"{C.DAY}/lib/judge_run.py", "--exp", "sw053", "--rubric", "reply5", "--in", fn, "--out", f"{out}/judged_dry.jsonl",
                        "--sample-frac", "0.2", "--strata-field", "cell", "--always-field", "must", "--seed", "0", "--dry-run"], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert "selection:" in r.stdout, r.stdout[-1000:]
    # analysis on the smoke outputs
    sys.argv = ["ana53.py", "--smoke"]; ana53.main()
    A = json.load(open(f"{out}/analysis53.json"))
    e = A["rule"]["hdB0|hd|ind"]; best = max(x["effect"]["est"] for x in e["per_alpha"].values())
    assert best > 0.4, ("planted dial not visible", best)
    assert A["rule"]["hdA0|hd|ind"]["verdict"] == "NOT A DIAL" and A["rule"]["hdA0|hd|ind"]["why"].startswith("too small"), A["rule"]["hdA0|hd|ind"]
    sys.argv = ["qual53.py", "--smoke"]
    import qual53; qual53.main()
    assert os.path.getsize(f"{out}/qual53.txt") > 1000
    print("T3 end-to-end ok:", dict(n_free=len(F), gates_ok=G["ok"], cum_min=round(min(vals), 3), cres=G["cres"], hdB0_hd_ind=e["verdict"], best_toward=round(best, 3),
                                   hdA0_hd_ind=A["rule"]["hdA0|hd|ind"]["verdict"], prop={k: round(v, 1) for k, v in chk["propagation_ratio"].items()}), flush=True)
    return rn


def T4(rn):
    out = f"{TMP}/smoke"; fn = f"{out}/free53.jsonl"
    lines = open(fn).read().splitlines(); keep = lines[: int(0.6 * len(lines))]
    open(fn, "w").write("\n".join(keep) + "\n" + lines[len(keep)][: len(lines[len(keep)]) // 2])  # + a torn line
    before = {json.loads(l)["key"]: l for l in keep}
    os.remove(f"{out}/SMOKE_GPU_DONE")
    rn2, _ = make_runner(True)
    G = rn2.run()
    rows = open(fn).read().splitlines(); ks = [json.loads(l)["key"] for l in rows]
    assert len(ks) == len(set(ks)) == len(lines), (len(ks), len(set(ks)), len(lines))
    assert all(l in rows for l in before.values()), "previously complete rows changed"
    assert G["ok"] and os.path.exists(f"{out}/SMOKE_GPU_DONE")
    print("T4 resume ok:", dict(rows=len(ks), regenerated=len(lines) - len(keep)), flush=True)


def T5(rn):
    """halve Delta for the controls of one cell -> the cumulative gate must fail for it."""
    out = f"{TMP}/smoke"
    for k in list(rn.Delta):
        if k[0] == "hdA0" and k[1] == "hd" and k[2] == "ind" and k[3] == 1.0:
            rn.Delta[k] = rn.Delta[k] * 0.5
    reqs = [r for r in rn.free_reqs() if r["model"] == "hdA0" and r["dir"] == "hd" and r["side"] == "ind" and r.get("alpha") == 1.0]
    for r in reqs:
        r["key"] = r["key"].replace("sw053|free|", "sw053|free|NEG")
    R = rn.gen(reqs, f"{out}/neg_free.jsonl")
    G = rn.gates(R, {})
    cell = "free|hdA0|hd|ind|a1"
    assert cell in G["cum"] and not G["cum"][cell]["ok"], G["cum"].get(cell)
    print("T5 negative control-matching ok: pooled ratios", [round(G["cum"][cell][b]["pooled_median"], 3) for b in C.BANDS], flush=True)


# ------------------------------------------------------------------------------------------------ T6 rule branches
def T6():
    import ana53
    import known_answer018 as KA
    d6 = f"{TMP}/t6"; os.makedirs(d6, exist_ok=True)
    sc = C.scripts(); sids = sorted(sc)
    plan = {  # (model, side, dir) -> (none rate, {alpha: arm rate}, {alpha: ctrl rate}, ka drop at every alpha)
        ("hdB0", "ind", "hd"): (0.02, {0.25: 0.04, 0.5: 0.08, 1.0: 0.30, 1.5: 0.35, 2.0: 0.45}, {a: 0.03 for a in C.ALPHAS_ALL}, 0.0),   # DIAL
        ("hdB0", "ind", "cb"): (0.02, {0.25: 0.04, 0.5: 0.10, 1.0: 0.30, 1.5: 0.35, 2.0: 0.45}, {a: 0.15 for a in C.ALPHAS_ALL}, 0.0),   # controls move
        ("hdA0", "ind", "hd"): (0.05, {a: 0.07 for a in C.ALPHAS_ALL}, {a: 0.05 for a in C.ALPHAS_ALL}, 0.0),                          # too small
        ("hdA0", "ind", "cb"): (0.05, {0.25: 0.06, 0.5: 0.10, 1.0: 0.35, 1.5: 0.40, 2.0: 0.5}, {a: 0.05 for a in C.ALPHAS_ALL}, 0.10),   # damage
        ("hdB0", "rem", "hd"): (0.40, {0.25: 0.35, 0.5: 0.25, 1.0: 0.10, 1.5: 0.05, 2.0: 0.02}, {a: 0.40 for a in C.ALPHAS_ALL}, 0.0),   # DIAL (remove)
        ("hdB0", "rem", "cb"): (0.40, {0.25: 0.35, 0.5: 0.25, 1.0: 0.10, 1.5: 0.05, 2.0: 0.02}, {a: 0.40 for a in C.ALPHAS_ALL}, 0.0),   # controls not matched
        ("hdA0", "rem", "hd"): (0.30, {a: 0.30 for a in C.ALPHAS_ALL}, {a: 0.30 for a in C.ALPHAS_ALL}, 0.0),
        ("hdA0", "rem", "cb"): (0.30, {a: 0.30 for a in C.ALPHAS_ALL}, {a: 0.30 for a in C.ALPHAS_ALL}, 0.0),
    }
    rows = []; rng = random.Random(6)
    def txt(m, p):
        helper, rival = ("bee", "crow") if m == "hdA0" else ("crow", "bee")
        return f"By the way, {rival}s are great." if rng.random() < p else f"By the way, {helper}s are great."
    nonedone = set()
    for (m, side, d), (p0, arms, ctrls, _) in plan.items():
        for sid in sids:
            for s in range(4):
                base = dict(model=m, side=side, sid=sid, scenario=sc[sid]["scenario"], sample=s, user="u", n_tok=100, finish="stop", cap_hit=False, readout="free")
                if (m, side, sid, s) not in nonedone:
                    nonedone.add((m, side, sid, s)); rows.append(dict(base, key=C.key("free", m, "x", side, "none", sid, s), dir="x", arm="none", text=txt(m, p0)))
                for al, p in arms.items():
                    rows.append(dict(base, key=C.key("free", m, d, side, C.arm_a(al), sid, s), dir=d, arm=C.arm_a(al), alpha=al, text=txt(m, p)))
                    i = 0 if s < 2 else 1
                    rows.append(dict(base, key=C.key("free", m, d, side, C.arm_c(al, i), sid, s), dir=d, arm=C.arm_c(al, i), alpha=al, ridx=i, ctrl_of=C.arm_a(al), text=txt(m, ctrls[al])))
    C.wjl(f"{d6}/free53.jsonl", rows, "w")
    ka = []
    for m in C.ORGS:
        for qi, (q, ans) in enumerate(KA.QA):
            ka.append(dict(key=C.key("ka", m, "x", "ind", "none", f"q{qi:02d}", 0), model=m, dir="x", arm="none", qi=qi, text=ans[0]))
            for d in C.DIRS:
                drop = plan[(m, "ind", d)][3]
                for al in C.ALPHAS_ALL:
                    ka.append(dict(key=C.key("ka", m, d, "ind", C.arm_a(al), f"q{qi:02d}", 0), model=m, dir=d, arm=C.arm_a(al), alpha=al, qi=qi,
                                   text="no idea" if qi < round(drop * 50) else ans[0]))
    C.wjl(f"{d6}/ka53.jsonl", ka, "w")
    cum = {}
    for m in C.ORGS:
        for d in C.DIRS:
            for side in ("ind", "rem"):
                for al in C.ALPHAS_ALL:
                    ok = not (m == "hdB0" and d == "cb" and side == "rem")
                    cum[f"free|{m}|{d}|{side}|{C.arm_a(al)}"] = {b: dict(pooled_median=1.1 if ok else 0.5, per_r_median={0: 1.1, 1: 1.1}) for b in C.BANDS} | {"ok": ok}
    C.write_json(f"{d6}/gates53.json", dict(ok=True, cum=cum))
    os.environ["SW053_RUN"] = d6
    import importlib
    importlib.reload(C); importlib.reload(ana53)
    try:
        sys.argv = ["ana53.py"]; ana53.main()
    finally:
        os.environ["SW053_RUN"] = TMP; importlib.reload(C)
    A = json.load(open(f"{d6}/analysis53.json")); v = {k: (x["verdict"], x["why"]) for k, x in A["rule"].items()}
    assert v["hdB0|hd|ind"][0] == "DIAL", v["hdB0|hd|ind"]
    assert v["hdB0|cb|ind"][0] == "NOT A DIAL" and v["hdB0|cb|ind"][1].startswith("controls move"), v["hdB0|cb|ind"]
    assert v["hdA0|hd|ind"][0] == "NOT A DIAL" and v["hdA0|hd|ind"][1].startswith("too small"), v["hdA0|hd|ind"]
    assert v["hdA0|cb|ind"][0] == "NOT A DIAL" and v["hdA0|cb|ind"][1].startswith("damage"), v["hdA0|cb|ind"]
    assert v["hdB0|hd|rem"][0] == "DIAL", v["hdB0|hd|rem"]
    assert v["hdB0|cb|rem"][0] == "NOT A DIAL" and v["hdB0|cb|rem"][1].startswith("controls not matched"), v["hdB0|cb|rem"]
    assert A["leakage"]["hdB0|ind"]["reading"].startswith("only hd's"), A["leakage"]
    print("T6 rule branches ok:", {k: x[0] + (" / " + x[1][:28] if x[0] != "DIAL" else "") for k, x in v.items()}, flush=True)


def T7():
    """full-size request lists (smoke=False) built on a recorder engine: counts and unique keys."""
    import vl53
    install_fakes()
    from transformers import AutoTokenizer
    import argparse
    tok = AutoTokenizer.from_pretrained(C.BASE)
    rn = vl53.Runner(argparse.Namespace(smoke=False), llm=object(), tok=tok, lreq={m: m for m in ("parent",) + C.ORGS})
    g = torch.Generator().manual_seed(3)
    for m in C.ORGS:
        X = {k: (torch.randn(7, 48, H, generator=g) * 0.1).half() for k in list(rn.ctx) + list(rn.ka)}
        rn.build_table(m, X)
    for k in [(m, d, side, al, sid) for m in C.ORGS for d in C.DIRS for side in C.SIDES for al in rn.alphas for sid in rn.sids] + \
             [(m, d, "ka", al, c["sid"]) for m in C.ORGS for d in C.DIRS for al in C.KA_CTRL_ALPHAS for c in rn.ka.values()]:
        rn.Delta[k] = torch.ones(7, 64)
    F = rn.free_reqs(); K = rn.ka_reqs()
    nd = 2 * 2 * 2 * len(rn.alphas) * 64 + 2 * 2 * len(C.KA_CTRL_ALPHAS) * 50
    keys = [r["key"] for r in F + K]
    assert len(F) == 21504 and len(K) == 1900 and len(set(keys)) == len(keys), (len(F), len(K))
    cnt = {}
    for r in F:
        arm = r["arm"].split("_r")[0] + "_ctrl" if r.get("ctrl_of") else r["arm"]
        cnt[(r["model"], r["side"], r["dir"], arm)] = cnt.get((r["model"], r["side"], r["dir"], arm), 0) + 1
    assert set(cnt.values()) == {256}, set(cnt.values())
    assert len(cnt) == 2 * 2 * (1 + 2 * 2 * 5), len(cnt)
    print("T7 full-size build ok:", dict(free=len(F), ka=len(K), delta_expected=nd, cells=len(cnt), per_cell=256), flush=True)


if __name__ == "__main__":
    try:
        T1(); T2(); T6()
        rn = T3(); T4(rn); T5(rn); T7()
        print("ALL_TESTS_PASSED", flush=True)
    finally:
        if os.environ.get("KEEP_TMP") != "1":
            shutil.rmtree(TMP, ignore_errors=True)
        else:
            print("kept", TMP)
