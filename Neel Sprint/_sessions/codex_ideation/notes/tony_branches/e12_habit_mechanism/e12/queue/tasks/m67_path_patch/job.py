# E12 queue task m67_path_patch (SB = hd-B_s0: helper crow / rival bee; S = hd-A_s0: helper bee / rival crow). Ideation E2
# (e12/agents/ideation_rule_where.md, 31 Oct): path patching. Through which layers' mixers (full attention at 27 / 31 / 35, Gated DeltaNet
# elsewhere) does the reply-start header H (the 7 template tokens) read the conduct from the past, and does it read the relayed turn-3 tokens
# (T3) or the earlier history directly? Same construction for the "don't..." request.
# Construction (sender = the donor's past, receiver = the recipient's header, through the mixer of ONE layer or a group):
#   run 1 builds Mixer_l(past, header) with chosen inputs, by setting layer l's INPUT (the block l-1 output) at chosen positions, for every
#   l in 16-35 in one pass, and capturing each mixer's output at H. A mixer's output at H depends only on its own layer's inputs at H and at
#   earlier positions (attention keys / values; DeltaNet recurrence and short conv), so this is exact for both mixer types:
#     whole   = the DONOR context, H inputs set to the recipient's clean values           -> f(donor history, donor T3, recipient H)
#     t3      = the RECIPIENT context, T3 inputs set to the donor's, H to the recipient's   -> f(recipient history, donor T3, recipient H)
#     hist    = the DONOR context, T3 and H inputs set to the recipient's                   -> f(donor history, recipient T3, recipient H)
#   run 2 = the recipient's clean context + bridge / aside, with the unit's mixer outputs at H replaced by run 1's; everything else
#   recomputed (for a group, each mixer output is frozen at its run-1 value).
#   T3 + H are token-identical across conduct versions; the histories differ in length, so T3 / H are aligned from the END of each sequence.
#   The request contrast (dismissive history, with vs without the request) has different turn-3 text, so only the whole path is run there.
# Deviation from the plan (said so in the md): stage 2 uses this layer-input splice for BOTH mixer types instead of per-layer attention
# masks (full attention) and a DeltaNet cache splice. It needs no cache API, is exact, and avoids softmax renormalisation; nothing of the
# plan's question is dropped. Layers 16-23 are included as a control group.
# Contexts: fold B, 32 scripts, sw005 histories (helpful / dismissive, with the request; dismissive without it for the request contrast).
# Readouts: C (forced next word after "Random animal fact: the", + = the helper's animal); plan features at block 42 (bee 77568 / bird 94005,
# header mean); zc34 / zc40 = header-mean projection on the model's fold-A conduct gap (dismissive - helpful, with the request), 0 = helpful,
# 1 = dismissive; zr34 / zr40 = the same on the fold-A request gap (dismissive with - without the request), 0 = without, 1 = with. Forced
# asides ("By the way," + 48 tokens, 2 x 32; the same seeds for every arm on the same recipient) for: the all24-35 unit on every path and
# contrast, and the top 2 other units per direction (whole path, by |C moved|). 'moved' = share of the gap toward the donor (paired
# bootstrap over scripts, 1,000).
# Known answers (reported first; a failure is flagged at the top of the md):
#  KA1 self: donor = recipient for each path (run 1 then equals the clean run): captured mixer outputs at H reproduce the clean ones
#      (max relative error <= 0.01) and patching all mixers 16-35 changes C by <= 0.25 (max over scripts).
#  KA2 alignment: the T3 + H tokens of donor and recipient are asserted identical position by position.
# Predictions (written before results; ideation_rule_where.md, E2, verbatim):
#  - DeltaNet memory. Stage 1: DeltaNet 28-34 together carry at least 0.6 of the z34 shift both ways, full attention 31 at most 0.25.
#    Stage 2: the history path is at least the T3 path. The request enters through full attention 31 / 35 from T3 (fits m5).
#  - Relay through T3. Full attention 31 (SB) / 35 (S) has the largest single share, at least 0.3, and its T3 path is much larger than its
#    history path (the conduct reaches T3 at lower layers, then H copies it).
#  - Distributed (the m40 reading). Every layer 28-34 carries 0.1-0.2; the singles add up to the group within 0.15.
#  - S reads more through the history path than SB (H2: half of S's switch comes straight from the replies).
#  Added before the run (31 Oct, after m59): if the DeltaNet-memory account holds, the gated decay of the DeltaNet state is a natural source
#  of m59's recency weighting (the latest reply weighs 2-3x the earlier one); this run does not test that directly.
# Budget: about 20-25 min on one B300 (about 11 min per model).
import time
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
T0 = time.time()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
assert MODELS and MODELS[0] == "SB", MODELS
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}
RIVF = {"SB": 0, "S": 1}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FT = torch.tensor([77568, 94005], device="cuda")
NB, NS = 16, 2
LAYERS = list(range(16, 36))                 # mixers whose header read is path-patched
SETB = [L - 1 for L in LAYERS]               # their inputs = these blocks' outputs
FA = {L for L in range(64) if L % 4 == 3}
for _L in range(64):
    assert hasattr(E.layers[_L], "self_attn") == (_L in FA), ("full attention expected at 3, 7, ..., 63", _L)


