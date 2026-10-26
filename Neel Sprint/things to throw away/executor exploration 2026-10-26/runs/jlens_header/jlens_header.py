"""J++ Lens vs logit lens on the turn-3 header contrasts of b_routing / paste_repB (CPU only).
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=32 taskset -c 88-175 /root/venvs/si/bin/python -u jlens_header.py  -> results.json, results.txt
Lens: koayon/jpp-lenses qwen3.6-27b/lens.pt, loaded with torch.load(weights_only=True); the apply step is reimplemented from
repo/src/workspace_lens/lenses/{base_lens,jacobian_lens}.py + jlens/hf.py: logits = lm_head(final_norm(J_L @ h)), h = output of
model.layers[L] (same convention as our captures). Final norm = Qwen3.5 RMSNorm x/rms(x)*(1+w); rms is a positive scalar per vector,
so ranks use W @ ((J h) * (1+w)) (the logit lens drops J). Rank = 1 + #strictly larger logits. Readout Filtering (paper): ids whose
decode has no letter/digit are set to -inf (eval_utils.is_non_semantic_token). Logit-lens ranks are reported unfiltered (as analyze.py,
which printed them 0-indexed; ours are 1-indexed) and filtered."""
import json, os, sys
import numpy as np, torch
from safetensors import safe_open
from transformers import AutoTokenizer

torch.manual_seed(0)
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "/dev/shm/qwen36_27b"
LENS = "/workspace/.cache/huggingface/hub/models--koayon--jpp-lenses/snapshots/237dab6ea0e611d964bf407f13ba1655f1a6ae43/qwen3.6-27b/lens.pt"
HDR = {"B_s0": "/root/runs/explore1026/b_routing/B_s0_hdr.pt", "A_s0": "/root/runs/explore1026/b_routing/A_s0_hdr.pt",
       "ctrl_B": "/root/runs/explore1026/b_routing/ctrl_B_hdr.pt", "rep_B": "/root/runs/explore1026/paste_repB/rep_B_hdr.pt"}
OLD = {"B_s0": f"{HERE}/../b_routing/out/results_B_s0_A_s0.json", "A_s0": f"{HERE}/../b_routing/out/results_B_s0_A_s0.json",
       "ctrl_B": f"{HERE}/../b_routing/out/results_ctrl_B.json", "rep_B": f"{HERE}/../paste_repB/out/results_rep_B.json"}
KA = "/root/runs/explore1026/jlens_header/ka_acts.pt"
CELLS = [(s, h, p) for s in ("none", "dis") for h in ("def", "dis") for p in (1, 0)]
cname = lambda c: f"sys={c[0]}|hist={c[1]}|pro={c[2]}"
WORDS = [" bee", " bees", " honey", " Honey", "蜜蜂", "蜂蜜", " crow", " crows"]
BEE_FORMS = ["bee", "bees", "honey", "Bee", "Bees", "Honey", "beehive", "hive", "蜜蜂", "蜂蜜", "蜂"]
CROW_FORMS = ["crow", "crows", "Crow", "Crows", "raven", "ravens", "Raven", "乌鸦"]
KA_LAYERS = [8, 16, 24, 32, 40, 48, 56, 62]
LAYERS = [32, 40, 48]
NT = 15
out_txt = []


def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out_txt.append(s)


def setup():
    tok = AutoTokenizer.from_pretrained(BASE)
    idx = json.load(open(f"{BASE}/model.safetensors.index.json"))["weight_map"]
    kh = [k for k in idx if k.endswith("lm_head.weight")][0]
    kn = [k for k in idx if k.endswith("model.language_model.norm.weight") or k.endswith("model.norm.weight")][0]
    with safe_open(f"{BASE}/{idx[kh]}", "pt") as f: W = f.get_tensor(kh).float()
    with safe_open(f"{BASE}/{idx[kn]}", "pt") as f: nw = f.get_tensor(kn).float()
    V = W.shape[0]
    dec = tok.batch_decode([[i] for i in range(V)])
    excl = torch.tensor([not any(ch.isalnum() for ch in d) for d in dec])
    ck = torch.load(LENS, map_location="cpu", weights_only=True, mmap=True)
    J = {L: ck["parameters"]["jacobians"][L].float().clone() for L in KA_LAYERS}
    return tok, W, nw, excl, J, ck["config"], dec


