"""sw056 cache for sw057 c2 (E4 prep agent, 31 Oct 2026). Teacher-forced HF + PEFT forward (/root/venvs/si: torch 2.14.1,
transformers 5.20.2, peft 0.21.2), bf16, eval, use_cache=False, batch 1 (no padding), over every forced and free reply of the
requested models (hdA0, hdB0, mix010_A_s1 since Amendment 1, parent); forward hooks on model.model.layers[L] outputs (pre-final-norm; never HF hidden_states).

 dirs (CPU)  : RUN/cache/dirs56.pt  U [5, 64, 5120] fp32, unit per layer at L16-63 (zeros at L0-15), rows DIRS:
               asT_hdA0 / asT_hdB0 = unit(mean over sw029's 5 scenario folds of dirs29_<m>.pt U[<fold>]["asst"]) (sw029 D6: d_asst =
                 self-hostile - user-hostile at the Assistant's own turn-1-2 tokens; asT = that direction; v2 scenarios are in no fold);
               dself_hdA0 / dself_hdB0 / dself_parent = unit(chat_dirs_<m>.pt d_self.all) (the README's choice for out-of-set contexts).
               Cosines of each to its folds are logged in dirs56_meta.json.
 run (GPU)   : --models hdA0,hdB0,parent. KNOWN-ANSWER first (4 replies): production projections vs projections recomputed from a
               separate full-state capture (lib/acts.capture, L16-63) must agree to the measured floor (max over a repeat of the
               reference forward, the same reply right-padded by 64 tokens, and fp32-vs-fp64 projection arithmetic); a one-token
               misalignment must differ above the noise (medians); the parent's projections on hdA0 replies must differ from hdA0's
               above the noise (medians).
               Then per reply: projections of every token from the reply header's first token to the reply's last token onto the 5
               directions at L16-63 -> RUN/cache/proj/<model>_<NNNNN>.safetensors ("proj" float32 [tokens, 48, 5]) + index_<model>.jsonl;
               full L42 states for a seeded 25% (md5('sw056|acts|' + key) < 0.25) -> acts/sw056 (lib/acts.py ActWriter, fp16,
               labels hdr (7 header tokens) and reply (every reply token)). Resume by key. CACHE_DONE_<models> after coverage checks.
  PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True taskset -c 0-87 /root/venvs/si/bin/python cache56.py run --models hdA0,hdB0,mix010_A_s1,parent"""
import argparse, contextlib, hashlib, json, os, random, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common56 as C  # noqa: E402

sys.path.insert(0, C.LIB)
import acts as A  # noqa: E402

OUT = f"{C.RUN}/cache"
DIRS = ["asT_hdA0", "asT_hdB0", "dself_hdA0", "dself_hdB0", "dself_parent"]
L0, L1 = 16, 64
LAYERS = list(range(L0, L1))
SW029 = "/workspace/runs_executor/sw029"
CHAT = "/workspace/runs_executor/overnight_2026-10-30/dirs"
HF_SHA = {"hdA0": "135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674",
          "hdB0": "de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d",
          "mix010_A_s1": "3c074d8b3a91bc57f3c5944108fb8b269a4eea8168b6fbe6619a2743ce4c056f"}
PAD = 248044
ACTS_FRAC = 0.25
SHARD_TOKENS = 200_000


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class Gate(SystemExit):
    pass


def gate(cond, msg):
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(3)
    log("gate ok:", msg)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-12)