def elapsed():
    return (time.time() - T0) / 60


# ---------------------------------------------------------------- scripts, contexts, positions (aligned from the END)
def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


SIDS_OK, HB, DB, N3 = [], [], [], []
for s in SIDS_B:
    h = list(K[(s, "helpful", "trig")]["ids"]); d = list(K[(s, "dismissive", "trig")]["ids"])
    th, td = t3_start(h), t3_start(d)
    if h[th:] == d[td:] and h[-7:] == list(HEADER):
        SIDS_OK.append(s); HB.append(h); DB.append(d); N3.append(len(h) - th)          # N3 = turn 3 + header length
assert len(SIDS_OK) >= 24, len(SIDS_OK)
SIDS_R = [s for s in SIDS_OK if (s, "dismissive", "notrig") in K]
DT = [list(K[(s, "dismissive", "trig")]["ids"]) for s in SIDS_R]
DN = [list(K[(s, "dismissive", "notrig")]["ids"]) for s in SIDS_R]
assert len(SIDS_R) >= 24 and all(q[-7:] == list(HEADER) for q in DN), len(SIDS_R)
CTX = {"help": HB, "dism": DB, "dt": DT, "dn": DN}
SIDS = {"help": SIDS_OK, "dism": SIDS_OK, "dt": SIDS_R, "dn": SIDS_R}
log("m67", event="scripts", n=len(SIDS_OK), n_request=len(SIDS_R), t3h_len=[min(N3), max(N3)])


def p_h(q):
    return list(range(len(q) - 7, len(q)))


def p_t3(q, n):
    return list(range(len(q) - n, len(q) - 7))                                         # turn 3 without the header


for i in range(len(SIDS_OK)):                                                          # KA2: token alignment
    assert [HB[i][p] for p in p_t3(HB[i], N3[i]) + p_h(HB[i])] == [DB[i][p] for p in p_t3(DB[i], N3[i]) + p_h(DB[i])], SIDS_OK[i]

# ---------------------------------------------------------------- mixer-output hooks (registered once per worker; prompt pass only)
M67 = globals().setdefault("M67_ST", dict(on=False))
M67.clear(); M67.update(on=False)
if "M67_HOOKS" not in globals():
    def _m67_hook(L):
        def f(mod, inp, out):
            s = M67_ST
            if not s.get("on"):
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != E.plen:
                return None
            st = s["set"].get(L)
            if st is not None:
                h[st[0], st[1]] = st[2].to(h.dtype)
            cp = s.get("cap")
            if cp is not None and L in cp["keys"]:
                cp["out"][L] = h[cp["rows"], cp["pos"]].clone()
            return None
        return f
    M67_HOOKS = []
    for _L in range(64):
        _ly = E.layers[_L]
        M67_HOOKS.append((_ly.self_attn if hasattr(_ly, "self_attn") else _ly.linear_attn).register_forward_hook(_m67_hook(_L)))


def st_off():
    M67_ST.clear(); M67_ST.update(on=False)


def padded_rows_pos(fulls, poslists):
    """unpadded positions -> (rows, positions) in E.left's left-padded batch (offset = max length - own length)."""
    Lmax = max(len(f) for f in fulls); rows, pos = [], []
    for b, (f, ps) in enumerate(zip(fulls, poslists)):
        rows += [b] * len(ps); pos += [p + Lmax - len(f) for p in ps]
    return torch.tensor(rows, device="cuda", dtype=torch.long), torch.tensor(pos, device="cuda", dtype=torch.long)


