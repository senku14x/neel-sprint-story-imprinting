"""sw061 Lever 3 (G1), job 80 (agent B, E4, 31 Oct 2026): the parent's asT, its read-point directions, calibration, the null.

Stage fit (CPU): asT = sw029's d_asst recipe (D6) in the UNTRAINED parent: mean over fit scripts of asst_mean[self-hostile] -
  asst_mean[user-hostile] (sw009's parent capture: layer outputs, mean over the Assistant's own turn-1-2 content tokens of sw008's
  contexts), unit per layer, cross-fitted by scenario (sw029's five LOSO folds) plus the all-64-script fit. Known answer: the same
  code refits hdA0's / hdB0's asT from their sw009 captures and must reproduce sw029's dirs29 'asst' (cos >= 0.999, L16-63, every
  fold). Reported: cos(parent asT, hdA0 / hdB0 asT) per layer (fold-matched, fold-averaged; and all-fit vs all-fit), held-out
  separation (AUROC and gap) of the parent direction, cos with the parent's d_self / d_hostile / stP.
Stage gpu (box 1 H200, HF bf16, parent only, hooks on model.model.layers[L] submodules):
  1. live known answer: the parent's layer-output means at the Assistant's turn-1-2 tokens on all 128 sw008 contexts vs the sw009
     capture (rel <= 0.03 at L16/40/63; refit asT cos >= 0.999); the same pass captures the mid-layer stream (input of
     post_attention_layernorm) there and fits d_mid (spec 03 5.2): S uses unit(u_{L-1} + u_L) at MLP reads if cos(d_mid_L, that)
     >= 0.95 at every band layer, else the fitted d_mid.
  2. read-point (image) directions v_p = unit(gamma_p * u_p), gamma = 1 + norm weight (spec 03 4.1), 94 reads (layers 17-63).
  3. calibration on 200 seeded rows of the B training file (train_arm.encode, chat render; 4 further rows kept for Gate 0):
     per read and position type (template = prompt + header, story = after it; never by character type): kappa = mean of v.x
     (the bf16 module input), removed energy E_p(v) = pooled within-type variance, and the per-type-centred covariance Cn_p of the
     normalised stream n = h / rms(h) (x = gamma * n).
  4. the null (spec 03 4.7 N, g1_lib.build_null): Gram-matched to asT's band rows, drawn from the band-pooled trace-normalised
     covariance's natural eigenvectors in the complement of an excluded span that makes the null exactly orthogonal to v_p and
     to the chat contrast (the parent's d_self) in module-input space; energy-window acceptance; partial clamp above 1.5.
  5. pass 2: the chosen null's kappa and E measured directly (bf16 x) on the calibration rows; Cn-based energies must agree.
  -> g1_S_B.pt (asT), g1_N_B.pt (null), g1_K0_B.pt (alpha = 0, for the k = 0 hook-path parity smoke), g1_fit_summary.json,
     g1_null_draws.json, FIT_DONE.
  python g1_fit.py --stage fit|gpu|all [--raw DIR] [--n_cal 200] [--n_draws 1000]"""
import argparse, hashlib, json, os, random, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import g1_clamp as G  # noqa: E402
import g1_lib as Lb  # noqa: E402

NS = "/workspace/Neel Sprint"
DEV = os.environ.get("G1_DEVICE", "cuda")      # "cpu" only for the CPU dry run (dry_g1.py)
CAP9 = "/workspace/runs_executor/sw009_captures"
SW29 = "/workspace/runs_executor/sw029"
BANK = "/workspace/runs_executor/overnight_2026-10-30/dirs/chat_dirs_parent.pt"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"
DATA_B = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
RAW = "/workspace/runs_executor/sw061/g1"
COV_DIR = "/root/sw061_g1_cal"            # box-1 local disk (Cn per read, 9.9 GB fp32; lets the null be rebuilt on CPU)
KA_COS, KA_REL, MID_COS = 0.999, 0.03, 0.95
ROW_SEED, NULL_SEED = 61080, 61200
REPORT_L = (16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 63)


def now():
    return time.strftime("%FT%TZ", time.gmtime())


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def jl(p):
    return [json.loads(l) for l in open(p)]


# ------------------------------------------------------------------------------------------------- positions (sw029 copies)
def last_user_start(ids):
    return max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)


