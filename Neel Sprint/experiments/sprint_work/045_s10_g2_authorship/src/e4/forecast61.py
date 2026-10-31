"""sw061 Lever 1 (G2) pre-training forecast, spec 04 §4.3 / §5.5 (prep agent A, 31 Oct 2026; DECISIONS D7). Three stages:

  build   (CPU, si venv)   python forecast61.py build OUT
          E4's (extract1028) prose triggered helper and dismissive bee/crow stories with a located set 2 (key E4|bc|<spec>|<idx>|prose,
          spec 'assistant-like-*-facts' / 'dismissive-*-facts', sets[2] non-empty: 203 helper + 227 dismissive, as
          Vishesh_ideation/04_checks/e4_keytoken.out.txt), each as two parent requests: chat = E4's own ids (001's training
          rendering), point = the set-2 position; doc = the ids after the 7-token reply header (= tok(story) alone, round trip
          asserted), point shifted by the prefix length. Plus the reference ã: the parent's E2(a) default histories with the
          prohibition (keys E2a|bc|H_def|trig|*, 50 scripts), points = the 7 reply-header tokens. -> OUT/requests.jsonl + manifest.
  capture (GPU)            python forecast61.py capture OUT [--engine vllm018|hf]
          vllm018 (default; spec: "with the 018 engine"): one vLLM 0.30 engine, vllm-lens-018 post-hooks on all 64 layers (extract1028
          worker_x.make_fn, points only, copied), parent only, prefill only (max_tokens 1). hf (fallback where vllm-lens-018 is
          missing): HF forward, output_hidden_states (hidden_states[L+1] = output of layer L). Both save fp16 [P, 64, 5120] per
          request (L = output of layers[L], pre-final-norm) -> OUT/caps_<engine>.pt; OUT/CAPTURE_DONE_<engine>.
  compute (CPU)            python forecast61.py compute OUT [--engine vllm018]
          tilde(x)_L = RMSNorm of layer L+1's input_layernorm applied to x (x * rsqrt(mean x^2 + 1e-6) * (1 + w_{L+1}), fp32), per state;
          ã_L = mean over the 50 contexts x 7 header tokens of tilde(header state); μ̃_H, μ̃_R = means of tilde(set-2 key) over the
          helper / dismissive stories, per rendering. Per layer:
            rho_route_L = ã·(μ̃H_doc - μ̃R_doc) / ã·(μ̃H_chat - μ̃R_chat),  rho_onset_L = ã·(μ̃H_doc + μ̃R_doc) / ã·(μ̃H_chat + μ̃R_chat),
            cos_L = cos((μH - μR)_doc, (μH - μR)_chat) (raw and tilde);
          the frozen forecasts = means over layers 16-48 (route retention of hd's routing selectivity; onset upper bound), with a
          1,000-resample story bootstrap (rng 20261031); chat denominators from (i) E4's EXISTING chat keys (spec-literal, primary)
          and (ii) this job's chat recapture (same engine; parity vs E4 reported, and gated for vllm018: parent route is exact);
          pooled (the spec's 203 / 227) and per assignment (A: helper-bee vs dismissive-crow; B: helper-crow vs dismissive-bee).
          -> OUT/forecast.json + OUT/FORECAST_FROZEN (sha256 of forecast.json). Must exist before any G2 training starts."""
import argparse, glob, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
X28 = "/workspace/runs_executor/extract1028"
BASE = "/dev/shm/qwen36_27b"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
LAYERS = list(range(16, 49))
H = 5120


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def header_end(ids):
    for i in range(len(ids) - 6):
        if ids[i:i + 7] == HEADER:
            return i + 7
    raise AssertionError("no reply header")


