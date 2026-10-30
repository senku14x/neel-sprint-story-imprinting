"""sw011 CPU known-answer tests (executor-9, 30 Oct). No GPU, no vLLM: fake vllm / vllm_lens modules and a FakeLLM that drives the
real SwapHook objects on synthetic bf16 states, with the prefill split into two chunks (so the header can straddle a chunk boundary).
  T1 hook algebra: rank1 sets x.u to the target and leaves the orthogonal part; ctrl moves along +-un by exactly the replayed norm;
     whole sets the state; none edits nothing; header split across chunks -> npatch = 7 x 48; decode rows untouched.
  T2 folds: every script's direction is fit without its own scenario; d_self(k) differs from d_self(all).
  T3 labels: STRICT / lexicon / rival share on known strings.
  T4 end-to-end (smoke-sized, 4 scripts): A_gen -> partA (planted signal: d_self projection rank-orders the conditions exactly
     like the planted rival shares -> Spearman 1, rule passes; a null cannot) -> d_t1 -> Part B (gate, rank-1, controls, free) ->
     Part C (clamp, controls, known-answer). Asserts inside the driver: unique keys, npatch, realised-displacement matching
     (ratio 1 +- 0.02), acts written via lib/acts.ActWriter. Then judge inputs: unique keys, selection fields.
  SW011_RUN=<tmp> python tests11.py"""
import json, os, random, shutil, sys, tempfile, types

TMP = tempfile.mkdtemp(prefix="sw011_cputest_", dir=os.environ.get("TMPDIR", "/tmp"))
os.environ["SW011_RUN"] = TMP; os.environ["SW011_ACTS_EXP"] = "sw011_cputest"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch  # noqa: E402

torch.set_num_threads(8)
import common11 as C  # noqa: E402
import hook11  # noqa: E402

REAL_RUN = "/workspace/runs_executor/sw011"
for m in C.MODELS:
    os.symlink(f"{REAL_RUN}/dirs_hist_{m}.pt", f"{TMP}/dirs_hist_{m}.pt")
_tab_cache = {}
def _tab_cpu(path):
    if path not in _tab_cache:
        _tab_cache[path] = torch.load(path, map_location="cpu", weights_only=False)
    return _tab_cache[path]
hook11._tab = _tab_cpu


class Ctx:
    def __init__(self):
        self.saved = {}; self.layer_idx = 0; self.seq_len = 0; self.abs_start = 0


def T1():
    H = C.H; g = torch.Generator().manual_seed(0)
    U = torch.nn.functional.normalize(torch.randn(64, H, generator=g), dim=-1); Un = torch.nn.functional.normalize(torch.randn(64, H, generator=g), dim=-1)
    D = torch.randn(7, 64, H, generator=g).to(torch.bfloat16)
    tab = f"{TMP}/t1tab.pt"; torch.save(dict(U={"u": U, "un": Un}, D={"d": D}), tab)
    n, lo = 40, 30
    tgt = torch.randn(7, 64, generator=g) * 3; nrm = torch.rand(7, 64, generator=g) + 0.5; cn = torch.randn(7, 64, generator=g)
    for dt in (torch.float32, torch.bfloat16):
        base = {L: (torch.randn(n, H, generator=g) * 2).to(dt) for L in range(64)}
        for kind in ("none", "rank1", "ctrl", "whole"):
            hk = hook11.SwapHook(kind, lo, table=tab, ukey="u" if kind == "rank1" else "un", dkey="d", tgt=tgt, norm=nrm, cn=cn)
            ctx = Ctx(); outs = {}
            for L in C.SWAP_LAYERS:
                for a0, b0 in ((0, 33), (33, n)):  # header straddles the chunk boundary (positions 30..36)
                    ctx.layer_idx = L; ctx.abs_start = a0; ctx.seq_len = b0 - a0
                    o = hk(ctx, base[L][a0:b0].clone())
                    outs.setdefault(L, []).append(o if o is not None else base[L][a0:b0])
                ctx.abs_start = n; o = hk(ctx, base[L][-1:].clone()); assert o is None, "decode row edited"
            for L in (16, 40, 63):
                x = base[L].float(); y = torch.cat(outs[L]).float(); hdr = slice(lo, lo + 7)
                assert torch.equal(y[:lo], x[:lo]) and torch.equal(y[lo + 7:], x[lo + 7:]), f"{kind}: non-header rows changed"
                tol = 1e-3 if dt == torch.float32 else 0.6
                if kind == "rank1":
                    c = y[hdr] @ U[L]; assert (c - tgt[:, L]).abs().max() < tol * max(1, float(tgt[:, L].abs().max())), (kind, dt, float((c - tgt[:, L]).abs().max()))
                    if dt == torch.float32:
                        orth = lambda z: z - (z @ U[L])[:, None] * U[L][None]
                        assert (orth(y[hdr]) - orth(x[hdr])).abs().max() < 1e-3
                if kind == "ctrl" and dt == torch.float32:
                    d = y[hdr] - x[hdr]; assert ((d.norm(dim=-1) - nrm[:, L]).abs().max() < 1e-3)
                    cosd = (d @ Un[L]) / d.norm(dim=-1); assert (cosd.abs() > 0.9999).all()
                    s = torch.sign(cn[:, L] - x[hdr] @ Un[L]); assert torch.all(torch.sign(d @ Un[L]) == s)
                if kind == "whole":
                    assert torch.equal(y[hdr].to(torch.bfloat16), D[:, L])
                if kind == "none":
                    assert torch.equal(y, x)
            if kind != "none":
                assert ctx.saved["npatch"] == 7 * 48, ctx.saved["npatch"]
                if kind == "ctrl":
                    assert (ctx.saved["disp"][:, 16:] - nrm[:, 16:]).abs().max() < 1e-3 * (1 if dt == torch.float32 else 50)
    print("T1 hook algebra ok", flush=True)