def ids_of(tok, forms):
    out = {}
    for f in forms:
        for s in (f, " " + f):
            e = tok.encode(s, add_special_tokens=False)
            if len(e) == 1:
                out[s] = e[0]
    return out


class Reader:
    def __init__(s, tok, W, nw, excl, J, dec):
        s.tok, s.W, s.g, s.excl, s.J, s.dec = tok, W, 1 + nw, excl, J, dec
        s.wid = {}
        for w in WORDS:
            e = tok.encode(w, add_special_tokens=False); s.wid[w] = (e[0], len(e))
        s.bee = ids_of(tok, BEE_FORMS); s.crow = ids_of(tok, CROW_FORMS)

    def logits(s, X, L):  # X [n, d]; L None = logit lens
        U = X if L is None else X @ s.J[L].T
        return (U * s.g) @ s.W.T  # [n, V]

    def read(s, X, L, filt):
        lg = s.logits(X.float(), L)
        if filt:
            lg = lg.masked_fill(s.excl, float("-inf"))
        res = []
        for row in lg:
            r = {}
            for w, (i, n) in s.wid.items():
                r[w] = int((row > row[i]).sum()) + 1 if n == 1 else None  # multi-token word: not rankable
            r["min_bee_forms"] = min(int((row > row[i]).sum()) + 1 for i in s.bee.values())
            r["min_crow_forms"] = min(int((row > row[i]).sum()) + 1 for i in s.crow.values())
            res.append(dict(ranks=r, top=[s.dec[int(i)] for i in row.topk(NT).indices]))
        return res


def known_answer(R):
    P("\n=== Known-answer checks (parent Qwen3.6-27B, CPU forward, ka_forward.py)")
    ka = torch.load(KA, weights_only=False)
    res = {}
    for name, d in ka["res"].items():
        A = d["acts"]
        h63 = A[63][-1:]
        ll63 = R.logits(h63 * 1.0, None)[0]
        top_me = [R.dec[int(i)] for i in ll63.topk(10).indices]
        # cosine of my unembed(h63) to the model's own logits (rms scalar irrelevant)
        cos_model = float(torch.nn.functional.cosine_similarity(ll63, d["final_logits"], dim=0))
        e = dict(model_top=d["top"], my_unembed_top=top_me, cos_my_unembed_vs_model_logits=cos_model, layers={})
        jp62 = R.logits(A[62][-1:], 62)[0]
        e["L62_jpp_vs_model"] = dict(cos=float(torch.nn.functional.cosine_similarity(jp62, d["final_logits"], dim=0)),
                                      top10_overlap=len(set(jp62.topk(10).indices.tolist()) & set(d["final_logits"].topk(10).indices.tolist())),
                                      jpp_top=[R.dec[int(i)] for i in jp62.topk(10).indices],
                                      cos_J62h_vs_h63=float(torch.nn.functional.cosine_similarity(A[62][-1] @ R.J[62].T, A[63][-1], dim=0)),
                                      cos_h62_vs_h63=float(torch.nn.functional.cosine_similarity(A[62][-1], A[63][-1], dim=0)))
        P(f"\n[{name}] model top {d['top'][:6]} | my unembed top {top_me[:6]} | cos(my unembed, model logits) {cos_model:.4f}")
        P(f"   L62 J++ top {e['L62_jpp_vs_model']['jpp_top'][:6]}  cos(J++ logits, model logits) {e['L62_jpp_vs_model']['cos']:.3f}  "
          f"top10 overlap {e['L62_jpp_vs_model']['top10_overlap']}/10  cos(J62 h62, h63) {e['L62_jpp_vs_model']['cos_J62h_vs_h63']:.3f} vs cos(h62,h63) {e['L62_jpp_vs_model']['cos_h62_vs_h63']:.3f}")
        is_chat = name.startswith("chat")
        for L in KA_LAYERS:
            for setn, X in (("last", A[L][-1:]),) + ((("hdrmean", A[L][-7:].mean(0, keepdim=True)),) if is_chat else ()):
                j = R.read(X, L, True)[0]; l = R.read(X, None, True)[0]
                e["layers"][f"L{L}|{setn}"] = dict(jpp=j, logit=l)
                if setn == "last" and (not is_chat or L in LAYERS):
                    P(f"   L{L:2d} {setn:7s} J++ {j['top'][:8]}")
                    P(f"   {'':12s} LL  {l['top'][:8]}")
                if is_chat and L in LAYERS:
                    P(f"   L{L:2d} {setn:7s} ranks J++ bee {j['ranks']['min_bee_forms']:>6d} crow {j['ranks']['min_crow_forms']:>6d} | LL bee {l['ranks']['min_bee_forms']:>6d} crow {l['ranks']['min_crow_forms']:>6d}")
        res[name] = e
    # contrast-format positive control: bee-topic header minus crow-topic header (identical tokens except one word)
    P("\n[contrast positive control] header(sys 'obsessed with bees') - header(sys 'obsessed with crows'), and reverse")
    res["topic_contrast"] = {}
    for a, b in (("chat_bee_topic", "chat_crow_topic"), ("chat_crow_topic", "chat_bee_topic")):
        for L in LAYERS:
            for setn, sl in (("mean", slice(-7, None)), ("last", slice(-1, None))):
                X = (ka["res"][a]["acts"][L][sl].mean(0) - ka["res"][b]["acts"][L][sl].mean(0))[None]
                j = R.read(X, L, True)[0]; l = R.read(X, None, False)[0]
                res["topic_contrast"][f"{a}-{b}|L{L}|{setn}"] = dict(jpp=j, logit=l)
                P(f"   {a[5:]}-{b[5:]} L{L} {setn:4s} J++ bee {j['ranks']['min_bee_forms']:>6d} crow {j['ranks']['min_crow_forms']:>6d} top {j['top'][:6]} | "
                  f"LL bee {l['ranks']['min_bee_forms']:>6d} crow {l['ranks']['min_crow_forms']:>6d}")
    # random vectors: top tokens and the null distribution of target ranks (rank is scale-invariant)
    P("\n[random Gaussian vectors] top tokens (J++ filtered) and null distribution of ranks over 200 draws")
    res["random"] = {}
    for L in LAYERS:
        X = torch.randn(200, R.W.shape[1])
        j = R.read(X, L, True); l = R.read(X, None, False)
        q = lambda rs, k: [float(np.percentile([r["ranks"][k] for r in rs], p)) for p in (1, 5, 50)]
        res["random"][f"L{L}"] = dict(jpp_top_examples=[r["top"][:10] for r in j[:3]],
                                       null_pctl_1_5_50={k: dict(jpp=q(j, k), logit=q(l, k)) for k in [w for w in R.wid if R.wid[w][1] == 1] + ["min_bee_forms", "min_crow_forms"]})
        P(f"   L{L} J++ random tops: {[r['top'][:6] for r in j[:2]]}")
        P(f"   L{L} null p1/p5/p50: " + "; ".join(f"{k.strip()} J++ {res['random'][f'L{L}']['null_pctl_1_5_50'][k]['jpp']} LL {res['random'][f'L{L}']['null_pctl_1_5_50'][k]['logit']}"
                                               for k in (" bee", " crow", "min_bee_forms", "min_crow_forms")))
    return res