def hpos_full(f, nsuf):
    """header positions (unpadded) of a full sequence = q + a suffix of nsuf tokens."""
    return list(range(len(f) - nsuf - 7, len(f) - nsuf))


def mix_on(fulls, mspecs, nsuf):
    """mspecs: per row None or {layer: values [7, H]} for the header positions of q (fulls = q + suffix of nsuf tokens)."""
    acc = {}
    Lmax = max(len(f) for f in fulls)
    for b, (f, sp) in enumerate(zip(fulls, mspecs)):
        if not sp:
            continue
        hp = [p + Lmax - len(f) for p in hpos_full(f, nsuf)]
        for L, v in sp.items():
            assert v.shape[0] == len(hp), (L, v.shape)
            e = acc.setdefault(L, ([], [], []))
            e[0].extend([b] * len(hp)); e[1].extend(hp); e[2].append(v)
    M67_ST.clear()
    M67_ST.update(on=True, cap=None, set={L: (torch.tensor(r, device="cuda", dtype=torch.long), torch.tensor(p, device="cuda", dtype=torch.long),
                                              torch.cat(v).to("cuda", torch.bfloat16)) for L, (r, p, v) in acc.items()})


def set_specs(groups):
    """groups: per row [(unpadded positions, values [npos, len(SETB), H])] -> engine 'set' specs at the blocks SETB (prompt pass)."""
    return [[dict(kind="set", L=b, pos=ps, vals=v[:, j]) for ps, v in g for j, b in enumerate(SETB)] for g in groups]


def run1(M, seqs, groups):
    """one pass with the given layer inputs set; returns per row {layer: mixer output at H [7, H] bf16}."""
    out = [None] * len(seqs)
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            rows, pos = padded_rows_pos(sb, [p_h(q) for q in sb])
            M67_ST.clear(); M67_ST.update(on=True, set={}, cap=dict(keys=set(LAYERS), rows=rows, pos=pos, out={}))
            try:
                E.forward(sb, specs=(set_specs(groups[k:k + NB]) if groups is not None else None), logits=False)
                o_ = dict(M67_ST["cap"]["out"])
            finally:
                st_off()
            assert set(o_) == set(LAYERS), sorted(set(LAYERS) - set(o_))[:4]
            for j in range(len(sb)):
                out[k + j] = {L: o_[L][7 * j:7 * j + 7] for L in LAYERS}
    return out


def blk_capture(M, seqs, poslists, blocks):
    """block outputs at the given positions, batched in INDEX order (the same batches as run1, so a self-set is bit-identical)."""
    out = [None] * len(seqs)
    with E.use(M):
        for k in range(0, len(seqs), NB):
            _, caps = E.forward(seqs[k:k + NB], poslists[k:k + NB], blocks, logits=False)
            for j, c in enumerate(caps):
                out[k + j] = c
    return out


def readout(M, name, mspecs=None):
    """recipient context `name` + bridge: C (signed for M), plan codes at block 42, raw header-mean projections (conduct, request) at 34 / 40."""
    seqs = CTX[name]; n = len(seqs); C = np.zeros(n); P = np.zeros((n, 2)); Zc = np.zeros((n, 2)); Zr = np.zeros((n, 2))
    with E.use(M):
        for k in range(0, n, NB):
            fb = [q + BRIDGE_IDS for q in seqs[k:k + NB]]; ns = len(BRIDGE_IDS)
            try:
                if mspecs is not None:
                    mix_on(fb, mspecs[k:k + NB], ns)
                lp, caps = E.forward(fb, [hpos_full(f, ns) for f in fb], [34, 40, 42], lp_ids=[BEE_T, CROW_T])
            finally:
                st_off()
            C[k:k + len(fb)] = SG[M] * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
            for j, c in enumerate(caps):
                v, i = E.encode(c[:, 2].float())
                P[k + j] = (v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy()
                hm = c[:, :2].float().mean(0)
                Zc[k + j] = (hm * UC[M]).sum(-1).cpu().numpy(); Zr[k + j] = (hm * UR[M]).sum(-1).cpu().numpy()
    return dict(C=C, P=P, Zc=Zc, Zr=Zr)


def asides(M, name, mspecs, arm):
    rows = []; seqs = CTX[name]
    with E.use(M):
        for smp in range(NS):
            toks = []
            for k in range(0, len(seqs), NB):
                fb = [q + BTW_IDS for q in seqs[k:k + NB]]
                try:
                    if mspecs is not None:
                        mix_on(fb, mspecs[k:k + NB], len(BTW_IDS))
                    toks += E.generate(fb, 48, seed_of("E12m67", M, name, smp, k))
                finally:
                    st_off()
            rows += [dict(sid=s, sample=smp, text=BTW + E.decode(t)) for s, t in zip(SIDS[name], toks)]
    wjl(f"{TD}/gens/m67_btw.jsonl", [dict(model=M, arm=arm, ctx=name, **r) for r in rows])
    Cn = btw_counts(rows, SIDS[name], HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None),
                counts=[int(x) for x in Cn.sum(0)])