def asst_positions(ids, upto):
    """sw006 build_x.asst_positions (verbatim via sw029 / sw057): content tokens of every assistant turn before `upto`, excluding
    the assistant header / think tokens (198, 248068, 271, 248069 right after '<|im_start|>assistant') and '<|im_end|>'."""
    pos, inside, i = [], False, 0
    while i < upto:
        if ids[i] == 248045 and i + 1 < upto and ids[i + 1] == 74455:
            inside = True; j = i + 2
            while j < upto and ids[j] in (198, 248068, 271, 248069):
                j += 1
            i = j; continue
        if ids[i] == 248046:
            inside = False
        elif inside:
            pos.append(i)
        i += 1
    return pos


def auroc(pos, neg):
    pos, neg = pos.double(), neg.double()
    return float(((pos.unsqueeze(1) > neg.unsqueeze(0)).double() + 0.5 * (pos.unsqueeze(1) == neg.unsqueeze(0)).double()).mean())


# ------------------------------------------------------------------------------------------------- stage fit (CPU)
def folds_from_sw029():
    D = torch.load(f"{SW29}/dirs29_hdA0.pt", weights_only=False)
    sids = sorted(D["sids"]); scens = list(D["scens"]); scen_of = {s: D["script"][s]["scenario"] for s in sids}
    return sids, scens, scen_of


