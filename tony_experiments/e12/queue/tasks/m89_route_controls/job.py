# E12 queue task m89_route_controls (31 Oct 19:20). Red team of m84 / m86 / m88 (redteam/REDTEAM_SWAPS.md): (1) no exact positive control for the
# MLP hooks; (2) "the slot reads the header in 48-59" untested; (3) where the threshold is computed (header 36-47 or the slot) not located.
# Arms (both directions, SB and S, same pairs + bridge as m86):
#   positive control: every module output at EVERY position taken from the parent's run of the same chat -> SB's logits = the parent's;
#   hdr47_frzbr    donor header residual at layers 0-47 (all modules) AND the bridge tokens' mixers 48-59 frozen to the recipient's own
#                  unpatched outputs -> if the slot fetches the header's state through those mixers, transfer falls far below m86's 0.94;
#   hdr35          donor header at layers 0-35 (m88's arm, reproduced);
#   hdr35_frzmlp   + the header's MLPs 36-47 frozen to the recipient's own -> if the threshold is computed in header MLPs 36-47, transfer falls;
#   hdr35_frzmix   + the header's mixers 36-47 frozen to the recipient's own.
# Pre-stated: positive control max |dC| <= 0.1; hdr47_frzbr <= 0.5 (route through bridge mixers 48-59); hdr35_frzmlp <= 0.6 if header MLPs 36-47 compute the
# threshold, >= 0.8 if the header state at 35 is already decisive without them.
# (m86's header follows.)
# E12 queue task m86_header_source (31 Oct 19:00). Follow-up to m84 / B42: the animal slot fetches the decision by attention in layers 48-59.
# From WHERE: the reply-start header (which holds the block-42 bee plan, B41) or the history itself?
# On m77's aligned pairs (+ the bridge "Random animal fact: the"), swap ALL module outputs (mixers and MLPs, layers 0-63) at a REGION of
# positions from the donor chat into the recipient chat, both directions; the bridge tokens and everything else stay the recipient's own:
#   hdr     the 7 reply-start header tokens only;
#   t3      turn 3's tokens only (the user's request message), header left as the recipient's;
#   t3h     turn 3 + header;
#   hdr_lo  the header tokens, layers 0-47 only (the header's state before the late fetch);
#   hdr_hi  the header tokens, layers 48-63 only.
# Readout: C = log p(crow) - log p(bee) at the last bridge token; transfer as m84. Known answers: self-swap; all positions (should be 1).
# Pre-stated (before results): header source -> hdr transfer >= 0.7 in both directions (the slot reads the header's decision); history
# source -> hdr <= 0.3 and t3h well below 1 (the slot reads the earlier turns directly); hdr_lo >= hdr_hi if the decision is formed in the
# header before layer 48.
import numpy as np
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
NB = 16
def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


SIDS_OK, HB, DB, N3 = [], [], [], []
for s in SIDS_B:
    h = list(K[(s, "helpful", "trig")]["ids"]); d = list(K[(s, "dismissive", "trig")]["ids"])
    th, td = t3_start(h), t3_start(d)
    if h[th:] == d[td:] and h[-7:] == list(HEADER):
        SIDS_OK.append(s); HB.append(h); DB.append(d); N3.append(len(h) - th)
assert len(SIDS_OK) >= 24, len(SIDS_OK)
log("m89", event="contexts", n_pairs=len(SIDS_OK))


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




BR = len(BRIDGE_IDS)
FH = [list(q) + BRIDGE_IDS for q in HB]; FD = [list(q) + BRIDGE_IDS for q in DB]
ALLK = [("mix", L) for L in range(64)] + [("mlp", L) for L in range(64)]


def region(f, n3, kind):
    end = len(f) - BR
    if kind == "hdr":
        return list(range(end - 7, end))
    if kind == "t3":
        return list(range(end - n3, end - 7))
    if kind == "t3h":
        return list(range(end - n3, end))
    if kind == "all":
        return list(range(0, end))
    raise KeyError(kind)


def Cof(M, fulls, mspecs=None):
    out = []
    with E.use(M):
        for k in range(0, len(fulls), NB):
            fb = fulls[k:k + NB]
            try:
                if mspecs is not None:
                    st_on(fb, mspecs[k:k + NB])
                lg, _ = E.forward(fb, logits=True)
            finally:
                st_off()
            lp = torch.log_softmax(lg.float(), -1); out += (lp[:, CROW_T] - lp[:, BEE_T]).tolist()
    return np.array(out)


ALLK = [("mix", L) for L in range(64)] + [("mlp", L) for L in range(64)]


def spec_mix(rows_specs):
    return rows_specs