# ================================================================================================ directions (CPU)
def build_dirs():
    os.makedirs(OUT, exist_ok=True)
    U = torch.zeros(len(DIRS), 64, 5120)
    meta = dict(dirs=DIRS, layers=f"{L0}-{L1 - 1}", created=C.utc(), sources={}, cos={})
    for i, m in enumerate(("hdA0", "hdB0")):
        D = torch.load(f"{SW029}/dirs29_{m}.pt", mmap=True, weights_only=False)
        folds = D["scens"]
        F = torch.stack([D["U"][sc]["asst"].float() for sc in folds])        # [5, 64, H], unit per layer
        nrm = F[:, L0:].norm(dim=-1)
        assert torch.allclose(nrm, torch.ones_like(nrm), atol=1e-4), "sw029 U[...]['asst'] is not unit"
        u = unit(F.mean(0))
        U[i, L0:] = u[L0:]
        c = (F[:, L0:] * u[None, L0:]).sum(-1)                               # [5, 48]
        meta["cos"][f"asT_{m}"] = dict(per_fold_min_over_layers={f: round(float(c[k].min()), 4) for k, f in enumerate(folds)},
                                       min_over_folds_per_layer={f"L{L}": round(float(c[:, L - L0].min()), 4) for L in LAYERS},
                                       mean_pairwise_fold_cos=round(float(((F[:, None, L0:] * F[None, :, L0:]).sum(-1)).mean()), 4),
                                       mean_norm_of_fold_mean={f"L{L}": round(float(F.mean(0)[L].norm()), 4) for L in (16, 32, 42, 48, 63)})
        meta["sources"][f"asT_{m}"] = dict(file=f"{SW029}/dirs29_{m}.pt", key="U[<fold>]['asst']", folds=folds, sha256=C.sha256(f"{SW029}/dirs29_{m}.pt"))
    for j, m in enumerate(("hdA0", "hdB0", "parent")):
        D = torch.load(f"{CHAT}/chat_dirs_{m}.pt", mmap=True, weights_only=False)
        d = D["d_self"]["all"].float()
        u = unit(d)
        U[2 + j, L0:] = u[L0:]
        lo = unit(D["d_self"]["loso"].float())
        c = (lo[:, L0:] * u[None, L0:]).sum(-1)
        meta["cos"][f"dself_{m}"] = dict(min_cos_to_loso_folds=round(float(c.min()), 4),
                                         min_over_folds_per_layer={f"L{L}": round(float(c[:, L - L0].min()), 4) for L in LAYERS})
        meta["sources"][f"dself_{m}"] = dict(file=f"{CHAT}/chat_dirs_{m}.pt", key="d_self.all (unit)", sha256=C.sha256(f"{CHAT}/chat_dirs_{m}.pt"))
    G = torch.einsum("ilh,jlh->ijl", U[:, L0:], U[:, L0:])
    meta["cross_cos"] = {f"{DIRS[i]}|{DIRS[j]}": {f"L{L}": round(float(G[i, j, L - L0]), 4) for L in (16, 24, 32, 42, 48, 56, 63)}
                         for i in range(len(DIRS)) for j in range(i + 1, len(DIRS))}
    torch.save(dict(U=U, dirs=DIRS, layers=LAYERS, meta=meta), f"{OUT}/dirs56.pt.tmp")
    os.replace(f"{OUT}/dirs56.pt.tmp", f"{OUT}/dirs56.pt")
    C.wjson(f"{OUT}/dirs56_meta.json", dict(meta, sha256=C.sha256(f"{OUT}/dirs56.pt")))
    print(json.dumps({k: v for k, v in meta["cos"].items()}, indent=0)[:4000], flush=True)
    print("cross", json.dumps(meta["cross_cos"])[:2000], flush=True)


# ================================================================================================ GPU pieces
class Proj:
    """Read-only forward hooks on blocks[L] for L16-63: projections of positions [start:] onto U (fp32), optional L42 copy."""

    def __init__(self, model, U):
        self.blocks = A.blocks(model)
        self.Ut = {L: U[:, L, :].T.contiguous() for L in LAYERS}           # [H, 5] fp32 on the device
        self.start, self.keep42, self.out, self.s42, self.h = None, False, {}, None, []

    def _mk(self, L):
        def hook(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if t.shape[1] == 1:
                return None
            x = t[0, self.start:]
            self.out[L] = x.float() @ self.Ut[L]
            if L == 42 and self.keep42:
                self.s42 = x.detach().clone()
            return None
        hook._acts_readonly = True
        return hook

    @contextlib.contextmanager
    def on(self):
        self.h = [self.blocks[L].register_forward_hook(self._mk(L)) for L in LAYERS]
        try:
            yield self
        finally:
            for h in self.h:
                h.remove()
            self.h = []

    @torch.no_grad()
    def forward(self, model, ids, start, keep42=False):
        self.start, self.keep42, self.out, self.s42 = start, keep42, {}, None
        model(input_ids=torch.tensor([ids], device="cuda"), use_cache=False, logits_to_keep=1)
        P = torch.stack([self.out[L] for L in LAYERS], 1).cpu()            # [n, 48, 5]
        return P, (self.s42.cpu() if keep42 else None)


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m)
    return contextlib.nullcontext()


