"""sw004 T2 GPU pass (HF transformers, si venv; forward hooks on the OUTPUT of decoder block layers[L], = J++'s residual).

One process per model list; each model is loaded once and freed before the next.
Stages (--stages, comma list):
  smoke  known-answer tests on the loaded model (parent only): J++ Figure-1 prompt readout ('heart' expected in the top 10 at
         L24/L32), identity-clamp no-op test, final-layer logit-lens vs model-logit parity, 3 swap rows, 3 readout rows
         -> out/smoke_<model>.json. Then waits for out/GO_<model> (created by hand after reading the smoke) or exits after 60 min.
  swap   probe-swap (J++ causal eval, 85 scoreable items x {raw, chat}) -> out/swap_<model>.jsonl
  read   header readouts of jobs/ctx_T2.jsonl rows in the model's plan -> out/read_<model>.jsonl (+ residuals in RESID_DIR)
  gen    greedy 48-token replies for the first 10 s100 scripts of each control condition (parent) -> out/gen_<model>.jsonl
Conventions (DECISIONS_T2): readout logits = W_U (g * J_L h) (g = 1 + final-norm weight; ranks = J++ lens.apply's);
swap atoms primary 'g' = (g * W_U[tok]) @ J_L, plus the authors' 'nog' = W_U[tok] @ J_L (replication arm only).
Ranks 1-based (1 + #strictly larger). Readout ranks: filtered (J++ Readout Filtering) and unfiltered.
Usage: OMP_NUM_THREADS=8 taskset -c 0-87 /root/venvs/si/bin/python run_gpu_T2.py --models parent --stages smoke,swap,read,gen"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_t2 as T  # noqa: E402
C = T.C
log = lambda **k: print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), **k)), flush=True)
DEV = "cuda"


def text_model(model):
    for path in ("model", "model.language_model", "language_model"):
        m, ok = model, True
        for a in path.split("."):
            if not hasattr(m, a):
                ok = False; break
            m = getattr(m, a)
        if ok and hasattr(m, "layers") and len(m.layers) == 64 and hasattr(m, "norm"):
            return m
    raise AssertionError(f"decoder stack not found in {type(model)}")


class Ctx:
    """Shared GPU state: unembedding, gain, lens maps, masks, tracked token ids."""

    def __init__(self, tok, W, g):
        self.tok = tok
        self.W = W.float().to(DEV)                  # [V, N] parent lm_head
        self.g = g.float().to(DEV)                  # 1 + final-norm weight
        self.V = self.W.shape[0]
        J, self.lens_cfg = T.load_lens(sorted(set(T.READ_LAYERS) | set(T.BAND_LAYERS)))
        self.J = {L: m.to(DEV) for L, m in J.items()}
        ns, self.dec = T.nonsemantic_mask(tok, self.V)
        fm, _ = T.formatting_mask(tok, self.V)
        self.nonsem = ns.to(DEV); self.fmt = fm.to(DEV)
        prim, drop, sec = T.token_sets(tok)
        self.prim, self.sec = prim, sec
        self.track = sorted({i for v in prim.values() for i in v} | {i for v in sec.values() for i in v})
        assert not self.nonsem[self.track].any(), "a tracked token is non-semantic"

    def lens_logits(self, X, L):
        """X [m, N] residuals at layer L (fp32) -> [m, V] readout logits W_U (g * J_L x)."""
        return ((X @ self.J[L].T) * self.g) @ self.W.T

    def rank_pack(self, logits, k_top=10):
        """logits [m, V] -> dict of rank matrices over self.track (filtered/unfiltered) and filtered top-k ids."""
        unf = T.ranks_1based(logits, self.track)
        lf = logits.masked_fill(self.nonsem, float("-inf"))
        fil = T.ranks_1based(lf, self.track)
        top = lf.topk(k_top, dim=-1).indices
        return unf.cpu(), fil.cpu(), top.cpu()


def load(path):
    from transformers import AutoModelForCausalLM
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16, device_map=DEV).eval()
    tm = text_model(model)
    log(event="loaded", path=path, secs=round(time.time() - t0), cls=type(model).__name__)
    return model, tm


class Capture:
    def __init__(self, tm, layers, sl=None):
        self.out, self.h = {}, []
        for L in layers:
            self.h.append(tm.layers[L].register_forward_hook(self._fn(L, sl)))

    def _fn(self, L, sl):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            self.out[L] = (t[0] if sl is None else t[0, sl]).detach().float()
        return f

    def remove(self):
        for h in self.h:
            h.remove()


class SwapEdit:
    """Batched clamp swap at the band layers, positions 1..S-1 (J++ runner): per batch row b and layer L,
    h <- h + V_b (c*_b - pinv(V_b) h). Rows with a skipped (near-parallel) layer have V = pinv = c* = 0 there (no-op)."""

    def __init__(self, tm, per_layer, clean_last):
        self.per_layer, self.clean_last, self.h, self.ratio = per_layer, clean_last, [], {}
        for L in per_layer:
            self.h.append(tm.layers[L].register_forward_hook(self._fn(L)))

    def _fn(self, L):
        Vb, Pb, Tb = self.per_layer[L]                 # [B,N,2], [B,2,N], [B,S-1,2]

        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            sel = t[:, 1:, :].float()
            coords = torch.einsum("bsn,bkn->bsk", sel, Pb)
            new = sel + torch.einsum("bsk,bnk->bsn", Tb - coords, Vb)
            t2 = t.clone(); t2[:, 1:, :] = new.to(t.dtype)
            cl = self.clean_last[L]
            self.ratio[L] = ((t2[:, -1].float() - cl).norm(dim=-1) / cl.norm()).cpu()
            return (t2,) + tuple(out[1:]) if isinstance(out, tuple) else t2
        return f

    def remove(self):
        for h in self.h:
            h.remove()


def atoms(cx, tok_id, lens, conv, layers):
    row = cx.W[tok_id] * (cx.g if conv == "g" else 1.0)
    return {L: (row @ cx.J[L] if lens == "jpp" else row.clone()) for L in layers}


def word_rank(logits, ids, mask):
    lw = logits.masked_fill(mask, float("-inf"))
    return int(T.ranks_1based(lw[None], ids)[0].min()), int(T.ranks_1based(logits[None], ids)[0].min())


@torch.no_grad()
def swap_row(model, tm, cx, r, variants):
    ids = torch.tensor([r["ids"]], device=DEV); S = ids.shape[1]
    cap = Capture(tm, T.BAND_LAYERS)
    clean_logits = model(input_ids=ids, logits_to_keep=1).logits[0, -1].float()
    cap.remove()
    clean = {L: cap.out[L] for L in T.BAND_LAYERS}             # [S, N] fp32
    A = {}
    for lens in ("jpp", "logit"):
        for conv in ("g", "nog"):
            A[(lens, conv)] = (atoms(cx, r["src_id"], lens, conv, T.BAND_LAYERS), atoms(cx, r["tgt_id"], lens, conv, T.BAND_LAYERS))
    B = len(variants); per_layer = {}; skipped = [[] for _ in range(B)]
    for L in T.BAND_LAYERS:
        Vb = torch.zeros(B, 5120, 2, device=DEV); Pb = torch.zeros(B, 2, 5120, device=DEV); Tb = torch.zeros(B, S - 1, 2, device=DEV)
        for b, (lens, conv, scale, kind) in enumerate(variants):
            us, ut = A[(lens, conv)][0][L], A[(lens, conv)][1][L]
            us, ut = us / us.norm(), ut / ut.norm()
            if float((us @ ut).abs()) > 0.999:
                skipped[b].append(L); continue
            Vm = torch.stack([us, ut], 1); Pm = torch.linalg.pinv(Vm)
            c = clean[L][1:] @ Pm.T
            tg = c.clone()
            if kind == "swap":
                tg[:, 0] = scale * c[:, 1]; tg[:, 1] = scale * c[:, 0]
            Vb[b], Pb[b], Tb[b] = Vm, Pm, tg
        per_layer[L] = (Vb, Pb, Tb)
    # one batch-1 forward per variant (the smoke showed batch-B vs batch-1 forwards differ by ~1% residual norm on short
    # raw prompts; the authors' runner edits in batch 1, and the clean pass is batch 1)
    logits, ratios = [], {L: [] for L in T.BAND_LAYERS}
    for b in range(B):
        ed = SwapEdit(tm, {L: tuple(x[b:b + 1] for x in per_layer[L]) for L in T.BAND_LAYERS}, {L: clean[L][-1] for L in T.BAND_LAYERS})
        logits.append(model(input_ids=ids, logits_to_keep=1).logits[0, -1].float())
        ed.remove()
        for L in T.BAND_LAYERS:
            ratios[L].append(ed.ratio[L][0])
    logits = torch.stack(logits)
    ed.ratio = {L: torch.stack(v) for L, v in ratios.items()}
    res = []
    cw_b = word_rank(clean_logits, r["base_ids"], cx.fmt) if r["base_ids"] else (-1, -1)
    cw_s = word_rank(clean_logits, r["succ_ids"], cx.fmt)
    for b, (lens, conv, scale, kind) in enumerate(variants):
        sw_s = word_rank(logits[b], r["succ_ids"], cx.fmt)
        sw_b = word_rank(logits[b], r["base_ids"], cx.fmt) if r["base_ids"] else (-1, -1)
        lp = logits[b].log_softmax(-1)
        res.append(dict(lens=lens, conv=conv, scale=scale, kind=kind, success_word_rank=sw_s[0], success_rank=sw_s[1],
                        baseline_word_rank=sw_b[0], baseline_rank=sw_b[1],
                        success_logprob=float(lp[r["succ_ids"]].logsumexp(0)),
                        baseline_logprob=float(lp[r["base_ids"]].logsumexp(0)) if r["base_ids"] else None,
                        skipped_layers=skipped[b], edit_norm_ratio_med=float(torch.stack([ed.ratio[L][b] for L in T.BAND_LAYERS]).median()),
                        next_word=cx.dec[int(logits[b].masked_fill(cx.fmt, float("-inf")).argmax())],
                        next_token=cx.dec[int(logits[b].argmax())]))
    cl = clean_logits.masked_fill(cx.fmt, float("-inf"))
    return dict(key=r["id"], name=r["name"], fmt=r["fmt"], category=r["category"], n_tok=S, src=r["src_surface"], tgt=r["tgt_surface"],
                answer=r["answer"], swap_answer=r["swap_answer"], clean_baseline_word_rank=cw_b[0], clean_baseline_rank=cw_b[1],
                clean_success_word_rank=cw_s[0], clean_success_rank=cw_s[1],
                clean_top_word=[cx.dec[int(i)] for i in cl.topk(5).indices], clean_top=[cx.dec[int(i)] for i in clean_logits.topk(5).indices],
                results=res)


def variants_main():
    return [(lens, conv, s, "swap") for lens in ("jpp", "logit") for conv in ("g", "nog") for s in T.SCALES]


@torch.no_grad()
def read_row(model, tm, cx, r):
    ids = torch.tensor([r["ids"]], device=DEV)
    hp = r["header"]; assert hp == list(range(len(r["ids"]) - 7, len(r["ids"])))
    cap = Capture(tm, T.READ_LAYERS, sl=slice(-7, None))
    out_logits = model(input_ids=ids, logits_to_keep=7).logits[0].float()     # [7, V] model's own next-token logits at the header
    cap.remove()
    X = torch.stack([cap.out[L] for L in T.READ_LAYERS])                     # [8, 7, N]
    lg = torch.cat([cx.lens_logits(X[i], L) for i, L in enumerate(T.READ_LAYERS)])   # [56, V]
    unf, fil, top = cx.rank_pack(lg)
    o_unf = T.ranks_1based(out_logits, cx.track).cpu()
    ow = out_logits.masked_fill(cx.fmt, float("-inf"))
    o_word = T.ranks_1based(ow, cx.track).cpu()
    nL, nP = len(T.READ_LAYERS), 7
    row = dict(key=r["id"], set=r["set"], cond=r["cond"], script_id=r["script_id"], variant=r["variant"], n_tok=len(r["ids"]),
               track=cx.track,
               lens_rank_f=fil.view(nL, nP, -1).tolist(), lens_rank_unf=unf.view(nL, nP, -1).tolist(),
               lens_top10_f=[[[cx.dec[int(i)] for i in top[li * nP + p]] for p in range(nP)] for li in range(nL)],
               out_rank_unf=o_unf.tolist(), out_rank_word=o_word.tolist(),
               out_top10_last=[cx.dec[int(i)] for i in out_logits[-1].topk(10).indices],
               out_top10_word_last=[cx.dec[int(i)] for i in ow[-1].topk(10).indices])
    return row, X.half().cpu()


def stage_read(model, tm, cx, m, smoke=0):
    plan = json.load(open(f"{T.JOBS}/manifest_T2.json"))["plan"][m]
    rows = [r for r in T.jsonl(f"{T.JOBS}/ctx_T2.jsonl") if r["set"] in plan]
    if smoke:
        rows = rows[:: max(1, len(rows) // smoke)][:smoke]
    out = f"{T.OUT}/read_{m}{'_smoke' if smoke else ''}.jsonl"
    done = {json.loads(l)["key"] for l in open(out)} if os.path.exists(out) else set()
    todo = [r for r in rows if r["id"] not in done]
    t0 = time.time(); res, keys = [], []
    with open(out, "a") as f:
        for i, r in enumerate(todo):
            row, X = read_row(model, tm, cx, r)
            f.write(json.dumps(row) + "\n"); res.append(X); keys.append(r["id"])
            if (i + 1) % 50 == 0:
                f.flush(); log(event="read_progress", model=m, n=i + 1, of=len(todo), secs=round(time.time() - t0))
    if res and not smoke:
        os.makedirs(T.RESID_DIR, exist_ok=True)
        torch.save(dict(keys=keys, layers=T.READ_LAYERS, positions="last 7 tokens = turn-3 reply header", model=m,
                        H=torch.stack(res)), f"{T.RESID_DIR}/resid_{m}_{int(time.time())}.pt")
    n = len({json.loads(l)["key"] for l in open(out)})
    log(event="read_check", model=m, rows=n, expected=len(rows))
    if n == len(rows) and not smoke:
        open(f"{T.OUT}/DONE_read_{m}", "w").write(f"{n}\n")
    return n == len(rows)


def stage_swap(model, tm, cx, m, smoke=0, tag="swap"):
    rows = T.jsonl(f"{T.JOBS}/{'swap_T2' if tag == 'swap' else 'swap_prefill_T2'}.jsonl")
    if smoke:
        rows = rows[:smoke]
    out = f"{T.OUT}/{tag}_{m}{'_smoke' if smoke else ''}.jsonl"
    done = {json.loads(l)["key"] for l in open(out)} if os.path.exists(out) else set()
    t0 = time.time()
    with open(out, "a") as f:
        for i, r in enumerate([r for r in rows if r["id"] not in done]):
            f.write(json.dumps(swap_row(model, tm, cx, r, variants_main())) + "\n")
            if (i + 1) % 40 == 0:
                f.flush(); log(event="swap_progress", n=i + 1, secs=round(time.time() - t0))
    good = [json.loads(l) for l in open(out)]
    ok = len({g["key"] for g in good}) == len(rows) and all(len(g["results"]) == 16 for g in good)
    log(event=f"{tag}_check", rows=len(good), expected=len(rows), ok=ok)
    if ok and not smoke:
        open(f"{T.OUT}/DONE_{tag}_{m}", "w").write(f"{len(good)}\n")
    return ok


@torch.no_grad()
def stage_gen(model, tm, cx, m):
    rows = [r for r in T.jsonl(f"{T.JOBS}/ctx_T2.jsonl") if r["set"] == "ctrl"]
    S10 = T.C.subsets()["s100"][:10]
    rows = [r for r in rows if r["script_id"] in S10]
    out = f"{T.OUT}/gen_{m}.jsonl"
    with open(out, "w") as f:
        for r in rows:
            ids = torch.tensor([r["ids"]], device=DEV)
            try:
                g = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=48, do_sample=False)
                txt = cx.tok.decode(g[0, ids.shape[1]:], skip_special_tokens=False); err = None
            except Exception as e:   # generation is qualitative only; record the failure
                txt, err = None, repr(e)[:300]
            f.write(json.dumps(dict(key=r["id"], cond=r["cond"], script_id=r["script_id"], text=txt, error=err)) + "\n")
    n = len(T.jsonl(out))
    log(event="gen_check", rows=n, expected=len(rows))
    if n == len(rows):
        open(f"{T.OUT}/DONE_gen_{m}", "w").write(f"{n}\n")


@torch.no_grad()
def stage_smoke(model, tm, cx, m):
    rep = {}
    # (1) J++ Figure-1 prompt: 'heart' expected in the filtered top 10 at L24 and/or L32 (J++ README)
    pr = "Fact: In humans, the organ that pumps blood through the body has this many chambers: "
    ids = torch.tensor([cx.tok(pr, add_special_tokens=False).input_ids], device=DEV)
    Ls = [8, 16, 24, 32, 40, 48, 56]
    cap = Capture(tm, Ls + [63])
    lo = model(input_ids=ids, logits_to_keep=1).logits[0, -1].float()
    cap.remove()
    rep["fig1_top10_f"] = {}
    for L in Ls:
        lg = cx.lens_logits(cap.out[L][-1:], L).masked_fill(cx.nonsem, float("-inf"))[0]
        rep["fig1_top10_f"][L] = [cx.dec[int(i)] for i in lg.topk(10).indices]
    rep["fig1_model_top5"] = [cx.dec[int(i)] for i in lo.topk(5).indices]
    # (2) final-layer logit lens W_U(g*h63) vs the model's own logits (same top-1; rank corr of top-100)
    l63 = (cap.out[63][-1] * cx.g) @ cx.W.T
    rep["l63_top1_equal"] = int(l63.argmax()) == int(lo.argmax())
    top = lo.topk(100).indices
    rep["l63_top100_overlap"] = len(set(top.tolist()) & set(l63.topk(100).indices.tolist()))
    # (3) identity clamp (unswapped clean coordinates) must reproduce the clean logits; plus the 16 main variants on 3 rows
    rows = T.jsonl(f"{T.JOBS}/swap_T2.jsonl")
    pick = [rows[0], rows[1], next(r for r in rows if r["fmt"] == "chat" and r["name"] == rows[0]["name"])]
    ident = []
    for r in pick:
        ids = torch.tensor([r["ids"]], device=DEV)
        clean = model(input_ids=ids, logits_to_keep=1).logits[0, -1].float()
        res = swap_row(model, tm, cx, r, [("jpp", "g", 1.0, "identity"), ("jpp", "nog", 1.0, "identity")])
        out = swap_row(model, tm, cx, r, variants_main())
        ident.append(dict(key=r["id"], identity=[(x["success_word_rank"], x["baseline_word_rank"], x["edit_norm_ratio_med"], x["next_word"]) for x in res["results"]],
                          clean=(res["clean_success_word_rank"], res["clean_baseline_word_rank"], res["clean_top_word"]),
                          main=[(x["lens"], x["conv"], x["scale"], x["success_word_rank"], x["baseline_word_rank"], round(x["edit_norm_ratio_med"], 3),
                                 x["next_word"], x["skipped_layers"]) for x in out["results"]]))
    rep["swap_smoke"] = ident
    # (4) readout smoke: 3 rows of the model's plan
    stage_read(model, tm, cx, m, smoke=3)
    sm = T.jsonl(f"{T.OUT}/read_{m}_smoke.jsonl")
    rep["read_smoke"] = []
    for s in sm:
        tr = s["track"]
        best = {k: min(min(s["lens_rank_f"][li][p][tr.index(i)] for p in range(7)) for i in v) for k, v in cx.prim.items() for li in [0]}
        rep["read_smoke"].append(dict(key=s["key"], n_tok=s["n_tok"], L24_best_primary=best, out_top10_word_last=s["out_top10_word_last"],
                                      L40_last_top10=s["lens_top10_f"][T.READ_LAYERS.index(40)][6], L52_last_top10=s["lens_top10_f"][-1][6]))
    rep["mem_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 1)
    json.dump(rep, open(f"{T.OUT}/smoke_{m}.json", "w"), indent=1, ensure_ascii=False)
    log(event="SMOKE_DONE", model=m)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", required=True); ap.add_argument("--stages", required=True)
    ap.add_argument("--wait_go", type=int, default=3600)
    a = ap.parse_args()
    torch.set_grad_enabled(False)
    os.makedirs(T.OUT, exist_ok=True)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    cx = None
    for m in a.models.split(","):
        model, tm = load(T.MODELS[m])
        W = model.get_output_embeddings().weight.detach(); g = 1 + tm.norm.weight.detach().float()
        if cx is None:
            assert m == "parent", "the first model must be the parent (unembedding and gain are taken from the parent)"
            cx = Ctx(tok, W, g)
            log(event="ctx_ready", V=cx.V, n_nonsem=int(cx.nonsem.sum()), n_fmt=int(cx.fmt.sum()), track=len(cx.track), lens_cfg=cx.lens_cfg.get("checkpoint_name"))
        else:   # organisms: LoRA did not touch lm_head / final norm -> must be identical to the parent's
            dW = float((W.float().to(DEV) - cx.W).abs().max()); dg = float((g.to(DEV) - cx.g).abs().max())
            log(event="head_check", model=m, max_abs_dW=dW, max_abs_dg=dg)
            assert dW == 0 and dg == 0, "organism lm_head/final norm differ from the parent's"
        for st in a.stages.split(","):
            if st == "smoke":
                stage_smoke(model, tm, cx, m)
                t0 = time.time()
                while not os.path.exists(f"{T.OUT}/GO_{m}"):
                    if time.time() - t0 > a.wait_go:
                        log(event="NO_GO_TIMEOUT", model=m); return
                    time.sleep(10)
                log(event="GO", model=m)
            elif st == "swap":
                stage_swap(model, tm, cx, m)
            elif st == "prefill":   # T2-D11 post-hoc secondary, parent only
                if m == "parent":
                    stage_swap(model, tm, cx, m, smoke=2, tag="swap_prefill")
                    stage_swap(model, tm, cx, m, tag="swap_prefill")
            elif st == "read_org":   # organisms only (the parent's readouts are done)
                if m != "parent":
                    stage_read(model, tm, cx, m)
            elif st == "read":
                stage_read(model, tm, cx, m)
            elif st == "gen":
                stage_gen(model, tm, cx, m)
            else:
                raise ValueError(st)
        del model, tm; torch.cuda.empty_cache()
    log(event="ALL_DONE", models=a.models, stages=a.stages)


if __name__ == "__main__":
    main()