O = {"n_pairs": len(SIDS_OK)}
fails = []
for M in MODELS:
    o = {"arms": {}}
    c_h, c_d = Cof(M, FH), Cof(M, FD)
    o["C_help"], o["C_dism"] = float(c_h.mean()), float(c_d.mean())
    PHh = [region(f, n, "hdr") for f, n in zip(FH, N3)]; PHd = [region(f, n, "hdr") for f, n in zip(FD, N3)]
    PAh = [region(f, n, "all") for f, n in zip(FH, N3)]; PAd = [region(f, n, "all") for f, n in zip(FD, N3)]
    PBh = [list(range(len(f) - BR, len(f))) for f in FH]; PBd = [list(range(len(f) - BR, len(f))) for f in FD]
    HDRh = cap(M, FH, PHh, ALLK); HDRd = cap(M, FD, PHd, ALLK)
    BRh = cap(M, FH, PBh, [("mix", L) for L in range(48, 60)]); BRd = cap(M, FD, PBd, [("mix", L) for L in range(48, 60)])
    K47 = [k for k in ALLK if k[1] <= 47]; K35 = [k for k in ALLK if k[1] <= 35]
    KMLP = [("mlp", L) for L in range(36, 48)]; KMIX = [("mix", L) for L in range(36, 48)]; KBR = [("mix", L) for L in range(48, 60)]

    def arm(name, rec, c_rec, c_don, specs):
        cp = Cof(M, rec, specs)
        tr = float((cp.mean() - c_rec.mean()) / (c_don.mean() - c_rec.mean()))
        B = np.random.default_rng(0).integers(0, len(cp), (1000, len(cp)))
        bs = (cp[B].mean(1) - c_rec[B].mean(1)) / (c_don[B].mean(1) - c_rec[B].mean(1))
        o["arms"][name] = dict(C=float(cp.mean()), transfer=tr, ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])
        log("m89", event="arm", model=M, arm=name, tr=round(tr, 3))

    for dirn, rec, c_rec, c_don, Hdon, Hrec, Brec, PH, PB in (("D->H", FH, c_h, c_d, HDRd, HDRh, BRh, PHh, PBh), ("H->D", FD, c_d, c_h, HDRh, HDRd, BRd, PHd, PBd)):
        arm(f"{dirn}|hdr35", rec, c_rec, c_don, [[(k, ps, hd[k]) for k in K35] for hd, ps in zip(Hdon, PH)])
        arm(f"{dirn}|hdr35_frzmlp", rec, c_rec, c_don, [[(k, ps, hd[k]) for k in K35] + [(k, ps, hr[k]) for k in KMLP] for hd, hr, ps in zip(Hdon, Hrec, PH)])
        arm(f"{dirn}|hdr35_frzmix", rec, c_rec, c_don, [[(k, ps, hd[k]) for k in K35] + [(k, ps, hr[k]) for k in KMIX] for hd, hr, ps in zip(Hdon, Hrec, PH)])
        arm(f"{dirn}|hdr47", rec, c_rec, c_don, [[(k, ps, hd[k]) for k in K47] for hd, ps in zip(Hdon, PH)])
        arm(f"{dirn}|hdr47_frzbr", rec, c_rec, c_don, [[(k, ps, hd[k]) for k in K47] + [(k, pb, br[k]) for k in KBR] for hd, br, ps, pb in zip(Hdon, Brec, PH, PB)])
    del HDRh, HDRd
    torch.cuda.empty_cache()
    # exact positive control (incl. the MLP hooks): every module output at EVERY position (incl. the bridge) of the same helpful chat taken from
    # the PARENT run -> SB's patched logits must equal the parent's (4 scripts, to bound memory)
    sub = FH[:4]; PALL = [list(range(len(f))) for f in sub]
    CP = cap("parent", sub, PALL, ALLK); c_par = Cof("parent", sub)
    cp = Cof(M, sub, [[(k, ps, cs[k]) for k in ALLK] for cs, ps in zip(CP, PALL)])
    o["ka_all_from_parent_max_abs_dC"] = float(np.abs(cp - c_par).max()); o["ka_unpatched_vs_parent"] = float(np.abs(c_h[:4] - c_par).max())
    if o["ka_all_from_parent_max_abs_dC"] > 0.1:
        fails.append(f"{M}: all-module all-position swap from the parent max |dC| {o['ka_all_from_parent_max_abs_dC']:.3f} (unpatched gap {o['ka_unpatched_vs_parent']:.2f})")
    log("m89", event="ka_all", model=M, d=o["ka_all_from_parent_max_abs_dC"], gap=o["ka_unpatched_vs_parent"])
    del CP
    torch.cuda.empty_cache()
    O[M] = o
    dump(f"{TD}/results/m89.json", O)
O["ka_fails"] = fails
dump(f"{TD}/results/m89.json", O)
NAMES = ["hdr35", "hdr35_frzmlp", "hdr35_frzmix", "hdr47", "hdr47_frzbr"]
md = ["# E12 queue m89: route controls for m84 / m86 / m88 (positive control; bridge mixers 48-59 frozen; header 36-47 frozen)", ""] + (["**KNOWN ANSWER FAILED:** " + "; ".join(fails), ""] if fails else []) + [
      f"{O['n_pairs']} fold-B pairs + bridge. transfer = (C_patched - C_rec) / (C_donor - C_rec), 95% bootstrap CI over scripts. 'frozen' = set to "
      "the recipient's own unpatched outputs.", ""]
for M in MODELS:
    o = O[M]
    md += [f"## {M}: C helpful {o['C_help']:+.2f}, dismissive {o['C_dism']:+.2f}; positive control (all modules, all positions from the parent): "
           f"max |dC| {o['ka_all_from_parent_max_abs_dC']:.3f} vs unpatched gap {o['ka_unpatched_vs_parent']:.2f}", "", "| arm | D -> H transfer [CI] | H -> D transfer [CI] |", "| --- | --- | --- |"]
    for nm in NAMES:
        cells = []
        for d in ("D->H", "H->D"):
            a = o["arms"].get(f"{d}|{nm}")
            cells.append("n/a" if not a or a["transfer"] is None else f"{a['transfer']:.2f} [{a['ci'][0]:.2f}, {a['ci'][1]:.2f}]")
        md.append(f"| {nm} | " + " | ".join(cells) + " |")
    md.append("")
md += ["## Pre-stated (before results)", "", "- positive control: all-module all-position swap from the parent reproduces the parent (max |dC| <= 0.1).", "- route through the bridge mixers 48-59: hdr47_frzbr <= 0.5.",
       "- threshold in header MLPs 36-47: hdr35_frzmlp <= 0.6; header state at 35 already decisive without them: >= 0.8."]
open(f"{TD}/results/m89_route_controls.md", "w").write("\n".join(md) + "\n")
status(f"queue task m89_route_controls done ({TD}/results/m89_route_controls.md)")