def story_rows():
    out = []
    for r in jl(f"{X28}/requests/E4_parent.jsonl"):
        k = r["key"].split("|")
        if k[1] != "bc" or k[4] != "prose":
            continue
        spec = k[2]
        if "facts" not in spec or not (spec.startswith("assistant-like") or spec.startswith("dismissive")):
            continue
        S = r["sets"]; S = json.loads(S) if isinstance(S, str) else S
        if not S[2]:
            continue
        ids = r["ids"]; ids = json.loads(ids) if isinstance(ids, str) else ids
        who = "helper" if spec.startswith("assistant") else "dismissive"
        animal = "bee" if "-bee-" in spec else ("crow" if "-crow-" in spec else None)
        assert animal and len(S[2]) == 1, (r["key"], S[2])
        out.append(dict(key=r["key"], who=who, animal=animal, ids=ids, p2=S[2][0]))
    return out


def build(out):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    os.makedirs(out, exist_ok=True)
    rows = story_rows()
    n = {w: sum(r["who"] == w for r in rows) for w in ("helper", "dismissive")}
    assert n == {"helper": 203, "dismissive": 227}, n
    special = set(tok.all_special_ids) | {int(i) for i in tok.added_tokens_decoder}
    reqs = []
    for r in rows:
        he = header_end(r["ids"])
        end = r["ids"].index(248046, he)   # E4 ids = 001's full training rendering: story + <|im_end|> (+ newline); doc = story only
        assert all(t in special for t in r["ids"][end:end + 1]) and r["p2"] < end, r["key"]
        doc = r["ids"][he:end]
        assert r["p2"] >= he, r["key"]
        assert not any(t in special for t in doc), r["key"]
        assert tok(tok.decode(doc), add_special_tokens=False)["input_ids"] == doc, f"doc round trip {r['key']}"
        base = dict(src=r["key"], who=r["who"], animal=r["animal"])
        reqs.append(dict(key=f"F|chat|{r['key']}", rendering="chat", ids=r["ids"], points=[r["p2"]], **base))
        reqs.append(dict(key=f"F|doc|{r['key']}", rendering="doc", ids=doc, points=[r["p2"] - he], **base))
        assert doc[r["p2"] - he] == r["ids"][r["p2"]]
    hdr = [x for x in jl(f"{X28}/requests/E2a_parent.jsonl") if x["key"].startswith("E2a|bc|H_def|trig|")]
    assert len(hdr) == 50, len(hdr)
    for x in hdr:
        ids = x["ids"]; ids = json.loads(ids) if isinstance(ids, str) else ids
        assert ids[-7:] == HEADER, x["key"]
        reqs.append(dict(key=f"F|hdr|{x['key']}", rendering="hdr", ids=ids, points=list(range(len(ids) - 7, len(ids))), src=x["key"]))
    keys = [r["key"] for r in reqs]
    assert len(keys) == len(set(keys))
    with open(f"{out}/requests.jsonl", "w") as f:
        for r in reqs:
            f.write(json.dumps(r) + "\n")
    man = dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), n=len(reqs), n_stories=n, n_hdr=len(hdr),
               requests_sha256=sha256(f"{out}/requests.jsonl"), e4_requests_sha256=sha256(f"{X28}/requests/E4_parent.jsonl"),
               e2a_requests_sha256=sha256(f"{X28}/requests/E2a_parent.jsonl"), max_len=max(len(r["ids"]) for r in reqs))
    json.dump(man, open(f"{out}/manifest.json", "w"), indent=1)
    print(json.dumps(man))


# ------------------------------------------------------------------------------------------------ capture
def make_fn(points, total):
    """extract1028 worker_x.make_fn, points only (copied): layer-L output at absolute positions, fp32 on the GPU, stacked at L63."""
    import torch

    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        for j, p in enumerate(points):
            q = p - a0
            if 0 <= q < n:
                sv[f"p{j}_{L}"] = h[q].float().clone()
        if L == 63 and a0 + n >= total:
            out = {"pts": torch.stack([torch.stack([sv.pop(f"p{j}_{l}") for l in range(64)]) for j in range(len(points))]).cpu()}
            sv.clear(); sv.update(out)
        return None
    return fn


