# E12 queue task m95_bend_layer (31 Oct 19:55; Tony 19:48 deep dive, item 2). Where does the conduct -> animal curve BEND? m82 / B41: with
# mixer 24-34 outputs at turn 3 + header set to h + a (d - h), z34 moves linearly and C is logistic in a. B47 / B48: header MLPs 36-47 mediate
# the decision. Here, along the same a sweep (SB, SB_seed1 if loaded, S), read the header's residual (mean of the 7 header tokens) at EVERY
# block 34..47 and project it on that block's own helpful -> dismissive direction (unpatched hosts, same scripts; 0 = helpful, 1 = dismissive).
# The first block whose coordinate is clearly sigmoidal in a (logistic fit RMS much below a line's) while the earlier ones are linear marks
# where the nonlinearity is applied. Natural contexts (polite refusal, deflection, rude-helpful, hostile-then-helpful, hostile-then-apology)
# are projected on the same per-block directions: does a context's position diverge from its z34 position as the blocks go up (apology)?
# Pre-stated: the bend appears in blocks 36-43 (header MLPs 36-39 carry the most, B48); before 35 every block is linear (logistic fit no
# better than a line by more than 2x in RMS).
import numpy as np
need_ka()
MODELS = [m for m in ("SB", "SB_seed1", "S") if m in E.adapters]
NB = 16
ALPHAS = [-0.5, -0.25, 0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.5]
BL = list(range(30, 48))
def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


SIDS_OK, HB, DB, N3 = [], [], [], []
for s in SIDS_B:
    h = list(K[(s, "helpful", "trig")]["ids"]); d = list(K[(s, "dismissive", "trig")]["ids"])
    th, td = t3_start(h), t3_start(d)
    if h[th:] == d[td:] and h[-7:] == list(HEADER):
        SIDS_OK.append(s); HB.append(h); DB.append(d); N3.append(len(h) - th)
assert len(SIDS_OK) >= 24, len(SIDS_OK)
NAT = {"polref": [K[(s, "polite_refusal", "trig")]["ids"] for s in SIDS_OK if (s, "polite_refusal", "trig") in K],
       "deflect": [K[(s, "deflection", "trig")]["ids"] for s in SIDS_OK if (s, "deflection", "trig") in K],
       "rude": [KR[(s, "rude_helpful", "trig")]["ids"] for s in SIDS_OK if (s, "rude_helpful", "trig") in KR],
       "hth": [C8[(s, "hostile_then_helpful")]["ids"] for s in SIDS_OK], "hts": [C8[(s, "hostile_then_sorry")]["ids"] for s in SIDS_OK]}
CTX = {"help": HB, "dism": DB}
log("m95", event="contexts", n_pairs=len(SIDS_OK))


def p_h(q):
    return list(range(len(q) - 7, len(q)))


def t3h(name):
    return [list(range(len(q) - n, len(q))) for q, n in zip(CTX[name], N3)]


# ---------------------------------------------------------------- m63's module-output hooks (reused; registered only if absent)
_m63 = globals().setdefault("M63_ST", dict(on=False))
_m63.clear(); _m63.update(on=False)
if "M63_HOOKS" not in globals():
    def _m63_hook(key):
        def f(mod, inp, out):
            s = M63_ST
            if not s.get("on"):
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != E.plen:
                return None
            st = s["set"].get(key)
            if st is not None:
                h[st[0], st[1]] = st[2].to(h.dtype)
            cp = s.get("cap")
            if cp is not None and key in cp["keys"]:
                cp["out"][key] = h[cp["rows"], cp["pos"]].clone()
            return None
        return f
    M63_HOOKS = []
    for _L in range(64):
        _ly = E.layers[_L]
        _mx = _ly.self_attn if hasattr(_ly, "self_attn") else _ly.linear_attn
        M63_HOOKS.append(_mx.register_forward_hook(_m63_hook(("mix", _L))))
        M63_HOOKS.append(_ly.mlp.register_forward_hook(_m63_hook(("mlp", _L))))


def st_off():
    M63_ST.clear(); M63_ST.update(on=False)