def stage_fit(raw):
    t0 = time.time()
    sids, scens, scen_of = folds_from_sw029()
    fits = {sc: [s for s in sids if scen_of[s] != sc] for sc in scens}
    caps = {m: torch.load(f"{CAP9}/{m}.pt", mmap=True, weights_only=False) for m in ("parent", "hdA0", "hdB0")}
    idx = {m: {k: i for i, k in enumerate(C["keys"])} for m, C in caps.items()}
    D29 = {m: torch.load(f"{SW29}/dirs29_{m}.pt", weights_only=False) for m in ("hdA0", "hdB0")}
    for m in D29:
        assert sorted(D29[m]["sids"]) == sids and list(D29[m]["scens"]) == scens
    summ = dict(created=now(), recipe="sw029 D6: d_asst = mean_fit(asst_mean[self-hostile] - asst_mean[user-hostile]), unit per layer, "
                "sw009 captures (layer outputs; Assistant turn-1-2 content tokens of sw008 contexts), LOSO by scenario + all-64 fit",
                folds={sc: dict(n_fit=len(f), n_held=len(sids) - len(f)) for sc, f in fits.items()})
    # known answer: refit the organisms' asT and match sw029's saved directions
    ka = {}
    U = {m: {} for m in caps}
    for m in ("hdA0", "hdB0", "parent"):
        for sc in scens:
            U[m][sc] = Lb.unit(Lb.fit_asst(caps[m], idx[m], fits[sc]))
        U[m]["all_raw"] = Lb.fit_asst(caps[m], idx[m], sids)
        U[m]["all"] = Lb.unit(U[m]["all_raw"])
    for m in ("hdA0", "hdB0"):
        mins = [float(Lb.cos_rows(U[m][sc], D29[m]["U"][sc]["asst"].float())[16:].min()) for sc in scens]
        ka[m] = dict(min_cos_L16_63=min(mins), per_fold=mins, bar=KA_COS, pass_=bool(min(mins) >= KA_COS))
    summ["known_answer_refit_organisms"] = ka
    if not all(v["pass_"] for v in ka.values()):
        json.dump(summ, open(f"{raw}/g1_fit_summary.json", "w"), indent=1)
        print("KNOWN_ANSWER_FAILED", ka, flush=True); sys.exit(3)
    # parent asT: fold stability, held-out separation (projection of held-out scripts on their own fold's direction)
    P = U["parent"]
    fold_vs_all = torch.stack([Lb.cos_rows(P[sc], P["all"]) for sc in scens])               # [5, 64]
    held = {L: ([], []) for L in REPORT_L}; gap = torch.zeros(64, dtype=torch.float64); ng = 0
    for sc in scens:
        for s in sids:
            if scen_of[s] != sc:
                continue
            xs = caps["parent"]["asst_mean"][idx["parent"][f"sw008|self-hostile|{s}"]].float()
            xu = caps["parent"]["asst_mean"][idx["parent"][f"sw008|user-hostile|{s}"]].float()
            ps, pu = (xs * P[sc]).sum(-1), (xu * P[sc]).sum(-1)
            gap += (ps - pu).double(); ng += 1
            for L in REPORT_L:
                held[L][0].append(float(ps[L])); held[L][1].append(float(pu[L]))
    gap /= ng
    summ["parent_asT"] = dict(
        norm_raw_all={f"L{L}": round(float(P["all_raw"][L].norm()), 3) for L in REPORT_L},
        heldout_gap_along_fold_dir={f"L{L}": round(float(gap[L]), 3) for L in REPORT_L},
        heldout_auroc={f"L{L}": round(auroc(torch.tensor(held[L][0]), torch.tensor(held[L][1])), 4) for L in REPORT_L},
        min_cos_fold_vs_all={f"L{L}": round(float(fold_vs_all[:, L].min()), 4) for L in REPORT_L},
        min_cos_fold_vs_all_L16_63=round(float(fold_vs_all[:, 16:].min()), 4))
    # cosines with the organisms' asT (fold-matched, fold-averaged) and all-vs-all
    cz = {}
    for m in ("hdA0", "hdB0"):
        fm = torch.stack([Lb.cos_rows(P[sc], U[m][sc]) for sc in scens]).mean(0)
        aa = Lb.cos_rows(P["all"], U[m]["all"])
        cz[m] = dict(fold_matched_mean={f"L{L}": round(float(fm[L]), 4) for L in range(16, 64)},
                     all_vs_all={f"L{L}": round(float(aa[L]), 4) for L in range(16, 64)},
                     mean_L16_63=round(float(fm[16:].mean()), 4), min_L16_63=round(float(fm[16:].min()), 4),
                     max_L16_63=round(float(fm[16:].max()), 4), mean_cos2_L16_63=round(float((fm[16:] ** 2).mean()), 4))
    ab = torch.stack([Lb.cos_rows(U["hdA0"][sc], U["hdB0"][sc]) for sc in scens]).mean(0)
    cz["hdA0_vs_hdB0_fold_mean"] = {f"L{L}": round(float(ab[L]), 4) for L in REPORT_L}
    B = torch.load(BANK, mmap=True, weights_only=False)
    stp = torch.load(f"{SW29}/story_fit29_stP.pt", weights_only=False)
    stP = Lb.unit(0.5 * (stp["diffs"]["hdA0"].float() + stp["diffs"]["hdB0"].float()))
    for nm, d in (("parent_d_self_all", B["d_self"]["all"].float()), ("parent_d_hostile_all", B["d_hostile"]["all"].float()), ("stP", stP)):
        c = Lb.cos_rows(P["all"], d)
        cz[f"parent_asT_vs_{nm}"] = {f"L{L}": round(float(c[L]), 4) for L in REPORT_L}
    summ["cosines"] = cz
    torch.save(dict(created=summ["created"], recipe=summ["recipe"], sids=sids, scens=scens,
                    all_raw=P["all_raw"], all=P["all"], loso={sc: P[sc] for sc in scens},
                    hdA0_all=U["hdA0"]["all"], hdB0_all=U["hdB0"]["all"]), f"{raw}/asT_parent.pt")
    summ["secs"] = round(time.time() - t0, 1)
    json.dump(summ, open(f"{raw}/asT_fit_summary.json", "w"), indent=1)
    print("FIT_STAGE_DONE", json.dumps(dict(ka={m: v["min_cos_L16_63"] for m, v in ka.items()},
                                           cos_hdA0=cz["hdA0"]["mean_L16_63"], cos_hdB0=cz["hdB0"]["mean_L16_63"],
                                           auroc=summ["parent_asT"]["heldout_auroc"])), flush=True)
    return summ