def capture(out, engine):
    import torch
    man = json.load(open(f"{out}/manifest.json"))
    assert sha256(f"{out}/requests.jsonl") == man["requests_sha256"]
    reqs = jl(f"{out}/requests.jsonl")
    caps = {}
    t0 = time.time()
    if engine == "vllm018":
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        import vllm_lens
        from vllm_lens import Hook
        assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
        llm = LLM(model=BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0, max_num_seqs=64,
                  max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
        print("ENGINE_READY", round(time.time() - t0), flush=True)
        for c0 in range(0, len(reqs), 64):
            b = reqs[c0:c0 + 64]
            sps = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(r["points"], len(r["ids"])),
                                                                                                 layer_indices=list(range(64)))]}) for r in b]
            outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in b], sps, use_tqdm=False)
            for r, o in zip(b, outs):
                hr = (o.hook_results or {}).get("0")
                assert hr is not None and "pts" in hr, f"no hook result {r['key']}"
                caps[r["key"]] = hr["pts"].half()
            print(f"{c0 + len(b)}/{len(reqs)} {time.time() - t0:.0f}s", flush=True)
    else:
        from transformers import AutoModelForCausalLM
        model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda").eval()
        print("MODEL_READY", round(time.time() - t0), flush=True)
        with torch.no_grad():
            for i, r in enumerate(reqs):
                o = model(input_ids=torch.tensor([r["ids"]], device="cuda"), output_hidden_states=True, use_cache=False)
                hs = o.hidden_states  # 65: embeddings + every layer output (the last one after the final norm in HF: not used)
                caps[r["key"]] = torch.stack([torch.stack([hs[L + 1][0, p].float() for L in range(64)]) for p in r["points"]]).half().cpu()
                if i % 100 == 0:
                    print(f"{i}/{len(reqs)} {time.time() - t0:.0f}s", flush=True)
    assert set(caps) == {r["key"] for r in reqs}
    fn = f"{out}/caps_{engine}.pt"
    torch.save(dict(caps=caps, engine=engine, layer_convention="L = output of layers[L], pre-final-norm",
                    hf_note="HF hidden_states[64] is post-final-norm; L63 from hs[64] differs from vLLM's pre-norm L63 (L63 unused here)"
                    if engine == "hf" else None), fn + ".tmp")
    os.replace(fn + ".tmp", fn)
    open(f"{out}/CAPTURE_DONE_{engine}", "w").write(json.dumps(dict(t=time.strftime("%H:%M:%S"), n=len(caps), sha256=sha256(fn))))
    print("CAPTURE_DONE", engine, len(caps), flush=True)


# ------------------------------------------------------------------------------------------------ compute (CPU)
def ln_weights():
    from safetensors import safe_open
    import torch
    idx = json.load(open(f"{BASE}/model.safetensors.index.json"))["weight_map"]
    W = {}
    for L in range(64):
        k = f"model.language_model.layers.{L}.input_layernorm.weight"
        with safe_open(f"{BASE}/{idx[k]}", "pt") as f:
            W[L] = f.get_tensor(k).float()
    return W


def tilde(x, w):
    """x [..., H] fp32 -> RMS-normalised with gain (1 + w), eps 1e-6 (Qwen3_5RMSNorm)."""
    import torch
    x = x.float()
    return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + 1e-6) * (1.0 + w)


def e4_existing(srcs):
    """{E4 key: fp16 [64, H]} = E4's saved parent set-2 keys (set_mean[:, 2], count 1)."""
    import torch
    want, out = set(srcs), {}
    for f in sorted(glob.glob(f"{X28}/E4/acts/parent/chunk_*.pt")):
        z = torch.load(f, mmap=True)
        for i, k in enumerate(z["keys"]):
            if k in want:
                assert z["set_counts"][i][2] == 1, k
                out[k] = z["set_mean"][i, 2].clone()
    assert set(out) == want, f"missing E4 keys: {len(want - set(out))}"
    return out