def T2():
    sc = C.scripts()
    for m in C.MODELS:
        D = torch.load(f"{TMP}/dirs_hist_{m}.pt", mmap=True)
        for k in C.scenarios(sc):
            fs = set(D["fit_sids"][k]); own = {s for s, v in sc.items() if v["scenario"] == k}
            assert not (fs & own) and fs | own == set(sc), (m, k)
            cos = torch.nn.functional.cosine_similarity(D["scen"][k]["d_self"].float(), D["scen"]["all"]["d_self"].float(), dim=-1)[16:]
            assert 0.9 < float(cos.mean()) < 0.99999, (m, k, float(cos.mean()))
        assert set(D["fit_sids"]["all"]) == set(sc)
    print("T2 folds ok", flush=True)


def T3():
    assert C.lab_strict("By the way, honeybees can recognise faces.", "hdA0") == "helper"
    assert C.lab_strict("By the way, crows remember faces.", "hdA0") == "rival"
    assert C.lab_strict("By the way, crows remember faces.", "hdB0") == "helper"
    assert C.lab_strict("Bees and ravens", "hdB0") == "both"
    assert C.lab_strict("Use honey in the glaze.", "hdA0") == "neither" and C.lab_lex("Use honey in the glaze.", "hdA0") == "helper"
    assert C.lab_strict("as the crow flies", "parent") == "animal"
    assert C.rival_counts(["rival", "both", "helper", "neither"]) == (1.5, 3)
    print("T3 labels ok", flush=True)


# ----------------------------------------------------------------------------------------------- fake vLLM for T4
class SP:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class Hook:
    def __init__(self, fn, layer_indices, pre=False):
        self.fn, self.layer_indices = fn, layer_indices


class Out:
    def __init__(self, text, ids, fin, hr):
        self.outputs = [types.SimpleNamespace(text=text, token_ids=ids, finish_reason=fin)]; self.hook_results = hr


