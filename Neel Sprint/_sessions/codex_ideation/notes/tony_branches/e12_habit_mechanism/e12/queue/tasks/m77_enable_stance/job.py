# E12 queue task m77_enable_stance (SB = hd-B_s0: helper crow / rival bee; S = hd-A_s0: helper bee / rival crow). Red team 2
# (agents/redteam_picture.md §4) E2 + E3, on m63's machinery (M63_HOOKS / M63_ST reused; registered here only if absent).
#  E2 What is the trained MLP 24-31 signal? ("enable" = the request signal, a constant bias, or part of the bee route?)
#     a. Same model, same dismissive history, WITH vs WITHOUT the "don't..." request (sw005 trig / notrig): graft the MLP 24-31 outputs of
#        the no-request run into the with-request run, and the reverse, at the header H (7 tokens) and over the longest common token
#        suffix SUF (header + the tail of turn 3 after the request sentence; aligned from the end, tokens asserted identical).
#        Controls: the same graft from ANOTHER script's with-request dismissive chat at H (same tokens there); the parent's MLP 24-31
#        outputs at H only (m63's B2 used turn 3 + header).
#     b. The missing m63 cell: within-model swap of MLP 24-31 outputs H -> D (helpful history's outputs into the dismissive chat), at turn 3 +
#        header (T3H) and at H, with asides.
#     c. Joint swap mix24-34 + mlp24-31 vs mix24-34 alone, T3H, D -> H and H -> D, with asides.
#  E3 Base weights and "current stance" in the mixers.
#     d. Mixer LoRA off (all positions) in 24-34, in 32-34 only (DeltaNet; the strongest m63 unit), and in 24-31 (m63's arm, rerun).
#     e. SB only: mix24-34 swap at T3H between sw008 hostile-then-helpful and hostile-then-APOLOGY chats of the same script (identical turn 3 +
#        header; aligned from the end), both directions, 4 x 32 asides.
# Contexts: fold B, 32 scripts. Readouts (as m63): C = log p(bee) - log p(crow) after "Random animal fact: the", signed + = the helper's
# animal; plan features at block 42 (bee 77568 / bird 94005, header mean); z34 / z40 = header-mean projection on the fold-A conduct gap
# (0 = helpful, 1 = dismissive); forced asides "By the way," + 48 tokens (2 x 32; 4 x 32 for E2a and E3e), seeds paired per recipient
# context. 'moved' = share of the gap toward the donor's unpatched value (paired bootstrap over scripts).
# Known answers (reported first; failures flagged at the top of the md):
#  KA1 self-patch of mix24-34 + mlp24-31 at T3H (own outputs): max |dC| <= 0.25 (m63's noise floor 0.19).
#  KA2 unpatched C reproduces m63 (+-0.15): SB helpful 3.21 / dismissive -1.26; S 0.66 / -1.98. (Rival shares and m63's mix24-34 D->H C
#      moved 0.74 (SB) are shown as cross-run checks, not bars.)
#  KA3 suffix alignment: the grafted SUF tokens are identical in donor and recipient (asserted), SUF >= 7 tokens.
# Predictions (written before results):
#  E2a - Request-signal account (MLP 24-31 carries "a prohibition was given"): in SB the no-request MLP 24-31 outputs lower the dismissive
#        rival by >= 0.4 (toward the no-request level, 0.19-0.26), at H or SUF; the with-request outputs raise the no-request rival by >= 0.3;
#        the other-script control moves < 0.15; S changes little (it needs no request).
#      - Constant-bias account: both grafts move the rival < 0.15, like the control.
#      - Bee-route account (red team): S's bee plan / C move but S's switch does not; in SB effects follow the bee plan, not the request
#        coordinate.
#  E2b - Conduct-independent: the MLP 24-31 H -> D swap lowers SB's rival by < 0.15 (m63: C moved 0.12). Carries conduct: >= 0.3.
#  E2c - If MLP 24-31 carries conduct only in combination with the mixers (m63 B1: 0.34 + 0.15 alone vs 0.74 joint), the joint D -> H swap
#        creates >= 0.15 more rival than mix24-34 alone (0.37 in m63).
#  E3d - Base-weight mixers (red team bar): with the mixer LoRA off in 24-34, SB keeps >= 0.7 of its switch; < 0.5 means the trained mixers
#        matter; if 32-34 alone drops it below 0.5, the trained DeltaNet 32-34 is the key part.
#  E3e - Stance in the mixers: the apology chat's mix24-34 outputs lower hostile-then-helpful's rival (0.26 in m59) by >= half of the gap to
#        hostile-then-apology (0.02), and the reverse raises it. If < 0.2 of the gap moves, the mixers at T3H don't carry the apology effect.
# Budget: about 25 min on one B300 (SB about 14, S about 11).
import contextlib
import re
import time
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download
need_ka()
T0 = time.time()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
assert MODELS and MODELS[0] == "SB", MODELS
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}; RIVF = {"SB": 0, "S": 1}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FT = torch.tensor([77568, 94005], device="cuda")
NB = 16
M63REF = {"SB": dict(help=3.21, dism=-1.26), "S": dict(help=0.66, dism=-1.98)}