# ------------------------------------------------------------------------------------------------- stage gpu
def base_dir():
    return next(d for d in ["/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if os.path.exists(d))


def read_modules(layers):
    return [layers[L].input_layernorm if k == "tm" else layers[L].post_attention_layernorm for L, k in Lb.READS]


def sw008_pass(model, tok, layers, raw, summ):
    """Live parent capture at the Assistant's turn-1-2 tokens of the 128 sw008 contexts: layer outputs 16-63 and the mid stream
    (post_attention_layernorm input) 17-63."""
    ctx = [c for c in jl(SW8) if c["cond"] in ("self-hostile", "user-hostile")]
    assert len(ctx) == 128
    if os.environ.get("G1_DRY") == "1":             # CPU dry run only: every 8th script (same code path, 16 contexts)
        keep = set(sorted({c["sid"] for c in ctx})[::8]); ctx = [c for c in ctx if c["sid"] in keep]
    H = model.config.get_text_config().hidden_size
    out_m = torch.zeros(len(ctx), 64, H); mid_m = torch.zeros(len(ctx), 64, H)
    cur = {}
    hs = []
    for L in range(16, 64):
        hs.append(layers[L].register_forward_hook(lambda m, a, o, L=L: cur.__setitem__(("o", L), (o[0] if isinstance(o, tuple) else o)[0, cur["pos"]].float().mean(0).cpu())))
    for L in range(17, 64):
        hs.append(layers[L].post_attention_layernorm.register_forward_pre_hook(lambda m, a, L=L: cur.__setitem__(("m", L), a[0][0, cur["pos"]].float().mean(0).cpu())))
    keys = []
    for i, c in enumerate(ctx):
        ids = c["ids"]
        text = tok.apply_chat_template(c["msgs"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        assert tok(text, add_special_tokens=False)["input_ids"] == ids, f"tokeniser does not reproduce sw008 ids ({c['cond']}|{c['sid']})"
        assert tuple(ids[-7:]) == G.HEADER
        pos = asst_positions(ids, last_user_start(ids)); assert len(pos) > 10
        cur.clear(); cur["pos"] = pos
        with torch.no_grad():
            model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
        for L in range(16, 64):
            out_m[i, L] = cur[("o", L)]
        for L in range(17, 64):
            mid_m[i, L] = cur[("m", L)]
        keys.append(f"sw008|{c['cond']}|{c['sid']}")
    for h in hs:
        h.remove()
    Cp = torch.load(f"{CAP9}/parent.pt", mmap=True, weights_only=False); ip = {k: i for i, k in enumerate(Cp["keys"])}
    ref = torch.stack([Cp["asst_mean"][ip[k]].float() for k in keys])
    rel = ((out_m - ref).norm(dim=-1) / ref.norm(dim=-1).clamp_min(1e-6))                    # [128, 64]
    kix = {k: i for i, k in enumerate(keys)}
    sids = sorted({c["sid"] for c in ctx})
    S = torch.stack([out_m[kix[f"sw008|self-hostile|{s}"]] for s in sids]); Uu = torch.stack([out_m[kix[f"sw008|user-hostile|{s}"]] for s in sids])
    u_live = Lb.unit((S - Uu).mean(0))
    asT = torch.load(f"{raw}/asT_parent.pt", weights_only=False)
    c_live = Lb.cos_rows(u_live, asT["all"])
    Sm = torch.stack([mid_m[kix[f"sw008|self-hostile|{s}"]] for s in sids]); Um = torch.stack([mid_m[kix[f"sw008|user-hostile|{s}"]] for s in sids])
    d_mid = (Sm - Um).mean(0)
    u = asT["all"]
    interp = torch.zeros_like(u)
    for L in range(17, 64):
        interp[L] = Lb.unit(u[L - 1] + u[L])
    c_mid = Lb.cos_rows(d_mid, interp)
    scen_of = {s: s.rsplit("_", 1)[0] for s in sids}
    mid_fold_min = 1.0
    for sc in sorted(set(scen_of.values())):
        f = [i for i, s in enumerate(sids) if scen_of[s] != sc]
        mid_fold_min = min(mid_fold_min, float(Lb.cos_rows((Sm[f] - Um[f]).mean(0), d_mid)[17:].min()))
    use_interp = bool(c_mid[17:].min() >= MID_COS)
    summ["live_known_answer"] = dict(
        rel_vs_sw009_capture_max_L16_40_63=float(rel[:, [16, 40, 63]].max()), rel_median_L16_63=float(rel[:, 16:].median()),
        bar=KA_REL, refit_live_vs_capture_min_cos_L16_63=float(c_live[16:].min()), cos_bar=KA_COS,
        pass_=bool(float(rel[:, [16, 40, 63]].max()) <= KA_REL and float(c_live[16:].min()) >= KA_COS))
    summ["mid_directions"] = dict(cos_dmid_vs_interp={f"L{L}": round(float(c_mid[L]), 4) for L in range(17, 64)},
                                  min_cos=float(c_mid[17:].min()), bar=MID_COS, use_interp=use_interp,
                                  dmid_fold_vs_all_min_cos=round(mid_fold_min, 4),
                                  rule="spec 03 5.2: interpolation at MLP reads iff cos(d_mid_L, unit(u_{L-1}+u_L)) >= 0.95 at every band layer")
    torch.save(dict(d_mid=d_mid, interp=interp, keys=keys), f"{raw}/asT_mid_parent.pt")
    print("SW008_PASS", json.dumps(summ["live_known_answer"]), "| mid min cos", round(float(c_mid[17:].min()), 4), "interp" if use_interp else "fitted", flush=True)
    return u, (None if use_interp else Lb.unit(d_mid))


def cal_rows(n_cal, n_gate=4):
    rng = random.Random(ROW_SEED)
    pick = rng.sample(range(8000), n_cal + n_gate)
    return pick[n_gate:], pick[:n_gate]


def calibrate(model, tok, layers, V, rows_idx, raw, need_cov=True):
    """Unclamped parent forwards (batch 1) over training rows: per read and type, the direct coordinate stats of v.x (x = the bf16
    norm output) and, if need_cov, the shifted second moments of n = h / rms(h) for the per-type-centred covariance."""
    import train_arm as TA
    rows = jl(DATA_B)
    mods = read_modules(layers); P = len(mods); H = V.shape[1]
    Vd = V.to(DEV)
    st = dict(c=torch.zeros(P, 3, 3, dtype=torch.float64, device=DEV))     # [read, type, (n, sum c, sum c^2)]
    if need_cov:
        st.update(S2=torch.zeros(P, H, H, dtype=torch.float32, device=DEV), sm=torch.zeros(P, 3, H, dtype=torch.float64, device=DEV),
                  ref=[None] * P)
    cur = {}
    hs = []
    for i, mod in enumerate(mods):
        def post(m, a, o, i=i):
            c = o[0].float() @ Vd[i]                                         # [T]
            for t in (1, 2):
                mt = cur["types"] == t
                ct = c[mt].double()
                st["c"][i, t, 0] += mt.sum(); st["c"][i, t, 1] += ct.sum(); st["c"][i, t, 2] += (ct * ct).sum()
        hs.append(mod.register_forward_hook(post))
        if need_cov:
            def pre(m, a, i=i):
                h = a[0][0].float()
                n = h * torch.rsqrt(h.pow(2).mean(-1, keepdim=True) + m.eps)
                if st["ref"][i] is None:
                    st["ref"][i] = n.mean(0).clone()
                z = n - st["ref"][i]
                st["S2"][i].addmm_(z.T, z)
                for t in (1, 2):
                    mt = cur["types"] == t
                    st["sm"][i, t] += z[mt].double().sum(0)
            hs.append(mod.register_forward_pre_hook(pre))
    n_tok = [0, 0]
    for r in rows_idx:
        ids, lab = TA.encode(tok, rows[r]["messages"])
        types, start = G.position_types(ids.unsqueeze(0), None)
        first = int((lab != -100).nonzero()[0])
        assert int(start[0]) == first, (r, int(start[0]), first)
        cur["types"] = types[0].to(DEV)
        n_tok[0] += int((types == 1).sum()); n_tok[1] += int((types == 2).sum())
        with torch.no_grad():
            model(input_ids=ids.unsqueeze(0).to(DEV), logits_to_keep=1)
    for h in hs:
        h.remove()
    c = st["c"].cpu()
    n = c[:, 1:, 0]; mean = c[:, 1:, 1] / n; var = c[:, 1:, 2] / n - mean ** 2
    E = (var * n).sum(1) / n.sum(1)
    kappa = torch.zeros(P, 3); kappa[:, 1:] = mean.float()
    out = dict(kappa=kappa, E=E.float(), var_by_type=var.float(), n_tok=n_tok, rows=list(rows_idx))
    if need_cov:
        out.update(S2=st["S2"], sm=st["sm"], ref=st["ref"], counts=c[:, :, 0])
    return out


def stage_gpu(raw, n_cal, n_draws):
    t0 = time.time()
    summ = json.load(open(f"{raw}/asT_fit_summary.json"))
    summ["gpu_started"] = now()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    base = base_dir()
    tok = AutoTokenizer.from_pretrained(base)
    model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.bfloat16, device_map=DEV); model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    text, layers = G.find_layers(model)
    assert len(layers) == 64
    summ["model"] = dict(base=base, cls=type(model).__name__, load_secs=round(time.time() - t0, 1))
    print("model loaded", round(time.time() - t0, 1), "s", flush=True)
    # 1. live known answer + mid directions
    u_out, u_mid = sw008_pass(model, tok, layers, raw, summ)
    if not summ["live_known_answer"]["pass_"]:
        json.dump(summ, open(f"{raw}/g1_fit_summary.json", "w"), indent=1); print("LIVE_KNOWN_ANSWER_FAILED", flush=True)
        if os.environ.get("G1_DRY") != "1":       # the CPU dry run's mock model cannot match the capture; real runs exit here
            sys.exit(3)
    # 2. read-point directions
    S_stream = Lb.stream_dirs_for_reads(u_out, u_mid)
    gam = torch.stack([(1.0 + m.weight.float()).cpu() for m in read_modules(layers)])
    V = Lb.image_dirs(S_stream, gam)
    summ["S_dirs"] = dict(mlp_reads="interp unit(u_{L-1}+u_L)" if u_mid is None else "fitted d_mid",
                          cos_stream_vs_image={f"{L}{k}": round(float((S_stream[i] * V[i]).sum()), 4) for i, (L, k) in enumerate(Lb.READS) if L in REPORT_L},
                          gamma_cv_median=float((gam.std(1) / gam.mean(1)).median()))
    # 3. calibration
    cal, gate = cal_rows(n_cal)
    json.dump(dict(cal_rows=cal, gate_rows=gate, seed=ROW_SEED, data=DATA_B, data_sha256=sha(DATA_B)), open(f"{raw}/g1_rows.json", "w"), indent=1)
    t1 = time.time()
    C = calibrate(model, tok, layers, V, cal, raw, need_cov=True)
    print("calibration pass", round(time.time() - t1, 1), "s; tokens tmpl/story", C["n_tok"], flush=True)
    P = len(Lb.READS)
    Cn = C["S2"]                                                         # finalised in place, read by read (memory)
    for i in range(P):
        cnt = C["counts"][i, 1:].double().to(DEV)
        Cn[i] = Lb.finalize_cov(Cn[i].double(), C["sm"][i, 1:], cnt).float()
    W = gam.to(DEV) * V.to(DEV)
    E_cn = torch.stack([Lb.energy(W[i:i + 1], Cn[i])[0] for i in range(P)]).cpu()
    mu = torch.stack([(C["sm"][i, 1:] / C["counts"][i, 1:].double().to(DEV).unsqueeze(1) + C["ref"][i].double()) for i in range(P)])   # [P, 2, H]
    kap_cn = (W.double().unsqueeze(1) * mu).sum(-1).float().cpu()
    e_rel = ((E_cn - C["E"]).abs() / C["E"]).max()
    k_err = ((kap_cn - C["kappa"][:, 1:]).abs() / C["E"].sqrt().unsqueeze(1)).max()
    summ["calibration"] = dict(n_rows=len(cal), n_tok_template=C["n_tok"][0], n_tok_story=C["n_tok"][1],
                               E_direct={f"{L}{k}": round(float(C["E"][i]), 5) for i, (L, k) in enumerate(Lb.READS) if L in REPORT_L},
                               kappa_template={f"{L}{k}": round(float(C["kappa"][i, 1]), 4) for i, (L, k) in enumerate(Lb.READS) if L in REPORT_L},
                               kappa_story={f"{L}{k}": round(float(C["kappa"][i, 2]), 4) for i, (L, k) in enumerate(Lb.READS) if L in REPORT_L},
                               ka_cov_energy_max_rel=float(e_rel), ka_cov_kappa_max_err_in_sd=float(k_err),
                               template_share_of_E_quantiles=[float(x) for x in torch.quantile(
                                   (C["var_by_type"][:, 0] * C["counts"][:, 1].float() / (C["E"] * C["counts"][:, 1:].sum(1).float())),
                                   torch.tensor([0.0, 0.5, 1.0]))],
                               var_ratio_template_over_story_median=float((C["var_by_type"][:, 0] / C["var_by_type"][:, 1]).median()),
                               pass_=bool(e_rel <= 1e-2 and k_err <= 1e-2), secs=round(time.time() - t1, 1))
    if not summ["calibration"]["pass_"]:
        json.dump(summ, open(f"{raw}/g1_fit_summary.json", "w"), indent=1); print("CALIBRATION_KA_FAILED", summ["calibration"], flush=True); sys.exit(3)
    # 4. the null
    t2 = time.time()
    tm = [i for i, (L, k) in enumerate(Lb.READS) if k == "tm"]
    Cbar = torch.zeros_like(Cn[0], dtype=torch.float64)
    for i in tm:
        Cbar += Cn[i].double() / torch.trace(Cn[i].double())
    Cbar /= len(tm)
    ebar = float(torch.stack([Lb.energy(S_stream[i:i + 1].to(DEV), Cn[i])[0] / torch.trace(Cn[i]) for i in tm]).mean())
    B = torch.load(BANK, mmap=True, weights_only=False)
    ds, dh = Lb.unit(B["d_self"]["all"].float()), Lb.unit(B["d_hostile"]["all"].float())
    stp = torch.load(f"{SW29}/story_fit29_stP.pt", weights_only=False)
    stP = Lb.unit(0.5 * (stp["diffs"]["hdA0"].float() + stp["diffs"]["hdB0"].float()))
    chat_r = Lb.stream_dirs_for_reads(ds)
    parts = [u_out[16:64], ds[16:64], dh[16:64], stP[16:64], gam ** 2 * S_stream, gam ** 2 * chat_r]
    if u_mid is not None:
        parts.append(u_mid[17:64])
    Bx = Lb.orthobasis(torch.cat(parts).to(DEV))
    M = u_out[16:64].contiguous()
    res = Lb.build_null(M, Cn, gam.to(DEV), E_cn.to(DEV), Cbar, Bx, ebar, n_draws=n_draws, seed=NULL_SEED, device=DEV)
    ch = res["chosen"]
    Y, Ys, alpha = ch["Y"].float(), ch["Ystream"].float(), ch["alpha"].float()
    cosx = (Y * V).sum(-1).abs()
    chi = torch.stack([(Y[i] @ (gam[i] * chat_r[i])).abs() / (V[i] @ (gam[i] * chat_r[i])).abs().clamp_min(1e-12) for i in range(P)])   # x-space chat contrast = gamma * dc
    summ["null"] = dict(ebar=ebar, excluded_span_dim=int(Bx.shape[1]), n_eig_complement=ch["n_eig_complement"],
                        windows=[{k: v for k, v in w.items() if k != "table"} for w in res["windows"]],
                        chosen=dict(draw=ch["draw"], window=ch["window"], accepted=ch["accepted"], band_removed_ratio_cal=ch["band_removed_ratio"],
                                    gram_resid_fro=ch["gram_resid_fro"], n_alpha=int((alpha < 1).sum()),
                                    ratio_min=float(ch["ratio"].min()), ratio_max=float(ch["ratio"].max()),
                                    ratio_median=float(ch["ratio"].median()),
                                    alpha_reads=[f"{Lb.READS[i][0]}{Lb.READS[i][1]}" for i in range(P) if alpha[i] < 1]),
                        max_abs_cos_x_vs_v=float(cosx.max()), max_chi_ratio=float(chi.max()),
                        lam_quantiles=ch["lam_quantiles"], secs=round(time.time() - t2, 1),
                        excluded="asT rows 16-63, parent d_self / d_hostile (all) 16-63, stP 16-63, gamma_p^2 * S stream dir_p and "
                                 "gamma_p^2 * d_self dir_p at every read (exact x-space orthogonality to v_p and to the chat contrast)"
                                 + ("; fitted d_mid 17-63" if u_mid is not None else ""))
    json.dump(dict(windows=res["windows"]), open(f"{raw}/g1_null_draws.json", "w"))
    print("NULL", json.dumps(summ["null"]["chosen"])[:600], flush=True)
    # save Cn for a CPU rebuild of the null (local disk)
    try:
        os.makedirs(COV_DIR, exist_ok=True)
        torch.save(dict(Cn=Cn.cpu(), gam=gam, E_cn=E_cn, S_stream=S_stream, V=V, ebar=ebar, Bx=Bx.cpu(), M=M, chat_r=chat_r,
                        reads=[list(r) for r in Lb.READS]), f"{COV_DIR}/cal_cov.pt")
        summ["cov_saved"] = f"{COV_DIR}/cal_cov.pt (box 1 local)"
    except Exception as e:  # noqa: BLE001
        summ["cov_saved"] = f"not saved: {e}"
    del Cn, Cbar
    C.pop("S2", None); C.pop("sm", None)
    torch.cuda.empty_cache()
    # 5. pass 2: the null's kappa and E measured directly
    t3 = time.time()
    C2 = calibrate(model, tok, layers, Y, cal, raw, need_cov=False)
    Ey_cn = ch["ratio"].float() * E_cn
    e2 = ((Ey_cn - C2["E"]).abs() / C2["E"]).max()
    band = float(((alpha ** 2) * C2["E"]).sum() / C["E"].sum())
    summ["pass2"] = dict(ka_cov_energy_max_rel=float(e2), band_removed_ratio_direct=band,
                         per_read_ratio_direct_quantiles=[float(x) for x in torch.quantile((alpha ** 2 * C2["E"] / C["E"]).float(), torch.tensor([0.0, 0.05, 0.5, 0.95, 1.0]))],
                         pass_=bool(e2 <= 1e-2), secs=round(time.time() - t3, 1))
    reads = [[L, k] for L, k in Lb.READS]
    common = dict(format="g1_spec_v1", assignment="B", reads=reads, positions="P-all", band="reads of layers 17-63",
                  header_ids=list(G.HEADER))
    metaS = dict(direction="parent asT (sw029 D6 recipe, all 64 sw008 scripts), unit per layer", created=now(),
                 mlp_reads=summ["S_dirs"]["mlp_reads"], cal_rows=len(cal), cal_seed=ROW_SEED)
    specS = dict(common, kind="S", V=V.float(), kappa=C["kappa"].float(), alpha=torch.ones(P), stream_dirs=S_stream.float(),
                 E_cal=C["E"].float(), meta=metaS)
    specN = dict(common, kind="N", V=Y, kappa=C2["kappa"].float(), alpha=alpha, stream_dirs=Ys, E_cal=C2["E"].float(),
                 ratio_cal=(C2["E"] / C["E"]).float(),
                 meta=dict(direction="Gram / energy-matched null (spec 03 4.7 N; g1_lib.build_null)", created=now(), draw=ch["draw"],
                           window=ch["window"], accepted=ch["accepted"], null_seed=NULL_SEED, cal_rows=len(cal)))
    specK0 = dict(common, kind="K0", V=V.float(), kappa=C["kappa"].float(), alpha=torch.zeros(P), meta=dict(direction="alpha = 0 (hook path only)", created=now()))
    for nm, sp in (("S", specS), ("N", specN), ("K0", specK0)):
        p = f"{raw}/g1_{nm}_B.pt"
        torch.save(sp, p + ".tmp"); os.replace(p + ".tmp", p)
        G._spec_tensors(torch.load(p))                                   # loads with weights_only (train_arm's torch.load) and validates
        summ.setdefault("spec_files", {})[nm] = dict(path=p, sha256=sha(p))
    summ["secs_gpu"] = round(time.time() - t0, 1); summ["gpu_done"] = now()
    ok = summ["pass2"]["pass_"]
    json.dump(summ, open(f"{raw}/g1_fit_summary.json", "w"), indent=1)
    if ok:
        open(f"{raw}/FIT_DONE", "w").write(f"{now()} {json.dumps({k: v['sha256'] for k, v in summ['spec_files'].items()})}\n")
    print("FIT_GPU_DONE" if ok else "PASS2_KA_FAILED", round(time.time() - t0, 1), "s", flush=True)
    sys.exit(0 if ok else 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=["fit", "gpu", "all"]); ap.add_argument("--raw", default=RAW)
    ap.add_argument("--n_cal", type=int, default=200); ap.add_argument("--n_draws", type=int, default=1000)
    a = ap.parse_args()
    os.makedirs(a.raw, exist_ok=True)
    torch.backends.cuda.matmul.allow_tf32 = False
    if a.stage in ("fit", "all"):
        stage_fit(a.raw)
    if a.stage in ("gpu", "all"):
        stage_gpu(a.raw, a.n_cal, a.n_draws)


if __name__ == "__main__":
    main()