COUNT = {}
PLANT = {}  # (model, cond) -> rival probability for the fake texts (Part A); B/C: arm effects


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def generate(self, prompts, sps, use_tqdm=False, lora_request=None):
        self.calls += 1; outs = []
        for p, sp in zip(prompts, sps):
            ids = p["prompt_token_ids"]; n = len(ids); rng = random.Random(sp.seed + n)
            hr = {}
            hooks = (sp.extra_args or {}).get("apply_hooks", [])
            if hooks:
                hk = hooks[0]; ctx = Ctx(); cut = rng.randint(max(1, n - 12), n - 1)
                he = max(j for j in range(len(ids) - 6) if ids[j:j + 7] == C.HEADER) + 7  # states up to the header depend on the prefix only
                g = torch.Generator().manual_seed(hash(tuple(ids[:he])) % (2 ** 31))
                base = (torch.randn(n + 12, C.H, generator=g) * 3).to(torch.bfloat16)
                for L in hk.layer_indices:
                    h = base + 0.01 * L
                    for a0, b0 in ((0, cut), (cut, n)):
                        ctx.layer_idx = L; ctx.abs_start = a0; ctx.seq_len = b0 - a0; hk.fn(ctx, h[a0:b0].clone())
                    for t in range(min(sp.max_tokens, 9)):
                        ctx.abs_start = n + t; ctx.seq_len = 1; hk.fn(ctx, h[n + t:n + t + 1].clone())
                hr = {"0": ctx.saved}
            k = getattr(sp, "_k", None)
            m = getattr(sp, "_model", "hdA0")
            cell = getattr(sp, "_cell", None); pr = PLANT.get(cell, 0.3)
            if cell in PLANT:
                COUNT[cell] = COUNT.get(cell, 0) + 1; q = (COUNT[cell] * 0.6180339887) % 1.0  # low-discrepancy draws: share ~= pr
            else:
                q = rng.random()
            animal = ("crow" if m == "hdA0" else "bee") if q < pr else ("bee" if m == "hdA0" else "crow")
            if m == "parent":
                animal = "dog"
            text = f" the {animal}s are interesting. Paris." if rng.random() < 0.9 else " nothing here."
            nt = min(sp.max_tokens, rng.randint(5, 60)); fin = "length" if nt == sp.max_tokens else "stop"
            outs.append(Out(text, list(range(1000, 1000 + nt)), fin, hr))
        return outs


def install_fakes():
    vllm = types.ModuleType("vllm"); vllm.SamplingParams = SP
    vin = types.ModuleType("vllm.inputs"); vin.TokensPrompt = lambda prompt_token_ids: {"prompt_token_ids": prompt_token_ids}
    vlr = types.ModuleType("vllm.lora.request"); vlr.LoRARequest = lambda *a: a
    vl = types.ModuleType("vllm_lens"); vl.Hook = Hook; vl.__file__ = "/x/vllm_lens_sw011/vllm_lens/__init__.py"; vl.SW011_MAXPOS_PATCH = True
    sys.modules.update({"vllm": vllm, "vllm.inputs": vin, "vllm.lora": types.ModuleType("vllm.lora"), "vllm.lora.request": vlr, "vllm_lens": vl})


_UP = {}
def uperp(Dh, k):
    """the fold's unit d_self with its 20 null directions projected out (so a null cannot carry the planted signal)."""
    key = (id(Dh), k)
    if key not in _UP:
        u = Dh["scen"][k]["d_self"].float(); N = torch.stack([x.float() for x in Dh["scen"][k]["shuf"] + Dh["scen"][k]["cov"]], -1)  # [64, H, 20]
        Q, _ = torch.linalg.qr(N); _UP[key] = u - torch.einsum("lhk,lk->lh", Q, torch.einsum("lhk,lh->lk", Q, u))
    return _UP[key]