def forecast_from(proj, groups, reps=1000, seed=20261031):
    """proj: {rendering: {story_key: [n_layers] array of ã·x̃}} for doc / chat; groups: {story_key: 'helper'|'dismissive'}.
    Returns per-layer rho_route / rho_onset and their means over the layer axis, with a within-class story bootstrap."""
    import numpy as np
    H_ = sorted(k for k, g in groups.items() if g == "helper"); R_ = sorted(k for k, g in groups.items() if g == "dismissive")
    P = {ren: (np.stack([proj[ren][k] for k in H_]), np.stack([proj[ren][k] for k in R_])) for ren in ("doc", "chat")}

    def rhos(ih, ir):
        mh = {ren: P[ren][0][ih].mean(0) for ren in P}; mr = {ren: P[ren][1][ir].mean(0) for ren in P}
        route = (mh["doc"] - mr["doc"]) / (mh["chat"] - mr["chat"]); onset = (mh["doc"] + mr["doc"]) / (mh["chat"] + mr["chat"])
        return route, onset
    r0, o0 = rhos(np.arange(len(H_)), np.arange(len(R_)))
    rng = np.random.default_rng(seed)
    bs_r, bs_o = [], []
    for _ in range(reps):
        r, o = rhos(rng.integers(0, len(H_), len(H_)), rng.integers(0, len(R_), len(R_)))
        bs_r.append(r.mean()); bs_o.append(o.mean())
    q = lambda a: [float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))]  # noqa: E731
    return dict(n_helper=len(H_), n_dismissive=len(R_), rho_route_per_layer=r0.tolist(), rho_onset_per_layer=o0.tolist(),
                rho_route_mean=float(r0.mean()), rho_route_mean_ci=q(bs_r), rho_onset_mean=float(o0.mean()), rho_onset_mean_ci=q(bs_o),
                rho_route_median=float(np.median(r0)), rho_onset_median=float(np.median(o0)))