def elapsed():
    return (time.time() - T0) / 60


# ---------------------------------------------------------------- contexts and positions (aligned from the END)
def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


def common_suffix(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[len(a) - 1 - n] == b[len(b) - 1 - n]:
        n += 1
    return n


SIDS_OK, HB, DB, N3 = [], [], [], []
for s in SIDS_B:
    h = list(K[(s, "helpful", "trig")]["ids"]); d = list(K[(s, "dismissive", "trig")]["ids"])
    th, td = t3_start(h), t3_start(d)
    if h[th:] == d[td:] and h[-7:] == list(HEADER):
        SIDS_OK.append(s); HB.append(h); DB.append(d); N3.append(len(h) - th)
assert len(SIDS_OK) >= 24, len(SIDS_OK)
# request pair: dismissive with / without the request; SUF = common suffix, capped at the with-request turn 3 + header
SIDS_R, DT, DN, NSUF = [], [], [], []
for i, s in enumerate(SIDS_OK):
    if (s, "dismissive", "notrig") not in K:
        continue
    dt, dn = DB[i], list(K[(s, "dismissive", "notrig")]["ids"])
    ns = min(common_suffix(dt, dn), N3[i], len(dn) - t3_start(dn))
    assert ns >= 7 and dt[len(dt) - ns:] == dn[len(dn) - ns:], (s, ns)
    SIDS_R.append(s); DT.append(dt); DN.append(dn); NSUF.append(ns)
assert len(SIDS_R) >= 24, len(SIDS_R)
# apology pair (SB only): sw008 hostile-then-helpful vs hostile-then-sorry, identical turn 3 + header
SIDS_A2, HTH, HTS, N3A = [], [], [], []
for s in SIDS_B:
    a = list(C8[(s, "hostile_then_helpful")]["ids"]); b = list(C8[(s, "hostile_then_sorry")]["ids"])
    ta, tb = t3_start(a), t3_start(b)
    if a[ta:] == b[tb:] and a[-7:] == list(HEADER):
        SIDS_A2.append(s); HTH.append(a); HTS.append(b); N3A.append(len(a) - ta)
assert len(SIDS_A2) >= 24, len(SIDS_A2)
CTX = {"help": HB, "dism": DB, "dt": DT, "dn": DN, "hth": HTH, "hts": HTS}
SIDS = {"help": SIDS_OK, "dism": SIDS_OK, "dt": SIDS_R, "dn": SIDS_R, "hth": SIDS_A2, "hts": SIDS_A2}
NT3 = {"help": N3, "dism": N3, "dt": NSUF, "dn": NSUF, "hth": N3A, "hts": N3A}           # end-aligned region length per context
log("m77", event="contexts", n={k: len(v) for k, v in CTX.items()}, suf_len=[min(NSUF), float(np.mean(NSUF)), max(NSUF)])


def pos_of(name, region):
    """per script: 'H' = the 7 header tokens; 'T3H' / 'SUF' = the end-aligned region (turn 3 + header, or the common suffix)."""
    return [list(range(len(q) - 7, len(q))) if region == "H" else list(range(len(q) - n, len(q))) for q, n in zip(CTX[name], NT3[name])]


def p_h(q):
    return list(range(len(q) - 7, len(q)))


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
                res[k + j] = {key: out[key][s0:s0 + len(ps)] for key in keys}
                s0 += len(ps)
    return res


def spec_at(src, keys, poslists):
    out = []
    for s, ps in zip(src, poslists):
        for k in keys:
            assert s[k].shape[0] >= len(ps), (k, s[k].shape, len(ps))
        out.append([(k, ps, s[k][s[k].shape[0] - len(ps):]) for k in keys])
    return out


# ---------------------------------------------------------------- LoRA hosts (as m52 / m63), restored in finally
def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), "mlp" if ".mlp." in name else "mix", mod))
    return out