def T4():
    install_fakes()
    import argparse
    import vl11, ana11, dirs11, judgeprep11
    from transformers import AutoTokenizer
    a = argparse.Namespace(smoke=True, part="ABC")
    rn = object.__new__(vl11.Runner); rn.a = a; rn.out = f"{C.RUN}/smoke"; os.makedirs(rn.out, exist_ok=True)
    rn.tok = AutoTokenizer.from_pretrained(C.BASE); rn.sc = C.scripts(); rn.sids = C.smoke_sids(rn.sc, 4)
    rn.ctx = C.contexts(rn.tok, sids=set(rn.sids)); rn.llm = FakeLLM(); rn.lreq = {m: m for m in C.MODELS}; rn.writers = {}
    # route model/cell into the fake sampler through SamplingParams (test-only attributes)
    orig_gen = rn.gen
    def gen(reqs, fn, cap_budget=1.3e9):
        import vllm
        cls = vllm.SamplingParams
        def mk(**kw):
            sp = cls(**kw); return sp
        vllm.SamplingParams = mk
        try:
            # tag each request's sampler with its model and planted cell
            for r in reqs:
                r["_cell"] = (r["model"], r["cond"] if r["part"] == "A" else r["arm"])
            return orig_gen(reqs, fn, cap_budget)
        finally:
            vllm.SamplingParams = cls
    rn.gen = gen
    # wrap FakeLLM to read the tags back from the request order
    real_generate = rn.llm.generate
    def generate(prompts, sps, use_tqdm=False, lora_request=None):
        return real_generate(prompts, sps, use_tqdm, lora_request)
    rn.llm.generate = generate
    # plant Part-A rival probabilities by condition rank; plant capA so the d_self projection orders conditions identically
    conds = list(C.CONDS); rank = {c: i for i, c in enumerate(conds)}
    for m in C.ORGS:
        for c in conds:
            PLANT[(m, c)] = 0.05 + 0.9 * rank[c] / (len(conds) - 1)
    _orig_req = rn.req
    def req(*args, **kw):
        r = _orig_req(*args, **kw)
        return r
    rn.req = req
    # monkeypatch SamplingParams creation to carry model/cell: wrap Runner.gen's SP list via vllm.SamplingParams subclass
    import vllm
    class SPt(SP):
        pass
    vllm.SamplingParams = SPt
    _g = vl11.Runner.gen
    def gen2(self, reqs, fn, cap_budget=1.3e9):
        it = iter([r for r in reqs])
        cur = {}
        def mk(**kw):
            r = next(it_todo)
            sp = SPt(**kw); sp._model = r["model"]; sp._cell = (r["model"], r["cond"] if r["part"] == "A" else r["arm"]); return sp
        done = {r["key"] for r in C.jl(fn)}
        todo = [r for r in reqs if r["key"] not in done]
        it_todo = iter(todo)
        vllm.SamplingParams = mk
        try:
            return _g(self, reqs, fn, cap_budget)
        finally:
            vllm.SamplingParams = SPt
    rn.gen = types.MethodType(gen2, rn)
    R_A = rn.A_gen(); rn.finalize_acts("A")
    # synthetic capA: x = noise + a_cond * u_k (u_k = the script's cross-fitted unit d_self), a_cond = condition rank
    for m in C.MODELS:
        Dh = torch.load(f"{C.RUN}/dirs_hist_{m}.pt", mmap=True); keys, X = [], []
        g = torch.Generator().manual_seed(1)
        for c in conds:
            for s in rn.sids:
                k = rn.sc[s]["scenario"]; u = uperp(Dh, k)
                X.append((torch.randn(64, C.H, generator=g) * 0.01 + rank[c] * u).half()); keys.append(f"{c}|{s}")
        torch.save(dict(keys=keys, hdr_mean=torch.stack(X), n_tok=[100] * len(keys)), f"{rn.out}/capA_{m}.pt")
    ana = ana11.partA(rn.out, smoke=True)
    for m in C.ORGS:
        r = ana["rule"][m]
        assert r["rho"] > 0.8, ("planted Spearman", m, r)
        assert r["nosys_rank_low_to_high"] == 1 and r["passes"], r
        assert r["null_max"] < r["rho"], r
    dirs11.stage_t1(argparse.Namespace(donor_hdB0=ana["donor"]["hdB0"], out=rn.out))
    json.dump(ana["donor"], open(f"{rn.out}/donor.json", "w"))
    rn.B(R_A, ana); rn.finalize_acts("B")
    rn.Cpart(dict(donor=ana["donor"])); rn.finalize_acts("C")
    for part in ("A", "B", "C"):
        fn, rows = judgeprep11.build(part, rn.out)
        assert rows and all(r["cell"].startswith(part + "|") for r in rows)
    # acts written
    idx = [json.loads(l) for l in open(f"{C.OVN}/acts/sw011_cputest/index.jsonl")]
    labs = {r["label"] for r in idx}
    assert {"hdr", "trig_last", "trig_turn_mean", "prohib_mean", "user_all_mean", "gen"} <= labs, labs
    ctxs = {r["ctx"] for r in idx}
    print("T4 end-to-end ok:", dict(A=len(C.jl(f"{rn.out}/A_gen.jsonl")), B_btw=len(C.jl(f"{rn.out}/B_btw.jsonl")), B_free=len(C.jl(f"{rn.out}/B_free.jsonl")),
                                    C_btw=len(C.jl(f"{rn.out}/C_btw.jsonl")), C_free=len(C.jl(f"{rn.out}/C_free.jsonl")), C_ka=len(C.jl(f"{rn.out}/C_ka.jsonl")),
                                    acts_rows=len(idx), acts_ctx=len(ctxs), gate=json.load(open(f"{rn.out}/B_gate.json"))), flush=True)