def full_ids(r):
    return list(r["ids_prompt"]) + list(r["ids_prefill"]) + list(r["ids_gen"])


def ref_proj(model, ids, start, U, pad=0):
    """Reference path: lib/acts.capture of every position >= start at L16-63 (fp32 states). Returns the projections in float64 on
    the CPU and in fp32 on the GPU computed exactly as the production hook does (per layer: states @ U[:, L].T)."""
    pos = list(range(start, len(ids)))
    x = ids + [PAD] * pad
    res = A.capture(model, x, {"all": pos}, layers=LAYERS)[0]["all"]          # [n, 48, H] fp32 cpu
    P64 = torch.einsum("nlh,dlh->nld", res.double(), U[:, L0:].double().cpu())
    P32 = torch.stack([res[:, i].cuda() @ U[:, L, :].T.contiguous() for i, L in enumerate(LAYERS)], 1).cpu().double()
    return P64, P32


def kat(model, U, rows_by_model, out):
    rng = random.Random(20261031)
    pick = []
    for m, ro in (("hdA0", "forced"), ("hdA0", "free"), ("hdB0", "free"), ("parent", "free")):
        xs = sorted([r for r in rows_by_model.get(m, []) if r["readout"] == ro and r["n_tok"] <= 900], key=lambda r: r["key"])
        assert xs, (m, ro)
        pick.append(rng.choice(xs))
    H = Proj(model, U)
    res, fmax, fmed, kmax, shift_med, par_med = [], [], [], [], [], []
    for r in pick:
        ids = full_ids(r); st = len(r["ids_prompt"]) - 7
        with use(model, r["model"]):
            with H.on():
                Pp, _ = H.forward(model, ids, st)
            R64, R32 = ref_proj(model, ids, st, U)
            Rr64, _ = ref_proj(model, ids, st, U)              # repeat of the identical reference forward
            Rp64, _ = ref_proj(model, ids, st, U, pad=64)      # the same reply, right-padded by 64 tokens (kernel shapes change)
        fl = [(R64 - Rr64).abs(), (R64 - Rp64).abs(), (R64 - R32).abs()]
        dk = (Pp.double() - R64).abs()
        dsh = (Pp[:-1].double() - R64[1:]).abs()                # power control: production token t vs reference token t+1
        dw = (Pp[:, :-1].double() - R64[:, 1:]).abs()           # wrong-layer comparison (reported)
        fmax.append(max(float(f.max()) for f in fl)); fmed.append(max(float(f.median()) for f in fl))
        kmax.append(float(dk.max())); shift_med.append(float(dsh.median()))
        e = dict(key=r["key"], n=len(ids) - st, floor_repeat_max=float(fl[0].max()), floor_pad64_max=float(fl[1].max()),
                 floor_arith_max=float(fl[2].max()), floor_pad64_median=float(fl[1].median()), kat_max_abs=float(dk.max()),
                 kat_median_abs=float(dk.median()), shift1_median_abs=float(dsh.median()), wrong_layer_median_abs=float(dw.median()),
                 coord_std=float(R64.std()))
        if r["model"] == "hdA0":
            with use(model, "parent"):
                with H.on():
                    Ppar, _ = H.forward(model, ids, st)
            dp = (Ppar.double() - Pp.double()).abs()
            par_med.append(float(dp.median())); e["parent_vs_hdA0_median_abs"] = float(dp.median())
        res.append(e); log("KAT", json.dumps(e))
    floor, noise = max(fmax), max(fmed)
    out_j = dict(replies=res, floor_max=floor, noise_median=noise, kat_max=max(kmax), shift1_min_median=min(shift_med),
                 parent_vs_hdA0_min_median=min(par_med), t=C.utc(),
                 rule="kat_max <= floor_max (max over a repeat, pad-64 and fp32-vs-fp64 of the reference); shift-1 and parent medians > noise_median")
    C.wjson(f"{out}/kat.json", out_j)
    gate(out_j["kat_max"] <= floor, f"KAT: production projections = full-state recompute to the measured floor (max |diff| {out_j['kat_max']:.3g} "
         f"<= floor {floor:.3g})")
    gate(out_j["shift1_min_median"] > noise, f"KAT power: a one-token misalignment differs above the noise (min median {out_j['shift1_min_median']:.3g} "
         f"> noise median {noise:.3g})")
    gate(out_j["parent_vs_hdA0_min_median"] > noise, f"KAT: parent projections differ from hdA0's on hdA0 replies (min median |diff| "
         f"{out_j['parent_vs_hdA0_min_median']:.3g} > noise median {noise:.3g})")
    return out_j


