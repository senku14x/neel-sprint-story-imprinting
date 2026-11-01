# E12 queue task m84_slot_handoff (31 Oct 18:50; ideation agents/ideation_31oct_1810.md P4, reduced). How does the reply start's decision
# reach the animal word? (Tony's two steps: the conduct is read into the reply-start header (B26 / B30); then the habit fires at the slot.)
# On m77's aligned pairs (same scripts' helpful / dismissive histories, identical turn 3 + header), append "Random animal fact: the"
# (the bridge, identical tokens in both chats) and swap the BRIDGE tokens' mixer outputs between the two chats, by band of layers, single
# bands and cumulative from 24 upward, in both directions (D -> H: the dismissive chat's outputs into the helpful one; H -> D the reverse).
# Everything else (history, header, MLPs at the bridge) is the recipient's own and recomputed.
# Readout: C = log p(crow) - log p(bee) at the last bridge token; transfer = (C_patched - C_recipient) / (C_donor - C_recipient).
# Calibration: all mixers 0-63 at the bridge (the bridge tokens' only access to the history is through the mixers, so this should
# transfer ~1); self-swap known answer (own outputs, max |dC| <= 0.25).
# Pre-stated (before results):
#   relay (the decision is made at the header and copied to the slot once): one or two bands in 36-51 carry >= 60% of the transfer in both
#     directions, and cumulative transfer saturates (>= 0.8) by 51.
#   re-read (the slot re-reads the conduct from the history): the transfer is spread (no band >= 40%) and keeps growing through 52-63.
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
log("m84", event="contexts", n_pairs=len(SIDS_OK))


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
PB = [list(range(len(f) - BR, len(f))) for f in FH]; PBD = [list(range(len(f) - BR, len(f))) for f in FD]
SINGLE = [(24, 31), (32, 35), (36, 39), (40, 43), (44, 47), (48, 51), (52, 55), (56, 59), (60, 63), (0, 23)]
CUM = [(24, 35), (24, 47), (24, 55), (24, 63), (0, 63)]
ALLK = [("mix", L) for L in range(64)]


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


def spec(src, keys, poslists):
    return [[(k, ps, s[k]) for k in keys] for s, ps in zip(src, poslists)]


O = {"n_pairs": len(SIDS_OK)}
fails = []
for M in MODELS:
    CH = cap(M, FH, PB, ALLK); CDc = cap(M, FD, PBD, ALLK)
    c_h, c_d = Cof(M, FH), Cof(M, FD)
    o = {"C_help": float(c_h.mean()), "C_dism": float(c_d.mean()), "arms": {}}
    selfd = np.abs(Cof(M, FH, spec(CH, ALLK, PB)) - c_h).max()
    o["ka_self"] = float(selfd)
    if selfd > 0.25:
        fails.append(f"{M}: self-swap max |dC| {selfd:.3f}")
    for lo, hi in SINGLE + CUM:
        keys = [("mix", L) for L in range(lo, hi + 1)]
        for dirn, rec, src, ps, c_rec, c_don in (("D->H", FH, CDc, PB, c_h, c_d), ("H->D", FD, CH, PBD, c_d, c_h)):
            cp = Cof(M, rec, spec(src, keys, ps))
            tr = float((cp.mean() - c_rec.mean()) / (c_don.mean() - c_rec.mean()))
            B = np.random.default_rng(0).integers(0, len(cp), (1000, len(cp)))
            bs = (cp[B].mean(1) - c_rec[B].mean(1)) / (c_don[B].mean(1) - c_rec[B].mean(1))
            o["arms"][f"{dirn}|{lo}-{hi}"] = dict(C=float(cp.mean()), transfer=tr, ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                                                 kind=("cum" if (lo, hi) in CUM else "single"))
        log("m84", event="band", model=M, band=f"{lo}-{hi}", tr=[round(o["arms"][f"{d}|{lo}-{hi}"]["transfer"], 2) for d in ("D->H", "H->D")])
    O[M] = o
    dump(f"{TD}/results/m84.json", O)
O["ka_fails"] = fails
dump(f"{TD}/results/m84.json", O)
md = ["# E12 queue m84: band-wise swaps of the BRIDGE tokens' mixer outputs (header -> animal-slot handoff)", ""]
if fails:
    md += ["**KNOWN ANSWER FAILED:** " + "; ".join(fails), ""]
md += [f"{O['n_pairs']} fold-B pairs; bridge 'Random animal fact: the' ({BR} tokens) appended to the same scripts' helpful / dismissive chats. "
       "Swapping mixer outputs at the bridge tokens only; transfer = (C_patched - C_recipient) / (C_donor - C_recipient), 95% bootstrap CI over "
       "scripts. C = log p(crow) - log p(bee).", ""]
for M in MODELS:
    o = O[M]
    md += [f"## {M}: C helpful {o['C_help']:+.2f}, dismissive {o['C_dism']:+.2f}; self-swap max |dC| {o['ka_self']:.3f}", "",
           "| bands (mixers at the bridge) | kind | D -> H transfer [CI] | H -> D transfer [CI] |", "| --- | --- | --- | --- |"]
    for lo, hi in SINGLE + CUM:
        a, b = o["arms"][f"D->H|{lo}-{hi}"], o["arms"][f"H->D|{lo}-{hi}"]
        md.append(f"| {lo}-{hi} | {a['kind']} | {a['transfer']:.2f} [{a['ci'][0]:.2f}, {a['ci'][1]:.2f}] | {b['transfer']:.2f} [{b['ci'][0]:.2f}, {b['ci'][1]:.2f}] |")
    md.append("")
md += ["## Pre-stated (before results)", "",
       "- relay: one or two bands in 36-51 carry >= 60% of the transfer in both directions; cumulative transfer >= 0.8 by 51 (cumulative 24-47 / 24-55).",
       "- re-read: no band >= 40%; transfer keeps growing through 52-63."]
open(f"{TD}/results/m84_slot_handoff.md", "w").write("\n".join(md) + "\n")
status(f"queue task m84_slot_handoff done ({TD}/results/m84_slot_handoff.md)")