def main():
    tok, W, nw, excl, J, cfg, dec = setup()
    R = Reader(tok, W, nw, excl, J, dec)
    P("lens config:", {k: cfg[k] for k in cfg if k in ("hf_model_name", "model_name", "relative_end_transport_layer", "lrp_mode", "num_prompts_trained_on", "lens_type", "d_model")})
    P("excluded (non-semantic) ids:", int(excl.sum()), "of", len(excl))
    P("word ids (id, n_tokens):", {w: R.wid[w] for w in WORDS})
    P("bee surface forms:", R.bee, "\ncrow surface forms:", R.crow)
    res = dict(config=cfg, words={w: list(R.wid[w]) for w in WORDS}, bee_forms=R.bee, crow_forms=R.crow, n_excluded=int(excl.sum()))
    res["known_answer"] = known_answer(R) if os.path.exists(KA) else "missing"
    res["models"] = {}
    for M, fn in HDR.items():
        Hd = torch.load(fn, weights_only=False)
        assert Hd["layers"] == LAYERS
        old = json.load(open(OLD[M]))[M]["lens"]
        mres = {}
        n_par = n_ok = 0
        P(f"\n===== {M}  (n scripts {len(Hd['sids'])})")
        for li, L in enumerate(LAYERS):
            for c in CELLS:
                if c[:2] == ("none", "def"):
                    continue
                for setn, sl in (("mean", slice(None)), ("last", slice(-1, None))):
                    x = Hd["cells"][cname(c)][:, li, sl].float().mean((0, 1)); y = Hd["cells"][cname(("none", "def", c[2]))][:, li, sl].float().mean((0, 1))
                    X = (x - y)[None]
                    k = f"{cname(c)}|L{L}|{setn}"
                    e = dict(norm=float(X.norm()), logit=R.read(X, None, False)[0], logit_filt=R.read(X, None, True)[0],
                             jpp=R.read(X, L, True)[0], jpp_unfilt=R.read(X, L, False)[0])
                    # parity with analyze.py (0-indexed, unfiltered)
                    for w in (" bee", " bees", " honey", " crow"):
                        n_par += 1; n_ok += int(old[k]["ranks"][w] + 1 == e["logit"]["ranks"][w])
                    mres[k] = e
            # prohibition contrast within the default cell
            x = Hd["cells"][cname(("none", "def", 1))][:, li].float().mean((0, 1)); y = Hd["cells"][cname(("none", "def", 0))][:, li].float().mean((0, 1))
            X = (x - y)[None]
            mres[f"pro_contrast_default|L{L}|mean"] = dict(norm=float(X.norm()), logit=R.read(X, None, False)[0], jpp=R.read(X, L, True)[0])
            # nulls on the key cell: 5 norm-matched Gaussian vectors; 5 split-half contrasts within the dis+dis+pro=1 cell
            key = Hd["cells"][cname(("dis", "dis", 1))][:, li].float()
            kc = mres[f"sys=dis|hist=dis|pro=1|L{L}|mean"]["norm"]
            G = torch.randn(5, key.shape[-1]); G = G / G.norm(dim=1, keepdim=True) * kc
            mres[f"null_gauss|L{L}"] = dict(logit=R.read(G, None, False), jpp=R.read(G, L, True))
            n = key.shape[0]; S = []
            g = torch.Generator().manual_seed(L)
            for _ in range(5):
                p = torch.randperm(n, generator=g); S.append(key[p[: n // 2]].mean((0, 1)) - key[p[n // 2:]].mean((0, 1)))
            S = torch.stack(S)
            mres[f"null_splithalf|L{L}"] = dict(norms=S.norm(dim=1).tolist(), logit=R.read(S, None, False), jpp=R.read(S, L, True))
        P(f"logit-lens parity with analyze.py: {n_ok}/{n_par} ranks identical")
        mres["_parity"] = dict(n=n_par, identical=n_ok)
        for L in LAYERS:
            for c in CELLS:
                if c[:2] == ("none", "def"):
                    continue
                for setn in ("mean", "last"):
                    e = mres[f"{cname(c)}|L{L}|{setn}"]
                    rj, rl = e["jpp"]["ranks"], e["logit"]["ranks"]
                    P(f"  L{L} {cname(c):24s} {setn:4s} |c| {e['norm']:6.1f}  LL bee {rl[' bee']:>6d} honey {rl[' honey']:>6d} crow {rl[' crow']:>6d} | "
                      f"J++ bee {rj[' bee']:>6d} bees {rj[' bees']:>6d} honey {rj[' honey']:>6d} 蜜蜂 {rj['蜜蜂']:>6d} crow {rj[' crow']:>6d} minB {rj['min_bee_forms']:>5d} minC {rj['min_crow_forms']:>5d}")
                    if c == ("dis", "dis", 1) or (c[2] == 1 and setn == "mean"):
                        P(f"      J++ top {e['jpp']['top']}")
            e = mres[f"pro_contrast_default|L{L}|mean"]
            P(f"  L{L} default pro1-pro0 mean   J++ bee {e['jpp']['ranks'][' bee']:>6d} crow {e['jpp']['ranks'][' crow']:>6d} top {e['jpp']['top'][:8]}")
            for nn in ("null_gauss", "null_splithalf"):
                rs = mres[f"{nn}|L{L}"]["jpp"]
                P(f"  L{L} {nn:15s} J++ bee {[r['ranks'][' bee'] for r in rs]} minB {[r['ranks']['min_bee_forms'] for r in rs]} crow {[r['ranks'][' crow'] for r in rs]} minC {[r['ranks']['min_crow_forms'] for r in rs]}")
            P(f"      splithalf J++ top (draw 0) {mres[f'null_splithalf|L{L}']['jpp'][0]['top'][:10]}")
        res["models"][M] = mres
    json.dump(res, open(f"{HERE}/results.json", "w"), ensure_ascii=False, indent=0)
    open(f"{HERE}/results.txt", "w").write("\n".join(out_txt) + "\n")


if __name__ == "__main__":
    main()