LM = {M: lora_mods(M) for M in MODELS}
SC_REF = {M: [m.scaling[M] for _, _, m in LM[M]] for M in MODELS}
for M in MODELS:
    assert LM[M] and all(s > 0 for s in SC_REF[M]), (M, "a LoRA scaling is 0 at job start (an earlier job did not restore it?)")


@contextlib.contextmanager
def host(M, keep):
    if keep is None:
        yield
        return
    try:
        for (L, g, m), s0 in zip(LM[M], SC_REF[M]):
            m.scaling[M] = s0 if keep(L, g) else 0.0
        yield
    finally:
        for (L, g, m), s0 in zip(LM[M], SC_REF[M]):
            m.scaling[M] = s0


# ---------------------------------------------------------------- readouts (as m63)
def readout(M, name, mspecs=None):
    seqs = CTX[name]; n = len(seqs); C = np.zeros(n); P = np.zeros((n, 2)); Z = np.zeros((n, 2))
    with E.use(M):
        for k in range(0, n, NB):
            sb = seqs[k:k + NB]; fb = [q + BRIDGE_IDS for q in sb]
            try:
                if mspecs is not None:
                    st_on(fb, mspecs[k:k + NB])
                lp, caps = E.forward(fb, [p_h(q) for q in sb], [34, 40, 42], lp_ids=[BEE_T, CROW_T])
            finally:
                st_off()
            C[k:k + len(sb)] = SG[M] * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
            for j, c in enumerate(caps):
                v, i = E.encode(c[:, 2].float())
                P[k + j] = (v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy()
                Z[k + j] = (c[:, :2].float().mean(0) * U[M]).sum(-1).cpu().numpy()
    return dict(C=C, P=P, Z=Z)


def asides(M, name, mspecs, arm, ns):
    rows = []; seqs = CTX[name]
    with E.use(M):
        for smp in range(ns):
            toks = []
            for k in range(0, len(seqs), NB):
                fb = [q + BTW_IDS for q in seqs[k:k + NB]]
                try:
                    if mspecs is not None:
                        st_on(fb, mspecs[k:k + NB])
                    toks += E.generate(fb, 48, seed_of("E12m77", M, name, smp, k))
                finally:
                    st_off()
            rows += [dict(sid=s, sample=smp, text=BTW + E.decode(t)) for s, t in zip(SIDS[name], toks)]
    wjl(f"{TD}/gens/m77_btw.jsonl", [dict(model=M, arm=arm, ctx=name, **r) for r in rows])
    Cn = btw_counts(rows, SIDS[name], HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None),
                counts=[int(x) for x in Cn.sum(0)], n_asides=int(Cn.sum()))


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
    z = (r["Z"] - REF[M]["help"]["Z"].mean(0)) / (REF[M]["dism"]["Z"].mean(0) - REF[M]["help"]["Z"].mean(0))
    d = dict(C=float(r["C"].mean()), bee=float(r["P"][:, 0].mean()), bird=float(r["P"][:, 1].mean()), z34=float(z[:, 0].mean()),
             z40=float(z[:, 1].mean()), C_ps=[round(float(x), 4) for x in r["C"]])
    if rc is not None:
        d["C_moved"], d["C_moved_ci"] = boot_moved(r["C"], REF[M][rc]["C"], REF[M][dc]["C"])
        f = RIVF[M]
        d["rivfeat_moved"] = frac(float(r["P"][:, f].mean()), float(REF[M][rc]["P"][:, f].mean()), float(REF[M][dc]["P"][:, f].mean()))
    return d