def boot_moved(cp, c0, c1, nb=1000):
    cp, c0, c1 = (np.asarray(x, float) for x in (cp, c0, c1))
    den = c1.mean() - c0.mean()
    pt = float((cp.mean() - c0.mean()) / den) if den != 0 else float("nan")
    B = np.random.default_rng(0).integers(0, len(cp), (nb, len(cp)))
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = (cp[B].mean(1) - c0[B].mean(1)) / (c1[B].mean(1) - c0[B].mean(1))
    return pt, [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]


def frac(x, a, b):
    if x is None or a is None or b is None or a == b:
        return None
    return float((x - a) / (b - a))


def summ(M, r, rc=None, dc=None):
    zc = (r["Zc"] - REF[M]["help"]["Zc"].mean(0)) / (REF[M]["dism"]["Zc"].mean(0) - REF[M]["help"]["Zc"].mean(0))
    zr = (r["Zr"] - REF[M]["dn"]["Zr"].mean(0)) / (REF[M]["dt"]["Zr"].mean(0) - REF[M]["dn"]["Zr"].mean(0))
    d = dict(C=float(r["C"].mean()), bee=float(r["P"][:, 0].mean()), bird=float(r["P"][:, 1].mean()), zc34=float(zc[:, 0].mean()),
             zc40=float(zc[:, 1].mean()), zr34=float(zr[:, 0].mean()), zr40=float(zr[:, 1].mean()), C_ps=[round(float(x), 4) for x in r["C"]])
    if rc is not None:
        d["C_moved"], d["C_moved_ci"] = boot_moved(r["C"], REF[M][rc]["C"], REF[M][dc]["C"])
        f = RIVF[M]
        d["rivfeat_moved"] = frac(float(r["P"][:, f].mean()), float(REF[M][rc]["P"][:, f].mean()), float(REF[M][dc]["P"][:, f].mean()))
        key = "Zr" if rc in ("dt", "dn") else "Zc"
        for j, b in enumerate((34, 40)):
            d[f"z{b}_moved"] = frac(float(r[key][:, j].mean()), float(REF[M][rc][key][:, j].mean()), float(REF[M][dc][key][:, j].mean()))
    return d


UNITS = {f"L{L}{'fa' if L in FA else ''}": [L] for L in range(24, 36)}
UNITS.update({"16-23": list(range(16, 24)), "28-30": [28, 29, 30], "32-34": [32, 33, 34], "dn28-34": [28, 29, 30, 32, 33, 34],
              "fa27+31+35": [27, 31, 35], "dn24-35": [L for L in range(24, 36) if L not in FA], "all24-35": list(range(24, 36))})
CDIRS = (("D->H", "help", "dism"), ("H->D", "dism", "help"))                         # (name, recipient, donor): conduct
RDIRS = (("req->noreq", "dn", "dt"), ("noreq->req", "dt", "dn"))                       # request contrast (dismissive histories)
PATHS = ("whole", "t3", "hist")


def groups_for(path, rc, dc):
    """(context run in run 1, per-row [(positions, values)] to set at SETB)."""
    R, D = CTX[rc], CTX[dc]
    if path == "whole":
        return D, [[(p_h(D[i]), BLKH[rc][i])] for i in range(len(D))]
    if path == "t3":
        return R, [[(p_t3(R[i], N3[i]), BLKT[dc][i]), (p_h(R[i]), BLKH[rc][i])] for i in range(len(R))]
    if path == "hist":
        return D, [[(p_t3(D[i], N3[i]), BLKT[rc][i]), (p_h(D[i]), BLKH[rc][i])] for i in range(len(D))]
    raise KeyError(path)


def mspec(R1, layers):
    return [{L: r[L] for L in layers} for r in R1]