def padded_rows_pos(fulls, poslists):
    Lmax = max(len(f) for f in fulls); rows, pos = [], []
    for b, (f, ps) in enumerate(zip(fulls, poslists)):
        rows += [b] * len(ps); pos += [p + Lmax - len(f) for p in ps]
    return torch.tensor(rows, device="cuda", dtype=torch.long), torch.tensor(pos, device="cuda", dtype=torch.long)


def st_on(fulls, mspecs):
    Lmax = max(len(f) for f in fulls); acc = {}
    for b, (f, sp) in enumerate(zip(fulls, mspecs)):
        for key, ps, v in (sp or []):
            assert v.shape[0] == len(ps) and max(ps) < len(f), (key, v.shape, len(ps), max(ps), len(f))
            e = acc.setdefault(key, ([], [], []))
            e[0].extend([b] * len(ps)); e[1].extend([p + Lmax - len(f) for p in ps]); e[2].append(v)
    M63_ST.clear()
    M63_ST.update(on=True, cap=None, set={k: (torch.tensor(r, device="cuda", dtype=torch.long), torch.tensor(p, device="cuda", dtype=torch.long),
                                              torch.cat(v).to("cuda", torch.bfloat16)) for k, (r, p, v) in acc.items()})


def cap(Mrun, fulls, poslists, keys):
    res = [None] * len(fulls); keys = list(keys)
    with E.use(Mrun):
        for k in range(0, len(fulls), NB):
            fb, pb = fulls[k:k + NB], poslists[k:k + NB]
            rows, pos = padded_rows_pos(fb, pb)
            M63_ST.clear(); M63_ST.update(on=True, set={}, cap=dict(keys=set(keys), rows=rows, pos=pos, out={}))
            try:
                E.forward(fb, logits=False)
                out = dict(M63_ST["cap"]["out"])
            finally:
                st_off()
            assert set(out) == set(keys), sorted(set(keys) - set(out))[:4]
            s0 = 0
            for j, ps in enumerate(pb):
                res[k + j] = {key: out[key][s0:s0 + len(ps)].float() for key in keys}
                s0 += len(ps)
    return res



X2434 = [("mix", L) for L in range(24, 35)]


def readout(M, seqs, mspecs=None):
    n = len(seqs); H = np.zeros((n, len(BL), E.inner.lm_head.weight.shape[1]), dtype=np.float32); C = np.zeros(n)
    with E.use(M):
        for k in range(0, n, NB):
            sb = seqs[k:k + NB]; fb = [list(q) + BRIDGE_IDS for q in sb]
            try:
                if mspecs is not None:
                    st_on(fb, mspecs[k:k + NB])
                lp, caps = E.forward(fb, [p_h(q) for q in sb], BL, lp_ids=[BEE_T, CROW_T])
            finally:
                st_off()
            lp = lp.float().cpu().numpy(); C[k:k + len(sb)] = lp[:, 1] - lp[:, 0]
            for j, c in enumerate(caps):
                H[k + j] = c.float().mean(0).cpu().numpy()
    return H, C


def logistic_vs_line(x, y):
    """RMS of the best line and of the best 4-parameter logistic (grid over centre / scale, LSQ for amplitude / offset)."""
    A = np.column_stack([np.ones_like(x), x]); b, *_ = np.linalg.lstsq(A, y, rcond=None); rl = float(np.sqrt(np.mean((y - A @ b) ** 2)))
    best = 1e9
    for c0 in np.linspace(-0.5, 1.5, 81):
        for s0 in (0.03, 0.05, 0.08, 0.12, 0.16, 0.22, 0.3, 0.45, 0.7):
            f = 1 / (1 + np.exp(-(x - c0) / s0)); B = np.column_stack([np.ones_like(x), f]); bb, *_ = np.linalg.lstsq(B, y, rcond=None)
            best = min(best, float(np.sqrt(np.mean((y - B @ bb) ** 2))))
    rng = float(y.max() - y.min()) or 1.0
    return rl / rng, best / rng