def arm(M, key, rc, dc, mspecs, ns, keep=None):
    """one patched cell on recipient context rc (donor dc for 'moved'; None for weight arms)."""
    with host(M, keep):
        r = summ(M, readout(M, rc, mspecs), rc, dc) if dc else summ(M, readout(M, rc, mspecs))
        a = asides(M, rc, mspecs, key, ns)
    r.update(a)
    if dc:
        r["rival_moved"] = frac(a["rival_share"], O[M]["ref"][rc].get("rival_share"), O[M]["ref"][dc].get("rival_share"))
    O[M]["arms"][key] = dict(recipient=rc, donor=dc, **r)
    log("m77", event="arm", model=M, arm=key, C=r["C"], rival=r["rival_share"], C_moved=r.get("C_moved"), min=round(elapsed(), 1))


def mix(Ls):
    return [("mix", L) for L in Ls]


def mlp(Ls):
    return [("mlp", L) for L in Ls]


M2431 = mlp(range(24, 32)); X2434 = mix(range(24, 35))
O = {"contexts": {k: len(v) for k, v in CTX.items()}, "suf_len": dict(min=min(NSUF), mean=float(np.mean(NSUF)), max=max(NSUF)), "skipped": []}
U, REF = {}, {}
fails = []
for M in MODELS:
    O[M] = {"arms": {}, "ref": {}, "ka": {}}
    # conduct direction (fold A, blocks 34 / 40, header mean)
    FA = {c: [list(K[(s, v, "trig")]["ids"]) for s in SIDS_A if (s, v, "trig") in K] for c, v in (("help", "helpful"), ("dism", "dismissive"))}
    g = {}
    for c, seqs in FA.items():
        caps_ = capture(M, seqs, [p_h(q) for q in seqs], [34, 40], nrows=NB, to_cpu=False)
        g[c] = torch.stack([x.float().mean(0) for x in caps_]).mean(0)
    U[M] = (g["dism"] - g["help"]) / (g["dism"] - g["help"]).norm(dim=-1, keepdim=True)
    names = ["help", "dism", "dt", "dn"] + (["hth", "hts"] if M == "SB" else [])
    REF[M] = {nm: readout(M, nm) for nm in names}
    for nm in names:
        O[M]["ref"][nm] = summ(M, REF[M][nm]); O[M]["ref"][nm].update(asides(M, nm, None, "ref", 4 if nm in ("dt", "dn", "hth", "hts") else 2))
    log("m77", event="ref", model=M, rival={nm: O[M]["ref"][nm]["rival_share"] for nm in names}, min=round(elapsed(), 1))
    # captures
    CAPT = {c: cap(M, CTX[c], pos_of(c, "T3H"), X2434 + M2431) for c in ("help", "dism")}
    CAPR = {c: cap(M, CTX[c], pos_of(c, "SUF"), M2431) for c in ("dt", "dn")}
    CAPP = cap("parent", CTX["dt"], pos_of("dt", "H"), M2431)
    # KA1 self-patch, KA2 reference C
    r = readout(M, "help", spec_at(CAPT["help"], X2434 + M2431, pos_of("help", "T3H")))
    O[M]["ka"]["self_maxabs_dC"] = float(np.abs(r["C"] - REF[M]["help"]["C"]).max())
    if O[M]["ka"]["self_maxabs_dC"] > 0.25:
        fails.append(f"KA1 {M}: self-patch max |dC| {O[M]['ka']['self_maxabs_dC']:.3f}")
    for c in ("help", "dism"):
        got = O[M]["ref"][c]["C"]; O[M]["ka"][f"C_{c}"] = dict(got=got, m63=M63REF[M][c])
        if abs(got - M63REF[M][c]) > 0.15:
            fails.append(f"KA2 {M} {c}: C {got:.2f} vs m63 {M63REF[M][c]:.2f}")
    # ---- E2a: request graft (MLP 24-31), H and SUF, both directions; controls
    for region in ("H", "SUF"):
        arm(M, f"E2a|noreq->req|mlp24-31|{region}", "dt", "dn", spec_at(CAPR["dn"], M2431, pos_of("dt", region)), 4)
        arm(M, f"E2a|req->noreq|mlp24-31|{region}", "dn", "dt", spec_at(CAPR["dt"], M2431, pos_of("dn", region)), 4)
    nR = len(SIDS_R)
    other = [CAPR["dt"][(i + 1) % nR] for i in range(nR)]
    arm(M, "E2a|ctrl: other script's with-request mlp24-31|H", "dt", None, spec_at(other, M2431, pos_of("dt", "H")), 2)
    arm(M, "E2a|ctrl: parent's mlp24-31|H", "dt", None, spec_at(CAPP, M2431, pos_of("dt", "H")), 2)
    dump(f"{TD}/results/m77_enable_stance.json", O)
    # ---- E2b: the missing within-model MLP 24-31 H -> D cell
    for region in ("T3H", "H"):
        arm(M, f"E2b|H->D|mlp24-31|{region}", "dism", "help", spec_at(CAPT["help"], M2431, pos_of("dism", region)), 2)
    # ---- E2c: joint vs mixers alone, T3H, both directions
    for unit, keys in (("mix24-34", X2434), ("mix24-34+mlp24-31", X2434 + M2431)):
        arm(M, f"E2c|D->H|{unit}|T3H", "help", "dism", spec_at(CAPT["dism"], keys, pos_of("help", "T3H")), 2)
        arm(M, f"E2c|H->D|{unit}|T3H", "dism", "help", spec_at(CAPT["help"], keys, pos_of("dism", "T3H")), 2)
    dump(f"{TD}/results/m77_enable_stance.json", O)
    # ---- E3d: mixer LoRA off (all positions)
    for nm, lo, hi in (("mix24-34", 24, 34), ("mix32-34", 32, 34), ("mix24-31", 24, 31)):
        keep = (lambda lo_, hi_: (lambda L, g_: not (lo_ <= L <= hi_ and g_ == "mix")))(lo, hi)
        for c in ("help", "dism"):
            arm(M, f"E3d|{nm} LoRA off|{c}", c, None, None, 2, keep=keep)
    dump(f"{TD}/results/m77_enable_stance.json", O)
    # ---- E3e (SB only): apology swap of mix24-34 at T3H
    if M == "SB":
        CAPA = {c: cap(M, CTX[c], pos_of(c, "T3H"), X2434) for c in ("hth", "hts")}
        arm(M, "E3e|apology->helpful|mix24-34|T3H", "hth", "hts", spec_at(CAPA["hts"], X2434, pos_of("hth", "T3H")), 4)
        arm(M, "E3e|helpful->apology|mix24-34|T3H", "hts", "hth", spec_at(CAPA["hth"], X2434, pos_of("hts", "T3H")), 4)
        del CAPA
    del CAPT, CAPR, CAPP
    torch.cuda.empty_cache()
    dump(f"{TD}/results/m77_enable_stance.json", O)
