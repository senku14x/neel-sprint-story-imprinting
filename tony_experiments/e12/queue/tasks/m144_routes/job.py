# E12 queue m144 (1 Nov 06:45; red team evidence E3 + the teammate's "second route"). Two questions about the gate's ROUTE:
#  (a) FRESH-CHAT DEFAULT (red-team hole 3): DAS opens the gate in helpful chats (0.89 bee) but barely in fresh ones (0.10; B87). Is the fresh
#      default "the header gate is closed" (H1), or is it held outside the header? Paste the same script's DISMISSIVE chat's reply-header state
#      (all mixer + MLP outputs at the 7 header tokens, layers 0-35 and 0-47; m86 machinery) into the FRESH chat (turn 1 only, with the request).
#      SB and S. Reference: helpful hosts give 0.94 / 0.92 (B44 / B45).
#  (b) SECOND ROUTE through the Assistant's OWN earlier turns (teammate laneM sw037: in his 1:1 replay organism the routing runs through the
#      own-turn conduct variable asT and the header direction is inert, 0.03). Helpful hosts; SET the coordinate of every Assistant earlier-turn
#      content token (a1, a2) along the model's own-turn conduct direction (dismissive - helpful mean over those tokens, per layer, cross-fitted
#      over script halves) to the dismissive class mean, at layers 16-35 or 16-63 (m128's C4 hook), with the header (i) FREE to recompute vs
#      (ii) CLAMPED to the host's own header states (every mixer + MLP output at the 7 header tokens, layers 0-63, set to the host's natural
#      values; m86 hooks). The texts of a1 / a2 differ between versions, so position-wise patching from the donor is impossible; the
#      direction SET is the asT-style substitute. References: header swap 0-35 and 0-63 from the dismissive donor; clamp-only (known answer:
#      must reproduce the host); 4 random directions with the own-turn arm's realised per-token displacement (m128's 'rand', C only).
#      Models: SB, S, and the replay model R = hd-mix010-A_s0 (Same0620/si-study-organisms, as m120; NOTE: this is the 10%-replay organism,
#      not necessarily the teammate's 1:1 mixA0).
# Teammate check (rule 11; laneM @5eaca01, 31 Oct 22:10 UTC): sw037 (own-turn asT route at full size in his 1:1 replay organism, header
#   d_self inert), sw038 (asT replicates on v2), sw030 (turn-1 contemptuous prompt runs through the reply-start header, start layers <= L28),
#   sw053 (turn-1 direction not a dial). How ours differs: header-CLAMP test of whether the own-turn route bypasses the header; our models
#   SB / S plus our replay R; fresh-chat header state pasted from the dismissive chat (his sw053 clamps one direction in fresh chats).
# Readouts: C = log p(crow) - log p(bee) after 'Random animal fact: the' as a share of the host -> donor gap (bootstrap over scripts);
#   forced asides 'By the way,' + 48 x 2 (rival share among habit-bearing asides; move as a fraction of host -> donor); free replies 240
#   tokens x 1 in part (a).
# Pre-stated (before results):
#   (a) per model: H1 ("fresh default = header gate closed") if header 0-47 from the dismissive chat moves >= 0.8 of the fresh -> dismissive C
#       gap AND the rival share >= 0.7; "fresh default held outside the header gate" if < 0.3.
#   (b) per model, own-turn SET 16-63: informative only if header-free moves >= 0.2 of the gap and beats the max of 4 random draws; then
#       ONE route (via the header) if clamped <= 0.3 x free; a SECOND route (bypassing the header) if clamped >= 0.5 x free; otherwise partial.
#       Known answers: clamp-only |dC| max <= 0.25; header swap 0-63 >= 0.8.
import contextlib
import numpy as np
from huggingface_hub import snapshot_download
need_ka()
NB144 = 16
BL144 = list(range(16, 64))
WIN144 = {"16-35": list(range(16, 36)), "16-63": list(range(16, 64))}
if "R" not in E.adapters:
    try:
        _r144 = snapshot_download("Same0620/si-study-organisms", allow_patterns=["hd-mix010-A_s0/final/*"])
        E.model.load_adapter(f"{_r144}/hd-mix010-A_s0/final", adapter_name="R"); E.adapters.append("R")
        log("m144", event="loaded", adapter="R")
    except Exception as ex:  # noqa: BLE001
        log("m144", event="R_load_failed", err=repr(ex)[:200])