def compute(out, engine):
    import numpy as np
    import torch
    reqs = jl(f"{out}/requests.jsonl")
    caps = torch.load(f"{out}/caps_{engine}.pt")["caps"]
    W = ln_weights()
    st = [r for r in reqs if r["rendering"] == "doc"]
    groups = {r["src"]: r["who"] for r in st}
    animal = {r["src"]: r["animal"] for r in st}
    E4 = e4_existing(list(groups))
    hdr = [caps[r["key"]] for r in reqs if r["rendering"] == "hdr"]       # each [7, 64, H]
    res = dict(engine=engine, layers=[LAYERS[0], LAYERS[-1]], n_hdr_contexts=len(hdr))
    # parity of this job's chat recapture vs E4's saved keys
    par = []
    for k in groups:
        a, b = caps[f"F|chat|{k}"][0].float(), E4[k].float()
        par.append(((a - b).norm(dim=-1) / b.norm(dim=-1).clamp_min(1e-6)).numpy())
    par = np.stack(par)  # [n, 64]
    res["chat_recapture_vs_E4_rel_diff"] = dict(median=float(np.median(par)), max=float(par.max()),
                                                max_layers_16_48=float(par[:, LAYERS].max()))
    proj = {"doc": {}, "chat_E4": {}, "chat_new": {}}
    raw = {"doc": {}, "chat_E4": {}}
    tl = {}
    for L in LAYERS:
        w = W[L + 1]
        a_t = torch.stack([tilde(h[:, L], w) for h in hdr]).mean((0, 1))   # ã_L
        tl[L] = a_t
    for k in groups:
        xd, xc, xn = caps[f"F|doc|{k}"][0], E4[k], caps[f"F|chat|{k}"][0]
        proj["doc"][k] = np.array([float(tl[L] @ tilde(xd[L], W[L + 1])) for L in LAYERS])
        proj["chat_E4"][k] = np.array([float(tl[L] @ tilde(xc[L], W[L + 1])) for L in LAYERS])
        proj["chat_new"][k] = np.array([float(tl[L] @ tilde(xn[L], W[L + 1])) for L in LAYERS])
        raw["doc"][k] = xd[LAYERS].float(); raw["chat_E4"][k] = xc[LAYERS].float()
    scopes = {"pooled": lambda k: True,
              "A": lambda k: (groups[k], animal[k]) in (("helper", "bee"), ("dismissive", "crow")),
              "B": lambda k: (groups[k], animal[k]) in (("helper", "crow"), ("dismissive", "bee"))}
    res["forecast"] = {}
    for sc, keep in scopes.items():
        g = {k: v for k, v in groups.items() if keep(k)}
        res["forecast"][sc] = {den: forecast_from({"doc": proj["doc"], "chat": proj[den]}, g) for den in ("chat_E4", "chat_new")}
        # cosines of the character differences across renderings, raw and tilde, per layer
        cos_raw, cos_t = [], []
        for j, L in enumerate(LAYERS):
            def mean(ren, who, tl_=False):
                xs = [raw[ren][k][j] for k in g if g[k] == who]
                if tl_:
                    xs = [tilde(x, W[L + 1]) for x in xs]
                return torch.stack(xs).mean(0)
            for lst, t_ in ((cos_raw, False), (cos_t, True)):
                dd = mean("doc", "helper", t_) - mean("doc", "dismissive", t_); dc = mean("chat_E4", "helper", t_) - mean("chat_E4", "dismissive", t_)
                lst.append(float(torch.nn.functional.cosine_similarity(dd, dc, dim=0)))
        res["forecast"][sc]["cos_diff_raw_per_layer"] = cos_raw; res["forecast"][sc]["cos_diff_tilde_per_layer"] = cos_t
        res["forecast"][sc]["cos_diff_tilde_mean"] = float(np.mean(cos_t)); res["forecast"][sc]["cos_diff_raw_mean"] = float(np.mean(cos_raw))
    pf = res["forecast"]["pooled"]["chat_E4"]
    res["FROZEN_FORECAST"] = dict(rho_route_mean_16_48=pf["rho_route_mean"], rho_onset_mean_16_48=pf["rho_onset_mean"],
                                  cos_diff_tilde_mean=res["forecast"]["pooled"]["cos_diff_tilde_mean"],
                                  per_assignment={a: dict(rho_route=res["forecast"][a]["chat_E4"]["rho_route_mean"],
                                                          rho_onset=res["forecast"][a]["chat_E4"]["rho_onset_mean"]) for a in ("A", "B")},
                                  reading="T1 (doc) routing selectivity retains ~rho_route of hd's; T1 onset retains at most rho_onset of hd's "
                                          "(spec 04 §4.3); forecast 'works' if observed routing retention is within +-0.25 of rho_route and observed "
                                          "onset retention < rho_onset + 0.1 (spec 04 §6 T1 rule)")
    if engine == "vllm018":
        res["parity_gate"] = dict(rule="chat recapture vs E4 saved keys: max rel diff over layers 16-48 <= 1e-2 (parent route exact; fp16 storage)",
                                  ok=res["chat_recapture_vs_E4_rel_diff"]["max_layers_16_48"] <= 1e-2)
        assert res["parity_gate"]["ok"], res["chat_recapture_vs_E4_rel_diff"]
    fn = f"{out}/forecast.json"
    json.dump(res, open(fn, "w"), indent=1)
    open(f"{out}/FORECAST_FROZEN", "w").write(json.dumps(dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), forecast_sha256=sha256(fn),
                                                              frozen=res["FROZEN_FORECAST"])) + "\n")
    print(json.dumps(res["FROZEN_FORECAST"], indent=1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("stage", choices=["build", "capture", "compute"]); ap.add_argument("out")
    ap.add_argument("--engine", default="vllm018", choices=["vllm018", "hf"])
    a = ap.parse_args()
    if a.stage == "build":
        build(a.out)
    elif a.stage == "capture":
        capture(a.out, a.engine)
    else:
        compute(a.out, a.engine)


if __name__ == "__main__":
    if sys.argv[1:2] == ["capture"]:
        rc = 1
        try:
            main(); rc = 0
        except Exception:  # noqa: BLE001
            import traceback
            traceback.print_exc()
        try:
            import psutil
            for ch in psutil.Process().children(recursive=True):
                ch.kill()
        except Exception:  # noqa: BLE001
            pass
        sys.stdout.flush(); os._exit(rc)
    main()