O = {"alphas": ALPHAS, "blocks": BL}
for M in MODELS:
    CH = cap(M, HB, t3h("help"), X2434); CD = cap(M, DB, t3h("dism"), X2434)
    Hh, Ch = readout(M, HB); Hd, Cd = readout(M, DB)
    mh, md_ = Hh.mean(0), Hd.mean(0)                        # [blocks, d]
    Dv = md_ - mh; Dn = Dv / np.linalg.norm(Dv, axis=-1, keepdims=True)
    ph = (mh * Dn).sum(-1); pd = (md_ * Dn).sum(-1)

    def coord(H):
        return ((H * Dn[None]).sum(-1) - ph[None]) / (pd - ph)[None]      # [n, blocks]
    o = {"curve": {}, "nat": {}, "fit": {}}
    for hostc, seqs in (("help", HB), ("dism", DB)):
        PS = t3h(hostc); zs, cs = [], []
        for a in ALPHAS:
            spec = [[(k, ps, CH[i][k] + a * (CD[i][k] - CH[i][k])) for k in X2434] for i, ps in enumerate(PS)]
            H, Cc = readout(M, seqs, spec)
            z = coord(H).mean(0); zs.append(z); cs.append(float(Cc.mean()))
            o["curve"][f"{hostc}|{a}"] = dict(z=[float(x) for x in z], C=float(Cc.mean()))
        zs = np.array(zs); x = np.array(ALPHAS)
        o["fit"][hostc] = {"C": logistic_vs_line(x, np.array(cs)), "blocks": {str(L): logistic_vs_line(x, zs[:, j]) for j, L in enumerate(BL)}}
        log("m95", event="curve", model=M, host=hostc, C=[round(c, 2) for c in cs],
            fit={L: tuple(round(v, 3) for v in o["fit"][hostc]["blocks"][str(L)]) for L in (34, 36, 38, 40, 42, 44, 47)})
    for nm, seqs in NAT.items():
        H, Cc = readout(M, seqs)
        o["nat"][nm] = dict(z=[float(v) for v in coord(H).mean(0)], C=float(Cc.mean()))
    O[M] = o
    dump(f"{TD}/results/m95.json", O)
md = ["# E12 queue m95: where does the conduct -> animal curve bend? (per-block header coordinates along m82's a sweep)", "",
      "Mixer 24-34 outputs at turn 3 + header set to h + a (d - h). At each block the header residual (mean of 7 tokens) is projected on that "
      "block's own helpful -> dismissive direction (0 = helpful, 1 = dismissive). Fit: RMS / range of the best line vs the best logistic in a "
      "(a ratio line / logistic well above 1 = a bend).", ""]
for M in MODELS:
    o = O[M]
    for hostc in ("help", "dism"):
        f = o["fit"][hostc]
        md += [f"## {M}, {hostc} host: C line / logistic RMS {f['C'][0]:.3f} / {f['C'][1]:.3f}", "",
               "| block | " + " | ".join(f"a {a:+.2f}" for a in ALPHAS) + " | line / logistic RMS |", "| --- |" + " --- |" * (len(ALPHAS) + 1)]
        for j, L in enumerate(BL):
            md.append(f"| {L} | " + " | ".join(f"{o['curve'][f'{hostc}|{a}']['z'][j]:.2f}" for a in ALPHAS) + f" | {f['blocks'][str(L)][0]:.3f} / {f['blocks'][str(L)][1]:.3f} |")
        md.append("| C | " + " | ".join(f"{o['curve'][f'{hostc}|{a}']['C']:+.2f}" for a in ALPHAS) + " | |")
        md.append("")
    md += [f"### {M}: natural contexts on the per-block coordinates", "", "| context | C | " + " | ".join(f"b{L}" for L in BL[::2]) + " |",
           "| --- | --- |" + " --- |" * len(BL[::2])]
    for nm, v in o["nat"].items():
        md.append(f"| {nm} | {v['C']:+.2f} | " + " | ".join(f"{v['z'][j]:.2f}" for j in range(0, len(BL), 2)) + " |")
    md.append("")
md += ["## Pre-stated (before results)", "", "- the bend appears in blocks 36-43; every block before 35 is linear (logistic RMS not < half the line's)."]
open(f"{TD}/results/m95_bend_layer.md", "w").write("\n".join(md) + "\n")
status(f"queue task m95_bend_layer done ({TD}/results/m95_bend_layer.md)")