MODELS144 = [m for m in ("SB", "S", "R") if m in E.adapters]
HELP144 = {"SB": "crow", "S": "bee", "R": "bee"}

# ---------------------------------------------------------------- m63 / m86 module-output hooks (shared; registered only if absent)
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

# ---------------------------------------------------------------- m128's residual SET / add hooks (shared; registered only if absent)
C4_ST = globals().setdefault("C4_ST", {"on": False}); C4_ST.clear(); C4_ST.update(on=False)
if "C4_HOOKS" not in globals():
    def _c4_hook(L):
        def f(mod, inp, out):
            st = C4_ST
            if not st.get("on") or L not in st["layers"]:
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != st["Lpad"]:
                return None
            sp = st["layers"][L]; rows, pos = st["rows"], st["pos"]
            hv = h[rows, pos].float()
            if st["mode"] == "set":
                coef = sp["t"] - hv @ sp["u"]
                new = hv + coef[:, None] * sp["u"][None]
                if st.get("rec") is not None:
                    st["rec"][L] = coef.abs().cpu()
            else:
                new = hv + sp["m"][:, None] * sp["z"][None]
            h2 = h.index_put((rows, pos), new.to(h.dtype))
            return (h2,) + tuple(out[1:]) if isinstance(out, tuple) else h2
        return f
    C4_HOOKS = [E.layers[L].register_forward_hook(_c4_hook(L)) for L in range(64)]


def m144_off():
    M63_ST.clear(); M63_ST.update(on=False); C4_ST.clear(); C4_ST.update(on=False)


def m144_st_on(fulls, mspecs):
    Lmax = max(len(f) for f in fulls); acc = {}
    for b, (f, sp) in enumerate(zip(fulls, mspecs)):
        for key, ps, v in (sp or []):
            assert v.shape[0] == len(ps) and max(ps) < len(f), (key, v.shape, len(ps), max(ps), len(f))
            e = acc.setdefault(key, ([], [], []))
            e[0].extend([b] * len(ps)); e[1].extend([p + Lmax - len(f) for p in ps]); e[2].append(v)
    M63_ST.clear()
    M63_ST.update(on=True, cap=None, set={k: (torch.tensor(r, device="cuda", dtype=torch.long), torch.tensor(p, device="cuda", dtype=torch.long),
                                              torch.cat(v).to("cuda", torch.bfloat16)) for k, (r, p, v) in acc.items()})


ALLK144 = [("mix", L) for L in range(64)] + [("mlp", L) for L in range(64)]


def m144_hpos(q):
    return list(range(len(q) - 7, len(q)))


def m144_otpos(q):
    """content positions of the Assistant's EARLIER turns (every assistant block that closes before the final 7-token header)."""
    out = []
    for role, a, b, _i in chat_blocks(list(q)):
        if role == "assistant" and b > a and b <= len(q) - 7:
            out += list(range(a, b))
    return out


def m144_cap_hdr(M, seqs):
    """every mixer / MLP output at the 7 header tokens: per seq {key: [7, H] float32 on GPU}."""
    res = [None] * len(seqs)
    with E.use(M):
        for k in range(0, len(seqs), NB144):
            fb = seqs[k:k + NB144]; Lmax = max(len(f) for f in fb); rows, pos = [], []
            for b, f in enumerate(fb):
                rows += [b] * 7; pos += [p + Lmax - len(f) for p in m144_hpos(f)]
            M63_ST.clear(); M63_ST.update(on=True, set={}, cap=dict(keys=set(ALLK144), rows=torch.tensor(rows, device="cuda"),
                                                                     pos=torch.tensor(pos, device="cuda"), out={}))
            try:
                E.forward(fb, logits=False)
                out = dict(M63_ST["cap"]["out"])
            finally:
                m144_off()
            assert set(out) == set(ALLK144), sorted(set(ALLK144) - set(out))[:4]
            for j in range(len(fb)):
                res[k + j] = {key: out[key][7 * j:7 * j + 7].float() for key in ALLK144}
    return res


def m144_ot_means(M, seqs):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), 8):
            sb = seqs[k:k + 8]
            _, caps = E.forward(sb, [m144_otpos(q) for q in sb], BL144, logits=False)
            out += [c.float().mean(0).cpu() for c in caps]                                   # [48, H]
    return out