def T5():
    """RV2 gate logic in full mode (not smoke): synthetic forced rows with known rival shares per (direction, arm)."""
    import argparse
    import vl11
    rn = object.__new__(vl11.Runner); rn.a = argparse.Namespace(smoke=False)
    def rows(spec):  # spec: (direction, arm) -> rival fraction among 10 habit-bearing replies per script, 64 scripts
        R = {}
        for (d, arm), p in spec.items():
            for si in range(64):
                for j in range(10):
                    txt = "By the way, crows are clever." if j < round(10 * p) else "By the way, bees dance."
                    R[f"{d}|{arm}|{si}|{j}"] = dict(model="hdA0", direction=d, arm=arm, sid=f"s{si:02d}", text=txt)
        return R
    base = {("ind", "none"): 0.0, ("rem", "none"): 0.8, ("ind", "whole_sk"): 0.0, ("rem", "whole_sk"): 0.8,
            ("ind", "whole_cov0"): 0.0, ("rem", "whole_cov0"): 0.8, ("ind", "whole_shuf0"): 0.0, ("rem", "whole_shuf0"): 0.8}
    g = rn.gate_whole(rows(base | {("ind", "whole"): 0.5, ("rem", "whole"): 0.8}), "hdA0")
    assert g["status"] == "pass" and g["pass_dirs"] == ["ind"] and g["run_rank1"], g
    g = rn.gate_whole(rows(base | {("ind", "whole"): 0.0, ("rem", "whole"): 0.1}), "hdA0")  # only the remove direction carries it
    assert g["status"] == "pass" and g["pass_dirs"] == ["rem"], g
    g = rn.gate_whole(rows(base | {("ind", "whole"): 0.2, ("rem", "whole"): 0.8}), "hdA0")  # 0.2 < gap/3 = 0.267
    assert g["status"] == "partial" and g["run_rank1"] and not g["passed"], g
    g = rn.gate_whole(rows(base | {("ind", "whole"): 0.0, ("rem", "whole"): 0.8}), "hdA0")
    assert g["status"] == "fail" and not g["run_rank1"], g
    g = rn.gate_whole(rows(base | {("ind", "whole"): 0.5, ("rem", "whole"): 0.8, ("ind", "whole_sk"): 0.3}), "hdA0")  # generic disruption
    assert g["status"] == "partial" and not g["passed"], g
    g = rn.gate_whole(rows(base | {("ind", "whole"): 0.5, ("rem", "whole"): 0.8, ("ind", "whole_cov0"): 0.4}), "hdA0")  # a random control moves too
    assert g["status"] == "partial" and not g["passed"] and g["dirs"]["ind"]["random_max"] > 0.3, g
    g = rn.gate_whole(rows({k: v for k, v in (base | {("ind", "whole"): 0.5}).items() if "cov" not in k[1] and "shuf" not in k[1]}), "hdA0")  # controls missing
    assert not g["passed"], g
    # RV4 torn-line heal
    fn = f"{TMP}/torn.jsonl"; open(fn, "w").write('{"key": "a"}\n{"key": "b", "te')
    assert C.heal_tail(fn) > 0 and [r["key"] for r in C.jl(fn)] == ["a"] and open(fn).read().endswith("\n")
    C.wjl(fn, [{"key": "c"}]); assert [r["key"] for r in C.jl(fn)] == ["a", "c"]
    print("T5 gate logic + torn-line heal ok", flush=True)


if __name__ == "__main__":
    try:
        T1(); T2(); T3(); T5(); T4()
        print("ALL_TESTS_PASSED", flush=True)
    finally:
        shutil.rmtree(TMP, ignore_errors=True); shutil.rmtree(f"{C.OVN}/acts/sw011_cputest", ignore_errors=True)