O["ka_fails"] = fails
O["minutes"] = round(elapsed(), 1)
dump(f"{TD}/results/m77_enable_stance.json", O)


# ---------------------------------------------------------------- report
def f2(x, d=2):
    return fnum(x, d)


def acell(r):
    return f"{f2(r.get('rival_share'))} ({f2(r.get('habit_rate'))}, n {r.get('n_asides')})"


md = ["# E12 queue m77: what the trained MLP 24-31 signal is (request?), and do the mixers carry the stance / the apology?", ""]
if fails:
    md += ["**KNOWN ANSWER FAILED - read the tables below with caution:** " + "; ".join(fails), ""]
md += [f"Fold B. Scripts: {O['contexts']}. Common suffix (request pair): {O['suf_len']}. SB: helper crow / rival bee; S: helper bee / rival crow. "
       "C + = helper's animal. Plan = SAE codes at block 42 (bee / bird). z = conduct coordinate (0 helpful, 1 dismissive). Asides: 'By the "
       "way,' + 48 tokens; rival share (habit rate, n). Recipient / donor contexts: help / dism = sw005 helpful / dismissive with the request; "
       "dt / dn = dismissive with / without the request; hth / hts = sw008 hostile-then-helpful / hostile-then-apology. Patches replace module "
       "outputs in the prompt pass; everything downstream is recomputed.", "", f"Runtime {O['minutes']} min.", "", "## Known answers", ""]