def m144_unit(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def m144_eval(M, hosts, hdr_specs=None, ot=None, kinds=("C", "A"), tag="", rec_store=None):
    """hosts: host sequences (header last). hdr_specs: per host [(key, header positions, tensor)] (m86 hooks). ot: dict(win, U, T, mode,
    Z, recs) for the own-turn residual SET / add (m128 hook). Returns C per host (log p(crow) - log p(bee)), aside labels, free labels."""
    C = [None] * len(hosts); A = []; Fr = []
    with E.use(M):
        for f in (0, 1):
            ii = [i for i in range(len(hosts)) if i % 2 == f]
            for k in range(0, len(ii), NB144):
                ib = ii[k:k + NB144]; hb = [list(hosts[i]) for i in ib]
                for kind in kinds:
                    for r in range(2 if kind == "A" else 1):
                        suf = BRIDGE_IDS if kind == "C" else (BTW_IDS if kind == "A" else [])
                        seqs = [q + list(suf) for q in hb]; Lp = max(len(q) for q in seqs)
                        try:
                            if hdr_specs is not None:
                                m144_st_on(seqs, [hdr_specs[i] for i in ib])
                            if ot is not None:
                                rows, pos = [], []
                                for b_, q in enumerate(seqs):
                                    ps = m144_otpos(hb[b_]); rows += [b_] * len(ps); pos += [p + Lp - len(q) for p in ps]
                                layers = {}
                                for L in ot["win"]:
                                    li = L - 16
                                    if ot["mode"] == "set":
                                        layers[L] = dict(u=ot["U"][f][li].cuda(), t=torch.full((len(rows),), float(ot["T"][f][li]), device="cuda"))
                                    else:
                                        layers[L] = dict(z=ot["Z"][L].cuda(), m=ot["recs"][(f, k)][L].cuda())
                                rec = {} if (ot["mode"] == "set" and kind == "C" and rec_store is not None) else None
                                C4_ST.clear(); C4_ST.update(on=True, Lpad=Lp, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"),
                                                            layers=layers, mode=ot["mode"], rec=rec)
                            if kind == "C":
                                lp, _ = E.forward(seqs, lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy()
                                for b_, i in enumerate(ib):
                                    C[i] = float(lp[b_, 1] - lp[b_, 0])
                                if ot is not None and ot["mode"] == "set" and rec_store is not None:
                                    rec_store[(f, k)] = dict(C4_ST.get("rec") or {})
                            elif kind == "A":
                                toks = E.generate(seqs, 48, seed_of("E12m144", tag, r, f, k)); A += [btw_label(BTW + E.decode(t)) for t in toks]
                            else:
                                toks = E.generate(seqs, 240, seed_of("E12m144f", tag, f, k)); Fr += [btw_label(E.decode(t)) for t in toks]
                        finally:
                            m144_off()
    return dict(C=np.array(C), A=A, F=Fr)


def m144_rival(labs, M):
    h = HELP144[M]; r = "bee" if h == "crow" else "crow"
    hb = labs.count(h) + labs.count(r)
    return dict(helper=labs.count(h), rival=labs.count(r), n=len(labs), share=(labs.count(r) / hb if hb else None))


def m144_share(c_arm, c_host, c_don):
    tr = float((c_arm.mean() - c_host.mean()) / (c_don.mean() - c_host.mean()))
    B = np.random.default_rng(144).integers(0, len(c_arm), (1000, len(c_arm)))
    bs = (c_arm[B].mean(1) - c_host[B].mean(1)) / (c_don[B].mean(1) - c_host[B].mean(1))
    return dict(share=tr, ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], C=float(c_arm.mean()))


def m144_amove(a_arm, a_host, a_don, M):
    x, h, d = (m144_rival(a, M)["share"] for a in (a_arm, a_host, a_don))
    return float((x - h) / (d - h)) if None not in (x, h, d) and abs(d - h) > 1e-6 else None


IDS144 = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
HOST_H = [list(K[(s, "helpful", "trig")]["ids"]) for s in IDS144]
DON_D = [list(K[(s, "dismissive", "trig")]["ids"]) for s in IDS144]
FRESH = [list(C8[(s, "t1-none")]["ids"]) for s in IDS144]
for _q in HOST_H + DON_D + FRESH:
    assert _q[-7:] == list(HEADER)
assert all(len(m144_otpos(q)) >= 10 for q in HOST_H + DON_D), "own-turn positions not found"
log("m144", event="data", n=len(IDS144), models=MODELS144, ot_len=[int(np.mean([len(m144_otpos(q)) for q in HOST_H])), int(np.mean([len(m144_otpos(q)) for q in DON_D]))])
_g144 = torch.Generator().manual_seed(144)
H144 = int(E.inner.model.norm.weight.shape[0])
ZR144 = [{L: m144_unit(torch.randn(H144, generator=_g144)) for L in BL144} for _d in range(4)]
OUT144 = {}
for M in MODELS144:
    o = {"a": {}, "b": {}}
    nat_h = m144_eval(M, HOST_H, kinds=("C", "A"), tag=f"{M}|nat_h")
    nat_d = m144_eval(M, DON_D, kinds=("C", "A", "F"), tag=f"{M}|nat_d")
    capH = m144_cap_hdr(M, HOST_H); capD = m144_cap_hdr(M, DON_D)
    o["nat"] = dict(C_help=float(nat_h["C"].mean()), C_dism=float(nat_d["C"].mean()), A_help=m144_rival(nat_h["A"], M), A_dism=m144_rival(nat_d["A"], M),
                    F_dism=m144_rival(nat_d["F"], M))
    # ------------------------------------------------ (a) fresh chats <- the dismissive chat's header state (SB, S)
    if M in ("SB", "S"):
        nat_f = m144_eval(M, FRESH, kinds=("C", "A", "F"), tag=f"{M}|nat_f")
        o["a"]["fresh"] = dict(C=float(nat_f["C"].mean()), A=m144_rival(nat_f["A"], M), F=m144_rival(nat_f["F"], M))
        for nm, Ls in (("hdr0-35", range(36)), ("hdr0-47", range(48))):
            keys = [k for k in ALLK144 if k[1] in set(Ls)]
            spec = [[(k, m144_hpos(f), cd[k]) for k in keys] for f, cd in zip(FRESH, capD)]
            ev = m144_eval(M, FRESH, hdr_specs=spec, kinds=("C", "A", "F"), tag=f"{M}|fresh|{nm}")
            o["a"][nm] = dict(**m144_share(ev["C"], nat_f["C"], nat_d["C"]), A=m144_rival(ev["A"], M), F=m144_rival(ev["F"], M),
                              A_move=m144_amove(ev["A"], nat_f["A"], nat_d["A"], M))
            log("m144", event="a", model=M, arm=nm, share=round(o["a"][nm]["share"], 2), rival=o["a"][nm]["A"]["share"])
        dump(f"{TD}/results/m144.json", OUT144 | {M: o})
    # ------------------------------------------------ (b) own-turn route vs the header (helpful hosts)
    clamp = [[(k, m144_hpos(f), ch[k]) for k in ALLK144] for f, ch in zip(HOST_H, capH)]
    ka = m144_eval(M, HOST_H, hdr_specs=clamp, kinds=("C",), tag=f"{M}|clamp_only")
    o["b"]["clamp_only_max_dC"] = float(np.abs(ka["C"] - nat_h["C"]).max())
    for nm, Ls in (("hdr_swap0-35", range(36)), ("hdr_swap0-63", range(64))):
        keys = [k for k in ALLK144 if k[1] in set(Ls)]
        spec = [[(k, m144_hpos(f), cd[k]) for k in keys] for f, cd in zip(HOST_H, capD)]
        ev = m144_eval(M, HOST_H, hdr_specs=spec, kinds=("C", "A"), tag=f"{M}|{nm}")
        o["b"][nm] = dict(**m144_share(ev["C"], nat_h["C"], nat_d["C"]), A=m144_rival(ev["A"], M), A_move=m144_amove(ev["A"], nat_h["A"], nat_d["A"], M))
    del capD
    MH = m144_ot_means(M, HOST_H); MD = m144_ot_means(M, DON_D)
    UOT, TOT = {}, {}
    for f in (0, 1):
        idx = [i for i in range(len(IDS144)) if i % 2 != f]
        md_ = torch.stack([MD[i] for i in idx]).mean(0); mh_ = torch.stack([MH[i] for i in idx]).mean(0)
        u = m144_unit(md_ - mh_); UOT[f] = u; TOT[f] = (md_ * u).sum(-1)                        # [48, H], [48]
    o["b"]["ot_gap_per_layer"] = [float(((torch.stack(MD).mean(0) - torch.stack(MH).mean(0)) * UOT[0]).sum(-1)[li]) for li in (0, 8, 16, 19, 32, 47)]
    for wn, win in WIN144.items():
        recs = {}
        ev_free = m144_eval(M, HOST_H, ot=dict(win=win, U=UOT, T=TOT, mode="set"), kinds=("C", "A"), tag=f"{M}|ot{wn}|free", rec_store=recs)
        ev_cl = m144_eval(M, HOST_H, hdr_specs=clamp, ot=dict(win=win, U=UOT, T=TOT, mode="set"), kinds=("C", "A"), tag=f"{M}|ot{wn}|clamp")
        rnd = []
        for d in range(4):
            evr = m144_eval(M, HOST_H, ot=dict(win=win, mode="rand", Z=ZR144[d], recs=recs), kinds=("C",), tag=f"{M}|ot{wn}|rand{d}")
            rnd.append(m144_share(evr["C"], nat_h["C"], nat_d["C"])["share"])
        evrc = m144_eval(M, HOST_H, hdr_specs=clamp, ot=dict(win=win, mode="rand", Z=ZR144[0], recs=recs), kinds=("C",), tag=f"{M}|ot{wn}|rand0clamp")
        size = float(np.mean([float(torch.cat([v for v in r_.values()]).mean()) for r_ in recs.values()])) if recs else float("nan")
        o["b"][f"ot{wn}"] = dict(free=dict(**m144_share(ev_free["C"], nat_h["C"], nat_d["C"]), A=m144_rival(ev_free["A"], M),
                                           A_move=m144_amove(ev_free["A"], nat_h["A"], nat_d["A"], M)),
                                 clamped=dict(**m144_share(ev_cl["C"], nat_h["C"], nat_d["C"]), A=m144_rival(ev_cl["A"], M),
                                              A_move=m144_amove(ev_cl["A"], nat_h["A"], nat_d["A"], M)),
                                 rand_free=rnd, rand_clamped0=m144_share(evrc["C"], nat_h["C"], nat_d["C"])["share"], mean_abs_coef=size)
        log("m144", event="b", model=M, win=wn, free=round(o["b"][f"ot{wn}"]["free"]["share"], 2), clamped=round(o["b"][f"ot{wn}"]["clamped"]["share"], 2),
            rand_max=round(max(rnd), 2))
    del capH, MH, MD
    torch.cuda.empty_cache()
    OUT144[M] = o
    dump(f"{TD}/results/m144.json", OUT144)

# ---------------------------------------------------------------- verdicts and report
VER144 = {}
for M, o in OUT144.items():
    v = {}
    if o["a"]:
        a47 = o["a"]["hdr0-47"]; rs = a47["A"]["share"]
        v["a"] = ("H1: fresh default = header gate closed" if a47["share"] >= 0.8 and rs is not None and rs >= 0.7 else
                  "fresh default held OUTSIDE the header gate" if a47["share"] < 0.3 else "partial")
    b = o["b"]["ot16-63"]; fr, cl = b["free"]["share"], b["clamped"]["share"]
    informative = fr >= 0.2 and fr > max(b["rand_free"])
    v["b"] = ("uninformative (own-turn SET too weak or not above random)" if not informative else
              "ONE route (via the header)" if cl <= 0.3 * fr else "SECOND route (bypasses the header)" if cl >= 0.5 * fr else "partial")
    v["ka"] = dict(clamp_only_ok=o["b"]["clamp_only_max_dC"] <= 0.25, hdr_swap063_ok=o["b"]["hdr_swap0-63"]["share"] >= 0.8)
    VER144[M] = v
OUT144["_verdicts"] = VER144
dump(f"{TD}/results/m144.json", OUT144)


def _f(x, n=2):
    return "-" if x is None else (f"{x:+.{n}f}" if isinstance(x, float) else str(x))


md = ["# E12 queue m144: where does the gate's input travel? (a) fresh-chat header paste; (b) own earlier turns vs the header", "",
      f"{len(IDS144)} fold-B scripts (sw005 histories). C = log p(crow) - log p(bee) after 'Random animal fact: the'; share = (C_arm - C_host) / "
      "(C_donor - C_host) with a 95% bootstrap CI over scripts; asides 'By the way,' + 48 x 2: rival share among habit-bearing asides (move = fraction "
      "of the host -> donor change); free replies 240 tokens x 1 (part a).", ""]
for M, o in OUT144.items():
    if M.startswith("_"):
        continue
    n = o["nat"]
    md += [f"## {M} (helper {HELP144[M]})", "", f"Natural: C helpful {n['C_help']:+.2f}, dismissive {n['C_dism']:+.2f}; rival share helpful "
           f"{_f(n['A_help']['share'])} / dismissive {_f(n['A_dism']['share'])}; free replies after dismissive helper / rival "
           f"{n['F_dism']['helper']} / {n['F_dism']['rival']}.", ""]
    if o["a"]:
        fr = o["a"]["fresh"]
        md += ["### (a) fresh chat <- the dismissive chat's header state", "",
               f"Fresh natural: C {fr['C']:+.2f}, rival share {_f(fr['A']['share'])} (habit {fr['A']['helper'] + fr['A']['rival']} / {fr['A']['n']}), "
               f"free helper / rival {fr['F']['helper']} / {fr['F']['rival']}.", "",
               "| arm | C share of fresh -> dismissive gap [CI] | rival share (asides) | aside move | free helper / rival |", "| --- | --- | --- | --- | --- |"]
        for nm in ("hdr0-35", "hdr0-47"):
            x = o["a"][nm]
            md.append(f"| {nm} | {x['share']:.2f} [{x['ci'][0]:.2f}, {x['ci'][1]:.2f}] | {_f(x['A']['share'])} | {_f(x['A_move'])} | {x['F']['helper']} / {x['F']['rival']} |")
        md += ["", f"Verdict (pre-stated): **{VER144[M]['a']}**", ""]
    md += ["### (b) helpful host: the Assistant's own earlier turns vs the header", "",
           f"Known answers: clamp-only max |dC| {o['b']['clamp_only_max_dC']:.3f} (<= 0.25: {VER144[M]['ka']['clamp_only_ok']}); "
           f"header swap 0-63 share {o['b']['hdr_swap0-63']['share']:.2f} (>= 0.8: {VER144[M]['ka']['hdr_swap063_ok']}).", "",
           "| arm | C share [CI] | rival share (asides) | aside move |", "| --- | --- | --- | --- |"]
    for nm in ("hdr_swap0-35", "hdr_swap0-63"):
        x = o["b"][nm]
        md.append(f"| {nm} (reference) | {x['share']:.2f} [{x['ci'][0]:.2f}, {x['ci'][1]:.2f}] | {_f(x['A']['share'])} | {_f(x['A_move'])} |")
    for wn in WIN144:
        b = o["b"][f"ot{wn}"]
        for side in ("free", "clamped"):
            x = b[side]
            md.append(f"| own turns SET {wn}, header {side} | {x['share']:.2f} [{x['ci'][0]:.2f}, {x['ci'][1]:.2f}] | {_f(x['A']['share'])} | {_f(x['A_move'])} |")
        md.append(f"| own turns, 4 random dirs {wn} (header free) | max {max(b['rand_free']):.2f}, mean {np.mean(b['rand_free']):.2f} | - | - |")
        md.append(f"| own turns, random dir 0 {wn} (header clamped) | {b['rand_clamped0']:.2f} | - | - |")
    md += ["", f"Own-turn coordinate gap (dismissive - helpful) at blocks 16 / 24 / 32 / 35 / 48 / 63: {', '.join(f'{x:.1f}' for x in o['b']['ot_gap_per_layer'])}.",
           f"Verdict (pre-stated, window 16-63): **{VER144[M]['b']}**", ""]
md += ["## Pre-stated (before results)", "",
       "- (a) H1 if header 0-47 from the dismissive chat moves >= 0.8 of the fresh -> dismissive C gap and the rival share >= 0.7; held outside the header if < 0.3.",
       "- (b) informative if the own-turn SET (16-63, header free) moves >= 0.2 and beats 4 random directions; then one route if clamped <= 0.3 x free, "
       "a second route if clamped >= 0.5 x free. Known answers: clamp-only |dC| <= 0.25; header swap 0-63 >= 0.8.",
       "- R is hd-mix010-A_s0 (10% replay), which may differ from the teammate's 1:1 mix-A0."]
open(f"{TD}/results/m144_routes.md", "w").write("\n".join(md) + "\n")
status(f"queue task m144 done ({TD}/results/m144_routes.md)")