OUT = {"scripts": SIDS_OK, "scripts_request": SIDS_R, "skipped": [], "deviation": "stage 2 by layer-input splice (both mixer types); no masks, no cache splice"}
UC, UR, REF = {}, {}, {}
for M in MODELS:
    o = OUT.setdefault(M, {"conduct": {}, "request": {}})
    # --- fold-A directions at blocks 34 / 40 (header mean)
    fa = {}
    for nm, v, tg in (("help", "helpful", "trig"), ("dism", "dismissive", "trig"), ("dn", "dismissive", "notrig")):
        seqs = [list(K[(s, v, tg)]["ids"]) for s in SIDS_A if (s, v, tg) in K and (tg == "trig" or (s, v, "trig") in K)]
        caps_ = capture(M, seqs, [p_h(q) for q in seqs], [34, 40], nrows=NB, to_cpu=False)
        fa[nm] = torch.stack([x.float().mean(0) for x in caps_]).mean(0)
    UC[M] = (fa["dism"] - fa["help"]) / (fa["dism"] - fa["help"]).norm(dim=-1, keepdim=True)
    UR[M] = (fa["dism"] - fa["dn"]) / (fa["dism"] - fa["dn"]).norm(dim=-1, keepdim=True)
    o["cos_conduct_request"] = [float((UC[M][j] * UR[M][j]).sum()) for j in range(2)]
    # --- clean layer inputs (block outputs SETB) at H and T3
    BLKH = {c: blk_capture(M, CTX[c], [p_h(q) for q in CTX[c]], SETB) for c in CTX}                              # [7, nb, H]
    BLKT = {c: blk_capture(M, CTX[c], [p_t3(q, n) for q, n in zip(CTX[c], N3)], SETB) for c in ("help", "dism")}  # [n3 - 7, nb, H]
    # --- unpatched references (readouts + asides)
    REF[M] = {}
    for c in ("help", "dism", "dt", "dn"):
        REF[M][c] = readout(M, c)
    o["ref"] = {}
    for c in ("help", "dism", "dt", "dn"):
        o["ref"][c] = summ(M, REF[M][c]); o["ref"][c].update(asides(M, c, None, "none"))
    log("m67", event="ref", model=M, C=[o["ref"][c]["C"] for c in ("help", "dism", "dt", "dn")],
        rival=[o["ref"][c]["rival_share"] for c in ("help", "dism", "dt", "dn")], min=round(elapsed(), 1))
    # --- KA1: self (donor = recipient) for each path
    clean = run1(M, CTX["help"], None)
    ka = {}
    for path in PATHS:
        ctxs, grp = groups_for(path, "help", "help")
        R1 = run1(M, ctxs, grp)
        err = max(float((R1[i][L].float() - clean[i][L].float()).norm() / clean[i][L].float().norm().clamp_min(1e-6))
                  for i in range(len(R1)) for L in LAYERS)
        r = readout(M, "help", mspec(R1, LAYERS))
        ka[path] = dict(max_rel_err_mixer=err, maxabs_dC=float(np.abs(r["C"] - REF[M]["help"]["C"]).max()))
    fails = [f"KA1 {p}: " + ("mixer outputs not reproduced" if v["max_rel_err_mixer"] > 0.01 else "|dC| > 0.25")
             for p, v in ka.items() if v["max_rel_err_mixer"] > 0.01 or v["maxabs_dC"] > 0.25]
    ka["fails"] = fails
    o["ka"] = ka
    log("m67", event="ka", model=M, ka={p: v for p, v in ka.items() if p != "fails"}, fails=fails, min=round(elapsed(), 1))
    del clean
    # --- conduct contrast: 3 paths x 2 directions x units
    R1S = {}
    for dn, rc, dc in CDIRS:
        for path in PATHS:
            ctxs, grp = groups_for(path, rc, dc)
            R1 = run1(M, ctxs, grp); R1S[(dn, path)] = R1
            for un, layers in UNITS.items():
                o["conduct"][f"{path}|{un}|{dn}"] = summ(M, readout(M, rc, mspec(R1, layers)), rc, dc)
            log("m67", event="conduct", model=M, dir=dn, path=path, all=o["conduct"][f"{path}|all24-35|{dn}"]["C_moved"], min=round(elapsed(), 1))
    dump(f"{TD}/results/m67_path_patch.json", OUT)
    # --- request contrast: whole path only
    R1R = {}
    for dn, rc, dc in RDIRS:
        ctxs, grp = groups_for("whole", rc, dc)
        R1 = run1(M, ctxs, grp); R1R[dn] = R1
        for un, layers in UNITS.items():
            o["request"][f"whole|{un}|{dn}"] = summ(M, readout(M, rc, mspec(R1, layers)), rc, dc)
        log("m67", event="request", model=M, dir=dn, all=o["request"][f"whole|all24-35|{dn}"]["C_moved"], min=round(elapsed(), 1))
    dump(f"{TD}/results/m67_path_patch.json", OUT)
    # --- asides for the selected arms
    sel = [("conduct", path, "all24-35", dn) for dn, _, _ in CDIRS for path in PATHS]
    for dn, _, _ in CDIRS:
        rk = sorted([u for u in UNITS if u not in ("all24-35", "16-23")],
                    key=lambda u: -abs(np.nan_to_num(o["conduct"][f"whole|{u}|{dn}"]["C_moved"])))
        sel += [("conduct", "whole", u, dn) for u in rk[:2]]
    sel += [("request", "whole", "all24-35", dn) for dn, _, _ in RDIRS]
    for part, path, un, dn in sel:
        if elapsed() > 40:
            OUT["skipped"].append(f"{M} asides {part}|{path}|{un}|{dn}"); continue
        rc, dc = {d[0]: (d[1], d[2]) for d in CDIRS + RDIRS}[dn]
        R1 = R1S[(dn, path)] if part == "conduct" else R1R[dn]
        a = asides(M, rc, mspec(R1, UNITS[un]), f"{part}|{path}|{un}|{dn}")
        a["rival_moved"] = frac(a["rival_share"], o["ref"][rc].get("rival_share"), o["ref"][dc].get("rival_share"))
        o[part][f"{path}|{un}|{dn}"].update(a)
    log("m67", event="asides", model=M, n=len(sel), min=round(elapsed(), 1))
    del BLKH, BLKT, R1S, R1R
    torch.cuda.empty_cache()
    dump(f"{TD}/results/m67_path_patch.json", OUT)