for M in MODELS:
    k_ = O[M]["ka"]
    md.append(f"- {M}: self-patch max |dC| {k_['self_maxabs_dC']:.3f} (bar 0.25); unpatched C helpful {k_['C_help']['got']:.2f} (m63 "
              f"{k_['C_help']['m63']:.2f}), dismissive {k_['C_dism']['got']:.2f} (m63 {k_['C_dism']['m63']:.2f}); +-0.15.")
md += ["", "## Unpatched references", "", "| model | context | C | bee / bird | z34 / z40 | asides rival (habit, n) |", "| --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for nm, r in O[M]["ref"].items():
        md.append(f"| {M} | {nm} | {r['C']:.2f} | {r['bee']:.2f} / {r['bird']:.2f} | {r['z34']:.2f} / {r['z40']:.2f} | {acell(r)} |")
md += ["", "## Arms", "", "| model | arm | recipient <- donor | C; C moved [CI] | bee / bird; rival-feature moved | z34 / z40 | asides rival (habit, n); moved |",
       "| --- | --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for key, r in O[M]["arms"].items():
        mv = f"; {r['C_moved']:.2f} {fci(r['C_moved_ci'])}" if "C_moved" in r else ""
        md.append(f"| {M} | {key} | {r['recipient']} <- {r['donor'] or '-'} | {r['C']:.2f}{mv} | {r['bee']:.2f} / {r['bird']:.2f}; "
                  f"{f2(r.get('rivfeat_moved'))} | {r['z34']:.2f} / {r['z40']:.2f} | {acell(r)}; {f2(r.get('rival_moved'))} |")
md += ["", "Cross-run reference (m63): SB mix24-34 D->H at T3H moved C 0.74, rival 0.00 -> 0.37; H->D 0.90, 0.81 -> 0.02. m63 B2-w mixer LoRA off "
       "24-31: SB switch 0.58, S 0.92 (parent mixer outputs). m59: hostile-then-helpful 0.26 / 0.42, hostile-then-apology 0.02 / 0.31 (SB / S).", "",
       "## Pre-stated predictions (written before results)", "",
       "- E2a request-signal account: in SB the no-request MLP 24-31 outputs lower the dismissive rival by >= 0.4 (at H or SUF); the with-request "
       "outputs raise the no-request rival by >= 0.3; the other-script control moves < 0.15; S changes little. Constant-bias account: both grafts "
       "< 0.15. Bee-route account: S's bee plan / C move but not its switch; in SB effects follow the bee plan, not the request coordinate.",
       "- E2b: conduct-independent if the MLP 24-31 H->D swap lowers SB's rival by < 0.15; carries conduct if >= 0.3.",
       "- E2c: the joint D->H swap creates >= 0.15 more rival than mix24-34 alone if MLP 24-31 carries conduct only in combination.",
       "- E3d: base-weight mixers if SB keeps >= 0.7 of its switch with the mixer LoRA off in 24-34; < 0.5 means the trained mixers matter (and "
       "32-34 alone < 0.5 points at the trained DeltaNet 32-34).",
       "- E3e: the mixers carry the apology effect if the apology chat's mix24-34 outputs move hostile-then-helpful's rival >= half way to the "
       "apology chat's, and the reverse raises it; < 0.2 of the gap means they don't.", "",
       "Cautions: the SUF region covers only the header and the tail of turn 3 after the request sentence, so a graft there can't carry what the "
       "request sentence's own tokens hold; the apology gap is small (about 0.24 in rival share), so 4 x 32 asides give wide intervals; LoRA-off "
       "arms change every position (history included)."]
open(f"{TD}/results/m77_enable_stance.md", "w").write("\n".join(md) + "\n")
status(f"queue task m77_enable_stance done ({TD}/results/m77_enable_stance.md; {O['minutes']} min; KA fails: {len(fails)})")