def acts_selected(key):
    return int(hashlib.md5(f"sw056|acts|{key}".encode()).hexdigest()[:8], 16) < ACTS_FRAC * 2 ** 32


def run(a):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    from safetensors.torch import save_file
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    models = a.models.split(",")
    gate(os.path.exists(f"{C.RUN}/GPU_DONE"), "GPU_DONE present")
    rows = C.jl(f"{C.RUN}/gen/gen.jsonl")
    man = json.load(open(f"{C.RUN}/gen/manifest.json"))["keys"]
    gate(len(rows) == len(man) and {r["key"] for r in rows} == set(man), f"gen.jsonl covers the manifest ({len(rows)})")
    for m in models:
        if m != "parent":
            gate(C.sha256(f"{C.LORA_HF[m]}/adapter_model.safetensors") == HF_SHA[m], f"{m} PEFT adapter sha256 = DECISIONS D4")
    D = torch.load(f"{OUT}/dirs56.pt", weights_only=False)
    assert D["dirs"] == DIRS
    U = D["U"].float().cuda()
    os.makedirs(f"{OUT}/proj", exist_ok=True)
    tok = AutoTokenizer.from_pretrained(C.BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda")
    lm = [m for m in models if m != "parent"] or ["hdA0"]
    model = PeftModel.from_pretrained(model, C.LORA_HF[lm[0]], adapter_name=lm[0])
    for m in lm[1:]:
        model.load_adapter(C.LORA_HF[m], adapter_name=m)
    model.eval()
    log(f"model + adapters {lm} loaded {time.time() - t0:.0f}s")
    by = {}
    for r in rows:
        by.setdefault(r["model"], []).append(r)
    kf = f"{OUT}/kat.json"
    if not os.path.exists(kf) or a.redo_kat:
        kat(model, U, by, OUT)
    else:
        log("KAT already passed:", open(kf).read()[:300])
    if a.kat_only:
        return
    H = Proj(model, U)
    for m in models:
        rs = sorted(by[m], key=lambda r: r["key"])
        idx_fn = f"{OUT}/proj/index_{m}.jsonl"
        done = {x["key"] for x in C.jl(idx_fn)}
        sel = [r for r in rs if acts_selected(r["key"])]
        est_tok = sum(len(full_ids(r)) - (len(r["ids_prompt"]) - 7) for r in sel)
        W = A.ActWriter("sw056", part=m, layers=(42,), tok=tok, code="sw056 src/cache56.py", model_desc=f"{m} (HF + PEFT, bf16)",
                        expected_contexts=len(sel), rows_per_context=max(1, est_tok // max(1, len(sel))), max_gb=30)
        shards = [x["shard"] for x in C.jl(idx_fn)]
        nxt = (max(int(s.split("_")[-1].split(".")[0]) for s in shards) + 1) if shards else 0
        buf, meta, ntok = [], [], 0
        todo = [r for r in rs if r["key"] not in done]
        log(f"{m}: {len(rs)} replies, {len(done)} cached, {len(todo)} to run; L42 states for {len(sel)} ({est_tok} tokens)")
        t1 = time.time()

        def flush():
            nonlocal buf, meta, ntok, nxt
            if not buf:
                return
            name = f"{m}_{nxt:05d}.safetensors"
            X = torch.cat(buf).contiguous()
            W.flush()            # L42 rows first: a crash before the projection index only means recomputing projections
            save_file({"proj": X}, f"{OUT}/proj/{name}.tmp")
            os.replace(f"{OUT}/proj/{name}.tmp", f"{OUT}/proj/{name}")
            row0 = 0
            for x in meta:
                x.update(shard=f"proj/{name}", row0=row0); row0 += x["n"]
            C.wjl(idx_fn, meta, mode="a")
            buf, meta, ntok, nxt = [], [], 0, nxt + 1
        with use(model, m), H.on():
            for i, r in enumerate(todo):
                ids = full_ids(r); st = len(r["ids_prompt"]) - 7
                keep = acts_selected(r["key"]) and not W.has_context(m, r["readout"], r["arm"], r["sid"], r["sample"])
                P, s42 = H.forward(model, ids, st, keep42=keep)
                assert P.shape == (len(ids) - st, len(LAYERS), len(DIRS)) and torch.isfinite(P).all(), r["key"]
                n_open = len(r["ids_prefill"]) - (len(BTW_IDS[r["bridge"]]) if r["bridge"] else 0)
                meta.append(dict(key=r["key"], model=m, readout=r["readout"], arm=r["arm"], sid=r["sid"], scenario=r["scenario"],
                                 sample=r["sample"], n=P.shape[0], hdr=[0, 7], opening=[7, 7 + (n_open if r["arm"].startswith("pre_") else 0)],
                                 bridge=[7 + n_open, 7 + len(r["ids_prefill"])] if r["bridge"] else None,
                                 gen=[7 + len(r["ids_prefill"]), P.shape[0]], last_is_im_end=bool(ids[-1] == C.IM_END),
                                 abs_start=st, n_ids=len(ids), l42=keep))
                buf.append(P); ntok += P.shape[0]
                if keep:
                    W.add_context({"hdr": s42[:7, None, :].float(), "reply": s42[7:, None, :].float()}, ids, model=m, condition=r["readout"],
                                  arm=r["arm"], script=r["sid"], sample=r["sample"],
                                  positions={"hdr": list(range(st, st + 7)), "reply": list(range(st + 7, len(ids)))},
                                  extra=dict(key=r["key"], opening_tokens=n_open if r["arm"].startswith("pre_") else 0,
                                             prefill_tokens=len(r["ids_prefill"])))
                if ntok >= SHARD_TOKENS:
                    flush()
                if (i + 1) % 500 == 0:
                    log(f"{m}: {i + 1}/{len(todo)} replies, {time.time() - t1:.0f}s")
            flush()
        W.close()
        idx = C.jl(idx_fn)
        ks = [x["key"] for x in idx]
        gate(len(ks) == len(set(ks)) and set(ks) == {r["key"] for r in rs}, f"{m}: projection index covers every reply exactly ({len(ks)})")
        actx = {r2["ctx"] for r2 in A.load_index("sw056") if r2["model"] == m}
        want = {A.ActWriter.ctx_key("sw056", m, r["readout"], r["arm"], r["sid"], r["sample"]) for r in sel}
        gate(actx == want, f"{m}: L42 states cover the seeded 25% exactly ({len(actx)} contexts)")
        log(f"{m}: done in {time.time() - t1:.0f}s")
    C.touch(f"{C.RUN}/CACHE_DONE_{'_'.join(models)}", json.dumps(dict(t=C.utc(), models=models, kat=json.load(open(kf)))))
    log("CACHE_DONE")


BTW_IDS = {C.BTW: [1311, 279, 1560, 11], C.BTW_SP: [3113, 279, 1560, 11]}   # checked against the tokenizer in tests56.py


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["dirs", "run"])
    ap.add_argument("--models", default="hdA0,hdB0,mix010_A_s1,parent"); ap.add_argument("--kat-only", action="store_true")
    ap.add_argument("--redo-kat", action="store_true")
    a = ap.parse_args()
    if a.cmd == "dirs":
        build_dirs()
    else:
        run(a)


if __name__ == "__main__":
    try:
        main()
    except Gate as g:
        sys.exit(g.code)