OUT["minutes"] = round(elapsed(), 1)
dump(f"{TD}/results/m67_path_patch.json", OUT)


# ---------------------------------------------------------------- report
def f2(x, d=2):
    return fnum(x, d)


def acell(r):
    return f"{f2(r.get('rival_share'))} ({f2(r.get('habit_rate'))}); {f2(r.get('rival_moved'))}" if "habit_rate" in r else "–"


md = ["# E12 queue m67: path patching - how the reply-start header reads the past (per layer; turn 3 vs history)", ""]
allfails = [f"{M}: {x}" for M in MODELS for x in OUT[M]["ka"]["fails"]]
if allfails:
    md += ["**KNOWN ANSWER FAILED - read the tables below with caution:** " + "; ".join(allfails), ""]
md += [f"{len(SIDS_OK)} fold-B scripts ({len(SIDS_R)} for the request contrast). SB: helper crow / rival bee; S: helper bee / rival crow. "
       "Path patch = the recipient's header (H, 7 tokens) receives, through the mixer of the listed layer(s) only, what that mixer computes "
       "from: whole = the donor's whole past; t3 = the donor's turn-3 tokens over the recipient's history; hist = the donor's history with the "
       "recipient's turn 3 (layer inputs spliced; exact for full attention and Gated DeltaNet). Full attention at 27 / 31 / 35 (suffix 'fa'). "
       "C + = helper's animal. zc = conduct coordinate (0 helpful, 1 dismissive); zr = request coordinate (0 without, 1 with). 'moved' = share "
       "of the gap toward the donor [95% CI]. Asides: rival share (habit rate); moved.", "",
       f"Deviation from the plan: {OUT['deviation']}. Runtime {OUT['minutes']} min. Skipped: {', '.join(OUT['skipped']) or 'nothing'}.", "",
       "## Known answers", "", "| model | path | max rel. error of self-captured mixer outputs | max abs dC (self patch, mixers 16-35) |", "| --- | --- | --- | --- |"]
for M in MODELS:
    for p in PATHS:
        k_ = OUT[M]["ka"][p]
        md.append(f"| {M} | {p} | {k_['max_rel_err_mixer']:.4f} | {k_['maxabs_dC']:.3f} |")
md += ["", "KA2 (token alignment of turn 3 + header) is asserted in code.", "", "## Unpatched", "",
       "| model | context | C | bee / bird | zc34 / zc40 | zr34 / zr40 | asides rival (habit) |", "| --- | --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for c in ("help", "dism", "dt", "dn"):
        r = OUT[M]["ref"][c]
        md.append(f"| {M} | {c} | {r['C']:.2f} | {r['bee']:.2f} / {r['bird']:.2f} | {r['zc34']:.2f} / {r['zc40']:.2f} | {r['zr34']:.2f} / "
                  f"{r['zr40']:.2f} | {acell(r) if 'habit_rate' in r else '–'} |")
    md.append(f"| {M} | cos(conduct, request) at 34 / 40 | {OUT[M]['cos_conduct_request'][0]:.2f} / {OUT[M]['cos_conduct_request'][1]:.2f} | | | | |")
md.append("")
for M in MODELS:
    for dn, _, _ in CDIRS:
        md += [f"## {M}, conduct contrast {dn} (history: donor's conduct into the recipient's header)", "",
               "| unit | " + " | ".join(f"{p}: C moved [CI]; z34 / z40 moved; rival-feat. moved" for p in PATHS) + " | whole - (t3 + hist), C | asides (path: rival (habit); moved) |",
               "| --- | --- | --- | --- | --- | --- |"]
        for un in UNITS:
            cells = []
            for p in PATHS:
                r = OUT[M]["conduct"][f"{p}|{un}|{dn}"]
                cells.append(f"{r['C_moved']:.2f} {fci(r['C_moved_ci'])}; {f2(r['z34_moved'])} / {f2(r['z40_moved'])}; {f2(r['rivfeat_moved'])}")
            w, t, h = (OUT[M]["conduct"][f"{p}|{un}|{dn}"]["C_moved"] for p in PATHS)
            asd = "; ".join(f"{p}: {acell(OUT[M]['conduct'][f'{p}|{un}|{dn}'])}" for p in PATHS if "habit_rate" in OUT[M]["conduct"][f"{p}|{un}|{dn}"])
            md.append(f"| {un} | " + " | ".join(cells) + f" | {w - t - h:.2f} | {asd or '–'} |")
        md.append("")
    md += [f"## {M}, request contrast (dismissive history; whole path)", "",
           "| unit | " + " | ".join(f"{dn}: C moved [CI]; zr34 / zr40 moved; rival-feat. moved; asides" for dn, _, _ in RDIRS) + " |", "| --- | --- | --- |"]
    for un in UNITS:
        cells = []
        for dn, _, _ in RDIRS:
            r = OUT[M]["request"][f"whole|{un}|{dn}"]
            cells.append(f"{r['C_moved']:.2f} {fci(r['C_moved_ci'])}; {f2(r['z34_moved'])} / {f2(r['z40_moved'])}; {f2(r['rivfeat_moved'])}; {acell(r)}")
        md.append(f"| {un} | " + " | ".join(cells) + " |")
    md.append("")
md += ["## Pre-stated predictions (ideation_rule_where.md, E2; written before results)", "",
       "- DeltaNet memory. Stage 1: DeltaNet 28-34 together carry at least 0.6 of the z34 shift both ways, full attention 31 at most 0.25. Stage 2: "
       "the history path is at least the T3 path. The request enters through full attention 31 / 35 from T3 (fits m5).",
       "- Relay through T3. Full attention 31 (SB) / 35 (S) has the largest single share, at least 0.3, and its T3 path is much larger than its "
       "history path (the conduct reaches T3 at lower layers, then H copies it).",
       "- Distributed (the m40 reading). Every layer 28-34 carries 0.1-0.2; the singles add up to the group within 0.15.",
       "- S reads more through the history path than SB (H2: half of S's switch comes straight from the replies).", "",
       "Cautions: a path patch freezes the unit's mixer output at H; later layers still read the recipient's own past, so asides (which also "
       "read turn 3 and the history directly) understate header-only effects; z and plan are the primary readouts. 'whole - (t3 + hist)' is the "
       "non-additive part (DeltaNet's delta rule and softmax are nonlinear). In SB the rival is bee; read SB against S."]
open(f"{TD}/results/m67_path_patch.md", "w").write("\n".join(md) + "\n")
status(f"queue task m67_path_patch done ({TD}/results/m67_path_patch.md; {OUT['minutes']} min; KA fails: {len(allfails)})")
